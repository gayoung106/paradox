import pandas as pd
import numpy as np
from semopy import Model, calc_stats
import os

# =============================================================
# Script 30: Bifactor DEI Diagnostics
#   1. Orthogonal bifactor: standardized loadings, ECV, omegaH, omega_s
#   2. Decision: if ECV < .85 AND max specific loading >= .30 ->
#      exploratory structural model (bifactor DEI -> OI -> OCB/UPB)
#      (orthogonal specific factors eliminate suppressor problem)
# Expected time: ~1 min
# =============================================================

df = pd.read_csv("../processed/analysis_data.csv")
bad_col = [c for c in df.columns if not all(ord(ch) < 128 for ch in c)][0]
pub_val = df[bad_col].value_counts().idxmax()
df["gender_male"] = (df["SQ1K1"] == 1.0).astype(int)
df["age"]         = 2023 - df["SQ1K2_1"]
df["public_org"]  = (df[bad_col] == pub_val).astype(int)
N = len(df)
print(f"N = {N}")

EQ_ITEMS  = ["Y8_1","Y8_2","Y8_3","Y8_4","Y8_5"]
INC_ITEMS = ["Y8_6","Y8_7","Y8_8","Y8_9"]
DEI_ITEMS = EQ_ITEMS + INC_ITEMS
OI_ITEMS  = ["Y1_1","Y1_2","Y1_3","Y1_4","Y1_5","Y1_6"]
EL_ITEMS  = ["Y11_1","Y11_2","Y11_3","Y11_4","Y11_5"]
OCB_ITEMS = ["Y19_1","Y19_2","Y19_3","Y19_4"]
UPB_ITEMS = ["Y20_1","Y20_2","Y20_3","Y20_4","Y20_5"]
CTRL = "+ gender_male + age + public_org"

# =============================================================
# PART 1: Orthogonal bifactor CFA (same model as script 28)
# =============================================================
print("\n" + "=" * 60)
print("PART 1: Orthogonal Bifactor CFA")
print("=" * 60)

bf_desc = """
g_dei =~ Y8_1 + Y8_2 + Y8_3 + Y8_4 + Y8_5 + Y8_6 + Y8_7 + Y8_8 + Y8_9
equity_s =~ Y8_1 + Y8_2 + Y8_3 + Y8_4 + Y8_5
inclusion_s =~ Y8_6 + Y8_7 + Y8_8 + Y8_9
g_dei ~~ 0*equity_s
g_dei ~~ 0*inclusion_s
equity_s ~~ 0*inclusion_s
"""

m_bf = Model(bf_desc)
m_bf.fit(df[DEI_ITEMS])
st_bf = calc_stats(m_bf).iloc[0]

print(f"chi2({int(st_bf['DoF'])}) = {st_bf['chi2']:.2f}")
print(f"CFI={st_bf['CFI']:.4f}, TLI={st_bf['TLI']:.4f}, RMSEA={st_bf['RMSEA']:.4f}")

# Extract standardized loadings
# In semopy: model desc 'factor =~ item' is stored as op="~", lval=item, rval=factor
est_bf = m_bf.inspect(std_est=True)
loads_raw = est_bf[est_bf["op"] == "~"][["lval","rval","Estimate","Est. Std"]].copy()
loads_raw.columns = ["item","factor","unstd","std_load"]

# Keep only DEI item rows (filter out structural paths if any)
loads_raw = loads_raw[loads_raw["item"].isin(DEI_ITEMS)].copy()

g_l   = dict(zip(loads_raw[loads_raw.factor=="g_dei"]["item"],
                 loads_raw[loads_raw.factor=="g_dei"]["std_load"].astype(float)))
eq_l  = dict(zip(loads_raw[loads_raw.factor=="equity_s"]["item"],
                 loads_raw[loads_raw.factor=="equity_s"]["std_load"].astype(float)))
inc_l = dict(zip(loads_raw[loads_raw.factor=="inclusion_s"]["item"],
                 loads_raw[loads_raw.factor=="inclusion_s"]["std_load"].astype(float)))

# Item-level table
rows_items = []
for item in DEI_ITEMS:
    grp = "equity" if item in EQ_ITEMS else "inclusion"
    gl  = g_l.get(item, 0.0)
    sl  = eq_l.get(item, inc_l.get(item, 0.0))
    h2  = gl**2 + sl**2
    uniq = 1 - h2
    rows_items.append({"item": item, "group": grp,
                        "lambda_g": round(gl, 3),
                        "lambda_s": round(sl, 3),
                        "communality_h2": round(h2, 3),
                        "unique": round(uniq, 3)})
df_items = pd.DataFrame(rows_items)
print("\n[Standardized Loadings]")
print(df_items.to_string(index=False))

# =============================================================
# PART 2: Bifactor indices (ECV, omegaH, omega_s)
# =============================================================
print("\n" + "=" * 60)
print("PART 2: Bifactor Indices")
print("=" * 60)

# ECV (Explained Common Variance by general factor)
g_sq_all  = sum(v**2 for v in g_l.values())
s_sq_eq   = sum(v**2 for v in eq_l.values())
s_sq_inc  = sum(v**2 for v in inc_l.values())
total_common = g_sq_all + s_sq_eq + s_sq_inc
ECV = g_sq_all / total_common

# ECV per subscale
ECV_eq  = sum(g_l[i]**2 for i in EQ_ITEMS)  / (
           sum(g_l[i]**2 for i in EQ_ITEMS) + s_sq_eq)
ECV_inc = sum(g_l[i]**2 for i in INC_ITEMS) / (
           sum(g_l[i]**2 for i in INC_ITEMS) + s_sq_inc)

# omega_H: proportion of unit-weighted composite variance due to g_dei
# Unit-weighted composite variance for standardized items in orthogonal bifactor:
# Var(C) = n + (sum_g)^2 - sum_g^2 + (sum_eq)^2 - sum_eq^2 + (sum_inc)^2 - sum_inc^2
n_all = len(DEI_ITEMS)
sum_g   = sum(g_l.values())
sum_eq  = sum(eq_l.values())
sum_inc = sum(inc_l.values())
sum_g_sq_all = sum(v**2 for v in g_l.values())

var_C = (n_all
         + sum_g**2   - sum_g_sq_all
         + sum_eq**2  - s_sq_eq
         + sum_inc**2 - s_sq_inc)
omega_H = sum_g**2 / var_C

# omega_s per subscale (unique variance explained by specific factor in subscale composite)
n_eq  = len(EQ_ITEMS)
sum_g_eq = sum(g_l[i] for i in EQ_ITEMS)
sum_g_eq_sq = sum(g_l[i]**2 for i in EQ_ITEMS)
var_Ceq = (n_eq
           + sum_g_eq**2 - sum_g_eq_sq
           + sum_eq**2   - s_sq_eq)
omega_s_eq = sum_eq**2 / var_Ceq

n_inc = len(INC_ITEMS)
sum_g_inc = sum(g_l[i] for i in INC_ITEMS)
sum_g_inc_sq = sum(g_l[i]**2 for i in INC_ITEMS)
var_Cinc = (n_inc
            + sum_g_inc**2 - sum_g_inc_sq
            + sum_inc**2   - s_sq_inc)
omega_s_inc = sum_inc**2 / var_Cinc

# Max specific loading
max_s = max([abs(v) for v in eq_l.values()] +
            [abs(v) for v in inc_l.values()])

print(f"\nECV (total g variance)    = {ECV:.4f}")
print(f"ECV_equity               = {ECV_eq:.4f}")
print(f"ECV_inclusion            = {ECV_inc:.4f}")
print(f"omega_H (reliability g)  = {omega_H:.4f}")
print(f"omega_s_equity           = {omega_s_eq:.4f}")
print(f"omega_s_inclusion        = {omega_s_inc:.4f}")
print(f"Max specific loading     = {max_s:.4f}")

# Decision
print("\n[Decision Rule]")
print(f"  ECV < .85?  -> {ECV < 0.85} (ECV = {ECV:.3f})")
print(f"  Max |s| >= .30? -> {max_s >= 0.30} (max = {max_s:.3f})")
print(f"  omega_s > .50?  -> equity={omega_s_eq > 0.50}, inclusion={omega_s_inc > 0.50}")

run_struct = (ECV < 0.85 and max_s >= 0.30)
print(f"\n  -> Run exploratory bifactor structural model: {run_struct}")

# =============================================================
# PART 3 (conditional): Exploratory structural model
# =============================================================
struct_rows = []
if run_struct:
    print("\n" + "=" * 60)
    print("PART 3: Exploratory bifactor structural model")
    print("NOTE: Exploratory only - not for manuscript main analysis")
    print("=" * 60)

    # Full measurement + bifactor DEI factors -> OI -> OCB/UPB
    # Orthogonal equity_s/inclusion_s eliminate suppressor problem
    MEAS_NONDEI = "\n".join([
        f"oi  =~ {' + '.join(OI_ITEMS)}",
        f"el  =~ {' + '.join(EL_ITEMS)}",
        f"ocb =~ {' + '.join(OCB_ITEMS)}",
        f"upb =~ {' + '.join(UPB_ITEMS)}",
    ])
    MEAS_BF = "\n".join([
        "g_dei       =~ Y8_1 + Y8_2 + Y8_3 + Y8_4 + Y8_5 + Y8_6 + Y8_7 + Y8_8 + Y8_9",
        "equity_s    =~ Y8_1 + Y8_2 + Y8_3 + Y8_4 + Y8_5",
        "inclusion_s =~ Y8_6 + Y8_7 + Y8_8 + Y8_9",
        "g_dei ~~ 0*equity_s",
        "g_dei ~~ 0*inclusion_s",
        "equity_s ~~ 0*inclusion_s",
    ])

    struct_bf_desc = f"""
{MEAS_BF}
{MEAS_NONDEI}
oi  ~ g_dei + equity_s + inclusion_s {CTRL}
upb ~ oi + g_dei + equity_s + inclusion_s + el {CTRL}
ocb ~ oi + g_dei + equity_s + inclusion_s + el {CTRL}
"""
    print("\nFitting exploratory bifactor structural model...")
    try:
        m_struct = Model(struct_bf_desc)
        m_struct.fit(df)
        st_struct = calc_stats(m_struct).iloc[0]
        print(f"  chi2({int(st_struct['DoF'])}) = {st_struct['chi2']:.2f}, "
              f"CFI={st_struct['CFI']:.4f}, TLI={st_struct['TLI']:.4f}, "
              f"RMSEA={st_struct['RMSEA']:.4f}")

        est_struct = m_struct.inspect(std_est=True)
        focus_dv   = ["oi", "upb", "ocb"]
        focus_pred = ["g_dei", "equity_s", "inclusion_s", "oi", "el"]

        print("\n[Bifactor structural paths (std beta)]")
        for dv in focus_dv:
            for pred in focus_pred:
                row = est_struct[(est_struct["lval"] == dv) &
                                 (est_struct["op"] == "~") &
                                 (est_struct["rval"] == pred)]
                if len(row):
                    b = float(row["Est. Std"].iloc[0])
                    p = float(row["p-value"].iloc[0])
                    sig = "***" if p < .001 else ("**" if p < .01 else
                          ("*" if p < .05 else "ns"))
                    print(f"  {dv} ~ {pred}: beta={b:.3f} {sig} (p={p:.3f})")
                    struct_rows.append({
                        "dv": dv, "predictor": pred,
                        "beta_std": round(b, 3), "p": round(p, 3), "sig": sig
                    })

        # Key test: equity_s vs inclusion_s signatures
        print("\n[Signature check (H4 via orthogonal specific factors)]")
        def get_b(dv, pred):
            r = est_struct[(est_struct.lval==dv) &
                           (est_struct.op=="~") &
                           (est_struct.rval==pred)]
            return float(r["Est. Std"].iloc[0]) if len(r) else np.nan

        sig_eq  = get_b("upb","equity_s") - get_b("ocb","equity_s")
        sig_inc = get_b("ocb","inclusion_s") - get_b("upb","inclusion_s")
        print(f"  equity_s: upb={get_b('upb','equity_s'):.3f}, "
              f"ocb={get_b('ocb','equity_s'):.3f}, diff(upb-ocb)={sig_eq:.3f}")
        print(f"  inclusion_s: ocb={get_b('ocb','inclusion_s'):.3f}, "
              f"upb={get_b('upb','inclusion_s'):.3f}, diff(ocb-upb)={sig_inc:.3f}")

    except Exception as e:
        print(f"  Model failed: {e}")
else:
    print("\nSpecific factors too weak or ECV too high -- skip exploratory SEM.")

# =============================================================
# PART 4: Fit index comparison (2-factor vs bifactor improvement)
# =============================================================
print("\n" + "=" * 60)
print("PART 4: Fit improvement analysis")
print("=" * 60)

delta_chi2 = 438.40 - float(st_bf["chi2"])
delta_df   = 26 - int(st_bf["DoF"])
from scipy.stats import chi2 as chi2_dist
p_delta = float(chi2_dist.sf(delta_chi2, delta_df)) if delta_df > 0 else np.nan

print(f"\n2-factor: chi2=438.40, df=26, CFI=.9618, RMSEA=.0886")
print(f"Bifactor: chi2={float(st_bf['chi2']):.2f}, df={int(st_bf['DoF'])}, "
      f"CFI={float(st_bf['CFI']):.4f}, RMSEA={float(st_bf['RMSEA']):.4f}")
print(f"Delta chi2({delta_df}) = {delta_chi2:.2f}, p = {p_delta:.4f}")
print(f"Note: df reduction from 26->18 (8 df freed for specific factor loadings)")

# Parsimony check: RMSEA already accounts for df, so comparison is valid
# Also check TLI which penalizes for complexity
print(f"TLI comparison: 2-factor=.9471, bifactor={float(st_bf['TLI']):.4f}")
print("(TLI penalizes complexity; if bifactor TLI not much better, parsimony favors 2-factor)")

# =============================================================
# Save results
# =============================================================
out_dir = "../results/sem"
os.makedirs(out_dir, exist_ok=True)

df_items.to_csv(os.path.join(out_dir, "sem08_bifactor_loadings.csv"),
                index=False, encoding="utf-8-sig")

indices = {
    "ECV_total": round(ECV, 4),
    "ECV_equity": round(ECV_eq, 4),
    "ECV_inclusion": round(ECV_inc, 4),
    "omega_H": round(omega_H, 4),
    "omega_s_equity": round(omega_s_eq, 4),
    "omega_s_inclusion": round(omega_s_inc, 4),
    "max_specific_loading": round(max_s, 4),
    "run_exploratory_SEM": run_struct,
    "delta_chi2_vs_2factor": round(delta_chi2, 2),
    "delta_df": delta_df,
    "p_delta": round(p_delta, 6),
}
pd.DataFrame([indices]).to_csv(
    os.path.join(out_dir, "sem08_bifactor_indices.csv"),
    index=False, encoding="utf-8-sig")

if struct_rows:
    pd.DataFrame(struct_rows).to_csv(
        os.path.join(out_dir, "sem08_bifactor_struct_paths.csv"),
        index=False, encoding="utf-8-sig")

md = f"""# 이중요인 DEI 진단 + 탐색적 구조모형

## 1. 직교 이중요인 CFA 표준화 적재량

{df_items.to_markdown(index=False)}

## 2. 이중요인 지표

| 지표 | 값 | 해석 기준 |
|:-----|:---:|:---------|
| ECV (전체) | {ECV:.4f} | >.85: g 지배, <.70: 고유요인 실질적 |
| ECV_equity | {ECV_eq:.4f} | 형평 하위척도 내 g 설명 비율 |
| ECV_inclusion | {ECV_inc:.4f} | 포용 하위척도 내 g 설명 비율 |
| omega_H | {omega_H:.4f} | >.80: g 요인 신뢰도 양호 |
| omega_s (형평) | {omega_s_eq:.4f} | >.50: 고유분산 신뢰 가능 |
| omega_s (포용) | {omega_s_inc:.4f} | >.50: 고유분산 신뢰 가능 |
| 최대 고유인자 적재량 | {max_s:.4f} | >=.30: 실질적 고유분산 |

## 3. 적합도 개선 분석

| 모형 | chi2 | df | CFI | TLI | RMSEA |
|:-----|-----:|---:|----:|----:|------:|
| 2요인 | 438.40 | 26 | .9618 | .9471 | .0886 |
| 이중요인 직교 | {float(st_bf['chi2']):.2f} | {int(st_bf['DoF'])} | {float(st_bf['CFI']):.4f} | {float(st_bf['TLI']):.4f} | {float(st_bf['RMSEA']):.4f} |

Delta chi2({delta_df}) = {delta_chi2:.2f}, p = {p_delta:.4f}
자유도 감소: 26 -> {int(st_bf['DoF'])} (고유인자 8개 적재 추가)

## 4. 탐색적 구조모형 (exploratory, 탈억제 H4 검증)

탐색 실행 여부: {run_struct}
{'(ECV=' + str(round(ECV,3)) + ' < .85, max specific loading=' + str(round(max_s,3)) + ' >= .30)' if run_struct else '(ECV >= .85 또는 고유인자 적재 < .30 -> 생략)'}

{pd.DataFrame(struct_rows).to_markdown(index=False) if struct_rows else '탐색 미실행'}

## 5. 서술 방침

**이중요인은 2요인 유지 결정을 지지하거나 보완하는 맥락에서만 참조.**
ECV 수준에 따라:
- ECV > .85: "DEI가 사실상 단일 구성 (g_dei 중심)" -> 2요인보다 1요인에 가까움
- ECV .70~.85: "g_dei가 지배적이나 형평/포용 고유분산 일부 존재"
- ECV < .70: "형평·포용이 실질적 고유분산 보유, 2요인 구분 측정적 정당화"
"""

with open(os.path.join(out_dir, "sem08_bifactor_diag_result.md"), "w", encoding="utf-8") as f:
    f.write(md)

print(f"\nResults saved to {out_dir}")
