import pandas as pd

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

df = pd.read_csv("../processed/analysis_data.csv")

# --------------------------------------------------
# 분석 변수
# --------------------------------------------------

vars_for_corr = [
    "equity_climate",
    "inclusion_climate",
    "org_identification",
    "ethical_leadership",
    "ocb",
    "upb"
]

# --------------------------------------------------
# 상관분석
# --------------------------------------------------

corr = df[vars_for_corr].corr()

print("\n상관분석")
print(corr.round(3))

# --------------------------------------------------
# CSV 저장
# --------------------------------------------------

corr.to_csv(
    "../processed/correlation_matrix.csv",
    encoding="utf-8-sig"
)

print("\n상관행렬 CSV 저장 완료")

# --------------------------------------------------
# Markdown 저장
# --------------------------------------------------

md_content = f"""
# Correlation Analysis Result

## 상관행렬

{corr.round(3).to_markdown()}

---

# 해석

## Equity Climate
- Inclusion Climate, Ethical Leadership, OCB와 정적 상관관계를 가질 가능성이 있음

## Inclusion Climate
- Organizational Identification와 높은 정적 관계가 예상됨
- 조직에 대한 심리적 소속감과 연결될 가능성이 있음

## Organizational Identification
- OCB와 정적 관계 예상
- 동시에 UPB와도 정적 관계가 나타날 가능성이 있음

## Ethical Leadership
- OCB와 정적 관계
- UPB와는 부적 관계 가능성 존재

## OCB와 UPB
- 둘 다 친조직 행동이라는 점에서 일부 정적 상관 가능성 존재
- 다만 윤리적 성격 차이가 존재함

---

# 연구적 함의

본 연구의 핵심은
포용적 조직문화와 조직동일시가
비윤리적 친조직행동(UPB)과 어떠한 관계를 가지는지 확인하는 데 있다.

특히 조직동일시와 UPB 간 정적 관계가 나타날 경우,
강한 조직 충성이 조직을 위한 비윤리 행동 정당화로 이어질 수 있다는
'좋은 조직의 역설' 가능성을 시사할 수 있다.
"""

with open(
    "../results/correlation_result.md",
    "w",
    encoding="utf-8"
) as f:
    f.write(md_content)

print("\nCorrelation Markdown 저장 완료")