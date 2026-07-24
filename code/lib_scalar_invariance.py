"""Two-group scalar (strong) measurement invariance via a joint ML fit
function, matching lavaan's group.equal=c("loadings","intercepts") behavior.

semopy has no native multi-group support, so 17_measurement_invariance.py
implements a hand-rolled joint optimizer (see also 18_multigroup_sem_paths.py,
which uses the same pattern for the covariance-only, no-mean-structure case
and is unaffected by the bug described below).

Scalar invariance requires: equal loadings (already constrained via shared
INV_L_* labels in `desc`, handled upstream), equal intercepts (`tau`, P
shared free parameters), and free latent factor means for every group
except one reference group, whose latent means are fixed at 0 for
identification (standard SEM identification convention -- see e.g. Bollen,
1989). Omitting the free latent means for the non-reference group silently
over-constrains the model: it fits "equal intercepts AND equal latent
means" instead of "equal intercepts alone", inflating the scalar-stage chi2
and its degrees of freedom by exactly one parameter per factor.

Verified against the classic Holzinger & Swineford (1939) multi-group CFA
benchmark in tests/test_measurement_invariance_hs39.py.
"""

import numpy as np
import semopy
from scipy.optimize import minimize


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


def _lambda_positions(model):
    """For each active parameter, in the same order used by
    model.get_objective()'s x vector, return its (row, col) position in
    mx_lambda if it is a loading parameter, else None."""
    positions = []
    for name, p in model.parameters.items():
        if not p.active:
            continue
        loc = p.locations[0]
        positions.append(loc.indices if loc.matrix is model.mx_lambda else None)
    return positions


def _group_term(model, fun, grad, x_g, tau, xbar, kappa=None, lambda_pos=None):
    """Augmented normal-theory ML discrepancy for one group: covariance term
    (semopy's validated MLW) + mean term. `fun(x_g)` updates the model's
    internal matrices (incl. mx_lambda) as a side effect, so mx_lambda is
    current by the time calc_sigma()/mu are computed below.

    If `kappa` is given (this group's free latent factor means), the
    model-implied mean is tau + Lambda(theta) @ kappa instead of just tau,
    and the gradient picks up the cross-derivative through Lambda for
    loading parameters (identified via `lambda_pos`)."""
    fcov = fun(x_g)
    zeros_kappa = np.zeros_like(kappa) if kappa is not None else None
    if not np.isfinite(fcov):
        return 1e8, np.zeros_like(x_g), np.zeros_like(tau), zeros_kappa
    try:
        sigma, (m, c) = model.calc_sigma()
        inv_sigma = np.linalg.inv(sigma)
    except np.linalg.LinAlgError:
        return 1e8, np.zeros_like(x_g), np.zeros_like(tau), zeros_kappa

    mu = tau + model.mx_lambda @ kappa if kappa is not None else tau
    r = xbar - mu
    fmean = r @ inv_sigma @ r
    sigma_grad = model.calc_sigma_grad(m, c)
    grad_theta = grad(x_g) + np.array(
        [-(r @ inv_sigma @ g @ inv_sigma @ r) for g in sigma_grad]
    )
    isr = inv_sigma @ r

    grad_kappa = None
    if kappa is not None:
        grad_kappa = -2 * (model.mx_lambda.T @ isr)
        for p_idx, pos in enumerate(lambda_pos):
            if pos is not None:
                row, col = pos
                grad_theta[p_idx] += -2 * kappa[col] * isr[row]

    grad_tau = -2 * isr
    return fcov + fmean, grad_theta, grad_tau, grad_kappa


def fit_scalar_multigroup(df1, df2, desc, all_items, n_factors):
    """Two-group scalar invariance fit (loadings + intercepts constrained
    equal across groups). Group 1 is the identification reference (latent
    means fixed at 0); group 2's latent means (`kappa`, length n_factors)
    are estimated freely -- this is what makes the between-group latent
    mean comparison possible once scalar invariance holds.

    Parameters
    ----------
    df1, df2 : DataFrame  (group 1 = reference, group 2 = comparison)
    desc : str  semopy model description with shared INV_L_* loading labels
           (i.e. already built for metric invariance)
    all_items : list[str]  all observed item names, in a fixed order
    n_factors : int  number of latent factors in `desc`

    Returns
    -------
    dict with chi2, dof, n_params, success, kappa (group 2's estimated
    latent factor means, in factor order), and the fitted OptimizeResult.
    """
    P = len(all_items)
    m1 = semopy.Model(desc)
    m2 = semopy.Model(desc)
    m1.load(df1)
    m2.load(df2)

    global_index, global_start, bounds = {}, [], []
    map1 = _joint_register(m1, "G1", global_index, global_start, bounds)
    map2 = _joint_register(m2, "G2", global_index, global_start, bounds)

    tau_start = len(global_start)
    xbar1 = df1[all_items].mean().values
    xbar2 = df2[all_items].mean().values
    n1, n2 = m1.n_samples, m2.n_samples
    tau0 = (xbar1 * n1 + xbar2 * n2) / (n1 + n2)
    for v in tau0:
        global_start.append(v)
        bounds.append((None, None))
    tau_idx = np.arange(tau_start, tau_start + P)

    kappa_start = len(global_start)
    for _ in range(n_factors):
        global_start.append(0.0)
        bounds.append((None, None))
    kappa_idx = np.arange(kappa_start, kappa_start + n_factors)

    lambda_pos2 = _lambda_positions(m2)

    fun1, grad1 = m1.get_objective("MLW")
    fun2, grad2 = m2.get_objective("MLW")

    def objective(x):
        x1, x2, tau, kappa = x[map1], x[map2], x[tau_idx], x[kappa_idx]
        f1, g1, gt1, _ = _group_term(m1, fun1, grad1, x1, tau, xbar1)
        f2, g2, gt2, gk2 = _group_term(
            m2, fun2, grad2, x2, tau, xbar2, kappa=kappa, lambda_pos=lambda_pos2
        )
        val = n1 * f1 + n2 * f2
        g = np.zeros_like(x)
        np.add.at(g, map1, n1 * g1)
        np.add.at(g, map2, n2 * g2)
        g[tau_idx] += n1 * gt1 + n2 * gt2
        g[kappa_idx] += n2 * gk2
        return val, g

    x0 = np.array(global_start, dtype=float)
    res = minimize(objective, x0, jac=True, method="SLSQP", bounds=bounds,
                    options={"maxiter": 5000, "ftol": 1e-12})

    m1.param_vals = res.x[map1]
    m1.update_matrices(res.x[map1])
    m2.param_vals = res.x[map2]
    m2.update_matrices(res.x[map2])

    n_params = len(res.x)
    dof = P * (P + 3) - n_params
    return dict(
        chi2=res.fun, dof=dof, n_params=n_params, success=res.success,
        kappa=res.x[kappa_idx], m1=m1, m2=m2, res=res,
    )
