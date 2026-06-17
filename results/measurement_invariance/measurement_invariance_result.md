# Measurement Invariance: Public vs. Private Sector (Configural / Metric / Scalar)

## 0. 분석 표본

- 공공(public): n = 1012
- 민간(private): n = 1008
- 항목 수: 29개 (6요인: equity, inclusion, oi, el, ocb, upb)

## 1. 방법론 노트

semopy는 lavaan 식의 다집단 동일성 제약(group.equal)을 직접 지원하지 않으므로,
두 집단의 파라미터를 직접 매핑한 결합 목적함수(가중합 MLW discrepancy function)를
공동 최적화하는 방식으로 동일성 제약을 구현하였다. Configural/Metric 단계는
순수 공분산구조모형(절편은 양쪽 집단에서 자유추정·포화되어 평균구조의 적합도
기여가 0이 되는 표준적 관행과 일치)으로, Scalar 단계는 절편을 두 집단 간 동일하게
제약한 평균+공분산 결합 ML 판별함수(Bollen, 1989의 augmented ML fit function)로
추정하였다(해석적 기울기는 수치미분으로 검증함).

## 2. 적합도 지표

| Model                 |    chi2 |   df |   CFI |   TLI |   RMSEA |   SRMR |
|:----------------------|--------:|-----:|------:|------:|--------:|-------:|
| Configural Invariance | 2355.72 |  724 | 0.95  | 0.944 |   0.033 |  0.043 |
| Metric Invariance     | 2426.59 |  747 | 0.949 | 0.944 |   0.033 |  0.044 |
| Scalar Invariance     | 3032.06 |  776 | 0.931 | 0.928 |   0.038 |  0.044 |

## 3. 단계 간 비교 (Cheung & Rensvold, 2002 기준: ΔCFI ≤ .01)

| Comparison           |    Δχ² |   Δdf |   ΔCFI |   ΔTLI |   ΔRMSEA |   ΔSRMR | Invariance 판정 (Cheung & Rensvold, 2002)   |
|:---------------------|-------:|------:|-------:|-------:|---------:|--------:|:--------------------------------------------|
| Metric vs Configural |  70.87 |    23 | -0.001 |  0     |   -0     |   0.001 | 지지됨 (ΔCFI ≤ .01)                         |
| Scalar vs Metric     | 605.47 |    29 | -0.018 | -0.016 |    0.005 |  -0     | 지지되지 않음 (ΔCFI > .01)                  |

- 요인동일성(Metric) 지지 여부: 지지됨
- 절편동일성(Scalar) 지지 여부: 지지되지 않음

## 4. SSCI Results 섹션 문단 (한국어, 바로 삽입 가능)

공공조직 종사자(n=1012)와 민간기업 종사자(n=1008) 간
측정동일성(measurement invariance)을 검증하기 위해 형태동일성(configural),
요인동일성(metric), 절편동일성(scalar)의 3단계 다집단 확인적 요인분석(multi-group CFA)을
순차적으로 실시하였다.

형태동일성 모형은 두 집단에서 동일한 6요인 구조(형평성 분위기, 포용성 분위기,
조직동일시, 윤리적 리더십, 조직시민행동, 비윤리적 친조직행동)를 자유롭게 추정한
모형으로, χ²(724) = 2355.72,
CFI = 0.950, TLI = 0.944,
RMSEA = 0.033, SRMR = 0.043로
양호한 적합도를 보였다.

요인동일성 모형은 형태동일성 모형에 모든 비기준(non-marker) 항목의 요인적재량을
두 집단 간 동일하게 제약한 모형으로, χ²(747) = 2426.59,
CFI = 0.949, RMSEA = 0.033,
SRMR = 0.044로 나타났다. 형태동일성 모형과 비교한 결과
ΔCFI = -0.001, ΔRMSEA = -0.000,
ΔSRMR = 0.001로, Cheung과 Rensvold(2002)의 기준(ΔCFI ≤ .01)에
따라 요인동일성이 지지되었다.

절편동일성 모형은 요인동일성 모형에 모든 항목의 절편(intercept)을 두 집단 간
동일하게 추가 제약한 모형으로, χ²(776) = 3032.06,
CFI = 0.931, RMSEA = 0.038,
SRMR = 0.044로 나타났다. 요인동일성 모형과 비교한 결과
ΔCFI = -0.018, ΔRMSEA = 0.005,
ΔSRMR = -0.000로, Cheung과 Rensvold(2002)의 기준에 따라
절편동일성이 지지되지 않았다.

종합적으로 두 집단 간 형태동일성과 요인동일성이 모두 확보되어, 공공-민간 비교에 필요한 최소 조건인 요인동일성(metric invariance)을 만족하므로 두 집단 간 구조적 경로계수(회귀계수) 비교가 통계적으로 정당화된다.
절편동일성은 완전한 형태로 지지되지 않았으므로, 두 집단 간 잠재평균 비교(예: 공공-민간 조직동일시 수준 차이)는 신중하게 해석하거나 부분 절편동일성 모형을 통해 보완할 필요가 있다. 다만 경로계수(회귀/공분산 구조) 비교는 절편동일성과 무관하게 요인동일성만으로 정당화된다(Vandenberg & Lance, 2000).

## 5. APA7 표

**Table X**

*Measurement Invariance Test Across Public and Private Sector Employees*

| Model                 |    chi2 |   df |   CFI |   TLI |   RMSEA |   SRMR |
|:----------------------|--------:|-----:|------:|------:|--------:|-------:|
| Configural Invariance | 2355.72 |  724 | 0.95  | 0.944 |   0.033 |  0.043 |
| Metric Invariance     | 2426.59 |  747 | 0.949 | 0.944 |   0.033 |  0.044 |
| Scalar Invariance     | 3032.06 |  776 | 0.931 | 0.928 |   0.038 |  0.044 |

*Note.* CFI = comparative fit index; TLI = Tucker-Lewis index; RMSEA = root mean square error of approximation; SRMR = standardized root mean square residual.

**Table X+1**

*Nested Model Comparisons for Measurement Invariance (Cheung & Rensvold, 2002)*

| Comparison           |    Δχ² |   Δdf |   ΔCFI |   ΔTLI |   ΔRMSEA |   ΔSRMR | Invariance 판정 (Cheung & Rensvold, 2002)   |
|:---------------------|-------:|------:|-------:|-------:|---------:|--------:|:--------------------------------------------|
| Metric vs Configural |  70.87 |    23 | -0.001 |  0     |   -0     |   0.001 | 지지됨 (ΔCFI ≤ .01)                         |
| Scalar vs Metric     | 605.47 |    29 | -0.018 | -0.016 |    0.005 |  -0     | 지지되지 않음 (ΔCFI > .01)                  |

*Note.* Invariance is supported when ΔCFI ≤ .01 (Cheung & Rensvold, 2002).
