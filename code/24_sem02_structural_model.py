import pandas as pd
import numpy as np
from semopy import Model, calc_stats
import os

# --------------------------------------------------
# SEM 주분석 3단계: 잠재변수 구조모형 (측정모형 + 구조모형 동시추정)
# --------------------------------------------------
# 05/11번의 복합점수(composite score) OLS 회귀와 동일한 구조적 경로를
# 전부 잠재변수로 승격하여 한 모형에서 동시추정한다:
#   oi ~ equity + inclusion
#   upb ~ oi + equity + inclusion + el
#   ocb ~ oi + equity + inclusion + el
# 05/11번 Model 4(복합점수 기반)와 표준화 경로계수를 나란히 대조하여,
# 잠재변수 승격이 부호/유의성을 뒤집는 경로가 있는지 확인한다.

df = pd.read_csv("../processed/analysis_data.csv")

print("데이터 크기:", df.shape)

model_desc = """
equity =~ Y8_1 + Y8_2 + Y8_3 + Y8_4 + Y8_5
inclusion =~ Y8_6 + Y8_7 + Y8_8 + Y8_9
oi =~ Y1_1 + Y1_2 + Y1_3 + Y1_4 + Y1_5 + Y1_6
el =~ Y11_1 + Y11_2 + Y11_3 + Y11_4 + Y11_5
ocb =~ Y19_1 + Y19_2 + Y19_3 + Y19_4
upb =~ Y20_1 + Y20_2 + Y20_3 + Y20_4 + Y20_5

oi ~ equity + inclusion
upb ~ oi + equity + inclusion + el
ocb ~ oi + equity + inclusion + el
"""

model = Model(model_desc)
model.fit(df)
stats = calc_stats(model).iloc[0]


def calc_srmr(model, items, data):
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


all_items = ["Y8_1", "Y8_2", "Y8_3", "Y8_4", "Y8_5", "Y8_6", "Y8_7", "Y8_8", "Y8_9",
             "Y1_1", "Y1_2", "Y1_3", "Y1_4", "Y1_5", "Y1_6",
             "Y11_1", "Y11_2", "Y11_3", "Y11_4", "Y11_5",
             "Y19_1", "Y19_2", "Y19_3", "Y19_4",
             "Y20_1", "Y20_2", "Y20_3", "Y20_4", "Y20_5"]
srmr = calc_srmr(model, all_items, df)

print("\n[구조모형 적합도]")
print(f"chi2({int(stats['DoF'])}) = {stats['chi2']:.2f}")
print(f"CFI = {stats['CFI']:.4f}")
print(f"TLI = {stats['TLI']:.4f}")
print(f"RMSEA = {stats['RMSEA']:.4f}")
print(f"SRMR = {srmr:.4f}")

est = model.inspect(std_est=True)
struct = est[(est["op"] == "~") & (est["rval"].isin(["equity", "inclusion", "oi", "el"]))].copy()
struct = struct[struct["lval"].isin(["oi", "upb", "ocb"])]
struct = struct[["lval", "rval", "Estimate", "Std. Err", "z-value", "p-value", "Est. Std"]]
struct.columns = ["dv", "predictor", "b", "se", "z", "p", "beta_std"]
for c in ["b", "se", "z", "beta_std"]:
    struct[c] = struct[c].astype(float).round(4)

print("\n[구조 경로계수 (잠재변수)]")
print(struct.to_string(index=False))

# --------------------------------------------------
# 05/11번(복합점수 OLS, Model 4)과의 대조
# --------------------------------------------------

composite_model4 = pd.DataFrame([
    {"dv": "upb", "predictor": "equity", "beta_composite": 0.1854, "p_composite": "<.001"},
    {"dv": "upb", "predictor": "inclusion", "beta_composite": -0.0365, "p_composite": ".260"},
    {"dv": "upb", "predictor": "oi", "beta_composite": 0.1475, "p_composite": "<.001"},
    {"dv": "upb", "predictor": "el", "beta_composite": 0.0175, "p_composite": ".532"},
    {"dv": "ocb", "predictor": "equity", "beta_composite": -0.0781, "p_composite": ".002"},
    {"dv": "ocb", "predictor": "inclusion", "beta_composite": 0.2666, "p_composite": "<.001"},
    {"dv": "ocb", "predictor": "oi", "beta_composite": 0.2069, "p_composite": "<.001"},
    {"dv": "ocb", "predictor": "el", "beta_composite": 0.0650, "p_composite": ".005"},
    {"dv": "oi", "predictor": "equity", "beta_composite": None, "p_composite": None},
    {"dv": "oi", "predictor": "inclusion", "beta_composite": None, "p_composite": None},
])

merged = struct.merge(composite_model4, on=["dv", "predictor"], how="left")
merged["sign_flip"] = np.sign(merged["beta_std"]) != np.sign(merged["beta_composite"].fillna(merged["beta_std"]))

print("\n[잠재변수 vs 복합점수(05/11번 Model4) 대조]")
print(merged.to_string(index=False))

sign_flips = merged[merged["beta_composite"].notna() & merged["sign_flip"]]
if len(sign_flips) > 0:
    print("\n*** 경고: 부호가 뒤집힌 경로 발견 ***")
    print(sign_flips.to_string(index=False))
else:
    print("\n부호가 뒤집힌 경로 없음.")

# --------------------------------------------------
# 결과 저장
# --------------------------------------------------

out_dir = "../results/sem"
os.makedirs(out_dir, exist_ok=True)

struct.to_csv(os.path.join(out_dir, "sem02_structural_paths.csv"), index=False, encoding="utf-8-sig")
merged.to_csv(os.path.join(out_dir, "sem02_vs_composite_comparison.csv"), index=False, encoding="utf-8-sig")

fit_row = pd.DataFrame([{
    "chi2": round(stats["chi2"], 2), "df": int(stats["DoF"]),
    "CFI": round(stats["CFI"], 4), "TLI": round(stats["TLI"], 4),
    "RMSEA": round(stats["RMSEA"], 4), "SRMR": round(srmr, 4),
}])
fit_row.to_csv(os.path.join(out_dir, "sem02_fit_indices.csv"), index=False, encoding="utf-8-sig")

md_content = f"""# SEM 주분석 3단계: 잠재변수 구조모형 (H1~H4)

## 모형 적합도

{fit_row.to_markdown(index=False)}

## 구조 경로계수 (잠재변수)

{struct.to_markdown(index=False)}

## 복합점수(05/11번 Model 4)와의 대조

{merged.to_markdown(index=False)}

*Note.* beta_std = 잠재변수 SEM 표준화 경로계수; beta_composite = 05/11번
복합점수(composite score) OLS(HC3) 표준화 계수(Model 4, 성별·연령·조직유형
통제 포함). sign_flip = 부호가 뒤집힌 경우 True.
"""

with open(os.path.join(out_dir, "sem02_structural_model_result.md"), "w", encoding="utf-8") as f:
    f.write(md_content)

print("\nSEM 3단계 결과 저장 완료")
print("저장 경로:", out_dir)
