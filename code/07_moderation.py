import pandas as pd
import statsmodels.formula.api as smf
import os

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

df = pd.read_csv(
    "../processed/analysis_data.csv"
)

print("데이터 크기:", df.shape)

# --------------------------------------------------
# 평균중심화
# --------------------------------------------------

df["oi_c"] = (
    df["org_identification"]
    - df["org_identification"].mean()
)

df["el_c"] = (
    df["ethical_leadership"]
    - df["ethical_leadership"].mean()
)

# --------------------------------------------------
# 상호작용항 생성
# --------------------------------------------------

df["interaction"] = (
    df["oi_c"] * df["el_c"]
)

# --------------------------------------------------
# 조절효과 회귀분석
# --------------------------------------------------

model = smf.ols(
    """
    upb ~
    oi_c +
    el_c +
    interaction
    """,
    data=df
).fit(cov_type="HC3")

print(model.summary())

# --------------------------------------------------
# 결과 폴더 생성
# --------------------------------------------------

os.makedirs(
    "../results/moderation",
    exist_ok=True
)

# --------------------------------------------------
# Markdown 저장
# --------------------------------------------------

md_content = f"""
# Moderation Analysis Result

# Model
Organizational Identification × Ethical Leadership → UPB

---

{model.summary().as_text()}

---

# 핵심 해석 포인트

## Interaction Term
interaction 항이 유의할 경우,
윤리적 리더십이
조직동일시와 UPB 간 관계를 조절하는 것으로 해석 가능.

---

## 예상 방향

### 음(-)의 interaction
윤리적 리더십이 높을수록,
조직동일시가 UPB로 이어지는 경향이 약화됨을 의미.

즉,
윤리적 리더십이
조직충성의 부정적 효과를 완충할 가능성 시사.

---

# 연구적 함의

본 연구는
강한 조직동일시가
항상 긍정적 결과만을 가져오는 것은 아닐 수 있다는 점에 주목한다.

그러나 윤리적 리더십이 존재할 경우,
조직을 위한 비윤리 행동으로의 전이를
억제할 가능성이 존재한다.

이는
포용적 조직문화 자체보다,
그 문화가 어떠한 윤리적 규범과 함께 운영되는지가
중요할 수 있음을 시사한다.
"""

with open(
    "../results/moderation/moderation_result.md",
    "w",
    encoding="utf-8"
) as f:

    f.write(md_content)

print("\n조절효과 Markdown 저장 완료")
print("\n저장 경로:")
print("../results/moderation/moderation_result.md")