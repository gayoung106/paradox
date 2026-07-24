# H7 잠재 상호작용 비교표: Method (a) vs (b) vs OLS

## 방법 비교 요약

| 측면 | Method (a): Product Indicator | Method (b): Hybrid |
|:-----|:-----|:-----|
| 상호작용 구성 | 잠재 OI x EL (5 곱 지표 -> latent oi_el) | 관측 합산점수 곱 (oi_mc x el_mc) |
| OI 처리 | 잠재변수 | 잠재변수 (main effect) + 관측 복합점수 (interaction) |
| 제약 여부 | 비제약 (unconstrained PI) | 없음 |
| 측정오차 보정 | 부분 (PI 관련 항에서만) | 없음 (interaction에서) |
| 수렴 안정성 | 수렴 확인 | 수렴 |
| 추정 시간 | 약 10.9분 | 10.9분 |

## 수치 결과 비교

| 항목 | PI 추정값 | PI BCa CI | PI 0포함 | 혼합 추정값 | 혼합 BCa CI | 혼합 0포함 | OLS 참고 |
|:-----|----------:|:----------|:--------:|------------:|:-----------|:--------:|:---------|
| Interaction OI x EL -> UPB | -0.087 | [-0.148,-0.022] | no | N/A | N/A | N/A | beta=-.062 (p=.011) |
| IE equity (EL-1SD) | 0.073 | [0.042,0.113] | no | 0.071 | [0.042,0.108] | no | .095 |
| IE equity (EL+1SD) | 0.024 | [-0.003,0.057] | yes | 0.026 | [0.000,0.059] | no | .046 |
| IE inclusion (EL-1SD) | 0.083 | [0.049,0.125] | no | 0.078 | [0.047,0.118] | no | n/a |
| IE inclusion (EL+1SD) | 0.027 | [-0.003,0.063] | yes | 0.029 | [0.000,0.063] | no | n/a |
| OI->UPB slope (EL-1SD) | 0.258 | [0.161,0.354] | no | 0.247 | [0.159,0.337] | no | n/a |
| OI->UPB slope (EL+1SD) | 0.084 | [-0.012,0.188] | yes | 0.091 | [-0.003,0.187] | yes | n/a |


## 모형 적합도

| 방법 | CFI | RMSEA | 비고 |
|:-----|----:|------:|:-----|
| OLS | n/a | n/a | R2 기반 |
| PI (비제약) | 0.9403 | 0.0423 | semopy unconstrained |
| Hybrid | 0.9376 | 0.0466 | 관측 상호작용항 |

## 방법론 평가

### Method (a): Product Indicator (곱셈지표)

**장점**:
- 완전 잠재변수 상호작용 (측정오차 보정)
- SSCI에서 인정된 방법 (Marsh et al., 2004; Lin et al., 2010)
- 상호작용의 신뢰구간이 이론적으로 더 정확

**단점**:
- semopy에서 비제약만 가능 (PI 오차분산 고정 미지원)
- 완전 구현은 Mplus LMS (Klein & Moosbrugger, 2000) 또는 R lavaan 권장
- 곱 지표 비정규성 -> 강건 추정 필요 (여기서는 bootstrap으로 부분 보완)
- 식별 취약성: 곱 지표가 원 지표와 공분산 구조 공유

**SSCI 통용도**: 비제약 PI는 Structural Equation Modeling 저널 등에서 수락 사례 있음.
"unconstrained approach (Kenny & Judd, 1984; Marsh et al., 2004)"로 명기 필요.

### Method (b): Hybrid (혼합 방식)

**장점**:
- 구현 단순, 식별 문제 없음
- 수렴 안정
- 상호작용 방향/유의성이 OLS와 비교 가능

**단점**:
- 상호작용항에 측정오차 포함 -> 영가설 방향 편향 (downward bias)
- OI 잠재변수와 OI 합산점수가 혼재 -> 이론적 비일관성
- 조건부 간접효과가 근사치 (잠재 OI와 관측 OI_mc 비동일성 무시)

**SSCI 통용도**: 응용 SEM 논문에서 광범위 사용 (Preacher & Hayes, 2008 확장).
단순성과 수렴 안정성으로 선호. 측정오차 편향은 한계로 명기.

## 권고 (확정)

**주분석은 Method (a) 곱셈지표(Product Indicator)로 확정한다.** Hybrid는
강건성 검증(robustness check)으로만 각주 처리한다. 근거:

1. 조직행동 계열 SSCI에서 곱셈지표 방식이 잠재 상호작용의 표준으로 통용됨.
2. Hybrid는 내생변수(OI)만 잠재이고 상호작용항은 관측 합산점수(oi_mc x
   el_mc)라 절충적이며, 왜 상호작용항만 관측변수로 남겨두는지 이론적
   설명 부담이 있음.
3. 적합도는 PI(CFI=.9403)가 Hybrid(CFI=.9376)보다 근소하게 우수하고,
   두 방법의 방향·전반적 결론(낮은 EL 유의, 높은 EL 비유의)이 일치하여
   강한 쪽(PI)을 주분석으로 채택해도 결론이 바뀌지 않음.

PI 모형의 곱지표 간 잔차공분산은 matched-pairs 설계 특성상 비제약(고정 0)이
올바른 설정이며(all-pairs 공유문항 전제의 Marsh, Wen, & Hau 2004 권고는
적용되지 않음), 전부 자유추정하는 대안을 시도했으나 경험적으로 비식별
(SE가 점추정치의 5~20배)로 확인되어 폐기하였다(자세한 내용은
[sem09_h7_product_indicator_result.md](sem09_h7_product_indicator_result.md) 참조).

**높은 EL 조건에서 조건부 간접효과·단순기울기 CI가 0을 포함하는 것은 결과로
채택한다.** "윤리적 리더십이 높으면 조직동일시->UPB 경로가 유의성을 잃는
수준까지 약화된다"가 확정 서술이며, 유의성을 만들어내기 위한 모형 재조정은
하지 않는다.

## 조건부 간접효과 해석 주의

- Method (a) 조건부 IE: EL +/-1SD = 잠재 EL 표준편차 단위 (=1)
- Method (b) 조건부 IE: EL +/-1SD = 관측 EL 복합점수 표준편차 (0.955)
- 두 방법의 조건부 IE 크기가 다를 수 있음 (단위 차이)
- OLS 조건부 IE(.095/.046)는 비표준화; 모두 방향성과 유의성으로 비교
