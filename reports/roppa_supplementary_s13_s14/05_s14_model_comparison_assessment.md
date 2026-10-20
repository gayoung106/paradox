# Assessment of Table S14 Regression and SEM Comparisons

## Overall assessment

The regression-based primary analyses and latent-variable SEM robustness analyses generally agree on the central directions: equity and inclusion are positively associated with organizational identification; organizational identification is positively associated with OCBI and UPB; equity and inclusion have positive indirect associations with UPB through organizational identification; and ethical leadership negatively moderates the OI–UPB association.

This agreement does not make the coefficient magnitudes interchangeable. The regression column contains a combination of unstandardized B coefficients and standardized β coefficients from several designated primary models, whereas the latent SEM column reports standardized β coefficients from simultaneous latent models. Table S14 therefore emphasizes direction and inference rather than numerical equality.

## Hypothesis level conclusions

| Hypothesis-related result | Cross-method conclusion |
|---|---|
| Equity → OI | Positive and statistically supported in both approaches |
| Inclusion → OI | Positive and statistically supported in both approaches |
| OI → OCBI | Positive and statistically supported in both approaches |
| OI → UPB | Positive and statistically supported in both approaches |
| Equity → OI → UPB | Positive; interval excludes zero in both approaches |
| Inclusion → OI → UPB | Positive; interval excludes zero in both approaches |
| OI × Ethical Leadership → UPB | Negative; interval excludes zero in both approaches |
| Relative direct associations | Main positive focal associations are retained, but cross-path inferences are specification-sensitive |

The core H1–H7 directional pattern can therefore be retained when described as statistical associations. The cross-sectional indirect effects must not be presented as causal mediation.

## Results with different inferential conclusions

### Equity → OCBI

The simultaneous HC3 regression estimate is B = −.042, p = .052, whereas the latent SEM estimate is β = −.226 with a BCa 95% CI [−.327, −.121]. The direction agrees, but the significance conclusion differs. Because B and β come from different measurement and structural specifications, the difference cannot be attributed to measurement-error correction alone. The result is `SPECIFICATION-SENSITIVE` and `NOT DIRECTLY COMPARABLE`.

### Inclusion → UPB

The simultaneous HC3 regression estimate is B = −.033, p = .307. The latent SEM reports a negative coefficient, but its own inferential procedures conflict: Wald β = −.101, p = .017, while the BCa estimate is −.097 with a 95% CI [−.190, .003]. The SEM result must not be labeled simply significant. It is `INFERENCE-SENSITIVE`, `SPECIFICATION-SENSITIVE`, and `NOT DIRECTLY COMPARABLE`.

### OI → UPB at high ethical leadership

The manuscript and existing Supplementary Table S3 report a significant regression simple slope, B = .111, 95% CI [.040, .182]. The latent SEM estimate is β = .084, 95% BCa CI [−.012, .188], which includes zero. Both approaches indicate attenuation, but they differ on whether the high-EL association is distinguishable from zero. The exact saved numerical output producing the reported regression confidence limits was not located, so the regression cell remains `UNVERIFIED` in the traceability file.

### Inclusion conditional indirect association at high ethical leadership

The regression-based PROCESS Model 14 estimate is B = .042, 95% bootstrap CI [.012, .073], whereas the latent PI SEM estimate is β = .027, 95% BCa CI [−.003, .063]. This result is `INFERENCE-SENSITIVE` and `NOT DIRECTLY COMPARABLE`. The common directional buffering pattern can be retained, but significance at high EL is method-dependent.

## Why differences cannot be assigned solely to measurement error

The approaches differ in more than their treatment of measurement error:

- Equity → OI and Inclusion → OI were estimated in separate regression mediation models but simultaneously in the latent SEM.
- The direct-effect regressions used observed composites, HC3 standard errors, and no latent measurement model.
- The regression indirect effects and PROCESS conditional indirect effects used bootstrap procedures that differ from the SEM BCa procedure.
- The latent interaction used a matched-pairs, double-mean-centered, unconstrained product-indicator approximation.
- Some regression entries are B, whereas the SEM entries are β.

Consequently, a disagreement is evidence of sensitivity to the combined specification and inferential framework, not a clean estimate of the effect of measurement-error correction.

## Conclusions that can be retained

The manuscript can retain the following bounded conclusions:

1. Equity and inclusion are each positively associated with organizational identification.
2. Organizational identification is positively associated with both OCBI and UPB, with a stronger standardized association with OCBI in the designated simultaneous regression path model.
3. Equity and inclusion each show positive statistical indirect associations with UPB through organizational identification; their indirect effects should not be ranked because their difference is not significant.
4. Inclusion is more strongly associated with OCBI and equity is more strongly associated with UPB in the formal direct-effect contrasts, but the component cross-path coefficients are sensitive to correlated predictors and model specification.
5. Ethical leadership attenuates the OI–UPB association. Whether the remaining association and the inclusion conditional indirect association are significant at high EL depends on the estimation approach.
6. Nonsignificant public/private path differences do not establish that the sectors are identical.

## Claims requiring correction or restraint

- Do not describe Equity → OCBI as significant in the current regression result; B = −.042, p = .052.
- Do not describe latent Inclusion → UPB as unambiguously significant; its BCa interval contains zero.
- Distinguish the negative interaction from the significance of a simple slope at a particular EL level.
- Do not present the indirect effects as causal mechanisms in cross-sectional data.
- Do not compare B and β magnitudes directly.

## Additional analysis requirement

No additional analysis is required to draft Tables S13 and S14. A limited reproduction of the regression simple-slope confidence intervals would be needed only to upgrade the two regression simple-slope traceability rows from `UNVERIFIED` to `VERIFIED`.
