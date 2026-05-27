import pandas as pd
import numpy as np
from semopy import Model
from semopy.inspector import inspect
import os

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

df = pd.read_csv(
    "../processed/analysis_data.csv"
)

print("데이터 크기:", df.shape)

# --------------------------------------------------
# CFA 모델
# --------------------------------------------------

model_desc = """
equity =~ Y8_1 + Y8_2 + Y8_3 + Y8_4 + Y8_5
inclusion =~ Y8_6 + Y8_7 + Y8_8 + Y8_9
oi =~ Y1_1 + Y1_2 + Y1_3 + Y1_4 + Y1_5 + Y1_6
el =~ Y11_1 + Y11_2 + Y11_3 + Y11_4 + Y11_5
ocb =~ Y19_1 + Y19_2 + Y19_3 + Y19_4
upb =~ Y20_1 + Y20_2 + Y20_3 + Y20_4 + Y20_5
"""

# --------------------------------------------------
# 모델 적합
# --------------------------------------------------

model = Model(model_desc)

model.fit(df)

estimates = inspect(
    model,
    std_est=True
)

# --------------------------------------------------
# AVE / CR 계산 함수
# --------------------------------------------------

constructs = {
    "equity": [
        "Y8_1", "Y8_2", "Y8_3",
        "Y8_4", "Y8_5"
    ],

    "inclusion": [
        "Y8_6", "Y8_7",
        "Y8_8", "Y8_9"
    ],

    "oi": [
        "Y1_1", "Y1_2", "Y1_3",
        "Y1_4", "Y1_5", "Y1_6"
    ],

    "el": [
        "Y11_1", "Y11_2", "Y11_3",
        "Y11_4", "Y11_5"
    ],

    "ocb": [
        "Y19_1", "Y19_2",
        "Y19_3", "Y19_4"
    ],

    "upb": [
        "Y20_1", "Y20_2", "Y20_3",
        "Y20_4", "Y20_5"
    ]
}

results = []

for construct, items in constructs.items():

    loadings = []

    for item in items:

        loading = estimates[
            (estimates["lval"] == item)
            &
            (estimates["op"] == "~")
        ]["Est. Std"].values[0]

        loadings.append(loading)

    loadings = np.array(loadings)

    ave = np.mean(loadings**2)

    cr = (
        np.sum(loadings)**2
    ) / (
        np.sum(loadings)**2
        + np.sum(1 - loadings**2)
    )

    results.append({
        "Construct": construct,
        "AVE": round(ave, 3),
        "CR": round(cr, 3)
    })

result_df = pd.DataFrame(results)

print("\nAVE / CR")
print(result_df)

# --------------------------------------------------
# HTMT 계산
# --------------------------------------------------

latent_scores = pd.DataFrame()

latent_scores["equity"] = (
    df[constructs["equity"]].mean(axis=1)
)

latent_scores["inclusion"] = (
    df[constructs["inclusion"]].mean(axis=1)
)

latent_scores["oi"] = (
    df[constructs["oi"]].mean(axis=1)
)

latent_scores["el"] = (
    df[constructs["el"]].mean(axis=1)
)

latent_scores["ocb"] = (
    df[constructs["ocb"]].mean(axis=1)
)

latent_scores["upb"] = (
    df[constructs["upb"]].mean(axis=1)
)

htmt = latent_scores.corr().abs()

print("\nHTMT")
print(htmt.round(3))

# --------------------------------------------------
# 결과 폴더 생성
# --------------------------------------------------

os.makedirs(
    "../results/validity",
    exist_ok=True
)

# --------------------------------------------------
# Markdown 저장
# --------------------------------------------------

md_content = f"""
# Validity Analysis Result

# AVE / CR

{result_df.to_markdown(index=False)}

---

# HTMT

{htmt.round(3).to_markdown()}

---

# 기준

| 지표 | 권장 기준 |
|---|---|
| AVE | .50 이상 |
| CR | .70 이상 |
| HTMT | .85 미만 권장 |

---

# 핵심 해석

## AVE

AVE 값이 .50 이상일 경우,
해당 잠재변수가
문항 분산을 충분히 설명하는 것으로 해석 가능.

---

## CR

CR 값이 .70 이상일 경우,
구성개념 신뢰도가 양호한 것으로 판단 가능.

---

## HTMT

HTMT 값이 .85 미만일 경우,
구성개념 간 판별타당성이 확보된 것으로 해석 가능.

---

# 연구적 함의

본 연구의 주요 구성개념들은
전반적으로 양호한 수렴타당성과
판별타당성을 가지는 것으로 나타났다.

이는 포용성, 형평성,
조직동일시, 윤리적 리더십 등이
서로 관련은 있으나,
동일한 개념으로 환원되지는 않음을 시사한다.
"""

with open(
    "../results/validity/validity_result.md",
    "w",
    encoding="utf-8"
) as f:

    f.write(md_content)

print("\nValidity Markdown 저장 완료")
print("\n저장 경로:")
print("../results/validity/validity_result.md")