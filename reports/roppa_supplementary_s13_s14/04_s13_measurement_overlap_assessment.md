# Assessment of Table S13 Measurement Overlap Sensitivity

## Conclusion

The item-exclusion evidence is **PARTIALLY ROBUST**. Removing either Y8_4 from perceived equity or Y11_1 from ethical leadership left the direction and approximate magnitude of the focal structural estimates intact, and the OI × ethical leadership interaction remained negative under every specification. The evidence does not justify replacing the original scales. It supports the narrower conclusion that the focal estimates are not driven solely by either potentially overlapping item.

## Model comparability

The three structural models used the same N = 2,020 cases, the same six latent constructs, the same structural equations, and the same controls for gender, age, and organizational sector. Only the designated measurement indicator was removed. The original, Y8_4-exclusion, and Y11_1-exclusion structural models all converged.

The interaction estimates came from a separate latent product-indicator model. The original and Y8_4-exclusion models used five matched product indicators. Excluding Y11_1 reduced ethical leadership to four indicators and therefore reduced the interaction factor to four matched product indicators. This is a necessary measurement change and should be disclosed; it prevents describing the three interaction models as literally identical measurement specifications.

## Measurement model results

| Specification | CFI | TLI | RMSEA | SRMR | Relevant AVE | Relevant CR |
|---|---:|---:|---:|---:|---|---|
| Original | .9404 | .9336 | .0470 | .0414 | Equity .647; EL .721 | Equity .902; EL .928 |
| Excluding Y8_4 | .9405 | .9334 | .0471 | .0414 | Equity .638 | Equity .875 |
| Excluding Y11_1 | .9385 | .9311 | .0479 | .0414 | EL .734 | EL .917 |

All retained constructs had four or more indicators, AVE above .50, and CR above .70. Removing Y8_4 did not materially improve fit and slightly reduced equity reliability and convergent validity. Removing Y11_1 increased EL AVE but slightly reduced global CFI and TLI. Neither deletion produced a clearly superior measurement model.

## Structural stability

Across the three structural models:

- Equity → OI ranged from β = .286 to .310.
- Inclusion → OI ranged from β = .302 to .317.
- Equity → UPB ranged from β = .269 to .309.
- Inclusion → OCBI ranged from β = .437 to .438.
- OI → UPB ranged from β = .170 to .183.
- OI × EL → UPB ranged from β = −.086 to −.090.

No focal coefficient reversed direction. The deletion-specification interaction Wald tests remained statistically significant. The original interaction also had a formal BCa 95% CI [−.148, −.022].

## Indirect associations

The deletion-model indirect point estimates were computed as products of standardized component paths and were close to the original estimates:

- Equity → OI → UPB: .052, .053, and .052.
- Inclusion → OI → UPB: .058, .051, and .058.

These are descriptive point-estimate comparisons. The deletion models were not bootstrapped for the indirect effects, so their confidence intervals and inferential status are `UNVERIFIED`. The original model's formal BCa intervals excluded zero for both equity [.030, .082] and inclusion [.033, .089].

## Why the classification is not fully robust

The numerical stability is strong, but two limitations prevent a full `ROBUST` classification:

1. BCa or percentile confidence intervals were not generated for the deletion-model structural paths, interactions, or indirect effects.
2. The Y11_1-exclusion interaction factor used four rather than five product indicators.

These limitations concern inferential replication and measurement equivalence, not an observed reversal of the focal pattern.

## Reproducibility evidence

- Model generation and estimation: `code/41_roppa_critical_revision.py`
- Structural fit: `reports/roppa_critical_revision/tables/item_deletion_sem_fit.csv`
- Structural paths: `reports/roppa_critical_revision/tables/item_deletion_sem_paths.csv`
- Interaction sensitivity: `reports/roppa_critical_revision/tables/item_deletion_pi_moderation.csv`
- Measurement quality: `reports/roppa_critical_revision/tables/item_deletion_validity.csv`
- Execution record: `reports/roppa_critical_revision/logs/41_roppa_critical_revision.log`

No additional model was estimated for the present audit.
