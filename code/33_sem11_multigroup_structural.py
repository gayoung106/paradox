import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2 as chi2_dist, norm
import semopy
import os

# =============================================================
# SEM 주분석 6단계: 다집단 구조모형 (공공 vs 민간)
#
# 18_multigroup_sem_paths.py는 복합점수(composite score) 기반 경로모형이었다.
# 여기서는 동일한 4개 핵심 경로를 전부 잠재변수로 승격하여 재검증한다:
#   equity -> OI, inclusion -> OI, OI -> UPB, OI x EL(잠재 상호작용, PI) -> UPB
#
# 17_measurement_invariance.py에서 확인된 상태: 요인동일성(metric)은 지지됨
# (ΔCFI=-.001), 절편동일성(scalar)은 근소하게 미지지(ΔCFI=-.012). 따라서
# 요인적재량은 두 집단 간 동일하게 제약(metric invariance 유지)하되,
# 절편/잠재평균은 다루지 않는다 - 오직 구조 경로계수 비교만 수행한다
# (Vandenberg & Lance, 2000: 경로계수 비교는 요인동일성만으로 정당화됨).
#
# 상호작용(OI x EL)은 5단계에서 확정한 matched-pairs 곱셈지표(product
# indicator) 방식을 그대로 사용한다: 이중평균중심화는 전체표본(공공+민간
# 통합) 기준으로 1회 수행한 뒤 두 집단으로 분리한다(그룹별 재중심화 아님 -
# 지표 척도를 두 집단 간 동일하게 유지하기 위함).
# =============================================================

df = pd.read_csv("../processed/analysis_data.csv")
df["gender_male"] = (df["SQ1K1"] == 1.0).astype(int)
df["age"] = 2023 - df["SQ1K2_1"]
df["public_org"] = (df["유형"] == "공공").astype(int)

OI_ITEMS = ["Y1_1", "Y1_2", "Y1_3", "Y1_4", "Y1_5", "Y1_6"]
EL_ITEMS = ["Y11_1", "Y11_2", "Y11_3", "Y11_4", "Y11_5"]
OI_MATCHED = OI_ITEMS[:5]

# 그랜드 평균중심화 (전체표본 기준, 1회) 후 두 집단으로 분리
for k, (oi_it, el_it) in enumerate(zip(OI_MATCHED, EL_ITEMS), 1):
    mc_oi = df[oi_it] - df[oi_it].mean()
    mc_el = df[el_it] - df[el_it].mean()
    df[f"pi_{k}"] = mc_oi * mc_el
PI_ITEMS = [f"pi_{k}" for k in range(1, 6)]

pub_df = df[df["public_org"] == 1].reset_index(drop=True)
priv_df = df[df["public_org"] == 0].reset_index(drop=True)
print("공공(public) 표본:", pub_df.shape[0])
print("민간(private) 표본:", priv_df.shape[0])

FACTOR_ITEMS = {
    "equity": ["Y8_1", "Y8_2", "Y8_3", "Y8_4", "Y8_5"],
    "inclusion": ["Y8_6", "Y8_7", "Y8_8", "Y8_9"],
    "oi": OI_ITEMS,
    "el": EL_ITEMS,
    "ocb": ["Y19_1", "Y19_2", "Y19_3", "Y19_4"],
    "upb": ["Y20_1", "Y20_2", "Y20_3", "Y20_4", "Y20_5"],
}
ALL_ITEMS = [it for items in FACTOR_ITEMS.values() for it in items] + PI_ITEMS

# --------------------------------------------------
# 측정모형 기술식 (요인동일성: 비마커 적재량 공유 라벨)
# --------------------------------------------------


def build_measurement(shared_loadings: bool) -> str:
    lines = []
    for factor, items in FACTOR_ITEMS.items():
        marker = items[0]
        if shared_loadings:
            terms = [marker] + [f"INV_L_{it}*{it}" for it in items[1:]]
        else:
            terms = items
        lines.append(f"{factor} =~ {' + '.join(terms)}")
    # oi_el (PI) factor loadings also constrained equal across groups
    if shared_loadings:
        pi_terms = [PI_ITEMS[0]] + [f"INV_L_{it}*{it}" for it in PI_ITEMS[1:]]
    else:
        pi_terms = PI_ITEMS
    lines.append(f"oi_el =~ {' + '.join(pi_terms)}")
    return "\n".join(lines)


CTRL = "+ gender_male + age"  # public_org already used as the grouping variable

PATH_TERMS = {
    "eq_oi": ("oi", "equity"),
    "incl_oi": ("oi", "inclusion"),
    "oi_upb": ("upb", "oi"),
    "int_upb": ("upb", "oi_el"),
}
PATH_LABELS_KR = {
    "eq_oi": "Equity -> OI",
    "incl_oi": "Inclusion -> OI",
    "oi_upb": "OI -> UPB",
    "int_upb": "OI x EL -> UPB (잠재 상호작용)",
}


def build_struct(shared_paths: set) -> str:
    def term(rval, key):
        return f"INV_{key}*{rval}" if key in shared_paths else rval

    oi_terms = " + ".join([
        term("equity", "eq_oi"),
        term("inclusion", "incl_oi"),
        # controls on oi
    ]) + f" {CTRL}"
    upb_terms = " + ".join([
        term("oi", "oi_upb"),
        term("oi_el", "int_upb"),
        "el", "equity", "inclusion",
    ]) + f" {CTRL}"
    return f"oi ~ {oi_terms}\nupb ~ {upb_terms}"


MEASUREMENT_DESC = build_measurement(shared_loadings=True)  # metric invariance held fixed

# --------------------------------------------------
# 다집단 결합 추정 (17/18번과 동일한 패턴)
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


def fit_struct_multigroup(struct_desc):
    full_desc = f"{MEASUREMENT_DESC}\n{struct_desc}"
    pub_model = semopy.Model(full_desc)
    priv_model = semopy.Model(full_desc)
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
                    options={"maxiter": 3000, "ftol": 1e-10})

    pub_model.param_vals = res.x[pub_map]
    pub_model.update_matrices(res.x[pub_map])
    priv_model.param_vals = res.x[priv_map]
    priv_model.update_matrices(res.x[priv_map])

    return dict(chi2=res.fun, n_params=len(res.x), success=res.success,
                pub_model=pub_model, priv_model=priv_model)


# --------------------------------------------------
# 1) 완전 자유모형
# --------------------------------------------------

print("\n[1] 완전 자유모형(4개 경로 모두 집단별 자유추정) 적합 중...")
res_free = fit_struct_multigroup(build_struct(shared_paths=set()))
print("chi2(free) =", round(res_free["chi2"], 3), "n_params =", res_free["n_params"],
      "success =", res_free["success"])

pub_est = res_free["pub_model"].inspect(std_est=True)
priv_est = res_free["priv_model"].inspect(std_est=True)

path_rows = []
for key, (lval, rval) in PATH_TERMS.items():
    row_pub = pub_est[(pub_est["lval"] == lval) & (pub_est["rval"] == rval) & (pub_est["op"] == "~")].iloc[0]
    row_priv = priv_est[(priv_est["lval"] == lval) & (priv_est["rval"] == rval) & (priv_est["op"] == "~")].iloc[0]
    b_pub, se_pub = float(row_pub["Estimate"]), float(row_pub["Std. Err"])
    b_priv, se_priv = float(row_priv["Estimate"]), float(row_priv["Std. Err"])
    se_diff = np.sqrt(se_pub ** 2 + se_priv ** 2)
    z = (b_pub - b_priv) / se_diff
    p_wald = 2 * (1 - norm.cdf(abs(z)))
    path_rows.append({
        "Path": PATH_LABELS_KR[key], "key": key,
        "B_public": round(b_pub, 4), "SE_public": round(se_pub, 4),
        "B_private": round(b_priv, 4), "SE_private": round(se_priv, 4),
        "Wald_z": round(z, 3), "p_Wald": round(p_wald, 4),
    })

path_table = pd.DataFrame(path_rows)
print("\n[Wald z-test: 집단 간 경로계수 차이]")
print(path_table.to_string(index=False))

# --------------------------------------------------
# 2) 경로별 동일성 제약 (LR 검정)
# --------------------------------------------------

print("\n[2] 경로별 동일성 제약모형(LR 검정) 적합 중...")
lr_rows = []
for key in PATH_TERMS:
    res_c = fit_struct_multigroup(build_struct(shared_paths={key}))
    dchi2 = max(res_c["chi2"] - res_free["chi2"], 0.0)
    p_lr = 1 - chi2_dist.cdf(dchi2, df=1)
    lr_rows.append({"Path": PATH_LABELS_KR[key], "key": key,
                     "Δχ²": round(dchi2, 3), "Δdf": 1, "p_LR": round(p_lr, 4),
                     "유의성(p<.05)": "차이 있음" if p_lr < 0.05 else "차이 없음"})
lr_table = pd.DataFrame(lr_rows)
print(lr_table.to_string(index=False))

# --------------------------------------------------
# 3) Omnibus
# --------------------------------------------------

print("\n[3] 전체 경로 동일성 제약모형(omnibus) 적합 중...")
res_all = fit_struct_multigroup(build_struct(shared_paths=set(PATH_TERMS.keys())))
dchi2_omni = max(res_all["chi2"] - res_free["chi2"], 0.0)
p_omni = 1 - chi2_dist.cdf(dchi2_omni, df=4)
print(f"omnibus Δχ²(4) = {dchi2_omni:.3f}, p = {p_omni:.4f}")

# --------------------------------------------------
# 결과 저장
# --------------------------------------------------

out_dir = "../results/sem"
os.makedirs(out_dir, exist_ok=True)

merged_table = path_table.merge(lr_table[["key", "Δχ²", "Δdf", "p_LR", "유의성(p<.05)"]], on="key")
merged_table = merged_table.drop(columns=["key"])
merged_table.to_csv(os.path.join(out_dir, "sem11_multigroup_path_tests.csv"), index=False, encoding="utf-8-sig")

omnibus_table = pd.DataFrame([{
    "Model": "전체 4개 경로 동일성 제약 (잠재변수)",
    "Δχ²": round(dchi2_omni, 3), "Δdf": 4, "p": round(p_omni, 4),
}])
omnibus_table.to_csv(os.path.join(out_dir, "sem11_multigroup_omnibus.csv"), index=False, encoding="utf-8-sig")

# 18번(복합점수) 결과와 대조
composite_ref = pd.DataFrame([
    {"Path": "Equity -> OI", "p_Wald_composite": 0.292, "p_LR_composite": 0.292},
    {"Path": "Inclusion -> OI", "p_Wald_composite": 0.241, "p_LR_composite": 0.241},
    {"Path": "OI -> UPB", "p_Wald_composite": 0.733, "p_LR_composite": 0.745},
    {"Path": "OI x EL -> UPB (상호작용)", "p_Wald_composite": 0.538, "p_LR_composite": 0.543},
])
comparison = merged_table.merge(composite_ref, on="Path", how="left")
comparison.to_csv(os.path.join(out_dir, "sem11_vs_composite_18_comparison.csv"), index=False, encoding="utf-8-sig")

print("\n[잠재변수 vs 복합점수(18번) 대조]")
print(comparison.to_string(index=False))

sig_paths = merged_table[merged_table["유의성(p<.05)"] == "차이 있음"]["Path"].tolist()
sig_text = (", ".join(sig_paths) + " 경로에서 공공-민간 간 유의한 차이가 발견되었다"
            if sig_paths else "4개 경로 모두 공공-민간 간 통계적으로 유의한 차이는 발견되지 않았다")

md_content = f"""# SEM 주분석 6단계: 다집단 구조모형 (잠재변수, 공공 vs 민간)

## 0. 전제

- 요인동일성(metric invariance)만 유지: 요인적재량은 두 집단 간 동일 제약,
  절편/잠재평균은 다루지 않음 (17번: 절편동일성 미지지, ΔCFI=-.012).
- 경로계수 비교만 수행하며 잠재평균 비교는 하지 않음(Vandenberg & Lance, 2000).
- 상호작용(OI x EL)은 5단계에서 확정한 matched-pairs 곱셈지표(PI), 전체표본
  그랜드 평균중심화, 곱지표 간 잔차공분산 비제약.
- 통제변수: 성별, 연령 (조직유형은 집단분리 변수이므로 통제에서 제외).

## 1. Wald z-검정 및 우도비(LR) Δχ² 검정

{merged_table.to_markdown(index=False)}

## 2. 전체(Omnibus) 경로 동일성 검정

{omnibus_table.to_markdown(index=False)}

## 3. 복합점수(18번, 논문 게재값)와의 대조

{comparison.to_markdown(index=False)}

*Note.* p_Wald_composite/p_LR_composite = 18번(복합점수 기반 경로모형)의
논문 게재값. 대조 기준: 4개 핵심 경로 모두 공공-민간 차이 없음(모든 p>.24),
omnibus Δχ²(4)=2.067, p=.723.

## 4. 결론

LR 검정 결과, {sig_text}. 전체 경로를 동시에 제약한 omnibus 모형은
완전 자유모형과 비교하여 Δχ²(4) = {dchi2_omni:.3f}, p = {p_omni:.4f}로 나타났다.
"""

with open(os.path.join(out_dir, "sem11_multigroup_structural_result.md"), "w", encoding="utf-8") as f:
    f.write(md_content)

print("\nSEM 6단계 결과 저장 완료")
print("저장 경로:", out_dir)
