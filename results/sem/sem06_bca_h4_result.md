# H4 대비 BCa 재계산 + 이중요인 직교 시도

## 1. 이중요인(직교) CFA 시도

| model                     |    chi2 |   df |    CFI |   RMSEA | note                                                     |
|:--------------------------|--------:|-----:|-------:|--------:|:---------------------------------------------------------|
| 1-factor DEI              | 1629.39 |   27 | 0.852  |  0.171  | from script 12                                           |
| 2-factor DEI              |  438.4  |   26 | 0.9618 |  0.0886 | primary model                                            |
| bifactor_orthogonal_0star |   97.43 |   18 | 0.9926 |  0.0468 | 0* constraint accepted; max off-diag factor cov = 0.0000 |

**결론**: 0* constraint accepted; max off-diag factor cov = 0.0000

## 2. 부트스트랩 설정

- 반복: 2000회 (케이스 재표집, 시드=42)
- 잭나이프: 2020회 (BCa 가속 인자 a 추정)
- CI 방법: BCa 95% (Percentile 병기)
- 부트스트랩 소요: 273초, 잭나이프 소요: 300초
- 유효 반복: 2000/2000회

## 3. H4 대비 (Percentile vs BCa 비교)

| contrast   | label                          |   est |   pct_lo |   pct_hi | zero_in_pct   |   bca_lo |   bca_hi | zero_in_bca   |
|:-----------|:-------------------------------|------:|---------:|---------:|:--------------|---------:|---------:|:--------------|
| d_OCB      | d_OCB = incl_ocb - eq_ocb      | 0.663 |    0.497 |    0.823 | no            |    0.493 |    0.819 | no            |
| d_UPB      | d_UPB = eq_upb - incl_upb      | 0.366 |    0.19  |    0.547 | no            |    0.182 |    0.541 | no            |
| sig_incl   | sig_incl = incl_ocb - incl_upb | 0.534 |    0.407 |    0.66  | no            |    0.406 |    0.659 | no            |
| sig_eq     | sig_eq = eq_upb - eq_ocb       | 0.495 |    0.349 |    0.648 | no            |    0.344 |    0.639 | no            |

*Note.* Percentile과 BCa 차이가 작으면 분포 대칭성이 높음을 의미.
보고 시 BCa 95% CI 사용.

## 4. 경로계수 CI (Percentile vs BCa)

| path           |    est |   pct_lo |   pct_hi | zero_in_pct   |   bca_lo |   bca_hi | zero_in_bca   |
|:---------------|-------:|---------:|---------:|:--------------|---------:|---------:|:--------------|
| inclusion->OCB |  0.437 |    0.346 |    0.529 | no            |    0.347 |    0.53  | no            |
| equity->OCB    | -0.226 |   -0.329 |   -0.123 | no            |   -0.327 |   -0.121 | no            |
| equity->UPB    |  0.269 |    0.161 |    0.381 | no            |    0.16  |    0.38  | no            |
| inclusion->UPB | -0.097 |   -0.192 |   -0.002 | no            |   -0.19  |    0.003 | yes           |

## 5. 서술 주의사항

- d_OCB, d_UPB: 0 미포함 → H4 지지. OLS 대비 크기 비교 불요
  (형평→OCB 부호역전이 대비값 증폭의 주원인 — 억제효과 산물)
- inclusion→UPB: CI 상한이 0에 가까움 — "경계적 결과"로 서술
