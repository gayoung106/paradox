import pandas as pd
import pingouin as pg
import os

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

df = pd.read_csv(
    "../processed/analysis_data.csv"
)

print("데이터 크기:", df.shape)

# --------------------------------------------------
# 결과 폴더 생성
# --------------------------------------------------

os.makedirs(
    "../results/mediation",
    exist_ok=True
)

# --------------------------------------------------
# 매개효과 분석
# Inclusion → OI → UPB
# --------------------------------------------------

med_result = pg.mediation_analysis(
    data=df,
    x="inclusion_climate",
    m="org_identification",
    y="upb",
    alpha=0.05,
    n_boot=5000,
    seed=42
)

print("\n매개효과 분석 결과")
print(med_result)

# --------------------------------------------------
# Equity 추가 분석
# --------------------------------------------------

equity_med_result = pg.mediation_analysis(
    data=df,
    x="equity_climate",
    m="org_identification",
    y="upb",
    alpha=0.05,
    n_boot=5000,
    seed=42
)

print("\nEquity 매개효과 결과")
print(equity_med_result)

# --------------------------------------------------
# Markdown 저장
# --------------------------------------------------

md_content = f"""
# Mediation Analysis Result

# Model 1
Inclusion Climate → Organizational Identification → UPB

{med_result.to_markdown(index=False)}

---

# Model 2
Equity Climate → Organizational Identification → UPB

{equity_med_result.to_markdown(index=False)}

---

# 핵심 해석 포인트

## Inclusion Climate

포용적 조직문화가
조직동일시를 강화하고,
그 결과 비윤리적 친조직행동(UPB)에
영향을 미치는지 확인.

특히 indirect effect가 유의할 경우,
조직동일시의 매개효과 가능성을 시사.

---

## Organizational Identification

조직동일시는 일반적으로
긍정적 조직행동을 강화하는 변수로 알려져 있으나,

본 연구에서는
강한 조직 동일시가
조직을 위한 비윤리 행동까지
정당화할 가능성이 있는지 검토.

---

## 연구적 함의

본 연구는
'좋은 조직문화'가 항상 윤리적 결과만을
가져오는 것은 아닐 수 있다는 점에 주목한다.

즉,
포용적 조직문화와 강한 조직동일시는
조직에 대한 헌신을 강화하지만,
동시에 조직 보호를 위한 비윤리 행동까지
정당화할 가능성이 존재할 수 있다.

이는 조직충성의 양면성(double-edged effect)을
시사한다.
"""

with open(
    "../results/mediation/mediation_result.md",
    "w",
    encoding="utf-8"
) as f:

    f.write(md_content)

print("\n매개효과 Markdown 저장 완료")
print("\n저장 경로:")
print("../results/mediation/mediation_result.md")