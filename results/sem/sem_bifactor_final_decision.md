# 이중요인(Bifactor) DEI 측정모형 — 최종 결정

## 결론

**이중요인 CFA는 Heywood case(부적절 해)로 추정에 실패했다. 측정모형은 2요인
(equity, inclusion)을 그대로 유지한다.**

## 근거

직교 이중요인 모형(`g_dei =~ 9개 DEI 항목; equity_s =~ Y8_1~5; inclusion_s =~
Y8_6~9`, 세 요인 간 공분산 0 제약)을 semopy로 재적합한 결과, Y8_1의 잔차분산이
정확히 0으로 추정되었다(raw parameter: Estimate = 0.000000, SE = 0.339,
p = 1.0). 표준화 적재량 기준으로도 lambda_g=.726, lambda_s=.688로
h² = .726² + .688² = 1.000, unique = 0 — 교과서적 Heywood case다.

equity_s의 나머지 네 문항(Y8_2~5) 표준화 고유적재량은 .171/.079/-.034/.041로
사실상 0에 가까워, equity_s가 실질적으로 Y8_1 단일 문항으로만 정의된
비식별에 가까운 상태다. equity_s 요인 자체의 분산 추정치도 유의하지 않다
(Estimate=.524, p=.124).

이 축퇴 해 위에서 산출된 탐색적 구조모형(`sem08_bifactor_struct_paths.csv`)의
equity_s→oi/upb/ocb 세 경로는 전부 -0.0/0.0/0.0(반올림 전에도 사실상 0)으로
나오는데, 이는 equity_s가 통계적으로 무의미한 요인이기 때문이지 "형평성의
고유효과가 0이다"라는 실질적 발견이 아니다.

## 인용 금지 사항

- **CFI = .993(이중요인 직교 모형의 적합도)은 부적절 해에서 나온 값이므로
  논문 어디에도 인용하지 않는다.** 2요인 모형의 CFI(.962)만 유효하다.
- **"역설적 경로(포용→UPB 등)는 공유 DEI 일반요인(g_dei)이 구동한다"는
  해석은 폐기한다.** `sem08_bifactor_diag_result.md` Part 4의 g_dei 관련
  유의한 경로(oi~g_dei=.513***, upb~g_dei=.242**)는 Heywood case 위에서
  나온 결과라 근거가 없다.
- 관련 이전 산출물(`sem05_bifactor_result.md`, `sem08_bifactor_diag_result.md`,
  `sem08_bifactor_loadings.csv`, `sem08_bifactor_indices.csv`,
  `sem08_bifactor_struct_paths.csv`)은 진단 과정 기록으로 보존하되,
  본 문서를 그 상위 결정으로 참조한다.

## 확정 사항

측정모형은 [12_cfa_dei.py](../../code/12_cfa_dei.py) / [23_sem01_measurement_model_cfa.py](../../code/23_sem01_measurement_model_cfa.py)의
**2요인(equity, inclusion) CFA를 그대로 유지**한다(CFI=.962/.9516, TLI=.947/.9457).
이중요인 검토는 여기서 종료한다.
