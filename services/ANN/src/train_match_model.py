# src/train_match_model.py
"""
Train ANN from CSVs and save model + scaler to models/
Expect CSV files at project_root/data/student_interest_pairs_final.csv
                     and project_root/data/student_users_final.csv

Run from project root (or anywhere) with:
    python src/train_match_model.py
"""

from pathlib import Path
import os, random
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score, confusion_matrix

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Determine project root (two levels up from this file) so script is robust
HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

PAIRS_CSV = DATA_DIR / "student_interest_pairs_final.csv"
USERS_CSV = DATA_DIR / "student_users_final.csv"

# Helpful message if files missing
if not PAIRS_CSV.exists() or not USERS_CSV.exists():
    raise FileNotFoundError(
        f"Missing CSV files.\nExpected:\n  {PAIRS_CSV}\n  {USERS_CSV}\n\n"
        "Put your CSVs into the project's data/ folder and run again."
    )

print("Loading CSVs from:", DATA_DIR)
pairs = pd.read_csv(PAIRS_CSV)
users = pd.read_csv(USERS_CSV)

# detect interest columns (pairs file contains <interest>_1 and <interest>_2)
interest_cols_1 = [c for c in pairs.columns if c.endswith("_1")]
interest_cols_2 = [c for c in pairs.columns if c.endswith("_2")]
interest_names = [c[:-2] for c in interest_cols_1]

if len(interest_names) == 0:
    raise ValueError("No interest columns found in pairs CSV (expect columns that end with _1/_2).")

# Build features & labels
X = pairs[interest_cols_1 + interest_cols_2].astype(float).values
y = pairs["match"].astype(int).values

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=RANDOM_SEED
)

# Scale
scaler = StandardScaler().fit(X_train)
X_train_s = scaler.transform(X_train)
X_test_s = scaler.transform(X_test)

# Try TensorFlow; fallback to sklearn
USE_TF = False
try:
    import tensorflow as tf
    from tensorflow.keras import layers, models, callbacks
    USE_TF = True
except Exception:
    USE_TF = False

if USE_TF:
    print("Training with TensorFlow/Keras (will use class_weight to address imbalance).")
    from sklearn.utils import class_weight
    classes = np.unique(y_train)
    cw = class_weight.compute_class_weight("balanced", classes=classes, y=y_train)
    class_weight_dict = {int(classes[i]): float(cw[i]) for i in range(len(classes))}
    print("Class weights:", class_weight_dict)

    def make_model(input_dim):
        inp = layers.Input(shape=(input_dim,))
        x = layers.Dense(128, activation="relu")(inp)
        x = layers.Dropout(0.2)(x)
        x = layers.Dense(64, activation="relu")(x)
        x = layers.Dropout(0.1)(x)
        x = layers.Dense(32, activation="relu")(x)
        out = layers.Dense(1, activation="sigmoid")(x)
        m = models.Model(inp, out)
        m.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
        return m

    model = make_model(X_train_s.shape[1])
    es = callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True, verbose=1)

    model.fit(
        X_train_s, y_train,
        validation_split=0.1,
        epochs=60,
        batch_size=64,
        callbacks=[es],
        class_weight=class_weight_dict,
        verbose=1
    )

    y_pred_prob = model.predict(X_test_s).ravel()
    model_path = MODELS_DIR / "student_match_model_tf.keras"
    model.save(str(model_path), include_optimizer=False)
    joblib.dump(scaler, MODELS_DIR / "scaler.pkl")
    print("Saved TF model to", model_path)

else:
    print("TensorFlow not available: training scikit-learn MLPClassifier fallback.")
    from sklearn.neural_network import MLPClassifier
    clf = MLPClassifier(hidden_layer_sizes=(128,64,32), activation="relu", max_iter=500, random_state=RANDOM_SEED)
    clf.fit(X_train_s, y_train)
    y_pred_prob = clf.predict_proba(X_test_s)[:, 1]
    model_path = MODELS_DIR / "student_match_model_sklearn.pkl"
    joblib.dump(clf, model_path)
    joblib.dump(scaler, MODELS_DIR / "scaler.pkl")
    print("Saved sklearn model to", model_path)

# Evaluate
TH = 0.5
y_pred = (y_pred_prob >= TH).astype(int)
acc = accuracy_score(y_test, y_pred)
try:
    auc = roc_auc_score(y_test, y_pred_prob)
except:
    auc = float("nan")
prec = precision_score(y_test, y_pred, zero_division=0)
rec = recall_score(y_test, y_pred, zero_division=0)
cm = confusion_matrix(y_test, y_pred)

print("\n=== Evaluation on test set ===")
print("Accuracy:", round(acc, 4))
print("AUC:", round(auc, 4))
print("Precision:", round(prec, 4))
print("Recall:", round(rec, 4))
print("Confusion matrix:\n", cm)
print("\nAll done. Model + scaler saved to:", MODELS_DIR)
