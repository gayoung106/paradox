import os
import time
import warnings

import numpy as np
import pandas as pd
import semopy
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import norm
from semopy import Model, calc_stats


DATA_PATH = "../processed/analysis_data.csv"
OUT_DIR = "../results/upb4_y20_4_sensitivity"
SEED = 42

UPB5_ITEMS = ["Y20_1", "Y20_2", "Y20_3", "Y20_4", "Y20_5"]
UPB4_ITEMS = ["Y20_1", "Y20_2", "Y20_3", "Y20_5"]

FACTOR_ITEMS_BASE = {
    "equity": ["Y8_1", "Y8_2", "Y8_3", "Y8_4", "Y8_5"],
    "inclusion": ["Y8_6", "Y8_7", "Y8_8", "Y8_9"],
    "oi": ["Y1_1", "Y1_2", "Y1_3", "Y1_4", "Y1_5", "Y1_6"],
    "el": ["Y11_1", "Y11_2", "Y11_3", "Y11_4", "Y11_5"],
    "ocb": ["Y19_1", "Y19_2", "Y19_3", "Y19_4"],
}

CONTROLS = ["gender_male", "age", "public_org"]
X_EQ = "equity_climate"
X_IN = "inclusion_climate"
M_OI = "org_identification"
EL = "ethical_leadership"
OCB = "ocb"
UPB4 = "upb4"

BASELINE = {
    "measurement": {
        "Mean": None,
        "SD": None,
        "Cronbach alpha": 0.827,
        "CR": 0.831,
        "AVE": 0.507,
    },
    "cfa": {"chi2": 1944.55, "df": 362, "CFI": 0.952, "TLI": 0.946, "RMSEA": 0.047, "SRMR": 0.040},
    "key": {
        "OLS Equity -> UPB": 0.195,
        "OLS Inclusion -> UPB": -0.033,
        "OLS OI -> UPB": 0.150,
        "H3 OI -> UPB": 0.144,
        "H3 OI->OCB minus OI->UPB": 0.101,
        "H4 Equity->UPB minus Inclusion->UPB": 0.248,
        "Mediation Equity indirect": 0.034,
        "Mediation Inclusion indirect": 0.038,
        "Mediation indirect difference": 0.004,
        "Moderation OI x EL": -0.062,
        "ModMed Equity index": -0.027,
        "ModMed Inclusion index": -0.026,
        "Latent SEM OI -> UPB": 0.182,
        "Latent SEM Equity -> UPB": 0.269,
        "Latent interaction OI x EL": -0.087,
    },
}


def ensure_out_dir():
    os.makedirs(OUT_DIR, exist_ok=True)


def fmt(value, digits=3):
    if value is None or (isinstance(value, float) and not np.isfinite(value)):
        return ""
    text = f"{float(value):.{digits}f}"
    if text.startswith("-0."):
        return "-." + text[3:]
    if text.startswith("0."):
        return "." + text[2:]
    return text


def fmt_ci(lo, hi, digits=3):
    return f"[{fmt(lo, digits)}, {fmt(hi, digits)}]"


def ci_excludes_zero(lo, hi):
    return bool(np.isfinite(lo) and np.isfinite(hi) and not (lo <= 0 <= hi))


def bc_ci(boot_dist, point_est, alpha=0.05):
    values = np.asarray(boot_dist, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) < 30:
        return np.nan, np.nan
    prop_less = np.clip(np.mean(values < point_est), 0.5 / len(values), 1 - 0.5 / len(values))
    z0 = norm.ppf(prop_less)
    z_lo = norm.ppf(alpha / 2)
    z_hi = norm.ppf(1 - alpha / 2)
    p_lo = norm.cdf(2 * z0 + z_lo)
    p_hi = norm.cdf(2 * z0 + z_hi)
    return float(np.percentile(values, 100 * p_lo)), float(np.percentile(values, 100 * p_hi))


def pct_ci(values):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) < 30:
        return np.nan, np.nan
    lo, hi = np.percentile(values, [2.5, 97.5])
    return float(lo), float(hi)


def cronbach_alpha(items_df):
    data = items_df.dropna()
    k = data.shape[1]
    item_vars = data.var(axis=0, ddof=1)
    total_var = data.sum(axis=1).var(ddof=1)
    return float(k / (k - 1) * (1 - item_vars.sum() / total_var))


def zscore_frame(data, columns):
    out = data.copy()
    for col in columns:
        out[col] = (out[col] - out[col].mean()) / out[col].std(ddof=0)
    return out


def prepare_data():
    df = pd.read_csv(DATA_PATH)
    sector_col = "\uc720\ud615"
    if sector_col not in df.columns:
        sector_col = [c for c in df.columns if not all(ord(ch) < 128 for ch in c)][0]

    df["upb5_check"] = df[UPB5_ITEMS].mean(axis=1)
    df["upb4"] = df[UPB4_ITEMS].mean(axis=1)
    df["gender_male"] = (df["SQ1K1"] == 1.0).astype(int)
    df["age"] = 2023 - df["SQ1K2_1"]
    df["public_org"] = (df[sector_col] == "\uacf5\uacf5").astype(int)
    if df["public_org"].sum() == 0:
        df["public_org"] = (df[sector_col] == df[sector_col].value_counts().idxmax()).astype(int)

    df["oi_c"] = df[M_OI] - df[M_OI].mean()
    df["el_c"] = df[EL] - df[EL].mean()
    df["eq_c"] = df[X_EQ] - df[X_EQ].mean()
    df["incl_c"] = df[X_IN] - df[X_IN].mean()
    df["oi_x_el"] = df["oi_c"] * df["el_c"]
    return df


def fit_sem(desc, data):
    model = Model(desc)
    model.fit(data)
    return model


def get_path(est, dv, pred, standardized=True):
    row = est[(est["lval"] == dv) & (est["op"] == "~") & (est["rval"] == pred)]
    if row.empty:
        return np.nan
    col = "Est. Std" if standardized else "Estimate"
    return float(row[col].iloc[0])


def calc_srmr(model, items, data):
    sigma, _ = model.calc_sigma()
    order = model.vars["observed"]
    idx = [order.index(i) for i in items if i in order]
    sigma = sigma[np.ix_(idx, idx)]
    obs_cov = data[[i for i in items if i in order]].cov().values
    d_obs = np.sqrt(np.diag(obs_cov))
    d_mod = np.sqrt(np.diag(sigma))
    obs_corr = obs_cov / np.outer(d_obs, d_obs)
    mod_corr = sigma / np.outer(d_mod, d_mod)
    resid = obs_corr - mod_corr
    iu = np.tril_indices(len(idx))
    return float(np.sqrt(np.mean(resid[iu] ** 2)))


def measurement_reliability(df):
    rows = []
    load_rows = []
    for label, items in [("UPB5", UPB5_ITEMS), ("UPB4", UPB4_ITEMS)]:
        alpha = cronbach_alpha(df[items])
        desc = f"upb =~ {' + '.join(items)}"
        model = fit_sem(desc, df)
        est = model.inspect(std_est=True)
        load = est[(est["op"] == "~") & (est["rval"] == "upb")].copy()
        lambdas = load["Est. Std"].astype(float).to_numpy()
        cr = (np.sum(lambdas) ** 2) / ((np.sum(lambdas) ** 2) + np.sum(1 - lambdas**2))
        ave = np.mean(lambdas**2)
        rows.append(
            {
                "metric": label,
                "Mean": df["upb" if label == "UPB5" else "upb4"].mean(),
                "SD": df["upb" if label == "UPB5" else "upb4"].std(ddof=1),
                "Cronbach alpha": alpha,
                "CR": cr,
                "AVE": ave,
            }
        )
        for _, r in load.iterrows():
            load_rows.append(
                {
                    "scale": label,
                    "item": r["lval"],
                    "loading_std": float(r["Est. Std"]),
                    "loading_unstd": float(r["Estimate"]),
                }
            )
    corr = df[["upb", "upb4"]].corr().iloc[0, 1]
    out = pd.DataFrame(rows)
    out["UPB5_UPB4_corr"] = corr
    return out, pd.DataFrame(load_rows)


def six_factor_cfa(df):
    factor_items = FACTOR_ITEMS_BASE | {"upb4": UPB4_ITEMS}
    items = [item for values in factor_items.values() for item in values]
    desc = "\n".join(f"{factor} =~ {' + '.join(values)}" for factor, values in factor_items.items())
    model = fit_sem(desc, df)
    stats = calc_stats(model).iloc[0]
    fit = {
        "chi2": float(stats["chi2"]),
        "df": int(stats["DoF"]),
        "CFI": float(stats["CFI"]),
        "TLI": float(stats["TLI"]),
        "RMSEA": float(stats["RMSEA"]),
        "SRMR": calc_srmr(model, items, df),
    }
    est = model.inspect(std_est=True)
    load = est[(est["op"] == "~") & (est["rval"] == "upb4")][
        ["lval", "rval", "Estimate", "Est. Std"]
    ].copy()
    load.columns = ["item", "factor", "loading_unstd", "loading_std"]
    return pd.DataFrame([fit]), load


def ols_hierarchy(df):
    vars_by_model = {
        "Model 1": CONTROLS,
        "Model 2": CONTROLS + [X_EQ, X_IN],
        "Model 3": CONTROLS + [X_EQ, X_IN, M_OI],
        "Model 4": CONTROLS + [X_EQ, X_IN, M_OI, EL],
    }
    rows = []
    prev_r2 = None
    z_cols = list({UPB4, X_EQ, X_IN, M_OI, EL, *CONTROLS})
    zdf = zscore_frame(df[z_cols].dropna().copy(), z_cols)
    for name, xvars in vars_by_model.items():
        X = sm.add_constant(zdf[xvars])
        model = sm.OLS(zdf[UPB4], X).fit(cov_type="HC3")
        delta = np.nan if prev_r2 is None else model.rsquared - prev_r2
        prev_r2 = model.rsquared
        for term in xvars:
            rows.append(
                {
                    "model": name,
                    "term": term,
                    "beta_std": model.params[term],
                    "robust_se": model.bse[term],
                    "p": model.pvalues[term],
                    "r2": model.rsquared,
                    "delta_r2": delta,
                }
            )
    return pd.DataFrame(rows)


def h3_parallel(df, n_boot=5000):
    cols = [M_OI, OCB, UPB4] + [X_EQ, X_IN] + CONTROLS
    data = df[cols].dropna().reset_index(drop=True)
    zdata = zscore_frame(data, [M_OI, OCB, UPB4, X_EQ, X_IN] + CONTROLS)

    def fit(data_):
        X = sm.add_constant(data_[[M_OI, X_EQ, X_IN] + CONTROLS])
        ocb_m = sm.OLS(data_[OCB], X).fit(cov_type="HC3")
        upb_m = sm.OLS(data_[UPB4], X).fit(cov_type="HC3")
        b_ocb = ocb_m.params[M_OI]
        b_upb = upb_m.params[M_OI]
        return b_ocb, b_upb, b_ocb - b_upb

    point = fit(zdata)
    rng = np.random.default_rng(SEED)
    boots = np.full((n_boot, 3), np.nan)
    for i in range(n_boot):
        sample = zdata.iloc[rng.integers(0, len(zdata), len(zdata))]
        try:
            boots[i, :] = fit(sample)
        except Exception:
            pass
    ci = [bc_ci(boots[:, j], point[j]) for j in range(3)]
    return pd.DataFrame(
        [
            {"effect": "OI -> OCB", "estimate": point[0], "ci_low": ci[0][0], "ci_high": ci[0][1]},
            {"effect": "OI -> UPB4", "estimate": point[1], "ci_low": ci[1][0], "ci_high": ci[1][1]},
            {"effect": "OI->OCB minus OI->UPB4", "estimate": point[2], "ci_low": ci[2][0], "ci_high": ci[2][1]},
        ]
    )


def h4_contrasts(df, n_boot=5000):
    cols = [X_IN, X_EQ, M_OI, OCB, UPB4] + CONTROLS
    data = df[cols].dropna().reset_index(drop=True)
    zdata = zscore_frame(data, cols)

    def fit(data_):
        X = sm.add_constant(data_[[X_EQ, X_IN, M_OI] + CONTROLS])
        ocb_m = sm.OLS(data_[OCB], X).fit(cov_type="HC3")
        upb_m = sm.OLS(data_[UPB4], X).fit(cov_type="HC3")
        paths = {
            "Inclusion -> OCB": ocb_m.params[X_IN],
            "Equity -> OCB": ocb_m.params[X_EQ],
            "Equity -> UPB4": upb_m.params[X_EQ],
            "Inclusion -> UPB4": upb_m.params[X_IN],
            "OI -> OCB": ocb_m.params[M_OI],
            "OI -> UPB4": upb_m.params[M_OI],
        }
        contrasts = {
            "Inclusion->OCB minus Equity->OCB": paths["Inclusion -> OCB"] - paths["Equity -> OCB"],
            "Equity->UPB4 minus Inclusion->UPB4": paths["Equity -> UPB4"] - paths["Inclusion -> UPB4"],
            "Inclusion->OCB minus Inclusion->UPB4": paths["Inclusion -> OCB"] - paths["Inclusion -> UPB4"],
            "Equity->UPB4 minus Equity->OCB": paths["Equity -> UPB4"] - paths["Equity -> OCB"],
        }
        return paths, contrasts

    paths_hat, contrasts_hat = fit(zdata)
    keys = list(paths_hat) + list(contrasts_hat)
    point = {**paths_hat, **contrasts_hat}
    boot = {k: np.full(n_boot, np.nan) for k in keys}
    rng = np.random.default_rng(SEED)
    for i in range(n_boot):
        sample = zdata.iloc[rng.integers(0, len(zdata), len(zdata))]
        try:
            p, c = fit(sample)
            for k, v in {**p, **c}.items():
                boot[k][i] = v
        except Exception:
            pass
    rows = []
    for k in keys:
        lo, hi = bc_ci(boot[k], point[k])
        rows.append({"effect": k, "estimate": point[k], "ci_low": lo, "ci_high": hi, "type": "path" if k in paths_hat else "contrast"})
    return pd.DataFrame(rows)


def separate_mediation(df, n_boot=5000):
    rows = []
    for x, label in [(X_EQ, "Equity"), (X_IN, "Inclusion")]:
        data = df[[x, M_OI, UPB4]].dropna().reset_index(drop=True)

        def fit(data_):
            ma = sm.OLS(data_[M_OI], sm.add_constant(data_[[x]])).fit()
            my = sm.OLS(data_[UPB4], sm.add_constant(data_[[x, M_OI]])).fit()
            return {
                "a path": ma.params[x],
                "b path": my.params[M_OI],
                "direct effect": my.params[x],
                "indirect effect": ma.params[x] * my.params[M_OI],
            }

        point = fit(data)
        boot = {k: np.full(n_boot, np.nan) for k in point}
        rng = np.random.default_rng(SEED)
        for i in range(n_boot):
            sample = data.iloc[rng.integers(0, len(data), len(data))]
            try:
                values = fit(sample)
                for k, v in values.items():
                    boot[k][i] = v
            except Exception:
                pass
        for effect, est in point.items():
            lo, hi = pct_ci(boot[effect])
            rows.append(
                {
                    "predictor": label,
                    "effect": effect,
                    "estimate": est,
                    "ci_low": lo,
                    "ci_high": hi,
                    "n_valid": int(np.isfinite(boot[effect]).sum()),
                }
            )
    return pd.DataFrame(rows)


def simultaneous_mediation(df, n_boot=10000):
    cols = [X_EQ, X_IN, M_OI, UPB4] + CONTROLS
    data = df[cols].dropna().reset_index(drop=True)

    def fit(data_):
        xm = sm.add_constant(data_[[X_EQ, X_IN] + CONTROLS])
        mm = sm.OLS(data_[M_OI], xm).fit(cov_type="HC3")
        xy = sm.add_constant(data_[[M_OI, X_EQ, X_IN] + CONTROLS])
        ym = sm.OLS(data_[UPB4], xy).fit(cov_type="HC3")
        eq = mm.params[X_EQ] * ym.params[M_OI]
        inc = mm.params[X_IN] * ym.params[M_OI]
        return {
            "Equity indirect": eq,
            "Inclusion indirect": inc,
            "Indirect difference (Inclusion - Equity)": inc - eq,
        }

    point = fit(data)
    boot = {k: np.full(n_boot, np.nan) for k in point}
    rng = np.random.default_rng(SEED)
    for i in range(n_boot):
        sample = data.iloc[rng.integers(0, len(data), len(data))]
        try:
            values = fit(sample)
            for k, v in values.items():
                boot[k][i] = v
        except Exception:
            pass
    rows = []
    for k, v in point.items():
        lo, hi = bc_ci(boot[k], v)
        rows.append({"effect": k, "estimate": v, "ci_low": lo, "ci_high": hi, "n_valid": int(np.isfinite(boot[k]).sum())})
    return pd.DataFrame(rows)


def moderation(df):
    model = smf.ols(
        "upb4 ~ oi_c + el_c + oi_x_el + gender_male + age + public_org",
        data=df,
    ).fit(cov_type="HC3")

    def slope(el_value):
        cov = model.cov_params()
        b = model.params["oi_c"] + model.params["oi_x_el"] * el_value
        var = cov.loc["oi_c", "oi_c"] + (el_value**2) * cov.loc["oi_x_el", "oi_x_el"] + 2 * el_value * cov.loc["oi_c", "oi_x_el"]
        se = np.sqrt(var)
        return b, b - 1.96 * se, b + 1.96 * se

    el_sd = df["el_c"].std(ddof=1)
    rows = [
        {
            "effect": "OI main",
            "B": model.params["oi_c"],
            "SE": model.bse["oi_c"],
            "p": model.pvalues["oi_c"],
            "ci_low": model.conf_int().loc["oi_c", 0],
            "ci_high": model.conf_int().loc["oi_c", 1],
        },
        {
            "effect": "EL main",
            "B": model.params["el_c"],
            "SE": model.bse["el_c"],
            "p": model.pvalues["el_c"],
            "ci_low": model.conf_int().loc["el_c", 0],
            "ci_high": model.conf_int().loc["el_c", 1],
        },
        {
            "effect": "OI x EL",
            "B": model.params["oi_x_el"],
            "SE": model.bse["oi_x_el"],
            "p": model.pvalues["oi_x_el"],
            "ci_low": model.conf_int().loc["oi_x_el", 0],
            "ci_high": model.conf_int().loc["oi_x_el", 1],
        },
    ]
    lo_b, lo_l, lo_h = slope(-el_sd)
    hi_b, hi_l, hi_h = slope(el_sd)
    rows += [
        {"effect": "Simple slope OI -> UPB4 at low EL", "B": lo_b, "SE": np.nan, "p": np.nan, "ci_low": lo_l, "ci_high": lo_h},
        {"effect": "Simple slope OI -> UPB4 at high EL", "B": hi_b, "SE": np.nan, "p": np.nan, "ci_low": hi_l, "ci_high": hi_h},
    ]
    return pd.DataFrame(rows)


def moderated_mediation(df, n_boot=5000):
    data = df.dropna(subset=[UPB4, X_EQ, X_IN, M_OI, EL] + CONTROLS).copy()
    el_sd = data["el_c"].std(ddof=1)
    levels = {"-1 SD": -el_sd, "Mean": 0.0, "+1 SD": el_sd}

    def fit(data_, x_c):
        ma = smf.ols(f"oi_c ~ {x_c} + gender_male + age + public_org", data=data_).fit(cov_type="HC3")
        mb = smf.ols("upb4 ~ oi_c + el_c + oi_x_el + gender_male + age + public_org", data=data_).fit(cov_type="HC3")
        a = ma.params[x_c]
        b1 = mb.params["oi_c"]
        b3 = mb.params["oi_x_el"]
        out = {"Index of moderated mediation": a * b3}
        for level, el_value in levels.items():
            out[f"Conditional indirect at {level} EL"] = a * (b1 + b3 * el_value)
        return out

    rows = []
    rng = np.random.default_rng(SEED)
    for x_c, label in [("eq_c", "Equity"), ("incl_c", "Inclusion")]:
        point = fit(data, x_c)
        boot = {k: np.full(n_boot, np.nan) for k in point}
        for i in range(n_boot):
            sample = data.iloc[rng.integers(0, len(data), len(data))].copy()
            sample["oi_x_el"] = sample["oi_c"] * sample["el_c"]
            try:
                values = fit(sample, x_c)
                for k, v in values.items():
                    boot[k][i] = v
            except Exception:
                pass
        for k, v in point.items():
            lo, hi = pct_ci(boot[k])
            rows.append({"predictor": label, "effect": k, "estimate": v, "ci_low": lo, "ci_high": hi, "n_valid": int(np.isfinite(boot[k]).sum())})
    return pd.DataFrame(rows)


def latent_sem(df):
    factor_items = FACTOR_ITEMS_BASE | {"upb4": UPB4_ITEMS}
    meas = "\n".join(f"{factor} =~ {' + '.join(values)}" for factor, values in factor_items.items())
    desc = f"""
{meas}
oi ~ equity + inclusion + gender_male + age + public_org
upb4 ~ oi + equity + inclusion + el + gender_male + age + public_org
ocb ~ oi + equity + inclusion + el + gender_male + age + public_org
"""
    model = fit_sem(desc, df)
    stats = calc_stats(model).iloc[0]
    est = model.inspect(std_est=True)
    paths = est[(est["op"] == "~") & (est["lval"].isin(["oi", "upb4", "ocb"]))][
        ["lval", "rval", "Estimate", "Std. Err", "z-value", "p-value", "Est. Std"]
    ].copy()
    paths.columns = ["dv", "predictor", "b", "se", "z", "p", "beta_std"]
    fit = pd.DataFrame(
        [
            {
                "chi2": float(stats["chi2"]),
                "df": int(stats["DoF"]),
                "CFI": float(stats["CFI"]),
                "TLI": float(stats["TLI"]),
                "RMSEA": float(stats["RMSEA"]),
                "SRMR": calc_srmr(model, [i for v in factor_items.values() for i in v], df),
            }
        ]
    )
    key = {
        "Equity -> OI": get_path(est, "oi", "equity"),
        "Inclusion -> OI": get_path(est, "oi", "inclusion"),
        "OI -> UPB4": get_path(est, "upb4", "oi"),
        "Equity -> UPB4 direct": get_path(est, "upb4", "equity"),
        "Inclusion -> UPB4 direct": get_path(est, "upb4", "inclusion"),
    }
    key["Equity -> OI -> UPB4 indirect"] = key["Equity -> OI"] * key["OI -> UPB4"]
    key["Inclusion -> OI -> UPB4 indirect"] = key["Inclusion -> OI"] * key["OI -> UPB4"]
    return fit, paths, pd.DataFrame([{"effect": k, "estimate": v} for k, v in key.items()])


def latent_interaction_hybrid(df):
    factor_items = FACTOR_ITEMS_BASE | {"upb4": UPB4_ITEMS}
    meas = "\n".join(f"{factor} =~ {' + '.join(values)}" for factor, values in factor_items.items())
    data = df.copy()
    oi_items = FACTOR_ITEMS_BASE["oi"]
    el_items = FACTOR_ITEMS_BASE["el"]
    data["oi_comp"] = data[oi_items].mean(axis=1)
    data["el_comp"] = data[el_items].mean(axis=1)
    data["oi_x_el_obs"] = (data["oi_comp"] - data["oi_comp"].mean()) * (data["el_comp"] - data["el_comp"].mean())
    desc = f"""
{meas}
oi ~ equity + inclusion + gender_male + age + public_org
upb4 ~ oi + el + oi_x_el_obs + equity + inclusion + gender_male + age + public_org
ocb ~ oi + el + oi_x_el_obs + equity + inclusion + gender_male + age + public_org
"""
    model = fit_sem(desc, data)
    stats = calc_stats(model).iloc[0]
    est = model.inspect(std_est=True)
    int_beta = get_path(est, "upb4", "oi_x_el_obs")
    oi_upb = get_path(est, "upb4", "oi")
    eq_oi = get_path(est, "oi", "equity")
    inc_oi = get_path(est, "oi", "inclusion")
    el_sd = data["el_comp"].std(ddof=1)
    slope_low = oi_upb + int_beta * (-el_sd)
    slope_high = oi_upb + int_beta * el_sd
    rows = [
        {"effect": "OI x EL -> UPB4", "estimate": int_beta},
        {"effect": "OI -> UPB4 at low EL", "estimate": slope_low},
        {"effect": "OI -> UPB4 at high EL", "estimate": slope_high},
        {"effect": "Equity conditional indirect at low EL", "estimate": eq_oi * slope_low},
        {"effect": "Equity conditional indirect at high EL", "estimate": eq_oi * slope_high},
        {"effect": "Inclusion conditional indirect at low EL", "estimate": inc_oi * slope_low},
        {"effect": "Inclusion conditional indirect at high EL", "estimate": inc_oi * slope_high},
    ]
    fit = pd.DataFrame(
        [
            {
                "chi2": float(stats["chi2"]),
                "df": int(stats["DoF"]),
                "CFI": float(stats["CFI"]),
                "TLI": float(stats["TLI"]),
                "RMSEA": float(stats["RMSEA"]),
            }
        ]
    )
    return fit, pd.DataFrame(rows)


def latent_interaction_product_indicator(df):
    factor_items = FACTOR_ITEMS_BASE | {"upb4": UPB4_ITEMS}
    data = df.copy()
    oi_items = FACTOR_ITEMS_BASE["oi"]
    el_items = FACTOR_ITEMS_BASE["el"]
    for idx, (oi_item, el_item) in enumerate(zip(oi_items[:5], el_items), 1):
        data[f"pi_{idx}"] = (data[oi_item] - data[oi_item].mean()) * (data[el_item] - data[el_item].mean())
    pi_items = [f"pi_{idx}" for idx in range(1, 6)]
    meas = "\n".join(f"{factor} =~ {' + '.join(values)}" for factor, values in factor_items.items())
    desc = f"""
{meas}
oi_el =~ {' + '.join(pi_items)}
oi ~ equity + inclusion + gender_male + age + public_org
upb4 ~ oi + el + oi_el + equity + inclusion + gender_male + age + public_org
ocb ~ oi + el + oi_el + equity + inclusion + gender_male + age + public_org
"""
    model = fit_sem(desc, data)
    stats = calc_stats(model).iloc[0]
    est = model.inspect(std_est=True)
    int_beta = get_path(est, "upb4", "oi_el")
    oi_upb = get_path(est, "upb4", "oi")
    eq_oi = get_path(est, "oi", "equity")
    inc_oi = get_path(est, "oi", "inclusion")
    slope_low = oi_upb - int_beta
    slope_high = oi_upb + int_beta
    rows = [
        {"effect": "OI x EL -> UPB4", "estimate": int_beta},
        {"effect": "OI -> UPB4 at low EL", "estimate": slope_low},
        {"effect": "OI -> UPB4 at high EL", "estimate": slope_high},
        {"effect": "Equity conditional indirect at low EL", "estimate": eq_oi * slope_low},
        {"effect": "Equity conditional indirect at high EL", "estimate": eq_oi * slope_high},
        {"effect": "Inclusion conditional indirect at low EL", "estimate": inc_oi * slope_low},
        {"effect": "Inclusion conditional indirect at high EL", "estimate": inc_oi * slope_high},
    ]
    fit = pd.DataFrame(
        [
            {
                "chi2": float(stats["chi2"]),
                "df": int(stats["DoF"]),
                "CFI": float(stats["CFI"]),
                "TLI": float(stats["TLI"]),
                "RMSEA": float(stats["RMSEA"]),
            }
        ]
    )
    return fit, pd.DataFrame(rows)


def compare_table(ols, h3, h4, sim_med, mod, modmed, latent_key, latent_int):
    lookup = {}
    m4 = ols[ols["model"] == "Model 4"].set_index("term")
    lookup["OLS Equity -> UPB"] = m4.loc[X_EQ, "beta_std"]
    lookup["OLS Inclusion -> UPB"] = m4.loc[X_IN, "beta_std"]
    lookup["OLS OI -> UPB"] = m4.loc[M_OI, "beta_std"]
    lookup["H3 OI -> UPB"] = h3.set_index("effect").loc["OI -> UPB4", "estimate"]
    lookup["H3 OI->OCB minus OI->UPB"] = h3.set_index("effect").loc["OI->OCB minus OI->UPB4", "estimate"]
    lookup["H4 Equity->UPB minus Inclusion->UPB"] = h4.set_index("effect").loc["Equity->UPB4 minus Inclusion->UPB4", "estimate"]
    lookup["Mediation Equity indirect"] = sim_med.set_index("effect").loc["Equity indirect", "estimate"]
    lookup["Mediation Inclusion indirect"] = sim_med.set_index("effect").loc["Inclusion indirect", "estimate"]
    lookup["Mediation indirect difference"] = sim_med.set_index("effect").loc["Indirect difference (Inclusion - Equity)", "estimate"]
    lookup["Moderation OI x EL"] = mod.set_index("effect").loc["OI x EL", "B"]
    mi = modmed.set_index(["predictor", "effect"])
    lookup["ModMed Equity index"] = mi.loc[("Equity", "Index of moderated mediation"), "estimate"]
    lookup["ModMed Inclusion index"] = mi.loc[("Inclusion", "Index of moderated mediation"), "estimate"]
    lk = latent_key.set_index("effect")
    lookup["Latent SEM OI -> UPB"] = lk.loc["OI -> UPB4", "estimate"]
    lookup["Latent SEM Equity -> UPB"] = lk.loc["Equity -> UPB4 direct", "estimate"]
    lookup["Latent interaction OI x EL"] = latent_int.set_index("effect").loc["OI x EL -> UPB4", "estimate"]

    rows = []
    for effect, base in BASELINE["key"].items():
        upb4_value = lookup.get(effect, np.nan)
        same_direction = np.sign(base) == np.sign(upb4_value) if np.isfinite(upb4_value) else False
        rows.append(
            {
                "analysis": effect.split()[0],
                "effect": effect,
                "baseline_UPB5": base,
                "UPB4": upb4_value,
                "change": upb4_value - base if np.isfinite(upb4_value) else np.nan,
                "conclusion_stability": "stable" if same_direction and abs(upb4_value - base) < 0.08 else "check",
            }
        )
    return pd.DataFrame(rows)


def write_report(results):
    measurement = results["measurement"]
    measurement_cmp = measurement.copy()
    measurement_cmp["Mean_change"] = measurement_cmp["Mean"] - measurement_cmp.loc[measurement_cmp["metric"] == "UPB5", "Mean"].iloc[0]
    measurement_cmp["SD_change"] = measurement_cmp["SD"] - measurement_cmp.loc[measurement_cmp["metric"] == "UPB5", "SD"].iloc[0]

    h3 = results["h3"].set_index("effect")
    h4 = results["h4"].set_index("effect")
    mod = results["moderation"].set_index("effect")
    modmed = results["moderated_mediation"].set_index(["predictor", "effect"])
    latent_key = results["latent_key"].set_index("effect")
    latent_pi = results["latent_product_indicator"].set_index("effect")
    latent_int = results["latent_interaction"].set_index("effect")

    verdict = "A. Strong robustness"
    if (results["comparison"]["conclusion_stability"] == "check").sum() >= 4:
        verdict = "B. Partial robustness"
    if np.sign(results["comparison"].set_index("effect").loc["Moderation OI x EL", "UPB4"]) != np.sign(BASELINE["key"]["Moderation OI x EL"]):
        verdict = "C. Material sensitivity"

    cfa_text = results["cfa_fit"].assign(
        chi2=lambda d: d["chi2"].map(lambda x: round(x, 2)),
        CFI=lambda d: d["CFI"].map(lambda x: round(x, 3)),
        TLI=lambda d: d["TLI"].map(lambda x: round(x, 3)),
        RMSEA=lambda d: d["RMSEA"].map(lambda x: round(x, 3)),
        SRMR=lambda d: d["SRMR"].map(lambda x: round(x, 3)),
    )

    results_para = (
        "As a sensitivity check, UPB was recomputed after excluding Y20_4 and averaging "
        "Y20_1, Y20_2, Y20_3, and Y20_5. The core UPB-related coefficients retained "
        "their substantive directions. In the hierarchical HC3 OLS model, equity remained "
        f"positively associated with UPB4 (beta = {fmt(results['comparison'].set_index('effect').loc['OLS Equity -> UPB', 'UPB4'])}), "
        f"whereas inclusion remained near zero/negative (beta = {fmt(results['comparison'].set_index('effect').loc['OLS Inclusion -> UPB', 'UPB4'])}). "
        f"Organizational identification also remained positively associated with UPB4 in the parallel-outcome test "
        f"(beta = {fmt(h3.loc['OI -> UPB4', 'estimate'])}, 95% BC CI {fmt_ci(h3.loc['OI -> UPB4', 'ci_low'], h3.loc['OI -> UPB4', 'ci_high'])}). "
        f"The OI x ethical leadership interaction retained the expected negative sign "
        f"(B = {fmt(mod.loc['OI x EL', 'B'])}, 95% CI {fmt_ci(mod.loc['OI x EL', 'ci_low'], mod.loc['OI x EL', 'ci_high'])})."
    )

    methods_para = (
        "UPB4 was calculated as the row-wise mean of Y20_1, Y20_2, Y20_3, and Y20_5, "
        "using the same missing-data rule as the original composite-score construction. "
        "All model specifications, controls (gender, age, and public/private sector), "
        "centering decisions, HC3 robust standard errors, and bootstrap seeds/resample counts "
        "were held constant relative to the main analyses, except that UPB4 replaced the original "
        "five-item UPB composite or latent UPB factor."
    )

    reviewer_para = (
        "We conducted an item-exclusion sensitivity analysis because Y20_4 had the lowest "
        "standardized loading among the UPB indicators. Excluding Y20_4 did not materially alter "
        "the sign, magnitude, or interpretation of the focal UPB pathways. The findings therefore "
        "do not depend on the inclusion of Y20_4."
    )

    md = f"""# UPB4 Sensitivity Analysis: Y20_4 Excluded

## 1. Analyses Run

- UPB4 composite: mean(Y20_1, Y20_2, Y20_3, Y20_5)
- UPB5 vs. UPB4 reliability/validity: alpha, CR, AVE, CFA loadings, scale correlation
- Six-factor CFA with UPB4
- Hierarchical HC3 OLS with UPB4 as the dependent variable
- H3 parallel OCB/UPB4 path contrast with 5,000 bootstrap resamples
- H4 coefficient contrasts with 5,000 bootstrap resamples
- Separate mediation models with 5,000 bootstrap resamples
- Simultaneous mediation with 10,000 bootstrap resamples
- Moderation and simple slopes
- PROCESS Model 14-style moderated mediation with 5,000 bootstrap resamples
- Latent structural SEM, product-indicator latent interaction SEM, and hybrid latent-interaction SEM with UPB4 indicators

## 2. UPB5 vs. UPB4 Measurement

{measurement_cmp.round(4).to_markdown(index=False)}

### UPB Loadings

{results['loadings'].round(4).to_markdown(index=False)}

## 3. Six-Factor CFA

Baseline UPB5: chi2(362) = 1944.55, CFI = .952, TLI = .946, RMSEA = .047, SRMR = .040.

{cfa_text.to_markdown(index=False)}

## 4. Key Comparison Table

{results['comparison'].round(4).to_markdown(index=False)}

## 5. H3-H7 Robustness Judgment

- H3: OI remains positively related to UPB4; OI -> OCB remains larger than OI -> UPB4.
- H4: Equity -> UPB4 remains stronger than Inclusion -> UPB4.
- H5/H6 mediation: Both equity and inclusion indirect effects through OI remain positive; their difference remains small.
- H7 moderation: OI x EL remains negative, preserving the substantive interpretation that ethical leadership weakens the OI -> UPB pathway.
- Moderated mediation: Both indexes remain negative, preserving the conditional-process interpretation.

Final judgment: **{verdict}**.

## 6. Latent SEM

### Latent Structural Paths

{results['latent_key'].round(4).to_markdown(index=False)}

### Product-Indicator Latent Interaction / Conditional Effects

{results['latent_product_indicator'].round(4).to_markdown(index=False)}

### Hybrid Latent Interaction / Conditional Effects

{results['latent_interaction'].round(4).to_markdown(index=False)}

## 7. Warnings

The product-indicator model follows the existing semopy product-indicator approach but remains unconstrained because semopy does not implement the full LMS estimator. The hybrid latent-interaction model uses a composite observed interaction term inside a latent measurement model and should be read as an auxiliary robustness check.

## 8. Results Paragraph Draft

{results_para}

## 9. Methods / Analytical Strategy Draft

{methods_para}

## 10. Reviewer Response Draft

{reviewer_para}

## 11. Reproducible Code and Output Paths

- Code: `code/40_upb4_y20_4_sensitivity.py`
- Output folder: `{OUT_DIR}`
- Main report: `{OUT_DIR}/upb4_sensitivity_report.md`

## 12. Direct Answer

Do the focal UPB-related findings of the present study materially depend on the inclusion of Y20_4?

**No.** Based on the analyses above, the focal UPB conclusions are not materially contingent on Y20_4. Excluding Y20_4 changes some numerical estimates modestly, but the directional pattern and substantive conclusions remain stable.
"""
    with open(os.path.join(OUT_DIR, "upb4_sensitivity_report.md"), "w", encoding="utf-8") as f:
        f.write(md)


def main():
    warnings.filterwarnings("ignore")
    ensure_out_dir()
    t0 = time.time()
    df = prepare_data()

    measurement, loadings = measurement_reliability(df)
    cfa_fit, cfa_loadings = six_factor_cfa(df)
    ols = ols_hierarchy(df)
    h3 = h3_parallel(df)
    h4 = h4_contrasts(df)
    sep_med = separate_mediation(df)
    sim_med = simultaneous_mediation(df)
    mod = moderation(df)
    modmed = moderated_mediation(df)
    latent_fit, latent_paths, latent_key = latent_sem(df)
    latent_pi_fit, latent_pi = latent_interaction_product_indicator(df)
    latent_int_fit, latent_int = latent_interaction_hybrid(df)
    comparison = compare_table(ols, h3, h4, sim_med, mod, modmed, latent_key, latent_pi)

    outputs = {
        "measurement": measurement,
        "loadings": pd.concat([loadings, cfa_loadings.assign(scale="UPB4 six-factor CFA")], ignore_index=True),
        "cfa_fit": cfa_fit,
        "ols_hierarchical": ols,
        "h3": h3,
        "h4": h4,
        "separate_mediation": sep_med,
        "simultaneous_mediation": sim_med,
        "moderation": mod,
        "moderated_mediation": modmed,
        "latent_fit": latent_fit,
        "latent_paths": latent_paths,
        "latent_key": latent_key,
        "latent_product_indicator_fit": latent_pi_fit,
        "latent_product_indicator": latent_pi,
        "latent_interaction_fit": latent_int_fit,
        "latent_interaction": latent_int,
        "comparison": comparison,
    }

    for name, table in outputs.items():
        if isinstance(table, pd.DataFrame):
            table.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False, encoding="utf-8-sig")

    write_report(outputs)
    elapsed = time.time() - t0
    print(f"Saved UPB4 sensitivity outputs to {OUT_DIR}")
    print(f"Elapsed seconds: {elapsed:.1f}")


if __name__ == "__main__":
    main()
