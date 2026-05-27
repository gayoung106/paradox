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
# 집단 분리
# --------------------------------------------------

public_df = df[
    df["유형"] == "공공"
]

private_df = df[
    df["유형"] == "민간"
]

print("\n공공 표본:", public_df.shape)
print("민간 표본:", private_df.shape)

# --------------------------------------------------
# 회귀 함수
# --------------------------------------------------

def run_regression(data, group_name):

    X = data[
        [
            "inclusion_climate",
            "org_identification",
            "ethical_leadership"
        ]
    ]

    X = sm.add_constant(X)

    y = data["upb"]

    model = sm.OLS(
        y,
        X
    ).fit(cov_type="HC3")

    print(f"\n{group_name}")
    print(model.summary())

    return model

# --------------------------------------------------
# 공공
# --------------------------------------------------

public_model = run_regression(
    public_df,
    "Public Organization"
)

# --------------------------------------------------
# 민간
# --------------------------------------------------

private_model = run_regression(
    private_df,
    "Private Organization"
)

# --------------------------------------------------
# 결과 폴더 생성
# --------------------------------------------------

os.makedirs(
    "../results/group_comparison",
    exist_ok=True
)

# --------------------------------------------------
# Markdown 저장
# --------------------------------------------------

md_content = f"""
# Group Comparison Result

# Public Organization

{public_model.summary().as_text()}

---

# Private Organization

{private_model.summary().as_text()}

---

# 핵심 해석

## 공공조직

공공조직에서는
조직보호 및 조직충성 논리가
UPB와 더 강하게 연결될 가능성이 존재함.

특히 조직동일시가
비윤리적 친조직행동과
강하게 연결될 경우,

이는 공공조직 특유의
조직보호 문화 및 평판관리 성향과
관련될 가능성이 있음.

---

## 민간조직

민간조직에서는
성과압박 및 경쟁 환경이
UPB를 강화할 가능성이 존재함.

따라서 동일한 조직동일시라도
공공과 민간에서
상이한 방식으로 작동할 가능성이 있음.

---

# 연구적 함의

본 연구는
포용적 조직문화와 조직동일시의 효과가
조직 맥락에 따라 다르게 나타날 수 있음을 시사한다.

즉,
공공과 민간은
서로 다른 조직논리 및 규범구조를 가지며,

동일한 조직충성이라도
비윤리적 친조직행동으로 이어지는 방식은
다를 수 있다.
"""

with open(
    "../results/group_comparison/group_comparison_result.md",
    "w",
    encoding="utf-8"
) as f:

    f.write(md_content)

print("\n집단비교 Markdown 저장 완료")
print("\n저장 경로:")
print(
    "../results/group_comparison/group_comparison_result.md"
)