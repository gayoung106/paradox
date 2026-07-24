"""Verification tests for code/lib_htmt.py.

These tests check the HTMT arithmetic (Henseler, Ringle, & Sarstedt, 2015)
against small correlation matrices that can be checked by hand with a
calculator -- they do not depend on the correctness of pandas' .corr(),
and they do not touch the project's real survey data.

Run with: venv/Scripts/python.exe -m pytest tests/ -v
"""

import math
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

from lib_htmt import htmt_from_corr, htmt_matrix, htmt_bootstrap  # noqa: E402


def test_two_construct_hand_calculation():
    """Two constructs, two items each. All six pairwise correlations are
    set explicitly, so HTMT can be re-derived with a calculator:

    within A (mono_A):        corr(a1, a2) = 0.8
    within B (mono_B):        corr(b1, b2) = 0.6
    across A-B (heterotrait):  corr(a1,b1)=.2, corr(a1,b2)=.3,
                                corr(a2,b1)=.1, corr(a2,b2)=.4

    heterotrait mean = (.2 + .3 + .1 + .4) / 4 = .25
    HTMT(A,B) = .25 / sqrt(.8 * .6) = .25 / sqrt(.48) = .25 / 0.6928203...
              = 0.3608439...
    """
    items = ["a1", "a2", "b1", "b2"]
    corr = pd.DataFrame(np.eye(4), index=items, columns=items)
    corr.loc["a1", "a2"] = corr.loc["a2", "a1"] = 0.8
    corr.loc["b1", "b2"] = corr.loc["b2", "b1"] = 0.6
    corr.loc["a1", "b1"] = corr.loc["b1", "a1"] = 0.2
    corr.loc["a1", "b2"] = corr.loc["b2", "a1"] = 0.3
    corr.loc["a2", "b1"] = corr.loc["b1", "a2"] = 0.1
    corr.loc["a2", "b2"] = corr.loc["b2", "a2"] = 0.4

    constructs = {"A": ["a1", "a2"], "B": ["b1", "b2"]}
    mat = htmt_from_corr(corr, constructs)

    expected = 0.25 / math.sqrt(0.8 * 0.6)
    assert mat.loc["A", "B"] == pytest.approx(expected, abs=1e-10)
    assert mat.loc["B", "A"] == pytest.approx(expected, abs=1e-10)
    assert math.isnan(mat.loc["A", "A"])
    assert math.isnan(mat.loc["B", "B"])


def test_three_construct_indexing():
    """Three constructs of unequal size; checks that the heterotrait /
    monotrait averages pick up the right item subsets and that the result
    is symmetric. Values are chosen to be simple fractions.

    Construct A: a1, a2, a3 (3 items) -> 3 within-pairs
    Construct B: b1, b2 (2 items)      -> 1 within-pair
    Construct C: c1, c2 (2 items)      -> 1 within-pair
    """
    items = ["a1", "a2", "a3", "b1", "b2", "c1", "c2"]
    corr = pd.DataFrame(np.eye(7), index=items, columns=items)

    within_A = {("a1", "a2"): 0.6, ("a1", "a3"): 0.7, ("a2", "a3"): 0.5}
    for (x, y), v in within_A.items():
        corr.loc[x, y] = corr.loc[y, x] = v
    corr.loc["b1", "b2"] = corr.loc["b2", "b1"] = 0.9
    corr.loc["c1", "c2"] = corr.loc["c2", "c1"] = 0.4

    # A-B heterotrait block (3x2 = 6 pairs), all set to 0.3
    for a in ["a1", "a2", "a3"]:
        for b in ["b1", "b2"]:
            corr.loc[a, b] = corr.loc[b, a] = 0.3

    # A-C heterotrait block, all set to 0.2
    for a in ["a1", "a2", "a3"]:
        for c in ["c1", "c2"]:
            corr.loc[a, c] = corr.loc[c, a] = 0.2

    # B-C heterotrait block, all set to 0.1
    for b in ["b1", "b2"]:
        for c in ["c1", "c2"]:
            corr.loc[b, c] = corr.loc[c, b] = 0.1

    constructs = {"A": ["a1", "a2", "a3"], "B": ["b1", "b2"], "C": ["c1", "c2"]}
    mat = htmt_from_corr(corr, constructs)

    mono_A = (0.6 + 0.7 + 0.5) / 3
    mono_B = 0.9
    mono_C = 0.4

    expected_AB = 0.3 / math.sqrt(mono_A * mono_B)
    expected_AC = 0.2 / math.sqrt(mono_A * mono_C)
    expected_BC = 0.1 / math.sqrt(mono_B * mono_C)

    assert mat.loc["A", "B"] == pytest.approx(expected_AB, abs=1e-10)
    assert mat.loc["A", "C"] == pytest.approx(expected_AC, abs=1e-10)
    assert mat.loc["B", "C"] == pytest.approx(expected_BC, abs=1e-10)
    # symmetry
    assert mat.loc["B", "A"] == pytest.approx(expected_AB, abs=1e-10)
    assert mat.loc["C", "A"] == pytest.approx(expected_AC, abs=1e-10)
    assert mat.loc["C", "B"] == pytest.approx(expected_BC, abs=1e-10)


def test_htmt_differs_from_raw_composite_correlation():
    """Regression guard for the bug found in 13_validity.py: HTMT must NOT
    collapse to the simple Pearson correlation between construct mean
    composites. Uses synthetic data with a known factor structure where the
    two are provably different (multi-item constructs with imperfect
    indicator reliability)."""
    rng = np.random.default_rng(0)
    n = 2000

    factor_a = rng.normal(size=n)
    factor_b = 0.5 * factor_a + np.sqrt(1 - 0.5**2) * rng.normal(size=n)

    def make_items(factor, loadings, rng):
        return {
            f"item{i}": loading * factor + np.sqrt(1 - loading**2) * rng.normal(size=n)
            for i, loading in enumerate(loadings)
        }

    items_a = make_items(factor_a, [0.7, 0.65, 0.6], rng)
    items_b = make_items(factor_b, [0.7, 0.65, 0.6], rng)

    df = pd.DataFrame({
        "a1": items_a["item0"], "a2": items_a["item1"], "a3": items_a["item2"],
        "b1": items_b["item0"], "b2": items_b["item1"], "b3": items_b["item2"],
    })

    constructs = {"A": ["a1", "a2", "a3"], "B": ["b1", "b2", "b3"]}
    htmt_val = htmt_matrix(df, constructs).loc["A", "B"]

    composite_a = df[constructs["A"]].mean(axis=1)
    composite_b = df[constructs["B"]].mean(axis=1)
    composite_corr = abs(composite_a.corr(composite_b))

    # HTMT corrects for attenuation and must come out noticeably larger
    # than the raw composite-score correlation for this design.
    assert htmt_val > composite_corr + 0.03


def test_bootstrap_ci_contains_point_estimate_and_flags_work():
    rng = np.random.default_rng(1)
    n = 500
    factor_a = rng.normal(size=n)
    factor_b = 0.3 * factor_a + np.sqrt(1 - 0.3**2) * rng.normal(size=n)

    df = pd.DataFrame({
        "a1": 0.7 * factor_a + np.sqrt(1 - 0.49) * rng.normal(size=n),
        "a2": 0.6 * factor_a + np.sqrt(1 - 0.36) * rng.normal(size=n),
        "b1": 0.7 * factor_b + np.sqrt(1 - 0.49) * rng.normal(size=n),
        "b2": 0.6 * factor_b + np.sqrt(1 - 0.36) * rng.normal(size=n),
    })
    constructs = {"A": ["a1", "a2"], "B": ["b1", "b2"]}

    result = htmt_bootstrap(df, constructs, n_boot=300, seed=42)
    row = result.iloc[0]

    assert row["ci_lower"] <= row["HTMT"] <= row["ci_upper"]
    assert row["ci_upper_exceeds_0.85"] == bool(row["ci_upper"] >= 0.85)
    assert row["ci_upper_exceeds_1.00"] == bool(row["ci_upper"] >= 1.00)
    # weakly-correlated factors (0.3) should not produce a discriminant
    # validity red flag
    assert row["ci_upper"] < 0.85
