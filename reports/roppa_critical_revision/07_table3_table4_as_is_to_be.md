# 07. Table 3과 Table 4 AS IS TO BE

## 적용 원칙

- OLS·HC3 주분석과 기존 Model 1~4 구조를 유지한다.
- 표의 값은 비표준화 B와 HC3 SE로 보고한다.
- Table 3은 현재 수정 코드의 UPB Model 1~4를 사용한다.
- Table 4는 최소 수정안으로 현재 Model 3만 사용하고 EL 행을 삭제한다.
- DOCX가 없어 실제 원고 위치는 UNVERIFIED이며, 검색 문자열은 `output/final/final_manuscript.md` 기준이다.

## 수정 기록 1 Table 3 전체

- 원고 위치: Results, “Table 3. UPB에 대한 위계적 회귀분석 결과 (HC3 이분산-강건 표준오차)”
- 검색 가능한 원문: `| 연령 | .002 | .004* | .007*** | .007*** |`
- 검증 상태: **UNVERIFIED** — DOCX 미제공. 아래 수치 출처는 VERIFIED.

### AS-IS

| 변수 | Model 1 | Model 2 | Model 3 | Model 4 |
|---|---|---|---|---|
| 연령 | .002 | .004* | .007*** | .007*** |
| 조직 유형 (공공=1) | -.222*** | -.147*** | -.150*** | -.154*** |
| 형평 기반 조직문화 | — | .228*** | .194*** | .184*** |
| 포용적 조직문화 | — | .006 | -.032 | -.036 |
| 조직동일시 | — | — | .150*** | .148*** |
| 윤리적 리더십 | — | — | — | .017 |
| R² | .018 | .080 | .095 | .095 |

### TO-BE

별표 대신 p를 함께 표시해 경계값의 오독을 막는 최소 수정표다.

| 변수 | Model 1 B (SE), p | Model 2 B (SE), p | Model 3 B (SE), p | Model 4 B (SE), p |
|---|---|---|---|---|
| 성별 (남성=1) | .021 (.037), .571 | -.022 (.037), .544 | -.015 (.036), .670 | -.017 (.036), .651 |
| 연령 | -.002 (.002), .260 | -.003 (.002), .080 | -.007 (.002), .001 | -.007 (.002), .001 |
| 조직 유형 (공공=1) | -.223 (.037), <.001 | -.146 (.037), <.001 | -.149 (.036), <.001 | -.153 (.037), <.001 |
| 형평 기반 조직문화 | — | .229 (.030), <.001 | .195 (.030), <.001 | .185 (.033), <.001 |
| 포용적 조직문화 | — | .005 (.031), .861 | -.033 (.032), .307 | -.037 (.032), .260 |
| 조직동일시 | — | — | .150 (.029), <.001 | .148 (.029), <.001 |
| 윤리적 리더십 | — | — | — | .018 (.028), .532 |
| R² | .018 | .080 | .095 | .095 |
| N | 2,020 | 2,020 | 2,020 | 2,020 |

- 수정 이유: AS-IS는 성별이 상수였던 구버전 실행을 사용했고 출생연도 B를 연령으로 잘못 표시했다. 값은 β가 아니다.
- 근거 코드 및 출력: `code/05_regression_upb.py`; `results/regression/regression_upb.md`; 구버전 `git:a0556490:code/05_regression_upb.py`와 대응 결과.

## 수정 기록 2 Table 4 전체

- 원고 위치: Results, “Table 4. 조직동일시의 양면적 효과: UPB vs. OCB 비교”
- 검색 가능한 원문: `*p<.05, **p<.01, ***p<.001; Model 3 기준 (통제변수 포함, EL 제외)`
- 검증 상태: **UNVERIFIED** — DOCX 미제공. 아래 수치 출처는 VERIFIED.

### AS-IS

| 변수 | UPB (β) | OCB (β) |
|---|---:|---:|
| 형평 기반 조직문화 | .194*** | -.047* |
| 포용적 조직문화 | -.032 | .282*** |
| 조직동일시 | .150*** | .217*** |
| 윤리적 리더십 | .017 | .063** |
| R² | .095 | .222 |

### TO-BE 최소 수정안

| 변수 | UPB B (HC3 SE), p | OCB B (HC3 SE), p |
|---|---|---|
| 형평 기반 조직문화 | .195 (.030), <.001 | -.042 (.022), .052 |
| 포용적 조직문화 | -.033 (.032), .307 | .281 (.027), <.001 |
| 조직동일시 | .150 (.029), <.001 | .215 (.024), <.001 |
| R² | .095 | .224 |
| N | 2,020 | 2,020 |

표 주석 TO-BE: “비표준화계수 B와 괄호 안 HC3 이분산-강건 표준오차를 보고하였다. Model 3은 성별, 연령 및 조직유형을 통제하고 Equity, Inclusion 및 OI를 동시에 포함하였다. EL은 포함하지 않았다.”

- 수정 이유: 여섯 focal 셀은 구버전 Model 3, EL 두 셀은 구버전 Model 4에서 가져왔다. OCB 열은 성별 인코딩 수정 후 수치와 Equity 유의성이 달라졌다.
- 근거 코드 및 CSV: `code/22_table5_dei_oi_direct_effects.py`; `results/tables/table5_dei_oi_direct_effects.csv`; `code/05_regression_upb.py`; `code/11_regression_ocb.py`.

## 수정 기록 3 Table 4 EL=.017

- 원고 위치: Table 4, 윤리적 리더십×UPB 셀
- 검색 가능한 원문: `| 윤리적 리더십 | .017 | .063** |`
- AS-IS: `.017`
- TO-BE: **셀과 EL 행 삭제**
- 수정 이유: `.017`은 Model 3 값이 아니라 구버전 UPB Model 4의 B=.0170(SE=.028, p=.543)이다. 현재 Model 4에서는 B=.0175(SE=.028, p=.532)이다. Model 3 표를 유지하는 최소 수정은 EL 행 삭제다.
- 근거 코드 및 출력: `code/05_regression_upb.py`; `results/regression/regression_upb.md`; `git:a0556490:results/regression/regression_upb.md`.
- 검증 상태: **VERIFIED**

## 수정 기록 4 Table 4 OCB=-.047

- 원고 위치: Table 4, 형평 기반 조직문화×OCB 셀
- 검색 가능한 원문: `| 형평 기반 조직문화 | .194*** | -.047* |`
- AS-IS: `-.047*`
- TO-BE: `-.042 (.022), p=.052` 또는 별표 체계 사용 시 `-.042†`
- 수정 이유: AS-IS는 성별을 상수로 잘못 만든 구버전 Model 3 B=-.0466, p=.032다. 현재 수정된 동일 Model 3은 B=-.0421, p=.052로 5% 기준에서 유의하지 않다.
- 근거 코드 및 CSV: `code/11_regression_ocb.py`; `code/22_table5_dei_oi_direct_effects.py`; `results/tables/table5_dei_oi_direct_effects.csv`.
- 검증 상태: **VERIFIED**

## 수정 기록 5 B와 β

- 원고 위치: Table 4 열 머리글 및 Table 3·4 관련 본문
- 검색 가능한 원문: `UPB (β)`, `OCB (β)`, `β=.281`, `β=.195`, `β=.150`, `β=.017`
- AS-IS: 해당 숫자를 표준화 β로 표기
- TO-BE: Table 3·4 머리글과 본문에서 B로 표기. 표준화계수가 꼭 필요하면 실제 β로 교체한다.

| B | 실제 β |
|---:|---:|
| OCB Inclusion B=.281 | β=.331 |
| UPB Equity B=.195 | β=.216 |
| UPB OI B=.150 | β=.144 |
| UPB Model 4 EL B=.018 | β=.021 |
| OCB OI B=.215 | β=.245 |

- 수정 이유: 현재 CSV와 statsmodels 결과는 원 단위 합성점수 회귀의 B를 출력한다.
- 근거 코드 및 CSV: `code/22_table5_dei_oi_direct_effects.py`; `results/tables/table5_dei_oi_direct_effects.csv`; `tables/coefficient_traceability.csv`.
- 검증 상태: **VERIFIED**

## 대안 Model 4 표가 필요한 경우

EL을 Table 4에 반드시 남기려면 아래처럼 모든 focal 계수와 R²를 Model 4로 바꿔야 한다. 이는 최소 수정안이 아니다.

| 변수 | UPB Model 4 B | OCB Model 4 B |
|---|---:|---:|
| Equity | .185 | -.078 |
| Inclusion | -.037 | .267 |
| OI | .148 | .207 |
| EL | .018 | .065 |
| R² | .095 | .228 |

근거는 `results/regression/regression_upb.md`와 `results/ocb_regression/ocb_regression_result.md`다.
