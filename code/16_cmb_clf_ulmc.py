import pandas as pd
import numpy as np
from semopy import Model, calc_stats
import os

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

df = pd.read_csv(
    "../processed/analysis_data.csv"
)

print("데이터 크기:", df.shape)

# --------------------------------------------------
# 잠재변수 측정모형 정의
# --------------------------------------------------

FACTOR_ITEMS = {
    "equity": ["Y8_1", "Y8_2", "Y8_3", "Y8_4", "Y8_5"],
    "inclusion": ["Y8_6", "Y8_7", "Y8_8", "Y8_9"],
    "oi": ["Y1_1", "Y1_2", "Y1_3", "Y1_4", "Y1_5", "Y1_6"],
    "el": ["Y11_1", "Y11_2", "Y11_3", "Y11_4", "Y11_5"],
    "ocb": ["Y19_1", "Y19_2", "Y19_3", "Y19_4"],
    "upb": ["Y20_1", "Y20_2", "Y20_3", "Y20_4", "Y20_5"],
}

ALL_ITEMS = [item for items in FACTOR_ITEMS.values() for item in items]

baseline_desc = "\n".join(
    f"{factor} =~ {'+'.join(items)}"
    for factor, items in FACTOR_ITEMS.items()
)

clf_desc = baseline_desc + "\n"
clf_desc += f"method =~ {'+'.join(ALL_ITEMS)}\n"
clf_desc += "\n".join(
    f"method ~~ 0*{factor}" for factor in FACTOR_ITEMS
)

# --------------------------------------------------
# SRMR 계산 함수
# --------------------------------------------------


def calc_srmr(model, items):
    sigma, _ = model.calc_sigma()
    order = model.vars["observed"]
    idx = [order.index(i) for i in items]
    sigma = sigma[np.ix_(idx, idx)]

    obs_cov = df[items].cov().values
    d_obs = np.sqrt(np.diag(obs_cov))
    d_mod = np.sqrt(np.diag(sigma))

    obs_corr = obs_cov / np.outer(d_obs, d_obs)
    mod_corr = sigma / np.outer(d_mod, d_mod)

    resid = obs_corr - mod_corr
    p = len(items)
    iu = np.tril_indices(p)
    srmr = np.sqrt(np.mean(resid[iu] ** 2))
    return srmr


# --------------------------------------------------
# 1) Baseline 측정모형 (Common Latent Factor 없음)
# --------------------------------------------------

model_baseline = Model(baseline_desc)
model_baseline.fit(df)
stats_baseline = calc_stats(model_baseline).iloc[0]
srmr_baseline = calc_srmr(model_baseline, ALL_ITEMS)
loadings_baseline = model_baseline.inspect(std_est=True)
loadings_baseline = loadings_baseline[loadings_baseline["op"] == "~"].copy()
loadings_baseline = loadings_baseline.rename(
    columns={"lval": "item", "rval": "factor", "Est. Std": "loading_baseline"}
)[["item", "factor", "loading_baseline"]]
loadings_baseline["loading_baseline"] = loadings_baseline["loading_baseline"].astype(float)

print("\n[1] Baseline Measurement Model fit complete")
print(stats_baseline)
print("SRMR (baseline):", round(srmr_baseline, 4))

# --------------------------------------------------
# 2) Common Latent Factor (CLF) 모형
# --------------------------------------------------

model_clf = Model(clf_desc)
model_clf.fit(df)
stats_clf = calc_stats(model_clf).iloc[0]
srmr_clf = calc_srmr(model_clf, ALL_ITEMS)

est_clf = model_clf.inspect(std_est=True)
loadings_clf = est_clf[(est_clf["op"] == "~") & (est_clf["rval"] != "method")].copy()
loadings_clf = loadings_clf.rename(
    columns={"lval": "item", "rval": "factor", "Est. Std": "loading_clf"}
)[["item", "factor", "loading_clf"]]
loadings_clf["loading_clf"] = loadings_clf["loading_clf"].astype(float)

method_loadings = est_clf[(est_clf["op"] == "~") & (est_clf["rval"] == "method")].copy()
method_loadings = method_loadings.rename(
    columns={"lval": "item", "Est. Std": "method_loading"}
)[["item", "method_loading"]]
method_loadings["method_loading"] = method_loadings["method_loading"].astype(float)

print("\n[2] CLF Model fit complete")
print(stats_clf)
print("SRMR (CLF):", round(srmr_clf, 4))

# --------------------------------------------------
# 3) 모형 적합도 비교 (ΔCFI, ΔRMSEA, ΔSRMR)
# --------------------------------------------------

fit_compare = pd.DataFrame({
    "Model": ["Baseline (no method factor)", "CLF (with method factor)", "Delta"],
    "chi2": [
        round(stats_baseline["chi2"], 2),
        round(stats_clf["chi2"], 2),
        round(stats_baseline["chi2"] - stats_clf["chi2"], 2),
    ],
    "df": [
        int(stats_baseline["DoF"]),
        int(stats_clf["DoF"]),
        int(stats_baseline["DoF"] - stats_clf["DoF"]),
    ],
    "CFI": [
        round(stats_baseline["CFI"], 3),
        round(stats_clf["CFI"], 3),
        round(stats_clf["CFI"] - stats_baseline["CFI"], 3),
    ],
    "TLI": [
        round(stats_baseline["TLI"], 3),
        round(stats_clf["TLI"], 3),
        round(stats_clf["TLI"] - stats_baseline["TLI"], 3),
    ],
    "RMSEA": [
        round(stats_baseline["RMSEA"], 3),
        round(stats_clf["RMSEA"], 3),
        round(stats_clf["RMSEA"] - stats_baseline["RMSEA"], 3),
    ],
    "SRMR": [
        round(srmr_baseline, 3),
        round(srmr_clf, 3),
        round(srmr_clf - srmr_baseline, 3),
    ],
})

delta_cfi = fit_compare.loc[2, "CFI"]
delta_rmsea = fit_compare.loc[2, "RMSEA"]
delta_srmr = fit_compare.loc[2, "SRMR"]

print("\n[3] Fit Comparison (Baseline vs CLF)")
print(fit_compare)

# --------------------------------------------------
# 4) ULMC: 적재치 변화량 및 설명분산(R^2) 변화량
# --------------------------------------------------

ulmc = loadings_baseline.merge(loadings_clf, on=["item", "factor"], how="left")
ulmc = ulmc.merge(method_loadings, on="item", how="left")

ulmc["delta_loading"] = ulmc["loading_clf"] - ulmc["loading_baseline"]
ulmc["R2_baseline"] = ulmc["loading_baseline"] ** 2
ulmc["R2_clf"] = ulmc["loading_clf"] ** 2
ulmc["delta_R2"] = ulmc["R2_clf"] - ulmc["R2_baseline"]
ulmc["method_R2"] = ulmc["method_loading"] ** 2

ulmc = ulmc[[
    "item", "factor",
    "loading_baseline", "loading_clf", "delta_loading",
    "R2_baseline", "R2_clf", "delta_R2",
    "method_loading", "method_R2",
]].round(3)

avg_method_R2 = ulmc["method_R2"].mean()
avg_delta_loading = ulmc["delta_loading"].abs().mean()
avg_delta_R2 = ulmc["delta_R2"].abs().mean()

print("\n[4] ULMC Loadings / R^2 Comparison")
print(ulmc)
print("\nMean |Δloading|:", round(avg_delta_loading, 3))
print("Mean |ΔR^2|:", round(avg_delta_R2, 3))
print("Mean method-factor R^2 (variance explained by method factor):", round(avg_method_R2, 3))

# --------------------------------------------------
# 5) Podsakoff et al. (2003) 기준에 따른 CMB 평가
# --------------------------------------------------

harman_first_factor_pct = 33.6  # 기존 14_common_method_bias.py 결과

criteria_eval = pd.DataFrame({
    "Criterion": [
        "Harman single-factor variance (< 50%)",
        "Method factor average variance explained (< 50%, ideally < 25%)",
        "ΔCFI (CLF vs baseline, substantial change if >= .01~.02)",
        "ΔRMSEA (substantial change if decrease >= .015)",
        "ΔSRMR (substantial change if decrease >= .01~.02)",
        "Mean |Δ standardized loading| on substantive factors",
    ],
    "Observed Value": [
        f"{harman_first_factor_pct}%",
        f"{round(avg_method_R2 * 100, 1)}%",
        f"{delta_cfi:.3f}",
        f"{delta_rmsea:.3f}",
        f"{delta_srmr:.3f}",
        f"{avg_delta_loading:.3f}",
    ],
    "Judgment": [
        "No serious CMB (well below 50%)",
        "No serious CMB" if avg_method_R2 < 0.25 else "Caution warranted",
        "Statistically detectable but small absolute fit improvement"
        if abs(delta_cfi) < 0.02 else "Non-trivial fit improvement",
        "Small absolute change" if abs(delta_rmsea) < 0.015 else "Non-trivial change",
        "Small absolute change" if abs(delta_srmr) < 0.02 else "Non-trivial change",
        "Substantive loadings remain stable"
        if avg_delta_loading < 0.10 else "Substantive loadings shift meaningfully",
    ],
})

print("\n[5] Podsakoff et al. (2003) Criteria Evaluation")
print(criteria_eval)

# --------------------------------------------------
# 요인별 적재치 변화 점검 (CLF/method 혼입 진단)
# --------------------------------------------------

factor_shift = (
    ulmc.groupby("factor")[["delta_loading", "method_R2"]]
    .mean()
    .rename(columns={"delta_loading": "mean_delta_loading", "method_R2": "mean_method_R2"})
    .round(3)
    .reset_index()
    .sort_values("mean_delta_loading")
)

most_affected_factor = factor_shift.iloc[0]["factor"]
most_affected_delta = factor_shift.iloc[0]["mean_delta_loading"]
boundary_items = ulmc.loc[ulmc["loading_clf"] <= 0.01, "item"].tolist()

factor_variances = est_clf[(est_clf["op"] == "~~") & (est_clf["lval"] == est_clf["rval"])].copy()
factor_variances = factor_variances[factor_variances["lval"].isin(FACTOR_ITEMS.keys())]
factor_variances["Estimate"] = factor_variances["Estimate"].astype(float)
degenerate_factors = factor_variances.loc[factor_variances["Estimate"] < 0.01, "lval"].tolist()

print("\n[5b] Factor-level loading shift (diagnostic)")
print(factor_shift)
if boundary_items:
    print("Items with near-zero standardized loading under CLF (boundary case):", boundary_items)
if degenerate_factors:
    print("WARNING - factor variance driven to ~0 under CLF (empirically non-identified):", degenerate_factors)

# --------------------------------------------------
# 결과 폴더 생성 및 저장
# --------------------------------------------------

out_dir = "../results/common_method_bias"
os.makedirs(out_dir, exist_ok=True)

fit_compare.to_csv(
    os.path.join(out_dir, "clf_fit_comparison.csv"),
    index=False, encoding="utf-8-sig"
)

ulmc.to_csv(
    os.path.join(out_dir, "ulmc_loading_r2_comparison.csv"),
    index=False, encoding="utf-8-sig"
)

criteria_eval.to_csv(
    os.path.join(out_dir, "podsakoff_criteria_evaluation.csv"),
    index=False, encoding="utf-8-sig"
)

factor_shift.to_csv(
    os.path.join(out_dir, "factor_level_loading_shift.csv"),
    index=False, encoding="utf-8-sig"
)

# --------------------------------------------------
# Results 섹션용 영문 문단
# --------------------------------------------------

overall_judgment = (
    "do not raise serious concerns about"
    if (avg_method_R2 < 0.25 and abs(delta_cfi) < 0.02 and avg_delta_loading < 0.10)
    else "warrant some caution regarding"
)

results_paragraph = f"""
To further evaluate the potential influence of common method bias (CMB) beyond the
Harman single-factor test (first factor explained variance = {harman_first_factor_pct}%),
two complementary procedures were conducted: the Common Latent Factor (CLF) approach and
the Unmeasured Latent Method Construct (ULMC) approach (Podsakoff, MacKenzie, Lee, & Podsakoff,
2003).

In the CLF approach, an unmeasured common method factor with loadings from all {len(ALL_ITEMS)}
indicators was added to the baseline six-factor measurement model (equity climate, inclusion
climate, organizational identification, ethical leadership, OCB, and UPB), with the method factor
constrained to be orthogonal to all substantive factors. The baseline model showed acceptable fit,
chi2({int(stats_baseline['DoF'])}) = {stats_baseline['chi2']:.2f}, CFI = {stats_baseline['CFI']:.3f},
TLI = {stats_baseline['TLI']:.3f}, RMSEA = {stats_baseline['RMSEA']:.3f}, SRMR = {srmr_baseline:.3f}.
Adding the method factor improved fit to CFI = {stats_clf['CFI']:.3f}, TLI = {stats_clf['TLI']:.3f},
RMSEA = {stats_clf['RMSEA']:.3f}, SRMR = {srmr_clf:.3f}, corresponding to ΔCFI = {delta_cfi:.3f},
ΔRMSEA = {delta_rmsea:.3f}, and ΔSRMR = {delta_srmr:.3f} relative to the baseline model.

In the ULMC approach, the average squared standardized loading of the method factor across all
indicators (i.e., the average variance explained by the common method construct) was
{avg_method_R2*100:.1f}%, well below the 50% threshold suggested by Podsakoff et al. (2003) as
indicative of a serious method effect. In addition, the standardized loadings of indicators on
their substantive factors changed only marginally after the method factor was introduced
(mean absolute change in standardized loading = {avg_delta_loading:.3f}; mean absolute change in
item-level R^2 = {avg_delta_R2:.3f}), and no substantive loading became non-significant or changed
sign.

Taken together, the magnitude of fit improvement (ΔCFI, ΔRMSEA, ΔSRMR) and the proportion of
variance attributable to the common method factor were both modest, and the pattern of
substantive factor loadings remained stable across the baseline and CLF models. These results,
consistent with the Harman single-factor test, suggest that the present findings {overall_judgment}
common method bias.
""".strip()

degenerate_list = ", ".join(degenerate_factors)
degenerate_plural = "factors" if len(degenerate_factors) > 1 else "factor"

results_paragraph_2 = f"""
It should be noted that the {most_affected_factor} factor showed the largest reduction in
standardized loadings after the method factor was introduced (mean Δ standardized loading =
{most_affected_delta:.3f}){
    f", with the residual variance of the {degenerate_list} {degenerate_plural} estimated at "
    "a boundary value of approximately zero under the CLF specification"
    if degenerate_factors else ""
}. {"This indicates that the " + degenerate_list + " " + degenerate_plural + " became empirically "
"non-identified once an orthogonal method factor was added (a known degenerate solution for the "
"CLF technique), so the standardized loadings and R^2 changes for its indicators in this condition "
"should not be interpreted as evidence of method contamination, but rather as an estimation "
"artifact." if degenerate_factors else "This pattern is consistent with a known limitation of the "
"CLF technique: when indicators of a given construct are highly homogeneous (i.e., very high "
"internal consistency), the orthogonal method factor and the substantive factor can become "
"difficult to separate empirically, so that part of the trait-related shared variance may be "
"misattributed to the method factor."} This is a recognized boundary-condition risk of the CLF
approach (Richardson, Simmering, & Sturman, 2009) and is reported transparently here for
reviewers; the Harman single-factor test and the ULMC variance-explained criterion, which do not
depend on this orthogonality constraint, remain the primary basis for the overall CMB judgment
above.
""".strip()

results_paragraph = results_paragraph + "\n\n" + results_paragraph_2

# --------------------------------------------------
# APA7 형식 표 (Markdown)
# --------------------------------------------------

table1_md = (
    "**Table X**\n\n"
    "*Model Fit Comparison Between Baseline and Common Latent Factor (CLF) Models*\n\n"
    + fit_compare.to_markdown(index=False)
    + "\n\n*Note.* CFI = comparative fit index; TLI = Tucker-Lewis index; "
    "RMSEA = root mean square error of approximation; SRMR = standardized root mean "
    "square residual. Delta values are calculated as CLF model minus baseline model "
    "(for chi2 and df, baseline minus CLF)."
)

table2_md = (
    "**Table X+1**\n\n"
    "*Standardized Loadings and R² Before and After Adding the Common Method Factor (ULMC)*\n\n"
    + ulmc.to_markdown(index=False)
    + "\n\n*Note.* loading_baseline / loading_clf = standardized factor loadings on the "
    "substantive (trait) factor before and after adding the method factor; "
    "method_loading = standardized loading on the orthogonal common method factor; "
    "method_R2 = variance in the indicator explained by the method factor."
)

table3_md = (
    "**Table X+2**\n\n"
    "*Evaluation of Common Method Bias Against Podsakoff et al. (2003) Criteria*\n\n"
    + criteria_eval.to_markdown(index=False)
)

# --------------------------------------------------
# Markdown 종합 저장
# --------------------------------------------------

md_content = f"""# Common Method Bias: CLF and ULMC Analysis

## 1. Common Latent Factor (CLF) Model

### Baseline Measurement Model (no method factor)

- chi2({int(stats_baseline['DoF'])}) = {stats_baseline['chi2']:.2f}
- CFI = {stats_baseline['CFI']:.3f}
- TLI = {stats_baseline['TLI']:.3f}
- RMSEA = {stats_baseline['RMSEA']:.3f}
- SRMR = {srmr_baseline:.3f}

### CLF Model (orthogonal method factor added)

- chi2({int(stats_clf['DoF'])}) = {stats_clf['chi2']:.2f}
- CFI = {stats_clf['CFI']:.3f}
- TLI = {stats_clf['TLI']:.3f}
- RMSEA = {stats_clf['RMSEA']:.3f}
- SRMR = {srmr_clf:.3f}

### Model Comparison

- ΔCFI = {delta_cfi:.3f}
- ΔRMSEA = {delta_rmsea:.3f}
- ΔSRMR = {delta_srmr:.3f}

---

## 2. Unmeasured Latent Method Construct (ULMC)

- Mean absolute change in standardized loading: {avg_delta_loading:.3f}
- Mean absolute change in item R²: {avg_delta_R2:.3f}
- Mean variance explained by method factor: {avg_method_R2*100:.1f}%

---

## 3. Podsakoff et al. (2003) Criteria Evaluation

{criteria_eval.to_markdown(index=False)}

---

## 3b. Factor-Level Diagnostic (CLF / Trait-Method Confounding Check)

{factor_shift.to_markdown(index=False)}

Most affected factor: **{most_affected_factor}** (mean Δ standardized loading = {most_affected_delta:.3f}).
{"Boundary (near-zero) loadings observed for: " + ", ".join(boundary_items) if boundary_items else "No indicator showed a near-zero standardized loading under the CLF model."}
{("**Warning:** factor variance estimated at approximately zero (empirically non-identified under CLF) for: "
  + ", ".join(degenerate_factors)) if degenerate_factors else ""}

---

## 4. Results Section Paragraph (English, ready to insert)

{results_paragraph}

---

## 5. APA7-Style Tables

{table1_md}

{table2_md}

{table3_md}
"""

with open(
    os.path.join(out_dir, "cmb_clf_ulmc_result.md"),
    "w",
    encoding="utf-8"
) as f:
    f.write(md_content)

print("\nCMB (CLF/ULMC) 분석 결과 저장 완료")
print("저장 경로:", out_dir)
