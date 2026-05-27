
# Moderated Mediation Result

# Model A
Inclusion Climate → Organizational Identification

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                   oi_c   R-squared:                       0.197
Model:                            OLS   Adj. R-squared:                  0.197
Method:                 Least Squares   F-statistic:                     393.4
Date:                Wed, 27 May 2026   Prob (F-statistic):           4.00e-80
Time:                        09:06:18   Log-Likelihood:                -2138.5
No. Observations:                2020   AIC:                             4281.
Df Residuals:                    2018   BIC:                             4292.
Df Model:                           1                                         
Covariance Type:                  HC3                                         
===============================================================================
                  coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------
Intercept   -9.415e-16      0.016  -6.06e-14      1.000      -0.030       0.030
inclusion_c     0.4290      0.022     19.834      0.000       0.387       0.471
==============================================================================
Omnibus:                       28.724   Durbin-Watson:                   1.843
Prob(Omnibus):                  0.000   Jarque-Bera (JB):               29.793
Skew:                          -0.279   Prob(JB):                     3.39e-07
Kurtosis:                       3.206   Cond. No.                         1.24
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)

---

# Model B
OI × Ethical Leadership → UPB

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    upb   R-squared:                       0.063
Model:                            OLS   Adj. R-squared:                  0.062
Method:                 Least Squares   F-statistic:                     34.16
Date:                Wed, 27 May 2026   Prob (F-statistic):           1.56e-21
Time:                        09:06:18   Log-Likelihood:                -2378.6
No. Observations:                2020   AIC:                             4765.
Df Residuals:                    2016   BIC:                             4788.
Df Model:                           3                                         
Covariance Type:                  HC3                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
Intercept      2.9460      0.018    163.183      0.000       2.911       2.981
oi_c           0.1619      0.027      6.035      0.000       0.109       0.214
el_c           0.0960      0.023      4.181      0.000       0.051       0.141
oi_x_el       -0.0647      0.024     -2.650      0.008      -0.112      -0.017
==============================================================================
Omnibus:                       20.865   Durbin-Watson:                   1.906
Prob(Omnibus):                  0.000   Jarque-Bera (JB):               21.399
Skew:                          -0.250   Prob(JB):                     2.26e-05
Kurtosis:                       2.933   Cond. No.                         1.79
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)

---

# Conditional Indirect Effect

| Condition | Indirect Effect |
|---|---|
| Low Ethical Leadership (-1SD) | 0.096 |
| High Ethical Leadership (+1SD) | 0.043 |

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
