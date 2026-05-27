
# Table 1. Descriptive Statistics and Correlations

# Descriptive Statistics

|                    |   Mean |    SD |   Min |   Max |
|:-------------------|-------:|------:|------:|------:|
| equity_climate     |  2.903 | 0.899 |     1 |     5 |
| inclusion_climate  |  3.389 | 0.806 |     1 |     5 |
| org_identification |  3.375 | 0.779 |     1 |     5 |
| ethical_leadership |  3.233 | 0.955 |     1 |     5 |
| ocb                |  3.72  | 0.685 |     1 |     5 |
| upb                |  2.926 | 0.812 |     1 |     5 |

---

# Correlation Matrix

|                    |   equity_climate |   inclusion_climate |   org_identification |   ethical_leadership |   ocb |   upb |
|:-------------------|-----------------:|--------------------:|---------------------:|---------------------:|------:|------:|
| equity_climate     |            1     |               0.636 |                0.454 |                0.668 | 0.25  | 0.269 |
| inclusion_climate  |            0.636 |               1     |                0.444 |                0.565 | 0.404 | 0.166 |
| org_identification |            0.454 |               0.444 |                1     |                0.41  | 0.373 | 0.214 |
| ethical_leadership |            0.668 |               0.565 |                0.41  |                1     | 0.295 | 0.19  |
| ocb                |            0.25  |               0.404 |                0.373 |                0.295 | 1     | 0.113 |
| upb                |            0.269 |               0.166 |                0.214 |                0.19  | 0.113 | 1     |

---

# VIF

| Variable           |    VIF |
|:-------------------|-------:|
| const              | 45.188 |
| equity_climate     |  2.344 |
| inclusion_climate  |  1.991 |
| org_identification |  1.439 |
| ethical_leadership |  1.959 |
| ocb                |  1.281 |
| upb                |  1.092 |

---

# 해석

## 기술통계

전반적으로 조직시민행동(OCB)의 평균이
비교적 높게 나타난 반면,

비윤리적 친조직행동(UPB)은
상대적으로 중간 수준으로 나타났다.

---

## 상관관계

포용적 조직문화와 조직동일시는
정적 상관관계를 가지는 것으로 나타났으며,

조직동일시는
OCB뿐 아니라 UPB와도
정적 관계를 보일 가능성이 확인되었다.

---

## 다중공선성

VIF 값이 일반적인 기준치(10 미만)를
초과하지 않는 경우,

심각한 다중공선성 문제는
없는 것으로 판단 가능하다.
