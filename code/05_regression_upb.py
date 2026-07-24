import pandas as pd
import statsmodels.api as sm
import os

from statsmodels.stats.outliers_influence import (
    variance_inflation_factor
)

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

df = pd.read_csv("../processed/analysis_data.csv")

print("데이터 크기:", df.shape)

# --------------------------------------------------
# 통제변수 전처리
# --------------------------------------------------

# 성별 더미화
# SQ1K1 값 코드: 1.0=남자, 2.0=여자 (raw_data.sav 값 라벨 기준)
df["gender_male"] = (
    df["SQ1K1"] == 1.0
).astype(int)

# 연령 (출생연도 -> 연령 환산; 조사 기준연도 2023년)
df["age"] = 2023 - df["SQ1K2_1"]

# 공공 여부 더미화
df["public_org"] = (
    df["유형"] == "공공"
).astype(int)

# --------------------------------------------------
# 회귀 함수
# --------------------------------------------------

def run_regression(name, x_vars):

    X = df[x_vars]

    X = sm.add_constant(X)

    y = df["upb"]

    model = sm.OLS(
        y,
        X
    ).fit(cov_type="HC3")

    print(f"\n{name}")
    print(model.summary())

    return model

# --------------------------------------------------
# Model 1
# 통제변수만
# --------------------------------------------------

model1_vars = [
    "gender_male",
    "age",
    "public_org"
]

model1 = run_regression(
    "Model 1",
    model1_vars
)

# --------------------------------------------------
# Model 2
# 조직문화 변수 추가
# --------------------------------------------------

model2_vars = model1_vars + [
    "equity_climate",
    "inclusion_climate"
]

model2 = run_regression(
    "Model 2",
    model2_vars
)

# --------------------------------------------------
# Model 3
# 조직동일시 추가
# --------------------------------------------------

model3_vars = model2_vars + [
    "org_identification"
]

model3 = run_regression(
    "Model 3",
    model3_vars
)

# --------------------------------------------------
# Model 4
# 윤리적 리더십 추가
# --------------------------------------------------

model4_vars = model3_vars + [
    "ethical_leadership"
]

model4 = run_regression(
    "Model 4",
    model4_vars
)

# --------------------------------------------------
# VIF 확인
# --------------------------------------------------

vif_X = df[model4_vars]

vif_X = sm.add_constant(vif_X)

vif_df = pd.DataFrame()

vif_df["Variable"] = vif_X.columns

vif_df["VIF"] = [
    variance_inflation_factor(
        vif_X.values,
        i
    )
    for i in range(vif_X.shape[1])
]

print("\nVIF 결과")
print(vif_df.round(3))

# --------------------------------------------------
# 결과 폴더 생성
# --------------------------------------------------

os.makedirs(
    "../results/regression",
    exist_ok=True
)

# --------------------------------------------------
# Markdown 생성
# --------------------------------------------------

print("\nMarkdown 생성 시작")

md_content = f"""
# Regression Analysis Result

## 종속변수
- UPB (비윤리적 친조직행동)

---

# Model 1
통제변수만 포함

{model1.summary().as_text()}

---

# Model 2
조직문화 변수 추가

{model2.summary().as_text()}

---

# Model 3
조직동일시 추가

{model3.summary().as_text()}

---

# Model 4
윤리적 리더십 추가

{model4.summary().as_text()}

---

# VIF 결과

{vif_df.round(3).to_markdown(index=False)}

---

# 핵심 해석 포인트

## Inclusion Climate
포용적 조직문화가
UPB와 정적 관계를 가지는지 확인 필요

## Organizational Identification
조직동일시가 추가되었을 때
Inclusion 효과가 감소하면
매개효과 가능성을 시사

## Ethical Leadership
윤리적 리더십이
UPB를 억제하는 방향인지 확인 필요

---

# 다중공선성 해석

- VIF 5 미만: 일반적으로 양호
- VIF 10 이상: 다중공선성 문제 가능성

조직문화 및 리더십 변수들은
개념적으로 상관성이 존재할 가능성이 있으므로
일정 수준의 상관은 예상 가능한 결과임.
"""

print("\n파일 저장 직전")

# --------------------------------------------------
# Markdown 저장
# --------------------------------------------------

with open(
    "../results/regression/regression_upb.md",
    "w",
    encoding="utf-8"
) as f:

    f.write(md_content)

print("\n회귀분석 Markdown 저장 완료")
print("\n저장 경로:")
print("../results/regression/regression_upb.md")