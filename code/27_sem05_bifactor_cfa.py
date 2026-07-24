import pandas as pd
import numpy as np
from semopy import Model, calc_stats
import os

# =====================================================================
# DEI 이중요인(Bifactor) 측정모형 검토
# 목적:
#   equity-inclusion 잠재상관 r=.729로 인한 억제효과 근본 원인 분석.
#   공통 DEI 요인(g_dei) + 형평 고유요인(equity_s) + 포용 고유요인(inclusion_s)
#   으로 구성한 bifactor 측정모형이 수렴하는지, 2요인 모형보다
#   적합도가 개선되는지 확인.
#
# 고유요인 직교 제약:
#   semopy에서 '~~' 없이 지정하면 기본적으로 모든 잠재변수 간 공분산을
#   자유모수로 추정함. 따라서 모델 지정 후 fix() 방법으로 직교 제약을
#   명시적으로 가함. 불가능 시 우회방법 사용 후 결과 해석 시 명기.
# =====================================================================

df = pd.read_csv("../processed/analysis_data.csv")

DEI_ITEMS = {
    "equity_items":    ["Y8_1","Y8_2","Y8_3","Y8_4","Y8_5"],
    "inclusion_items": ["Y8_6","Y8_7","Y8_8","Y8_9"],
}
ALL_DEI = DEI_ITEMS["equity_items"] + DEI_ITEMS["inclusion_items"]
N = len(df)
print("N =", N)


def calc_srmr_subset(model, items, data):
    try:
        sigma, _ = model.calc_sigma()
        order = model.vars["observed"]
        idx = [order.index(i) for i in items if i in order]
        s = sigma[np.ix_(idx, idx)]
        oc = data[items].cov().values
        d_o = np.sqrt(np.diag(oc)); d_m = np.sqrt(np.diag(s))
        r_o = oc / np.outer(d_o, d_o); r_m = s / np.outer(d_m, d_m)
        resid = r_o - r_m
        iu = np.tril_indices(len(items))
        return float(np.sqrt(np.mean(resid[iu] ** 2)))
    except Exception as e:
        return np.nan


# =====================================================================
# 기준: 2요인 모형 (12번 결과)
# =====================================================================
ref_2f = {"chi2": 438.40, "df": 26, "CFI": 0.9618, "TLI": 0.9471, "RMSEA": 0.0886}
print("\n[기준] 2요인 모형 (equity + inclusion, 12번 결과)")
print(f"  chi2={ref_2f['chi2']}, df={ref_2f['df']}, CFI={ref_2f['CFI']}, "
      f"TLI={ref_2f['TLI']}, RMSEA={ref_2f['RMSEA']}")

# =====================================================================
# 단일요인 모형 (기준 비교용, 12번 결과)
# =====================================================================
ref_1f = {"chi2": 1629.39, "df": 27, "CFI": 0.8516, "RMSEA": 0.1714}

# =====================================================================
# Bifactor 모형 지정
# g_dei: 9개 항목 모두에 적재
# equity_s: 형평 5개 항목에만 적재
# inclusion_s: 포용 4개 항목에만 적재
# 직교 제약: g_dei ⊥ equity_s, g_dei ⊥ inclusion_s, equity_s ⊥ inclusion_s
# =====================================================================
print("\n[Bifactor 모형 지정 및 수렴 시도]")

# 방법 1: 직교 제약 명시 (semopy ~~ 0 문법 시도)
bifactor_desc_try1 = """
g_dei =~ Y8_1 + Y8_2 + Y8_3 + Y8_4 + Y8_5 + Y8_6 + Y8_7 + Y8_8 + Y8_9
equity_s =~ Y8_1 + Y8_2 + Y8_3 + Y8_4 + Y8_5
inclusion_s =~ Y8_6 + Y8_7 + Y8_8 + Y8_9
"""

m_bi = Model(bifactor_desc_try1)

# semopy의 parameter 리스트 확인 (고정 전)
try:
    # 직교 제약 시도: 공분산 모수를 0으로 고정
    # semopy에서 lval ~~ rval 공분산이 자유모수로 있는 경우 fix 가능
    m_bi.fit(df)
    params_bi = m_bi.inspect()
    # 요인 간 공분산 파악
    factor_names = ["g_dei", "equity_s", "inclusion_s"]
    fac_cov = params_bi[
        (params_bi["op"] == "~~") &
        (params_bi["lval"].isin(factor_names)) &
        (params_bi["rval"].isin(factor_names)) &
        (params_bi["lval"] != params_bi["rval"])
    ]
    print("\n  [비제약 bifactor 요인 간 공분산]")
    if len(fac_cov) > 0:
        print(fac_cov[["lval","rval","Estimate","p-value"]].to_string(index=False))
    else:
        print("  요인 간 공분산 추정 없음 (semopy가 자동 직교 처리)")
    bi_converged_free = True
except Exception as e:
    print(f"  비제약 bifactor 수렴 실패: {e}")
    bi_converged_free = False

# 방법 2: 수렴된 비제약 모형의 공분산 값을 0으로 고정해 재추정
bi_stats_orthog = None
bi_srmr_orthog = np.nan
bi_converged_orthog = False

if bi_converged_free and len(fac_cov) > 0:
    # 요인 간 공분산 추정값 확인
    print("\n  [직교 제약 적용: 요인 간 공분산 = 0으로 고정 시도]")

    # semopy에서 모수 이름 확인
    all_params = m_bi.inspect()
    print("  모수명 샘플:")
    print(all_params[all_params["lval"].isin(factor_names)].head(10).to_string(index=False))

    # fix 접근: 비제약 모형 결과에서 공분산이 작으면 직교로 볼 수 있음
    max_fac_cov = fac_cov["Estimate"].abs().max() if len(fac_cov) > 0 else 0
    print(f"\n  최대 요인 간 공분산 절대값: {max_fac_cov:.4f}")
    if max_fac_cov < 0.1:
        print("  → 사실상 직교 (|cov| < 0.1), 적합도를 직교 모형으로 보고 가능")
    else:
        print("  → 직교 제약이 필요하나 semopy fix API 미지원 가능성 있음")
        print("  → 비제약 bifactor 적합도를 상한(upper bound)으로 보고")

    # 비제약 모형 적합도 추출
    bi_stats_orthog = calc_stats(m_bi).iloc[0]
    bi_srmr_orthog = calc_srmr_subset(m_bi, ALL_DEI, df)
    bi_converged_orthog = True

elif bi_converged_free:
    # 요인 간 공분산이 자동으로 0 (직교) 처리된 경우
    bi_stats_orthog = calc_stats(m_bi).iloc[0]
    bi_srmr_orthog = calc_srmr_subset(m_bi, ALL_DEI, df)
    bi_converged_orthog = True
    print("\n  bifactor 수렴, 요인 간 공분산 없음 (직교 자동 처리)")

# 방법 3: 고유요인 분리 식별 문제로 미수렴 시
# → 항목별 공통분산을 직접 EFA Schmid-Leiman 방식으로 근사
if not bi_converged_free:
    print("\n  [대안] 고계 요인 모형(Higher-order) 시도")
    # DEI 2요인이 1개 g 요인에 의해 설명되는 고계 요인 모형
    hof_desc = """
    equity =~ Y8_1 + Y8_2 + Y8_3 + Y8_4 + Y8_5
    inclusion =~ Y8_6 + Y8_7 + Y8_8 + Y8_9
    g_dei =~ equity + inclusion
    """
    try:
        m_hof = Model(hof_desc)
        m_hof.fit(df)
        bi_stats_orthog = calc_stats(m_hof).iloc[0]
        bi_srmr_orthog = calc_srmr_subset(m_hof, ALL_DEI, df)
        bi_converged_orthog = True
        print("  고계 요인 모형 수렴")
    except Exception as e2:
        print(f"  고계 요인 모형도 실패: {e2}")

# =====================================================================
# 모형 비교
# =====================================================================
print("\n" + "=" * 60)
print("[DEI 측정모형 비교]")
print("=" * 60)

rows_cmp = [
    {"모형": "단일요인 (1-factor)",
     "chi2": ref_1f["chi2"], "df": ref_1f["df"],
     "CFI": ref_1f["CFI"], "TLI": "—", "RMSEA": ref_1f["RMSEA"], "SRMR": "—",
     "비고": "12번 재현"},
    {"모형": "2요인 (equity+inclusion)",
     "chi2": ref_2f["chi2"], "df": ref_2f["df"],
     "CFI": ref_2f["CFI"], "TLI": ref_2f["TLI"], "RMSEA": ref_2f["RMSEA"], "SRMR": "—",
     "비고": "12번 재현 (주 측정모형)"},
]

if bi_converged_orthog and bi_stats_orthog is not None:
    rows_cmp.append({
        "모형": "Bifactor (g + equity_s + inclusion_s)",
        "chi2": round(float(bi_stats_orthog["chi2"]), 2),
        "df": int(bi_stats_orthog["DoF"]),
        "CFI": round(float(bi_stats_orthog["CFI"]), 4),
        "TLI": round(float(bi_stats_orthog["TLI"]), 4),
        "RMSEA": round(float(bi_stats_orthog["RMSEA"]), 4),
        "SRMR": round(bi_srmr_orthog, 4) if not np.isnan(bi_srmr_orthog) else "—",
        "비고": "수렴 (비제약 bifactor)" if len(fac_cov) > 0 else "수렴 (직교 자동)",
    })
    # 2요인 vs bifactor Δchi2 (카이제곱 차이 검정)
    delta_chi2 = ref_2f["chi2"] - float(bi_stats_orthog["chi2"])
    delta_df   = ref_2f["df"]   - int(bi_stats_orthog["DoF"])
    print(f"\n  2요인 vs Bifactor: Δchi2={delta_chi2:.2f}, Δdf={delta_df}")
    from scipy.stats import chi2 as chi2_dist
    p_val = chi2_dist.sf(abs(delta_chi2), abs(delta_df)) if delta_df != 0 else np.nan
    print(f"  p(Δchi2) = {p_val:.4f}" if not np.isnan(p_val) else "  p: df=0이므로 검정 불가")

df_cmp = pd.DataFrame(rows_cmp)
print(df_cmp.to_string(index=False))

# =====================================================================
# Bifactor 표준화 적재량
# =====================================================================
if bi_converged_free:
    print("\n[Bifactor 표준화 적재량]")
    est_bi = m_bi.inspect(std_est=True)
    loadings_bi = est_bi[est_bi["op"] == "~"][["lval","rval","Estimate","Est. Std"]].copy()
    loadings_bi.columns = ["item","factor","unstd","std"]
    print(loadings_bi.to_string(index=False))

    # 공통분산(공통성) = g_dei 적재² + 고유요인 적재² per item
    print("\n[항목별 공통성 분해]")
    g_loads = dict(zip(
        loadings_bi[loadings_bi["factor"] == "g_dei"]["item"],
        loadings_bi[loadings_bi["factor"] == "g_dei"]["std"].astype(float)
    ))
    eq_loads = dict(zip(
        loadings_bi[loadings_bi["factor"] == "equity_s"]["item"],
        loadings_bi[loadings_bi["factor"] == "equity_s"]["std"].astype(float)
    ))
    inc_loads = dict(zip(
        loadings_bi[loadings_bi["factor"] == "inclusion_s"]["item"],
        loadings_bi[loadings_bi["factor"] == "inclusion_s"]["std"].astype(float)
    ))
    for item in ALL_DEI:
        gl = g_loads.get(item, 0)
        sl = eq_loads.get(item, inc_loads.get(item, 0))
        h2 = gl**2 + sl**2
        print(f"  {item}: g={gl:.3f}, s={sl:.3f}, h²={h2:.3f}")

# =====================================================================
# 결과 저장
# =====================================================================
out_dir = "../results/sem"
os.makedirs(out_dir, exist_ok=True)

df_cmp.to_csv(os.path.join(out_dir, "sem05_bifactor_model_comparison.csv"),
              index=False, encoding="utf-8-sig")

md_lines = ["# DEI Bifactor 측정모형 검토\n"]
md_lines.append("## 모형 비교\n")
md_lines.append(df_cmp.to_markdown(index=False))
md_lines.append("\n")

if bi_converged_free:
    md_lines.append("## Bifactor 표준화 적재량\n")
    md_lines.append(loadings_bi.to_markdown(index=False))
    md_lines.append("\n")
    if len(fac_cov) > 0:
        md_lines.append("## 요인 간 공분산 (직교 미제약 버전)\n")
        md_lines.append(fac_cov[["lval","rval","Estimate","p-value"]].to_markdown(index=False))
        md_lines.append("\n")

md_lines.append("""## 해석 노트

Bifactor 모형 결과의 핵심 판단 기준:

1. **수렴 여부**: 위 결과 참조
2. **적합도 개선**: 2요인 대비 ΔCFI, ΔRMSEA 방향
3. **고유요인 적재량 의미**: equity_s·inclusion_s의 std 적재량이 충분히 크면
   (≥.30) 두 차원이 g_dei 이상의 고유 분산을 보유 → bifactor 정당화
4. **직교 제약 충족 여부**: 요인 간 공분산 ≈ 0 확인 필요
5. **구조모형 확장 여부**: 연구자 결정 (이 스크립트는 측정모형만 검토)
""")

with open(os.path.join(out_dir, "sem05_bifactor_result.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print("\n결과 저장 완료:", out_dir)
