import pandas as pd

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

df = pd.read_spss(
    "../raw/raw_data.sav",
    convert_categoricals=False
)

print("원본 데이터:", df.shape)

# --------------------------------------------------
# 변수 정의
# --------------------------------------------------

# 조직동일시-매개변수
oi_cols = [
    "Y1_1",
    "Y1_2",
    "Y1_3",
    "Y1_4",
    "Y1_5",
    "Y1_6"
]
# DEI(포용성, 형평성) - 독립변수
# =========================
# Diversity & Equity Climate
# (EFA 결과 기반)
# =========================

equity_cols = [
    "Y8_1",
    "Y8_2",
    "Y8_3",
    "Y8_4",
    "Y8_5"
]

# =========================
# Inclusion Climate
# (Y8_10 제거)
# =========================

inclusion_cols = [
    "Y8_6",
    "Y8_7",
    "Y8_8",
    "Y8_9"
]

# 윤리적 리더십-조절변수
el_cols = [
    "Y11_1",
    "Y11_2",
    "Y11_3",
    "Y11_4",
    "Y11_5"
]
# UPB(비윤리적 친조직행동) - 종속변수
upb_cols = [
    "Y20_1",
    "Y20_2",
    "Y20_3",
    "Y20_4",
    "Y20_5"
]

# =========================
# 조직시민행동 (OCB)
# =========================

ocb_cols = [
    "Y19_1",
    "Y19_2",
    "Y19_3",
    "Y19_4"
]


# =========================
# 개인특성 통제변수
# =========================
personal_control_cols = [
    "SQ1K1",    # 성별
    "SQ1K2_1",  # 연령
    "SQ1K3",    # 교육수준
    "SQ1K4",    # 소득
]

# =========================
# 조직특성 통제변수
# =========================

org_control_cols = [
    "유형",      # 공공/민간
    "SQ2K3",     # 조직유형
    "SQ3K1",     # 기업규모
]


# --------------------------------------------------
# 최종 변수 리스트
# --------------------------------------------------

selected_cols = (
    oi_cols +
    equity_cols +
    inclusion_cols +
    el_cols +
    ocb_cols +
    upb_cols +
    personal_control_cols +
    org_control_cols
)

# --------------------------------------------------
# 분석 데이터셋 생성
# --------------------------------------------------

analysis_df = df[selected_cols]

print("분석 데이터셋:", analysis_df.shape)

# --------------------------------------------------
# 결측 확인
# --------------------------------------------------

print("\n결측치 개수")
print(analysis_df.isnull().sum())

# 핵심 연구 변수는 결측 없음
# 조직특성 변수는 공공/민간 분기로 인해 결측 존재

# --------------------------------------------------
# 저장
# --------------------------------------------------


# --------------------------------------------------
# 변수 생성
# --------------------------------------------------

# 조직동일시
analysis_df["org_identification"] = (
    analysis_df[oi_cols].mean(axis=1)
)

# Diversity & Equity Climate
analysis_df["equity_climate"] = (
    analysis_df[equity_cols].mean(axis=1)
)

# Inclusion Climate
analysis_df["inclusion_climate"] = (
    analysis_df[inclusion_cols].mean(axis=1)
)

# 윤리적 리더십
analysis_df["ethical_leadership"] = (
    analysis_df[el_cols].mean(axis=1)
)

# 조직시민행동
analysis_df["ocb"] = (
    analysis_df[ocb_cols].mean(axis=1)
)

# 친조직 비윤리행동
analysis_df["upb"] = (
    analysis_df[upb_cols].mean(axis=1)
)

# --------------------------------------------------
# 저장
# --------------------------------------------------

analysis_df.to_csv(
    "../processed/analysis_data.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n분석용 데이터 저장 완료")
print("\n저장 경로: ../processed/analysis_data.csv")

# --------------------------------------------------
# 생성 변수 확인
# --------------------------------------------------

created_vars = [
    "org_identification",
    "equity_climate",
    "inclusion_climate",
    "ethical_leadership",
    "ocb",
    "upb"
]

print("\n생성 변수 기술통계")
# --------------------------------------------------
# 생성 변수 기술통계
# --------------------------------------------------

desc_stats = (
    analysis_df[created_vars]
    .describe()
    .round(3)
)

print("\n생성 변수 기술통계")
print(desc_stats)

# --------------------------------------------------
# Markdown 저장
# --------------------------------------------------

md_content = f"""
# Preprocessing Summary

## 원본 데이터 크기
- {df.shape}

## 분석 데이터셋 크기
- {analysis_df.shape}

---

# 생성 변수 기술통계

{desc_stats.to_markdown()}

---

# 생성 변수 목록

- org_identification
- equity_climate
- inclusion_climate
- ethical_leadership
- ocb
- upb
"""

with open(
    "../results/preprocessing_summary.md",
    "w",
    encoding="utf-8"
) as f:
    f.write(md_content)

print("\nMarkdown 저장 완료")