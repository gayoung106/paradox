
# Regression Analysis Result

## 종속변수
- UPB (비윤리적 친조직행동)

---

# Model 1
통제변수만 포함

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    upb   R-squared:                       0.018
Model:                            OLS   Adj. R-squared:                  0.017
Method:                 Least Squares   F-statistic:                     18.44
Date:                Wed, 27 May 2026   Prob (F-statistic):           1.16e-08
Time:                        09:03:36   Log-Likelihood:                -2426.4
No. Observations:                2020   AIC:                             4859.
Df Residuals:                    2017   BIC:                             4876.
Df Model:                           2                                         
Covariance Type:                  HC3                                         
===============================================================================
                  coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------
const          -0.8687      3.801     -0.229      0.819      -8.318       6.581
gender_male  1.196e-13   5.23e-13      0.229      0.819   -9.05e-13    1.14e-12
SQ1K2_1         0.0020      0.002      1.027      0.305      -0.002       0.006
public_org     -0.2225      0.037     -6.067      0.000      -0.294      -0.151
==============================================================================
Omnibus:                       22.013   Durbin-Watson:                   1.924
Prob(Omnibus):                  0.000   Jarque-Bera (JB):               21.874
Skew:                          -0.235   Prob(JB):                     1.78e-05
Kurtosis:                       2.802   Cond. No.                     7.73e+19
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)
[2] The smallest eigenvalue is 1.33e-30. This might indicate that there are
strong multicollinearity problems or that the design matrix is singular.

---

# Model 2
조직문화 변수 추가

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    upb   R-squared:                       0.080
Model:                            OLS   Adj. R-squared:                  0.078
Method:                 Least Squares   F-statistic:                     34.26
Date:                Wed, 27 May 2026   Prob (F-statistic):           1.06e-27
Time:                        09:03:36   Log-Likelihood:                -2360.1
No. Observations:                2020   AIC:                             4730.
Df Residuals:                    2015   BIC:                             4758.
Df Model:                           4                                         
Covariance Type:                  HC3                                         
=====================================================================================
                        coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------------
const                -5.0207      3.716     -1.351      0.177     -12.303       2.262
gender_male       -9.794e-13   7.25e-13     -1.351      0.177    -2.4e-12    4.41e-13
SQ1K2_1               0.0037      0.002      1.976      0.048    3.01e-05       0.007
public_org           -0.1471      0.037     -4.015      0.000      -0.219      -0.075
equity_climate        0.2275      0.029      7.763      0.000       0.170       0.285
inclusion_climate     0.0060      0.031      0.194      0.846      -0.055       0.067
==============================================================================
Omnibus:                       13.851   Durbin-Watson:                   1.959
Prob(Omnibus):                  0.001   Jarque-Bera (JB):               14.060
Skew:                          -0.198   Prob(JB):                     0.000885
Kurtosis:                       2.903   Cond. No.                     4.17e+19
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)
[2] The smallest eigenvalue is 4.56e-30. This might indicate that there are
strong multicollinearity problems or that the design matrix is singular.

---

# Model 3
조직동일시 추가

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    upb   R-squared:                       0.095
Model:                            OLS   Adj. R-squared:                  0.092
Method:                 Least Squares   F-statistic:                     32.80
Date:                Wed, 27 May 2026   Prob (F-statistic):           2.92e-32
Time:                        09:03:36   Log-Likelihood:                -2344.1
No. Observations:                2020   AIC:                             4700.
Df Residuals:                    2014   BIC:                             4734.
Df Model:                           5                                         
Covariance Type:                  HC3                                         
======================================================================================
                         coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------------
const                -11.4163      3.825     -2.984      0.003     -18.914      -3.919
gender_male         3.984e-12   1.33e-12      2.984      0.003    1.37e-12     6.6e-12
SQ1K2_1                0.0068      0.002      3.532      0.000       0.003       0.011
public_org            -0.1498      0.036     -4.118      0.000      -0.221      -0.079
equity_climate         0.1939      0.029      6.579      0.000       0.136       0.252
inclusion_climate     -0.0322      0.032     -1.013      0.311      -0.095       0.030
org_identification     0.1502      0.029      5.197      0.000       0.094       0.207
==============================================================================
Omnibus:                       16.679   Durbin-Watson:                   1.963
Prob(Omnibus):                  0.000   Jarque-Bera (JB):               16.971
Skew:                          -0.224   Prob(JB):                     0.000206
Kurtosis:                       2.990   Cond. No.                     3.84e+19
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)
[2] The smallest eigenvalue is 5.37e-30. This might indicate that there are
strong multicollinearity problems or that the design matrix is singular.

---

# Model 4
윤리적 리더십 추가

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    upb   R-squared:                       0.095
Model:                            OLS   Adj. R-squared:                  0.092
Method:                 Least Squares   F-statistic:                     27.32
Date:                Wed, 27 May 2026   Prob (F-statistic):           1.80e-31
Time:                        09:03:36   Log-Likelihood:                -2343.9
No. Observations:                2020   AIC:                             4702.
Df Residuals:                    2013   BIC:                             4741.
Df Model:                           6                                         
Covariance Type:                  HC3                                         
======================================================================================
                         coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------------
const                -11.3553      3.829     -2.966      0.003     -18.860      -3.850
gender_male        -4.842e-12   1.63e-12     -2.966      0.003   -8.04e-12   -1.64e-12
SQ1K2_1                0.0068      0.002      3.511      0.000       0.003       0.011
public_org            -0.1536      0.037     -4.190      0.000      -0.225      -0.082
equity_climate         0.1844      0.033      5.560      0.000       0.119       0.249
inclusion_climate     -0.0360      0.032     -1.114      0.265      -0.099       0.027
org_identification     0.1480      0.029      5.101      0.000       0.091       0.205
ethical_leadership     0.0170      0.028      0.609      0.543      -0.038       0.072
==============================================================================
Omnibus:                       16.441   Durbin-Watson:                   1.964
Prob(Omnibus):                  0.000   Jarque-Bera (JB):               16.717
Skew:                          -0.223   Prob(JB):                     0.000234
Kurtosis:                       2.995   Cond. No.                     2.54e+20
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)
[2] The smallest eigenvalue is 1.23e-31. This might indicate that there are
strong multicollinearity problems or that the design matrix is singular.

---

# VIF 결과

| Variable           |       VIF |
|:-------------------|----------:|
| const              | 51928.1   |
| gender_male        |   nan     |
| SQ1K2_1            |     1.157 |
| public_org         |     1.143 |
| equity_climate     |     2.432 |
| inclusion_climate  |     1.878 |
| org_identification |     1.463 |
| ethical_leadership |     2     |

---

# 핵심 해석 포인트

## Inclusion Climate
포용적 조직문화가
UPB와 정적 관계를 가지는지 확인 필요

## Organizational Identification
조직동일시가 추가되었을 때
Inclusion 효과가 감소하면
매개효과 가능성을 시사

## Ethical Leadership
윤리적 리더십이
UPB를 억제하는 방향인지 확인 필요

---

# 다중공선성 해석

- VIF 5 미만: 일반적으로 양호
- VIF 10 이상: 다중공선성 문제 가능성

조직문화 및 리더십 변수들은
개념적으로 상관성이 존재할 가능성이 있으므로
일정 수준의 상관은 예상 가능한 결과임.
