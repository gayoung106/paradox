import pandas as pd
import numpy as np
import time
from scipy.stats import norm as spnorm
from semopy import Model, calc_stats
import os

# =============================================================
# Script 29: Mediation analysis H5 / H6
#
# (a) Simple mediation (one DEI at a time -> OI -> UPB)
#     2000 bootstrap, Percentile CI
#     OLS comparison: equity .048[.026,.070], inclusion .078[.053,.104]
#
# (b) Simultaneous mediation (both DEI -> OI -> UPB)
#     Extracted from Part (c) Stage C bootstrap
#     OLS comparison: equity .034[.020,.051], inclusion .038[.023,.056]
#     Difference .004[-.009,.018]
#
# (c) 4 indirect effects (both DEI x both outcomes, Stage C)
#     5000 bootstrap + 2020 jackknife, BCa CI
#     OLS comparison: incl->OCB .055, incl->UPB .038, eq->OCB .049, eq->UPB .034
#
# STOP RULE: if any of eq_oi, incl_oi, oi_upb, oi_ocb flips sign, stop and report.
#
# Expected time: ~7 min (Part A) + ~15 min (Part C) = ~22 min total
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

# Model descriptions
# Part A: single predictor, UPB only
DESC_EQ = f"""
{MEAS}
oi  ~ equity {CTRL}
upb ~ oi + equity {CTRL}
"""

DESC_INCL = f"""
{MEAS}
oi  ~ inclusion {CTRL}
upb ~ oi + inclusion {CTRL}
"""

# Part C (and B): full Stage C
DESC_C = f"""
{MEAS}
oi  ~ equity + inclusion {CTRL}
upb ~ oi + equity + inclusion + el {CTRL}
ocb ~ oi + equity + inclusion + el {CTRL}
"""

OLS_REF = {
    "eq_simple":        {"est": 0.048, "lo": 0.026, "hi": 0.070,  "note": "(a) equity simple"},
    "incl_simple":      {"est": 0.078, "lo": 0.053, "hi": 0.104,  "note": "(a) inclusion simple"},
    "eq_simult":        {"est": 0.034, "lo": 0.020, "hi": 0.051,  "note": "(b) equity simult."},
    "incl_simult":      {"est": 0.038, "lo": 0.023, "hi": 0.056,  "note": "(b) inclusion simult."},
    "diff_b":           {"est": 0.004, "lo":-0.009, "hi": 0.018,  "note": "(b) eq-incl diff"},
    "incl_oi_ocb":      {"est": 0.055, "lo": None,  "hi": None,   "note": "(c) incl->OI->OCB"},
    "incl_oi_upb":      {"est": 0.038, "lo": None,  "hi": None,   "note": "(c) incl->OI->UPB"},
    "eq_oi_ocb":        {"est": 0.049, "lo": None,  "hi": None,   "note": "(c) eq->OI->OCB"},
    "eq_oi_upb":        {"est": 0.034, "lo": None,  "hi": None,   "note": "(c) eq->OI->UPB"},
    "incl_ocb_vs_upb":  {"est": 0.017, "lo": None,  "hi": None,   "note": "(c) incl OCB-UPB diff (CI incl 0)"},
    "eq_ocb_vs_upb":    {"est": 0.015, "lo": None,  "hi": None,   "note": "(c) eq OCB-UPB diff (CI incl 0)"},
}


def get_std(est, dv, pred):
    row = est[(est["lval"] == dv) & (est["op"] == "~") & (est["rval"] == pred)]
    return float(row["Est. Std"].iloc[0]) if len(row) else np.nan


def fit_simple(data, desc, dei_key):
    m = Model(desc)
    m.fit(data)
    est = m.inspect(std_est=True)
    a      = get_std(est, "oi",  dei_key)
    b_upb  = get_std(est, "upb", "oi")
    direct = get_std(est, "upb", dei_key)
    return {"a": a, "b_upb": b_upb, "indirect": a * b_upb, "direct": direct}


def fit_stage_c(data):
    m = Model(DESC_C)
    m.fit(data)
    est = m.inspect(std_est=True)
    return {
        "eq_oi":    get_std(est, "oi",  "equity"),
        "incl_oi":  get_std(est, "oi",  "inclusion"),
        "oi_upb":   get_std(est, "upb", "oi"),
        "oi_ocb":   get_std(est, "ocb", "oi"),
        "eq_d_upb":   get_std(est, "upb", "equity"),
        "eq_d_ocb":   get_std(est, "ocb", "equity"),
        "incl_d_upb": get_std(est, "upb", "inclusion"),
        "incl_d_ocb": get_std(est, "ocb", "inclusion"),
    }


def compute_indirects(b):
    ie = {
        "eq_oi_upb":   b["eq_oi"]   * b["oi_upb"],
        "incl_oi_upb": b["incl_oi"] * b["oi_upb"],
        "eq_oi_ocb":   b["eq_oi"]   * b["oi_ocb"],
        "incl_oi_ocb": b["incl_oi"] * b["oi_ocb"],
    }
    ie["diff_b_upb"]      = ie["eq_oi_upb"]   - ie["incl_oi_upb"]
    ie["incl_ocb_vs_upb"] = ie["incl_oi_ocb"] - ie["incl_oi_upb"]
    ie["eq_ocb_vs_upb"]   = ie["eq_oi_ocb"]   - ie["eq_oi_upb"]
    return ie


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
    a_acc = num / den if den > 1e-12 else 0.0

    def adj(z_a):
        inner = 1 - a_acc * (z0 + z_a)
        if abs(inner) < 1e-10:
            return 1.0 if z_a > 0 else 0.0
        return float(np.clip(spnorm.cdf(z0 + (z0 + z_a) / inner), 0.001, 0.999))

    return (np.percentile(b, 100 * adj(spnorm.ppf(alpha / 2))),
            np.percentile(b, 100 * adj(spnorm.ppf(1 - alpha / 2))))


def pct_ci(arr):
    a = arr[np.isfinite(arr)]
    return np.percentile(a, 2.5), np.percentile(a, 97.5)


def zero_in(lo, hi):
    if lo is None or np.isnan(lo):
        return "?"
    return "yes" if lo <= 0 <= hi else "no"


# =============================================================
# PART A: Simple mediation
# =============================================================
print("\n" + "=" * 60)
print("PART A: Simple mediation (2000 bootstrap, Percentile CI)")
print("=" * 60)

print("\nFitting equity-only and inclusion-only on full data...")
t0 = time.time()
obs_eq   = fit_simple(df, DESC_EQ,   "equity")
t_eq     = time.time() - t0
t0 = time.time()
obs_incl = fit_simple(df, DESC_INCL, "inclusion")
t_incl   = time.time() - t0

print(f"  equity-only fit:    {t_eq:.2f}s")
print(f"  inclusion-only fit: {t_incl:.2f}s")
print("  equity:    ", {k: round(v, 4) for k, v in obs_eq.items()})
print("  inclusion: ", {k: round(v, 4) for k, v in obs_incl.items()})

N_BOOT_A = 2000
t_per_iter = t_eq + t_incl
est_min_a  = round(N_BOOT_A * t_per_iter / 60, 1)
print(f"\nPart A bootstrap: {N_BOOT_A} iter x {t_per_iter:.2f}s = ~{est_min_a} min")

rng_a = np.random.default_rng(42)
SKEYS = ["a", "b_upb", "indirect", "direct"]
boot_eq   = {k: np.full(N_BOOT_A, np.nan) for k in SKEYS}
boot_incl = {k: np.full(N_BOOT_A, np.nan) for k in SKEYS}

t_a0 = time.time()
n_fail_a = 0
print(f"\nRunning Part A bootstrap...", flush=True)
for i in range(N_BOOT_A):
    idx  = rng_a.integers(0, N, size=N)
    samp = df.iloc[idx].reset_index(drop=True)
    try:
        res = fit_simple(samp, DESC_EQ, "equity")
        for k in SKEYS: boot_eq[k][i] = res[k]
    except Exception:
        n_fail_a += 1
    try:
        res = fit_simple(samp, DESC_INCL, "inclusion")
        for k in SKEYS: boot_incl[k][i] = res[k]
    except Exception:
        n_fail_a += 1
    if (i + 1) % 400 == 0:
        print(f"  {i+1}/{N_BOOT_A} ({time.time()-t_a0:.0f}s, fails={n_fail_a})", flush=True)

t_a = time.time() - t_a0
print(f"Part A done: {t_a:.1f}s, failures: {n_fail_a}", flush=True)

print("\n[PART A RESULTS]")
print(f"{'DEI':<12} {'Effect':<10} {'Est':>8} {'95%CI':>22} {'OLS':>8} {'0_in':>5}")
rows_a = []
ols_a_map = {
    ("equity",    "indirect"): OLS_REF["eq_simple"],
    ("inclusion", "indirect"): OLS_REF["incl_simple"],
}
for dei, boot_d, obs_d in [("equity", boot_eq, obs_eq), ("inclusion", boot_incl, obs_incl)]:
    for eff in ["indirect", "direct", "a", "b_upb"]:
        est = obs_d[eff]
        plo, phi = pct_ci(boot_d[eff])
        zi = zero_in(plo, phi)
        ols = ols_a_map.get((dei, eff))
        ols_str = f"{ols['est']:.3f}" if ols else "n/a"
        print(f"  {dei:<10} {eff:<10} {est:>8.4f} [{plo:.4f},{phi:.4f}] {ols_str:>8} {zi:>5}")
        rows_a.append({
            "dei": dei, "effect": eff, "sem_est": round(est, 4),
            "pct_lo": round(plo, 4), "pct_hi": round(phi, 4),
            "zero_in": zi,
            "ols_est": ols["est"] if ols else None,
        })


# =============================================================
# PART C (and B): Stage C full model
# =============================================================
print("\n" + "=" * 60)
print("PART C: Stage C mediation (5000 bootstrap + 2020 jackknife, BCa)")
print("=" * 60)

print("\nFitting Stage C on full data...")
t0 = time.time()
betas_obs = fit_stage_c(df)
t_c = time.time() - t0
ie_obs = compute_indirects(betas_obs)

print(f"  Stage C fit: {t_c:.2f}s")

# Sign-flip check
EXPECTED_POS = ["eq_oi", "incl_oi", "oi_upb", "oi_ocb"]
flipped = [k for k in EXPECTED_POS if betas_obs.get(k, 1) < 0]
if flipped:
    print("\n!!! SIGN FLIP DETECTED n/a STOPPING !!!")
    print(f"  Flipped paths: {flipped}")
    print("  OLS expected: all positive. Investigate before proceeding.")
    import sys; sys.exit(1)
else:
    print("  Sign check PASSED: eq_oi, incl_oi, oi_upb, oi_ocb all positive")

print("  Stage C betas:", {k: round(v, 4) for k, v in betas_obs.items()})
print("  Indirect effects:", {k: round(v, 4) for k, v in ie_obs.items()})

N_BOOT_C = 5000
est_min_c = round(N_BOOT_C * t_c / 60, 1)
est_min_j = round(N * t_c / 60, 1)
print(f"\nPart C bootstrap: {N_BOOT_C} x {t_c:.2f}s = ~{est_min_c} min")
print(f"Jackknife:         {N} x {t_c:.2f}s = ~{est_min_j} min")
print(f"Part C total expected: ~{est_min_c + est_min_j:.1f} min")

ALL_KEYS = list(betas_obs.keys()) + list(ie_obs.keys())
boot_c = {k: np.full(N_BOOT_C, np.nan) for k in ALL_KEYS}
jack_c = {k: np.full(N, np.nan) for k in ALL_KEYS}

rng_c = np.random.default_rng(42)
t_c0 = time.time()
n_fail_c = 0
print(f"\nBootstrap ({N_BOOT_C} iterations)...", flush=True)
for i in range(N_BOOT_C):
    idx = rng_c.integers(0, N, size=N)
    try:
        b  = fit_stage_c(df.iloc[idx].reset_index(drop=True))
        ie = compute_indirects(b)
        for k in betas_obs: boot_c[k][i] = b[k]
        for k in ie_obs:    boot_c[k][i] = ie[k]
    except Exception:
        n_fail_c += 1
    if (i + 1) % 500 == 0:
        print(f"  {i+1}/{N_BOOT_C} ({time.time()-t_c0:.0f}s, fails={n_fail_c})", flush=True)

t_boot_c = time.time() - t_c0
print(f"Bootstrap done: {t_boot_c:.1f}s, failures: {n_fail_c}", flush=True)

t_j0 = time.time()
n_fail_j = 0
print(f"\nJackknife ({N} iterations)...", flush=True)
for i in range(N):
    idx = np.concatenate([np.arange(i), np.arange(i + 1, N)])
    try:
        b  = fit_stage_c(df.iloc[idx].reset_index(drop=True))
        ie = compute_indirects(b)
        for k in betas_obs: jack_c[k][i] = b[k]
        for k in ie_obs:    jack_c[k][i] = ie[k]
    except Exception:
        n_fail_j += 1
    if (i + 1) % 400 == 0:
        print(f"  {i+1}/{N} ({time.time()-t_j0:.0f}s, fails={n_fail_j})", flush=True)

t_jack_c = time.time() - t_j0
print(f"Jackknife done: {t_jack_c:.1f}s, failures: {n_fail_j}", flush=True)

n_valid_c = np.isfinite(boot_c["eq_oi_upb"]).sum()
print(f"Valid bootstrap samples: {n_valid_c}/{N_BOOT_C}")

# ---- Part C results ----
print("\n[PART B: Simultaneous UPB mediation (from Stage C)]")
print("Note: Stage C includes EL in outcome equations; OLS 표7 did not.")
print(f"{'Effect':<18} {'Est':>8} {'BCa_lo':>8} {'BCa_hi':>8} {'0_BCa':>6} {'OLS_est':>8}")
rows_b = []
for key, ols_key, label, ols_ref_key in [
    ("eq_oi_upb",   "eq_oi_upb",   "eq->OI->UPB",      "eq_simult"),
    ("incl_oi_upb", "incl_oi_upb", "incl->OI->UPB",    "incl_simult"),
    ("diff_b_upb",  "diff_b_upb",  "eq - incl (UPB)",  "diff_b"),
]:
    est  = ie_obs[key]
    blo, bhi = bca_ci(boot_c[key], est, jack_c[key])
    zi_b = zero_in(blo, bhi)
    ols  = OLS_REF.get(ols_ref_key, {})
    ols_str = f"{ols.get('est',''):.3f}" if ols.get("est") is not None else "n/a"
    print(f"  {label:<16} {est:>8.4f} {blo:>8.4f} {bhi:>8.4f} {zi_b:>6} {ols_str:>8}")
    rows_b.append({
        "part": "B", "effect": label, "sem_est": round(est, 4),
        "bca_lo": round(blo, 4) if not np.isnan(blo) else None,
        "bca_hi": round(bhi, 4) if not np.isnan(bhi) else None,
        "zero_in_bca": zi_b, "ols_est": ols.get("est"),
    })

print("\n[PART C: 4 indirect effects + contrasts (Stage C, BCa)]")
print(f"{'Effect':<22} {'Est':>8} {'Pct_lo':>8} {'Pct_hi':>8} {'BCa_lo':>8} {'BCa_hi':>8} {'0_BCa':>6} {'OLS':>7}")
rows_c = []
ie_display = [
    ("incl_oi_ocb",    "incl->OI->OCB",    "incl_oi_ocb"),
    ("incl_oi_upb",    "incl->OI->UPB",    "incl_oi_upb"),
    ("eq_oi_ocb",      "eq->OI->OCB",      "eq_oi_ocb"),
    ("eq_oi_upb",      "eq->OI->UPB",      "eq_oi_upb"),
    ("incl_ocb_vs_upb","incl: OCB-UPB diff","incl_ocb_vs_upb"),
    ("eq_ocb_vs_upb",  "eq: OCB-UPB diff", "eq_ocb_vs_upb"),
]
for key, label, ols_key in ie_display:
    est  = ie_obs[key]
    plo, phi = pct_ci(boot_c[key])
    blo, bhi = bca_ci(boot_c[key], est, jack_c[key])
    zi_b = zero_in(blo, bhi)
    ols  = OLS_REF.get(ols_key, {})
    ols_str = f"{ols.get('est',''):.3f}" if ols.get("est") is not None else "n/a"
    print(f"  {label:<20} {est:>8.4f} {plo:>8.4f} {phi:>8.4f} {blo:>8.4f} {bhi:>8.4f} {zi_b:>6} {ols_str:>7}")
    rows_c.append({
        "part": "C", "effect": label, "sem_est": round(est, 4),
        "pct_lo": round(plo, 4), "pct_hi": round(phi, 4),
        "bca_lo": round(blo, 4) if not np.isnan(blo) else None,
        "bca_hi": round(bhi, 4) if not np.isnan(bhi) else None,
        "zero_in_bca": zi_b, "ols_est": ols.get("est"),
    })

# Also print key b-paths (sign check)
print("\n[Stage C a- and b-paths (sign check)]")
for k in EXPECTED_POS:
    est = betas_obs[k]
    plo, phi = pct_ci(boot_c[k])
    blo, bhi = bca_ci(boot_c[k], est, jack_c[k])
    zi_b = zero_in(blo, bhi)
    print(f"  {k:<12} est={est:.4f} BCa=[{blo:.4f},{bhi:.4f}] 0_in={zi_b}")


# ---- Save ----
out_dir = "../results/sem"
os.makedirs(out_dir, exist_ok=True)

pd.DataFrame(rows_a).to_csv(
    os.path.join(out_dir, "sem07_part_a_simple_mediation.csv"),
    index=False, encoding="utf-8-sig")

pd.DataFrame(rows_b + rows_c).to_csv(
    os.path.join(out_dir, "sem07_part_bc_stage_c_mediation.csv"),
    index=False, encoding="utf-8-sig")

# Markdown report
def fmt_ci(lo, hi):
    if lo is None or (isinstance(lo, float) and np.isnan(lo)):
        return "n/a"
    return f"[{lo:.3f}, {hi:.3f}]"

part_a_tbl = pd.DataFrame([
    {"DEI": r["dei"], "효과": r["effect"],
     "SEM β_std": round(r["sem_est"], 3),
     "95% Percentile CI": fmt_ci(r["pct_lo"], r["pct_hi"]),
     "0 포함": r["zero_in"],
     "OLS (ref)": r["ols_est"] if r["ols_est"] else "n/a"}
    for r in rows_a
])

part_b_tbl = pd.DataFrame([
    {"효과": r["effect"],
     "SEM β_std": round(r["sem_est"], 3),
     "95% BCa CI": fmt_ci(r["bca_lo"], r["bca_hi"]),
     "0 포함": r["zero_in_bca"],
     "OLS (ref)": r["ols_est"] if r["ols_est"] else "n/a"}
    for r in rows_b
])

part_c_tbl = pd.DataFrame([
    {"효과": r["effect"],
     "SEM β_std": round(r["sem_est"], 3),
     "95% Pct CI": fmt_ci(r["pct_lo"], r["pct_hi"]),
     "95% BCa CI": fmt_ci(r["bca_lo"], r["bca_hi"]),
     "0 포함 (BCa)": r["zero_in_bca"],
     "OLS (ref)": r["ols_est"] if r["ols_est"] else "n/a"}
    for r in rows_c
])

total_min = round((t_a + t_boot_c + t_jack_c) / 60, 1)

md = f"""# SEM 매개분석 (H5·H6)

## 분석 설정

- 통제변수: gender_male, age, public_org
- 측정모형: 6요인 CFA (전 분석 공통)
- 부호역전 자동중지: eq_oi/incl_oi/oi_upb/oi_ocb n/a 통과

## (a) 단독 투입 매개분석 (표7 대조)

부트스트랩 {N_BOOT_A}회, Percentile 95% CI, 시드=42.
참고: SEM β_std(표준화)이며 OLS는 비표준화 간접효과 (단위 상이).

{part_a_tbl.to_markdown(index=False)}

## (b) 동시 투입 매개분석 n/a UPB 경로 (표7 대조)

Stage C 모형 기반 ({N_BOOT_C}회, BCa 95% CI).
주의: Stage C에는 EL이 UPB 방정식에 추가 포함되어 있어 OLS 표7과 구조 차이 있음.

{part_b_tbl.to_markdown(index=False)}

## (c) 4개 간접효과 (OCB·UPB 동시, Stage C)

부트스트랩 {N_BOOT_C}회 + 잭나이프 {N}회 (BCa), 시드=42.
유효 반복: {n_valid_c}/{N_BOOT_C}회.

{part_c_tbl.to_markdown(index=False)}

## a·b 경로계수 (BCa CI)

| 경로 | β_std | BCa_lo | BCa_hi | 0 포함 |
|:-----|------:|-------:|-------:|:------:|
"""
for k in EXPECTED_POS:
    blo, bhi = bca_ci(boot_c[k], betas_obs[k], jack_c[k])
    md += f"| {k} | {betas_obs[k]:.3f} | {blo:.3f} | {bhi:.3f} | {zero_in(blo, bhi)} |\n"

md += f"""
## 실행 정보

- 총 소요: {total_min}분
- Part A: {t_a:.0f}초 ({N_BOOT_A}회)
- Part C 부트스트랩: {t_boot_c:.0f}초 ({N_BOOT_C}회)
- Part C 잭나이프: {t_jack_c:.0f}초 ({N}회)
"""

with open(os.path.join(out_dir, "sem07_mediation_result.md"), "w", encoding="utf-8") as f:
    f.write(md)

print(f"\nAll results saved to {out_dir}")
print(f"Total elapsed: {total_min} min")
