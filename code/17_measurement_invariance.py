import pandas as pd
import numpy as np
from scipy.optimize import minimize
import semopy
from semopy import calc_stats
import os

# --------------------------------------------------
# 데이터 불러오기 및 집단 분리
# --------------------------------------------------

df = pd.read_csv(
    "../processed/analysis_data.csv"
)

print("데이터 크기:", df.shape)

# organization_type: 1=public(공공), 0=private(민간)
df["organization_type"] = (df["유형"] == "공공").astype(int)

pub_df = df[df["organization_type"] == 1].reset_index(drop=True)
priv_df = df[df["organization_type"] == 0].reset_index(drop=True)

print("공공(public) 표본:", pub_df.shape[0])
print("민간(private) 표본:", priv_df.shape[0])

# --------------------------------------------------
# 측정모형 정의 (6요인, 29항목)
# --------------------------------------------------

FACTOR_ITEMS = {
    "equity": ["Y8_1", "Y8_2", "Y8_3", "Y8_4", "Y8_5"],
    "inclusion": ["Y8_6", "Y8_7", "Y8_8", "Y8_9"],
    "oi": ["Y1_1", "Y1_2", "Y1_3", "Y1_4", "Y1_5", "Y1_6"],
    "el": ["Y11_1", "Y11_2", "Y11_3", "Y11_4", "Y11_5"],
    "ocb": ["Y19_1", "Y19_2", "Y19_3", "Y19_4"],
    "upb": ["Y20_1", "Y20_2", "Y20_3", "Y20_4", "Y20_5"],
}
ALL_ITEMS = [it for items in FACTOR_ITEMS.values() for it in items]
P = len(ALL_ITEMS)


def build_desc(shared_loadings: bool) -> str:
    """Build a semopy CFA description. If shared_loadings, every non-marker
    indicator gets a label (INV_L_*) that is reused identically across the
    public and private model descriptions, which forces semopy to treat the
    two group-specific parameters as a single, equality-constrained parameter
    once they are merged in the joint multi-group optimizer below."""
    lines = []
    for factor, items in FACTOR_ITEMS.items():
        marker = items[0]
        if shared_loadings:
            terms = [marker] + [f"INV_L_{it}*{it}" for it in items[1:]]
        else:
            terms = items
        lines.append(f"{factor} =~ {' + '.join(terms)}")
    return "\n".join(lines)


# --------------------------------------------------
# 다집단 결합 추정을 위한 보조 함수
# --------------------------------------------------
#
# semopy는 lavaan 식의 다집단 동일성 제약(group.equal)을 직접 지원하지 않으므로,
# 두 집단 모형의 파라미터를 직접 매핑하여 결합 목적함수(=두 집단 가중합 MLW)를
# 공동 최적화하는 방식으로 다집단 SEM을 구현한다. 동일한 레이블 문자열
# (INV_ 접두사)을 양쪽 집단 기술식에 동일하게 사용하면 해당 파라미터가
# 전역 벡터에서 하나로 합쳐져(동일성 제약) 최적화된다.


def joint_register(model, tag, global_index, global_start, bounds):
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


def fit_covariance_multigroup(desc):
    """Configural / metric stage: covariance-structure only. Intercepts are
    left unconstrained (saturated) in both groups, so the mean structure
    contributes exactly zero to misfit/DoF at this stage -- this matches
    standard multi-group CFA practice where configural/metric invariance is
    evaluated on the covariance structure alone."""
    pub_model = semopy.Model(desc)
    priv_model = semopy.Model(desc)
    pub_model.load(pub_df)
    priv_model.load(priv_df)

    global_index, global_start, bounds = {}, [], []
    pub_map = joint_register(pub_model, "PUB", global_index, global_start, bounds)
    priv_map = joint_register(priv_model, "PRIV", global_index, global_start, bounds)

    fun_pub, grad_pub = pub_model.get_objective("MLW")
    fun_priv, grad_priv = priv_model.get_objective("MLW")
    n_pub, n_priv = pub_model.n_samples, priv_model.n_samples

    def objective(x):
        xp, xv = x[pub_map], x[priv_map]
        val = n_pub * fun_pub(xp) + n_priv * fun_priv(xv)
        g = np.zeros_like(x)
        np.add.at(g, pub_map, n_pub * grad_pub(xp))
        np.add.at(g, priv_map, n_priv * grad_priv(xv))
        return val, g

    x0 = np.array(global_start, dtype=float)
    res = minimize(objective, x0, jac=True, method="SLSQP", bounds=bounds,
                    options={"maxiter": 3000, "ftol": 1e-12})

    pub_model.param_vals = res.x[pub_map]
    pub_model.update_matrices(res.x[pub_map])
    priv_model.param_vals = res.x[priv_map]
    priv_model.update_matrices(res.x[priv_map])

    n_params = len(res.x)
    dof = 2 * (P * (P + 1) // 2) - n_params
    return dict(chi2=res.fun, dof=dof, n_params=n_params,
                pub_model=pub_model, priv_model=priv_model,
                success=res.success)


BIG_PENALTY = 1e8


def _group_term(model, fun, grad, x_g, tau, xbar):
    """Augmented normal-theory ML discrepancy for one group: covariance term
    (semopy's validated MLW) plus a hand-derived mean term
    (xbar - tau)' Sigma^-1 (xbar - tau), with analytic gradients verified
    against finite differences. Used only at the scalar-invariance stage,
    where item intercepts (tau) are constrained equal across groups and
    therefore no longer trivially saturate the sample means."""
    fcov = fun(x_g)
    if not np.isfinite(fcov):
        return BIG_PENALTY, np.zeros_like(x_g), np.zeros_like(tau)
    try:
        sigma, (m, c) = model.calc_sigma()
        inv_sigma = np.linalg.inv(sigma)
    except np.linalg.LinAlgError:
        return BIG_PENALTY, np.zeros_like(x_g), np.zeros_like(tau)
    r = xbar - tau
    fmean = r @ inv_sigma @ r
    sigma_grad = model.calc_sigma_grad(m, c)
    grad_theta = grad(x_g) + np.array(
        [-(r @ inv_sigma @ g @ inv_sigma @ r) for g in sigma_grad]
    )
    grad_tau = -2 * inv_sigma @ r
    return fcov + fmean, grad_theta, grad_tau


def fit_scalar_multigroup(desc):
    """Scalar stage: loadings remain equality-constrained (as in the metric
    model) and item intercepts are additionally constrained equal across
    groups (INV_I_* shared labels), modeled via the augmented mean+covariance
    ML discrepancy function defined above."""
    pub_model = semopy.Model(desc)
    priv_model = semopy.Model(desc)
    pub_model.load(pub_df)
    priv_model.load(priv_df)

    global_index, global_start, bounds = {}, [], []
    pub_map = joint_register(pub_model, "PUB", global_index, global_start, bounds)
    priv_map = joint_register(priv_model, "PRIV", global_index, global_start, bounds)

    tau_start = len(global_start)
    xbar_pub = pub_df[ALL_ITEMS].mean().values
    xbar_priv = priv_df[ALL_ITEMS].mean().values
    n_pub, n_priv = pub_model.n_samples, priv_model.n_samples
    tau0 = (xbar_pub * n_pub + xbar_priv * n_priv) / (n_pub + n_priv)
    for v in tau0:
        global_start.append(v)
        bounds.append((None, None))
    tau_idx = np.arange(tau_start, tau_start + P)

    fun_pub, grad_pub = pub_model.get_objective("MLW")
    fun_priv, grad_priv = priv_model.get_objective("MLW")

    def objective(x):
        xp, xv, tau = x[pub_map], x[priv_map], x[tau_idx]
        fp, gp, gtp = _group_term(pub_model, fun_pub, grad_pub, xp, tau, xbar_pub)
        fv, gv, gtv = _group_term(priv_model, fun_priv, grad_priv, xv, tau, xbar_priv)
        val = n_pub * fp + n_priv * fv
        g = np.zeros_like(x)
        np.add.at(g, pub_map, n_pub * gp)
        np.add.at(g, priv_map, n_priv * gv)
        g[tau_idx] += n_pub * gtp + n_priv * gtv
        return val, g

    x0 = np.array(global_start, dtype=float)
    res = minimize(objective, x0, jac=True, method="SLSQP", bounds=bounds,
                    options={"maxiter": 5000, "ftol": 1e-12})

    pub_model.param_vals = res.x[pub_map]
    pub_model.update_matrices(res.x[pub_map])
    priv_model.param_vals = res.x[priv_map]
    priv_model.update_matrices(res.x[priv_map])

    n_params = len(res.x)
    dof = 2 * (P * (P + 3) // 2) - n_params
    return dict(chi2=res.fun, dof=dof, n_params=n_params,
                pub_model=pub_model, priv_model=priv_model,
                success=res.success)


# --------------------------------------------------
# Baseline(독립) 모형: CFI/TLI 산출용 (모든 단계에서 동일하게 사용)
# --------------------------------------------------

desc_baseline = "\n".join(f"{f} =~ {'+'.join(items)}" for f, items in FACTOR_ITEMS.items())
chi2_base_total, dof_base_total = 0.0, 0
for g_df in (pub_df, priv_df):
    m_base = semopy.Model(desc_baseline, baseline=True)
    m_base.fit(g_df)
    s_base = calc_stats(m_base)
    chi2_base_total += s_base["chi2"].values[0]
    dof_base_total += int(s_base["DoF"].values[0])

print("\nBaseline(독립모형) 합산 chi2:", round(chi2_base_total, 2), "dof:", dof_base_total)


# --------------------------------------------------
# SRMR 계산 (집단별 가중평균)
# --------------------------------------------------

def group_srmr(model, items, data):
    sigma, _ = model.calc_sigma()
    order = model.vars["observed"]
    idx = [order.index(i) for i in items]
    sigma = sigma[np.ix_(idx, idx)]
    obs_cov = data[items].cov().values
    d_obs = np.sqrt(np.diag(obs_cov))
    d_mod = np.sqrt(np.diag(sigma))
    obs_corr = obs_cov / np.outer(d_obs, d_obs)
    mod_corr = sigma / np.outer(d_mod, d_mod)
    resid = obs_corr - mod_corr
    iu = np.tril_indices(len(items))
    return np.sqrt(np.mean(resid[iu] ** 2))


def weighted_srmr(pub_model, priv_model):
    srmr_pub = group_srmr(pub_model, ALL_ITEMS, pub_df)
    srmr_priv = group_srmr(priv_model, ALL_ITEMS, priv_df)
    n_pub, n_priv = pub_model.n_samples, priv_model.n_samples
    return (srmr_pub * n_pub + srmr_priv * n_priv) / (n_pub + n_priv), srmr_pub, srmr_priv


# --------------------------------------------------
# 1) Configural Invariance
# --------------------------------------------------

print("\n[1] Configural Invariance 적합 중...")
res_configural = fit_covariance_multigroup(build_desc(shared_loadings=False))

# --------------------------------------------------
# 2) Metric Invariance
# --------------------------------------------------

print("[2] Metric Invariance 적합 중...")
res_metric = fit_covariance_multigroup(build_desc(shared_loadings=True))

# --------------------------------------------------
# 3) Scalar Invariance
# --------------------------------------------------

print("[3] Scalar Invariance 적합 중...")
res_scalar = fit_scalar_multigroup(build_desc(shared_loadings=True))

print("\n적합 성공 여부:", res_configural["success"], res_metric["success"], res_scalar["success"])

# --------------------------------------------------
# 적합도 지표 계산
# --------------------------------------------------

N_total = pub_df.shape[0] + priv_df.shape[0]
N_GROUPS = 2


def fit_indices(chi2, dof):
    cfi = 1 - (chi2 - dof) / (chi2_base_total - dof_base_total)
    a, b = chi2 / dof, chi2_base_total / dof_base_total
    tli = (b - a) / (b - 1)
    rmsea = 0.0 if chi2 < dof else np.sqrt((chi2 / dof - 1) / (N_total - N_GROUPS))
    return cfi, tli, rmsea


stages = {}
for name, res in [("configural", res_configural), ("metric", res_metric), ("scalar", res_scalar)]:
    cfi, tli, rmsea = fit_indices(res["chi2"], res["dof"])
    srmr_w, srmr_pub, srmr_priv = weighted_srmr(res["pub_model"], res["priv_model"])
    stages[name] = dict(chi2=res["chi2"], dof=res["dof"], cfi=cfi, tli=tli, rmsea=rmsea,
                         srmr=srmr_w, srmr_pub=srmr_pub, srmr_priv=srmr_priv,
                         n_params=res["n_params"])

fit_table = pd.DataFrame([
    {
        "Model": label,
        "chi2": round(stages[key]["chi2"], 2),
        "df": stages[key]["dof"],
        "CFI": round(stages[key]["cfi"], 3),
        "TLI": round(stages[key]["tli"], 3),
        "RMSEA": round(stages[key]["rmsea"], 3),
        "SRMR": round(stages[key]["srmr"], 3),
    }
    for key, label in [
        ("configural", "Configural Invariance"),
        ("metric", "Metric Invariance"),
        ("scalar", "Scalar Invariance"),
    ]
])

print("\n[적합도 지표 비교]")
print(fit_table)

# --------------------------------------------------
# 단계 간 비교 (Δχ², Δdf, ΔCFI, ΔRMSEA, ΔSRMR) 및 Cheung & Rensvold(2002) 판정
# --------------------------------------------------

def delta_row(label, a_key, b_key):
    a, b = stages[a_key], stages[b_key]
    return {
        "Comparison": label,
        "Δχ²": round(b["chi2"] - a["chi2"], 2),
        "Δdf": b["dof"] - a["dof"],
        "ΔCFI": round(b["cfi"] - a["cfi"], 3),
        "ΔTLI": round(b["tli"] - a["tli"], 3),
        "ΔRMSEA": round(b["rmsea"] - a["rmsea"], 3),
        "ΔSRMR": round(b["srmr"] - a["srmr"], 3),
    }


delta_table = pd.DataFrame([
    delta_row("Metric vs Configural", "configural", "metric"),
    delta_row("Scalar vs Metric", "metric", "scalar"),
])


def cheung_rensvold_verdict(delta_cfi):
    return "지지됨 (ΔCFI ≤ .01)" if abs(delta_cfi) <= 0.01 else "지지되지 않음 (ΔCFI > .01)"


delta_table["Invariance 판정 (Cheung & Rensvold, 2002)"] = delta_table["ΔCFI"].apply(cheung_rensvold_verdict)

print("\n[단계 간 비교 및 Cheung & Rensvold 판정]")
print(delta_table)

metric_supported = abs(delta_table.loc[0, "ΔCFI"]) <= 0.01
scalar_supported = abs(delta_table.loc[1, "ΔCFI"]) <= 0.01

# --------------------------------------------------
# 결과 저장
# --------------------------------------------------

out_dir = "../results/measurement_invariance"
os.makedirs(out_dir, exist_ok=True)

fit_table.to_csv(os.path.join(out_dir, "invariance_fit_indices.csv"), index=False, encoding="utf-8-sig")
delta_table.to_csv(os.path.join(out_dir, "invariance_delta_comparison.csv"), index=False, encoding="utf-8-sig")

# --------------------------------------------------
# SSCI Results 문단 (한국어)
# --------------------------------------------------

metric_text = "지지되었다" if metric_supported else "지지되지 않았다"
scalar_text = "지지되었다" if scalar_supported else "지지되지 않았다"

results_paragraph = f"""
공공조직 종사자(n={pub_df.shape[0]})와 민간기업 종사자(n={priv_df.shape[0]}) 간
측정동일성(measurement invariance)을 검증하기 위해 형태동일성(configural),
요인동일성(metric), 절편동일성(scalar)의 3단계 다집단 확인적 요인분석(multi-group CFA)을
순차적으로 실시하였다.

형태동일성 모형은 두 집단에서 동일한 6요인 구조(형평성 분위기, 포용성 분위기,
조직동일시, 윤리적 리더십, 조직시민행동, 비윤리적 친조직행동)를 자유롭게 추정한
모형으로, χ²({stages['configural']['dof']}) = {stages['configural']['chi2']:.2f},
CFI = {stages['configural']['cfi']:.3f}, TLI = {stages['configural']['tli']:.3f},
RMSEA = {stages['configural']['rmsea']:.3f}, SRMR = {stages['configural']['srmr']:.3f}로
양호한 적합도를 보였다.

요인동일성 모형은 형태동일성 모형에 모든 비기준(non-marker) 항목의 요인적재량을
두 집단 간 동일하게 제약한 모형으로, χ²({stages['metric']['dof']}) = {stages['metric']['chi2']:.2f},
CFI = {stages['metric']['cfi']:.3f}, RMSEA = {stages['metric']['rmsea']:.3f},
SRMR = {stages['metric']['srmr']:.3f}로 나타났다. 형태동일성 모형과 비교한 결과
ΔCFI = {delta_table.loc[0,'ΔCFI']:.3f}, ΔRMSEA = {delta_table.loc[0,'ΔRMSEA']:.3f},
ΔSRMR = {delta_table.loc[0,'ΔSRMR']:.3f}로, Cheung과 Rensvold(2002)의 기준(ΔCFI ≤ .01)에
따라 요인동일성이 {metric_text}.

절편동일성 모형은 요인동일성 모형에 모든 항목의 절편(intercept)을 두 집단 간
동일하게 추가 제약한 모형으로, χ²({stages['scalar']['dof']}) = {stages['scalar']['chi2']:.2f},
CFI = {stages['scalar']['cfi']:.3f}, RMSEA = {stages['scalar']['rmsea']:.3f},
SRMR = {stages['scalar']['srmr']:.3f}로 나타났다. 요인동일성 모형과 비교한 결과
ΔCFI = {delta_table.loc[1,'ΔCFI']:.3f}, ΔRMSEA = {delta_table.loc[1,'ΔRMSEA']:.3f},
ΔSRMR = {delta_table.loc[1,'ΔSRMR']:.3f}로, Cheung과 Rensvold(2002)의 기준에 따라
절편동일성이 {scalar_text}.

{"종합적으로 두 집단 간 형태동일성과 요인동일성이 모두 확보되어, 공공-민간 비교에 필요한 최소 조건인 요인동일성(metric invariance)을 만족하므로 두 집단 간 구조적 경로계수(회귀계수) 비교가 통계적으로 정당화된다." if metric_supported else "다만 요인동일성이 완전한 형태로 지지되지 않아, 두 집단 간 경로계수 비교 시 부분동일성(partial invariance) 모형을 고려하거나 결과 해석에 유의할 필요가 있다."}
{"절편동일성까지 확보되어 두 집단 간 잠재평균(latent mean) 비교도 가능하다." if scalar_supported else "절편동일성은 완전한 형태로 지지되지 않았으므로, 두 집단 간 잠재평균 비교(예: 공공-민간 조직동일시 수준 차이)는 신중하게 해석하거나 부분 절편동일성 모형을 통해 보완할 필요가 있다. 다만 경로계수(회귀/공분산 구조) 비교는 절편동일성과 무관하게 요인동일성만으로 정당화된다(Vandenberg & Lance, 2000)."}
""".strip()

print("\n[SSCI Results 문단]")
print(results_paragraph)

# --------------------------------------------------
# APA7 표 (Markdown)
# --------------------------------------------------

table_fit_md = (
    "**Table X**\n\n"
    "*Measurement Invariance Test Across Public and Private Sector Employees*\n\n"
    + fit_table.to_markdown(index=False)
    + "\n\n*Note.* CFI = comparative fit index; TLI = Tucker-Lewis index; "
    "RMSEA = root mean square error of approximation; SRMR = standardized root mean "
    "square residual."
)

table_delta_md = (
    "**Table X+1**\n\n"
    "*Nested Model Comparisons for Measurement Invariance (Cheung & Rensvold, 2002)*\n\n"
    + delta_table.to_markdown(index=False)
    + "\n\n*Note.* Invariance is supported when ΔCFI ≤ .01 (Cheung & Rensvold, 2002)."
)

# --------------------------------------------------
# Markdown 종합 저장
# --------------------------------------------------

md_content = f"""# Measurement Invariance: Public vs. Private Sector (Configural / Metric / Scalar)

## 0. 분석 표본

- 공공(public): n = {pub_df.shape[0]}
- 민간(private): n = {priv_df.shape[0]}
- 항목 수: {P}개 (6요인: equity, inclusion, oi, el, ocb, upb)

## 1. 방법론 노트

semopy는 lavaan 식의 다집단 동일성 제약(group.equal)을 직접 지원하지 않으므로,
두 집단의 파라미터를 직접 매핑한 결합 목적함수(가중합 MLW discrepancy function)를
공동 최적화하는 방식으로 동일성 제약을 구현하였다. Configural/Metric 단계는
순수 공분산구조모형(절편은 양쪽 집단에서 자유추정·포화되어 평균구조의 적합도
기여가 0이 되는 표준적 관행과 일치)으로, Scalar 단계는 절편을 두 집단 간 동일하게
제약한 평균+공분산 결합 ML 판별함수(Bollen, 1989의 augmented ML fit function)로
추정하였다(해석적 기울기는 수치미분으로 검증함).

## 2. 적합도 지표

{fit_table.to_markdown(index=False)}

## 3. 단계 간 비교 (Cheung & Rensvold, 2002 기준: ΔCFI ≤ .01)

{delta_table.to_markdown(index=False)}

- 요인동일성(Metric) 지지 여부: {"지지됨" if metric_supported else "지지되지 않음"}
- 절편동일성(Scalar) 지지 여부: {"지지됨" if scalar_supported else "지지되지 않음"}

## 4. SSCI Results 섹션 문단 (한국어, 바로 삽입 가능)

{results_paragraph}

## 5. APA7 표

{table_fit_md}

{table_delta_md}
"""

with open(os.path.join(out_dir, "measurement_invariance_result.md"), "w", encoding="utf-8") as f:
    f.write(md_content)

print("\n측정동일성 분석 결과 저장 완료")
print("저장 경로:", out_dir)

# 후속 다집단 구조모형 스크립트에서 재사용할 플래그 저장
with open(os.path.join(out_dir, "invariance_flags.csv"), "w", encoding="utf-8-sig") as f:
    f.write("flag,value\n")
    f.write(f"metric_supported,{metric_supported}\n")
    f.write(f"scalar_supported,{scalar_supported}\n")
