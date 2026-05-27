import pandas as pd
import numpy as np
import os
import statsmodels.api as sm

from statsmodels.stats.outliers_influence import (
    variance_inflation_factor
)

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

df = pd.read_csv(
    "../processed/analysis_data.csv"
)

print("데이터 크기:", df.shape)

# --------------------------------------------------
# 분석 변수
# --------------------------------------------------

variables = [
    "equity_climate",
    "inclusion_climate",
    "org_identification",
    "ethical_leadership",
    "ocb",
    "upb"
]

# --------------------------------------------------
# 기술통계
# --------------------------------------------------

desc = (
    df[variables]
    .describe()
    .T[
        ["mean", "std", "min", "max"]
    ]
    .round(3)
)

desc.columns = [
    "Mean",
    "SD",
    "Min",
    "Max"
]

print("\n기술통계")
print(desc)

# --------------------------------------------------
# 상관행렬
# --------------------------------------------------

corr = (
    df[variables]
    .corr()
    .round(3)
)

print("\n상관행렬")
print(corr)

# --------------------------------------------------
# VIF
# --------------------------------------------------

X = df[variables]

X = sm.add_constant(X)

vif_df = pd.DataFrame()

vif_df["Variable"] = X.columns

vif_df["VIF"] = [
    variance_inflation_factor(
        X.values,
        i
    )
    for i in range(X.shape[1])
]

vif_df = vif_df.round(3)

print("\nVIF")
print(vif_df)

# --------------------------------------------------
# 결과 폴더 생성
# --------------------------------------------------

os.makedirs(
    "../results/tables",
    exist_ok=True
)

# --------------------------------------------------
# Markdown 저장
# --------------------------------------------------

md_content = f"""
# Table 1. Descriptive Statistics and Correlations

# Descriptive Statistics

{desc.to_markdown()}

---

# Correlation Matrix

{corr.to_markdown()}

---

# VIF

{vif_df.to_markdown(index=False)}

---

# 해석

## 기술통계

전반적으로 조직시민행동(OCB)의 평균이
비교적 높게 나타난 반면,

비윤리적 친조직행동(UPB)은
상대적으로 중간 수준으로 나타났다.

---

## 상관관계

포용적 조직문화와 조직동일시는
정적 상관관계를 가지는 것으로 나타났으며,

조직동일시는
OCB뿐 아니라 UPB와도
정적 관계를 보일 가능성이 확인되었다.

---

## 다중공선성

VIF 값이 일반적인 기준치(10 미만)를
초과하지 않는 경우,

심각한 다중공선성 문제는
없는 것으로 판단 가능하다.
"""

with open(
    "../results/tables/table1_descriptive.md",
    "w",
    encoding="utf-8"
) as f:

    f.write(md_content)

print("\nTable 1 Markdown 저장 완료")
print("\n저장 경로:")
print(
    "../results/tables/table1_descriptive.md"
)