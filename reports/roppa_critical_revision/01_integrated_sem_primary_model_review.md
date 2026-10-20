# 01. 통합 SEM의 주분석 적합성 검토

## 판정

**PRIMARY_MODEL_READY_WITH_LIMITATIONS**

기존 통제변수 포함 6요인 잠재변수 SEM을 H1~H6의 주분석으로, 곱셈지표(product-indicator, PI) 잠재상호작용 SEM을 H7의 사전 지정 확장모형으로 사용하는 것이 가능하다. 다만 현재 원고는 별도 OLS·단순매개·PROCESS 결과를 본문 중심에 두고 있고 가설 번호도 H1~H6만 사용하므로, 결과 선택이 아니라 **분석 체계와 번호를 통합 SEM 기준으로 재정렬**해야 한다.

## 조사한 기존 자료

- 자료: `raw/raw_data.sav`(2,020명, 137변수), `processed/analysis_data.csv`(2,020명, 42개 원래 열; 이번 실행 중 파생 통제변수 3개 추가)
- 통합 측정·구조모형: `code/23_sem01_measurement_model_cfa.py`~`code/33_sem11_multigroup_structural.py`
- 핵심 결과: `results/sem/00_SEM_MASTER_SUMMARY.md`, `sem03_controls_multicollinearity_result.md`, `sem06_bca_h4_result.md`, `sem07_mediation_result.md`, `sem09_h7_product_indicator_result.md`
- 기존 원고: `output/final/final_manuscript.md`
- 심사평 원문과 Figure 1 이미지 파일은 프로젝트에서 발견하지 못했다. Figure 1 일치 여부는 원고의 텍스트 연구모형과 요청서에 열거된 경로를 기준으로 판정했다.

## 기존 SEM 구조와 Figure 1 대응

통제변수 포함 구조모형은 다음을 한 모형에서 추정한다.

- 측정요인: equity, inclusion, OI, ethical leadership(EL), OCBI, UPB
- `OI ~ equity + inclusion + male + age + public`
- `UPB ~ OI + equity + inclusion + EL + male + age + public`
- `OCBI ~ OI + equity + inclusion + EL + male + age + public`
- equity와 inclusion 등 외생 잠재변수의 공분산은 SEM 기본 구조에서 추정된다.
- OCBI와 UPB의 잔차상관은 별도 합성점수 병렬모형에서는 허용되나, 현재 잠재 구조모형 명세에는 명시적 잔차상관이 없다. 연구 질문상 필수 경로는 아니지만 Methods에 명세를 정확히 밝혀야 한다.

H7은 같은 측정구조에 OI×EL 잠재요인을 추가한 PI 모형으로 추정되어 있다. 따라서 모든 효과가 단 하나의 수치적 모형에서 동시에 산출된 것은 아니지만, 동일 자료·동일 구성개념·동일 통제를 공유하는 **기본 통합 SEM + 사전 지정 잠재상호작용 확장 SEM** 체계이다. Figure 1의 실질 경로와는 일치한다.

기본모형 적합도는 χ²(448)=2448.56, CFI=.9404, TLI=.9336, RMSEA=.0470, SRMR=.0414였다. H7 PI 모형은 χ²(608)=2799.86, CFI=.9403, TLI=.9343, RMSEA=.0423이었다.

## 요청서 기준 H1~H7 검증 가능성

요청서가 전제하는 H1~H7은 현재 원고의 H1~H6 번호와 다르다. 아래는 요청서·SEM 산출물의 7개 효과 체계로 정리한 결과다.

| 가설 | 통합 결과 | 불확실성 | 판정 |
|---|---:|---|---|
| H1 Equity→OI (+) | β=.286 | Wald p<.001 | SUPPORTED |
| H2 Inclusion→OI (+) | β=.317 | Wald p<.001 | SUPPORTED |
| H3 OI→OCBI 및 OI→UPB (+), 크기 차이 | .287, .182; 차이=.105 | 1,000회 percentile CI [.007,.205] | SUPPORTED |
| H4 차별적 직접효과 | Inclusion→OCBI .437; Equity→UPB .269 | d_OCBI=.663, BCa [.493,.819]; d_UPB=.366, BCa [.182,.541] | SUPPORTED, 단 억제효과 해석 제한 |
| H5 Equity→OI→UPB | 간접효과=.052 | BCa [.030,.082] | SUPPORTED |
| H6 Inclusion→OI→UPB | 간접효과=.058 | BCa [.033,.089] | SUPPORTED |
| H7 OI×EL→UPB | β=-.087 | BCa [-.148,-.022] | SUPPORTED |

H3의 잠재계수 차이는 이번 제한적 재분석에서 1,000회 사례 부트스트랩으로 추가했다(`tables/latent_h3_path_difference_bootstrap.csv`). 2,000회 실행은 환경의 10분 제한으로 결과 저장 전 종료되어 1,000회로 재실행했으며 1,000회 모두 수렴했다.

H5와 H6의 두 간접효과 차이는 -.006, BCa 95% CI [-.035,.024]로 유의하지 않다. 두 간접효과는 각각 유의하지만 어느 하나가 더 강하다는 서열 주장은 지지되지 않는다.

## 기존 결과와 통합 SEM의 차이

| 효과 | 기존 원고의 분리 분석 | 통합 잠재 SEM | 판단 |
|---|---:|---:|---|
| Equity→OI | β=.393 | β=.286 | 측정오차 보정·동시투입 사양 차이. SEM을 정본으로 사용 |
| Inclusion→OI | β=.429 | β=.317 | 동일 |
| OI→UPB | β=.150이라고 표기 | β=.182 | 원고 값은 실제로 비표준화 B=.150. 표기 수정 필요 |
| OI→OCBI | β=.217이라고 표기 | β=.287 | 원고 값은 합성점수 모형 값. SEM 기준으로 교체 |
| Inclusion→UPB | 합성점수 B=-.033, p=.307 | β=-.097, Wald p=.024; BCa [-.190,.003] | bootstrap 기준 경계적·비유의로 판정 |
| H7 상호작용 | 합성점수 β≈-.065 | 잠재 PI β=-.087, BCa [-.148,-.022] | 방향·결론 일치 |
| 높은 EL의 OI→UPB | 기존 OLS에서 유의 | PI SEM .084, BCa [-.012,.188] | 유의성을 잃을 정도로 약화된 것으로 수정 |

## 주분석 사용 권고

통합 SEM을 주분석으로 사용할 수 있다. 권장 구조는 다음과 같다.

1. 6요인 CFA와 통제변수 포함 잠재 구조모형을 H1~H6의 단일 정본으로 제시한다.
2. H7은 PI 잠재상호작용 확장모형으로 명시하고, 조건부 간접효과도 이 모형에서만 판단한다.
3. 위계적 HC3 OLS, 개별 단순매개, PROCESS 유사 모형, 합성점수 대비는 보충자료의 강건성 분석으로 이동한다.
4. 같은 경로에 서로 다른 계수를 섞지 말고 각 표의 B/β, 추정법, 통제변수, CI 종류를 표 주석에 명시한다.

## Methods와 Results 수정사항

- Methods에 기본 SEM과 PI 확장 SEM의 정확한 방정식, 통제변수, 추정법, 표준화 방식, 부트스트랩 반복 수를 쓴다.
- H1~H7 번호를 하나로 확정한다. 현재 원고는 H1~H6이고 SEM 산출물은 H7을 조절가설로 부르므로 그대로 제출하면 안 된다.
- Results는 통합 SEM 표 하나를 중심으로 직접·간접·대비를 보고하고, H7 표를 별도로 둔다.
- Wald p와 BCa CI가 충돌하는 Inclusion→UPB는 BCa CI를 우선해 “경계적이며 0을 포함”으로 보고한다.
- H7의 높은 EL 조건은 “효과가 완전히 제거됐다”가 아니라 “점추정치는 양수지만 CI가 0을 포함할 정도로 약화됐다”고 쓴다.

## 남은 한계

- semopy의 PI 모형은 비제약 matched-pairs 근사이며 Mplus LMS와 동일하지 않다.
- H3 차이의 새 CI는 계산 제한 때문에 1,000회 percentile이며 기존 BCa 결과보다 근거 수준이 낮다.
- Figure 1 원본과 심사평 원문이 없어 그래픽·문구 단위의 완전 대조는 하지 못했다.
- 횡단면 자기보고 자료이므로 매개를 인과적 심리 메커니즘의 입증으로 표현할 수 없다.
