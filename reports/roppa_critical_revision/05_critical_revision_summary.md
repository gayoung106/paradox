# 05. ROPPA 핵심 방법론 검증 종합

## 최종 판정

**READY_FOR_TARGETED_MANUSCRIPT_REVISION**

제한적 재분석으로 심사평의 핵심 방법론 쟁점을 검증했다. 기존 통합 SEM과 PI 잠재상호작용 모형을 주분석 체계로 사용할 수 있고, 추가적인 대규모 분석은 필요하지 않다. 다만 현재 원고의 B/β 오표기, 서로 다른 모형의 계수 혼입, H1~H6/H7 번호 불일치, 간접효과 차이에 대한 과장, 높은 EL 조건의 잘못된 유의성 서술은 원고 수정 전에 반드시 바로잡아야 한다.

## 1. 검증 결과 요약

| 검증 항목 | 기존 분석 활용 가능 | 재분석 수행 | 핵심 결과 | 논문 수정 필요 |
|---|---|---|---|---|
| 통합 잠재 SEM | 예 | H3 잠재계수 차이만 추가 | 적합도 CFI=.940, RMSEA=.047; H1~H6 평가 가능 | 예: 통합 SEM 중심으로 재구성 |
| OI→OCBI 대 OI→UPB | 부분 | 1,000회 bootstrap | .287 vs .182; 차이=.105, CI [.007,.205] | 예: 정본 수치 교체 |
| Equity/Inclusion 억제 | 부분 | A–D HC3 회귀 | Inclusion→UPB .164→.005→-.032; Equity→OCBI .269→.009→-.055 | 예: 조건부 순효과로 제한 |
| H4 직접효과 대비 | 예 | 재실행 안 함 | 잠재 d_OCBI=.663, d_UPB=.366; BCa 모두 0 미포함 | 예: 메커니즘 입증과 구분 |
| H5/H6 동시 간접효과 | 예 | 재실행 안 함 | .052 [.030,.082], .058 [.033,.089]; 차이 ns | 예: 강도 서열 주장 철회 |
| Y8_4/Y11_1 중복 | 기존 타당도 활용 | 두 삭제모형 추정 | 경로·상호작용 안정; 삭제모형 우월성 없음 | 예: 한계·부록 보고 |
| H7 잠재 조절 | 예 | 문항삭제 민감도만 추가 | β=-.087, BCa [-.148,-.022]; 삭제 후 -.090/-.086 | 예: 높은 EL 결과 수정 |
| Y20_4 제외 | 예 | 재실행 안 함 | 기존 Strong robustness; 상호작용 -.087→-.085 | 부록 요약 |
| 추론 일관성 | 부분 | 감사 수행 | Inclusion→UPB Wald 유의, BCa 0 포함 | 예: BCa 기준 경계적 비유의 |
| 측정동일성 | 예 | 재실행 안 함 | metric 확보, scalar 미확보(ΔCFI=-.012) | 예: 잠재평균 해석 금지 |
| 표본·결측·가중치 | 부분 | 메타데이터 감사 | N=2,020 완전; WT 미사용; 직급 부문별 변수 존재 | 예: 비가중 명시·코드북 확인 |

## 2. 가설 유지 가능성

요청서의 H1~H7 분석 체계를 기준으로 판정한다. 현재 원고는 H1~H6만 정의하므로 아래 번호로 개편할지, 기존 원고 번호를 유지하면서 H3/H4의 대비를 보조검정으로 둘지 편집 단계에서 하나를 선택해야 한다.

| 가설 | 요청서 기준 효과 | 판정 | 근거와 해석 한계 |
|---|---|---|---|
| H1 | Equity→OI (+) | SUPPORTED | β=.286, p<.001 |
| H2 | Inclusion→OI (+) | SUPPORTED | β=.317, p<.001 |
| H3 | OI가 OCBI·UPB 모두 증가, OCBI 경로가 더 큼 | SUPPORTED | .287/.182; 차이 CI [.007,.205]. 양면성의 통계적 패턴 지지 |
| H4 | Inclusion은 OCBI, Equity는 UPB와 상대적으로 더 강한 순효과 | SUPPORTED | 두 공식 BCa 대비 유의. 억제에 민감하며 다른 심리 메커니즘 자체는 입증하지 않음 |
| H5 | Equity→OI→UPB | SUPPORTED | 간접=.052, BCa [.030,.082] |
| H6 | Inclusion→OI→UPB | SUPPORTED | 간접=.058, BCa [.033,.089]. H5보다 강하다는 차이는 비유의 |
| H7 | EL이 OI→UPB를 약화 | SUPPORTED | PI β=-.087, BCa [-.148,-.022]; 문항삭제 후 안정 |

통계적 지지는 횡단면 자료에서 인과적 심리 메커니즘의 입증을 의미하지 않는다. H4~H6은 특히 “연관성·간접효과”로 표현해야 한다.

## 3. 수정 우선순위

### CRITICAL

1. 통합 SEM을 주분석으로 정하고 OLS·개별매개·PROCESS를 보충자료로 이동한다.
2. 모든 표와 본문에서 비표준화 B를 β로 쓴 오류를 고친다.
3. Table 4의 Model 3 계수와 Model 4 EL 계수 혼입을 제거한다.
4. H1~H6/H7 가설 번호·문구를 초록, 이론, Methods, Results, Discussion 전체에서 통일한다.
5. 동일 경로에 개별 단순매개 값과 통합 SEM 값을 섞지 않는다.
6. Inclusion→UPB는 Wald p=.024가 아니라 사전 지정 BCa CI [-.190,.003]을 우선해 경계적 비유의로 판정한다.
7. 높은 EL 조건의 OI→UPB 및 조건부 간접효과가 PI SEM에서 0을 포함한다는 결과로 본문을 수정한다.

### IMPORTANT

1. Equity/Inclusion의 차별적 효과를 “조건부 순효과 패턴”으로 완화하고 별도 심리 메커니즘 입증 주장을 철회한다.
2. 두 간접효과의 크기 차이가 유의하지 않음을 보고하고 47% 대 20%의 강도 서열 해석을 제거한다.
3. Equity–EL 문항 내용 중복과 HTMT=.731 [CI .699,.761], 문항삭제 민감도를 보고한다.
4. scalar invariance 미확보로 잠재평균 차이를 해석하지 않는다.
5. 가중치 WT 미사용을 명시하고 KIPA 코드북의 가중치 사용 지침을 확인한다.
6. 전처리 코드의 SQ1K3/SQ1K4/SQ3K1 설명 오류를 정정한다.

### OPTIONAL

- KIPA 지침이 요구할 경우에만 WT 적용 강건성 분석 수행.
- 직급(SQ2K4/SQ3K3)을 부문 간 공통척도로 조화할 수 있을 때만 추가 통제 강건성 분석 수행.
- 부분 scalar invariance 탐색. 이번 핵심 결론에는 필요하지 않다.
- Mplus LMS로 H7을 재추정. semopy PI의 방법론적 한계를 줄이는 데 유용하지만 제한적 수정의 필수 요건은 아니다.

## 4. 논문 수정 지침

### Methods — 분석전략

- 기존 주장: 위계 OLS, 개별매개, 동시매개, PROCESS, SEM을 병렬로 제시.
- 문제: 동일 경로가 서로 다른 모형에서 다른 의미·계수를 갖는다.
- 권장: 6요인 통제포함 SEM을 기본모형, PI SEM을 H7 확장모형으로 명시한다. OLS와 PROCESS는 강건성 부록으로 이동한다.
- 권장 문안: “가설 검증의 주분석은 모든 잠재구성개념과 직접·간접 경로를 동시에 포함한 구조방정식모형으로 수행하였다. 조절가설은 동일 측정구조에 이중평균중심화 곱셈지표로 구성한 OI×EL 잠재요인을 추가한 확장모형에서 검증하였다.”
- 관련 심사: Reviewer 3 Comment 9.

### Results — H1/H2와 매개

- 기존 주장: 개별 단순매개 B=.393/.429와 간접효과 .048/.078을 통합 결과처럼 사용.
- 권장: 통합 SEM β=.286/.317, 동시 간접효과 .052/.058을 정본으로 사용한다. 간접효과 차이 BCa CI가 0을 포함함을 추가한다.
- 관련 심사: Reviewer 3 Comments 4, 9, 10.

### Results — 차별적 행동 연관성

- 기존 주장: 다른 심리 메커니즘과 매개비율 강도 차이를 확정적으로 해석.
- 권장 문안: “동일모형 대비는 포용성의 OCBI 순효과와 형평성의 UPB 순효과가 상대적으로 더 큼을 보였다. 다만 계수는 두 문화 차원의 높은 공유분산과 OI 통제에 민감했으므로, 이 패턴은 조건부 연관성으로 해석하며 별개의 심리 메커니즘을 직접 입증하지 않는다.”
- 관련 심사: Reviewer 3 Comments 4, 10.

### Results — H7

- 기존 주장: 높은 EL에서도 OI→UPB와 조건부 간접효과가 유의.
- 권장 문안: “OI×EL 상호작용은 부적이었다(β=-.087, BCa 95% CI [-.148,-.022]). 낮은 EL에서 OI→UPB는 유의했으나(β=.258, CI [.161,.354]), 높은 EL에서는 점추정치가 작아지고 CI가 0을 포함했다(β=.084, CI [-.012,.188]).”
- 관련 심사: Reviewer 3 Comments 9, 15.

### Measurement validity

- 권장: 문제 문항의 내용을 나란히 제시하고 문항삭제 후 상호작용과 핵심경로가 유지됐음을 부록에 보고한다. “중복 없음”이 아니라 “통상 판별타당성 기준 충족, 내용 중복은 잔여 한계”로 쓴다.
- 관련 심사: Reviewer 1 Measurement validity; Reviewer 3 Comment 11.

### Tables and notes

- 모든 표에서 B/β, SE 종류, CI 종류, bootstrap 횟수, N, 통제변수, 모형을 명시한다.
- Table 4의 혼합모형을 제거하고 Table 3~7 및 초록의 숫자를 주분석과 동기화한다.
- 관련 심사: Reviewer 3 Comments 15, 17.

## 5. 일곱 질문에 대한 답

1. **기존 분석결과를 유지할 수 있는가?** 방향과 핵심 역설은 유지 가능하지만 수치와 일부 유의성·해석은 통합 SEM 기준으로 교체해야 한다.
2. **기존 통합 SEM을 주분석으로 사용할 수 있는가?** 가능하다. H7은 동일 측정구조의 PI 확장모형으로 분리해 명시한다.
3. **Equity와 Inclusion의 차별적 효과 주장을 유지할 수 있는가?** 공식 대비에 근거한 조건부 행동 연관성 패턴으로는 가능하다. 서로 다른 심리 메커니즘을 입증했다는 주장은 불가능하다.
4. **윤리적 리더십 조절효과는 안정적인가?** 방향·크기·문항삭제 민감도에서 안정적이다. 다만 높은 EL의 조건부 효과는 PI 모형에서 비유의다.
5. **어떤 가설 해석을 수정해야 하는가?** H4의 메커니즘 해석, H5/H6의 강도 서열, H7의 높은 EL 해석을 수정해야 한다. 가설 번호 자체도 통일해야 한다.
6. **추가 분석 없이 본문 수정 단계로 갈 수 있는가?** 핵심 방법론 범위에서는 가능하다. WT 지침 확인은 문서 확인 과제이며, 지침이 가중분석을 요구할 때만 추가 분석한다.
7. **지도교수 전달 전 반드시 해결할 문제는?** B/β 오류, Table 4 혼입, 가설 번호, 통합 SEM 수치 동기화, BCa 기준 적용, 높은 EL 결과, WT 사용 지침 확인이다.

## 생성 산출물

- `01_integrated_sem_primary_model_review.md`
- `02_equity_inclusion_suppression_sensitivity.md`
- `03_measurement_overlap_sensitivity.md`
- `04_statistical_reporting_consistency_audit.md`
- `05_critical_revision_summary.md`
- `tables/zero_order_correlations.csv`
- `tables/suppression_staged_regressions.csv`
- `tables/suppression_vif.csv`
- `tables/item_deletion_sem_fit.csv`
- `tables/item_deletion_sem_paths.csv`
- `tables/item_deletion_validity.csv`
- `tables/item_deletion_pi_moderation.csv`
- `tables/item_deletion_composite_moderation.csv`
- `tables/latent_h3_path_difference_bootstrap.csv`
- `logs/41_roppa_critical_revision.log`

재현 스크립트: `code/41_roppa_critical_revision.py`. 기존 원자료·코드·결과는 삭제하거나 덮어쓰지 않았다.
