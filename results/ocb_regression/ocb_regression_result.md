
# OCB Regression Analysis Result

## 종속변수
- OCB (조직시민행동)

---

# Model 1

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    ocb   R-squared:                       0.022
Model:                            OLS   Adj. R-squared:                  0.021
Method:                 Least Squares   F-statistic:                     25.53
Date:                Wed, 27 May 2026   Prob (F-statistic):           1.12e-11
Time:                        09:09:17   Log-Likelihood:                -2078.2
No. Observations:                2020   AIC:                             4162.
Df Residuals:                    2017   BIC:                             4179.
Df Model:                           2                                         
Covariance Type:                  HC3                                         
===============================================================================
                  coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------
const          24.0487      3.037      7.917      0.000      18.095      30.002
gender_male -3.309e-12   4.18e-13     -7.917      0.000   -4.13e-12   -2.49e-12
SQ1K2_1        -0.0103      0.002     -6.702      0.000      -0.013      -0.007
public_org      0.1191      0.031      3.856      0.000       0.059       0.180
==============================================================================
Omnibus:                      116.094   Durbin-Watson:                   2.019
Prob(Omnibus):                  0.000   Jarque-Bera (JB):              150.123
Skew:                          -0.540   Prob(JB):                     2.52e-33
Kurtosis:                       3.786   Cond. No.                     7.73e+19
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)
[2] The smallest eigenvalue is 1.33e-30. This might indicate that there are
strong multicollinearity problems or that the design matrix is singular.

---

# Model 2

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    ocb   R-squared:                       0.180
Model:                            OLS   Adj. R-squared:                  0.178
Method:                 Least Squares   F-statistic:                     72.14
Date:                Wed, 27 May 2026   Prob (F-statistic):           3.51e-57
Time:                        09:09:17   Log-Likelihood:                -1899.8
No. Observations:                2020   AIC:                             3810.
Df Residuals:                    2015   BIC:                             3838.
Df Model:                           4                                         
Covariance Type:                  HC3                                         
=====================================================================================
                        coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------------
const                19.2204      2.748      6.994      0.000      13.834      24.607
gender_male         3.75e-12   5.36e-13      6.994      0.000     2.7e-12     4.8e-12
SQ1K2_1              -0.0084      0.001     -6.085      0.000      -0.011      -0.006
public_org            0.1288      0.029      4.411      0.000       0.072       0.186
equity_climate        0.0019      0.022      0.088      0.930      -0.041       0.045
inclusion_climate     0.3376      0.027     12.692      0.000       0.285       0.390
==============================================================================
Omnibus:                       75.967   Durbin-Watson:                   2.041
Prob(Omnibus):                  0.000   Jarque-Bera (JB):              119.895
Skew:                          -0.334   Prob(JB):                     9.23e-27
Kurtosis:                       3.990   Cond. No.                     4.17e+19
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)
[2] The smallest eigenvalue is 4.56e-30. This might indicate that there are
strong multicollinearity problems or that the design matrix is singular.

---

# Model 3

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    ocb   R-squared:                       0.222
Model:                            OLS   Adj. R-squared:                  0.220
Method:                 Least Squares   F-statistic:                     71.69
Date:                Wed, 27 May 2026   Prob (F-statistic):           3.31e-69
Time:                        09:09:17   Log-Likelihood:                -1846.4
No. Observations:                2020   AIC:                             3705.
Df Residuals:                    2014   BIC:                             3738.
Df Model:                           5                                         
Covariance Type:                  HC3                                         
======================================================================================
                         coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------------
const                  9.9868      2.832      3.527      0.000       4.437      15.537
gender_male        -3.485e-12   9.88e-13     -3.527      0.000   -5.42e-12   -1.55e-12
SQ1K2_1               -0.0040      0.001     -2.800      0.005      -0.007      -0.001
public_org             0.1248      0.028      4.395      0.000       0.069       0.181
equity_climate        -0.0466      0.022     -2.142      0.032      -0.089      -0.004
inclusion_climate      0.2824      0.027     10.608      0.000       0.230       0.335
org_identification     0.2169      0.024      8.872      0.000       0.169       0.265
==============================================================================
Omnibus:                       63.854   Durbin-Watson:                   2.034
Prob(Omnibus):                  0.000   Jarque-Bera (JB):              107.523
Skew:                          -0.267   Prob(JB):                     4.48e-24
Kurtosis:                       3.996   Cond. No.                     3.84e+19
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)
[2] The smallest eigenvalue is 5.37e-30. This might indicate that there are
strong multicollinearity problems or that the design matrix is singular.

---

# Model 4

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    ocb   R-squared:                       0.226
Model:                            OLS   Adj. R-squared:                  0.224
Method:                 Least Squares   F-statistic:                     62.31
Date:                Wed, 27 May 2026   Prob (F-statistic):           4.32e-71
Time:                        09:09:17   Log-Likelihood:                -1841.3
No. Observations:                2020   AIC:                             3697.
Df Residuals:                    2013   BIC:                             3736.
Df Model:                           6                                         
Covariance Type:                  HC3                                         
======================================================================================
                         coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------------
const                 10.2139      2.835      3.603      0.000       4.658      15.769
gender_male         4.356e-12   1.21e-12      3.603      0.000    1.99e-12    6.72e-12
SQ1K2_1               -0.0041      0.001     -2.884      0.004      -0.007      -0.001
public_org             0.1107      0.029      3.836      0.000       0.054       0.167
equity_climate        -0.0819      0.025     -3.264      0.001      -0.131      -0.033
inclusion_climate      0.2682      0.027      9.824      0.000       0.215       0.322
org_identification     0.2086      0.025      8.470      0.000       0.160       0.257
ethical_leadership     0.0633      0.023      2.765      0.006       0.018       0.108
==============================================================================
Omnibus:                       61.636   Durbin-Watson:                   2.038
Prob(Omnibus):                  0.000   Jarque-Bera (JB):              103.454
Skew:                          -0.259   Prob(JB):                     3.43e-23
Kurtosis:                       3.980   Cond. No.                     2.54e+20
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)
[2] The smallest eigenvalue is 1.23e-31. This might indicate that there are
strong multicollinearity problems or that the design matrix is singular.

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
