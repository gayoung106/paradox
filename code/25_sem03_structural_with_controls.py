import pandas as pd
import numpy as np
from semopy import Model, calc_stats
from numpy.linalg import inv as la_inv, cond as la_cond
import os

# =====================================================================
# SEM 주분석: 구조모형 (통제변수 포함) + 다중공선성 진단
# 목적:
#   1. 통제변수(gender_male, age, public_org) 추가 후 구조모형 재추정
#      → 표5 OLS 기준과 H1~H4 경로 대조
#   2. 6요인 잠재변수 간 상관행렬 (6×6) 추출
#   3. 다중공선성·억제효과 진단
#      (a) 잠재변수 간 상관행렬 기반 VIF
#      (b) 3단계 중첩 구조모형: 형평 단독 → +포용 → +EL
#          → equity→OCB / inclusion→UPB 계수 변화 추적
# =====================================================================

# ------------------------------------------------------------------
# 데이터 로드 및 통제변수 생성
# ------------------------------------------------------------------
df = pd.read_csv("../processed/analysis_data.csv")

# '유형' 컬럼이 인코딩 문제로 깨져 있을 때를 위한 안전한 식별
non_ascii_cols = [c for c in df.columns if not all(ord(ch) < 128 for ch in c)]
if not non_ascii_cols:
    raise ValueError("'유형' 컬럼을 찾을 수 없습니다")
sector_col = non_ascii_cols[0]  # '유형' (공공/민간)
# 두 값 중 빈도가 높은 쪽(1012)이 공공 — multigroup_result 기준
pub_val = df[sector_col].value_counts().idxmax()

df["gender_male"] = (df["SQ1K1"] == 1.0).astype(int)   # 남성=1
df["age"] = 2023 - df["SQ1K2_1"]                        # 05번과 동일 기준
df["public_org"] = (df[sector_col] == pub_val).astype(int)  # 공공=1

print("데이터 크기:", df.shape)
print(f"public_org: 공공={df['public_org'].sum()}, 민간={len(df)-df['public_org'].sum()}")

# ------------------------------------------------------------------
# 공통 설정
# ------------------------------------------------------------------
FACTOR_ITEMS = {
    "equity":    ["Y8_1",  "Y8_2",  "Y8_3",  "Y8_4",  "Y8_5"],
    "inclusion": ["Y8_6",  "Y8_7",  "Y8_8",  "Y8_9"],
    "oi":        ["Y1_1",  "Y1_2",  "Y1_3",  "Y1_4",  "Y1_5",  "Y1_6"],
    "el":        ["Y11_1", "Y11_2", "Y11_3", "Y11_4", "Y11_5"],
    "ocb":       ["Y19_1", "Y19_2", "Y19_3", "Y19_4"],
    "upb":       ["Y20_1", "Y20_2", "Y20_3", "Y20_4", "Y20_5"],
}
ALL_ITEMS = [item for items in FACTOR_ITEMS.values() for item in items]
FACTORS = list(FACTOR_ITEMS.keys())
MEAS_DESC = "\n".join(
    f"{f} =~ {' + '.join(items)}" for f, items in FACTOR_ITEMS.items()
)
CTRL = "+ gender_male + age + public_org"


def calc_srmr(model, items, data):
    sigma, _ = model.calc_sigma()
    order = model.vars["observed"]
    idx = [order.index(i) for i in items if i in order]
    sigma_sub = sigma[np.ix_(idx, idx)]
    obs_cov = data[items].cov().values
    d_obs = np.sqrt(np.diag(obs_cov))
    d_mod = np.sqrt(np.diag(sigma_sub))
    obs_corr = obs_cov / np.outer(d_obs, d_obs)
    mod_corr = sigma_sub / np.outer(d_mod, d_mod)
    resid = obs_corr - mod_corr
    iu = np.tril_indices(len(items))
    return float(np.sqrt(np.mean(resid[iu] ** 2)))


# =====================================================================
# PART A: 6요인 CFA → 잠재변수 간 상관행렬 (6×6)
# =====================================================================
print("\n" + "=" * 60)
print("PART A: 6-factor CFA -- latent correlation matrix")
print("=" * 60)

cfa_model = Model(MEAS_DESC)
cfa_model.fit(df)
params_cfa = cfa_model.inspect()

# 요인 분산 (비표준화)
fvars = {
    r["lval"]: float(r["Estimate"])
    for _, r in params_cfa[
        (params_cfa["op"] == "~~") &
        (params_cfa["lval"] == params_cfa["rval"]) &
        (params_cfa["lval"].isin(FACTORS))
    ].iterrows()
}

# 요인 공분산 (비표준화)
fcovs = params_cfa[
    (params_cfa["op"] == "~~") &
    (params_cfa["lval"].isin(FACTORS)) &
    (params_cfa["rval"].isin(FACTORS)) &
    (params_cfa["lval"] != params_cfa["rval"])
].copy()

# 상관행렬 구성: corr = cov / sqrt(var_i * var_j)
corr_mat = pd.DataFrame(np.eye(len(FACTORS)), index=FACTORS, columns=FACTORS)
for _, row in fcovs.iterrows():
    l, r = row["lval"], row["rval"]
    if l in fvars and r in fvars:
        cov = float(row["Estimate"])
        corr = cov / np.sqrt(fvars[l] * fvars[r])
        corr_mat.loc[l, r] = round(corr, 4)
        corr_mat.loc[r, l] = round(corr, 4)

print("\n[6×6 잠재변수 간 상관행렬]")
print(corr_mat.round(3).to_string())

# ------------------------------------------------------------------
# VIF: 구조방정식의 주요 예측변수(equity, inclusion, el, oi) 기준
# ------------------------------------------------------------------
pred_names = ["equity", "inclusion", "el", "oi"]
R = corr_mat.loc[pred_names, pred_names].values.astype(float)
R_inv = la_inv(R)
vifs = {pred_names[i]: round(float(R_inv[i, i]), 3) for i in range(len(pred_names))}
cond_num = round(float(la_cond(R)), 2)

print("\n[잠재변수 VIF (UPB/OCB 구조방정식 내 주요 예측변수)]")
for k, v in vifs.items():
    print(f"  {k}: VIF = {v:.3f}")
print(f"  조건수(condition number): {cond_num:.2f}")

# 주요 상관 (억제효과 진단)
print("\n[억제효과 관련 잠재변수 쌍 상관]")
pairs = [
    ("equity", "inclusion"),
    ("equity", "el"),
    ("equity", "oi"),
    ("inclusion", "el"),
    ("inclusion", "oi"),
]
for a, b in pairs:
    print(f"  {a} - {b}: r = {corr_mat.loc[a, b]:.3f}")


# =====================================================================
# PART B: 완전 구조모형 (통제변수 포함) — 표5 대조
# =====================================================================
print("\n" + "=" * 60)
print("PART B: Full structural model with controls -- Table5 comparison")
print("=" * 60)

struct_full_desc = f"""
{MEAS_DESC}
oi ~ equity + inclusion {CTRL}
upb ~ oi + equity + inclusion + el {CTRL}
ocb ~ oi + equity + inclusion + el {CTRL}
"""

model_full = Model(struct_full_desc)
model_full.fit(df)
stats_full = calc_stats(model_full).iloc[0]
srmr_full = calc_srmr(model_full, ALL_ITEMS, df)

print("\n[구조모형(통제변수 포함) 적합도]")
print(f"chi2({int(stats_full['DoF'])}) = {stats_full['chi2']:.2f}")
print(f"CFI = {stats_full['CFI']:.4f}")
print(f"TLI = {stats_full['TLI']:.4f}")
print(f"RMSEA = {stats_full['RMSEA']:.4f}")
print(f"SRMR = {srmr_full:.4f}")

est_full = model_full.inspect(std_est=True)
struct_df = est_full[
    (est_full["op"] == "~") &
    (est_full["lval"].isin(["oi", "upb", "ocb"]))
][["lval", "rval", "Estimate", "Std. Err", "z-value", "p-value", "Est. Std"]].copy()
struct_df.columns = ["dv", "predictor", "b", "se", "z", "p", "beta_std"]
for c in ["b", "se", "z", "beta_std"]:
    struct_df[c] = struct_df[c].astype(float).round(4)

print("\n[구조 경로계수]")
print(struct_df.to_string(index=False))

# 표5 OLS 기준선 (EL 제외 모형: OI+DEI → UPB/OCB)
# 표5는 EL을 포함하지 않으므로, EL 경로는 OLS 없음으로 표기
table5_ref = pd.DataFrame([
    {"dv": "oi",  "predictor": "equity",    "t5_beta": None,   "t5_p": None,    "note": "표5 미포함(단순매개)"},
    {"dv": "oi",  "predictor": "inclusion", "t5_beta": None,   "t5_p": None,    "note": "표5 미포함(단순매개)"},
    {"dv": "upb", "predictor": "oi",        "t5_beta":  0.150, "t5_p": "<.001", "note": "H3 UPB측"},
    {"dv": "upb", "predictor": "equity",    "t5_beta":  0.195, "t5_p": "<.001", "note": "H4 형평→UPB"},
    {"dv": "upb", "predictor": "inclusion", "t5_beta": -0.033, "t5_p": ".307",  "note": "H4 교차(ns)"},
    {"dv": "upb", "predictor": "el",        "t5_beta": None,   "t5_p": None,    "note": "표5 미포함(표4)"},
    {"dv": "ocb", "predictor": "oi",        "t5_beta":  0.215, "t5_p": "<.001", "note": "H3 OCB측"},
    {"dv": "ocb", "predictor": "equity",    "t5_beta": -0.042, "t5_p": ".052",  "note": "H4 교차(ns†)"},
    {"dv": "ocb", "predictor": "inclusion", "t5_beta":  0.281, "t5_p": "<.001", "note": "H4 포용→OCB"},
    {"dv": "ocb", "predictor": "el",        "t5_beta": None,   "t5_p": None,    "note": "표5 미포함(표4)"},
    # 통제변수
    {"dv": "upb", "predictor": "gender_male", "t5_beta": -0.017, "t5_p": ".651", "note": "통제"},
    {"dv": "upb", "predictor": "age",          "t5_beta": -0.007, "t5_p": ".001", "note": "통제"},
    {"dv": "upb", "predictor": "public_org",   "t5_beta": -0.149, "t5_p": "<.001","note": "통제"},
    {"dv": "ocb", "predictor": "gender_male", "t5_beta": -0.058, "t5_p": ".029", "note": "통제"},
    {"dv": "ocb", "predictor": "age",          "t5_beta":  0.005, "t5_p": ".001", "note": "통제"},
    {"dv": "ocb", "predictor": "public_org",   "t5_beta":  0.129, "t5_p": "<.001","note": "통제"},
])

merged = struct_df.merge(table5_ref, on=["dv", "predictor"], how="left")
merged["부호일치"] = merged.apply(
    lambda r: "✓" if r["t5_beta"] is None or np.sign(r["beta_std"]) == np.sign(r["t5_beta"])
    else "❌", axis=1
)
merged["유의성일치"] = merged.apply(
    lambda r: "—" if r["t5_beta"] is None else
              ("✓" if (float(r["p"]) < 0.05) == (r["t5_p"] not in (".307", ".052", ".651"))
               else "⚠️"), axis=1
)
# 교차경로 별도 표기
cross_mask = merged["predictor"].isin(["equity", "inclusion"]) & \
             ((merged["dv"] == "ocb") & (merged["predictor"] == "equity") |
              (merged["dv"] == "upb") & (merged["predictor"] == "inclusion"))
merged.loc[cross_mask, "유의성일치"] = merged.loc[cross_mask].apply(
    lambda r: "✓(ns)" if float(r["p"]) >= 0.05 else "❌(sig→sig→?)", axis=1
)

print("\n[표5 OLS vs SEM(통제포함) 대조]")
display_cols = ["dv", "predictor", "beta_std", "p", "t5_beta", "t5_p", "부호일치", "유의성일치", "note"]
print(merged[display_cols].to_string(index=False))


# =====================================================================
# PART C: 억제효과 진단 — 3단계 중첩 구조모형
# =====================================================================
print("\n" + "=" * 60)
print("PART C: Nested structural models (suppressor effect diagnosis)")
print("=" * 60)

FOCUS_PATHS = [
    ("ocb", "equity"),       # 형평 → OCB (교차경로)
    ("upb", "inclusion"),    # 포용 → UPB (교차경로)
    ("ocb", "inclusion"),    # 포용 → OCB (주경로)
    ("upb", "equity"),       # 형평 → UPB (주경로)
    ("oi",  "equity"),
    ("oi",  "inclusion"),
]


def fit_extract(desc, label):
    m = Model(desc)
    m.fit(df)
    est = m.inspect(std_est=True)
    rows = []
    for (dv, pred) in FOCUS_PATHS:
        row = est[(est["lval"] == dv) & (est["op"] == "~") & (est["rval"] == pred)]
        if len(row) > 0:
            rows.append({
                "단계": label,
                "dv": dv,
                "predictor": pred,
                "beta_std": round(float(row["Est. Std"].iloc[0]), 4),
                "p": round(float(row["p-value"].iloc[0]), 4),
            })
        else:
            rows.append({
                "단계": label, "dv": dv, "predictor": pred,
                "beta_std": None, "p": None,
            })
    return rows


# Stage A: 형평만
desc_a = f"""
{MEAS_DESC}
oi ~ equity {CTRL}
upb ~ oi + equity {CTRL}
ocb ~ oi + equity {CTRL}
"""
print("\n[Stage A: 형평(equity)만 구조투입 중...]", flush=True)
rows_a = fit_extract(desc_a, "A: equity 단독")

# Stage B: 형평+포용
desc_b = f"""
{MEAS_DESC}
oi ~ equity + inclusion {CTRL}
upb ~ oi + equity + inclusion {CTRL}
ocb ~ oi + equity + inclusion {CTRL}
"""
print("[Stage B: 형평+포용 구조투입 중...]", flush=True)
rows_b = fit_extract(desc_b, "B: +inclusion")

# Stage C: 형평+포용+EL (완전 모형)
desc_c = f"""
{MEAS_DESC}
oi ~ equity + inclusion {CTRL}
upb ~ oi + equity + inclusion + el {CTRL}
ocb ~ oi + equity + inclusion + el {CTRL}
"""
print("[Stage C: 형평+포용+EL 구조투입 중...]", flush=True)
rows_c = fit_extract(desc_c, "C: +EL (완전)")

nested_df = pd.DataFrame(rows_a + rows_b + rows_c)
print("\n[3단계 중첩모형: 교차경로·주요경로 계수 변화]")
print(nested_df.to_string(index=False))

# 교차경로만 요약 비교
cross_df = nested_df[nested_df["predictor"].isin(["equity", "inclusion"]) &
                      ((nested_df["dv"] == "ocb") | (nested_df["dv"] == "upb"))].copy()
cross_pivot = cross_df.pivot_table(
    index=["dv", "predictor"], columns="단계", values="beta_std"
).reset_index()
print("\n[교차경로 변화 요약 (beta_std)]")
print(cross_pivot.to_string(index=False))

# OCB~equity 단독 단계에서의 상관
print("\n[참고] 잠재 equity-inclusion 상관:",
      round(float(corr_mat.loc["equity", "inclusion"]), 3))
print("[참고] 잠재 equity-el 상관:",
      round(float(corr_mat.loc["equity", "el"]), 3))
print("[참고] 잠재 inclusion-ocb 상관 (HTMT 기반):",
      round(float(corr_mat.loc["inclusion", "ocb"]), 3))
print("[참고] 잠재 equity-ocb 상관 (HTMT 기반):",
      round(float(corr_mat.loc["equity", "ocb"]), 3))


# =====================================================================
# 결과 저장
# =====================================================================
out_dir = "../results/sem"
os.makedirs(out_dir, exist_ok=True)

# 잠재변수 상관행렬
corr_mat.round(4).to_csv(
    os.path.join(out_dir, "sem03_latent_corr_matrix.csv"),
    encoding="utf-8-sig"
)

# VIF
vif_df = pd.DataFrame([{"predictor": k, "VIF": v} for k, v in vifs.items()])
vif_df["condition_number"] = cond_num
vif_df.to_csv(
    os.path.join(out_dir, "sem03_latent_vif.csv"),
    index=False, encoding="utf-8-sig"
)

# 구조모형(통제포함) 적합도 및 경로
fit_row = pd.DataFrame([{
    "chi2": round(float(stats_full["chi2"]), 2),
    "df": int(stats_full["DoF"]),
    "CFI": round(float(stats_full["CFI"]), 4),
    "TLI": round(float(stats_full["TLI"]), 4),
    "RMSEA": round(float(stats_full["RMSEA"]), 4),
    "SRMR": round(srmr_full, 4),
}])
fit_row.to_csv(os.path.join(out_dir, "sem03_fit_indices.csv"), index=False, encoding="utf-8-sig")
merged.to_csv(os.path.join(out_dir, "sem03_vs_table5_comparison.csv"), index=False, encoding="utf-8-sig")
nested_df.to_csv(os.path.join(out_dir, "sem03_nested_model_paths.csv"), index=False, encoding="utf-8-sig")

# 마크다운 보고서
md = f"""# SEM 주분석: 구조모형(통제변수 포함) + 다중공선성·억제효과 진단

## A. 잠재변수 간 상관행렬 (6×6, 6요인 CFA 기반)

{corr_mat.round(3).to_markdown()}

## B. 잠재변수 VIF (UPB/OCB 구조방정식 주요 예측변수)

{vif_df.to_markdown(index=False)}

*Note.* VIF = (R⁻¹)_{{jj}}: 잠재변수 상관행렬의 역행렬 대각 원소.
기준: VIF < 5 양호, ≥ 10 다중공선성 우려.

## C. 완전 구조모형 적합도 (통제변수 포함)

{fit_row.to_markdown(index=False)}

## D. 표5 OLS vs SEM(통제포함) 대조

{merged[display_cols].to_markdown(index=False)}

## E. 3단계 중첩모형 억제효과 진단

{nested_df.to_markdown(index=False)}

### 교차경로 변화 요약

{cross_pivot.to_markdown(index=False)}
"""

with open(os.path.join(out_dir, "sem03_controls_multicollinearity_result.md"), "w", encoding="utf-8") as f:
    f.write(md)

print("\n결과 저장 완료:", out_dir)
