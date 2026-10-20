# Table 3·4 관련 본문 수정 감사

## 범위와 판정 원칙

`manuscript_260825.docx`가 작업공간과 첨부 경로에 없어 검색 원문은 `output/final/final_manuscript.md`와 `output/final/abstract.md`에서 확인했다. 따라서 실제 DOCX의 절·페이지·문장 위치는 **UNVERIFIED**이다. 아래 TO-BE 계수의 모형·B·SE·p는 기존 코드와 출력으로 검증했다. 새 분석이나 부트스트랩은 실행하지 않았다.

## 1. Results — Table 3 설명

- **원고의 정확한 위치:** Results, Table 3 인접 문단. 검색 원문: `Model 1에서 공공기관 종사자의 UPB 수준이 유의하게 낮았다`
- **AS-IS:** `공공기관(β=-.222, p<.001), Equity(β=.228, p<.001), Inclusion(β=.006, ns), OI(β=.150, p<.001), EL(β=.017, p=.543).`
- **TO-BE:** `공공기관(B=-.223, SE=.037, p<.001), Equity(B=.229, SE=.030, p<.001), Inclusion(B=.005, SE=.031, p=.861), OI(B=.150, SE=.029, p<.001), EL(B=.018, SE=.028, p=.532).`
- **수정 이유:** AS-IS는 β가 아니라 B이며, 성별 상수 코딩과 출생연도/연령 표기 오류가 있던 과거 실행값이다. TO-BE는 수정된 동일 OLS 사양의 기존 출력이다.
- **근거가 되는 코드 및 CSV 파일 경로:** `code/05_regression_upb.py`; `results/regression/regression_upb.md`; `reports/roppa_critical_revision/tables/coefficient_traceability.csv`
- **검증 상태:** **UNVERIFIED** — 수치는 VERIFIED이나 실제 DOCX 위치를 확인하지 못했다.

- **원고의 정확한 위치:** 같은 문단. 검색 원문: `상호작용을 통해서만 영향을 미침을 시사한다`
- **AS-IS:** `이는 윤리적 리더십이 UPB에 직접 영향을 미치기보다는 조직동일시와의 상호작용을 통해서만 영향을 미침을 시사한다.`
- **TO-BE:** `Model 4에서 윤리적 리더십과 UPB 간 직접적 관계는 유의하지 않았다. 조절효과는 별도의 상호작용 모형에서 검증하였다.`
- **수정 이유:** 유의하지 않은 직접효과만으로 “상호작용을 통해서만”이라고 단정할 수 없다.
- **근거가 되는 코드 및 CSV 파일 경로:** `code/05_regression_upb.py`; `code/07_moderation.py`; `results/regression/regression_upb.md`; `results/moderation/moderation_result.md`
- **검증 상태:** **UNVERIFIED** — 통계적 판단은 VERIFIED이나 실제 DOCX 위치를 확인하지 못했다.

## 2. Results — Table 4 설명

- **원고의 정확한 위치:** Results, Table 4 설명. 검색 원문: `조직동일시는 OCB(β=.217, p<.001)와 UPB(β=.150, p<.001) 모두에`
- **AS-IS:** `OI: OCB β=.217, UPB β=.150; Inclusion: OCB β=.282, UPB β=-.032; Equity: OCB β=-.047, p=.032, UPB β=.194.`
- **TO-BE:** `OI: OCB B=.215(SE=.024, p<.001), UPB B=.150(SE=.029, p<.001); Inclusion: OCB B=.281(SE=.027, p<.001), UPB B=-.033(SE=.032, p=.307); Equity: OCB B=-.042(SE=.022, p=.052), UPB B=.195(SE=.030, p<.001).`
- **수정 이유:** 모든 AS-IS 계수는 B이다. OCB의 Equity 효과는 현재 Model 3에서 p=.052이므로 기존 유의성 해석도 삭제해야 한다.
- **근거가 되는 코드 및 CSV 파일 경로:** `code/22_table5_dei_oi_direct_effects.py`; `results/tables/table5_dei_oi_direct_effects.csv`; `results/ocb_regression/ocb_regression_result.md`; `results/regression/regression_upb.md`
- **검증 상태:** **UNVERIFIED** — TO-BE 수치는 VERIFIED이나 실제 DOCX 위치를 확인하지 못했다.

- **원고의 정확한 위치:** Results, Table 4 관련 본문/각주. 검색 원문: `β=.017, p=.543`
- **AS-IS:** `윤리적 리더십의 UPB 직접효과는 유의하지 않았다(β=.017, p=.543).`
- **TO-BE:** `윤리적 리더십을 추가한 Model 4에서 직접효과는 유의하지 않았다(B=.018, SE=.028, p=.532).`
- **수정 이유:** `.017, p=.543`은 과거 UPB Model 4의 B와 p다. Table 4가 Model 3 표라면 EL 행은 삭제해야 하며, 문장을 유지하면 Model 4임을 밝혀야 한다.
- **근거가 되는 코드 및 CSV 파일 경로:** `code/05_regression_upb.py`; `results/regression/regression_upb.md`; `reports/roppa_critical_revision/tables/coefficient_traceability.csv`
- **검증 상태:** **UNVERIFIED** — 수치 출처는 VERIFIED이나 실제 DOCX 위치를 확인하지 못했다.

- **원고의 정확한 위치:** Results, 가설검증 요약표. 검색 원문: `조직동일시 → UPB`와 `.150***`
- **AS-IS:** `β=.150***`
- **TO-BE:** `B=.150***` 또는 열 제목을 `비표준화계수(B)`로 변경
- **수정 이유:** `.150`은 Model 3의 B다. 기존 수치를 보존하는 최소 수정은 기호 변경이다.
- **근거가 되는 코드 및 CSV 파일 경로:** `code/22_table5_dei_oi_direct_effects.py`; `results/tables/table5_dei_oi_direct_effects.csv`
- **검증 상태:** **UNVERIFIED** — 단위 판정은 VERIFIED이나 실제 DOCX 셀을 확인하지 못했다.

## 3. Results — 조절 및 조건부 간접효과

- **원고의 정확한 위치:** Results, 조절효과 문단. 검색 원문: `상호작용항은 유의한 부적 효과를 나타냈다(β=-.065, p=.008)`
- **AS-IS:** `β=-.065, p=.008`
- **TO-BE:** `B=-.062, SE=.025, p=.011, 95% CI [-.110, -.014]`
- **수정 이유:** AS-IS는 과거 실행의 B를 β로 표시한 값이다. TO-BE는 수정된 기존 OLS 조절모형 출력이다.
- **근거가 되는 코드 및 CSV 파일 경로:** `code/07_moderation.py`; `results/moderation/moderation_result.md`
- **검증 상태:** **UNVERIFIED** — 수치는 VERIFIED이나 실제 DOCX 위치를 확인하지 못했다.

- **원고의 정확한 위치:** Results, 조절효과 문단. 검색 원문: `윤리적 리더십이 낮을 때(-1SD)`
- **AS-IS:** `낮은 EL: B=.230, 95% CI [.169, .291]; 높은 EL: B=.111, 95% CI [.049, .173].`
- **TO-BE:** `[수치 교체 보류] 수정된 조절모형에서 단순기울기와 신뢰구간을 재현한 뒤 확정한다.`
- **수정 이유:** 현재 저장 출력에 단순기울기와 그 CI가 없다. 이 항목만 제한적 재현 실행이 필요하다.
- **근거가 되는 코드 및 CSV 파일 경로:** `code/07_moderation.py`; `results/moderation/moderation_result.md`
- **검증 상태:** **UNVERIFIED**

- **원고의 정확한 위치:** Results 또는 Abstract. 검색 원문: `조건부 간접효과는 윤리적 리더십이 낮을 때 .096`
- **AS-IS:** `낮은 EL .096; 높은 EL .043`
- **TO-BE:** `낮은 EL .095(95% CI [.064, .126]); 높은 EL .046(95% CI [.016, .076])`
- **수정 이유:** 수정된 기존 Model 14 저장 출력값은 .095와 .046이다.
- **근거가 되는 코드 및 CSV 파일 경로:** `code/08_moderated_mediation.py`; `results/moderated_mediation/moderated_mediation_result.md`; `results/equity_model14_with_direct/conditional_indirect_effects.csv`
- **검증 상태:** **UNVERIFIED** — 수치는 VERIFIED이나 실제 DOCX 위치를 확인하지 못했다.

## 4. Discussion

- **원고의 정확한 위치:** Discussion. 검색 원문: `조직동일시는 OCB(β=.217)와 UPB(β=.150) 모두에`
- **AS-IS:** `조직동일시는 OCB(β=.217)와 UPB(β=.150) 모두에 정적 영향을 미쳤다.`
- **TO-BE:** `조직동일시는 OCB(B=.215, p<.001)와 UPB(B=.150, p<.001) 모두와 정적 관계를 보였다.`
- **수정 이유:** 두 값은 B이며 OCB 현재값은 .215다.
- **근거가 되는 코드 및 CSV 파일 경로:** `code/22_table5_dei_oi_direct_effects.py`; `results/tables/table5_dei_oi_direct_effects.csv`
- **검증 상태:** **UNVERIFIED** — 수치는 VERIFIED이나 실제 DOCX 위치를 확인하지 못했다.

- **원고의 정확한 위치:** Discussion. 검색 원문: `형평 기반 조직문화는 UPB에 정적 직접효과(β=.195`
- **AS-IS:** `β=.195, p<.001`
- **TO-BE:** `B=.195, SE=.030, p<.001`
- **수정 이유:** `.195`는 B이므로 수치는 유지하고 기호만 고치면 된다.
- **근거가 되는 코드 및 CSV 파일 경로:** `code/22_table5_dei_oi_direct_effects.py`; `results/tables/table5_dei_oi_direct_effects.csv`
- **검증 상태:** **UNVERIFIED** — 단위는 VERIFIED이나 실제 DOCX 위치를 확인하지 못했다.

- **원고의 정확한 위치:** Discussion. 검색 원문: `직접효과는 유의하지 않았으나(β=.017, p=.543)`
- **AS-IS:** `EL 직접효과 β=.017, p=.543; OI×EL β=-.065, p=.008.`
- **TO-BE:** `Model 4 EL 직접효과 B=.018, SE=.028, p=.532; 별도 조절모형 OI×EL B=-.062, SE=.025, p=.011.`
- **수정 이유:** 두 값 모두 B이고 서로 다른 모형에서 나왔다. 현재 기존 출력에 맞춰 수치와 모형을 구분해야 한다.
- **근거가 되는 코드 및 CSV 파일 경로:** `code/05_regression_upb.py`; `code/07_moderation.py`; `results/regression/regression_upb.md`; `results/moderation/moderation_result.md`
- **검증 상태:** **UNVERIFIED** — 수치·모형은 VERIFIED이나 실제 DOCX 위치를 확인하지 못했다.

- **원고의 정확한 위치:** Discussion. 검색 원문: `공공기관 종사자의 UPB 수준이 낮았다(β=-.222`
- **AS-IS:** `β=-.222, p<.001`
- **TO-BE:** `B=-.223, SE=.037, p<.001`
- **수정 이유:** 현재 수정 출력은 B=-.2226이다.
- **근거가 되는 코드 및 CSV 파일 경로:** `code/05_regression_upb.py`; `results/regression/regression_upb.md`
- **검증 상태:** **UNVERIFIED** — 수치는 VERIFIED이나 실제 DOCX 위치를 확인하지 못했다.

## 5. Abstract

- **원고의 정확한 위치:** 국문 Abstract. 검색 원문: `조직동일시는 UPB(β=.150)와 OCB(β=.217) 모두에`
- **AS-IS:** `UPB β=.150; OCB β=.217`
- **TO-BE:** `UPB B=.150, p<.001; OCB B=.215, p<.001`
- **수정 이유:** 두 값은 B이며 OCB 현재값은 .215다.
- **근거가 되는 코드 및 CSV 파일 경로:** `code/22_table5_dei_oi_direct_effects.py`; `results/tables/table5_dei_oi_direct_effects.csv`
- **검증 상태:** **UNVERIFIED** — 수치는 VERIFIED이나 실제 DOCX 위치를 확인하지 못했다.

- **원고의 정확한 위치:** 국문 Abstract. 검색 원문: `윤리적 리더십은 조직동일시와 UPB 간 관계를 부적으로 조절하였다(β=-.065`
- **AS-IS:** `OI×EL β=-.065, p=.008; 조건부 간접효과 .096/.043`
- **TO-BE:** `OI×EL B=-.062, p=.011; 조건부 간접효과 .095/.046`
- **수정 이유:** 수정된 기존 조절회귀 및 Model 14 저장값을 반영한다.
- **근거가 되는 코드 및 CSV 파일 경로:** `code/07_moderation.py`; `code/08_moderated_mediation.py`; `results/moderation/moderation_result.md`; `results/moderated_mediation/moderated_mediation_result.md`
- **검증 상태:** **UNVERIFIED** — 수치는 VERIFIED이나 실제 DOCX 위치를 확인하지 못했다.

- **원고의 정확한 위치:** 영문 Abstract. 검색 원문: `organizational identification was positively associated with both UPB (β=.150) and OCB (β=.217)`
- **AS-IS:** `UPB β=.150; OCB β=.217`
- **TO-BE:** `UPB B=.150, p<.001; OCB B=.215, p<.001`
- **수정 이유:** 원 수치는 B이며 OCB 현재값은 .215다.
- **근거가 되는 코드 및 CSV 파일 경로:** `code/22_table5_dei_oi_direct_effects.py`; `results/tables/table5_dei_oi_direct_effects.csv`
- **검증 상태:** **UNVERIFIED** — 수치는 VERIFIED이나 실제 DOCX 위치를 확인하지 못했다.

- **원고의 정확한 위치:** 영문 Abstract. 검색 원문: `Ethical leadership negatively moderated the relationship between organizational identification and UPB (β=-.065`
- **AS-IS:** `OI×EL β=-.065, p=.008; conditional indirect effects .096/.043.`
- **TO-BE:** `OI×EL B=-.062, p=.011; conditional indirect effects .095/.046.`
- **수정 이유:** 수정된 기존 조절회귀 및 Model 14 저장값을 반영한다.
- **근거가 되는 코드 및 CSV 파일 경로:** `code/07_moderation.py`; `code/08_moderated_mediation.py`; `results/moderation/moderation_result.md`; `results/moderated_mediation/moderated_mediation_result.md`
- **검증 상태:** **UNVERIFIED** — 수치는 VERIFIED이나 실제 DOCX 위치를 확인하지 못했다.

## 6. 수정 유형 요약

### B/β 표기만 수정하면 되는 경우

- UPB Model 3 OI `.150`: `β` → `B`
- 현재 출력값을 이미 사용한 UPB Equity `.195`: `β` → `B`
- 현재 출력값을 이미 사용한 OCB Inclusion `.281`: `β` → `B`

### 수치 자체도 교체해야 하는 경우

- OCB Model 3 OI `.217` → `.215`
- OCB Model 3 Equity `-.047, p=.032` → `-.042, p=.052` 및 유의성 해석 삭제
- UPB Model 4 EL `.017, p=.543` → `.018, p=.532`
- OI×EL `-.065, p=.008` → `-.062, p=.011`
- 조건부 간접효과 `.096/.043` → `.095/.046`
- Table 3 과거 출생연도 기반 `age` 행은 현재 연령 코딩 출력으로 전 행 교체

## 7. 남은 확인

`manuscript_260825.docx`가 제공되면 추가 분석 없이 실제 표 셀·각주와 Results·Discussion·Abstract의 페이지·문단을 대조해 문서 위치 상태를 VERIFIED로 확정할 수 있다. 현재는 존재하지 않는 DOCX 위치를 추정하지 않았다.
