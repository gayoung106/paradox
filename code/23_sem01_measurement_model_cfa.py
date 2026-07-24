import pandas as pd
import numpy as np
from semopy import Model, calc_stats
import os

# --------------------------------------------------
# SEM 주분석 1단계: 6요인 통합 측정모형 CFA
# --------------------------------------------------
# 13_validity.py와 동일한 측정모형(FACTOR_ITEMS)을 사용하지만, 13번은
# AVE/CR/HTMT 산출에 집중하고 전체 모형 적합도(chi2/CFI/TLI/RMSEA/SRMR)를
# 별도로 보고하지 않으므로, 이 스크립트에서 공식 SEM 주분석 1단계 산출물로
# 적합도와 표준화 적재량을 함께 저장한다.

df = pd.read_csv("../processed/analysis_data.csv")

print("데이터 크기:", df.shape)

FACTOR_ITEMS = {
    "equity": ["Y8_1", "Y8_2", "Y8_3", "Y8_4", "Y8_5"],
    "inclusion": ["Y8_6", "Y8_7", "Y8_8", "Y8_9"],
    "oi": ["Y1_1", "Y1_2", "Y1_3", "Y1_4", "Y1_5", "Y1_6"],
    "el": ["Y11_1", "Y11_2", "Y11_3", "Y11_4", "Y11_5"],
    "ocb": ["Y19_1", "Y19_2", "Y19_3", "Y19_4"],
    "upb": ["Y20_1", "Y20_2", "Y20_3", "Y20_4", "Y20_5"],
}
ALL_ITEMS = [it for items in FACTOR_ITEMS.values() for it in items]

model_desc = "\n".join(
    f"{factor} =~ {' + '.join(items)}" for factor, items in FACTOR_ITEMS.items()
)

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


srmr = calc_srmr(model, ALL_ITEMS, df)

print("\n[6요인 통합 측정모형 CFA 적합도]")
print(f"chi2({int(stats['DoF'])}) = {stats['chi2']:.2f}")
print(f"CFI = {stats['CFI']:.4f}")
print(f"TLI = {stats['TLI']:.4f}")
print(f"RMSEA = {stats['RMSEA']:.4f}")
print(f"SRMR = {srmr:.4f}")

estimates = model.inspect(std_est=True)
loadings = estimates[estimates["op"] == "~"][["lval", "rval", "Estimate", "Est. Std"]].copy()
loadings.columns = ["item", "factor", "unstd", "std"]
loadings["unstd"] = loadings["unstd"].astype(float).round(4)
loadings["std"] = loadings["std"].astype(float).round(4)

print("\n[표준화 적재량]")
print(loadings.to_string(index=False))

# --------------------------------------------------
# 12번(2요인 DEI CFA)과의 대조
# --------------------------------------------------
# 12_cfa_dei.py는 형평/포용 2요인만으로 별도 CFA를 적합한다
# (results/cfa/cfa_result.md: DoF=26, chi2=438.40, CFI=.9618, TLI=.9471,
# RMSEA=.0886). 6요인 통합모형에 embedding되면 다른 4개 요인과의
# 공유분산/제약이 추가되어 적합도가 달라지는 것이 일반적이며, 이는
# 오류가 아니라 임베딩에 따른 정상적인 차이다.

comparison = pd.DataFrame([
    {"모형": "12번: 형평-포용 2요인 단독 CFA", "chi2": 438.40, "df": 26,
     "CFI": 0.9618, "TLI": 0.9471, "RMSEA": 0.0886, "SRMR": "(미산출)"},
    {"모형": "본 스크립트: 6요인 통합 CFA", "chi2": round(stats["chi2"], 2),
     "df": int(stats["DoF"]), "CFI": round(stats["CFI"], 4),
     "TLI": round(stats["TLI"], 4), "RMSEA": round(stats["RMSEA"], 4),
     "SRMR": round(srmr, 4)},
])

print("\n[12번 2요인 단독 CFA와의 대조]")
print(comparison.to_string(index=False))

# --------------------------------------------------
# 결과 저장
# --------------------------------------------------

out_dir = "../results/sem"
os.makedirs(out_dir, exist_ok=True)

loadings.to_csv(os.path.join(out_dir, "sem01_measurement_model_loadings.csv"),
                 index=False, encoding="utf-8-sig")
comparison.to_csv(os.path.join(out_dir, "sem01_vs_12_comparison.csv"),
                   index=False, encoding="utf-8-sig")

fit_row = pd.DataFrame([{
    "chi2": round(stats["chi2"], 2), "df": int(stats["DoF"]),
    "CFI": round(stats["CFI"], 4), "TLI": round(stats["TLI"], 4),
    "RMSEA": round(stats["RMSEA"], 4), "SRMR": round(srmr, 4),
}])
fit_row.to_csv(os.path.join(out_dir, "sem01_fit_indices.csv"), index=False, encoding="utf-8-sig")

md_content = f"""# SEM 주분석 1단계: 6요인 통합 측정모형 CFA

## 모형 적합도

{fit_row.to_markdown(index=False)}

## 12번(형평-포용 2요인 단독 CFA)과의 대조

{comparison.to_markdown(index=False)}

*Note.* 6요인 통합모형은 12번의 2요인 단독모형과 표본·항목이 다르지 않으나,
나머지 4개 요인(OI, EL, OCB, UPB)과의 공분산 구조가 추가되어 형평·포용 요인의
적합도 기여분이 달라진다. 이는 방법론적 정상 범위이며, 두 모형의 형평/포용
표준화 적재량이 유사한 범위에 있는지로 일관성을 점검한다.

## 표준화 적재량 (전체 29항목)

{loadings.to_markdown(index=False)}
"""

with open(os.path.join(out_dir, "sem01_measurement_model_result.md"), "w", encoding="utf-8") as f:
    f.write(md_content)

print("\nSEM 1단계 결과 저장 완료")
print("저장 경로:", out_dir)
