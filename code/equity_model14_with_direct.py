import os

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import norm


DATA_PATH = "../processed/analysis_data.csv"
OUT_DIR = "../results/equity_model14_with_direct"
N_BOOT = 5000
SEED = 42


def pvalue_from_z(z_value):
    return 2 * (1 - norm.cdf(abs(z_value)))


def sig_from_ci(lo, hi):
    return "significant" if not (lo <= 0 <= hi) else "non-significant"


def prepare_data():
    data = pd.read_csv(DATA_PATH)
    data["equity_c"] = data["equity_climate"] - data["equity_climate"].mean()
    data["inclusion_c"] = data["inclusion_climate"] - data["inclusion_climate"].mean()
    data["oi_c"] = data["org_identification"] - data["org_identification"].mean()
    data["el_c"] = data["ethical_leadership"] - data["ethical_leadership"].mean()
    data["gender_male"] = (data["SQ1K1"] == 1.0).astype(int)
    data["age"] = 2023 - data["SQ1K2_1"]
    data["public_org"] = (data["\uc720\ud615"] == "\uacf5\uacf5").astype(int)
    data["oi_x_el"] = data["oi_c"] * data["el_c"]
    return data


def outcome_formula(x_c):
    return f"""
        upb ~
        {x_c} +
        oi_c +
        el_c +
        oi_x_el +
        gender_male +
        age +
        public_org
    """


def fit_models(data, x_c):
    model_a = smf.ols(
        f"oi_c ~ {x_c} + gender_male + age + public_org",
        data=data,
    ).fit(cov_type="HC3")

    model_y = smf.ols(
        outcome_formula(x_c),
        data=data,
    ).fit(cov_type="HC3")

    return model_a, model_y


def coefficient_row(model, term):
    ci = model.conf_int().loc[term]
    return {
        "B": model.params[term],
        "SE": model.bse[term],
        "z": model.tvalues[term],
        "p": model.pvalues[term],
        "ci_low": ci[0],
        "ci_high": ci[1],
    }


def simple_slope(model_y, el_value):
    cov = model_y.cov_params()
    slope = model_y.params["oi_c"] + model_y.params["oi_x_el"] * el_value
    var_slope = (
        cov.loc["oi_c", "oi_c"]
        + (el_value**2) * cov.loc["oi_x_el", "oi_x_el"]
        + 2 * el_value * cov.loc["oi_c", "oi_x_el"]
    )
    se = np.sqrt(var_slope)
    z_value = slope / se
    p_value = pvalue_from_z(z_value)
    return {
        "B": slope,
        "SE": se,
        "z": z_value,
        "p": p_value,
        "ci_low": slope - 1.96 * se,
        "ci_high": slope + 1.96 * se,
    }


def bootstrap_model14(data, x_c, n_boot=N_BOOT, seed=SEED):
    np.random.seed(seed)
    el_sd = data["el_c"].std()
    conditions = {"-1 SD": -el_sd, "Mean": 0.0, "+1 SD": el_sd}
    effects = {name: [] for name in conditions}
    indexes = []

    for _ in range(n_boot):
        sample = data.sample(n=len(data), replace=True).copy()
        sample["oi_x_el"] = sample["oi_c"] * sample["el_c"]

        a_model = smf.ols(
            f"oi_c ~ {x_c} + gender_male + age + public_org",
            data=sample,
        ).fit()

        y_model = smf.ols(
            outcome_formula(x_c),
            data=sample,
        ).fit()

        try:
            a_path = a_model.params[x_c]
            b1 = y_model.params["oi_c"]
            b3 = y_model.params["oi_x_el"]
            indexes.append(a_path * b3)
            for name, el_value in conditions.items():
                effects[name].append(a_path * (b1 + b3 * el_value))
        except Exception:
            continue

    boot = {
        "index": {
            "B": float(np.mean(indexes)),
            "SE": float(np.std(indexes, ddof=1)),
            "ci_low": float(np.percentile(indexes, 2.5)),
            "ci_high": float(np.percentile(indexes, 97.5)),
            "n_valid": len(indexes),
        },
        "conditional_indirect": {},
    }
    for name, values in effects.items():
        boot["conditional_indirect"][name] = {
            "B": float(np.mean(values)),
            "SE": float(np.std(values, ddof=1)),
            "ci_low": float(np.percentile(values, 2.5)),
            "ci_high": float(np.percentile(values, 97.5)),
            "n_valid": len(values),
        }
    return boot


def analyze(data, dimension, x_c):
    model_a, model_y = fit_models(data, x_c)
    el_sd = data["el_c"].std()
    slopes = {
        "-1 SD": simple_slope(model_y, -el_sd),
        "Mean": simple_slope(model_y, 0.0),
        "+1 SD": simple_slope(model_y, el_sd),
    }
    boot = bootstrap_model14(data, x_c)

    return {
        "dimension": dimension,
        "x_c": x_c,
        "a_path": coefficient_row(model_a, x_c),
        "direct": coefficient_row(model_y, x_c),
        "outcome_paths": {
            "OI -> UPB": coefficient_row(model_y, "oi_c"),
            "EL -> UPB": coefficient_row(model_y, "el_c"),
            "OI x EL -> UPB": coefficient_row(model_y, "oi_x_el"),
        },
        "full_outcome_model": model_y,
        "slopes": slopes,
        "boot": boot,
    }


def rows_for_paths(result):
    rows = [{"DEI dimension": result["dimension"], "Path": "a path: X -> OI", **result["a_path"]}]
    rows.append({"DEI dimension": result["dimension"], "Path": "c prime: X -> UPB", **result["direct"]})
    for path, values in result["outcome_paths"].items():
        rows.append({"DEI dimension": result["dimension"], "Path": path, **values})
    return rows


def write_outputs(results):
    os.makedirs(OUT_DIR, exist_ok=True)

    path_rows = []
    slope_rows = []
    indirect_rows = []
    index_rows = []
    outcome_rows = []

    for result in results:
        path_rows.extend(rows_for_paths(result))
        for level, values in result["slopes"].items():
            slope_rows.append({"DEI dimension": result["dimension"], "EL level": level, **values})
        for level, values in result["boot"]["conditional_indirect"].items():
            indirect_rows.append(
                {
                    "DEI dimension": result["dimension"],
                    "EL level": level,
                    **values,
                    "Decision": sig_from_ci(values["ci_low"], values["ci_high"]),
                }
            )
        idx = result["boot"]["index"]
        index_rows.append(
            {
                "DEI dimension": result["dimension"],
                **idx,
                "Decision": sig_from_ci(idx["ci_low"], idx["ci_high"]),
            }
        )

        params = result["full_outcome_model"].params
        for term in params.index:
            row = coefficient_row(result["full_outcome_model"], term)
            outcome_rows.append({"DEI dimension": result["dimension"], "Term": term, **row})

    pd.DataFrame(path_rows).to_csv(
        os.path.join(OUT_DIR, "model14_with_direct_paths.csv"),
        index=False,
        encoding="utf-8-sig",
    )
    pd.DataFrame(slope_rows).to_csv(
        os.path.join(OUT_DIR, "model14_with_direct_simple_slopes.csv"),
        index=False,
        encoding="utf-8-sig",
    )
    pd.DataFrame(indirect_rows).to_csv(
        os.path.join(OUT_DIR, "model14_with_direct_conditional_indirect_effects.csv"),
        index=False,
        encoding="utf-8-sig",
    )
    pd.DataFrame(index_rows).to_csv(
        os.path.join(OUT_DIR, "model14_with_direct_indexes.csv"),
        index=False,
        encoding="utf-8-sig",
    )
    pd.DataFrame(outcome_rows).to_csv(
        os.path.join(OUT_DIR, "model14_with_direct_full_outcome_models.csv"),
        index=False,
        encoding="utf-8-sig",
    )

    md = [
        "# Model 14 With X Direct Effect\n\n",
        f"- Data: `{DATA_PATH}`\n",
        f"- Bootstrap: {N_BOOT:,}, seed={SEED}, percentile 95% CI\n",
        "- Outcome formula: `upb ~ X_c + oi_c + el_c + oi_x_el + gender_male + age + public_org`\n\n",
        "## Paths\n\n",
        pd.DataFrame(path_rows).to_markdown(index=False),
        "\n\n## Simple Slopes\n\n",
        pd.DataFrame(slope_rows).to_markdown(index=False),
        "\n\n## Conditional Indirect Effects\n\n",
        pd.DataFrame(indirect_rows).to_markdown(index=False),
        "\n\n## Index of Moderated Mediation\n\n",
        pd.DataFrame(index_rows).to_markdown(index=False),
        "\n\n## Full Outcome Models\n\n",
        pd.DataFrame(outcome_rows).to_markdown(index=False),
        "\n",
    ]
    with open(
        os.path.join(OUT_DIR, "model14_with_direct_results.md"),
        "w",
        encoding="utf-8",
    ) as f:
        f.write("".join(md))


def main():
    data = prepare_data()
    results = [
        analyze(data, "Equity", "equity_c"),
        analyze(data, "Inclusion", "inclusion_c"),
    ]
    write_outputs(results)

    print("Existing scripts omit X from the outcome equation.")
    print("Corrected outcome formula: upb ~ X_c + oi_c + el_c + oi_x_el + gender_male + age + public_org")
    for result in results:
        print("\n" + "=" * 72)
        print(result["dimension"])
        print("=" * 72)
        print("a path:", result["a_path"])
        print("direct:", result["direct"])
        print("outcome paths:", result["outcome_paths"])
        print("simple slopes:", result["slopes"])
        print("conditional indirect:", result["boot"]["conditional_indirect"])
        print("index:", result["boot"]["index"])
        print("full outcome params:")
        print(result["full_outcome_model"].params)
    print(f"\nSaved outputs to: {OUT_DIR}")


if __name__ == "__main__":
    main()
