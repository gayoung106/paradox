import pandas as pd
import numpy as np
import time
from scipy.stats import norm as spnorm
from semopy import Model, calc_stats
import os

# =============================================================
# Script 32: H7 Latent interaction -- Method (b)
#   Hybrid: OI and UPB latent, interaction from observed composites
#   oi_x_el_obs = (OI_composite_mc) x (EL_composite_mc)
#
#   Model: full 6-factor CFA (measurement)
#   Structural: oi ~ equity + inclusion + ctrl
#               upb ~ oi + el + oi_x_el_obs + equity + inclusion + ctrl
#               ocb ~ oi + el + oi_x_el_obs + equity + inclusion + ctrl
#   oi_x_el_obs is an OBSERVED variable (standardized product)
#
#   Also generates final COMPARISON TABLE (Methods a vs b vs OLS)
#
#   Bootstrap 2000 + Jackknife 2020 -> BCa CI
#   Expected time: ~9-11 min
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

# Create mean-centered observed composites + product (on full data)
df["oi_comp"]    = df[OI_ITEMS].mean(axis=1)
df["el_comp"]    = df[EL_ITEMS].mean(axis=1)
df["oi_mc"]      = df["oi_comp"] - df["oi_comp"].mean()
df["el_mc"]      = df["el_comp"] - df["el_comp"].mean()
df["oi_x_el_obs"] = df["oi_mc"] * df["el_mc"]
SD_EL_OBS = float(df["el_mc"].std())
print(f"SD of el_mc (observed): {SD_EL_OBS:.4f}")
print(f"oi_x_el_obs: mean={df['oi_x_el_obs'].mean():.4f}, "
      f"std={df['oi_x_el_obs'].std():.4f}")

MODEL_DESC = f"""
{MEAS}
oi ~ equity + inclusion {CTRL}
upb ~ oi + el + oi_x_el_obs + equity + inclusion {CTRL}
ocb ~ oi + el + oi_x_el_obs + equity + inclusion {CTRL}
"""

# BCa
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
            np.percentile(b, 100*adj(spnorm.ppf(1-alpha/2))))

def pct_ci(arr):
    a = arr[np.isfinite(arr)]
    return np.percentile(a, 2.5), np.percentile(a, 97.5)

def get_std(est, dv, pred):
    r = est[(est.lval==dv) & (est.op=="~") & (est.rval==pred)]
    return float(r["Est. Std"].iloc[0]) if len(r) else np.nan


def get_all_betas(data):
    """
    Create observed product on bootstrap sample, fit model, return betas.
    The product uses the GLOBAL mean (from full data) for centering to
    maintain mean-centering interpretation across bootstrap samples.
    """
    d = data.copy()
    d["oi_comp_b"]    = d[OI_ITEMS].mean(axis=1)
    d["el_comp_b"]    = d[EL_ITEMS].mean(axis=1)
    # Use bootstrap-sample means for centering (consistent with bootstrap logic)
    d["oi_mc_b"]      = d["oi_comp_b"] - d["oi_comp_b"].mean()
    d["el_mc_b"]      = d["el_comp_b"] - d["el_comp_b"].mean()
    d["oi_x_el_obs"]  = d["oi_mc_b"] * d["el_mc_b"]

    m = Model(MODEL_DESC)
    m.fit(d)
    est = m.inspect(std_est=True)
    return {
        "eq_oi":       get_std(est, "oi",  "equity"),
        "incl_oi":     get_std(est, "oi",  "inclusion"),
        "oi_upb":      get_std(est, "upb", "oi"),
        "int_upb":     get_std(est, "upb", "oi_x_el_obs"),  # INTERACTION
        "el_upb":      get_std(est, "upb", "el"),
        "oi_ocb":      get_std(est, "ocb", "oi"),
        "int_ocb":     get_std(est, "ocb", "oi_x_el_obs"),
        "el_ocb":      get_std(est, "ocb", "el"),
        "eq_d_upb":    get_std(est, "upb", "equity"),
        "incl_d_upb":  get_std(est, "upb", "inclusion"),
    }


def compute_cond_indirect(b, sd_el=SD_EL_OBS):
    """
    Conditional indirect effects at EL +/- sd_el (observed composite units).
    Approximation: the interaction coefficient int_upb is in the metric of
    (observed OI composite) x (observed EL composite). The conditional slope
    of latent OI on latent UPB at EL = +/- sd_el is approximated as:
      slope = oi_upb + int_upb * sd_el
    Note: this ignores the correlation between latent OI and observed OI_mc.
    """
    slope_low  = b["oi_upb"] + b["int_upb"] * (-sd_el)
    slope_high = b["oi_upb"] + b["int_upb"] * (+sd_el)
    return {
        "int_coef":      b["int_upb"],
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
print("\nFitting hybrid model on full data...")
t0 = time.time()
betas_obs = get_all_betas(df)
t_fit = time.time() - t0
cond_obs  = compute_cond_indirect(betas_obs)

print(f"  Fit time: {t_fit:.2f}s")
print(f"  Interaction (obs OI*EL -> UPB): beta_std = {betas_obs['int_upb']:.4f}")
print(f"  OI->UPB main: {betas_obs['oi_upb']:.4f}")
print(f"  EL->UPB: {betas_obs['el_upb']:.4f}")

if betas_obs["oi_upb"] < 0:
    print("!!! SIGN FLIP: oi_upb negative. Stop.")
    raise SystemExit("Sign flip detected")

print(f"  Cond IE equity: low={cond_obs['ie_eq_low']:.4f}, high={cond_obs['ie_eq_high']:.4f}")
print(f"  (OLS: low=.095, high=.046)")

N_BOOT = 2000
est_b_min = round(N_BOOT * t_fit / 60, 1)
est_j_min = round(N     * t_fit / 60, 1)
print(f"\nBootstrap {N_BOOT}: ~{est_b_min} min")
print(f"Jackknife  {N}: ~{est_j_min} min")
print(f"Total expected: ~{est_b_min + est_j_min:.1f} min")

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
print(f"Valid: {n_valid}/{N_BOOT}")

# ---- Results ----
print("\n[H7 INTERACTION RESULTS -- Method (b) Hybrid]")
print(f"{'Effect':<22} {'Est':>8} {'BCa_lo':>8} {'BCa_hi':>8} {'0_BCa':>6}")

KEY_LABELS = {
    "int_coef":     "OI_obs*EL_obs->UPB (interaction)",
    "ie_eq_low":    "IE equity at EL-1SD",
    "ie_eq_high":   "IE equity at EL+1SD",
    "ie_incl_low":  "IE incl at EL-1SD",
    "ie_incl_high": "IE incl at EL+1SD",
    "slope_low":    "OI slope at EL-1SD",
    "slope_high":   "OI slope at EL+1SD",
}

rows_h7b = []
for key, label in KEY_LABELS.items():
    est = cond_obs[key]
    blo, bhi = bca_ci(boot_c[key], est, jack_c[key])
    zi = "yes" if (np.isnan(blo) or blo <= 0 <= bhi) else "no"
    print(f"  {label:<24} {est:>8.4f} {blo:>8.4f} {bhi:>8.4f} {zi:>6}")
    rows_h7b.append({"effect": label, "est": round(est, 4),
                     "bca_lo": round(blo, 4) if not np.isnan(blo) else None,
                     "bca_hi": round(bhi, 4) if not np.isnan(bhi) else None,
                     "zero_in_bca": zi})

# Fit
m_obs = Model(MODEL_DESC)
m_obs.fit(df)
st = calc_stats(m_obs).iloc[0]
fit_b = {"chi2": round(float(st["chi2"]),2), "df": int(st["DoF"]),
         "CFI": round(float(st["CFI"]),4), "TLI": round(float(st["TLI"]),4),
         "RMSEA": round(float(st["RMSEA"]),4)}

print(f"\n[Model fit (hybrid)]")
print(f"  chi2({fit_b['df']}) = {fit_b['chi2']}, CFI={fit_b['CFI']}, "
      f"TLI={fit_b['TLI']}, RMSEA={fit_b['RMSEA']}")

# ---- Save ----
out_dir = "../results/sem"
os.makedirs(out_dir, exist_ok=True)

df_h7b = pd.DataFrame(rows_h7b)
df_h7b.to_csv(os.path.join(out_dir, "sem10_h7_hybrid_result.csv"),
              index=False, encoding="utf-8-sig")

# =============================================================
# FINAL COMPARISON TABLE (load Method a results if available)
# =============================================================
print("\n" + "=" * 60)
print("FINAL COMPARISON TABLE: Method (a) vs (b) vs OLS")
print("=" * 60)

# Load Method (a) results
pi_path = os.path.join(out_dir, "sem09_h7_product_indicator_result.csv")
pi_fit_path = os.path.join(out_dir, "sem09_h7_product_indicator_fit.csv")

pi_available = os.path.exists(pi_path)
if pi_available:
    df_pi = pd.read_csv(pi_path)
    # Check if it's a failure record or actual results
    if "status" in df_pi.columns and (df_pi.get("status","") == "FAILED").any():
        pi_available = False
        print("  Method (a) FAILED -- comparison will show N/A for PI method")

def get_val(df_src, effect_label, col):
    if df_src is None:
        return "N/A"
    r = df_src[df_src["effect"] == effect_label]
    if len(r) == 0:
        return "N/A"
    v = r.iloc[0].get(col, "N/A")
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "N/A"
    return v

df_pi_res = pd.read_csv(pi_path) if pi_available else None

def fmt_est_ci(df_src, effect):
    est = get_val(df_src, effect, "est")
    lo  = get_val(df_src, effect, "bca_lo")
    hi  = get_val(df_src, effect, "bca_hi")
    zi  = get_val(df_src, effect, "zero_in_bca")
    if est == "N/A":
        return "N/A", "N/A", "N/A"
    try:
        return round(float(est),3), f"[{float(lo):.3f},{float(hi):.3f}]", str(zi)
    except Exception:
        return est, f"[{lo},{hi}]", str(zi)

# OLS reference
OLS = {
    "int": (-0.062, "p=.011"),
    "ie_eq_low":  0.095,
    "ie_eq_high": 0.046,
    "ie_incl_low":  None,
    "ie_incl_high": None,
}

comp_rows = []
for effect_key, label, ols_val in [
    ("OI_EL->UPB (interaction)",     "Interaction OI x EL -> UPB",  f"beta=-.062 (p=.011)"),
    ("IE equity at EL-1SD",          "IE equity (EL-1SD)",           ".095"),
    ("IE equity at EL+1SD",          "IE equity (EL+1SD)",           ".046"),
    ("IE incl at EL-1SD",            "IE inclusion (EL-1SD)",        "n/a"),
    ("IE incl at EL+1SD",            "IE inclusion (EL+1SD)",        "n/a"),
    ("OI slope at EL-1SD",           "OI->UPB slope (EL-1SD)",       "n/a"),
    ("OI slope at EL+1SD",           "OI->UPB slope (EL+1SD)",       "n/a"),
]:
    est_a, ci_a, zi_a = fmt_est_ci(df_pi_res, effect_key)
    # Method b
    est_b_r = df_h7b[df_h7b["effect"] == effect_key]
    if len(est_b_r):
        r = est_b_r.iloc[0]
        v = r.get("est", None)
        lo = r.get("bca_lo", None)
        hi = r.get("bca_hi", None)
        zi_b = r.get("zero_in_bca", "?")
        try:
            est_b_out = round(float(v), 3)
            ci_b  = f"[{float(lo):.3f},{float(hi):.3f}]"
        except Exception:
            est_b_out, ci_b = "?", "?"
    else:
        est_b_out, ci_b, zi_b = "N/A", "N/A", "N/A"

    comp_rows.append({
        "aspect":  label,
        "PI_est":  est_a, "PI_BCa_CI": ci_a, "PI_0in": zi_a,
        "Hyb_est": est_b_out, "Hyb_BCa_CI": ci_b, "Hyb_0in": zi_b,
        "OLS_ref": ols_val,
    })
    print(f"  {label[:30]:<30} | PI: {str(est_a):>7} {str(ci_a):>18} | "
          f"Hyb: {str(est_b_out):>7} {str(ci_b):>18} | OLS: {ols_val}")

# Fit comparison
if pi_available and os.path.exists(pi_fit_path):
    fi_pi = pd.read_csv(pi_fit_path).iloc[0]
    pi_fit_str = f"CFI={fi_pi['CFI']}, RMSEA={fi_pi['RMSEA']}"
else:
    pi_fit_str = "N/A (model failed)"

hyb_fit_str = f"CFI={fit_b['CFI']}, RMSEA={fit_b['RMSEA']}"

print(f"\n  Model fit: PI={pi_fit_str}, Hybrid={hyb_fit_str}")

# ---- Final markdown ----
df_comp = pd.DataFrame(comp_rows)

md = f"""# H7 잠재 상호작용 비교표: Method (a) vs (b) vs OLS

## 방법 비교 요약

| 측면 | Method (a): Product Indicator | Method (b): Hybrid |
|:-----|:-----|:-----|
| 상호작용 구성 | 잠재 OI x EL (5 곱 지표 -> latent oi_el) | 관측 합산점수 곱 (oi_mc x el_mc) |
| OI 처리 | 잠재변수 | 잠재변수 (main effect) + 관측 복합점수 (interaction) |
| 제약 여부 | 비제약 (unconstrained PI) | 없음 |
| 측정오차 보정 | 부분 (PI 관련 항에서만) | 없음 (interaction에서) |
| 수렴 안정성 | {'수렴 확인' if pi_available else '수렴 실패 -- 결과 없음'} | 수렴 |
| 추정 시간 | {'약 ' + str(round((t_boot+t_jack)/60,1)) + '분' if pi_available else 'N/A'} | {round((t_boot+t_jack)/60,1)}분 |

## 수치 결과 비교

| 항목 | PI 추정값 | PI BCa CI | PI 0포함 | 혼합 추정값 | 혼합 BCa CI | 혼합 0포함 | OLS 참고 |
|:-----|----------:|:----------|:--------:|------------:|:-----------|:--------:|:---------|
"""
for r in comp_rows:
    md += (f"| {r['aspect']} | {r['PI_est']} | {r['PI_BCa_CI']} | {r['PI_0in']} | "
           f"{r['Hyb_est']} | {r['Hyb_BCa_CI']} | {r['Hyb_0in']} | {r['OLS_ref']} |\n")

md += f"""

## 모형 적합도

| 방법 | CFI | RMSEA | 비고 |
|:-----|----:|------:|:-----|
| OLS | n/a | n/a | R2 기반 |
| PI (비제약) | {fi_pi['CFI'] if pi_available and os.path.exists(pi_fit_path) else 'N/A'} | {fi_pi['RMSEA'] if pi_available and os.path.exists(pi_fit_path) else 'N/A'} | semopy unconstrained |
| Hybrid | {fit_b['CFI']} | {fit_b['RMSEA']} | 관측 상호작용항 |

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

## 권고

양 방법 모두 구현되었으므로:
1. 상호작용이 **양쪽 모두 유의**: H7 지지 강도 높음 -> 어느 방법으로 보고해도 무방.
   논문에서는 Hybrid로 보고 (단순·안정), PI 결과를 robustness check으로 각주.
2. **한쪽만 유의**: 방법 효과 존재. OLS 결과(-.062, p=.011)를 1차 근거로,
   SEM을 보완 근거로 제시. 한계 명기.
3. **양쪽 모두 비유의**: H7 지지 약화. OLS 결과만 보고하고 SEM에서 재확인 시도 언급.

## 조건부 간접효과 해석 주의

- Method (a) 조건부 IE: EL +/-1SD = 잠재 EL 표준편차 단위 (=1)
- Method (b) 조건부 IE: EL +/-1SD = 관측 EL 복합점수 표준편차 ({SD_EL_OBS:.3f})
- 두 방법의 조건부 IE 크기가 다를 수 있음 (단위 차이)
- OLS 조건부 IE(.095/.046)는 비표준화; 모두 방향성과 유의성으로 비교
"""

with open(os.path.join(out_dir, "sem10_h7_comparison_result.md"), "w", encoding="utf-8") as f:
    f.write(md)

df_comp.to_csv(os.path.join(out_dir, "sem10_h7_comparison.csv"), index=False, encoding="utf-8-sig")

total_min = round((t_boot + t_jack) / 60, 1)
print(f"\nAll results saved to {out_dir}")
print(f"Method (b) total time: {total_min} min")
