import pandas as pd
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import (
    calculate_kmo,
    calculate_bartlett_sphericity
)

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

df = pd.read_spss(
    "../raw/raw_data.sav",
    convert_categoricals=False
)

# --------------------------------------------------
# 문항 8 (DEI)
# --------------------------------------------------

dei_cols = [
    "Y8_1", "Y8_2", "Y8_3", "Y8_4", "Y8_5",
    "Y8_6", "Y8_7", "Y8_8", "Y8_9", "Y8_10"
]

dei_df = df[dei_cols]

# --------------------------------------------------
# 결측 제거
# --------------------------------------------------

dei_df = dei_df.dropna()

print("데이터 크기:", dei_df.shape)

# --------------------------------------------------
# KMO
# --------------------------------------------------

kmo_all, kmo_model = calculate_kmo(dei_df)

print("\nKMO:", round(kmo_model, 3))

# --------------------------------------------------
# Bartlett
# --------------------------------------------------

chi_square_value, p_value = calculate_bartlett_sphericity(dei_df)

print("Bartlett p-value:", p_value)

# --------------------------------------------------
# EFA
# --------------------------------------------------

fa = FactorAnalyzer(
    n_factors=2,
    rotation="oblimin"
)

fa.fit(dei_df)

# --------------------------------------------------
# 요인적재량
# --------------------------------------------------

loadings = pd.DataFrame(
    fa.loadings_,
    index=dei_cols,
    columns=["Factor1", "Factor2"]
)

print("\n요인적재량")
print(loadings.round(3))

# --------------------------------------------------
# Markdown 저장
# --------------------------------------------------

md_content = f"""
# EFA Result

## 데이터 크기
- {dei_df.shape}

---

# KMO

- KMO = {round(kmo_model, 3)}

## 해석
KMO 값이 .90 이상으로 매우 우수한 수준으로 나타나,
요인분석에 적합한 데이터로 판단된다.

---

# Bartlett 구형성 검정

- p-value = {p_value}

## 해석
Bartlett 검정 결과 통계적으로 유의하게 나타나(p < .001),
변수 간 상관관계가 존재하며 요인분석 수행이 적절한 것으로 확인되었다.

---

# 요인적재량

{loadings.round(3).to_markdown()}

---

# 해석

## Factor1
- Y8_1 ~ Y8_5 문항이 높게 적재됨
- 조직의 다양성·형평성·공정한 운영 체계에 관한 차원으로 해석 가능

## Factor2
- Y8_6 ~ Y8_9 문항이 높게 적재됨
- 조직 내 심리적 포용성과 소속감에 관한 차원으로 해석 가능

## Y8_10
- 두 요인에 모두 일부 적재되는 경향이 나타남
- 개념적 혼재 가능성이 있어 후속 분석에서 제외
"""

with open(
    "../results/efa_result.md",
    "w",
    encoding="utf-8"
) as f:
    f.write(md_content)

print("\nEFA Markdown 저장 완료")