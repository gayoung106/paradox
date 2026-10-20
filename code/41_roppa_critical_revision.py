"""Limited reanalysis for the ROPPA critical-methods review.

This script does not overwrite any pre-existing result.  It produces only the
two analyses not already available in the repository:

1. Staged HC3 regressions for the equity/inclusion suppression diagnosis.
2. Y8_4 / Y11_1 item-deletion sensitivity checks for the integrated SEM and
   the OI x ethical-leadership moderation.

All focal variables and controls follow the corrected existing scripts:
male = 1, age = 2024 - birth year, public = 1.  Standardized regressions use
population-SD z scores (ddof=0), matching code/21_h4_signature_direct_effects.py.
"""

from __future__ import annotations

import contextlib
import os
import platform
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import semopy
import statsmodels
import statsmodels.api as sm
from semopy import Model, calc_stats
from statsmodels.stats.outliers_influence import variance_inflation_factor


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "processed" / "analysis_data.csv"
OUT_DIR = ROOT / "reports" / "roppa_critical_revision"
TABLE_DIR = OUT_DIR / "tables"
LOG_DIR = OUT_DIR / "logs"
TABLE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = LOG_DIR / "41_roppa_critical_revision.log"


def zscore(frame: pd.DataFrame) -> pd.DataFrame:
    return (frame - frame.mean()) / frame.std(ddof=0)


def p_text(value: object) -> float:
    if value == "-" or pd.isna(value):
        return np.nan
    return float(value)


def srmr(model: Model, items: list[str], data: pd.DataFrame) -> float:
    sigma, _ = model.calc_sigma()
    order = model.vars["observed"]
    idx = [order.index(item) for item in items]
    sigma = sigma[np.ix_(idx, idx)]
    obs_cov = data[items].cov().values
    obs_corr = obs_cov / np.outer(np.sqrt(np.diag(obs_cov)), np.sqrt(np.diag(obs_cov)))
    mod_corr = sigma / np.outer(np.sqrt(np.diag(sigma)), np.sqrt(np.diag(sigma)))
    residual = obs_corr - mod_corr
    lower = np.tril_indices(len(items))
    return float(np.sqrt(np.mean(residual[lower] ** 2)))


def fit_hc3(zdata: pd.DataFrame, outcome: str, predictors: list[str]):
    x = sm.add_constant(zdata[predictors], has_constant="add")
    return sm.OLS(zdata[outcome], x).fit(cov_type="HC3")


def staged_regressions(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    controls = ["male", "age", "public"]
    specs = {
        "A_equity_only": controls + ["equity_climate"],
        "B_inclusion_only": controls + ["inclusion_climate"],
        "C_equity_inclusion": controls + ["equity_climate", "inclusion_climate"],
        "D_plus_OI": controls + ["equity_climate", "inclusion_climate", "org_identification"],
    }
    cols = sorted(set(sum(specs.values(), []) + ["ocb", "upb"]))
    zdata = zscore(df[cols].dropna())
    rows: list[dict] = []
    vif_rows: list[dict] = []
    for outcome in ["ocb", "upb"]:
        for model_name, predictors in specs.items():
            fit = fit_hc3(zdata, outcome, predictors)
            ci = fit.conf_int(alpha=0.05)
            for predictor in ["equity_climate", "inclusion_climate", "org_identification"]:
                if predictor in predictors:
                    rows.append({
                        "outcome": outcome,
                        "model": model_name,
                        "predictor": predictor,
                        "beta": fit.params[predictor],
                        "ci_low": ci.loc[predictor, 0],
                        "ci_high": ci.loc[predictor, 1],
                        "p": fit.pvalues[predictor],
                        "r_squared": fit.rsquared,
                        "n": int(fit.nobs),
                    })
            x = zdata[predictors]
            for index, predictor in enumerate(predictors):
                vif_rows.append({
                    "outcome": outcome,
                    "model": model_name,
                    "predictor": predictor,
                    "vif": variance_inflation_factor(x.values, index),
                })
    return pd.DataFrame(rows), pd.DataFrame(vif_rows)


BASE_FACTORS = {
    "equity": ["Y8_1", "Y8_2", "Y8_3", "Y8_4", "Y8_5"],
    "inclusion": ["Y8_6", "Y8_7", "Y8_8", "Y8_9"],
    "oi": ["Y1_1", "Y1_2", "Y1_3", "Y1_4", "Y1_5", "Y1_6"],
    "el": ["Y11_1", "Y11_2", "Y11_3", "Y11_4", "Y11_5"],
    "ocb": ["Y19_1", "Y19_2", "Y19_3", "Y19_4"],
    "upb": ["Y20_1", "Y20_2", "Y20_3", "Y20_4", "Y20_5"],
}


def factor_spec(variant: str) -> dict[str, list[str]]:
    factors = {name: items.copy() for name, items in BASE_FACTORS.items()}
    if variant == "drop_Y8_4":
        factors["equity"].remove("Y8_4")
    elif variant == "drop_Y11_1":
        factors["el"].remove("Y11_1")
    return factors


def build_sem_desc(factors: dict[str, list[str]]) -> str:
    measurement = "\n".join(
        f"{factor} =~ {' + '.join(items)}" for factor, items in factors.items()
    )
    return f"""
{measurement}
oi ~ equity + inclusion + male + age + public
upb ~ oi + equity + inclusion + el + male + age + public
ocb ~ oi + equity + inclusion + el + male + age + public
"""


def get_path(est: pd.DataFrame, dv: str, predictor: str) -> pd.Series:
    row = est[(est["lval"] == dv) & (est["op"] == "~") & (est["rval"] == predictor)]
    if row.empty:
        raise KeyError(f"Missing path {predictor} -> {dv}")
    return row.iloc[0]


def structural_sensitivity(df: pd.DataFrame):
    fit_rows: list[dict] = []
    path_rows: list[dict] = []
    validity_rows: list[dict] = []
    model_objects: dict[str, Model] = {}
    for variant in ["original", "drop_Y8_4", "drop_Y11_1"]:
        factors = factor_spec(variant)
        desc = build_sem_desc(factors)
        model = Model(desc)
        model.fit(df)
        model_objects[variant] = model
        stats = calc_stats(model).iloc[0]
        items = [item for values in factors.values() for item in values]
        fit_rows.append({
            "variant": variant,
            "chi2": float(stats["chi2"]),
            "df": int(stats["DoF"]),
            "CFI": float(stats["CFI"]),
            "TLI": float(stats["TLI"]),
            "RMSEA": float(stats["RMSEA"]),
            "SRMR": srmr(model, items, df),
            "n": len(df),
        })
        est = model.inspect(std_est=True)
        wanted = [
            ("oi", "equity"), ("oi", "inclusion"),
            ("upb", "oi"), ("ocb", "oi"),
            ("upb", "equity"), ("upb", "inclusion"),
            ("ocb", "equity"), ("ocb", "inclusion"),
        ]
        path_map: dict[tuple[str, str], float] = {}
        for dv, pred in wanted:
            row = get_path(est, dv, pred)
            beta = float(row["Est. Std"])
            path_map[(dv, pred)] = beta
            path_rows.append({
                "variant": variant,
                "path": f"{pred}->{dv}",
                "b": float(row["Estimate"]),
                "se": float(row["Std. Err"]),
                "z": float(row["z-value"]),
                "p_wald": p_text(row["p-value"]),
                "beta_std": beta,
            })
        path_rows.extend([
            {"variant": variant, "path": "equity->oi->upb", "b": np.nan, "se": np.nan,
             "z": np.nan, "p_wald": np.nan,
             "beta_std": path_map[("oi", "equity")] * path_map[("upb", "oi")]},
            {"variant": variant, "path": "inclusion->oi->upb", "b": np.nan, "se": np.nan,
             "z": np.nan, "p_wald": np.nan,
             "beta_std": path_map[("oi", "inclusion")] * path_map[("upb", "oi")]},
        ])
        for factor in ["equity", "el"]:
            loadings = est[
                (est["op"] == "~") & (est["rval"] == factor) &
                (est["lval"].isin(factors[factor]))
            ]["Est. Std"].astype(float).to_numpy()
            ave = float(np.mean(loadings ** 2))
            cr = float(np.sum(loadings) ** 2 /
                       (np.sum(loadings) ** 2 + np.sum(1 - loadings ** 2)))
            validity_rows.append({
                "variant": variant, "construct": factor,
                "n_items": len(loadings), "AVE": ave, "CR": cr,
                "min_loading": float(loadings.min()), "max_loading": float(loadings.max()),
            })
    return (pd.DataFrame(fit_rows), pd.DataFrame(path_rows),
            pd.DataFrame(validity_rows), model_objects)


def latent_h3_difference_bootstrap(
    df: pd.DataFrame, n_boot: int = 1000, seed: int = 20261020
) -> pd.DataFrame:
    """Percentile bootstrap for beta(OI->OCB) - beta(OI->UPB)."""
    factors = factor_spec("original")
    desc = build_sem_desc(factors)

    def estimate(data: pd.DataFrame) -> tuple[float, float, float]:
        model = Model(desc)
        model.fit(data)
        est = model.inspect(std_est=True)
        ocb = float(get_path(est, "ocb", "oi")["Est. Std"])
        upb = float(get_path(est, "upb", "oi")["Est. Std"])
        return ocb, upb, ocb - upb

    point = estimate(df)
    rng = np.random.default_rng(seed)
    draws = np.full((n_boot, 3), np.nan)
    for index in range(n_boot):
        sample_index = rng.integers(0, len(df), size=len(df))
        try:
            draws[index] = estimate(df.iloc[sample_index].reset_index(drop=True))
        except Exception:
            continue
    valid = draws[np.isfinite(draws).all(axis=1)]
    labels = ["OI->OCB", "OI->UPB", "difference_OCB_minus_UPB"]
    rows = []
    for column, label in enumerate(labels):
        low, high = np.percentile(valid[:, column], [2.5, 97.5])
        rows.append({
            "effect": label, "estimate": point[column],
            "percentile_ci_low": low, "percentile_ci_high": high,
            "zero_in_ci": bool(low <= 0 <= high),
            "n_boot_requested": n_boot, "n_boot_valid": len(valid), "seed": seed,
        })
    return pd.DataFrame(rows)


def pi_moderation_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    oi_items = BASE_FACTORS["oi"]
    for variant in ["original", "drop_Y8_4", "drop_Y11_1"]:
        factors = factor_spec(variant)
        data = df.copy()
        el_items = factors["el"]
        matched_oi = oi_items[:len(el_items)]
        pi_items = []
        for index, (oi_item, el_item) in enumerate(zip(matched_oi, el_items), 1):
            name = f"pi_{index}"
            data[name] = ((data[oi_item] - data[oi_item].mean()) *
                          (data[el_item] - data[el_item].mean()))
            pi_items.append(name)
        measurement = "\n".join(
            f"{factor} =~ {' + '.join(items)}" for factor, items in factors.items()
        )
        desc = f"""
{measurement}
oi_el =~ {' + '.join(pi_items)}
oi ~ equity + inclusion + male + age + public
upb ~ oi + el + oi_el + equity + inclusion + male + age + public
ocb ~ oi + el + oi_el + equity + inclusion + male + age + public
"""
        model = Model(desc)
        model.fit(data)
        est = model.inspect(std_est=True)
        stats = calc_stats(model).iloc[0]
        values = {}
        for key, dv, pred in [
            ("eq_oi", "oi", "equity"), ("incl_oi", "oi", "inclusion"),
            ("oi_upb", "upb", "oi"), ("interaction", "upb", "oi_el"),
        ]:
            row = get_path(est, dv, pred)
            values[key] = float(row["Est. Std"])
            if key == "interaction":
                interaction_b = float(row["Estimate"])
                interaction_se = float(row["Std. Err"])
                interaction_p = p_text(row["p-value"])
        slope_low = values["oi_upb"] - values["interaction"]
        slope_high = values["oi_upb"] + values["interaction"]
        rows.append({
            "variant": variant,
            "n_product_indicators": len(pi_items),
            "interaction_b": interaction_b,
            "interaction_se": interaction_se,
            "interaction_p_wald": interaction_p,
            "interaction_beta_std": values["interaction"],
            "oi_upb_beta_std": values["oi_upb"],
            "oi_slope_low_EL": slope_low,
            "oi_slope_high_EL": slope_high,
            "equity_cond_indirect_low": values["eq_oi"] * slope_low,
            "equity_cond_indirect_high": values["eq_oi"] * slope_high,
            "inclusion_cond_indirect_low": values["incl_oi"] * slope_low,
            "inclusion_cond_indirect_high": values["incl_oi"] * slope_high,
            "CFI": float(stats["CFI"]), "TLI": float(stats["TLI"]),
            "RMSEA": float(stats["RMSEA"]),
        })
    return pd.DataFrame(rows)


def composite_moderation_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for variant in ["original", "drop_Y8_4", "drop_Y11_1"]:
        factors = factor_spec(variant)
        data = pd.DataFrame(index=df.index)
        data["equity"] = df[factors["equity"]].mean(axis=1)
        data["inclusion"] = df[factors["inclusion"]].mean(axis=1)
        data["oi"] = df[factors["oi"]].mean(axis=1)
        data["el"] = df[factors["el"]].mean(axis=1)
        data["upb"] = df[factors["upb"]].mean(axis=1)
        data[["male", "age", "public"]] = df[["male", "age", "public"]]
        z = zscore(data)
        z["oi_x_el"] = z["oi"] * z["el"]
        predictors = ["equity", "inclusion", "oi", "el", "oi_x_el",
                      "male", "age", "public"]
        fit = fit_hc3(z, "upb", predictors)
        ci = fit.conf_int().loc["oi_x_el"]
        rows.append({
            "variant": variant,
            "interaction_beta": fit.params["oi_x_el"],
            "ci_low_HC3": ci.iloc[0], "ci_high_HC3": ci.iloc[1],
            "p_HC3": fit.pvalues["oi_x_el"], "r_squared": fit.rsquared,
            "equity_el_composite_r": data[["equity", "el"]].corr().iloc[0, 1],
        })
    return pd.DataFrame(rows)


def main() -> None:
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    df["male"] = (df["SQ1K1"] == 1.0).astype(int)
    df["age"] = 2024 - df["SQ1K2_1"]
    df["public"] = (df["유형"] == "공공").astype(int)

    print(f"Data: {DATA_PATH}")
    print(f"Shape: {df.shape}; complete focal cases: {len(df)}")
    print(f"Python: {sys.version.split()[0]}; platform: {platform.platform()}")
    print(f"pandas={pd.__version__}; numpy={np.__version__}; scipy={scipy.__version__}")
    print(f"statsmodels={statsmodels.__version__}; semopy={semopy.__version__}")
    print("Age rule: 2024 - SQ1K2_1; controls: male, age, public")

    corr_vars = ["equity_climate", "inclusion_climate", "org_identification",
                 "ethical_leadership", "ocb", "upb"]
    correlations = df[corr_vars].corr()
    correlations.to_csv(TABLE_DIR / "zero_order_correlations.csv", encoding="utf-8-sig")

    staged, vifs = staged_regressions(df)
    staged.to_csv(TABLE_DIR / "suppression_staged_regressions.csv",
                  index=False, encoding="utf-8-sig")
    vifs.to_csv(TABLE_DIR / "suppression_vif.csv", index=False, encoding="utf-8-sig")

    fit, paths, validity, _ = structural_sensitivity(df)
    fit.to_csv(TABLE_DIR / "item_deletion_sem_fit.csv", index=False, encoding="utf-8-sig")
    paths.to_csv(TABLE_DIR / "item_deletion_sem_paths.csv", index=False, encoding="utf-8-sig")
    validity.to_csv(TABLE_DIR / "item_deletion_validity.csv", index=False, encoding="utf-8-sig")

    h3_boot = latent_h3_difference_bootstrap(df)
    h3_boot.to_csv(TABLE_DIR / "latent_h3_path_difference_bootstrap.csv",
                   index=False, encoding="utf-8-sig")

    pi = pi_moderation_sensitivity(df)
    pi.to_csv(TABLE_DIR / "item_deletion_pi_moderation.csv",
              index=False, encoding="utf-8-sig")
    comp = composite_moderation_sensitivity(df)
    comp.to_csv(TABLE_DIR / "item_deletion_composite_moderation.csv",
                index=False, encoding="utf-8-sig")

    print("\nZero-order focal correlations:\n", correlations.round(4).to_string())
    print("\nStaged focal regressions:\n", staged.round(4).to_string(index=False))
    print("\nMax focal VIF by model:\n",
          vifs[vifs.predictor.isin(["equity_climate", "inclusion_climate", "org_identification"])]
          .groupby(["outcome", "model"])["vif"].max().round(4).to_string())
    print("\nItem-deletion SEM fit:\n", fit.round(4).to_string(index=False))
    print("\nItem-deletion SEM paths:\n", paths.round(4).to_string(index=False))
    print("\nItem-deletion AVE/CR:\n", validity.round(4).to_string(index=False))
    print("\nLatent H3 path-difference bootstrap:\n", h3_boot.round(4).to_string(index=False))
    print("\nItem-deletion PI moderation:\n", pi.round(4).to_string(index=False))
    print("\nItem-deletion composite moderation:\n", comp.round(4).to_string(index=False))
    print(f"\nOutputs written to: {TABLE_DIR}")


if __name__ == "__main__":
    with LOG_PATH.open("w", encoding="utf-8") as log_file:
        with contextlib.redirect_stdout(log_file), contextlib.redirect_stderr(log_file):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                main()
                if caught:
                    print("\nWarnings:")
                    for warning in caught:
                        print(f"- {warning.category.__name__}: {warning.message}")
