# Reviewer Simulation Report
> Generated: 2026-05-27
> Manuscript: 좋은 조직의 역설: 포용적 조직문화는 친조직 비윤리행동을 증가시키는가?

---

## Overview

| Reviewer | Score | Verdict | Primary Concern |
|---|---|---|---|
| reviewer_ssci | 72/100 | Major Revision | Cultural generalizability; Table 6 CI 누락 |
| reviewer_theory | 79/100 | Minor Revision | Moral disengagement black-box 가능성 |
| reviewer_methodology | 76/100 | Minor Revision | VIF const 이상값 표기; CMB 방법론 |
| reviewer_contribution | 80/100 | Accept w/ Minor Revision | Upstream mechanism 전면화 필요 |
| skeptical_reviewer | 74/100 | Major Revision | 형평 기반 OC 직접효과 이론화 불충분 |

**Composite Score: 76.2/100 → Minor-to-Major Revision 수준**

---

## reviewer_ssci

### Concerns

**[MAJOR-1] 표 6 조건부 간접효과 CI 수치 누락**
Results 10절 Table 6에서 조건부 간접효과가 "낮은 수준=.096, 높은 수준=.043"으로 보고되었으나, 각각의 95% 신뢰구간 수치가 "[유의]"로만 기재되어 있다. SSCI급 저널은 bootstrap 결과에서 구체적 CI 하한값과 상한값의 보고를 요구한다.

**→ 수정 필요:** 원 분석 데이터에서 각 조건부 간접효과의 CI 확인 후 보고. (현재 이용 가능한 데이터: Low EL(-1SD)=.096, High EL(+1SD)=.043 — CI 수치는 원 Python 분석 재실행 또는 Hayes PROCESS 검증 필요)

**[MINOR-1] 문화적 일반화 논의 보완**
현재 Discussion 한계에서 "집단주의적 조직문화"를 언급하지만 구체적 함의가 미약하다. 한국의 유교적 위계 구조에서 조직동일시와 UPB 간 관계가 서구 개인주의 표본 대비 강화될 가능성을 1-2문장으로 추가 서술 권고.

**[MINOR-2] EFA에서 최초 추출 요인 수 결정 기준 미기재**
Methods 4절 EFA 설명에서 Kaiser 기준(고유값 1 이상)과 스크리 도표 등 요인 수 결정 근거가 명시되지 않았다.

---

## reviewer_theory

### Concerns

**[MINOR-1] SIT-도덕적 탈구 연결 메커니즘 추가 명료화**
이론 1절에서 SIT의 내집단 편향이 도덕적 탈구로 이어지는 연쇄를 제안하지만, "강화된 동일시 → 도덕적 탈구 → UPB 정당화"의 각 단계가 어떤 조건에서 활성화되는지가 다소 추상적이다. 특히 모든 OI가 도덕적 탈구로 이어지는 것이 아닌데, 그 조건이 윤리적 리더십 부재임을 이론 1절에서 더 명확하게 연결해야 한다.

**[MINOR-2] H2 vs H1 경로 구분의 실증적 의미**
포용적 OC의 a경로(β=.429)가 형평 기반 OC(β=.393)보다 크다는 결과가 이론적으로 예측된 것인지, 아니면 사후 설명인지가 불분명하다. 이론 3절에서 포용적 OC의 "보다 직접적인 정체성 경로"를 예측했다면, 이것이 a경로 크기 차이를 예측하는 것으로 연결되는지를 Discussion에서 한 문장으로 명확화 필요.

**[관찰] 도덕적 탈구 미측정 한계 처리**
Discussion 향후연구에서 도덕적 탈구 직접 측정 제안이 포함되어 있어 적절히 처리됨. ✓

---

## reviewer_methodology

### Concerns

**[MAJOR-1] VIF const 이상값 처리 필요**
원 VIF 분석에서 const(상수항)의 VIF=51,928이 나타남. 이는 표준화되지 않은 회귀에서 상수항의 공선성 지표로, 실질적 공선성 문제가 아닌 수치 계산 이슈임. 그러나 이를 Results에 보고할 경우 독자가 오해할 수 있으므로, "분석변수(실질적 독립변수)의 VIF는 모두 5 미만(최고값 equity climate=2.432)으로 다중공선성 우려가 없다"는 언급에 const 제외를 명시하거나 footnote 추가 필요.

**[MINOR-1] Harman 검정 한계 인정 보완**
현재 "Harman 검정의 탐색적 성격을 감안하여...절대적 근거로 해석하지 않는다"는 문구가 있음. 추가적으로 Podsakoff et al.(2003)이 제안한 CMB 절차적 통제(procedure controls) — 예를 들어 익명성 보장, 시차 설계 등 — 중 적용한 것이 있다면 언급하는 것이 reviewer 대응에 유리함.

**[MINOR-2] 횡단 자료와 매개분석 결합의 한계 강조**
현재 한계 1절에서 횡단 자료의 인과 추론 한계를 다루고 있으나, 특히 "baronomial 매개분석(causal mediation inference)"에서의 한계—즉, 횡단 자료에서는 "DEI 기후 → OI → UPB"의 시간적 순서를 검증할 수 없다는 점—를 1문장 추가 명시 권고.

---

## reviewer_contribution

### Concerns

**[MINOR-1] Upstream mechanism 전면화**
Introduction 서두에서 "DEI 기후가 UPB에 미치는 영향"처럼 읽힐 수 있는 구절이 있다. 본 연구의 핵심 기여가 "DEI가 직접 UPB를 유발하는 것이 아니라, DEI → OI → UPB라는 조직문화 수준의 upstream 경로"임을 서론 첫 단락 또는 연구 격차 절에서 더 전면에 배치 권고.

현재 서론 5절(학술적 기여)에서 "DEI 효과 연구를 넘어, 조직충성의 dark side를 다루는 이론적 논의에 독립적으로 기여한다"는 표현이 있어 기여가 명시됨. ✓

**[관찰-긍정] OI duality 실증의 독창성 인정**
동일 모형에서 OI→OCB와 OI→UPB를 동시에 확인한 것은 기존 OI 연구의 긍정 편향을 극복하는 실질적 기여로 인정됨. ✓

---

## skeptical_reviewer

### Core Critique

**[CHALLENGE-1] 기존 명제의 결합에 불과하다는 비판**

> "이 연구는 'DEI기후→OI'(Ashforth & Mael; Shore et al. 계열)와 'OI→UPB'(Umphress & Bingham 2011)를 단순 결합한 것에 불과하다. 두 기존 명제의 결합이 어떻게 독자적 기여가 되는가?"

**대응 논거 (논문에 이미 반영됨):**
1. DEI를 2요인으로 경험적 구분하여 차별적 경로(매개 비율 47% vs. 20%) 실증 — 기존 DEI-UPB 연구 없음
2. OI duality를 동일 모형에서 OCB+UPB 동시 확인 — 기존 OI 연구의 긍정 편향 극복
3. UPB의 조직문화 수준 upstream 기제 — 개인 수준 중심의 UPB 연구에서 조직 수준으로 설명 확장
4. EL의 조절 특이성(moderator specificity) — 직접효과 비유의, 조절효과 유의의 메커니즘 특정

**→ 반영 상태: 양호. Introduction 5절과 Discussion 2.2절에서 명확히 처리됨.**

**[CHALLENGE-2] 형평 기반 OC의 강한 직접효과(β=.228) 이론화 불충분**

> "형평 기반 OC가 조직동일시 이외의 경로로 UPB에 직접 영향을 미친다면, 그 경로는 무엇인가? '의무감과 호혜 기대'라는 언급만으로는 post-hoc rationalization이다."

**대응 방향 (보완 필요):**
사회교환 이론의 호혜 규범(norm of reciprocity; Gouldner, 1960)을 구체적으로 언급하여, 공정하게 처우받는다는 인식이 조직에 대한 강한 의무감(felt obligation)을 형성하고, 이 의무감이 OI를 경유하지 않고도 직접적으로 UPB를 촉발하는 경로를 이론화할 것.

**→ Discussion 2.1 또는 Theory 6절에 1-2문장 추가 권고.**

**[CHALLENGE-3] EL의 주효과가 왜 UPB와 양(+)의 관계인가 (조절된 매개 Model B)**

> "조절된 매개 Model B에서 EL 주효과가 β=.096(p<.001)으로 나타난다. EL이 UPB를 증가시킨다는 것인가?"

**대응:** Model B는 DEI 기후 변수를 포함하지 않은 축약 모형(mediation pathway b-path model)으로, EL의 양(+)의 주효과는 형평 기반 OC와의 공분산이 통제되지 않은 결과임. 전체 통제변수를 포함한 Model 4에서 EL β=.017(ns)로 나타나는 것이 적절한 해석 기반임. 이 점을 Methods 또는 Results footnote에 명시하는 것이 reviewer 대응에 효과적.

---

## 종합 수정 권고 (Priority)

| 우선순위 | 유형 | 내용 | 위치 |
|---|---|---|---|
| P1 | 필수 | Table 6 조건부 간접효과 CI 수치 추가 | Results 10절 |
| P2 | 필수 | VIF const 이상값 footnote 추가 | Results 4절/5절 |
| P3 | 권고 | 형평 기반 OC 직접효과 — 호혜 규범(Gouldner, 1960) 이론화 1문장 추가 | Discussion 2.1 |
| P4 | 권고 | EL Model B 주효과 해석 footnote 추가 | Results 9절/10절 |
| P5 | 선택 | 문화적 일반화 한계 1문장 보강 | Discussion 5.1절 |
| P6 | 선택 | EFA 요인 수 결정 기준 명시 | Methods 4절 |

---
