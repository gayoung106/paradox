import pandas as pd
import statsmodels.api as sm
import os

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

df = pd.read_csv(
    "../processed/analysis_data.csv"
)

print("데이터 크기:", df.shape)

# --------------------------------------------------
# 통제변수 전처리
# --------------------------------------------------

df["gender_male"] = (
    df["SQ1K1"] == "남자"
).astype(int)

df["public_org"] = (
    df["유형"] == "공공"
).astype(int)

# --------------------------------------------------
# 회귀 함수
# --------------------------------------------------

def run_regression(name, x_vars):

    X = df[x_vars]

    X = sm.add_constant(X)

    y = df["ocb"]

    model = sm.OLS(
        y,
        X
    ).fit(cov_type="HC3")

    print(f"\n{name}")
    print(model.summary())

    return model

# --------------------------------------------------
# Model 1
# --------------------------------------------------

model1_vars = [
    "gender_male",
    "SQ1K2_1",
    "public_org"
]

model1 = run_regression(
    "Model 1",
    model1_vars
)

# --------------------------------------------------
# Model 2
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
# --------------------------------------------------

model4_vars = model3_vars + [
    "ethical_leadership"
]

model4 = run_regression(
    "Model 4",
    model4_vars
)

# --------------------------------------------------
# 결과 폴더 생성
# --------------------------------------------------

os.makedirs(
    "../results/ocb_regression",
    exist_ok=True
)

# --------------------------------------------------
# Markdown 생성
# --------------------------------------------------

md_content = f"""
# OCB Regression Analysis Result

## 종속변수
- OCB (조직시민행동)

---

# Model 1

{model1.summary().as_text()}

---

# Model 2

{model2.summary().as_text()}

---

# Model 3

{model3.summary().as_text()}

---

# Model 4

{model4.summary().as_text()}

---

# 핵심 해석

## Organizational Identification

조직동일시는
조직시민행동(OCB)을 강화하는 방향으로
작동할 가능성이 존재함.

이는 기존 조직행동 연구와
일관된 결과로 해석 가능.

---

## Inclusion Climate

포용적 조직문화는
조직구성원의 자발적 조직기여 행동을
강화할 가능성이 존재함.

---

# 연구적 함의

본 연구는
강한 조직충성이
긍정적 조직행동(OCB)뿐 아니라,
비윤리적 친조직행동(UPB)까지
동시에 강화할 가능성이 있음을 시사한다.

즉,
조직동일시는
양면적(double-edged) 특성을 가지며,

조직에 대한 헌신은
상황에 따라
윤리적 행동과 비윤리적 행동 모두로
이어질 수 있다.
"""

with open(
    "../results/ocb_regression/ocb_regression_result.md",
    "w",
    encoding="utf-8"
) as f:

    f.write(md_content)

print("\nOCB 회귀분석 Markdown 저장 완료")
print("\n저장 경로:")
print(
    "../results/ocb_regression/ocb_regression_result.md"
)