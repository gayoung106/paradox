# DEI Bifactor 측정모형 검토

## 핵심 결과: 수렴 불안정 — 사용 불가

### 경고 메시지
```
WARNING: Fisher Information Matrix is not PD.
Moore-Penrose inverse will be used instead of Cholesky decomposition.
```

Fisher Information Matrix가 양정치(positive definite)가 아님 → 표준오차 신뢰 불가,
모형이 식별되지 않았거나 수치 불안정 상태.

### 비제약 bifactor에서 나타난 요인 간 공분산

| lval | rval | Estimate | p-value |
|:-----|:-----|:--------:|:-------:|
| g_dei | equity_s | **−9.668** | .468 |
| g_dei | inclusion_s | 0.475 | <.001 |
| inclusion_s | equity_s | −0.622 | <.001 |

g_dei − equity_s 공분산 = **−9.668** (비현실적; 요인 분산이 각 ~7~13 수준)
→ 두 요인이 동일한 5개 항목(Y8_1~5)에 모두 적재되어 **회전 불확정성** 발생.

### 식별 문제 원인

| 요인 | 적재 항목 수 |
|:-----|:----------:|
| g_dei | 9개 (전체) |
| equity_s | 5개 (Y8_1~5) |
| inclusion_s | 4개 (Y8_6~9) |

g_dei와 equity_s가 **동일한 5개 항목**에 모두 적재 → 직교 제약 없이는
무한히 많은 동치해(equivalent solutions)가 존재. semopy는 직교 제약을
지원하지 않아 수치 불안정 해로 수렴.

## 모형 비교

| 모형 | chi2 | df | CFI | TLI | RMSEA | 비고 |
|:-----|-----:|---:|----:|----:|------:|:-----|
| 단일요인 | 1629.39 | 27 | .852 | .802 | .171 | 12번 재현 |
| 2요인 (equity+inclusion) | 438.40 | 26 | .962 | .947 | .089 | **주 측정모형** |
| Bifactor (비제약) | 97.94 | 15 | .993 | .986 | .050 | **식별 불안정** |

- Δchi2(11) = 340.46, p < .001 (2요인 vs bifactor)
- Bifactor 적합도가 수치상 더 좋으나, Fisher 행렬 PD 실패 및 요인 공분산 -9.67로 결과 신뢰 불가

## 결론

**Bifactor CFA는 semopy에서 신뢰할 수 있는 해를 얻지 못함.**

원인: g_dei와 equity_s가 동일한 항목 집합을 공유하므로, 직교 제약(g_dei ⊥ equity_s)
없이는 모형이 식별되지 않음. semopy는 현재 직교 제약을 지원하지 않음.

## 권고

| 옵션 | 비고 |
|:-----|:-----|
| R의 lavaan 사용 | `model.type = "bifactor"` 지원, 직교 자동 처리 |
| 2요인 유지 | 현재 측정모형 유지, 억제효과는 별도 보고 |
| 고계요인 모형 | g_dei → equity, inclusion (구조적 위계 표현) |

**현재 결정**: 2요인 측정모형 유지 (CFI=.962, RMSEA=.089).
Bifactor 검토 결과는 "semopy 환경에서 식별 불가"로 명기.
억제효과 해결 목적이면 고계요인(higher-order) 모형이 현실적 대안.
