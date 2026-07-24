# SEM 주분석 종합 요약 (영문 원고 집필 출발점)

작성일: 2026-07-25 (코드 감사 및 SEM 주분석 세션 종료 시점)

이 문서는 (1) 통제변수/재현성 감사(Task A/B)에서 발견·수정한 4개 버그,
(2) semopy 기반 SEM 주분석 6단계 결과와 복합점수(OLS) 모형과의 일치 여부,
(3) 해석 시 반드시 유의해야 할 항목(억제효과·Heywood case·경계적 결과),
(4) 영문 원고에서 다뤄야 할 항목을 한곳에 정리한다. 개별 산출물은
`results/sem/`, `results/validity/`, `results/measurement_invariance/`
하위 각 파일을 참조한다.

---

## 1. 감사 중 발견·수정한 버그 4건

### ① 성별(gender_male) 인코딩 버그
- **증상**: `05_regression_upb.py`/`11_regression_ocb.py`가
  `SQ1K1 == "남자"`로 비교했으나, 전처리 단계(`convert_categoricals=False`)
  때문에 `SQ1K1`은 숫자코드(1.0/2.0)로 저장되어 있어 비교가 항상 False —
  `gender_male`이 2,020건 전부 0인 상수였다.
- **확인**: raw_data.sav 값 라벨 검증 결과 1.0=남자(1,127명), 2.0=여자(893명).
- **수정**: `SQ1K1 == 1.0` 기준으로 정정 (05/07/08/11번+ 22번 신규 스크립트).
- **영향**: 상수였을 때는 다른 계수에 수학적으로 영향이 없었으나(절편과
  완전공선), 정상 인코딩(실제 분산 있는 변수)으로 바꾸자 형평→OCB
  계수/유의성이 논문 게재값(-.042, p=.052)과 정확히 수렴했다. 표4/표5/표8의
  잔여 불일치가 이 버그와 이후 ②의 "모형 혼입" 문제로 전부 설명되었다.

### ② 표5 "모형 혼입" (Model3 계수 + Model4 EL 값 짜깁기)
- **증상**: 논문 표5 UPB 열(형평.194/포용-.032/OI.150/EL.017)이 실제로는
  EL 미포함 3변수 모형(Model3)의 형평·포용·OI 계수에, EL 포함 4변수 모형
  (Model4)의 EL 계수만 이어붙인 값이었다. 실제 4변수 동시투입 모형에서는
  형평=.184로 다르게 나온다.
- **수정**: `22_table5_dei_oi_direct_effects.py` 신규 작성 — 형평·포용·OI
  3변수 동시투입(EL 제외, EL 직접효과는 표4 Model4에 별도 보고) 단일 모형을
  정본으로 확정. 성별 버그 수정 후 이 3변수 모형이 게재값과 완전히 일치함을
  확인.

### ③ HTMT 오계산 (구성개념 상관을 HTMT로 잘못 라벨링)
- **증상**: `13_validity.py`가 문항 평균 합성점수 간 피어슨 상관을
  `htmt`라는 이름으로 출력하고 있었다. Henseler et al.(2015) 공식
  (이형질-이방법 평균 / 동형질-이방법 기하평균)이 전혀 구현되지 않음.
- **수정**: `code/lib_htmt.py` 신규(공식 구현), `tests/test_htmt.py`(손계산
  가능한 소규모 상관행렬 4개 테스트, 전부 통과)로 검증 후 `13_validity.py`에
  반영. 부트스트랩 95% CI(5,000회) 추가.
- **결과**: 올바른 HTMT는 기존 값보다 전반적으로 큼(예: equity-el .668→.731).
  결론(모두 .85 미만, 판별타당성 확보)은 유지되나 여유폭이 크게 줄었다
  (최댓값 equity-el .731, CI 상한 .761 — .85 기준에 근접).

### ④ 절편동일성(Scalar invariance) — 비교집단 잠재평균 미추정
- **증상**: `17_measurement_invariance.py`의 Scalar 단계가 두 집단의
  절편만 동일 제약하고, 비교집단(민간)의 잠재평균을 암묵적으로 0(기준집단과
  동일)으로 고정한 채 자유추정하지 않았다. 표준 절차는 기준집단만 잠재평균
  0 고정, 비교집단은 요인 수만큼(6개) 자유추정해야 한다.
- **확인**: 자유도 산술(Δdf=29 vs 이론값 23=29-6)로 버그 존재를 먼저
  특정, Holzinger & Swineford(1939) 표준 벤치마크(lavaan 공식 게재값
  χ²=164.10/df=60)로 수정 전/후를 대조하여 수정 후 정확히 재현됨을 확인
  (`code/lib_scalar_invariance.py`, `tests/test_measurement_invariance_hs39.py`
  4개 테스트 전부 통과).
- **결과 (논문 데이터, 공공 vs 민간)**: χ²(776)=3032.06→**χ²(770)=2856.06**,
  CFI .931→**.937**, ΔCFI -.018→**-.012**. 결론(절편동일성 미지지)은
  바뀌지 않지만 "명백한 기각"에서 "근소한 기각(경계선)"으로 성격이
  바뀌었다. `results/measurement_invariance/supplementary_appendix_public_private.md`
  갱신 완료.

---

## 2. SEM 주분석 6단계 결과 (semopy) — 복합점수(OLS) 모형과의 대조

| 단계 | 내용 | 핵심 결과 | 복합점수 모형과의 관계 |
|---|---|---|---|
| 1 | 6요인 통합 측정모형 CFA | CFI=.9516, TLI=.9457, RMSEA=.0465, SRMR=.0400, χ²(362)=1944.55 | 12번(2요인 DEI 단독)과 정합(CFI差는 임베딩에 따른 정상 범위) |
| 2 | 2요인 vs 1요인 DEI 재현 | ΔCFI=.1102(≈.110), ΔRMSEA=.0828(≈.083) | 논문 게재값과 정확히 일치, 버그 없음 |
| 3 | 잠재변수 구조모형(H1-H4) | 형평/포용→OI, OI→UPB/OCB 등 주요 경로 부호 일치, 크기 확대(측정오차 보정) | inclusion→UPB만 일시적으로 유의성 반전 → §3에서 해소(억제효과) |
| 4 | 이중요인(bifactor) DEI 진단 | **Heywood case로 추정 실패, 2요인 측정모형 유지 확정** | 해당 없음(측정모형 대안 검토였음) |
| 5 | H7 잠재 상호작용(OI×EL) | **곱셈지표(PI) 방식을 주분석으로 확정.** 상호작용 β=-.0872, BCa[-.1483,-.0220]. 낮은 EL 조건 유의, **높은 EL 조건은 CI가 0 포함(결과로 채택)** | OLS(Table 8: 둘 다 유의)와 결론이 갈림 — 정밀도 차이로 진단 완료(§4) |
| 6 | 다집단 구조모형(공공/민간) | 4개 핵심 경로 전부 차이 없음(모든 p>.23), omnibus Δχ²(4)=2.166, p=.705 | 18번 게재값(모든 p>.24, Δχ²(4)=2.067, p=.723)과 사실상 일치 |

### 3단계 미결 항목 해소 기록

`inclusion→UPB`의 유의성 변화(복합점수 ns → 잠재변수 β=-.101, p=.017)는
후속 진단으로 다음과 같이 해소됨(`results/sem/sem_step3_resolution.md`,
`sem03_controls_multicollinearity_result.md`, `sem06_bca_h4_result.md` 참조):

- BCa 95% 부트스트랩 CI = **[-.190, +.003]**로 상한이 0을 포함 → 경계적 결과.
- 원인: 잠재변수 equity-inclusion 상관 **r=.729**(매우 높음)에 의한
  고전적 억제효과(suppression). 중첩모형 진단(A: equity 단독 → B: +inclusion
  → C: +EL 완전모형)에서 **equity→OCB가 +.156 → -.164 → -.226으로 부호
  반전**되는 것이 같은 현상의 증거.
- **결론**: "포용성이 UPB를 직접 억제한다"는 새 서술은 만들지 않는다.
  논문의 기존 서술("개별 경로가 아니라 순효과로 해석")이 이 현상을 포괄한다.

### 4단계 부트스트랩 규모 근거 (참고: 사용자 요청에 따라 실측 기반 결정)

- 단일 모형 적합 소요시간을 먼저 실측(0.14~0.28초/회)한 뒤 반복수 결정.
- H4 대비/경로계수: 2,000회 Percentile(약 4.5분).
- 매개(H5·H6) 4개 간접효과 동시비교: 5,000회 + 잭나이프 2,020회 BCa(약 24분).
- H7 PI 상호작용(측정모형 가장 복잡): 2,000회 + 잭나이프 2,020회 BCa(약 17.4분).

---

## 3. 해석 시 반드시 유의해야 할 항목

1. **억제효과(suppression)**: equity-inclusion(r=.729), equity-el(r=.735)
   상관이 매우 높다. equity→OCB는 inclusion을 통제하면 부호가 반전되는
   고전적 억제효과를 보인다(§2 3단계 참조). 개별 교차경로 계수보다
   "차이(diff)"나 "순효과" 프레이밍으로 해석해야 한다.
2. **이중요인(bifactor) CFI=.993은 Heywood case에서 나온 값이므로 어디에도
   인용 금지.** "공유 DEI 일반요인이 역설적 경로를 구동한다"는 해석도
   폐기됨(`results/sem/sem_bifactor_final_decision.md`).
3. **H7 High-EL 경계 결과**: 곱셈지표(PI) 모형에서 EL이 높을 때 OI→UPB
   경로와 그 조건부 간접효과의 CI가 0을 포함한다. 이것은 모형 결함이
   아니라 결과이며, "윤리적 리더십이 높으면 조직동일시→UPB 경로가
   유의성을 잃는 수준까지 약화된다"로 서술 확정. 유의성을 만들기 위해
   모형 사양(잔차공분산 등)을 조정하지 않았다.
4. **절편동일성(scalar invariance) 경계적 미지지**: ΔCFI=-.012로 .01
   기준을 근소하게 초과. 잠재평균(공공-민간) 비교는 참고용
   (`results/measurement_invariance/latent_mean_comparison.csv`)으로만
   남기고 본문 해석에는 사용하지 않는다.
5. **낮은 표준화 적재량**: Y1_6(OI, .500)과 Y20_4(UPB, .442)는 기준
   미달/경계값이나 문항 정제는 하지 않기로 결정(Fornell & Larcker 1981
   예외 조항, CR/HTMT 근거 — `results/validity/oi_item_trimming_sensitivity.md`).
6. **semopy는 lavaan의 `group.equal`, LMS(잠재조절), 제약형 PI를 지원하지
   않아 전부 자체 구현**했다. 다집단 결합추정과 절편동일성 로직은
   Holzinger-Swineford(1939) 표준 벤치마크로, HTMT는 손계산 가능한 소규모
   행렬로 검증했다(`tests/` 폴더, 8개 테스트 전부 통과). 이 자체구현·자체검증
   구조를 방법론 절에 명시해야 방어력이 생긴다.

---

## 4. 영문 원고에서 다뤄야 할 항목

1. **억제효과 투명 보고**: equity→OCB 부호 반전을 은폐하지 말고 명시적으로
   보고 — "controlling for inclusion climate, the direct effect of equity
   climate on OCB reverses sign, consistent with classical suppression
   (MacKinnon, Krull, & Lockwood, 2000) driven by the high equity-inclusion
   latent correlation (r=.729)."
2. **부분 절편동일성(partial scalar invariance) 검토**: 어느 항목의
   절편을 자유화하면 완전 절편동일성에 도달하는지 modification index
   기반 탐색이 아직 수행되지 않았다 — 필요 시 후속 분석으로 명시.
3. **Y1_6·Y20_4 낮은 적재량**: 원척도(각각 조직동일시, Umphress et al.
   2010 UPB) 보존을 이유로 유지했음을 각주로 명시하고, 문항정제 민감도
   분석(AVE .455→.523 등)을 부록에 배치할지 결정 필요.
4. **H7 결과의 이론적 프레이밍**: "조절효과가 완전히 사라진다"가 아니라
   "낮은 EL에서는 강하고 유의하지만, 높은 EL에서는 유의성을 잃을 만큼
   약화된다"는 완충(buffering)의 정도 차이로 서술. OLS(복합점수)와 SEM
   (측정오차 보정) 간 결론 차이의 이유(정밀도)를 방법론 절에 함께 명기.
5. **HTMT 경계 사례**: equity-el(.731), equity-inclusion(.720) 두 쌍이
   .85 기준에 상대적으로 가깝다는 점을 판별타당성 논의에서 선제적으로
   언급(리뷰어 질문 예방).
6. **semopy 선택과 자체 검증 절차**: R/lavaan 대신 Python semopy를
   사용했고, lavaan에 있는 기능(다집단 동일성 제약, HTMT)을 직접 구현한
   부분은 표준 벤치마크(HS1939)와 손계산 테스트로 검증했음을 방법론
   절에 기술 — 리뷰어의 "왜 이 패키지인가" 질문에 대한 선제 대응.
7. **다집단(공공/민간) 결과의 일반화 주장 강화 근거**: 6단계 잠재변수
   다집단 모형이 18번 복합점수 모형과 결론이 완전히 일치(omnibus
   Δχ²(4)=2.166 vs 2.067)한다는 점을 강건성 증거로 명시적으로 인용 가능.

---

## 5. 파일 인덱스

| 파일 | 내용 |
|---|---|
| `sem01_measurement_model_result.md` | 1단계: 6요인 CFA |
| `sem02_structural_model_result.md` | 3단계: 구조모형 초기 결과(성별/억제효과 진단 전) |
| `sem03_controls_multicollinearity_result.md` | 3단계: 통제포함 구조모형 + 억제효과 진단 |
| `sem_bifactor_final_decision.md` | 4단계: 이중요인 최종 결정(Heywood case) |
| `sem04_h4_suppressor_result.md` | H4 대비 부트스트랩 + 억제효과 4열표 |
| `sem05_bifactor_result.md`, `sem08_bifactor_diag_result.md` | 4단계: 이중요인 진단 과정 기록(인용 금지, 참고용) |
| `sem06_bca_h4_result.md` | H4 대비 BCa 재계산(경계적 결과 확정) |
| `sem07_mediation_result.md` | 4단계: 매개(H5·H6) 부트스트랩 |
| `sem_step3_resolution.md` | 3단계 미결 항목 해소 기록 |
| `sem09_h7_product_indicator_result.md` | 5단계: H7 PI 주분석(확정) |
| `sem10_h7_comparison_result.md` | 5단계: PI vs Hybrid 비교 및 최종 권고 |
| `sem11_multigroup_structural_result.md` | 6단계: 다집단 구조모형 |
| `low_loading_note.md` | Y1_6/Y20_4 낮은 적재량 기록 |
| `../validity/` | HTMT 재계산, OI 문항정제 민감도 |
| `../measurement_invariance/` | 측정동일성(수정판), 부록 문서 |
