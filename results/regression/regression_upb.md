
# Regression Analysis Result

## 종속변수
- UPB (비윤리적 친조직행동)

---

# Model 1
통제변수만 포함

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    upb   R-squared:                       0.018
Model:                            OLS   Adj. R-squared:                  0.016
Method:                 Least Squares   F-statistic:                     12.54
Date:                Fri, 24 Jul 2026   Prob (F-statistic):           4.03e-08
Time:                        14:48:36   Log-Likelihood:                -2426.2
No. Observations:                2020   AIC:                             4860.
Df Residuals:                    2016   BIC:                             4883.
Df Model:                           3                                         
Covariance Type:                  HC3                                         
===============================================================================
                  coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------
const           3.1195      0.087     35.837      0.000       2.949       3.290
gender_male     0.0211      0.037      0.566      0.571      -0.052       0.094
age            -0.0023      0.002     -1.127      0.260      -0.006       0.002
public_org     -0.2234      0.037     -6.097      0.000      -0.295      -0.152
==============================================================================
Omnibus:                       22.361   Durbin-Watson:                   1.924
Prob(Omnibus):                  0.000   Jarque-Bera (JB):               22.279
Skew:                          -0.238   Prob(JB):                     1.45e-05
Kurtosis:                       2.805   Cond. No.                         214.
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)

---

# Model 2
조직문화 변수 추가

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    upb   R-squared:                       0.080
Model:                            OLS   Adj. R-squared:                  0.078
Method:                 Least Squares   F-statistic:                     27.39
Date:                Fri, 24 Jul 2026   Prob (F-statistic):           6.66e-27
Time:                        14:48:36   Log-Likelihood:                -2359.9
No. Observations:                2020   AIC:                             4732.
Df Residuals:                    2014   BIC:                             4765.
Df Model:                           5                                         
Covariance Type:                  HC3                                         
=====================================================================================
                        coef    std err          z      P>|z|      [0.025      0.975]
-------------------------------------------------------------------------------------
const                 2.4687      0.120     20.593      0.000       2.234       2.704
gender_male          -0.0222      0.037     -0.607      0.544      -0.094       0.049
age                  -0.0034      0.002     -1.750      0.080      -0.007       0.000
public_org           -0.1456      0.037     -3.976      0.000      -0.217      -0.074
equity_climate        0.2291      0.030      7.739      0.000       0.171       0.287
inclusion_climate     0.0054      0.031      0.175      0.861      -0.056       0.066
==============================================================================
Omnibus:                       13.453   Durbin-Watson:                   1.959
Prob(Omnibus):                  0.001   Jarque-Bera (JB):               13.647
Skew:                          -0.195   Prob(JB):                      0.00109
Kurtosis:                       2.901   Cond. No.                         276.
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)

---

# Model 3
조직동일시 추가

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    upb   R-squared:                       0.095
Model:                            OLS   Adj. R-squared:                  0.092
Method:                 Least Squares   F-statistic:                     27.33
Date:                Fri, 24 Jul 2026   Prob (F-statistic):           1.72e-31
Time:                        14:48:36   Log-Likelihood:                -2344.0
No. Observations:                2020   AIC:                             4702.
Df Residuals:                    2013   BIC:                             4741.
Df Model:                           6                                         
Covariance Type:                  HC3                                         
======================================================================================
                         coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------------
const                  2.3186      0.123     18.876      0.000       2.078       2.559
gender_male           -0.0154      0.036     -0.426      0.670      -0.087       0.056
age                   -0.0066      0.002     -3.292      0.001      -0.010      -0.003
public_org            -0.1488      0.036     -4.091      0.000      -0.220      -0.078
equity_climate         0.1951      0.030      6.549      0.000       0.137       0.254
inclusion_climate     -0.0325      0.032     -1.022      0.307      -0.095       0.030
org_identification     0.1498      0.029      5.180      0.000       0.093       0.207
==============================================================================
Omnibus:                       16.348   Durbin-Watson:                   1.963
Prob(Omnibus):                  0.000   Jarque-Bera (JB):               16.628
Skew:                          -0.222   Prob(JB):                     0.000245
Kurtosis:                       2.989   Cond. No.                         284.
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)

---

# Model 4
윤리적 리더십 추가

                            OLS Regression Results                            
==============================================================================
Dep. Variable:                    upb   R-squared:                       0.095
Model:                            OLS   Adj. R-squared:                  0.092
Method:                 Least Squares   F-statistic:                     23.41
Date:                Fri, 24 Jul 2026   Prob (F-statistic):           9.59e-31
Time:                        14:48:36   Log-Likelihood:                -2343.8
No. Observations:                2020   AIC:                             4704.
Df Residuals:                    2012   BIC:                             4748.
Df Model:                           7                                         
Covariance Type:                  HC3                                         
======================================================================================
                         coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------------
const                  2.3117      0.124     18.630      0.000       2.069       2.555
gender_male           -0.0165      0.036     -0.453      0.651      -0.088       0.055
age                   -0.0065      0.002     -3.261      0.001      -0.010      -0.003
public_org            -0.1526      0.037     -4.165      0.000      -0.224      -0.081
equity_climate         0.1854      0.033      5.560      0.000       0.120       0.251
inclusion_climate     -0.0365      0.032     -1.125      0.260      -0.100       0.027
org_identification     0.1475      0.029      5.080      0.000       0.091       0.204
ethical_leadership     0.0175      0.028      0.624      0.532      -0.037       0.072
==============================================================================
Omnibus:                       16.076   Durbin-Watson:                   1.964
Prob(Omnibus):                  0.000   Jarque-Bera (JB):               16.339
Skew:                          -0.220   Prob(JB):                     0.000283
Kurtosis:                       2.994   Cond. No.                         286.
==============================================================================

Notes:
[1] Standard Errors are heteroscedasticity robust (HC3)

---

# VIF 결과

| Variable           |    VIF |
|:-------------------|-------:|
| const              | 43.782 |
| gender_male        |  1.082 |
| age                |  1.23  |
| public_org         |  1.147 |
| equity_climate     |  2.445 |
| inclusion_climate  |  1.88  |
| org_identification |  1.465 |
| ethical_leadership |  2.004 |

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
