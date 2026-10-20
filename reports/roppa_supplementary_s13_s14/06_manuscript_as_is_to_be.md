# Manuscript and Supplement AS IS TO BE Corrections

The locations and quotations below were verified against `manuscript_261020.docx` and `0824_Online supplemental_Paradox Good Organizational Culture (1).docx`. Neither document was modified.

## 1 Add the Table S13 cross reference

- **Exact location:** Manuscript, Results, Section 4.5, final paragraph beginning `Additional sensitivity analyses examined the potential content overlap between perceived equity and ethical leadership.`
- **Searchable existing sentence:** `These results suggest that the focal findings were not driven solely by either item. Nevertheless, the analyses do not eliminate concerns regarding conceptual overlap between the two constructs.`
- **AS-IS:** The paragraph does not identify a supplementary table containing the numerical results.
- **TO-BE:** `These results suggest that the focal findings were not driven solely by either item. Nevertheless, the analyses do not eliminate concerns regarding conceptual overlap between the two constructs. Detailed item-exclusion results are reported in Supplementary Table S13.`
- **Reason:** Table S13 supplies the numerical structural, interaction, fit, and measurement-quality evidence underlying the narrative.
- **Evidence:** Table S13, Panels A–C and Model Information; `reports/roppa_critical_revision/tables/item_deletion_sem_paths.csv`; `item_deletion_pi_moderation.csv`; `item_deletion_sem_fit.csv`.
- **Status:** **VERIFIED**

## 2 Add the Table S14 cross reference

- **Exact location:** Manuscript, Results, Section 4.5, paragraph ending `Detailed latent-variable results are reported in Supplementary Appendix B.`
- **Searchable existing sentence:** `Overall, the focal directions and the ethical leadership interaction were generally robust to latent-variable estimation, although some direct and conditional indirect effects at high levels of ethical leadership were sensitive to the estimation and inferential procedures used.`
- **AS-IS:** The manuscript summarizes the comparison but does not direct readers to a side-by-side table.
- **TO-BE:** `Overall, the focal directions and the ethical leadership interaction were generally robust to latent-variable estimation, although some direct and conditional indirect effects at high levels of ethical leadership were sensitive to the estimation and inferential procedures used. A side-by-side comparison of the regression-based and latent-variable estimates is reported in Supplementary Table S14.`
- **Reason:** Table S14 makes the B/β, specification, and inferential differences explicit without replacing the regression-based primary analyses.
- **Evidence:** Table S14, Panels A–C.
- **Status:** **VERIFIED**

## 3 Correct the mixed coefficient note in Supplementary Table S12

- **Exact location:** Existing online supplement, Supplementary Appendix F, Table S12 note.
- **Searchable existing sentence:** `Unless otherwise indicated, entries are standardized coefficients.`
- **AS-IS:** `Note. UPB5 denotes the original five-item measure; UPB4 denotes the four-item sensitivity measure excluding Y20_4. Unless otherwise indicated, entries are standardized coefficients.`
- **TO-BE:** `Note. UPB5 denotes the original five-item measure; UPB4 denotes the four-item sensitivity measure excluding Y20_4. Equity → UPB, Inclusion → UPB, the two indirect effects, and OI × EL are unstandardized coefficients (B). OI → UPB and OI→OCBI − OI→UPB are standardized coefficients (β and Δβ, respectively). Entries labeled Latent are standardized coefficients (β). The four-item specification was used only as a sensitivity analysis; the five-item measure remains the primary specification.`
- **Reason:** Table S12 mixes B, β, and Δβ. The existing blanket statement misclassifies the regression direct, indirect, and interaction coefficients. Table S14 uses explicit cell-level coefficient labels and should be consistent with S12.
- **Evidence:** Table S14 notes; `results/tables/table5_dei_oi_direct_effects.csv`; `results/indirect_effect_comparison/indirect_effect_comparison.csv`; `results/moderation/moderation_result.md`; `results/oi_duality_parallel_mediation/duality_test.csv`; `results/sem/sem09_h7_product_indicator_result.csv`.
- **Status:** **VERIFIED**

## 4 Correct the age cells in Manuscript Table 3

- **Exact location:** Manuscript, Results, Table 3, `Age` row, Models 3 and 4.
- **Searchable existing row:** `Age    -.002    -.003    .001    .001`
- **AS-IS:** Model 3 = `.001`; Model 4 = `.001`.
- **TO-BE:** Model 3 = `−.007 (p = .001)`; Model 4 = `−.007 (p = .001)`; assign significance symbols from the unrounded p values used by the table-generation rule.
- **Reason:** The saved HC3 regression output reports B = −.0066 and −.0065, respectively. The manuscript cells have the wrong sign and magnitude.
- **Evidence:** `code/05_regression_upb.py`; `results/regression/regression_upb.md`; Table S14 uses the same corrected control-variable coding context.
- **Status:** **VERIFIED** for B and displayed p; **UNVERIFIED** for whether the intended star rule treats the unrounded Model 3 p as below .001 because the table-generation output was not saved.

## 5 Correct the significance marker in Manuscript Table 4

- **Exact location:** Manuscript, Results, Table 4, `Organizational Identification` row, OCBI column.
- **Searchable existing cell:** `.215**`
- **AS-IS:** `.215**`
- **TO-BE:** `.215***`
- **Reason:** The current HC3 OCBI Model 3 estimate is B = .2155, SE = .024, p < .001. Table S14 reports this regression family as the observed-score direct-association specification.
- **Evidence:** `code/11_regression_ocb.py`; `code/22_table5_dei_oi_direct_effects.py`; `results/ocb_regression/ocb_regression_result.md`; `results/tables/table5_dei_oi_direct_effects.csv`.
- **Status:** **VERIFIED**

## 6 Preserve the qualified Inclusion to UPB SEM wording

- **Exact location:** Manuscript, Results, Section 4.5, paragraph beginning `One exception involved the latent inclusion→UPB path`.
- **Searchable existing sentence:** `We therefore treat this as a borderline finding whose statistical significance depends on the inferential procedure used.`
- **AS-IS:** The current sentence already reports Wald β = −.101, p = .017 and BCa β = −.097, 95% CI [−.190, .003].
- **TO-BE:** No numerical change. Retain the current sentence and link it to Supplementary Table S14.
- **Reason:** Table S14 confirms that this result is `INFERENCE-SENSITIVE`; replacing the qualified wording with “significant in SEM” would be inaccurate.
- **Evidence:** Table S14, Panel A; `results/sem/sem06_bca_h4_paths.csv`; existing Supplementary Table S5.
- **Status:** **VERIFIED**

## 7 Preserve the qualified high Ethical Leadership interpretation

- **Exact location:** Manuscript, Results, Section 4.5, sentences beginning `The latent OI×ethical leadership interaction was negative` and `At high levels of ethical leadership`.
- **Searchable existing sentence:** `Thus, while both approaches supported a negative interaction, the statistical significance of the association at high levels of ethical leadership differed across estimation approaches.`
- **AS-IS:** The manuscript distinguishes the interaction from the high-EL simple slope and reports the regression/SEM divergence.
- **TO-BE:** No numerical change. Retain the wording and add the Table S14 cross-reference proposed above.
- **Reason:** Table S14 confirms a negative interaction under both methods but an inference-sensitive high-EL simple slope and inclusion conditional indirect association.
- **Evidence:** Table S14, Panel C; `results/moderation/moderation_result.md`; `results/sem/sem09_h7_product_indicator_result.csv`; `results/equity_model14_with_direct/model14_with_direct_conditional_indirect_effects.csv`.
- **Status:** **VERIFIED**, except for the exact regression simple-slope confidence limits described in Item 8.

## 8 Verify rather than silently replace the regression simple slope confidence limits

- **Exact location:** Manuscript, Results, Section 4.3, sentence beginning `The positive association between organizational identification and UPB was stronger`; existing online supplement, Table S3.
- **Searchable existing text:** `B = .230, 95% CI [.158, .298]` and `B = .111, 95% CI [.040, .182]`.
- **AS-IS:** Both the manuscript and Table S3 report these values.
- **TO-BE:** `[No numerical replacement at this stage.] Reproduce the designated interaction model's simple-slope covariance calculation and retain or correct the confidence limits only after matching them to a saved output.`
- **Reason:** The point estimates are compatible with the saved interaction model, but an exact saved numerical output for the reported confidence limits was not located. Other saved Model 14 slope files correspond to different outcome specifications and cannot be substituted.
- **Evidence:** Table S14, Panel C and footnote a; `code/07_moderation.py`; `code/99_reanalysis_gender_age_controls.py`; `results/moderation/moderation_result.md`.
- **Status:** **UNVERIFIED**

## 9 Align the online supplement title with the current manuscript

- **Exact location:** Existing online supplement, title line.
- **Searchable existing text:** `The Paradox of a Good Organizational Culture: Equity, Inclusion, and the Duality of Organizational Identification`
- **AS-IS:** `The Paradox of a Good Organizational Culture: Equity, Inclusion, and the Duality of Organizational Identification`
- **TO-BE:** `The Paradox of Favorable Organizational Perceptions: Equity, Inclusion, and Unethical Pro-Organizational Behavior`
- **Reason:** The online supplement title does not match the title of `manuscript_261020.docx`. Adding Appendices G and H without correcting the title would preserve a document-level version inconsistency.
- **Evidence:** Title text in the two supplied DOCX files.
- **Status:** **VERIFIED**

## Abstract and Discussion check

The current abstract contains no numerical coefficient claims requiring synchronization with Tables S13 or S14. The Discussion already states that the latent-variable results generally reproduced the focal pattern while some direct and high-EL conditional results were estimation-sensitive. No numerical replacement is required there. When Tables S13 and S14 are inserted, a brief supplementary cross-reference may be added to the limitations/robustness discussion, but the current qualified interpretation should be preserved.
