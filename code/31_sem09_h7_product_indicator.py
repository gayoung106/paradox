import pandas as pd
import numpy as np
import time
from scipy.stats import norm as spnorm
from semopy import Model, calc_stats
import os

# =============================================================
# Script 31: H7 Latent interaction -- Method (a)
#   Double mean-centered product indicator (Lin et al., 2010)
#   Matched pairs: Y1_i (mean-centered) x Y11_i for i=1..5
#   Y1_6 remains a free indicator of OI only
#   Unconstrained version (semopy does not support fixing error
#   variances of product indicators to theoretical values from
#   original loadings -- limitation noted)
#
#   Model: full 6-factor CFA + latent oi_el (5 product indicators)
#   Structural: oi ~ equity + inclusion + ctrl
#               upb ~ oi + el + oi_el + equity + inclusion + ctrl
#               ocb ~ oi + el + oi_el + equity + inclusion + ctrl
#
#   Bootstrap 2000 + Jackknife 2020 -> BCa CI
#   Expected time: ~15-20 min
# =============================================================

df = pd.read_csv("../processed/analysis_data.csv")
bad_col = [c for c in df.columns if not all(ord(ch) < 128 for ch in c)][0]
pub_val = df[bad_col].value_counts().idxmax()
df["gender_male"] = (df["SQ1K1"] == 1.0).astype(int)
df["age"]         = 2023 - df["SQ1K2_1"]
df["public_org"]  = (df[bad_col] == pub_val).astype(int)
N = len(df)
print("N =", N)

OI_ITEMS  = ["Y1_1","Y1_2","Y1_3","Y1_4","Y1_5","Y1_6"]
EL_ITEMS  = ["Y11_1","Y11_2","Y11_3","Y11_4","Y11_5"]
OI_MATCHED = OI_ITEMS[:5]   # first 5 OI items for product indicators

# Create double mean-centered product indicators on full data
for k, (oi_it, el_it) in enumerate(zip(OI_MATCHED, EL_ITEMS), 1):
    mc_oi = df[oi_it] - df[oi_it].mean()
    mc_el = df[el_it] - df[el_it].mean()
    df[f"pi_{k}"] = mc_oi * mc_el

PI_ITEMS = [f"pi_{k}" for k in range(1, 6)]
print("Product indicators created:", PI_ITEMS[:3], "...")
print("pi stats:", df[PI_ITEMS].describe().loc[["mean","std"]].round(3).to_string())

FACTOR_ITEMS = {
    "equity":    ["Y8_1","Y8_2","Y8_3","Y8_4","Y8_5"],
    "inclusion": ["Y8_6","Y8_7","Y8_8","Y8_9"],
    "oi":        OI_ITEMS,
    "el":        EL_ITEMS,
    "ocb":       ["Y19_1","Y19_2","Y19_3","Y19_4"],
    "upb":       ["Y20_1","Y20_2","Y20_3","Y20_4","Y20_5"],
}
MEAS = "\n".join(f"{f} =~ {' + '.join(it)}" for f, it in FACTOR_ITEMS.items())
CTRL = "+ gender_male + age + public_org"

# Product indicator factor: latent oi_el from 5 product indicators
PI_MEAS = "oi_el =~ " + " + ".join(PI_ITEMS)

# Residual covariances among the 5 product indicators are left at semopy's
# default (fixed to 0), i.e. unconstrained/independent uniquenesses. This
# was tested with all C(5,2)=10 pairwise covariances freed instead (Marsh,
# Wen, & Hau 2004-style), but that model was empirically near-unidentified
# with this matched-pairs design (SEs 5-20x the point estimates, since all
# 5 indicators are built from only 2 underlying factors, OI and EL -- too
# little independent information to pin down 10 extra covariance
# parameters). Matched-pairs indicators also do not share a first-order
# item the way Marsh et al.'s classic all-pairs justification assumes, so
# independent uniquenesses is the correct default here, not a shortcut.
MODEL_DESC = f"""
{MEAS}
{PI_MEAS}
oi ~ equity + inclusion {CTRL}
upb ~ oi + el + oi_el + equity + inclusion {CTRL}
ocb ~ oi + el + oi_el + equity + inclusion {CTRL}
"""

ALL_ITEMS = [it for its in FACTOR_ITEMS.values() for it in its] + PI_ITEMS

# BCa helper
def bca_ci(boot_arr, theta_hat, jack_arr, alpha=0.05):
    b = boot_arr[np.isfinite(boot_arr)]
    if len(b) < 20:
        return np.nan, np.nan
    prop = np.clip(np.mean(b < theta_hat), 0.5/len(b), 1 - 0.5/len(b))
    z0 = spnorm.ppf(prop)
    jk = jack_arr[np.isfinite(jack_arr)]
    jk_mean = np.mean(jk)
    diffs = jk_mean - jk
    num = np.sum(diffs**3)
    den = 6 * np.sum(diffs**2)**1.5
    a_acc = num / den if den > 1e-12 else 0.0
    def adj(z_a):
        inner = 1 - a_acc * (z0 + z_a)
        if abs(inner) < 1e-10:
            return 1.0 if z_a > 0 else 0.0
        return float(np.clip(spnorm.cdf(z0 + (z0 + z_a)/inner), 0.001, 0.999))
    return (np.percentile(b, 100*adj(spnorm.ppf(alpha/2))),
            np.percentile(b, 100*adj(spnorm.ppf(1 - alpha/2))))

def pct_ci(arr):
    a = arr[np.isfinite(arr)]
    return np.percentile(a, 2.5), np.percentile(a, 97.5)


def get_std(est, dv, pred):
    r = est[(est.lval==dv) & (est.op=="~") & (est.rval==pred)]
    return float(r["Est. Std"].iloc[0]) if len(r) else np.nan


def get_all_betas(data):
    """Create product indicators on resampled data and fit model."""
    d = data.copy()
    for k, (oi_it, el_it) in enumerate(zip(OI_MATCHED, EL_ITEMS), 1):
        mc_oi = d[oi_it] - d[oi_it].mean()
        mc_el = d[el_it] - d[el_it].mean()
        d[f"pi_{k}"] = mc_oi * mc_el
    m = Model(MODEL_DESC)
    m.fit(d)
    est = m.inspect(std_est=True)
    return {
        "eq_oi":      get_std(est, "oi",  "equity"),
        "incl_oi":    get_std(est, "oi",  "inclusion"),
        "oi_upb":     get_std(est, "upb", "oi"),
        "oi_el_upb":  get_std(est, "upb", "oi_el"),   # INTERACTION
        "el_upb":     get_std(est, "upb", "el"),
        "oi_ocb":     get_std(est, "ocb", "oi"),
        "oi_el_ocb":  get_std(est, "ocb", "oi_el"),
        "el_ocb":     get_std(est, "ocb", "el"),
        "eq_upb":     get_std(est, "upb", "equity"),   # direct
        "incl_upb":   get_std(est, "upb", "inclusion"),
    }


def compute_cond_indirect(b, el_sd=1.0):
    """
    Conditional indirect effects at EL +/- el_sd (standardized units).
    For product indicator: el_sd=1 (latent EL is standardized, SD=1).
    slope(OI->UPB|EL=c) = oi_upb + oi_el_upb * c
    """
    slope_low  = b["oi_upb"] + b["oi_el_upb"] * (-el_sd)
    slope_high = b["oi_upb"] + b["oi_el_upb"] * (+el_sd)
    return {
        "int_coef":      b["oi_el_upb"],
        "ie_eq_low":     b["eq_oi"]   * slope_low,
        "ie_eq_high":    b["eq_oi"]   * slope_high,
        "ie_incl_low":   b["incl_oi"] * slope_low,
        "ie_incl_high":  b["incl_oi"] * slope_high,
        "slope_low":     slope_low,
        "slope_high":    slope_high,
        "diff_ie_eq":    b["eq_oi"]   * (slope_low - slope_high),
        "diff_ie_incl":  b["incl_oi"] * (slope_low - slope_high),
    }


# ---- Point estimates ----
print("\nFitting product indicator model on full data...")
t0 = time.time()
try:
    betas_obs = get_all_betas(df)
    t_fit = time.time() - t0
    print(f"  Fit time: {t_fit:.2f}s")

    # Check Fisher matrix
    m_check = Model(MODEL_DESC)
    m_check.fit(df)
    # semopy logs warnings to stderr; we'll check if key estimates look reasonable
    int_obs = betas_obs["oi_el_upb"]
    print(f"  Interaction (OI x EL -> UPB): beta_std = {int_obs:.4f}")
    print(f"  OI->UPB main: {betas_obs['oi_upb']:.4f}")
    print(f"  OI->OCB main: {betas_obs['oi_ocb']:.4f}")
    print(f"  EL->UPB: {betas_obs['el_upb']:.4f}")

    # Sign-flip check vs OLS
    if betas_obs["oi_upb"] < 0:
        print("!!! SIGN FLIP: oi_upb is negative. Stop and report.")
        raise SystemExit("Sign flip detected")
    if int_obs > 0.05:
        print("  Note: interaction has unexpected positive sign (OLS was negative -.062)")

    cond_obs = compute_cond_indirect(betas_obs, el_sd=1.0)
    print(f"\n  Conditional indirect (equity, EL-1SD): {cond_obs['ie_eq_low']:.4f}")
    print(f"  Conditional indirect (equity, EL+1SD): {cond_obs['ie_eq_high']:.4f}")
    print(f"  (OLS reference: low=.095, high=.046)")

except Exception as e:
    print(f"  Model FAILED: {e}")
    print("  -> Product indicator model not feasible in semopy with this specification.")
    print("     Record failure and proceed to Method (b).")
    # Save failure note
    failure_note = {
        "method": "product_indicator",
        "status": "FAILED",
        "error": str(e)[:200],
        "note": ("Product indicator latent interaction may be underidentified or "
                 "unstable in semopy without proper PI measurement constraints. "
                 "Use Method (b) hybrid approach or Mplus for full latent interaction.")
    }
    out_dir = "../results/sem"
    os.makedirs(out_dir, exist_ok=True)
    pd.DataFrame([failure_note]).to_csv(
        os.path.join(out_dir, "sem09_h7_product_indicator_result.csv"),
        index=False, encoding="utf-8-sig")
    import sys; sys.exit(0)

# ---- Bootstrap ----
N_BOOT = 2000
est_boot_min = round(N_BOOT * t_fit / 60, 1)
est_jack_min = round(N * t_fit / 60, 1)
print(f"\nBootstrap {N_BOOT}: ~{est_boot_min} min")
print(f"Jackknife  {N}: ~{est_jack_min} min")
print(f"Total expected: ~{est_boot_min + est_jack_min:.1f} min")

BETA_KEYS = list(betas_obs.keys())
COND_KEYS = list(cond_obs.keys())

boot_b = {k: np.full(N_BOOT, np.nan) for k in BETA_KEYS}
boot_c = {k: np.full(N_BOOT, np.nan) for k in COND_KEYS}
jack_b = {k: np.full(N, np.nan) for k in BETA_KEYS}
jack_c = {k: np.full(N, np.nan) for k in COND_KEYS}

rng = np.random.default_rng(42)
t_b0 = time.time()
n_fail = 0
print(f"\nBootstrap ({N_BOOT})...", flush=True)
for i in range(N_BOOT):
    idx = rng.integers(0, N, size=N)
    try:
        b = get_all_betas(df.iloc[idx].reset_index(drop=True))
        c = compute_cond_indirect(b)
        for k in BETA_KEYS: boot_b[k][i] = b[k]
        for k in COND_KEYS: boot_c[k][i] = c[k]
    except Exception:
        n_fail += 1
    if (i+1) % 400 == 0:
        print(f"  {i+1}/{N_BOOT} ({time.time()-t_b0:.0f}s, fails={n_fail})", flush=True)

t_boot = time.time() - t_b0
print(f"Bootstrap done: {t_boot:.1f}s, failures: {n_fail}", flush=True)

t_j0 = time.time()
n_jfail = 0
print(f"\nJackknife ({N})...", flush=True)
for i in range(N):
    idx = np.concatenate([np.arange(i), np.arange(i+1, N)])
    try:
        b = get_all_betas(df.iloc[idx].reset_index(drop=True))
        c = compute_cond_indirect(b)
        for k in BETA_KEYS: jack_b[k][i] = b[k]
        for k in COND_KEYS: jack_c[k][i] = c[k]
    except Exception:
        n_jfail += 1
    if (i+1) % 400 == 0:
        print(f"  {i+1}/{N} ({time.time()-t_j0:.0f}s, fails={n_jfail})", flush=True)

t_jack = time.time() - t_j0
print(f"Jackknife done: {t_jack:.1f}s, failures: {n_jfail}", flush=True)

n_valid = np.isfinite(boot_c["int_coef"]).sum()
print(f"Valid bootstrap samples: {n_valid}/{N_BOOT}")

# ---- Results ----
print("\n[H7 INTERACTION RESULTS -- Method (a) Product Indicator]")
print(f"{'Effect':<22} {'Est':>8} {'BCa_lo':>8} {'BCa_hi':>8} {'0_BCa':>6}")

rows_h7 = []
key_map = {
    "int_coef":     "OI_EL->UPB (interaction)",
    "ie_eq_low":    "IE equity at EL-1SD",
    "ie_eq_high":   "IE equity at EL+1SD",
    "ie_incl_low":  "IE incl at EL-1SD",
    "ie_incl_high": "IE incl at EL+1SD",
    "slope_low":    "OI slope at EL-1SD",
    "slope_high":   "OI slope at EL+1SD",
}
for key, label in key_map.items():
    est = cond_obs[key]
    blo, bhi = bca_ci(boot_c[key], est, jack_c[key])
    zi = "yes" if (np.isnan(blo) or blo <= 0 <= bhi) else "no"
    print(f"  {label:<22} {est:>8.4f} {blo:>8.4f} {bhi:>8.4f} {zi:>6}")
    rows_h7.append({"effect": label, "est": round(est, 4),
                    "bca_lo": round(blo, 4) if not np.isnan(blo) else None,
                    "bca_hi": round(bhi, 4) if not np.isnan(bhi) else None,
                    "zero_in_bca": zi})

# ---- Model fit ----
st_full = calc_stats(m_check).iloc[0]
print(f"\n[Model fit (product indicator)]")
print(f"  chi2({int(st_full['DoF'])}) = {st_full['chi2']:.2f}")
print(f"  CFI={st_full['CFI']:.4f}, TLI={st_full['TLI']:.4f}, RMSEA={st_full['RMSEA']:.4f}")

# Save
out_dir = "../results/sem"
os.makedirs(out_dir, exist_ok=True)

df_h7 = pd.DataFrame(rows_h7)
fit_info = {"chi2": round(float(st_full["chi2"]),2), "df": int(st_full["DoF"]),
            "CFI": round(float(st_full["CFI"]),4), "TLI": round(float(st_full["TLI"]),4),
            "RMSEA": round(float(st_full["RMSEA"]),4), "n_boot": N_BOOT,
            "n_valid": int(n_valid), "n_jfail": int(n_jfail),
            "boot_time_s": round(t_boot,1), "jack_time_s": round(t_jack,1)}

df_h7.to_csv(os.path.join(out_dir, "sem09_h7_product_indicator_result.csv"),
             index=False, encoding="utf-8-sig")
pd.DataFrame([fit_info]).to_csv(
    os.path.join(out_dir, "sem09_h7_product_indicator_fit.csv"),
    index=False, encoding="utf-8-sig")

md = f"""# H7 잠재 상호작용: Method (a) 곱셈지표 (Product Indicator)

## 방법 명세

- **방법**: 이중평균중심화 곱셈지표 (Lin et al., 2010 기반)
- **지표 구성**: matched-pairs, Y1_i(OI) x Y11_i(EL) for i=1..5 (5 쌍)
- **평균중심화**: 각 문항을 표본 평균에서 차감 후 곱
- **Y1_6**: OI 고유 지표로만 포함 (EL 대응 문항 없음)
- **제약 여부**: **비제약 (unconstrained)** — semopy에서 오차분산 고정 불가
  (완전 제약 PI 모형은 Mplus 필요)
- **모형**: 6요인 CFA + oi_el 잠재요인(5 PI) + 구조방정식

## 부트스트랩 설정

- 부트스트랩: {N_BOOT}회, 잭나이프: {N}회 (BCa), 시드=42
- 유효 반복: {n_valid}/{N_BOOT}회
- 총 소요: {round((t_boot+t_jack)/60,1)}분

## 적합도

| chi2 | df | CFI | TLI | RMSEA |
|-----:|---:|----:|----:|------:|
| {fit_info['chi2']} | {fit_info['df']} | {fit_info['CFI']} | {fit_info['TLI']} | {fit_info['RMSEA']} |

## H7 상호작용 및 조건부 간접효과 (BCa 95% CI)

OLS 기준: 상호작용 beta=-.062 (p=.011), 조건부 간접효과 낮음=.095, 높음=.046.

{df_h7.to_markdown(index=False)}

*Note.* 조건부 간접효과: EL +/-1SD는 잠재 EL 표준편차 단위 (=1).
SEM beta_std는 OLS 비표준화와 단위 상이; 방향과 유의성 비교.

## 방법론적 평가

**장점**:
- 측정오차 보정된 상호작용 추정 (measurement error correction in interaction)
- 잠재변수 간 순수 상호작용 표현

**단점**:
- 비제약 PI는 부하량-오차 구조 이론적 불일치 (Kenny & Judd, 1984 원래 요구사항 미충족)
- 곱 지표의 비정규성 무처리 (bootstrap으로 부분 보완)
- 곱 지표가 원래 문항과 공분산 구조 가짐 -> 식별 취약
- Mplus LMS(Klein & Moosbrugger, 2000)이 표준; semopy는 근사치

**SSCI 통용도**: 비제약 PI는 다수 저널 수락 (Kline, 2015 인용 가능), 단 제약 미충족 명기 필요.
"""

with open(os.path.join(out_dir, "sem09_h7_product_indicator_result.md"), "w", encoding="utf-8") as f:
    f.write(md)

total_min = round((t_boot + t_jack) / 60, 1)
print(f"\nSaved to {out_dir}")
print(f"Total time: {total_min} min")
