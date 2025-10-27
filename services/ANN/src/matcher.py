# src/matcher.py
"""
Matcher helper (final version).
- Loads saved model + scaler from ../models/
- Exposes get_top_k_from_users_flexible(choices, users_rows, interest_names, k)
- CLI/demo available: run with or without arguments.

Usage:
  python src/matcher.py                        -> runs built-in demo using data/student_users_final.csv
  python src/matcher.py "ml=9,ai=7,robotics=4" 6  -> runs CLI with the given choices and prints top-k
"""

from pathlib import Path
import os
import sys
import joblib
import numpy as np
import pandas as pd

# ---------------- CONFIG ----------------
HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"
SCALER_PATH = MODELS_DIR / "scaler.pkl"
TF_MODEL_PATH = MODELS_DIR / "student_match_model_tf.keras"
SKL_MODEL_PATH = MODELS_DIR / "student_match_model_sklearn.pkl"
DEV_USERS_CSV = DATA_DIR / "student_users_final.csv"

# Canonical interest list used in training (must match exactly)
INTEREST_NAMES = [
    "artificial intelligence", "machine learning", "data science", "hackathon",
    "full stack development", "fintech", "ui/ux design", "cybersecurity",
    "web development", "app development", "cloud computing", "deep learning",
    "robotics", "research", "blockchain", "entrepreneurship",
    "vibecoding", "collaboration", "trading", "product management"
]

# ---------------- Load scaler & model ----------------
if not SCALER_PATH.exists():
    raise FileNotFoundError(f"Scaler not found at {SCALER_PATH}. Run training first.")

scaler = joblib.load(SCALER_PATH)
MODEL_FRAMEWORK = None
model = None
# Try TF model
try:
    import tensorflow as tf  # optional
    if TF_MODEL_PATH.exists():
        model = tf.keras.models.load_model(str(TF_MODEL_PATH))
        MODEL_FRAMEWORK = "tensorflow"
except Exception:
    model = None

# Fallback to sklearn
if model is None and SKL_MODEL_PATH.exists():
    model = joblib.load(str(SKL_MODEL_PATH))
    MODEL_FRAMEWORK = "sklearn"

if model is None:
    raise FileNotFoundError(f"No trained model found. Expected one of:\n  {TF_MODEL_PATH}\n  {SKL_MODEL_PATH}")

print(f"[INFO] Loaded model framework: {MODEL_FRAMEWORK}")
print(f"[INFO] Scaler loaded from: {SCALER_PATH}")

# ---------------- Helpers ----------------
def choices_to_vector(choices, interest_names=INTEREST_NAMES):
    """
    Convert choices list [('machine learning',9), ...] -> vector of length D
    """
    vec = np.zeros(len(interest_names), dtype=float)
    name_to_idx = {n: i for i, n in enumerate(interest_names)}
    for it, score in choices:
        # allow some flexible matching (lowercase)
        if it in name_to_idx:
            vec[name_to_idx[it]] = float(score)
        else:
            low = it.lower().strip()
            # try exact case-insensitive match
            found = False
            for cand in interest_names:
                if low == cand.lower():
                    vec[name_to_idx[cand]] = float(score)
                    found = True
                    break
            if not found:
                # try partial match (substring)
                for cand in interest_names:
                    if low in cand.lower():
                        vec[name_to_idx[cand]] = float(score)
                        found = True
                        break
            if not found:
                # ignore unknown interest but warn
                print(f"[WARN] Unknown interest '{it}' (ignored). Allowed examples: {interest_names[:5]}...")
    return vec

def expand_user_row_to_full(row, interest_names=INTEREST_NAMES):
    """
    Accepts a dict-like row from DB or CSV, returns a dict:
      {'name': <name>, <interest1>: val, ..., <interest20>: val}
    Handles:
      - full rows that already have the 20 interest columns
      - compact rows with interest1/interest1_weight, interest2/interest2_weight, interest3/interest3_weight
    """
    out = {"name": row.get("name", row.get("Name", None))}
    # check if full
    has_full = all((it in row) or (it.lower() in [k.lower() for k in row.keys()]) for it in interest_names)
    if has_full:
        for it in interest_names:
            # try original key first, then lowercase
            if it in row:
                val = row[it]
            else:
                # find case-insensitive key
                found_key = None
                for k in row.keys():
                    if k.lower() == it.lower():
                        found_key = k; break
                val = row.get(found_key, 0) if found_key else 0
            try:
                out[it] = float(val)
            except:
                out[it] = 0.0
        return out

    # otherwise, look for compact 3-choice fields
    # normalize lower-case lookup
    row_lc = {k.lower(): v for k, v in row.items() if k is not None}
    choices = []
    # pattern: interest1 / interest1_weight
    for i in (1, 2, 3):
        k_int = f"interest{i}"
        k_w = f"interest{i}_weight"
        if k_int in row_lc:
            interest_val = row_lc.get(k_int)
            weight_val = row_lc.get(k_w, row_lc.get(f"weight{i}", 0))
            try:
                choices.append((str(interest_val).strip(), float(weight_val)))
            except:
                # maybe interest_{i}_score naming
                choices.append((str(interest_val).strip(), float(row_lc.get(f"interest{i}_score", 0))))
    # alternative pattern: interest1_name / interest1_score
    if not choices:
        for i in (1, 2, 3):
            k_n = f"interest{i}_name"
            k_s = f"interest{i}_score"
            if k_n in row_lc:
                try:
                    choices.append((str(row_lc[k_n]).strip(), float(row_lc.get(k_s, 0))))
                except:
                    pass

    # fallback: try to pick any of the interest_names that exist non-zero
    if not choices:
        for it in interest_names:
            if it.lower() in row_lc:
                try:
                    v = float(row_lc[it.lower()])
                    if v != 0:
                        choices.append((it, v))
                except:
                    pass

    # build full dict with zeros and fill
    for it in interest_names:
        out[it] = 0.0
    for it_name, w in choices:
        # exact or case-insensitive match or partial
        matched = None
        for cand in interest_names:
            if it_name == cand:
                matched = cand; break
        if matched is None:
            for cand in interest_names:
                if it_name.lower() == cand.lower():
                    matched = cand; break
        if matched is None:
            for cand in interest_names:
                if it_name.lower() in cand.lower() or cand.lower() in it_name.lower():
                    matched = cand; break
        if matched:
            try:
                out[matched] = float(w)
            except:
                out[matched] = 0.0
        else:
            print(f"[WARN] Could not match interest name '{it_name}' to canonical list (ignored).")
    return out

def get_top_k_from_users_flexible(choices, users_rows, interest_names=INTEREST_NAMES, k=6, batch_size=256):
    """
    choices: list of tuples [('machine learning',9), ...]
    users_rows: list of dict-like rows (from SQL or CSV)
    returns: list of (name, prob)
    """
    if not isinstance(choices, (list, tuple)):
        raise ValueError("choices must be a list of (interest,score) tuples.")
    u_vec = choices_to_vector(choices, interest_names)
    cand_names = []
    feats = []
    for row in users_rows:
        full_row = expand_user_row_to_full(row, interest_names)
        cand_names.append(full_row["name"])
        v = np.array([full_row[it] for it in interest_names], dtype=float)
        feats.append(np.concatenate([u_vec, v]))
    if len(feats) == 0:
        print("[WARN] No candidate users provided.")
        return []
    X = np.vstack(feats)
    Xs = scaler.transform(X)
    if MODEL_FRAMEWORK == "tensorflow":
        probs = model.predict(Xs, batch_size=batch_size).ravel()
    else:
        probs = model.predict_proba(Xs)[:, 1]
    idx = np.argsort(probs)[::-1][:k]
    return [(cand_names[i], float(probs[i])) for i in idx]

# ---------------- CLI / demo ----------------
def parse_cli_string(s):
    """Simple parser: accepts 'a=9,b=7,c=4' or 'a:9,b:7' or 'a=9 b=7' etc."""
    if not s:
        return []
    s = s.replace(":", "=")
    parts = [p.strip() for p in s.replace(",", " ").split() if p.strip()]
    choices = []
    for p in parts:
        if "=" not in p:
            continue
        name, val = p.split("=", 1)
        try:
            choices.append((name.strip(), float(val.strip())))
        except:
            try:
                choices.append((name.strip(), float(val.strip())))
            except:
                pass
    return choices

def demo_run(choices=None, k=6):
    # Load users for demo
    if not DEV_USERS_CSV.exists():
        print(f"[ERROR] Demo CSV not found at {DEV_USERS_CSV}. Place your student_users_final.csv there or run matcher with SQL data.")
        return
    users_df = pd.read_csv(DEV_USERS_CSV)
    users_rows = users_df.to_dict(orient="records")
    if choices is None:
        # choose a default test user (first row) and make sample choices, or hardcoded
        choices = [("machine learning", 9), ("artificial intelligence", 7), ("robotics", 4)]
        print("[INFO] No CLI choices provided. Using default choices:", choices)
    print("[INFO] Running matching on", len(users_rows), "users ...")
    topk = get_top_k_from_users_flexible(choices, users_rows, INTEREST_NAMES, k=k)
    print(f"\n=== Top {k} matches ===")
    for i, (name, p) in enumerate(topk, 1):
        print(f"{i}. {name}  ->  {p:.4f}")

if __name__ == "__main__":
    # Two modes:
    # 1) python src/matcher.py "ml=9,ai=7,robotics=4" 6
    # 2) python src/matcher.py  -> runs demo using CSV (if present)
    args = sys.argv[1:]
    if len(args) >= 1:
        cli_str = args[0]
        k = int(args[1]) if len(args) >= 2 else 6
        choices = parse_cli_string(cli_str)
        if not choices:
            print("[ERROR] Could not parse choices. Example input: \"machine learning=9,artificial intelligence=7,robotics=4\"")
            sys.exit(1)
        print("[INFO] Parsed choices:", choices)
        # Load users from CSV for demo; in production backend will supply users_rows from SQL
        if DEV_USERS_CSV.exists():
            users_df = pd.read_csv(DEV_USERS_CSV)
            users_rows = users_df.to_dict(orient="records")
            demo_run(choices=choices, k=k)
        else:
            print("[ERROR] No demo CSV found at", DEV_USERS_CSV, " — in production pass users_rows from DB.")
            sys.exit(1)
    else:
        # no args -> run default demo (if CSV exists)
        demo_run(choices=None, k=6)
