
# Moderated Mediation Result

# Model A
Inclusion Climate → Organizational Identification

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                   oi_c   R-squared:                       0.269
Model:                            OLS   Adj. R-squared:                  0.267
Method:                 Least Squares   F-statistic:                     171.2
Date:                Fri, 24 Jul 2026   Prob (F-statistic):          2.70e-126
Time:                        14:42:37   Log-Likelihood:                -2044.5
No. Observations:                2020   AIC:                             4099.
Df Residuals:                    2015   BIC:                             4127.
Df Model:                           4                                         
Covariance Type:                  HC3                                         
===============================================================================
                  coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------
Intercept      -0.8543      0.072    -11.796      0.000      -0.996      -0.712
inclusion_c     0.4115      0.021     19.718      0.000       0.371       0.452
gender_male    -0.0131      0.031     -0.425      0.671      -0.074       0.047
age             0.0215      0.002     13.118      0.000       0.018       0.025
public_org     -0.0508      0.031     -1.654      0.098      -0.111       0.009
==============================================================================
Omnibus:                       22.335   Durbin-Watson:                   1.905
Prob(Omnibus):                  0.000   Jarque-Bera (JB):               22.864
Skew:                          -0.247   Prob(JB):                     1.08e-05
Kurtosis:                       3.168   Cond. No.                         214.
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)

---

# Model B
OI × Ethical Leadership → UPB

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    upb   R-squared:                       0.081
Model:                            OLS   Adj. R-squared:                  0.079
Method:                 Least Squares   F-statistic:                     23.81
Date:                Fri, 24 Jul 2026   Prob (F-statistic):           2.47e-27
Time:                        14:42:37   Log-Likelihood:                -2358.7
No. Observations:                2020   AIC:                             4731.
Df Residuals:                    2013   BIC:                             4771.
Df Model:                           6                                         
Covariance Type:                  HC3                                         
===============================================================================
                  coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------
Intercept       3.3276      0.086     38.643      0.000       3.159       3.496
oi_c            0.1707      0.028      6.178      0.000       0.117       0.225
el_c            0.0972      0.023      4.201      0.000       0.052       0.142
oi_x_el        -0.0623      0.025     -2.539      0.011      -0.110      -0.014
gender_male     0.0007      0.036      0.020      0.984      -0.070       0.072
age            -0.0067      0.002     -3.324      0.001      -0.011      -0.003
public_org     -0.2128      0.035     -6.025      0.000      -0.282      -0.144
==============================================================================
Omnibus:                       15.130   Durbin-Watson:                   1.952
Prob(Omnibus):                  0.001   Jarque-Bera (JB):               15.359
Skew:                          -0.214   Prob(JB):                     0.000462
Kurtosis:                       2.992   Cond. No.                         221.
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)

---

# Conditional Indirect Effect

| Condition | Indirect Effect | 95% CI Lower | 95% CI Upper |
|---|---|---|---|
| Low Ethical Leadership (-1SD) | 0.095 | 0.064 | 0.126 |
| High Ethical Leadership (+1SD) | 0.046 | 0.016 | 0.076 |

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
