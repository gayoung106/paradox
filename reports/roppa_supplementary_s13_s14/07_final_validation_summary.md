# Final Validation Summary for Supplementary Tables S13 and S14

## Final status

**READY_WITH_DOCUMENTED_LIMITATIONS**

Tables S13 and S14 are complete as insertion-ready English Markdown drafts. All displayed estimates are tied to an existing code or output source. No source manuscript, supplement, code, raw data, or existing result file was modified. No model was re-estimated for this task.

## Completion checklist

| Item | Status | Result |
|---|---|---|
| Table S13 completed | Yes | Three item specifications, structural estimates, latent interaction, descriptive indirect estimates, model fit, and full note included |
| Table S14 completed | Yes | Direct, indirect, moderation, simple-slope, and conditional indirect panels included |
| Existing results reused | Yes | Existing regression, mediation, PROCESS, SEM, item-deletion, manuscript, and supplementary outputs used |
| Reanalysis executed | No | Not required for table drafting |
| B and β separated | Yes | Coefficient type is explicit in every table cell or note |
| Wald/BCa conflict disclosed | Yes | Inclusion → UPB classified as inference-sensitive |
| Different model specifications disclosed | Yes | Regression submodels and separate latent interaction model identified |
| Source traceability completed | Yes | Required 15-field CSV created |

## Table S13 validation

- N = 2,020 in all three structural specifications.
- The original, Y8_4-exclusion, and Y11_1-exclusion models converged.
- Only the designated measurement item was removed from the structural models.
- The focal structural coefficients retained their direction.
- OI × EL remained negative: β = −.087, −.090, and −.086.
- Measurement quality remained acceptable after either deletion.
- The Y11_1-exclusion interaction model necessarily used four rather than five matched product indicators.
- Deletion-model bootstrap confidence intervals were not produced.
- Final S13 conclusion: **PARTIALLY ROBUST**.

## Table S14 validation

The following conclusions were consistent across regression-based and latent-variable analyses:

- Equity → OI was positive.
- Inclusion → OI was positive.
- OI → OCBI and OI → UPB were positive.
- Equity and inclusion each had a positive indirect association with UPB through OI.
- OI × ethical leadership was negative.
- The equity conditional indirect association at high EL included zero under both approaches.

The following conclusions were sensitive:

- Equity → OCBI: regression B = −.042, p = .052; latent SEM β = −.226, BCa CI [−.327, −.121].
- Inclusion → UPB: regression B = −.033, p = .307; latent SEM Wald p = .017 but BCa CI [−.190, .003].
- OI → UPB at high EL: reported regression CI excludes zero; latent SEM BCa CI [−.012, .188] includes zero.
- Inclusion conditional indirect association at high EL: regression bootstrap CI [.012, .073] excludes zero; latent SEM BCa CI [−.003, .063] includes zero.

These differences cannot be assigned solely to measurement-error correction because the models also differ in simultaneous versus separate predictor entry, coefficient scale, structural specification, and inferential method.

## Unverified coefficients

Only two coefficient rows remain `UNVERIFIED`:

1. Regression simple slope of OI → UPB at low EL: B = .230, 95% CI [.158, .298].
2. Regression simple slope of OI → UPB at high EL: B = .111, 95% CI [.040, .182].

The manuscript and existing Supplementary Table S3 agree on these values, but an exact saved numerical output reproducing the confidence limits was not located. The estimates were not replaced with values from a different Model 14 specification.

## Manuscript and supplement inconsistencies

1. Existing Supplementary Table S12 incorrectly describes a mixed set of B, β, and Δβ values as standardized coefficients unless otherwise indicated.
2. Manuscript Table 3 reports `.001` for Age in Models 3 and 4; the saved output is approximately B = −.007, p = .001 in both models.
3. Manuscript Table 4 reports OI → OCBI as `.215**`; the saved HC3 output is B = .2155, p < .001 and therefore requires `***` under the stated convention.
4. The online supplement carries an older title that does not match `manuscript_261020.docx`.
5. The manuscript discusses the Y8_4/Y11_1 sensitivity and regression/SEM differences but does not yet cite Tables S13 and S14.

## Additional analysis requirement

No additional analysis is required for supplementary insertion with documented limitations. A limited reproduction of the designated moderation model's simple-slope confidence intervals is recommended only if the two `UNVERIFIED` rows must be upgraded before submission.

## Files produced

- `01_table_s13_measurement_overlap.md`
- `02_table_s14_regression_sem_comparison.md`
- `03_s13_s14_coefficient_traceability.csv`
- `04_s13_measurement_overlap_assessment.md`
- `05_s14_model_comparison_assessment.md`
- `06_manuscript_as_is_to_be.md`
- `07_final_validation_summary.md`
