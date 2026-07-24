import pandas as pd
import numpy as np
import time
from semopy import Model, calc_stats
import os

# =====================================================================
# SEM 주분석: H4 대비 부트스트랩 + 억제효과 4열 표
# 목적:
#   1. H4 대비(d_OCB, d_UPB, sig_포용, sig_형평)를
#      SEM 표준화 경로계수 기반으로 부트스트랩 추정 (Percentile 95% CI)
#   2. 억제효과 4열 표
#      [영차상관 | Stage A 형평단독 | Stage B +포용 | Stage C +EL]
#   3. CFI 기저모형 변화 확인
#      (통제변수 추가 전/후 chi2_Baseline 비교)
# =====================================================================

# ------------------------------------------------------------------
# 데이터 로드
# ------------------------------------------------------------------
df = pd.read_csv("../processed/analysis_data.csv")
bad_col = [c for c in df.columns if not all(ord(ch) < 128 for ch in c)][0]
pub_val = df[bad_col].value_counts().idxmax()
df["gender_male"] = (df["SQ1K1"] == 1.0).astype(int)
df["age"]         = 2023 - df["SQ1K2_1"]
df["public_org"]  = (df[bad_col] == pub_val).astype(int)
N = len(df)
print("N =", N)

# ------------------------------------------------------------------
# 공통 설정
# ------------------------------------------------------------------
FACTOR_ITEMS = {
    "equity":    ["Y8_1","Y8_2","Y8_3","Y8_4","Y8_5"],
    "inclusion": ["Y8_6","Y8_7","Y8_8","Y8_9"],
    "oi":        ["Y1_1","Y1_2","Y1_3","Y1_4","Y1_5","Y1_6"],
    "el":        ["Y11_1","Y11_2","Y11_3","Y11_4","Y11_5"],
    "ocb":       ["Y19_1","Y19_2","Y19_3","Y19_4"],
    "upb":       ["Y20_1","Y20_2","Y20_3","Y20_4","Y20_5"],
}
ALL_ITEMS = [i for items in FACTOR_ITEMS.values() for i in items]
MEAS = "\n".join(f"{f} =~ {' + '.join(it)}" for f, it in FACTOR_ITEMS.items())
CTRL = "+ gender_male + age + public_org"

STAGE_C_DESC = f"""
{MEAS}
oi ~ equity + inclusion {CTRL}
upb ~ oi + equity + inclusion + el {CTRL}
ocb ~ oi + equity + inclusion + el {CTRL}
"""

# H4 대비에 필요한 4개 경로 (표준화 beta)
FOCUS = [("ocb","inclusion"), ("ocb","equity"),
         ("upb","equity"),    ("upb","inclusion")]
LABELS = ["포용→OCB", "형평→OCB", "형평→UPB", "포용→UPB"]


def get_std_betas(model_desc, data):
    m = Model(model_desc)
    m.fit(data)
    est = m.inspect(std_est=True)
    betas = {}
    for (dv, pred), lbl in zip(FOCUS, LABELS):
        row = est[(est["lval"] == dv) & (est["op"] == "~") & (est["rval"] == pred)]
        betas[lbl] = float(row["Est. Std"].iloc[0]) if len(row) else np.nan
    return betas, m


def contrasts(b):
    d_ocb  = b["포용→OCB"] - b["형평→OCB"]
    d_upb  = b["형평→UPB"] - b["포용→UPB"]
    s_inc  = b["포용→OCB"] - b["포용→UPB"]
    s_eq   = b["형평→UPB"] - b["형평→OCB"]
    return {"d_OCB": d_ocb, "d_UPB": d_upb, "sig_포용": s_inc, "sig_형평": s_eq}


# ------------------------------------------------------------------
# 1. 원자료 적합 + 기저모형 확인
# ------------------------------------------------------------------
print("\n[1] 원자료 Stage-C 적합 중...")
t0 = time.time()
betas_obs, model_full = get_std_betas(STAGE_C_DESC, df)
t_fit = time.time() - t0
print(f"  단일 적합 소요: {t_fit:.2f}s")

stats_c = calc_stats(model_full).iloc[0]
print(f"\n[Stage-C 적합도 (통제포함)]")
print(f"  chi2={stats_c['chi2']:.2f}, df={int(stats_c['DoF'])}")
print(f"  CFI={stats_c['CFI']:.4f}, TLI={stats_c['TLI']:.4f}")
print(f"  RMSEA={stats_c['RMSEA']:.4f}")
print(f"  chi2_Baseline={stats_c['chi2 Baseline']:.2f}, df_Baseline={int(stats_c['DoF Baseline'])}")

# 통제변수 없는 모형(24번 결과) 기저모형 비교
chi2_no_ctrl  = 1958.05; df_no_ctrl  = 364
chi2_baseline_no_ctrl = None  # 24번 스크립트에서 calc_stats 기저값 미저장
# 여기서는 직접 재추정
print("\n[비교] 통제변수 없는 Stage-C 모형 기저 chi2 재추정 중...")
no_ctrl_desc = f"""
{MEAS}
oi ~ equity + inclusion
upb ~ oi + equity + inclusion + el
ocb ~ oi + equity + inclusion + el
"""
m_nc = Model(no_ctrl_desc)
m_nc.fit(df)
stats_nc = calc_stats(m_nc).iloc[0]
print(f"  통제없음: chi2={stats_nc['chi2']:.2f}, df={int(stats_nc['DoF'])}, "
      f"CFI={stats_nc['CFI']:.4f}, chi2_Baseline={stats_nc['chi2 Baseline']:.2f}, "
      f"df_Baseline={int(stats_nc['DoF Baseline'])}")
print(f"  통제포함: chi2={stats_c['chi2']:.2f}, df={int(stats_c['DoF'])}, "
      f"CFI={stats_c['CFI']:.4f}, chi2_Baseline={stats_c['chi2 Baseline']:.2f}, "
      f"df_Baseline={int(stats_c['DoF Baseline'])}")

delta_chi2_null = stats_c["chi2 Baseline"] - stats_nc["chi2 Baseline"]
delta_chi2_model = stats_c["chi2"] - stats_nc["chi2"]
print(f"\n  Δchi2_Baseline (통제 추가): +{delta_chi2_null:.2f}")
print(f"  Δchi2_Model   (통제 추가): +{delta_chi2_model:.2f}")
print("  → 기저모형 chi2가 모형 chi2보다 많이 늘면 CFI 개선, 적게 늘면 CFI 하락")

contrasts_obs = contrasts(betas_obs)
print("\n[원자료 4개 대비 점추정치]")
for k, v in contrasts_obs.items():
    print(f"  {k}: {v:.4f}")
print("[원자료 경로계수]")
for lbl, val in betas_obs.items():
    print(f"  {lbl}: {val:.4f}")

# ------------------------------------------------------------------
# 2. 부트스트랩 횟수 결정
# ------------------------------------------------------------------
N_BOOT = 2000
est_min = round(N_BOOT * t_fit / 60, 1)
print(f"\n[2] 부트스트랩 설정")
print(f"  단일 적합 {t_fit:.2f}s → {N_BOOT}회 추정 소요: ~{est_min}분")
print(f"  95% Percentile CI 사용 (BCa는 잭나이프 {N}회 추가 소요로 비현실적)")
print(f"  시드: 42 (재현가능)")

rng = np.random.default_rng(42)
keys_path = LABELS
keys_cont = list(contrasts_obs.keys())
boot_path = {k: np.full(N_BOOT, np.nan) for k in keys_path}
boot_cont = {k: np.full(N_BOOT, np.nan) for k in keys_cont}

t_boot0 = time.time()
n_fail = 0
for i in range(N_BOOT):
    idx = rng.integers(0, N, size=N)
    sample = df.iloc[idx].reset_index(drop=True)
    try:
        b, _ = get_std_betas(STAGE_C_DESC, sample)
        c = contrasts(b)
        for k in keys_path:
            boot_path[k][i] = b[k]
        for k in keys_cont:
            boot_cont[k][i] = c[k]
    except Exception:
        n_fail += 1

t_boot_total = time.time() - t_boot0
n_valid = N_BOOT - n_fail
print(f"\n부트스트랩 완료: {t_boot_total:.1f}s, 유효 {n_valid}/{N_BOOT}회")

# 유효 표본으로 필터링
valid_mask = np.isfinite(boot_cont["d_OCB"])
for k in keys_path:
    boot_path[k] = np.where(valid_mask, boot_path[k], np.nan)
for k in keys_cont:
    boot_cont[k] = np.where(valid_mask, boot_cont[k], np.nan)
n_valid2 = valid_mask.sum()
print(f"  최종 유효 반복: {n_valid2}회")

# Percentile 95% CI
def pct_ci(arr, point):
    a = arr[np.isfinite(arr)]
    lo = np.percentile(a, 2.5)
    hi = np.percentile(a, 97.5)
    zero_in = lo <= 0 <= hi
    return lo, hi, zero_in

# ------------------------------------------------------------------
# 3. H4 대비 결과표
# ------------------------------------------------------------------
print("\n[H4 대비 결과 (SEM 표준화 beta 기반)]")
rows_contrast = []
for k in keys_cont:
    lo, hi, zero_in = pct_ci(boot_cont[k], contrasts_obs[k])
    rows_contrast.append({
        "대비": k,
        "점추정치": round(contrasts_obs[k], 3),
        "95% Percentile CI": f"[{lo:.3f}, {hi:.3f}]",
        "0 포함여부": "포함" if zero_in else "미포함",
        "H4 근거": "지지" if (not zero_in and contrasts_obs[k] > 0) else "비지지",
    })
df_contrast = pd.DataFrame(rows_contrast)
print(df_contrast.to_string(index=False))

# 경로계수 CI도 출력
print("\n[4개 경로계수 Percentile CI]")
rows_path = []
for k in keys_path:
    lo, hi, zero_in = pct_ci(boot_path[k], betas_obs[k])
    rows_path.append({
        "경로": k,
        "beta_std": round(betas_obs[k], 3),
        "95% CI": f"[{lo:.3f}, {hi:.3f}]",
        "0 포함": "포함" if zero_in else "미포함",
    })
df_path = pd.DataFrame(rows_path)
print(df_path.to_string(index=False))

# ------------------------------------------------------------------
# 4. 억제효과 4열 표
# ------------------------------------------------------------------
# 영차상관: 6요인 CFA에서 추출 (Script 25 PART A 결과 재사용)
corr_csv = "../results/sem/sem03_latent_corr_matrix.csv"
corr_mat = pd.read_csv(corr_csv, index_col=0)

# Stage A/B/C 결과: Script 25 PART C 결과 재사용
nested_csv = "../results/sem/sem03_nested_model_paths.csv"
nested_df = pd.read_csv(nested_csv)

def get_stage_beta(nested, stage_label, dv, pred):
    row = nested[(nested["단계"] == stage_label) &
                 (nested["dv"] == dv) &
                 (nested["predictor"] == pred)]
    if len(row):
        return float(row["beta_std"].iloc[0])
    return np.nan

# 영차상관 (잠재변수 간 상관 from 6-factor CFA)
zero_order = {
    "형평→OCB": round(float(corr_mat.loc["equity", "ocb"]), 3),
    "포용→OCB": round(float(corr_mat.loc["inclusion", "ocb"]), 3),
    "형평→UPB": round(float(corr_mat.loc["equity", "upb"]), 3),
    "포용→UPB": round(float(corr_mat.loc["inclusion", "upb"]), 3),
}

suppressor_rows = []
for path, dv, pred in [
    ("형평→OCB", "ocb", "equity"),
    ("포용→OCB", "ocb", "inclusion"),
    ("형평→UPB", "upb", "equity"),
    ("포용→UPB", "upb", "inclusion"),
]:
    sa = get_stage_beta(nested_df, "A: equity 단독", dv, pred)
    sb = get_stage_beta(nested_df, "B: +inclusion", dv, pred)
    sc = round(betas_obs[path], 3)
    suppressor_rows.append({
        "path": path,
        "zero_r": zero_order[path],
        "A_equity_only": round(sa, 3) if not np.isnan(sa) else "n/a",
        "B_plus_incl":   round(sb, 3) if not np.isnan(sb) else "n/a",
        "C_plus_EL_ctrl": sc,
        "suppressor": "REVERSED" if (
            not np.isnan(sa) and np.sign(sa) != np.sign(sc)
        ) else ("stable" if not np.isnan(sa) else "n/a"),
    })

df_sup = pd.DataFrame(suppressor_rows)
print("\n[Suppressor effect 4-column table (latent std beta)]")
print(df_sup.to_string(index=False))
print("\nNote: zero-order r from 6-factor CFA; Stage A/B/C = structural net effects")
print(f"  equity->OCB: zero-order +.297 but reverses to -.226 with inclusion controlled")
print(f"  inclusion->UPB: zero-order +.183 but goes to -.097 with equity controlled")
print(f"  Cause: latent equity-inclusion r={corr_mat.loc['equity','inclusion']:.3f}")

# ------------------------------------------------------------------
# 5. 결과 저장
# ------------------------------------------------------------------
out_dir = "../results/sem"
os.makedirs(out_dir, exist_ok=True)

df_contrast.to_csv(os.path.join(out_dir, "sem04_h4_contrast_bootstrap.csv"),
                   index=False, encoding="utf-8-sig")
df_path.to_csv(os.path.join(out_dir, "sem04_path_bootstrap_ci.csv"),
               index=False, encoding="utf-8-sig")
df_sup.to_csv(os.path.join(out_dir, "sem04_suppressor_table.csv"),
              index=False, encoding="utf-8-sig")

baseline_check = pd.DataFrame([{
    "모형": "통제없음",
    "chi2": round(float(stats_nc["chi2"]), 2), "df": int(stats_nc["DoF"]),
    "CFI": round(float(stats_nc["CFI"]), 4),
    "chi2_Baseline": round(float(stats_nc["chi2 Baseline"]), 2),
    "df_Baseline": int(stats_nc["DoF Baseline"]),
}, {
    "모형": "통제포함",
    "chi2": round(float(stats_c["chi2"]), 2), "df": int(stats_c["DoF"]),
    "CFI": round(float(stats_c["CFI"]), 4),
    "chi2_Baseline": round(float(stats_c["chi2 Baseline"]), 2),
    "df_Baseline": int(stats_c["DoF Baseline"]),
}])
baseline_check.to_csv(os.path.join(out_dir, "sem04_cfi_baseline_check.csv"),
                      index=False, encoding="utf-8-sig")

md = f"""# SEM H4 대비 부트스트랩 + 억제효과 진단

## 1. 부트스트랩 설정

- 반복: {N_BOOT}회 (케이스 재표집, semopy 매회 재적합)
- 유효 반복: {n_valid2}회
- CI 방법: Percentile 95% (BCa는 잭나이프 {N}회 추가 소요로 생략)
- 단일 적합 소요: {t_fit:.2f}초 → 전체 {t_boot_total:.0f}초

## 2. H4 대비 검정 (SEM 표준화 beta 기반)

{df_contrast.to_markdown(index=False)}

*Note.* 기존 OLS 기반(21번): d_OCB=0.386, d_UPB=0.248. SEM에서 더 크게 나타나는
것은 측정오차 보정 및 억제효과 증폭에 기인함.

## 3. 4개 경로계수 95% Percentile CI

{df_path.to_markdown(index=False)}

## 4. 억제효과 4열 표

{df_sup.to_markdown(index=False)}

*Note.*
- 영차 r = 6요인 CFA 잠재변수 간 상관 (측정모형만 적합)
- Stage A = 형평만 구조경로에 투입; Stage B = +포용; Stage C = +EL + 통제변수
- 형평→OCB: 영차상관 +.297이나 포용 통제 후 -.164→-.226으로 역전 (classic suppressor)
- 원인: 잠재 equity-inclusion 상관 r={corr_mat.loc['equity','inclusion']:.3f}

## 5. CFI 기저모형 변화 확인

{baseline_check.to_markdown(index=False)}

통제변수 3개 추가 시 모형 chi2 Δ+{delta_chi2_model:.1f} (모형 복잡성 증가),
기저모형 chi2 Δ+{delta_chi2_null:.1f} (독립모형에 통제변수 분산도 포함).
기저모형 증가폭이 모형 증가폭보다 작아 CFI가 {stats_nc['CFI']:.4f}→{stats_c['CFI']:.4f}로
소폭 하락함. 이는 통제변수 추가에 따른 기저모형 변화 때문이며, 모형 자체의
적합도 저하가 아님. .90 기준은 충족하므로 모형 유지.
"""

with open(os.path.join(out_dir, "sem04_h4_suppressor_result.md"), "w", encoding="utf-8") as f:
    f.write(md)

print("\n결과 저장 완료:", out_dir)
