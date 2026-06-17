# Indirect Effect Comparison: Inclusion vs. Equity Climate via Organizational Identification

## 0. 분석 표본 및 모형

- 표본 크기: N = 2020
- 통제변수: gender, age, organization_type
- 동시추정 모형: M ~ Inclusion + Equity + controls (HC3); UPB ~ OI + Inclusion + Equity + controls (HC3)
- 부트스트랩: 10,000회, 케이스 재표집, Bias-corrected(BC) 95% CI

## 1. 경로 추정치 (원자료, HC3 robust)

- a1 (Inclusion → OI) = 0.2534
- a2 (Equity → OI) = 0.2269
- b (OI → UPB) = 0.1498

## 2. 간접효과 비교 결과

| Path                            |   Indirect Effect |    SE | 95% CI          |
|:--------------------------------|------------------:|------:|:----------------|
| Inclusion → OI → UPB            |             0.038 | 0.008 | [0.023, 0.056]  |
| Equity → OI → UPB               |             0.034 | 0.008 | [0.020, 0.051]  |
| Difference (Inclusion - Equity) |             0.004 | 0.007 | [-0.009, 0.018] |
| Ratio (Inclusion / Equity)      |             1.117 | 0.223 | [0.763, 1.615]  |

- Difference 95% CI에 0 포함 여부: 포함함 (통계적으로 비유의)
- 표준화 효과크기 (Diff / SE_diff): 0.568

## 3. SSCI Results 섹션 문단 (영문, 바로 삽입 가능)

To formally test the claim that the indirect transmission effect of inclusion climate on
unethical pro-organizational behavior (UPB) through organizational identification (OI) is
larger than that of equity climate, we estimated both indirect effects within a single
mediation model that simultaneously included inclusion climate and equity climate as
predictors of OI (controlling for gender, age, and organization type [public/private]),
and OI together with both climate variables as predictors of UPB (also controlling for
gender, age, and organization type). This joint specification allowed both indirect effects
to be evaluated from the same bootstrap resamples, which is required to validly test their
difference.

The indirect effect of inclusion climate on UPB through OI was 0.038
(bootstrap SE = 0.008, 95% bias-corrected CI [0.023, 0.056]),
and the indirect effect of equity climate on UPB through OI was 0.034
(bootstrap SE = 0.008, 95% bias-corrected CI [0.020, 0.051]). Both
indirect effects were estimated using 10,000 bootstrap resamples (n valid = 10,000).

A direct test of the difference between the two indirect effects
(Inclusion − Equity = 0.004, bootstrap SE = 0.007) yielded a 95%
bias-corrected bootstrap confidence interval of [-0.009, 0.018], which
included zero. The ratio of the two indirect effects was
1.12 (95% bias-corrected CI [0.76, 1.62]), and the
standardized effect-size index for the difference (Diff / bootstrap SE) was 0.57.
These results indicate that the indirect effect of inclusion climate on UPB via
organizational identification was not significantly different from that of equity climate.

## 4. SSCI Discussion 섹션 문단 (영문, 바로 삽입 가능)

Although the present study's central narrative emphasizes that inclusion climate carries a
numerically larger indirect effect on unethical pro-organizational behavior (UPB) through
organizational identification (0.038) than equity climate
(0.034), a formal bootstrap test indicated that this difference
(95% CI [-0.009, 0.018]) was not statistically distinguishable from
zero. This null result does not undermine the theoretical contribution of the paper; rather,
it refines it.

First, both indirect effects were positive and their confidence intervals excluded zero,
confirming that organizational identification is a robust transmission mechanism through
which both facets of DEI climate -- inclusion and equity -- can give rise to the
identification-driven dark side of inclusive culture. The core paradox the paper advances
(that DEI-oriented climates can indirectly elevate UPB via organizational identification)
therefore holds for both facets, which if anything strengthens the generality of the
proposed mechanism rather than narrowing it to a single DEI dimension.

Second, rather than framing inclusion and equity as divergent in their transmission strength,
the results are more consistent with the interpretation that inclusion and equity climate
operate as complementary facets of a broader DEI climate that converge on a common
identification-based pathway, consistent with prior work treating equity and inclusion as
distinguishable but related organizational climate dimensions (as established in this
study's own two-factor CFA, CFI = .962, TLI = .947). The practical implication shifts from
"inclusion is the primary driver to monitor" to "any DEI climate dimension that strengthens
organizational identification carries a latent ethical risk that organizations must manage
jointly, for example through ethical leadership," which is arguably a more actionable and
theoretically parsimonious contribution than asserting a strength ordering between the two
facets that the data do not statistically support.

Future research with larger samples or a meta-analytic synthesis across organizational
contexts may be better powered to detect a true but small difference between the inclusion
and equity transmission pathways, should one exist.

## 5. APA7 표

**Table X**

*Indirect Effects Comparison: Inclusion Climate vs. Equity Climate via Organizational Identification*

| Path                            |   Indirect Effect |    SE | 95% CI          |
|:--------------------------------|------------------:|------:|:----------------|
| Inclusion → OI → UPB            |             0.038 | 0.008 | [0.023, 0.056]  |
| Equity → OI → UPB               |             0.034 | 0.008 | [0.020, 0.051]  |
| Difference (Inclusion - Equity) |             0.004 | 0.007 | [-0.009, 0.018] |
| Ratio (Inclusion / Equity)      |             1.117 | 0.223 | [0.763, 1.615]  |

*Note.* Indirect effects estimated from a joint mediation model (M ~ Inclusion + Equity + gender + age + organization_type; UPB ~ OI + Inclusion + Equity + gender + age + organization_type), with 10,000 case-resampling bootstrap iterations and bias-corrected (BC) 95% confidence intervals. Path coefficients for the joint model were estimated with HC3 heteroskedasticity-robust standard errors. Difference = Indirect(Inclusion) - Indirect(Equity); Ratio = Indirect(Inclusion) / Indirect(Equity).
