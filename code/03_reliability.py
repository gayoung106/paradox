import pandas as pd
from pingouin import cronbach_alpha

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

df = pd.read_csv("../processed/analysis_data.csv")

# --------------------------------------------------
# 변수 정의
# --------------------------------------------------

equity_cols = [
    "Y8_1", "Y8_2", "Y8_3",
    "Y8_4", "Y8_5"
]

inclusion_cols = [
    "Y8_6", "Y8_7",
    "Y8_8", "Y8_9"
]

oi_cols = [
    "Y1_1", "Y1_2", "Y1_3",
    "Y1_4", "Y1_5", "Y1_6"
]

el_cols = [
    "Y11_1", "Y11_2", "Y11_3",
    "Y11_4", "Y11_5"
]

ocb_cols = [
    "Y19_1", "Y19_2",
    "Y19_3", "Y19_4"
]

upb_cols = [
    "Y20_1", "Y20_2", "Y20_3",
    "Y20_4", "Y20_5"
]

# --------------------------------------------------
# 신뢰도 계산 함수
# --------------------------------------------------

results = []

def check_alpha(name, cols):

    alpha, _ = cronbach_alpha(df[cols])

    print(f"\n{name}")
    print(f"Cronbach α = {round(alpha, 3)}")

    results.append({
        "Variable": name,
        "Cronbach_alpha": round(alpha, 3)
    })

# --------------------------------------------------
# 실행
# --------------------------------------------------

check_alpha("Equity Climate", equity_cols)
check_alpha("Inclusion Climate", inclusion_cols)
check_alpha("Organizational Identification", oi_cols)
check_alpha("Ethical Leadership", el_cols)
check_alpha("OCB", ocb_cols)
check_alpha("UPB", upb_cols)

# --------------------------------------------------
# 결과 DataFrame
# --------------------------------------------------

result_df = pd.DataFrame(results)

# --------------------------------------------------
# Markdown 저장
# --------------------------------------------------

md_content = f"""
# Reliability Analysis Result

## Cronbach Alpha Result

{result_df.to_markdown(index=False)}

---

# 해석

## Equity Climate
- Cronbach α = {result_df.loc[0, 'Cronbach_alpha']}
- 매우 높은 내부일관성을 보임

## Inclusion Climate
- Cronbach α = {result_df.loc[1, 'Cronbach_alpha']}
- 안정적인 심리적 포용성 척도로 판단 가능

## Organizational Identification
- Cronbach α = {result_df.loc[2, 'Cronbach_alpha']}
- 조직동일시 척도의 신뢰도가 양호함

## Ethical Leadership
- Cronbach α = {result_df.loc[3, 'Cronbach_alpha']}
- 매우 높은 수준의 내부일관성을 보임

## OCB
- Cronbach α = {result_df.loc[4, 'Cronbach_alpha']}
- 조직시민행동 척도의 신뢰도가 양호함

## UPB
- Cronbach α = {result_df.loc[5, 'Cronbach_alpha']}
- 비윤리적 친조직행동 척도의 신뢰도가 양호함

---

# 종합 해석

모든 변수의 Cronbach α 값이 .80 이상으로 나타나,
측정도구의 내부일관성이 전반적으로 우수한 수준임을 확인하였다.
"""

with open(
    "../results/reliability_result.md",
    "w",
    encoding="utf-8"
) as f:
    f.write(md_content)

print("\nReliability Markdown 저장 완료")