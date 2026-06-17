import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.stats import norm

df = pd.read_csv("../processed/analysis_data.csv")
N = len(df)
print("=" * 70)
print("DATA SIZE:", df.shape)
print("=" * 70)

# --------------------------------------------------------------------
# 0. Variable reconstruction
# --------------------------------------------------------------------

# OLD (as used in 05_regression_upb.py / 11_regression_ocb.py)
df["gender_male_OLD"] = (df["SQ1K1"] == "남자").astype(int)

# NEW (assuming KIPA standard coding 1=male, 2=female; raw_data.sav not
# available locally to verify value labels directly -- see caveat in report)
df["gender_male_NEW"] = (df["SQ1K1"] == 1).astype(int)

df["public_org"] = (df["유형"] == "공공").astype(int)

# OLD age proxy: SQ1K2_1 used raw (actually birth year)
df["age_OLD_raw"] = df["SQ1K2_1"]

# NEW age: survey fielded Oct-Nov 2024 per manuscript -> convert birth year
df["age_NEW"] = 2024 - df["SQ1K2_1"]

print("\n[0-1] gender_male OLD frequency / variance")
print(df["gender_male_OLD"].value_counts())
print("variance:", df["gender_male_OLD"].var())

print("\n[0-2] gender_male NEW frequency / variance")
print(df["gender_male_NEW"].value_counts())
print("variance:", df["gender_male_NEW"].var())
print("(SQ1K1 raw value_counts:)")
print(df["SQ1K1"].value_counts())

print("\n[0-3] age OLD (raw SQ1K2_1) range:", df["age_OLD_raw"].min(), "-", df["age_OLD_raw"].max())
print("[0-4] age NEW (2024 - birth year) range:", df["age_NEW"].min(), "-", df["age_NEW"].max())
print("age NEW describe:\n", df["age_NEW"].describe())

# --------------------------------------------------------------------
# 1. TABLE 4 (UPB hierarchical regression) -- OLD vs NEW
# --------------------------------------------------------------------

def run_ols(y, x_vars, data):
    X = sm.add_constant(data[x_vars])
    return sm.OLS(data[y], X).fit(cov_type="HC3")

print("\n" + "=" * 70)
print("[1] TABLE 4 RE-ESTIMATION: UPB ~ controls + DEI + OI + EL")
print("=" * 70)

old_sets = {
    "Model1": ["gender_male_OLD", "age_OLD_raw", "public_org"],
    "Model2": ["gender_male_OLD", "age_OLD_raw", "public_org", "equity_climate", "inclusion_climate"],
    "Model3": ["gender_male_OLD", "age_OLD_raw", "public_org", "equity_climate", "inclusion_climate", "org_identification"],
    "Model4": ["gender_male_OLD", "age_OLD_raw", "public_org", "equity_climate", "inclusion_climate", "org_identification", "ethical_leadership"],
}
new_sets = {
    "Model1": ["gender_male_NEW", "age_NEW", "public_org"],
    "Model2": ["gender_male_NEW", "age_NEW", "public_org", "equity_climate", "inclusion_climate"],
    "Model3": ["gender_male_NEW", "age_NEW", "public_org", "equity_climate", "inclusion_climate", "org_identification"],
    "Model4": ["gender_male_NEW", "age_NEW", "public_org", "equity_climate", "inclusion_climate", "org_identification", "ethical_leadership"],
}

upb_old = {}
upb_new = {}
for m in ["Model1", "Model2", "Model3", "Model4"]:
    upb_old[m] = run_ols("upb", old_sets[m], df)
    upb_new[m] = run_ols("upb", new_sets[m], df)

print("\n--- UPB Model 4 OLD (coef / p) ---")
print(upb_old["Model4"].params.round(4))
print(upb_old["Model4"].pvalues.round(4))
print("R2:", upb_old["Model4"].rsquared.round(4))

print("\n--- UPB Model 4 NEW (coef / p) ---")
print(upb_new["Model4"].params.round(4))
print(upb_new["Model4"].pvalues.round(4))
print("R2:", upb_new["Model4"].rsquared.round(4))

print("\n--- UPB Model 3 OLD (coef / p) ---")
print(upb_old["Model3"].params.round(4))
print(upb_old["Model3"].pvalues.round(4))
print("R2:", upb_old["Model3"].rsquared.round(4))

print("\n--- UPB Model 3 NEW (coef / p) ---")
print(upb_new["Model3"].params.round(4))
print(upb_new["Model3"].pvalues.round(4))
print("R2:", upb_new["Model3"].rsquared.round(4))

print("\n--- UPB Model 2 OLD (coef / p) ---")
print(upb_old["Model2"].params.round(4))
print(upb_old["Model2"].pvalues.round(4))

print("\n--- UPB Model 2 NEW (coef / p) ---")
print(upb_new["Model2"].params.round(4))
print(upb_new["Model2"].pvalues.round(4))

print("\n--- UPB Model 1 OLD (coef / p) ---")
print(upb_old["Model1"].params.round(4))
print(upb_old["Model1"].pvalues.round(4))

print("\n--- UPB Model 1 NEW (coef / p) ---")
print(upb_new["Model1"].params.round(4))
print(upb_new["Model1"].pvalues.round(4))

# VIF (Model 4, NEW)
from statsmodels.stats.outliers_influence import variance_inflation_factor
vif_X = sm.add_constant(df[new_sets["Model4"]])
vif_df = pd.DataFrame()
vif_df["Variable"] = vif_X.columns
vif_df["VIF"] = [variance_inflation_factor(vif_X.values, i) for i in range(vif_X.shape[1])]
print("\n--- VIF (NEW, Model 4) ---")
print(vif_df.round(3))

# --------------------------------------------------------------------
# 2. TABLE 5 / OCB regression -- OLD vs NEW (parallel Model 3, EL excluded per Table5)
# --------------------------------------------------------------------

print("\n" + "=" * 70)
print("[2] TABLE 5 (OCB side) RE-ESTIMATION")
print("=" * 70)

ocb_old = {}
ocb_new = {}
for m in ["Model1", "Model2", "Model3", "Model4"]:
    ocb_old[m] = run_ols("ocb", old_sets[m], df)
    ocb_new[m] = run_ols("ocb", new_sets[m], df)

print("\n--- OCB Model 3 OLD (coef / p) [matches Table5 column, EL excluded] ---")
print(ocb_old["Model3"].params.round(4))
print(ocb_old["Model3"].pvalues.round(4))
print("R2:", ocb_old["Model3"].rsquared.round(4))

print("\n--- OCB Model 3 NEW (coef / p) ---")
print(ocb_new["Model3"].params.round(4))
print(ocb_new["Model3"].pvalues.round(4))
print("R2:", ocb_new["Model3"].rsquared.round(4))

print("\n--- OCB Model 4 OLD (coef / p) ---")
print(ocb_old["Model4"].params.round(4))
print(ocb_old["Model4"].pvalues.round(4))

print("\n--- OCB Model 4 NEW (coef / p) ---")
print(ocb_new["Model4"].params.round(4))
print(ocb_new["Model4"].pvalues.round(4))

# --------------------------------------------------------------------
# 3. H6 MODERATION RE-ESTIMATION (with vs without controls)
# --------------------------------------------------------------------

print("\n" + "=" * 70)
print("[3] H6 MODERATION RE-ESTIMATION: UPB ~ OI*EL (+- controls)")
print("=" * 70)

df["oi_c"] = df["org_identification"] - df["org_identification"].mean()
df["el_c"] = df["ethical_leadership"] - df["ethical_leadership"].mean()
df["oi_x_el"] = df["oi_c"] * df["el_c"]

mod_old = run_ols("upb", ["oi_c", "el_c", "oi_x_el"], df)
mod_new = run_ols("upb", ["oi_c", "el_c", "oi_x_el", "gender_male_NEW", "age_NEW", "public_org"], df)

print("\n--- H6 OLD (no controls) ---")
print(mod_old.params.round(4))
print(mod_old.pvalues.round(4))
print("R2:", mod_old.rsquared.round(4))

print("\n--- H6 NEW (with gender/age/org_type controls) ---")
print(mod_new.params.round(4))
print(mod_new.pvalues.round(4))
print("R2:", mod_new.rsquared.round(4))

# Simple slopes at -1SD / +1SD EL, OLD and NEW
el_sd = df["el_c"].std()


def simple_slope(model, b1_name, b3_name, el_value, cov_vars):
    b1 = model.params[b1_name]
    b3 = model.params[b3_name]
    slope = b1 + b3 * el_value
    # variance of slope = var(b1) + el_value^2 * var(b3) + 2*el_value*cov(b1,b3)
    cov = model.cov_params()
    var_slope = (
        cov.loc[b1_name, b1_name]
        + (el_value ** 2) * cov.loc[b3_name, b3_name]
        + 2 * el_value * cov.loc[b1_name, b3_name]
    )
    se_slope = np.sqrt(var_slope)
    z = slope / se_slope
    p = 2 * (1 - norm.cdf(abs(z)))
    return slope, se_slope, z, p


print("\n--- Simple slopes OLD ---")
for label, val in [("Low EL (-1SD)", -el_sd), ("Mean EL (0)", 0.0), ("High EL (+1SD)", el_sd)]:
    s, se, z, p = simple_slope(mod_old, "oi_c", "oi_x_el", val, None)
    print(f"{label}: slope={s:.4f}, SE={se:.4f}, z={z:.3f}, p={p:.4f}")

print("\n--- Simple slopes NEW (with controls) ---")
for label, val in [("Low EL (-1SD)", -el_sd), ("Mean EL (0)", 0.0), ("High EL (+1SD)", el_sd)]:
    s, se, z, p = simple_slope(mod_new, "oi_c", "oi_x_el", val, None)
    print(f"{label}: slope={s:.4f}, SE={se:.4f}, z={z:.3f}, p={p:.4f}")

# Johnson-Neyman point (where slope of OI on UPB becomes p=.05), for NEW model
b1 = mod_new.params["oi_c"]
b3 = mod_new.params["oi_x_el"]
cov = mod_new.cov_params()
var_b1 = cov.loc["oi_c", "oi_c"]
var_b3 = cov.loc["oi_x_el", "oi_x_el"]
cov_b1b3 = cov.loc["oi_c", "oi_x_el"]
crit = 1.96  # large-N HC3 z approx

# slope(EL) = b1 + b3*EL ; SE(EL)^2 = var_b1 + EL^2*var_b3 + 2*EL*cov_b1b3
# Solve |slope(EL)| = crit * SE(EL)  =>  slope(EL)^2 - crit^2*SE(EL)^2 = 0
# (b1+b3*EL)^2 - crit^2*(var_b1 + EL^2*var_b3 + 2*EL*cov_b1b3) = 0
A = b3 ** 2 - (crit ** 2) * var_b3
B = 2 * b1 * b3 - (crit ** 2) * 2 * cov_b1b3
C = b1 ** 2 - (crit ** 2) * var_b1

disc = B ** 2 - 4 * A * C
print("\n--- Johnson-Neyman (NEW model, centered EL units) ---")
if disc >= 0 and A != 0:
    r1 = (-B + np.sqrt(disc)) / (2 * A)
    r2 = (-B - np.sqrt(disc)) / (2 * A)
    el_mean = df["ethical_leadership"].mean()
    print(f"JN points (centered EL): {r1:.4f}, {r2:.4f}")
    print(f"JN points (raw EL scale): {r1 + el_mean:.4f}, {r2 + el_mean:.4f}")
else:
    print("No real JN solution (discriminant < 0) -- slope significant across observed EL range, or A=0")

# --------------------------------------------------------------------
# 4. MODERATED MEDIATION RE-ESTIMATION (bootstrap, with controls)
# --------------------------------------------------------------------

print("\n" + "=" * 70)
print("[4] MODERATED MEDIATION RE-ESTIMATION (Inclusion -> OI -> UPB, mod by EL)")
print("=" * 70)

df["inclusion_c"] = df["inclusion_climate"] - df["inclusion_climate"].mean()


def fit_modmed(data, with_controls):
    d = data.copy()
    d["oi_c"] = d["org_identification"] - d["org_identification"].mean()
    d["el_c"] = d["ethical_leadership"] - d["ethical_leadership"].mean()
    d["oi_x_el"] = d["oi_c"] * d["el_c"]
    d["inclusion_c"] = d["inclusion_climate"] - d["inclusion_climate"].mean()

    a_vars = ["inclusion_c"]
    b_vars = ["oi_c", "el_c", "oi_x_el"]
    if with_controls:
        a_vars = a_vars + ["gender_male_NEW", "age_NEW", "public_org"]
        b_vars = b_vars + ["gender_male_NEW", "age_NEW", "public_org"]

    Xa = sm.add_constant(d[a_vars])
    model_a = sm.OLS(d["oi_c"], Xa).fit(cov_type="HC3")
    a_path = model_a.params["inclusion_c"]

    Xb = sm.add_constant(d[b_vars])
    model_b = sm.OLS(d["upb"], Xb).fit(cov_type="HC3")
    b1 = model_b.params["oi_c"]
    b3 = model_b.params["oi_x_el"]

    el_sd_local = d["el_c"].std()
    low = a_path * (b1 + b3 * (-el_sd_local))
    mean_ = a_path * b1
    high = a_path * (b1 + b3 * el_sd_local)
    index_mod_med = a_path * b3  # Index of moderated mediation
    return low, mean_, high, index_mod_med, a_path, b1, b3


low_old, mean_old, high_old, imm_old, a_o, b1_o, b3_o = fit_modmed(df, with_controls=False)
low_new, mean_new, high_new, imm_new, a_n, b1_n, b3_n = fit_modmed(df, with_controls=True)

print(f"\nOLD (no controls): a={a_o:.4f}, b1={b1_o:.4f}, b3={b3_o:.4f}")
print(f"Low EL = {low_old:.4f}, Mean EL = {mean_old:.4f}, High EL = {high_old:.4f}")
print(f"Index of Moderated Mediation (a*b3) = {imm_old:.4f}")

print(f"\nNEW (with controls): a={a_n:.4f}, b1={b1_n:.4f}, b3={b3_n:.4f}")
print(f"Low EL = {low_new:.4f}, Mean EL = {mean_new:.4f}, High EL = {high_new:.4f}")
print(f"Index of Moderated Mediation (a*b3) = {imm_new:.4f}")

# Bootstrap CIs (5000 reps, seed=42, matching original 08_moderated_mediation.py)
N_BOOT = 5000
rng = np.random.default_rng(42)

boot_low_old = np.empty(N_BOOT)
boot_high_old = np.empty(N_BOOT)
boot_imm_old = np.empty(N_BOOT)
boot_low_new = np.empty(N_BOOT)
boot_high_new = np.empty(N_BOOT)
boot_imm_new = np.empty(N_BOOT)

for i in range(N_BOOT):
    idx = rng.integers(0, N, size=N)
    sample = df.iloc[idx]
    try:
        lo, me, hi, imm, *_ = fit_modmed(sample, with_controls=False)
    except Exception:
        lo, hi, imm = np.nan, np.nan, np.nan
    boot_low_old[i] = lo
    boot_high_old[i] = hi
    boot_imm_old[i] = imm

    try:
        lo2, me2, hi2, imm2, *_ = fit_modmed(sample, with_controls=True)
    except Exception:
        lo2, hi2, imm2 = np.nan, np.nan, np.nan
    boot_low_new[i] = lo2
    boot_high_new[i] = hi2
    boot_imm_new[i] = imm2


def pct_ci(arr):
    arr = arr[np.isfinite(arr)]
    return np.percentile(arr, 2.5), np.percentile(arr, 97.5)


print("\n--- Bootstrap 95% percentile CI (5000 reps) ---")
print("OLD Low EL  CI:", pct_ci(boot_low_old))
print("OLD High EL CI:", pct_ci(boot_high_old))
print("OLD Index of Moderated Mediation CI:", pct_ci(boot_imm_old))
print("NEW Low EL  CI:", pct_ci(boot_low_new))
print("NEW High EL CI:", pct_ci(boot_high_new))
print("NEW Index of Moderated Mediation CI:", pct_ci(boot_imm_new))

print("\nDONE")
