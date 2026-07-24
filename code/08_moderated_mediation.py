import pandas as pd
import statsmodels.formula.api as smf
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
# 평균중심화
# --------------------------------------------------

df["inclusion_c"] = (
    df["inclusion_climate"]
    - df["inclusion_climate"].mean()
)

df["oi_c"] = (
    df["org_identification"]
    - df["org_identification"].mean()
)

df["el_c"] = (
    df["ethical_leadership"]
    - df["ethical_leadership"].mean()
)

# --------------------------------------------------
# 통제변수 (성별·연령·조직유형; 05/11번과 동일한 사양)
# --------------------------------------------------

# SQ1K1 값 코드: 1.0=남자, 2.0=여자 (raw_data.sav 값 라벨 기준)
df["gender_male"] = (
    df["SQ1K1"] == 1.0
).astype(int)

# 연령 (출생연도 -> 연령 환산; 조사 기준연도 2023년)
df["age"] = 2023 - df["SQ1K2_1"]

df["public_org"] = (
    df["유형"] == "공공"
).astype(int)

CONTROLS = ["gender_male", "age", "public_org"]

# --------------------------------------------------
# interaction
# --------------------------------------------------

df["oi_x_el"] = (
    df["oi_c"] * df["el_c"]
)

# --------------------------------------------------
# 1단계
# Inclusion → OI
# --------------------------------------------------

model_a = smf.ols(
    "oi_c ~ inclusion_c + gender_male + age + public_org",
    data=df
).fit(cov_type="HC3")

print("\nModel A")
print(model_a.summary())

# --------------------------------------------------
# 2단계
# OI × EL → UPB
# --------------------------------------------------

model_b = smf.ols(
    """
    upb ~
    oi_c +
    el_c +
    oi_x_el +
    gender_male +
    age +
    public_org
    """,
    data=df
).fit(cov_type="HC3")

print("\nModel B")
print(model_b.summary())

# --------------------------------------------------
# Conditional indirect effect
# --------------------------------------------------

a_path = model_a.params["inclusion_c"]

b1 = model_b.params["oi_c"]

b3 = model_b.params["oi_x_el"]

el_sd = df["el_c"].std()

# 낮은 윤리적 리더십
low_el = -el_sd

# 높은 윤리적 리더십
high_el = el_sd

# conditional indirect effect
low_indirect = a_path * (
    b1 + b3 * low_el
)

high_indirect = a_path * (
    b1 + b3 * high_el
)

print("\nConditional Indirect Effect")
print("Low EL:", round(low_indirect, 3))
print("High EL:", round(high_indirect, 3))

# --------------------------------------------------
# Bootstrap Conditional Indirect Effect
# --------------------------------------------------

def bootstrap_conditional_indirect(
    data,
    n_boot=5000,
    seed=42
):

    np.random.seed(seed)

    low_effects = []
    high_effects = []

    el_sd_boot = data["el_c"].std()

    low_el_boot = -el_sd_boot
    high_el_boot = el_sd_boot

    for _ in range(n_boot):

        # bootstrap sample
        sample = data.sample(
            n=len(data),
            replace=True
        ).copy()

        # interaction 재생성
        sample["oi_x_el"] = (
            sample["oi_c"] * sample["el_c"]
        )

        # a path
        a_model = smf.ols(
            "oi_c ~ inclusion_c + gender_male + age + public_org",
            data=sample
        ).fit()

        # b path
        b_model = smf.ols(
            """
            upb ~
            oi_c +
            el_c +
            oi_x_el +
            gender_male +
            age +
            public_org
            """,
            data=sample
        ).fit()

        try:

            a = a_model.params["inclusion_c"]

            b1_boot = b_model.params["oi_c"]

            b3_boot = b_model.params["oi_x_el"]

            # conditional indirect effect
            low_ie = a * (
                b1_boot + b3_boot * low_el_boot
            )

            high_ie = a * (
                b1_boot + b3_boot * high_el_boot
            )

            low_effects.append(low_ie)
            high_effects.append(high_ie)

        except:

            continue

    # percentile bootstrap CI
    low_ci = np.percentile(
        low_effects,
        [2.5, 97.5]
    )

    high_ci = np.percentile(
        high_effects,
        [2.5, 97.5]
    )

    return {

        "low_effect": np.mean(low_effects),
        "low_ci_lower": low_ci[0],
        "low_ci_upper": low_ci[1],

        "high_effect": np.mean(high_effects),
        "high_ci_lower": high_ci[0],
        "high_ci_upper": high_ci[1]
    }

# --------------------------------------------------
# Bootstrap 실행
# --------------------------------------------------

boot_result = bootstrap_conditional_indirect(
    df,
    n_boot=5000
)

print("\nBootstrap Conditional Indirect Effect")

print(
    f"""
Low EL (-1SD)
Indirect Effect = {boot_result['low_effect']:.3f}

95% Bootstrap CI:
[
{boot_result['low_ci_lower']:.3f},
{boot_result['low_ci_upper']:.3f}
]

-----------------------------------

High EL (+1SD)
Indirect Effect = {boot_result['high_effect']:.3f}

95% Bootstrap CI:
[
{boot_result['high_ci_lower']:.3f},
{boot_result['high_ci_upper']:.3f}
]
"""
)

# --------------------------------------------------
# 결과 폴더 생성
# --------------------------------------------------

os.makedirs(
    "../results/moderated_mediation",
    exist_ok=True
)

# --------------------------------------------------
# Markdown 저장
# --------------------------------------------------

md_content = f"""
# Moderated Mediation Result

# Model A
Inclusion Climate → Organizational Identification

{model_a.summary().as_text()}

---

# Model B
OI × Ethical Leadership → UPB

{model_b.summary().as_text()}

---

# Conditional Indirect Effect

| Condition | Indirect Effect | 95% CI Lower | 95% CI Upper |
|---|---|---|---|
| Low Ethical Leadership (-1SD) | {boot_result['low_effect']:.3f} | {boot_result['low_ci_lower']:.3f} | {boot_result['low_ci_upper']:.3f} |
| High Ethical Leadership (+1SD) | {boot_result['high_effect']:.3f} | {boot_result['high_ci_lower']:.3f} | {boot_result['high_ci_upper']:.3f} |

---

# 핵심 해석

## Moderated Mediation

본 분석은
포용적 조직문화가
조직동일시를 통해
비윤리적 친조직행동(UPB)에 영향을 미치는 과정이,

윤리적 리더십 수준에 따라
달라지는지를 검토하였다.

---

## Conditional Indirect Effect

### Low Ethical Leadership

윤리적 리더십이 낮은 환경에서는
조직동일시를 통한 UPB 증가 효과가
상대적으로 강하게 나타날 가능성이 있음.

### High Ethical Leadership

윤리적 리더십이 높은 환경에서는
동일한 조직동일시가
UPB로 이어지는 경향이 약화될 가능성이 있음.

---

# Bootstrap Interpretation

조건부 간접효과의 통계적 유의성은
95% Bootstrap Confidence Interval 기준으로 검토하였다.

신뢰구간에 0이 포함되지 않을 경우,
조건부 간접효과가 유의한 것으로 해석할 수 있다.

---

# 연구적 함의

본 연구는
포용적 조직문화 자체가
반드시 윤리적 결과만을 보장하지는 않을 수 있다는 점에 주목한다.

특히 강한 조직동일시는
조직 보호 심리를 강화하며,
일부 상황에서는
비윤리적 친조직행동까지 정당화할 가능성이 존재한다.

그러나 윤리적 리더십이 존재할 경우,
이러한 위험 경로는 완화될 수 있으며,

이는 조직문화의 효과가
윤리적 규범 및 리더십 환경과 함께
해석될 필요가 있음을 시사한다.
"""

with open(
    "../results/moderated_mediation/moderated_mediation_result.md",
    "w",
    encoding="utf-8"
) as f:

    f.write(md_content)

print("\n조건부 간접효과 Markdown 저장 완료")

print("\n저장 경로:")

print(
    "../results/moderated_mediation/moderated_mediation_result.md"
)