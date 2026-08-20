# UPB4 Sensitivity Analysis: Y20_4 Excluded

## 1. Analyses Run

- UPB4 composite: mean(Y20_1, Y20_2, Y20_3, Y20_5)
- UPB5 vs. UPB4 reliability/validity: alpha, CR, AVE, CFA loadings, scale correlation
- Six-factor CFA with UPB4
- Hierarchical HC3 OLS with UPB4 as the dependent variable
- H3 parallel OCB/UPB4 path contrast with 5,000 bootstrap resamples
- H4 coefficient contrasts with 5,000 bootstrap resamples
- Separate mediation models with 5,000 bootstrap resamples
- Simultaneous mediation with 10,000 bootstrap resamples
- Moderation and simple slopes
- PROCESS Model 14-style moderated mediation with 5,000 bootstrap resamples
- Latent structural SEM, product-indicator latent interaction SEM, and hybrid latent-interaction SEM with UPB4 indicators

## 2. UPB5 vs. UPB4 Measurement

| metric   |   Mean |     SD |   Cronbach alpha |     CR |    AVE |   UPB5_UPB4_corr |   Mean_change |   SD_change |
|:---------|-------:|-------:|-----------------:|-------:|-------:|-----------------:|--------------:|------------:|
| UPB5     | 2.9263 | 0.8118 |           0.8272 | 0.8306 | 0.5071 |            0.973 |         0     |       0     |
| UPB4     | 2.8793 | 0.8738 |           0.8433 | 0.8459 | 0.5831 |            0.973 |        -0.047 |       0.062 |

### UPB Loadings

| scale               | item   |   loading_std |   loading_unstd | factor   |
|:--------------------|:-------|--------------:|----------------:|:---------|
| UPB5                | Y20_1  |        0.8397 |          1      | nan      |
| UPB5                | Y20_2  |        0.8642 |          1.0605 | nan      |
| UPB5                | Y20_3  |        0.7001 |          0.8294 | nan      |
| UPB5                | Y20_4  |        0.4413 |          0.5208 | nan      |
| UPB5                | Y20_5  |        0.6315 |          0.7603 | nan      |
| UPB4                | Y20_1  |        0.8437 |          1      | nan      |
| UPB4                | Y20_2  |        0.8718 |          1.0649 | nan      |
| UPB4                | Y20_3  |        0.692  |          0.8161 | nan      |
| UPB4                | Y20_5  |        0.6179 |          0.7405 | nan      |
| UPB4 six-factor CFA | Y20_1  |        0.8437 |          1      | upb4     |
| UPB4 six-factor CFA | Y20_2  |        0.8697 |          1.0622 | upb4     |
| UPB4 six-factor CFA | Y20_3  |        0.6943 |          0.8187 | upb4     |
| UPB4 six-factor CFA | Y20_5  |        0.6197 |          0.7427 | upb4     |

## 3. Six-Factor CFA

Baseline UPB5: chi2(362) = 1944.55, CFI = .952, TLI = .946, RMSEA = .047, SRMR = .040.

|    chi2 |   df |   CFI |   TLI |   RMSEA |   SRMR |
|--------:|-----:|------:|------:|--------:|-------:|
| 1816.58 |  335 | 0.954 | 0.948 |   0.047 |   0.04 |

## 4. Key Comparison Table

| analysis   | effect                              |   baseline_UPB5 |    UPB4 |   change | conclusion_stability   |
|:-----------|:------------------------------------|----------------:|--------:|---------:|:-----------------------|
| OLS        | OLS Equity -> UPB                   |           0.195 |  0.2209 |   0.0259 | stable                 |
| OLS        | OLS Inclusion -> UPB                |          -0.033 | -0.0584 |  -0.0254 | stable                 |
| OLS        | OLS OI -> UPB                       |           0.15  |  0.1495 |  -0.0005 | stable                 |
| H3         | H3 OI -> UPB                        |           0.144 |  0.1513 |   0.0073 | stable                 |
| H3         | H3 OI->OCB minus OI->UPB            |           0.101 |  0.0938 |  -0.0072 | stable                 |
| H4         | H4 Equity->UPB minus Inclusion->UPB |           0.248 |  0.2847 |   0.0367 | stable                 |
| Mediation  | Mediation Equity indirect           |           0.034 |  0.0385 |   0.0045 | stable                 |
| Mediation  | Mediation Inclusion indirect        |           0.038 |  0.043  |   0.005  | stable                 |
| Mediation  | Mediation indirect difference       |           0.004 |  0.0045 |   0.0005 | stable                 |
| Moderation | Moderation OI x EL                  |          -0.062 | -0.0635 |  -0.0015 | stable                 |
| ModMed     | ModMed Equity index                 |          -0.027 | -0.0239 |   0.0031 | stable                 |
| ModMed     | ModMed Inclusion index              |          -0.026 | -0.0261 |  -0.0001 | stable                 |
| Latent     | Latent SEM OI -> UPB                |           0.182 |  0.185  |   0.003  | stable                 |
| Latent     | Latent SEM Equity -> UPB            |           0.269 |  0.2726 |   0.0036 | stable                 |
| Latent     | Latent interaction OI x EL          |          -0.087 | -0.0851 |   0.0019 | stable                 |

## 5. H3-H7 Robustness Judgment

- H3: OI remains positively related to UPB4; OI -> OCB remains larger than OI -> UPB4.
- H4: Equity -> UPB4 remains stronger than Inclusion -> UPB4.
- H5/H6 mediation: Both equity and inclusion indirect effects through OI remain positive; their difference remains small.
- H7 moderation: OI x EL remains negative, preserving the substantive interpretation that ethical leadership weakens the OI -> UPB pathway.
- Moderated mediation: Both indexes remain negative, preserving the conditional-process interpretation.

Final judgment: **A. Strong robustness**.

## 6. Latent SEM

### Latent Structural Paths

| effect                           |   estimate |
|:---------------------------------|-----------:|
| Equity -> OI                     |     0.286  |
| Inclusion -> OI                  |     0.3166 |
| OI -> UPB4                       |     0.185  |
| Equity -> UPB4 direct            |     0.2726 |
| Inclusion -> UPB4 direct         |    -0.1049 |
| Equity -> OI -> UPB4 indirect    |     0.0529 |
| Inclusion -> OI -> UPB4 indirect |     0.0585 |

### Product-Indicator Latent Interaction / Conditional Effects

| effect                                    |   estimate |
|:------------------------------------------|-----------:|
| OI x EL -> UPB4                           |    -0.0851 |
| OI -> UPB4 at low EL                      |     0.2584 |
| OI -> UPB4 at high EL                     |     0.0883 |
| Equity conditional indirect at low EL     |     0.0729 |
| Equity conditional indirect at high EL    |     0.0249 |
| Inclusion conditional indirect at low EL  |     0.0828 |
| Inclusion conditional indirect at high EL |     0.0283 |

### Hybrid Latent Interaction / Conditional Effects

| effect                                    |   estimate |
|:------------------------------------------|-----------:|
| OI x EL -> UPB4                           |    -0.08   |
| OI -> UPB4 at low EL                      |     0.2484 |
| OI -> UPB4 at high EL                     |     0.0955 |
| Equity conditional indirect at low EL     |     0.071  |
| Equity conditional indirect at high EL    |     0.0273 |
| Inclusion conditional indirect at low EL  |     0.0786 |
| Inclusion conditional indirect at high EL |     0.0303 |

## 7. Warnings

The product-indicator model follows the existing semopy product-indicator approach but remains unconstrained because semopy does not implement the full LMS estimator. The hybrid latent-interaction model uses a composite observed interaction term inside a latent measurement model and should be read as an auxiliary robustness check.

## 8. Results Paragraph Draft

As a sensitivity check, UPB was recomputed after excluding Y20_4 and averaging Y20_1, Y20_2, Y20_3, and Y20_5. The core UPB-related coefficients retained their substantive directions. In the hierarchical HC3 OLS model, equity remained positively associated with UPB4 (beta = .221), whereas inclusion remained near zero/negative (beta = -.058). Organizational identification also remained positively associated with UPB4 in the parallel-outcome test (beta = .151, 95% BC CI [.097, .206]). The OI x ethical leadership interaction retained the expected negative sign (B = -.064, 95% CI [-.115, -.012]).

## 9. Methods / Analytical Strategy Draft

UPB4 was calculated as the row-wise mean of Y20_1, Y20_2, Y20_3, and Y20_5, using the same missing-data rule as the original composite-score construction. All model specifications, controls (gender, age, and public/private sector), centering decisions, HC3 robust standard errors, and bootstrap seeds/resample counts were held constant relative to the main analyses, except that UPB4 replaced the original five-item UPB composite or latent UPB factor.

## 10. Reviewer Response Draft

We conducted an item-exclusion sensitivity analysis because Y20_4 had the lowest standardized loading among the UPB indicators. Excluding Y20_4 did not materially alter the sign, magnitude, or interpretation of the focal UPB pathways. The findings therefore do not depend on the inclusion of Y20_4.

## 11. Reproducible Code and Output Paths

- Code: `code/40_upb4_y20_4_sensitivity.py`
- Output folder: `../results/upb4_y20_4_sensitivity`
- Main report: `../results/upb4_y20_4_sensitivity/upb4_sensitivity_report.md`

## 12. Direct Answer

Do the focal UPB-related findings of the present study materially depend on the inclusion of Y20_4?

**No.** Based on the analyses above, the focal UPB conclusions are not materially contingent on Y20_4. Excluding Y20_4 changes some numerical estimates modestly, but the directional pattern and substantive conclusions remain stable.
