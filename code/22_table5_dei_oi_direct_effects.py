import pandas as pd
import statsmodels.api as sm
import os

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

df = pd.read_csv("../processed/analysis_data.csv")

print("데이터 크기:", df.shape)

# --------------------------------------------------
# 통제변수 (05/11번과 동일한 사양)
# --------------------------------------------------

# SQ1K1 값 코드: 1.0=남자, 2.0=여자 (raw_data.sav 값 라벨 기준)
df["gender_male"] = (
    df["SQ1K1"] == 1.0
).astype(int)

# 연령 (출생연도 -> 연령 환산; 조사 기준연도 2023년)
df["age"] = 2023 - df["SQ1K2_1"]

df["public_org"] = (
    df["유형"] == "공공"
).astype(int)

CONTROLS = ["gender_male", "age", "public_org"]
DEI_OI = ["equity_climate", "inclusion_climate", "org_identification"]
X_VARS = CONTROLS + DEI_OI

# --------------------------------------------------
# 표5 정본 모형: 형평·포용·조직동일시 동시투입
# (윤리적 리더십 제외 - 리더십 직접효과는 표4 Model4에 별도 보고)
# --------------------------------------------------


def run_regression(y_var):
    X = sm.add_constant(df[X_VARS])
    y = df[y_var]
    model = sm.OLS(y, X).fit(cov_type="HC3")
    return model


model_upb = run_regression("upb")
model_ocb = run_regression("ocb")

print("\n=== UPB ===")
print(model_upb.summary())
print("\n=== OCB ===")
print(model_ocb.summary())

# --------------------------------------------------
# APA7 표 구성
# --------------------------------------------------

VAR_LABELS = {
    "const": "(상수)",
    "gender_male": "성별(남성=1)",
    "age": "연령",
    "public_org": "조직유형(공공=1)",
    "equity_climate": "형평성 분위기",
    "inclusion_climate": "포용성 분위기",
    "org_identification": "조직동일시",
}


def sig_stars(p):
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    if p < 0.10:
        return "†"
    return ""


def fmt_col(model):
    rows = []
    for var in ["const"] + X_VARS:
        b = model.params[var]
        se = model.bse[var]
        p = model.pvalues[var]
        rows.append(f"{b:.3f}{sig_stars(p)} ({se:.3f})")
    rows.append(f"{model.rsquared:.3f}")
    rows.append(f"{model.nobs:.0f}")
    return rows


row_labels = [VAR_LABELS[v] for v in ["const"] + X_VARS] + ["R²", "N"]
col_upb = fmt_col(model_upb)
col_ocb = fmt_col(model_ocb)

table_df = pd.DataFrame({
    "변수": row_labels,
    "UPB": col_upb,
    "OCB": col_ocb,
})

print("\n=== 표5 정본 (APA7) ===")
print(table_df.to_markdown(index=False))

# --------------------------------------------------
# 결과 저장
# --------------------------------------------------

out_dir = "../results/tables"
os.makedirs(out_dir, exist_ok=True)

md_content = f"""# Table 5 (정본): DEI 분위기·조직동일시가 UPB/OCB에 미치는 직접효과

## 모형 사양

- 확질: 형평성 분위기 + 포용성 분위기 + 조직동일시(OI) 동시투입 단일 모형 (윤리적 리더십 EL 제외 - EL 직접효과는 표4 Model4에 보고됨)
- 통제변수: 성별(gender_male, 1.0=남자 기준 수정), 연령(age=2023-출생연도), 조직유형(public_org)
- 추정: OLS, HC3 강건 표준오차
- N = {int(model_upb.nobs)}

## 표5. 형평성·포용성 분위기 및 조직동일시가 UPB/OCB에 미치는 직접효과 (정본)

{table_df.to_markdown(index=False)}

*Note.* 경상자는 비표준화계수(HC3 강건표준오차), †p<.10, *p<.05, **p<.01, ***p<.001.
UPB = 비윤리적 친조직행동; OCB = 조직시민행동; OI = 조직동일시.
이 모형은 윤리적 리더십(EL)을 포함하지 않은 3변수 동시투입 모형이며, EL의 직접효과는 표4(Model 4)에 보고된다.
"""

with open(os.path.join(out_dir, "table5_dei_oi_direct_effects.md"), "w", encoding="utf-8") as f:
    f.write(md_content)

table_df.to_csv(
    os.path.join(out_dir, "table5_dei_oi_direct_effects.csv"),
    index=False,
    encoding="utf-8-sig",
)

print("\n표5 정본 저장 완료")
print("저장 경로:", out_dir)
