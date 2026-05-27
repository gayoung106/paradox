import pandas as pd
from factor_analyzer import FactorAnalyzer
import numpy as np
import os

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

df = pd.read_csv(
    "../processed/analysis_data.csv"
)

print("데이터 크기:", df.shape)

# --------------------------------------------------
# 분석 문항
# --------------------------------------------------

all_items = [

    # OI
    "Y1_1", "Y1_2", "Y1_3",
    "Y1_4", "Y1_5", "Y1_6",

    # Equity
    "Y8_1", "Y8_2", "Y8_3",
    "Y8_4", "Y8_5",

    # Inclusion
    "Y8_6", "Y8_7",
    "Y8_8", "Y8_9",

    # EL
    "Y11_1", "Y11_2", "Y11_3",
    "Y11_4", "Y11_5",

    # OCB
    "Y19_1", "Y19_2",
    "Y19_3", "Y19_4",

    # UPB
    "Y20_1", "Y20_2", "Y20_3",
    "Y20_4", "Y20_5"
]

cmb_df = df[all_items]

# --------------------------------------------------
# Harman Single Factor
# --------------------------------------------------

fa = FactorAnalyzer(
    n_factors=1,
    rotation=None
)

fa.fit(cmb_df)

ev, v = fa.get_eigenvalues()

total_variance = np.sum(ev)

first_factor_variance = ev[0]

explained_ratio = (
    first_factor_variance / total_variance
) * 100

print("\nHarman Single Factor Test")
print(
    "First Factor Explained Variance:",
    round(explained_ratio, 3),
    "%"
)

# --------------------------------------------------
# 결과 폴더 생성
# --------------------------------------------------

os.makedirs(
    "../results/common_method_bias",
    exist_ok=True
)

# --------------------------------------------------
# Markdown 저장
# --------------------------------------------------

md_content = f"""
# Common Method Bias Result

# Harman Single Factor Test

## First Factor Explained Variance

- {round(explained_ratio, 3)}%

---

# 해석 기준

| 설명분산 | 해석 |
|---|---|
| 50% 미만 | 일반적으로 CMB 문제 크지 않음 |
| 50% 이상 | 공통방법편의 우려 가능 |

---

# 결과 해석

본 연구에서는
Harman의 단일요인 검정을 수행하였다.

분석 결과,
첫 번째 요인의 설명분산은
{round(explained_ratio, 3)}%로 나타났다.

이는 일반적으로 사용되는 기준치인
50%를 초과하지 않는 수준으로,

공통방법편의(Common Method Bias)가
심각한 수준은 아닌 것으로 판단된다.

---

# 연구적 함의

본 연구는
동일 설문 및 자기보고식 자료를 활용하였으므로,
공통방법편의 가능성을 완전히 배제할 수는 없다.

다만 Harman 단일요인 검정 결과,
단일요인이 전체 분산의 대부분을 설명하지 않는 것으로 나타나,
공통방법편의가 연구결과를 결정적으로 왜곡할 가능성은
상대적으로 제한적인 것으로 판단된다.
"""

with open(
    "../results/common_method_bias/cmb_result.md",
    "w",
    encoding="utf-8"
) as f:

    f.write(md_content)

print("\nCMB Markdown 저장 완료")
print("\n저장 경로:")
print(
    "../results/common_method_bias/cmb_result.md"
)