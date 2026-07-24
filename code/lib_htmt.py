"""Heterotrait-Monotrait ratio of correlations (HTMT), Henseler, Ringle, &
Sarstedt (2015). Shared by 13_validity.py and tests/test_htmt.py.

HTMT_ij = mean(|corr(item_a, item_b)|) for a in construct i, b in construct j
          -----------------------------------------------------------------
          sqrt( mean(|corr(a, a')|, a != a' in i) * mean(|corr(b, b')|, b != b' in j) )
"""

import itertools

import numpy as np
import pandas as pd


def _monotrait_mean(corr, items):
    """Average of the absolute off-diagonal correlations within one
    construct's own item set (heterotrait-*mono*method in Henseler et al.'s
    terminology refers to different traits; this is the within-trait,
    between-indicator average -- i.e. the "monotrait-heteromethod" block)."""
    if len(items) < 2:
        raise ValueError("A construct needs >= 2 items to define HTMT.")
    vals = [corr.loc[a, b] for a, b in itertools.combinations(items, 2)]
    return float(np.mean(vals))


def _heterotrait_mean(corr, items_i, items_j):
    """Average of the absolute correlations between every item of construct
    i and every item of construct j (heterotrait-heteromethod block)."""
    vals = [corr.loc[a, b] for a in items_i for b in items_j]
    return float(np.mean(vals))


def htmt_from_corr(corr, constructs):
    """Assemble the HTMT matrix from an already-computed |correlation|
    matrix. Split out from htmt_matrix() so the arithmetic can be unit
    tested against a hand-specified correlation matrix, independent of
    whether pandas' .corr() itself is trusted."""
    names = list(constructs.keys())
    mono = {k: _monotrait_mean(corr, v) for k, v in constructs.items()}

    mat = pd.DataFrame(index=names, columns=names, dtype=float)
    for i, j in itertools.combinations(names, 2):
        het = _heterotrait_mean(corr, constructs[i], constructs[j])
        denom = np.sqrt(mono[i] * mono[j])
        val = het / denom
        mat.loc[i, j] = val
        mat.loc[j, i] = val
    for n in names:
        mat.loc[n, n] = np.nan
    return mat


def htmt_matrix(data, constructs):
    """Point-estimate HTMT matrix.

    Parameters
    ----------
    data : DataFrame containing all items listed in `constructs`.
    constructs : dict[str, list[str]] mapping construct name -> item columns.

    Returns
    -------
    DataFrame (construct x construct), NaN on the diagonal.
    """
    corr = data[[it for items in constructs.values() for it in items]].corr().abs()
    return htmt_from_corr(corr, constructs)


def htmt_bootstrap(data, constructs, n_boot=5000, seed=42, alpha=0.05):
    """Percentile bootstrap CIs for every pairwise HTMT (Henseler et al. 2015
    inference procedure: case resampling, then re-derive HTMT per resample).

    Returns a long-format DataFrame with one row per construct pair:
    point estimate, bootstrap mean, SE, CI bounds, and flags for whether the
    CI upper bound exceeds 0.85 / 1.00.
    """
    rng = np.random.default_rng(seed)
    n = len(data)
    names = list(constructs.keys())
    pairs = list(itertools.combinations(names, 2))

    point = htmt_matrix(data, constructs)

    boot_vals = {p: np.empty(n_boot) for p in pairs}
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        sample = data.iloc[idx]
        boot_mat = htmt_matrix(sample, constructs)
        for i, j in pairs:
            boot_vals[(i, j)][b] = boot_mat.loc[i, j]

    rows = []
    for i, j in pairs:
        vals = boot_vals[(i, j)]
        lo, hi = np.percentile(vals, [100 * alpha / 2, 100 * (1 - alpha / 2)])
        rows.append({
            "construct_i": i,
            "construct_j": j,
            "HTMT": round(float(point.loc[i, j]), 4),
            "boot_mean": round(float(np.mean(vals)), 4),
            "boot_se": round(float(np.std(vals, ddof=1)), 4),
            "ci_lower": round(float(lo), 4),
            "ci_upper": round(float(hi), 4),
            "ci_upper_exceeds_0.85": bool(hi >= 0.85),
            "ci_upper_exceeds_1.00": bool(hi >= 1.00),
        })
    return pd.DataFrame(rows)
