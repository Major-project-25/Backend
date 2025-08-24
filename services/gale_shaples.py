# gale_cosine_recommender.py
from typing import Dict, List, Sequence, Tuple, Optional
import numpy as np

# ---------- internal helpers (not exported) ----------

def _normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    keys = list(weights.keys())
    vals = np.array([weights.get(k, 0.0) for k in keys], dtype=float)
    s = float(vals.sum())
    if s <= 0.0:
        # equal split fallback
        eq = 1.0 / max(1, len(keys))
        return {k: eq for k in keys}
    vals = vals / s
    return {k: float(v) for k, v in zip(keys, vals)}

def _create_vector(w: Dict[str, float], subjects: Sequence[str]) -> np.ndarray:
    return np.array([w.get(s, 0.0) for s in subjects], dtype=float)

def _cosine_similarity_matrix(X: np.ndarray) -> np.ndarray:
    X = X.astype(float)
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    Xn = X / norms
    return Xn @ Xn.T

def _preferences_from_similarity(names: List[str], S: np.ndarray) -> Dict[str, List[str]]:
    n = len(names)
    prefs: Dict[str, List[str]] = {}
    for i in range(n):
        scored = [(names[j], float(S[i, j])) for j in range(n) if j != i]
        scored.sort(key=lambda x: x[1], reverse=True)
        prefs[names[i]] = [name for name, _ in scored]
    return prefs

def _gale_shapley_core(
    groupA: List[str],
    groupB: List[str],
    preferences: Dict[str, List[str]],
) -> Dict[str, str]:
    """
    Classic GS core (A proposes to B). Returns mapping B -> A.
    """
    free_A = list(groupA)
    engaged: Dict[str, str] = {}        # B -> A
    proposed: Dict[str, set] = {a: set() for a in groupA}

    while free_A:
        a = free_A[0]
        options = [b for b in preferences.get(a, []) if b not in proposed[a] and b in groupB]
        if not options:
            free_A.pop(0)
            continue

        b = options[0]
        proposed[a].add(b)

        if b not in engaged:
            engaged[b] = a
            free_A.pop(0)
        else:
            current_a = engaged[b]
            b_list = preferences.get(b, [])
            if b_list.index(a) < b_list.index(current_a):
                engaged[b] = a
                free_A[0] = current_a
            else:
                # a stays free and will try next
                pass
    return engaged

# ---------- public API ----------

def recommend_gale_cosine(
    profiles: Dict[str, Dict[str, float]],
    subjects: Sequence[str],
    me: str,
    groupA: Optional[List[str]] = None,
) -> Tuple[List[str], List[str]]:
    """
    Build cosine-based preference lists and run Gale–Shapley (A proposes to B).

    Returns:
      best_partner: [<name>] or []   (your stable match, if any)
      recommendations: [<name>, <name>, ...]  (your preference order, names only)

    Notes:
      - If groupA is None, defaults to [me] (you are the sole proposer).
      - Provide multiple proposers in groupA to get non-trivial stable outcomes.
      - No scores are returned; only names.
    """
    # 1) normalize every profile
    norm_profiles = {n: _normalize_weights(w) for n, w in profiles.items()}
    if me not in norm_profiles:
        raise ValueError(f"'{me}' not found in profiles.")
    names = list(norm_profiles.keys())

    # 2) cosine similarity
    X = np.stack([_create_vector(norm_profiles[n], subjects) for n in names], axis=0)
    S = _cosine_similarity_matrix(X)

    # 3) preferences
    prefs = _preferences_from_similarity(names, S)

    # 4) partition A/B
    A = [me] if groupA is None else list(groupA)
    B = [n for n in names if n not in A]

    # 5) GS
    engaged_B_to_A = _gale_shapley_core(A, B, prefs)

    # 6) outputs
    best_partner: List[str] = []
    for b, a in engaged_B_to_A.items():
        if a == me:
            best_partner = [b]
            break
    recommendations = prefs.get(me, [])[:]
    return best_partner, recommendations