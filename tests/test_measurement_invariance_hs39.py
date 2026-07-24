"""Verification test for code/lib_scalar_invariance.py against the classic
Holzinger & Swineford (1939) multi-group CFA benchmark (Pasteur vs.
Grant-White schools), as published in the lavaan tutorial
(https://lavaan.ugent.be/tutorial/groups.html):

    Configural: chi2 = 115.85, df = 48
    Metric:     chi2 = 124.04, df = 54   (Δchi2 = 8.19,  Δdf = 6, ns)
    Scalar:     chi2 = 164.10, df = 60   (Δchi2 = 40.06, Δdf = 6, p<.001)

This dataset ships with semopy itself (semopy/examples/), so the test needs
no network access and no R/lavaan installation.

Configural and metric use the same joint-optimizer pattern already used (and
independently validated here) for 17_measurement_invariance.py /
18_multigroup_sem_paths.py; only the scalar stage (lib_scalar_invariance)
needed a fix (see module docstring), which is what this test guards.
"""

import os
import sys

import numpy as np
import pandas as pd
import pytest
import semopy
from scipy.optimize import minimize

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

from lib_scalar_invariance import fit_scalar_multigroup  # noqa: E402

HS39_PATH = os.path.join(
    os.path.dirname(semopy.__file__), "examples", "holzinger_swineford39_data.csv"
)

FACTOR_ITEMS = {
    "visual": ["x1", "x2", "x3"],
    "textual": ["x4", "x5", "x6"],
    "speed": ["x7", "x8", "x9"],
}
ALL_ITEMS = [it for items in FACTOR_ITEMS.values() for it in items]
P = len(ALL_ITEMS)
N_FACTORS = len(FACTOR_ITEMS)


def _build_desc(shared_loadings):
    lines = []
    for factor, items in FACTOR_ITEMS.items():
        marker = items[0]
        terms = [marker] + [
            (f"INV_L_{it}*{it}" if shared_loadings else it) for it in items[1:]
        ]
        lines.append(f"{factor} =~ {' + '.join(terms)}")
    return "\n".join(lines)


def _joint_register(model, tag, global_index, global_start, bounds):
    idx = []
    for name, p in model.parameters.items():
        if not p.active:
            continue
        key = name if name.startswith("INV_") else f"{tag}::{name}"
        if key not in global_index:
            global_index[key] = len(global_start)
            global_start.append(p.start)
            bounds.append(p.bound)
        idx.append(global_index[key])
    return np.array(idx, dtype=int)


def _fit_covariance_multigroup(df1, df2, desc):
    """Configural / metric stage (covariance-structure only), same pattern
    as 17_measurement_invariance.py's fit_covariance_multigroup."""
    m1, m2 = semopy.Model(desc), semopy.Model(desc)
    m1.load(df1)
    m2.load(df2)

    global_index, global_start, bounds = {}, [], []
    map1 = _joint_register(m1, "G1", global_index, global_start, bounds)
    map2 = _joint_register(m2, "G2", global_index, global_start, bounds)

    fun1, grad1 = m1.get_objective("MLW")
    fun2, grad2 = m2.get_objective("MLW")
    n1, n2 = m1.n_samples, m2.n_samples

    def objective(x):
        x1, x2 = x[map1], x[map2]
        val = n1 * fun1(x1) + n2 * fun2(x2)
        g = np.zeros_like(x)
        np.add.at(g, map1, n1 * grad1(x1))
        np.add.at(g, map2, n2 * grad2(x2))
        return val, g

    x0 = np.array(global_start, dtype=float)
    res = minimize(objective, x0, jac=True, method="SLSQP", bounds=bounds,
                    options={"maxiter": 3000, "ftol": 1e-12})
    n_params = len(res.x)
    dof = 2 * (P * (P + 1) // 2) - n_params
    return dict(chi2=res.fun, dof=dof, n_params=n_params, success=res.success)


@pytest.fixture(scope="module")
def hs39_groups():
    df = pd.read_csv(HS39_PATH, index_col=0)
    pasteur = df[df["school"] == "Pasteur"].reset_index(drop=True)
    grant = df[df["school"] == "Grant-White"].reset_index(drop=True)
    return pasteur, grant


def test_configural_matches_lavaan(hs39_groups):
    pasteur, grant = hs39_groups
    res = _fit_covariance_multigroup(pasteur, grant, _build_desc(shared_loadings=False))
    assert res["success"]
    assert res["chi2"] == pytest.approx(115.85, abs=0.05)
    assert res["dof"] == 48


def test_metric_matches_lavaan(hs39_groups):
    pasteur, grant = hs39_groups
    res = _fit_covariance_multigroup(pasteur, grant, _build_desc(shared_loadings=True))
    assert res["success"]
    assert res["chi2"] == pytest.approx(124.04, abs=0.05)
    assert res["dof"] == 54


def test_scalar_matches_lavaan_after_fix(hs39_groups):
    """The regression guard for the bug: before the fix this returned
    chi2=204.6, dof=63 (missing the 3 free latent factor means for the
    comparison group)."""
    pasteur, grant = hs39_groups
    res = fit_scalar_multigroup(
        pasteur, grant, _build_desc(shared_loadings=True), ALL_ITEMS, N_FACTORS
    )
    assert res["success"]
    assert res["dof"] == 60, "dof should be 60 (=54+6), not 63 -- check kappa freeing"
    assert res["chi2"] == pytest.approx(164.10, abs=0.5)


def test_scalar_delta_chi2_matches_lavaan(hs39_groups):
    pasteur, grant = hs39_groups
    metric = _fit_covariance_multigroup(pasteur, grant, _build_desc(shared_loadings=True))
    scalar = fit_scalar_multigroup(
        pasteur, grant, _build_desc(shared_loadings=True), ALL_ITEMS, N_FACTORS
    )
    dchi2 = scalar["chi2"] - metric["chi2"]
    ddof = scalar["dof"] - metric["dof"]
    assert ddof == 6
    assert dchi2 == pytest.approx(40.06, abs=0.5)
