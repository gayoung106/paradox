import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2 as chi2_dist
import semopy
import os

# --------------------------------------------------
# 데이터 불러오기 및 집단 분리
# --------------------------------------------------

df = pd.read_csv(
    "../processed/analysis_data.csv"
)

df["organization_type"] = (df["유형"] == "공공").astype(int)

# 조절효과 상호작용항: 전체표본 평균중심화(grand-mean centering) -
# 두 집단에 동일한 중심화 기준을 적용하여 변수 정의를 일치시킴
# (기존 07_moderation.py와 동일한 평균중심화 컨벤션을 따름)
df["oi_c"] = df["org_identification"] - df["org_identification"].mean()
df["el_c"] = df["ethical_leadership"] - df["ethical_leadership"].mean()
df["interaction"] = df["oi_c"] * df["el_c"]

pub_df = df[df["organization_type"] == 1].reset_index(drop=True)
priv_df = df[df["organization_type"] == 0].reset_index(drop=True)

print("공공(public) 표본:", pub_df.shape[0])
print("민간(private) 표본:", priv_df.shape[0])

# 측정동일성 결과 확인 (요인동일성 충족 시에만 구조경로 비교가 정당화됨;
# Vandenberg & Lance, 2000)
try:
    flags = pd.read_csv("../results/measurement_invariance/invariance_flags.csv")
    metric_supported = bool(flags.set_index("flag").loc["metric_supported", "value"])
except FileNotFoundError:
    metric_supported = None

print("요인동일성(metric invariance) 충족 여부:", metric_supported)

# --------------------------------------------------
# 구조모형 정의 (복합점수 기반 경로모형)
# --------------------------------------------------
#
# Equity → OI, Inclusion → OI, OI → UPB, OI×EL(interaction) → UPB 의 4개 경로에
# 대해 두 집단(공공/민간) 간 차이를 검정한다. EL의 주효과(El → UPB)는 비교 대상이
# 아니므로 양 집단에서 항상 자유추정한다.

PATH_TERMS = {
    "eq_oi": ("org_identification", "equity_climate"),
    "incl_oi": ("org_identification", "inclusion_climate"),
    "oi_upb": ("upb", "org_identification"),
    "int_upb": ("upb", "interaction"),
}
PATH_LABELS_KR = {
    "eq_oi": "Equity → OI",
    "incl_oi": "Inclusion → OI",
    "oi_upb": "OI → UPB",
    "int_upb": "OI × EL → UPB (상호작용)",
}


def build_struct_desc(shared_paths: set) -> str:
    def term(lval, rval, key):
        if key in shared_paths:
            return f"INV_{key}*{rval}"
        return rval

    oi_terms = " + ".join([
        term(*PATH_TERMS["eq_oi"], "eq_oi"),
        term(*PATH_TERMS["incl_oi"], "incl_oi"),
    ])
    upb_terms = " + ".join([
        term(*PATH_TERMS["oi_upb"], "oi_upb"),
        "ethical_leadership",
        term(*PATH_TERMS["int_upb"], "int_upb"),
    ])
    return f"org_identification ~ {oi_terms}\nupb ~ {upb_terms}"


# --------------------------------------------------
# 다집단 결합 추정 (측정동일성 스크립트와 동일한 방식)
# --------------------------------------------------

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


def fit_struct_multigroup(desc):
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
    return dict(chi2=res.fun, n_params=len(res.x), success=res.success,
                pub_model=pub_model, priv_model=priv_model)


# --------------------------------------------------
# 1) 완전 자유모형 (Fully Unconstrained, 모든 경로 자유추정)
# --------------------------------------------------

print("\n[1] 완전 자유모형(모든 경로 집단별 자유추정) 적합 중...")
res_free = fit_struct_multigroup(build_struct_desc(shared_paths=set()))
print("chi2(free) =", res_free["chi2"], "n_params =", res_free["n_params"])

# 자유모형에서의 집단별 경로계수 및 표준오차 (Wald 검정용)
pub_est = res_free["pub_model"].inspect(std_est=True)
priv_est = res_free["priv_model"].inspect(std_est=True)

path_rows = []
for key, (lval, rval) in PATH_TERMS.items():
    row_pub = pub_est[(pub_est["lval"] == lval) & (pub_est["rval"] == rval)].iloc[0]
    row_priv = priv_est[(priv_est["lval"] == lval) & (priv_est["rval"] == rval)].iloc[0]
    b_pub, se_pub = float(row_pub["Estimate"]), float(row_pub["Std. Err"])
    b_priv, se_priv = float(row_priv["Estimate"]), float(row_priv["Std. Err"])
    se_diff = np.sqrt(se_pub ** 2 + se_priv ** 2)
    z = (b_pub - b_priv) / se_diff
    p_wald = 2 * (1 - chi2_dist.cdf(z ** 2, df=1) ** 0.5) if False else None
    from scipy.stats import norm
    p_wald = 2 * (1 - norm.cdf(abs(z)))
    path_rows.append({
        "Path": PATH_LABELS_KR[key],
        "key": key,
        "B_public": round(b_pub, 3),
        "SE_public": round(se_pub, 3),
        "B_private": round(b_priv, 3),
        "SE_private": round(se_priv, 3),
        "Wald_z": round(z, 3),
        "p_Wald": round(p_wald, 4),
    })

path_table = pd.DataFrame(path_rows)
print("\n[Wald z-test: 집단 간 경로계수 차이]")
print(path_table)

# --------------------------------------------------
# 2) 경로별 동일성 제약 모형 (Δχ² LR 검정, df=1)
# --------------------------------------------------

print("\n[2] 경로별 동일성 제약모형(LR 검정) 적합 중...")
lr_rows = []
for key in PATH_TERMS:
    res_constrained = fit_struct_multigroup(build_struct_desc(shared_paths={key}))
    delta_chi2 = res_constrained["chi2"] - res_free["chi2"]
    delta_chi2 = max(delta_chi2, 0.0)
    p_lr = 1 - chi2_dist.cdf(delta_chi2, df=1)
    lr_rows.append({
        "Path": PATH_LABELS_KR[key],
        "key": key,
        "Δχ²": round(delta_chi2, 3),
        "Δdf": 1,
        "p_LR": round(p_lr, 4),
        "유의성(p<.05)": "차이 있음" if p_lr < 0.05 else "차이 없음",
    })

lr_table = pd.DataFrame(lr_rows)
print("\n[경로별 Δχ² LR 검정]")
print(lr_table)

# --------------------------------------------------
# 3) 전체(omnibus) 동일성 제약 모형 (Δdf=4)
# --------------------------------------------------

print("\n[3] 전체 경로 동일성 제약모형(omnibus) 적합 중...")
res_all_constrained = fit_struct_multigroup(build_struct_desc(shared_paths=set(PATH_TERMS.keys())))
delta_chi2_omnibus = max(res_all_constrained["chi2"] - res_free["chi2"], 0.0)
p_omnibus = 1 - chi2_dist.cdf(delta_chi2_omnibus, df=4)
print(f"omnibus Δχ²(4) = {delta_chi2_omnibus:.3f}, p = {p_omnibus:.4f}")

# --------------------------------------------------
# 결과 저장
# --------------------------------------------------

out_dir = "../results/multigroup_sem"
os.makedirs(out_dir, exist_ok=True)

merged_table = path_table.merge(lr_table[["key", "Δχ²", "Δdf", "p_LR", "유의성(p<.05)"]], on="key")
merged_table = merged_table.drop(columns=["key"])

merged_table.to_csv(os.path.join(out_dir, "path_difference_tests.csv"), index=False, encoding="utf-8-sig")

omnibus_table = pd.DataFrame([{
    "Model": "전체 경로 동일성 제약 (4개 경로 모두 동일)",
    "Δχ²": round(delta_chi2_omnibus, 3),
    "Δdf": 4,
    "p": round(p_omnibus, 4),
}])
omnibus_table.to_csv(os.path.join(out_dir, "omnibus_path_test.csv"), index=False, encoding="utf-8-sig")

# --------------------------------------------------
# SSCI Results 문단 (한국어)
# --------------------------------------------------

sig_paths = merged_table[merged_table["유의성(p<.05)"] == "차이 있음"]["Path"].tolist()
sig_text = (
    ", ".join(sig_paths) + " 경로에서 공공-민간 간 통계적으로 유의한 차이가 발견되었다"
    if sig_paths else "4개 경로 모두 공공-민간 간 통계적으로 유의한 차이는 발견되지 않았다"
)

invariance_note = (
    "측정동일성 검증에서 요인동일성(metric invariance)이 지지되어, 두 집단 간 "
    "구조적 경로계수 비교가 통계적으로 정당화됨을 확인하였다."
    if metric_supported
    else "측정동일성 검증에서 요인동일성이 완전히 지지되지 않았으므로, 아래 경로계수 비교 결과는 "
    "잠정적(tentative) 결과로 해석할 필요가 있다."
)

results_paragraph = f"""
{invariance_note}

공공조직(n={pub_df.shape[0]})과 민간기업(n={priv_df.shape[0]}) 간 구조적 경로계수의
차이를 검정하기 위해 다집단 경로모형(multi-group path model)을 추정하였다. 모형은
형평성 분위기(equity climate)와 포용성 분위기(inclusion climate)가 조직동일시(OI)에
미치는 영향, 조직동일시가 비윤리적 친조직행동(UPB)에 미치는 영향, 그리고 조직동일시와
윤리적 리더십의 상호작용(OI × EL)이 UPB에 미치는 영향(조절효과)으로 구성되었다.
윤리적 리더십의 주효과는 비교 대상에서 제외하고 양 집단에서 자유추정하였다.

각 경로의 집단 간 차이는 두 가지 방식으로 검정하였다: (1) 완전 자유모형에서 추정된
집단별 비표준화 경로계수와 표준오차를 이용한 Wald z 검정, (2) 해당 경로를 두 집단 간
동일하게 제약한 모형과 완전 자유모형 간의 우도비(likelihood ratio) Δχ² 검정(df=1).

{merged_table.to_string(index=False)}

LR 검정 결과, {sig_text}. 4개 경로를 동시에 동일하게 제약한 전체(omnibus) 모형은
완전 자유모형과 비교하여 Δχ²(4) = {delta_chi2_omnibus:.3f}, p = {p_omnibus:.4f}로 나타났다.
""".strip()

print("\n[SSCI Results 문단]")
print(results_paragraph)

# --------------------------------------------------
# APA7 표 (Markdown)
# --------------------------------------------------

table_path_md = (
    "**Table X**\n\n"
    "*Multi-Group Path Coefficient Comparisons: Public vs. Private Sector*\n\n"
    + merged_table.to_markdown(index=False)
    + "\n\n*Note.* B = 비표준화 경로계수; SE = 표준오차; Wald_z = 두 집단 간 계수차의 "
    "Wald z 통계량((B_public - B_private)/sqrt(SE_public² + SE_private²)); "
    "Δχ²/Δdf/p_LR = 해당 경로를 양 집단 간 동일하게 제약한 모형과 완전 자유모형 간의 "
    "우도비 Δχ² 검정(df=1) 결과."
)

table_omnibus_md = (
    "**Table X+1**\n\n"
    "*Omnibus Test of Overall Path Equality Across Sectors*\n\n"
    + omnibus_table.to_markdown(index=False)
)

# --------------------------------------------------
# Markdown 종합 저장
# --------------------------------------------------

md_content = f"""# Multi-Group Structural Path Comparison: Public vs. Private Sector

## 0. 분석 표본 및 전제

- 공공(public): n = {pub_df.shape[0]}
- 민간(private): n = {priv_df.shape[0]}
- 측정동일성(요인동일성) 충족 여부: {metric_supported}

## 1. 방법론 노트

구조경로 비교는 복합점수(composite score) 기반 경로모형(equity_climate,
inclusion_climate, org_identification, ethical_leadership, upb 및 평균중심화
상호작용항)으로 추정하였다. 다집단 동일성 제약은 측정동일성 스크립트와 동일한
방식(공동 목적함수 결합 최적화)으로 구현하였다.

## 2. Wald z-검정 및 우도비(LR) Δχ² 검정

{merged_table.to_markdown(index=False)}

## 3. 전체(Omnibus) 경로 동일성 검정

{omnibus_table.to_markdown(index=False)}

## 4. SSCI Results 섹션 문단 (한국어)

{results_paragraph}

## 5. APA7 표

{table_path_md}

{table_omnibus_md}
"""

with open(os.path.join(out_dir, "multigroup_sem_result.md"), "w", encoding="utf-8") as f:
    f.write(md_content)

print("\n다집단 구조모형 분석 결과 저장 완료")
print("저장 경로:", out_dir)
