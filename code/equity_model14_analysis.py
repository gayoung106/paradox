import os

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import norm


DATA_PATH = "../processed/analysis_data.csv"
OUT_DIR = "../results/equity_model14"
N_BOOT = 5000
SEED = 42

EXPECTED_INCLUSION = {
    "interaction_b": -0.062,
    "interaction_p": 0.011,
    "index": -0.026,
    "index_ci": (-0.046, -0.006),
    "low_ie": 0.095,
    "low_ci": (0.064, 0.126),
    "high_ie": 0.046,
    "high_ci": (0.016, 0.075),
}


def pvalue_from_z(z_value):
    return 2 * (1 - norm.cdf(abs(z_value)))


def fmt_p(p_value):
    if p_value < 0.001:
        return "<.001"
    return f"{p_value:.3f}".replace("0.", ".")


def fmt_num(value, digits=3):
    text = f"{value:.{digits}f}"
    if text.startswith("-0."):
        return "-." + text[3:]
    if text.startswith("0."):
        return "." + text[2:]
    return text


def sig_from_ci(lo, hi):
    return "significant" if not (lo <= 0 <= hi) else "non-significant"


def prepare_data(path):
    df = pd.read_csv(path)

    org_type_col = "\uc720\ud615"
    public_label = "\uacf5\uacf5"

    df["inclusion_c"] = df["inclusion_climate"] - df["inclusion_climate"].mean()
    df["equity_c"] = df["equity_climate"] - df["equity_climate"].mean()
    df["oi_c"] = df["org_identification"] - df["org_identification"].mean()
    df["el_c"] = df["ethical_leadership"] - df["ethical_leadership"].mean()

    # Same control coding as code/08_moderated_mediation.py.
    df["gender_male"] = (df["SQ1K1"] == 1.0).astype(int)
    df["age"] = 2023 - df["SQ1K2_1"]
    df["public_org"] = (df[org_type_col] == public_label).astype(int)

    df["oi_x_el"] = df["oi_c"] * df["el_c"]
    return df


def fit_model14(data, x_c):
    model_a = smf.ols(
        f"oi_c ~ {x_c} + gender_male + age + public_org",
        data=data,
    ).fit(cov_type="HC3")

    model_b = smf.ols(
        """
        upb ~
        oi_c +
        el_c +
        oi_x_el +
        gender_male +
        age +
        public_org
        """,
        data=data,
    ).fit(cov_type="HC3")

    return model_a, model_b


def slope_from_model(model_b, el_value):
    cov = model_b.cov_params()
    slope = model_b.params["oi_c"] + model_b.params["oi_x_el"] * el_value
    var_slope = (
        cov.loc["oi_c", "oi_c"]
        + (el_value**2) * cov.loc["oi_x_el", "oi_x_el"]
        + 2 * el_value * cov.loc["oi_c", "oi_x_el"]
    )
    se = np.sqrt(var_slope)
    z_value = slope / se
    p_value = pvalue_from_z(z_value)
    ci_low = slope - 1.96 * se
    ci_high = slope + 1.96 * se
    return {
        "B": slope,
        "SE": se,
        "z": z_value,
        "p": p_value,
        "ci_low": ci_low,
        "ci_high": ci_high,
    }


def bootstrap_model14(data, x_c, n_boot=N_BOOT, seed=SEED):
    np.random.seed(seed)

    el_sd = data["el_c"].std()
    conditions = {
        "-1 SD": -el_sd,
        "Mean": 0.0,
        "+1 SD": el_sd,
    }
    effects = {name: [] for name in conditions}
    indexes = []

    for _ in range(n_boot):
        sample = data.sample(n=len(data), replace=True).copy()
        sample["oi_x_el"] = sample["oi_c"] * sample["el_c"]

        a_model = smf.ols(
            f"oi_c ~ {x_c} + gender_male + age + public_org",
            data=sample,
        ).fit()

        b_model = smf.ols(
            """
            upb ~
            oi_c +
            el_c +
            oi_x_el +
            gender_male +
            age +
            public_org
            """,
            data=sample,
        ).fit()

        try:
            a_path = a_model.params[x_c]
            b1 = b_model.params["oi_c"]
            b3 = b_model.params["oi_x_el"]
            indexes.append(a_path * b3)
            for name, el_value in conditions.items():
                effects[name].append(a_path * (b1 + b3 * el_value))
        except Exception:
            continue

    result = {
        "conditions": {},
        "index": {
            "mean": float(np.mean(indexes)),
            "se": float(np.std(indexes, ddof=1)),
            "ci_low": float(np.percentile(indexes, 2.5)),
            "ci_high": float(np.percentile(indexes, 97.5)),
            "n_valid": len(indexes),
        },
    }

    for name, values in effects.items():
        result["conditions"][name] = {
            "mean": float(np.mean(values)),
            "se": float(np.std(values, ddof=1)),
            "ci_low": float(np.percentile(values, 2.5)),
            "ci_high": float(np.percentile(values, 97.5)),
            "n_valid": len(values),
        }

    return result


def coefficient_row(model, term):
    ci = model.conf_int().loc[term]
    stat = model.tvalues[term]
    return {
        "B": model.params[term],
        "SE": model.bse[term],
        "z": stat,
        "p": model.pvalues[term],
        "ci_low": ci[0],
        "ci_high": ci[1],
    }


def analyze_dimension(data, dimension, x_c):
    model_a, model_b = fit_model14(data, x_c)
    boot = bootstrap_model14(data, x_c)

    el_sd = data["el_c"].std()
    slopes = {
        "-1 SD": slope_from_model(model_b, -el_sd),
        "Mean": slope_from_model(model_b, 0.0),
        "+1 SD": slope_from_model(model_b, el_sd),
    }

    a_path = coefficient_row(model_a, x_c)
    b_paths = {
        "OI": coefficient_row(model_b, "oi_c"),
        "EL": coefficient_row(model_b, "el_c"),
        "OI x EL": coefficient_row(model_b, "oi_x_el"),
    }

    point_index = model_a.params[x_c] * model_b.params["oi_x_el"]
    point_conditional = {}
    for level, el_value in {"-1 SD": -el_sd, "Mean": 0.0, "+1 SD": el_sd}.items():
        point_conditional[level] = model_a.params[x_c] * (
            model_b.params["oi_c"] + model_b.params["oi_x_el"] * el_value
        )

    return {
        "dimension": dimension,
        "x_c": x_c,
        "model_a": model_a,
        "model_b": model_b,
        "a_path": a_path,
        "b_paths": b_paths,
        "slopes": slopes,
        "boot": boot,
        "point_index": point_index,
        "point_conditional": point_conditional,
    }


def inclusion_reproduced(inclusion):
    b_int = inclusion["b_paths"]["OI x EL"]["B"]
    p_int = inclusion["b_paths"]["OI x EL"]["p"]
    boot = inclusion["boot"]

    def close(value, expected, tol=0.001):
        return abs(value - expected) <= tol

    checks = {
        "interaction_b": close(b_int, EXPECTED_INCLUSION["interaction_b"]),
        "interaction_p": close(p_int, EXPECTED_INCLUSION["interaction_p"]),
        "index": close(boot["index"]["mean"], EXPECTED_INCLUSION["index"]),
        "index_ci_low": close(boot["index"]["ci_low"], EXPECTED_INCLUSION["index_ci"][0]),
        "index_ci_high": close(boot["index"]["ci_high"], EXPECTED_INCLUSION["index_ci"][1]),
        "low_ie": close(boot["conditions"]["-1 SD"]["mean"], EXPECTED_INCLUSION["low_ie"]),
        "low_ci_low": close(boot["conditions"]["-1 SD"]["ci_low"], EXPECTED_INCLUSION["low_ci"][0]),
        "low_ci_high": close(boot["conditions"]["-1 SD"]["ci_high"], EXPECTED_INCLUSION["low_ci"][1]),
        "high_ie": close(boot["conditions"]["+1 SD"]["mean"], EXPECTED_INCLUSION["high_ie"]),
        "high_ci_low": close(boot["conditions"]["+1 SD"]["ci_low"], EXPECTED_INCLUSION["high_ci"][0]),
        "high_ci_high": close(boot["conditions"]["+1 SD"]["ci_high"], EXPECTED_INCLUSION["high_ci"][1]),
    }
    return all(checks.values()), checks


def make_tables(inclusion, equity):
    rows = []
    for result in [equity, inclusion]:
        for level in ["-1 SD", "Mean", "+1 SD"]:
            cond = result["boot"]["conditions"][level]
            rows.append(
                {
                    "DEI dimension": result["dimension"],
                    "EL level": level,
                    "Conditional indirect effect (B)": cond["mean"],
                    "Bootstrap SE": cond["se"],
                    "95% Bootstrap CI": f"[{cond['ci_low']:.3f}, {cond['ci_high']:.3f}]",
                    "Decision": sig_from_ci(cond["ci_low"], cond["ci_high"]),
                }
            )
    conditional = pd.DataFrame(rows)

    index_rows = []
    for result in [equity, inclusion]:
        idx = result["boot"]["index"]
        index_rows.append(
            {
                "DEI dimension": result["dimension"],
                "Index of Moderated Mediation": idx["mean"],
                "Bootstrap SE": idx["se"],
                "95% Bootstrap CI": f"[{idx['ci_low']:.3f}, {idx['ci_high']:.3f}]",
                "Decision": sig_from_ci(idx["ci_low"], idx["ci_high"]),
            }
        )
    indexes = pd.DataFrame(index_rows)
    return conditional, indexes


def write_outputs(data, inclusion, equity, checks):
    os.makedirs(OUT_DIR, exist_ok=True)

    conditional, indexes = make_tables(inclusion, equity)
    conditional.to_csv(
        os.path.join(OUT_DIR, "equity_model14_conditional_indirect_effects.csv"),
        index=False,
        encoding="utf-8-sig",
    )
    indexes.to_csv(
        os.path.join(OUT_DIR, "equity_model14_index_of_moderated_mediation.csv"),
        index=False,
        encoding="utf-8-sig",
    )

    regression_rows = []
    for label, row in [("Equity -> OI", equity["a_path"])]:
        regression_rows.append({"Path": label, **row})
    for label, row in equity["b_paths"].items():
        regression_rows.append({"Path": f"{label} -> UPB", **row})
    pd.DataFrame(regression_rows).to_csv(
        os.path.join(OUT_DIR, "equity_model14_regression_paths.csv"),
        index=False,
        encoding="utf-8-sig",
    )

    slope_rows = []
    for level, row in equity["slopes"].items():
        slope_rows.append({"EL level": level, **row})
    pd.DataFrame(slope_rows).to_csv(
        os.path.join(OUT_DIR, "equity_model14_simple_slopes.csv"),
        index=False,
        encoding="utf-8-sig",
    )

    md = []
    md.append("# Equity Model 14 Analysis\n")
    md.append("## Reproduction Check: Inclusion Model 14\n")
    md.append(f"- Data: `{DATA_PATH}`\n")
    md.append("- Reference script: `../code/08_moderated_mediation.py`\n")
    md.append(f"- Bootstrap: {N_BOOT:,} case-resampling iterations, seed={SEED}, percentile 95% CI\n")
    md.append(f"- Reproduction checks: `{checks}`\n\n")

    b_int = inclusion["b_paths"]["OI x EL"]
    idx = inclusion["boot"]["index"]
    md.append(
        f"Inclusion OI x EL -> UPB: B={b_int['B']:.6f}, p={b_int['p']:.6f}\n\n"
    )
    md.append(
        "Inclusion index of moderated mediation: "
        f"{idx['mean']:.6f}, 95% CI [{idx['ci_low']:.6f}, {idx['ci_high']:.6f}]\n\n"
    )

    md.append("## Equity A Path\n\n")
    md.append(pd.DataFrame([{"Path": "Equity -> OI", **equity["a_path"]}]).to_markdown(index=False))
    md.append("\n\n## Equity B Paths and Moderation\n\n")
    md.append(
        pd.DataFrame(
            [{"Path": f"{label} -> UPB", **row} for label, row in equity["b_paths"].items()]
        ).to_markdown(index=False)
    )
    md.append("\n\n## Simple Slopes: OI -> UPB by EL\n\n")
    md.append(
        pd.DataFrame(
            [{"EL level": level, **row} for level, row in equity["slopes"].items()]
        ).to_markdown(index=False)
    )
    md.append("\n\n## Conditional Indirect Effects\n\n")
    md.append(conditional.to_markdown(index=False))
    md.append("\n\n## Index of Moderated Mediation\n\n")
    md.append(indexes.to_markdown(index=False))
    md.append("\n")

    with open(
        os.path.join(OUT_DIR, "equity_model14_results.md"),
        "w",
        encoding="utf-8",
    ) as f:
        f.write("".join(md))


def print_key_results(inclusion, equity, checks):
    print("Inclusion reproduction checks")
    print(checks)

    for result in [inclusion, equity]:
        print("\n" + "=" * 72)
        print(result["dimension"])
        print("=" * 72)
        print("A path")
        print(result["a_path"])
        print("B paths")
        for key, value in result["b_paths"].items():
            print(key, value)
        print("Simple slopes")
        for key, value in result["slopes"].items():
            print(key, value)
        print("Conditional indirect effects")
        for key, value in result["boot"]["conditions"].items():
            print(key, value)
        print("Index")
        print(result["boot"]["index"])


def main():
    data = prepare_data(DATA_PATH)

    inclusion = analyze_dimension(data, "Inclusion", "inclusion_c")
    reproduced, checks = inclusion_reproduced(inclusion)
    if not reproduced:
        print_key_results(inclusion, inclusion, checks)
        raise SystemExit("Inclusion Model 14 was not reproduced; stopping before Equity analysis.")

    equity = analyze_dimension(data, "Equity", "equity_c")
    write_outputs(data, inclusion, equity, checks)
    print_key_results(inclusion, equity, checks)
    print(f"\nSaved outputs to: {OUT_DIR}")


if __name__ == "__main__":
    main()

