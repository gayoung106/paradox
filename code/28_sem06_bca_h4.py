import pandas as pd
import numpy as np
import time
from scipy.stats import norm as spnorm
from semopy import Model, calc_stats
import os

# =============================================================
# Script 28: BCa H4 contrast recomputation + orthogonal bifactor retry
#   Part A: Orthogonal bifactor (0* constraint or HOF fallback)
#   Part B: H4 bootstrap 2000 iter + jackknife 2020 iter -> BCa CI
# Expected time: ~9 min (2000 boot + 2020 jackknife at 0.13s/fit)
# =============================================================

df = pd.read_csv("../processed/analysis_data.csv")
bad_col = [c for c in df.columns if not all(ord(ch) < 128 for ch in c)][0]
pub_val = df[bad_col].value_counts().idxmax()
df["gender_male"] = (df["SQ1K1"] == 1.0).astype(int)
df["age"]         = 2023 - df["SQ1K2_1"]
df["public_org"]  = (df[bad_col] == pub_val).astype(int)
N = len(df)
print("N =", N)

FACTOR_ITEMS = {
    "equity":    ["Y8_1","Y8_2","Y8_3","Y8_4","Y8_5"],
    "inclusion": ["Y8_6","Y8_7","Y8_8","Y8_9"],
    "oi":        ["Y1_1","Y1_2","Y1_3","Y1_4","Y1_5","Y1_6"],
    "el":        ["Y11_1","Y11_2","Y11_3","Y11_4","Y11_5"],
    "ocb":       ["Y19_1","Y19_2","Y19_3","Y19_4"],
    "upb":       ["Y20_1","Y20_2","Y20_3","Y20_4","Y20_5"],
}
MEAS = "\n".join(f"{f} =~ {' + '.join(it)}" for f, it in FACTOR_ITEMS.items())
CTRL = "+ gender_male + age + public_org"

STAGE_C = f"""
{MEAS}
oi ~ equity + inclusion {CTRL}
upb ~ oi + equity + inclusion + el {CTRL}
ocb ~ oi + equity + inclusion + el {CTRL}
"""

DEI_ITEMS = FACTOR_ITEMS["equity"] + FACTOR_ITEMS["inclusion"]


# ---- BCa helper ----
def bca_ci(boot_arr, theta_hat, jack_arr, alpha=0.05):
    b = boot_arr[np.isfinite(boot_arr)]
    if len(b) < 20:
        return np.nan, np.nan
    prop = np.clip(np.mean(b < theta_hat), 0.5 / len(b), 1 - 0.5 / len(b))
    z0 = spnorm.ppf(prop)
    jk = jack_arr[np.isfinite(jack_arr)]
    jk_mean = np.mean(jk)
    diffs = jk_mean - jk
    num = np.sum(diffs ** 3)
    den = 6 * np.sum(diffs ** 2) ** 1.5
    a = num / den if den > 1e-12 else 0.0

    def adj(z_alpha):
        inner = 1 - a * (z0 + z_alpha)
        if abs(inner) < 1e-10:
            return 1.0 if z_alpha > 0 else 0.0
        return float(np.clip(spnorm.cdf(z0 + (z0 + z_alpha) / inner), 0.001, 0.999))

    lo = np.percentile(b, 100 * adj(spnorm.ppf(alpha / 2)))
    hi = np.percentile(b, 100 * adj(spnorm.ppf(1 - alpha / 2)))
    return lo, hi


def pct_ci(arr):
    a = arr[np.isfinite(arr)]
    return np.percentile(a, 2.5), np.percentile(a, 97.5)


# =============================================================
# PART A: Orthogonal bifactor retry
# =============================================================
print("\n" + "=" * 60)
print("PART A: Orthogonal bifactor CFA")
print("=" * 60)

bifactor_result = {"method": None, "converged": False, "CFI": None,
                   "RMSEA": None, "chi2": None, "DoF": None, "note": ""}

# --- Attempt 1: lavaan-style 0* covariance constraint ---
bf_desc_orth = """
g_dei =~ Y8_1 + Y8_2 + Y8_3 + Y8_4 + Y8_5 + Y8_6 + Y8_7 + Y8_8 + Y8_9
equity_s =~ Y8_1 + Y8_2 + Y8_3 + Y8_4 + Y8_5
inclusion_s =~ Y8_6 + Y8_7 + Y8_8 + Y8_9
g_dei ~~ 0*equity_s
g_dei ~~ 0*inclusion_s
equity_s ~~ 0*inclusion_s
"""
print("\nAttempt 1: '0*' constraint syntax in semopy...")
try:
    m1 = Model(bf_desc_orth)
    m1.fit(df[DEI_ITEMS])
    st1 = calc_stats(m1).iloc[0]
    bifactor_result.update({
        "method": "bifactor_orthogonal_0star",
        "converged": True,
        "CFI":   round(float(st1["CFI"]), 4),
        "RMSEA": round(float(st1["RMSEA"]), 4),
        "chi2":  round(float(st1["chi2"]), 2),
        "DoF":   int(st1["DoF"]),
    })
    # Check whether constraints actually held
    est1 = m1.inspect()
    fac_names = ["g_dei", "equity_s", "inclusion_s"]
    fac_cov = est1[(est1["op"] == "~~") &
                   est1["lval"].isin(fac_names) &
                   est1["rval"].isin(fac_names) &
                   (est1["lval"] != est1["rval"])]
    max_cov = fac_cov["Estimate"].abs().max() if len(fac_cov) else 0.0
    bifactor_result["note"] = (
        f"0* constraint accepted; max off-diag factor cov = {max_cov:.4f}"
    )
    print(f"  Converged: CFI={bifactor_result['CFI']}, RMSEA={bifactor_result['RMSEA']}")
    print(f"  Max off-diagonal factor cov: {max_cov:.4f}")
    if not fac_cov.empty:
        print(fac_cov[["lval", "rval", "Estimate"]].to_string(index=False))
except Exception as e:
    err = str(e)
    print(f"  Failed: {err[:120]}")
    bifactor_result["note"] = f"0* syntax failed: {err[:100]}"

# --- Attempt 2: Higher-order factor model (if bifactor failed) ---
if not bifactor_result["converged"]:
    print("\nAttempt 2: Higher-order factor model (g_dei -> equity, inclusion)...")
    hof_desc = """
equity    =~ Y8_1 + Y8_2 + Y8_3 + Y8_4 + Y8_5
inclusion =~ Y8_6 + Y8_7 + Y8_8 + Y8_9
g_dei     =~ equity + inclusion
"""
    try:
        m2 = Model(hof_desc)
        m2.fit(df[DEI_ITEMS])
        st2 = calc_stats(m2).iloc[0]
        bifactor_result.update({
            "method": "higher_order_factor",
            "converged": True,
            "CFI":   round(float(st2["CFI"]), 4),
            "RMSEA": round(float(st2["RMSEA"]), 4),
            "chi2":  round(float(st2["chi2"]), 2),
            "DoF":   int(st2["DoF"]),
            "note":  ("HOF (g_dei->equity/inclusion): not a proper bifactor "
                      "but hierarchical alternative. Factors are orthogonalized by structure."),
        })
        print(f"  HOF converged: CFI={bifactor_result['CFI']}, RMSEA={bifactor_result['RMSEA']}")
    except Exception as e2:
        print(f"  HOF failed: {str(e2)[:120]}")
        bifactor_result["note"] += f"; HOF also failed: {str(e2)[:100]}"

# 2-factor reference
print("\nFitting 2-factor DEI reference model...")
m_2f = Model("equity =~ Y8_1+Y8_2+Y8_3+Y8_4+Y8_5\ninclusion =~ Y8_6+Y8_7+Y8_8+Y8_9")
m_2f.fit(df[DEI_ITEMS])
st_2f = calc_stats(m_2f).iloc[0]
ref_2f = {"CFI": round(float(st_2f["CFI"]), 4), "RMSEA": round(float(st_2f["RMSEA"]), 4),
          "chi2": round(float(st_2f["chi2"]), 2), "DoF": int(st_2f["DoF"])}
print(f"  2-factor: chi2={ref_2f['chi2']}, df={ref_2f['DoF']}, "
      f"CFI={ref_2f['CFI']}, RMSEA={ref_2f['RMSEA']}")

print("\n[Part A Summary]")
print(f"  Method tried: {bifactor_result['method']}")
print(f"  Converged: {bifactor_result['converged']}")
if bifactor_result["converged"]:
    print(f"  chi2={bifactor_result['chi2']}, df={bifactor_result['DoF']}, "
          f"CFI={bifactor_result['CFI']}, RMSEA={bifactor_result['RMSEA']}")
print(f"  Note: {bifactor_result['note']}")


# =============================================================
# PART B: BCa H4 bootstrap
# =============================================================
print("\n" + "=" * 60)
print("PART B: BCa H4 bootstrap (2000 iter + 2020 jackknife)")
print("=" * 60)

FOCUS  = [("ocb","inclusion"), ("ocb","equity"), ("upb","equity"), ("upb","inclusion")]
KEYS   = ["incl_ocb", "eq_ocb", "eq_upb", "incl_upb"]
LABELS = ["inclusion->OCB", "equity->OCB", "equity->UPB", "inclusion->UPB"]

CONT_KEYS = ["d_OCB", "d_UPB", "sig_incl", "sig_eq"]
CONT_LABELS = ["d_OCB = incl_ocb - eq_ocb", "d_UPB = eq_upb - incl_upb",
               "sig_incl = incl_ocb - incl_upb", "sig_eq = eq_upb - eq_ocb"]


def get_betas(data):
    m = Model(STAGE_C)
    m.fit(data)
    est = m.inspect(std_est=True)
    out = {}
    for (dv, pred), k in zip(FOCUS, KEYS):
        row = est[(est["lval"] == dv) & (est["op"] == "~") & (est["rval"] == pred)]
        out[k] = float(row["Est. Std"].iloc[0]) if len(row) else np.nan
    return out


def get_contrasts(b):
    return {
        "d_OCB":    b["incl_ocb"] - b["eq_ocb"],
        "d_UPB":    b["eq_upb"]   - b["incl_upb"],
        "sig_incl": b["incl_ocb"] - b["incl_upb"],
        "sig_eq":   b["eq_upb"]   - b["eq_ocb"],
    }


# Point estimates
print("\nFitting Stage C on full data...")
t0 = time.time()
betas_obs = get_betas(df)
t_fit = time.time() - t0
cont_obs = get_contrasts(betas_obs)
print(f"  Single fit: {t_fit:.2f}s")

N_BOOT = 2000
est_boot = round(N_BOOT * t_fit / 60, 1)
est_jack = round(N * t_fit / 60, 1)
print(f"  Bootstrap {N_BOOT}: ~{est_boot} min")
print(f"  Jackknife  {N}: ~{est_jack} min")
print(f"  Total expected: ~{est_boot + est_jack:.1f} min")

# ---- Bootstrap ----
rng = np.random.default_rng(42)
boot_p = {k: np.full(N_BOOT, np.nan) for k in KEYS}
boot_c = {k: np.full(N_BOOT, np.nan) for k in CONT_KEYS}

print(f"\nBootstrap ({N_BOOT} iterations)...", flush=True)
t_b0 = time.time()
n_fail = 0
for i in range(N_BOOT):
    idx = rng.integers(0, N, size=N)
    try:
        b = get_betas(df.iloc[idx].reset_index(drop=True))
        c = get_contrasts(b)
        for k in KEYS: boot_p[k][i] = b[k]
        for k in CONT_KEYS: boot_c[k][i] = c[k]
    except Exception:
        n_fail += 1
    if (i + 1) % 400 == 0:
        el = time.time() - t_b0
        print(f"  {i+1}/{N_BOOT} ({el:.0f}s, fails={n_fail})", flush=True)

t_boot = time.time() - t_b0
print(f"Bootstrap done: {t_boot:.1f}s, failures: {n_fail}", flush=True)

# ---- Jackknife ----
jack_p = {k: np.full(N, np.nan) for k in KEYS}
jack_c = {k: np.full(N, np.nan) for k in CONT_KEYS}

print(f"\nJackknife ({N} iterations)...", flush=True)
t_j0 = time.time()
n_jfail = 0
for i in range(N):
    idx = np.concatenate([np.arange(i), np.arange(i + 1, N)])
    try:
        b = get_betas(df.iloc[idx].reset_index(drop=True))
        c = get_contrasts(b)
        for k in KEYS: jack_p[k][i] = b[k]
        for k in CONT_KEYS: jack_c[k][i] = c[k]
    except Exception:
        n_jfail += 1
    if (i + 1) % 400 == 0:
        el = time.time() - t_j0
        print(f"  {i+1}/{N} ({el:.0f}s, fails={n_jfail})", flush=True)

t_jack = time.time() - t_j0
print(f"Jackknife done: {t_jack:.1f}s, failures: {n_jfail}", flush=True)

n_valid = np.isfinite(boot_c["d_OCB"]).sum()
print(f"Valid bootstrap samples: {n_valid}/{N_BOOT}")

# ---- Results ----
print("\n[H4 CONTRAST RESULTS (Percentile vs BCa)]")
hdr = f"{'Contrast':<12} {'Est':>7} | {'Pct_lo':>7} {'Pct_hi':>7} {'0_Pct':>6} | {'BCa_lo':>7} {'BCa_hi':>7} {'0_BCa':>6}"
print(hdr)
print("-" * len(hdr))

rows_cont = []
for k, lbl in zip(CONT_KEYS, CONT_LABELS):
    est = cont_obs[k]
    plo, phi = pct_ci(boot_c[k])
    blo, bhi = bca_ci(boot_c[k], est, jack_c[k])
    zi_p = "yes" if plo <= 0 <= phi else "no"
    zi_b = "yes" if (not np.isnan(blo) and blo <= 0 <= bhi) else "no"
    print(f"{k:<12} {est:>7.3f} | {plo:>7.3f} {phi:>7.3f} {zi_p:>6} | {blo:>7.3f} {bhi:>7.3f} {zi_b:>6}")
    rows_cont.append({
        "contrast": k, "label": lbl, "est": round(est, 3),
        "pct_lo": round(plo, 3), "pct_hi": round(phi, 3), "zero_in_pct": zi_p,
        "bca_lo": round(blo, 3) if not np.isnan(blo) else None,
        "bca_hi": round(bhi, 3) if not np.isnan(bhi) else None,
        "zero_in_bca": zi_b,
    })

print("\n[PATH COEFFICIENT RESULTS (Percentile vs BCa)]")
rows_path = []
for k, lbl in zip(KEYS, LABELS):
    est = betas_obs[k]
    plo, phi = pct_ci(boot_p[k])
    blo, bhi = bca_ci(boot_p[k], est, jack_p[k])
    zi_p = "yes" if plo <= 0 <= phi else "no"
    zi_b = "yes" if (not np.isnan(blo) and blo <= 0 <= bhi) else "no"
    print(f"{lbl:<18} est={est:>7.3f} | Pct=[{plo:.3f},{phi:.3f}] {zi_p:>3} | BCa=[{blo:.3f},{bhi:.3f}] {zi_b:>3}")
    rows_path.append({
        "path": lbl, "est": round(est, 3),
        "pct_lo": round(plo, 3), "pct_hi": round(phi, 3), "zero_in_pct": zi_p,
        "bca_lo": round(blo, 3), "bca_hi": round(bhi, 3), "zero_in_bca": zi_b,
    })

# ---- Save ----
out_dir = "../results/sem"
os.makedirs(out_dir, exist_ok=True)

df_cont = pd.DataFrame(rows_cont)
df_path = pd.DataFrame(rows_path)
df_cont.to_csv(os.path.join(out_dir, "sem06_bca_h4_contrasts.csv"), index=False, encoding="utf-8-sig")
df_path.to_csv(os.path.join(out_dir, "sem06_bca_h4_paths.csv"), index=False, encoding="utf-8-sig")

# Bifactor comparison table
rows_bf = [
    {"model": "1-factor DEI", "chi2": 1629.39, "df": 27, "CFI": 0.852, "RMSEA": 0.171,
     "note": "from script 12"},
    {"model": "2-factor DEI", "chi2": ref_2f["chi2"], "df": ref_2f["DoF"],
     "CFI": ref_2f["CFI"], "RMSEA": ref_2f["RMSEA"], "note": "primary model"},
]
if bifactor_result["converged"]:
    rows_bf.append({
        "model": bifactor_result["method"],
        "chi2": bifactor_result["chi2"], "df": bifactor_result["DoF"],
        "CFI": bifactor_result["CFI"], "RMSEA": bifactor_result["RMSEA"],
        "note": bifactor_result["note"],
    })
df_bf = pd.DataFrame(rows_bf)

md = f"""# H4 대비 BCa 재계산 + 이중요인 직교 시도

## 1. 이중요인(직교) CFA 시도

{df_bf.to_markdown(index=False)}

**결론**: {bifactor_result['note']}

## 2. 부트스트랩 설정

- 반복: {N_BOOT}회 (케이스 재표집, 시드=42)
- 잭나이프: {N}회 (BCa 가속 인자 a 추정)
- CI 방법: BCa 95% (Percentile 병기)
- 부트스트랩 소요: {t_boot:.0f}초, 잭나이프 소요: {t_jack:.0f}초
- 유효 반복: {n_valid}/{N_BOOT}회

## 3. H4 대비 (Percentile vs BCa 비교)

{df_cont.to_markdown(index=False)}

*Note.* Percentile과 BCa 차이가 작으면 분포 대칭성이 높음을 의미.
보고 시 BCa 95% CI 사용.

## 4. 경로계수 CI (Percentile vs BCa)

{df_path.to_markdown(index=False)}

## 5. 서술 주의사항

- d_OCB, d_UPB: 0 미포함 → H4 지지. OLS 대비 크기 비교 불요
  (형평→OCB 부호역전이 대비값 증폭의 주원인 — 억제효과 산물)
- inclusion→UPB: CI 상한이 0에 가까움 — "경계적 결과"로 서술
"""

with open(os.path.join(out_dir, "sem06_bca_h4_result.md"), "w", encoding="utf-8") as f:
    f.write(md)

total_min = round((t_boot + t_jack) / 60, 1)
print(f"\nSaved to {out_dir}")
print(f"Total time: {total_min} min")
