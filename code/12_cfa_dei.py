import pandas as pd
from semopy import Model
from semopy import calc_stats
import os

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

df = pd.read_csv(
    "../processed/analysis_data.csv"
)

print("데이터 크기:", df.shape)

# --------------------------------------------------
# 2요인 CFA 모델
# --------------------------------------------------

model_desc_2factor = """
equity =~ Y8_1 + Y8_2 + Y8_3 + Y8_4 + Y8_5
inclusion =~ Y8_6 + Y8_7 + Y8_8 + Y8_9
"""

# --------------------------------------------------
# 1요인 CFA 모델
# --------------------------------------------------

model_desc_1factor = """
dei =~ Y8_1 + Y8_2 + Y8_3 + Y8_4 + Y8_5 + Y8_6 + Y8_7 + Y8_8 + Y8_9
"""

# --------------------------------------------------
# 2요인 모델 적합
# --------------------------------------------------

model2 = Model(model_desc_2factor)

model2.fit(df)

stats2 = calc_stats(model2)

print("\n2-Factor CFA")
print(stats2)

# --------------------------------------------------
# 2요인 표준화 적재량
# --------------------------------------------------

estimates2 = model2.inspect(std_est=True)

print("\n2-Factor Standardized Loadings")
print(estimates2)

# --------------------------------------------------
# 1요인 모델 적합
# --------------------------------------------------

model1 = Model(model_desc_1factor)

model1.fit(df)

stats1 = calc_stats(model1)

print("\n1-Factor CFA")
print(stats1)

# --------------------------------------------------
# 1요인 표준화 적재량
# --------------------------------------------------

estimates1 = model1.inspect(std_est=True)

print("\n1-Factor Standardized Loadings")
print(estimates1)

# --------------------------------------------------
# 결과 폴더 생성
# --------------------------------------------------

os.makedirs(
    "../results/cfa",
    exist_ok=True
)

os.makedirs(
    "../processed",
    exist_ok=True
)

# --------------------------------------------------
# 적재량 CSV 저장
# --------------------------------------------------

estimates2.to_csv(
    "../processed/cfa_2factor_loadings.csv",
    index=False,
    encoding="utf-8-sig"
)

estimates1.to_csv(
    "../processed/cfa_1factor_loadings.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n표준화 적재량 CSV 저장 완료")

# --------------------------------------------------
# Markdown 저장
# --------------------------------------------------

md_content = f"""
# CFA Result

# 2-Factor Model

## Model Specification

- Equity Climate
- Inclusion Climate

---

# Fit Indices

{stats2.to_markdown()}

---

# Standardized Loadings

{estimates2.to_markdown(index=False)}

---

# 1-Factor Model

## Model Specification

- Single DEI Factor

---

# Fit Indices

{stats1.to_markdown()}

---

# Standardized Loadings

{estimates1.to_markdown(index=False)}

---

# 핵심 해석

## 2-Factor Model

형평성(Equity)과
포용성(Inclusion)을
서로 구분된 구성개념으로 설정한 모델.

---

## 1-Factor Model

DEI를 단일 차원으로 간주한 모델.

---

# 모델 비교 해석

만약 2-factor 모델의 적합도가
1-factor 모델보다 우수하게 나타날 경우,

형평성과 포용성은
동일 개념이 아니라,
서로 구분되는 조직문화 차원으로
해석 가능함.

---

# 주요 적합도 기준

| 지표 | 권장 기준 |
|---|---|
| CFI | .90 이상 |
| TLI | .90 이상 |
| RMSEA | .08 이하 |
| SRMR | .08 이하 |

---

# 연구적 함의

본 연구는
조직 내 포용성과 형평성이
동일한 개념으로 작동하지 않을 가능성에 주목한다.

특히 형평성은
제도적·절차적 공정성에 가까운 반면,

포용성은
심리적 소속감 및 존중 경험과
보다 밀접하게 연결될 가능성이 존재한다.

이는 DEI를 단일 차원으로 보기보다,
서로 다른 조직경험 차원으로
구분하여 접근할 필요성을 시사한다.
"""

with open(
    "../results/cfa/cfa_result.md",
    "w",
    encoding="utf-8"
) as f:

    f.write(md_content)

print("\nCFA Markdown 저장 완료")
print("\n저장 경로:")
print("../results/cfa/cfa_result.md")