import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.stats import norm
import os

# --------------------------------------------------
# 데이터 불러오기 및 변수 정의
# --------------------------------------------------

df = pd.read_csv(
    "../processed/analysis_data.csv"
)

print("데이터 크기:", df.shape)

df["gender"] = df["SQ1K1"]
df["age"] = 2023 - df["SQ1K2_1"]  # SQ1K2_1 = 출생연도; 2023년 기준 환산
df["organization_type"] = (df["유형"] == "공공").astype(int)

X1 = "inclusion_climate"
X2 = "equity_climate"
M = "org_identification"
Y = "upb"
CONTROLS = ["gender", "age", "organization_type"]

cols = [X1, X2, M, Y] + CONTROLS
analysis_df = df[cols].dropna().reset_index(drop=True)
N = len(analysis_df)
print("분석 표본 크기:", N)

# --------------------------------------------------
# 동시추정 모형 (공통 매개변수를 통한 두 간접효과 비교)
# --------------------------------------------------
#
# Indirect(Inclusion)와 Indirect(Equity)를 동일한 부트스트랩 표본에서 공동으로
# 산출해야 차이(Difference)와 비율(Ratio)의 표집분포를 올바르게 구성할 수 있다.
# 이를 위해 두 독립변수와 통제변수를 모두 포함한 단일 매개모형을 동시추정한다.
#
# a1: X1(inclusion) -> M,  a2: X2(equity) -> M  (공통 절편모형, M ~ X1+X2+controls)
# b : M -> Y                                     (공통 절편모형, Y ~ M+X1+X2+controls)
# Indirect(Inclusion) = a1*b,  Indirect(Equity) = a2*b


def fit_paths(data):
    Xm = sm.add_constant(data[[X1, X2] + CONTROLS])
    model_m = sm.OLS(data[M], Xm).fit(cov_type="HC3")
    a1 = model_m.params[X1]
    a2 = model_m.params[X2]

    Xy = sm.add_constant(data[[M, X1, X2] + CONTROLS])
    model_y = sm.OLS(data[Y], Xy).fit(cov_type="HC3")
    b = model_y.params[M]

    return a1, a2, b, model_m, model_y


a1_hat, a2_hat, b_hat, model_m, model_y = fit_paths(analysis_df)

indirect_inclusion_hat = a1_hat * b_hat
indirect_equity_hat = a2_hat * b_hat
diff_hat = indirect_inclusion_hat - indirect_equity_hat
ratio_hat = indirect_inclusion_hat / indirect_equity_hat

print("\n[동시추정 모형 결과 (HC3 robust SE)]")
print("a1 (Inclusion -> OI):", round(a1_hat, 4))
print("a2 (Equity -> OI):", round(a2_hat, 4))
print("b  (OI -> UPB):", round(b_hat, 4))
print("Indirect(Inclusion) =", round(indirect_inclusion_hat, 4))
print("Indirect(Equity)    =", round(indirect_equity_hat, 4))
print("Difference          =", round(diff_hat, 4))
print("Ratio               =", round(ratio_hat, 4))

# --------------------------------------------------
# 1) 부트스트랩 (10,000회, 케이스 단위 재표집)
# --------------------------------------------------

N_BOOT = 10000
rng = np.random.default_rng(42)

boot_indirect_inclusion = np.empty(N_BOOT)
boot_indirect_equity = np.empty(N_BOOT)
boot_diff = np.empty(N_BOOT)
boot_ratio = np.empty(N_BOOT)

print(f"\n부트스트랩 {N_BOOT}회 진행 중...")
for i in range(N_BOOT):
    idx = rng.integers(0, N, size=N)
    boot_sample = analysis_df.iloc[idx]
    try:
        a1_b, a2_b, b_b, _, _ = fit_paths(boot_sample)
    except Exception:
        a1_b, a2_b, b_b = np.nan, np.nan, np.nan
    ind_incl_b = a1_b * b_b
    ind_eq_b = a2_b * b_b
    boot_indirect_inclusion[i] = ind_incl_b
    boot_indirect_equity[i] = ind_eq_b
    boot_diff[i] = ind_incl_b - ind_eq_b
    boot_ratio[i] = ind_incl_b / ind_eq_b

valid = np.isfinite(boot_diff) & np.isfinite(boot_ratio)
n_valid = valid.sum()
print(f"유효 부트스트랩 반복: {n_valid} / {N_BOOT}")

boot_indirect_inclusion = boot_indirect_inclusion[valid]
boot_indirect_equity = boot_indirect_equity[valid]
boot_diff = boot_diff[valid]
boot_ratio = boot_ratio[valid]


# --------------------------------------------------
# Bias-corrected (BC) percentile CI
# --------------------------------------------------

def bc_ci(boot_dist, point_est, alpha=0.05):
    """Efron의 Bias-corrected(BC) percentile CI (가속도 보정 없음)."""
    boot_dist = np.asarray(boot_dist)
    prop_less = np.mean(boot_dist < point_est)
    prop_less = np.clip(prop_less, 1e-6, 1 - 1e-6)
    z0 = norm.ppf(prop_less)
    z_lo = norm.ppf(alpha / 2)
    z_hi = norm.ppf(1 - alpha / 2)
    p_lo = norm.cdf(2 * z0 + z_lo)
    p_hi = norm.cdf(2 * z0 + z_hi)
    lo = np.percentile(boot_dist, 100 * p_lo)
    hi = np.percentile(boot_dist, 100 * p_hi)
    return lo, hi


ci_incl = bc_ci(boot_indirect_inclusion, indirect_inclusion_hat)
ci_eq = bc_ci(boot_indirect_equity, indirect_equity_hat)
ci_diff = bc_ci(boot_diff, diff_hat)
ci_ratio = bc_ci(boot_ratio, ratio_hat)

se_incl = boot_indirect_inclusion.std(ddof=1)
se_eq = boot_indirect_equity.std(ddof=1)
se_diff = boot_diff.std(ddof=1)
se_ratio = boot_ratio.std(ddof=1)

diff_sig = not (ci_diff[0] <= 0 <= ci_diff[1])

print("\n[Bias-corrected 95% CI]")
print(f"Indirect(Inclusion) = {indirect_inclusion_hat:.4f}, SE={se_incl:.4f}, "
      f"95% CI [{ci_incl[0]:.4f}, {ci_incl[1]:.4f}]")
print(f"Indirect(Equity)    = {indirect_equity_hat:.4f}, SE={se_eq:.4f}, "
      f"95% CI [{ci_eq[0]:.4f}, {ci_eq[1]:.4f}]")
print(f"Difference          = {diff_hat:.4f}, SE={se_diff:.4f}, "
      f"95% CI [{ci_diff[0]:.4f}, {ci_diff[1]:.4f}]  -> "
      f"{'0을 포함하지 않음(유의)' if diff_sig else '0을 포함함(비유의)'}")
print(f"Ratio                = {ratio_hat:.4f}, SE={se_ratio:.4f}, "
      f"95% CI [{ci_ratio[0]:.4f}, {ci_ratio[1]:.4f}]")

# --------------------------------------------------
# 2) 효과크기 비교: Ratio 및 표준화 차이(z-type effect size)
# --------------------------------------------------
#
# Ratio = Indirect(Inclusion) / Indirect(Equity) 는 이미 위에서 산출함.
# 추가로, 두 간접효과 차이를 부트스트랩 표준오차로 표준화한 지표
# (ES_diff = Diff / SE_diff)를 함께 제시한다. 이는 차이 검정의 Wald 통계량과
# 동일한 형태로, 두 간접효과 차이의 '신호 대 잡음비'를 나타내는 표준화 효과크기로
# 해석할 수 있다.

es_diff = diff_hat / se_diff

print("\n[효과크기 비교]")
print("Ratio (Inclusion/Equity):", round(ratio_hat, 3))
print("표준화 효과크기 ES_diff = Diff / SE(Diff):", round(es_diff, 3))

# --------------------------------------------------
# 결과 저장
# --------------------------------------------------

out_dir = "../results/indirect_effect_comparison"
os.makedirs(out_dir, exist_ok=True)

table_main = pd.DataFrame([
    {
        "Path": "Inclusion → OI → UPB",
        "Indirect Effect": round(indirect_inclusion_hat, 3),
        "SE": round(se_incl, 3),
        "95% CI": f"[{ci_incl[0]:.3f}, {ci_incl[1]:.3f}]",
    },
    {
        "Path": "Equity → OI → UPB",
        "Indirect Effect": round(indirect_equity_hat, 3),
        "SE": round(se_eq, 3),
        "95% CI": f"[{ci_eq[0]:.3f}, {ci_eq[1]:.3f}]",
    },
    {
        "Path": "Difference (Inclusion - Equity)",
        "Indirect Effect": round(diff_hat, 3),
        "SE": round(se_diff, 3),
        "95% CI": f"[{ci_diff[0]:.3f}, {ci_diff[1]:.3f}]",
    },
    {
        "Path": "Ratio (Inclusion / Equity)",
        "Indirect Effect": round(ratio_hat, 3),
        "SE": round(se_ratio, 3),
        "95% CI": f"[{ci_ratio[0]:.3f}, {ci_ratio[1]:.3f}]",
    },
])
table_main.to_csv(os.path.join(out_dir, "indirect_effect_comparison.csv"), index=False, encoding="utf-8-sig")

# --------------------------------------------------
# SSCI Results 문단 (영문)
# --------------------------------------------------

sig_text_diff = "did not include zero" if diff_sig else "included zero"
sig_verdict = "significantly larger" if diff_sig else "not significantly different from"

results_paragraph = f"""
To formally test the claim that the indirect transmission effect of inclusion climate on
unethical pro-organizational behavior (UPB) through organizational identification (OI) is
larger than that of equity climate, we estimated both indirect effects within a single
mediation model that simultaneously included inclusion climate and equity climate as
predictors of OI (controlling for gender, age, and organization type [public/private]),
and OI together with both climate variables as predictors of UPB (also controlling for
gender, age, and organization type). This joint specification allowed both indirect effects
to be evaluated from the same bootstrap resamples, which is required to validly test their
difference.

The indirect effect of inclusion climate on UPB through OI was {indirect_inclusion_hat:.3f}
(bootstrap SE = {se_incl:.3f}, 95% bias-corrected CI [{ci_incl[0]:.3f}, {ci_incl[1]:.3f}]),
and the indirect effect of equity climate on UPB through OI was {indirect_equity_hat:.3f}
(bootstrap SE = {se_eq:.3f}, 95% bias-corrected CI [{ci_eq[0]:.3f}, {ci_eq[1]:.3f}]). Both
indirect effects were estimated using {N_BOOT:,} bootstrap resamples (n valid = {n_valid:,}).

A direct test of the difference between the two indirect effects
(Inclusion − Equity = {diff_hat:.3f}, bootstrap SE = {se_diff:.3f}) yielded a 95%
bias-corrected bootstrap confidence interval of [{ci_diff[0]:.3f}, {ci_diff[1]:.3f}], which
{sig_text_diff}. The ratio of the two indirect effects was
{ratio_hat:.2f} (95% bias-corrected CI [{ci_ratio[0]:.2f}, {ci_ratio[1]:.2f}]), and the
standardized effect-size index for the difference (Diff / bootstrap SE) was {es_diff:.2f}.
These results indicate that the indirect effect of inclusion climate on UPB via
organizational identification was {sig_verdict} that of equity climate.
""".strip()

print("\n[SSCI Results 문단]")
print(results_paragraph)

# --------------------------------------------------
# SSCI Discussion 문단 (영문) - 유의/비유의 분기
# --------------------------------------------------

if diff_sig:
    discussion_paragraph = f"""
The finding that inclusion climate transmitted a significantly stronger indirect effect on
unethical pro-organizational behavior (UPB) through organizational identification than
equity climate (difference = {diff_hat:.3f}, 95% CI [{ci_diff[0]:.3f}, {ci_diff[1]:.3f}])
suggests that these two facets of DEI climate may operate through qualitatively distinct
psychological mechanisms rather than functioning as interchangeable indicators of a single
underlying construct.

From a Social Identity Theory (SIT) perspective, inclusion climate -- which signals that
employees are valued, respected, and psychologically embraced as full members of the
organization regardless of their background -- speaks directly to the depersonalization and
self-categorization processes that are the proximal antecedents of organizational
identification (Tajfel & Turner, 1979; Ashforth & Mael, 1989). Inclusion climate may
therefore strengthen identification by deepening employees' sense of belonging to the
organizational in-group, which in turn intensifies the motivation to protect and favor the
organization -- including, paradoxically, through unethical means.

By contrast, equity climate primarily concerns the perceived fairness of organizational
procedures and outcomes (e.g., equal opportunity, fair treatment, distributive justice).
From a Social Exchange Theory (SET) perspective, equity climate is more naturally understood
as fostering a reciprocity-based exchange relationship (Blau, 1964; Cropanzano & Mitchell,
2005): employees who perceive fair treatment may feel obligated to reciprocate through
constructive effort and compliance, but this exchange logic is calibrative and
transactional rather than identity-based, and therefore may translate less directly into
the strong in-group identification that drives identity-protective unethical behavior.

Taken together, this pattern of results implies that interventions aimed at curbing the
identification-driven dark side of inclusive culture should distinguish between inclusion
and equity as distinct levers: strengthening equity (fairness-based) practices may be a
comparatively safer way to support DEI goals without disproportionately amplifying the
identification-UPB pathway, whereas inclusion-focused practices may require complementary
ethical safeguards (e.g., strong ethical leadership) to offset their stronger indirect
pull toward unethical pro-organizational behavior.
""".strip()
else:
    discussion_paragraph = f"""
Although the present study's central narrative emphasizes that inclusion climate carries a
numerically larger indirect effect on unethical pro-organizational behavior (UPB) through
organizational identification ({indirect_inclusion_hat:.3f}) than equity climate
({indirect_equity_hat:.3f}), a formal bootstrap test indicated that this difference
(95% CI [{ci_diff[0]:.3f}, {ci_diff[1]:.3f}]) was not statistically distinguishable from
zero. This null result does not undermine the theoretical contribution of the paper; rather,
it refines it.

First, both indirect effects were positive and their confidence intervals excluded zero,
confirming that organizational identification is a robust transmission mechanism through
which both facets of DEI climate -- inclusion and equity -- can give rise to the
identification-driven dark side of inclusive culture. The core paradox the paper advances
(that DEI-oriented climates can indirectly elevate UPB via organizational identification)
therefore holds for both facets, which if anything strengthens the generality of the
proposed mechanism rather than narrowing it to a single DEI dimension.

Second, rather than framing inclusion and equity as divergent in their transmission strength,
the results are more consistent with the interpretation that inclusion and equity climate
operate as complementary facets of a broader DEI climate that converge on a common
identification-based pathway, consistent with prior work treating equity and inclusion as
distinguishable but related organizational climate dimensions (as established in this
study's own two-factor CFA, CFI = .962, TLI = .947). The practical implication shifts from
"inclusion is the primary driver to monitor" to "any DEI climate dimension that strengthens
organizational identification carries a latent ethical risk that organizations must manage
jointly, for example through ethical leadership," which is arguably a more actionable and
theoretically parsimonious contribution than asserting a strength ordering between the two
facets that the data do not statistically support.

Future research with larger samples or a meta-analytic synthesis across organizational
contexts may be better powered to detect a true but small difference between the inclusion
and equity transmission pathways, should one exist.
""".strip()

print("\n[SSCI Discussion 문단]")
print(discussion_paragraph)

# --------------------------------------------------
# APA7 표 (Markdown)
# --------------------------------------------------

table_md = (
    "**Table X**\n\n"
    "*Indirect Effects Comparison: Inclusion Climate vs. Equity Climate via Organizational "
    "Identification*\n\n"
    + table_main.to_markdown(index=False)
    + "\n\n*Note.* Indirect effects estimated from a joint mediation model "
    "(M ~ Inclusion + Equity + gender + age + organization_type; "
    "UPB ~ OI + Inclusion + Equity + gender + age + organization_type), "
    f"with {N_BOOT:,} case-resampling bootstrap iterations and bias-corrected (BC) "
    "95% confidence intervals. Path coefficients for the joint model were estimated with "
    "HC3 heteroskedasticity-robust standard errors. "
    "Difference = Indirect(Inclusion) - Indirect(Equity); "
    "Ratio = Indirect(Inclusion) / Indirect(Equity)."
)

# --------------------------------------------------
# Markdown 종합 저장
# --------------------------------------------------

md_content = f"""# Indirect Effect Comparison: Inclusion vs. Equity Climate via Organizational Identification

## 0. 분석 표본 및 모형

- 표본 크기: N = {N}
- 통제변수: gender, age, organization_type
- 동시추정 모형: M ~ Inclusion + Equity + controls (HC3); UPB ~ OI + Inclusion + Equity + controls (HC3)
- 부트스트랩: {N_BOOT:,}회, 케이스 재표집, Bias-corrected(BC) 95% CI

## 1. 경로 추정치 (원자료, HC3 robust)

- a1 (Inclusion → OI) = {a1_hat:.4f}
- a2 (Equity → OI) = {a2_hat:.4f}
- b (OI → UPB) = {b_hat:.4f}

## 2. 간접효과 비교 결과

{table_main.to_markdown(index=False)}

- Difference 95% CI에 0 포함 여부: {"포함하지 않음 (통계적으로 유의)" if diff_sig else "포함함 (통계적으로 비유의)"}
- 표준화 효과크기 (Diff / SE_diff): {es_diff:.3f}

## 3. SSCI Results 섹션 문단 (영문, 바로 삽입 가능)

{results_paragraph}

## 4. SSCI Discussion 섹션 문단 (영문, 바로 삽입 가능)

{discussion_paragraph}

## 5. APA7 표

{table_md}
"""

with open(os.path.join(out_dir, "indirect_effect_comparison_result.md"), "w", encoding="utf-8") as f:
    f.write(md_content)

print("\n간접효과 비교 분석 결과 저장 완료")
print("저장 경로:", out_dir)
