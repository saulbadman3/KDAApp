#src.core.math_model.py
import numpy as np
from scipy import stats

def build_profile(attempts):
    M = np.array(attempts)
    N, n = M.shape

    if N <= n:
        raise ValueError(f"Number of attempts (N={N}) must be greater than number of features (n={n})")

    lo = np.percentile(M, 5, axis=0)
    hi = np.percentile(M, 95, axis=0)
    M_clipped = np.clip(M, lo, hi)

    mu = np.mean(M_clipped, axis=0)
    
    std = np.std(M_clipped, axis=0)
    std = np.maximum(std, 15.0) 

    M_norm = (M_clipped - mu) / std

    cov = np.cov(M_norm, rowvar=False)
    
    cov += np.eye(n) * 0.08  

    return {
        "means": mu.tolist(),
        "std": std.tolist(),
        "cov": cov.tolist(),
        "N": N,
        "raw": M.tolist()
    }

def score_attempt(feats, profile, clip_outliers=False):
    mu = np.array(profile["means"])
    std = np.array(profile["std"])
    cov = np.array(profile["cov"])

    if clip_outliers and "raw" in profile:
        raw_data = np.array(profile["raw"])
        lo = np.percentile(raw_data, 5, axis=0)
        hi = np.percentile(raw_data, 95, axis=0)
        feats = np.clip(feats, lo, hi)

    feats_norm = (feats - mu) / std
    cov_inv = np.linalg.pinv(cov)
    d2 = np.dot(np.dot(feats_norm, cov_inv), feats_norm)
    
    return float(d2.item() if hasattr(d2, "item") else d2)

def threshold(n_feat, alpha):
    theoretical_tau = float(stats.chi2.ppf(1 - alpha, df=n_feat))
    return theoretical_tau * 1.2

def roc_det(legit, impost, pts=60):
    lo = min(legit + impost) * 0.8
    hi = max(legit + impost) * 1.2
    thr = np.linspace(lo, hi, pts)
    far = np.array([sum(s <= t for s in impost) / max(len(impost), 1) for t in thr])
    frr = np.array([sum(s > t for s in legit) / max(len(legit),  1) for t in thr])
    return thr, far, frr, 1 - frr