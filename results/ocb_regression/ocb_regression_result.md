
# OCB Regression Analysis Result

## 종속변수
- OCB (조직시민행동)

---

# Model 1

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    ocb   R-squared:                       0.023
Model:                            OLS   Adj. R-squared:                  0.021
Method:                 Least Squares   F-statistic:                     17.75
Date:                Fri, 24 Jul 2026   Prob (F-statistic):           2.25e-11
Time:                        14:49:00   Log-Likelihood:                -2077.3
No. Observations:                2020   AIC:                             4163.
Df Residuals:                    2016   BIC:                             4185.
Df Model:                           3                                         
Covariance Type:                  HC3                                         
===============================================================================
                  coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------
const           3.2353      0.071     45.601      0.000       3.096       3.374
gender_male    -0.0437      0.031     -1.394      0.163      -0.105       0.018
age             0.0109      0.002      6.835      0.000       0.008       0.014
public_org      0.1210      0.031      3.920      0.000       0.061       0.181
==============================================================================
Omnibus:                      113.662   Durbin-Watson:                   2.019
Prob(Omnibus):                  0.000   Jarque-Bera (JB):              145.896
Skew:                          -0.535   Prob(JB):                     2.08e-32
Kurtosis:                       3.768   Cond. No.                         214.
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)

---

# Model 2

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    ocb   R-squared:                       0.182
Model:                            OLS   Adj. R-squared:                  0.180
Method:                 Least Squares   F-statistic:                     58.29
Date:                Fri, 24 Jul 2026   Prob (F-statistic):           8.47e-57
Time:                        14:49:00   Log-Likelihood:                -1897.0
No. Observations:                2020   AIC:                             3806.
Df Residuals:                    2014   BIC:                             3840.
Df Model:                           5                                         
Covariance Type:                  HC3                                         
=====================================================================================
                        coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------------
const                 2.1487      0.101     21.307      0.000       1.951       2.346
gender_male          -0.0675      0.029     -2.311      0.021      -0.125      -0.010
age                   0.0093      0.001      6.439      0.000       0.006       0.012
public_org            0.1333      0.029      4.562      0.000       0.076       0.191
equity_climate        0.0068      0.022      0.308      0.758      -0.036       0.050
inclusion_climate     0.3358      0.027     12.661      0.000       0.284       0.388
==============================================================================
Omnibus:                       73.383   Durbin-Watson:                   2.043
Prob(Omnibus):                  0.000   Jarque-Bera (JB):              114.180
Skew:                          -0.329   Prob(JB):                     1.61e-25
Kurtosis:                       3.962   Cond. No.                         276.
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)

---

# Model 3

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    ocb   R-squared:                       0.224
Model:                            OLS   Adj. R-squared:                  0.222
Method:                 Least Squares   F-statistic:                     59.59
Date:                Fri, 24 Jul 2026   Prob (F-statistic):           3.99e-68
Time:                        14:49:00   Log-Likelihood:                -1844.3
No. Observations:                2020   AIC:                             3703.
Df Residuals:                    2013   BIC:                             3742.
Df Model:                           6                                         
Covariance Type:                  HC3                                         
======================================================================================
                         coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------------
const                  1.9329      0.105     18.452      0.000       1.728       2.138
gender_male           -0.0578      0.028     -2.040      0.041      -0.113      -0.002
age                    0.0048      0.001      3.257      0.001       0.002       0.008
public_org             0.1287      0.028      4.521      0.000       0.073       0.185
equity_climate        -0.0421      0.022     -1.941      0.052      -0.085       0.000
inclusion_climate      0.2812      0.027     10.597      0.000       0.229       0.333
org_identification     0.2155      0.024      8.848      0.000       0.168       0.263
==============================================================================
Omnibus:                       63.078   Durbin-Watson:                   2.035
Prob(Omnibus):                  0.000   Jarque-Bera (JB):              105.746
Skew:                          -0.265   Prob(JB):                     1.09e-23
Kurtosis:                       3.987   Cond. No.                         284.
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)

---

# Model 4

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    ocb   R-squared:                       0.228
Model:                            OLS   Adj. R-squared:                  0.225
Method:                 Least Squares   F-statistic:                     53.40
Date:                Fri, 24 Jul 2026   Prob (F-statistic):           3.42e-70
Time:                        14:49:00   Log-Likelihood:                -1838.9
No. Observations:                2020   AIC:                             3694.
Df Residuals:                    2012   BIC:                             3739.
Df Model:                           7                                         
Covariance Type:                  HC3                                         
======================================================================================
                         coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------------
const                  1.9075      0.105     18.244      0.000       1.703       2.112
gender_male           -0.0615      0.028     -2.180      0.029      -0.117      -0.006
age                    0.0049      0.001      3.373      0.001       0.002       0.008
public_org             0.1145      0.029      3.959      0.000       0.058       0.171
equity_climate        -0.0781      0.025     -3.116      0.002      -0.127      -0.029
inclusion_climate      0.2666      0.027      9.799      0.000       0.213       0.320
org_identification     0.2069      0.025      8.433      0.000       0.159       0.255
ethical_leadership     0.0650      0.023      2.838      0.005       0.020       0.110
==============================================================================
Omnibus:                       60.686   Durbin-Watson:                   2.040
Prob(Omnibus):                  0.000   Jarque-Bera (JB):              101.333
Skew:                          -0.257   Prob(JB):                     9.90e-23
Kurtosis:                       3.970   Cond. No.                         286.
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)

---

# 핵심 해석

## Organizational Identification

조직동일시는
조직시민행동(OCB)을 강화하는 방향으로
작동할 가능성이 존재함.

이는 기존 조직행동 연구와
일관된 결과로 해석 가능.

---

## Inclusion Climate

포용적 조직문화는
조직구성원의 자발적 조직기여 행동을
강화할 가능성이 존재함.

---

# 연구적 함의

본 연구는
강한 조직충성이
긍정적 조직행동(OCB)뿐 아니라,
비윤리적 친조직행동(UPB)까지
동시에 강화할 가능성이 있음을 시사한다.

즉,
조직동일시는
양면적(double-edged) 특성을 가지며,

조직에 대한 헌신은
상황에 따라
윤리적 행동과 비윤리적 행동 모두로
이어질 수 있다.
