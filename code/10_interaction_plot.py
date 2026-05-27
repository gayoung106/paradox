import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.formula.api as smf
import os

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

df = pd.read_csv(
    "../processed/analysis_data.csv"
)

# --------------------------------------------------
# 평균중심화
# --------------------------------------------------

df["oi_c"] = (
    df["org_identification"]
    - df["org_identification"].mean()
)

df["el_c"] = (
    df["ethical_leadership"]
    - df["ethical_leadership"].mean()
)

# --------------------------------------------------
# interaction
# --------------------------------------------------

df["interaction"] = (
    df["oi_c"] * df["el_c"]
)

# --------------------------------------------------
# 모델
# --------------------------------------------------

model = smf.ols(
    """
    upb ~
    oi_c +
    el_c +
    interaction
    """,
    data=df
).fit()

# --------------------------------------------------
# 예측값 생성
# --------------------------------------------------

oi_range = np.linspace(
    df["oi_c"].min(),
    df["oi_c"].max(),
    100
)

el_low = -df["el_c"].std()
el_high = df["el_c"].std()

# low EL
pred_low = (
    model.params["Intercept"]
    + model.params["oi_c"] * oi_range
    + model.params["el_c"] * el_low
    + model.params["interaction"] * oi_range * el_low
)

# high EL
pred_high = (
    model.params["Intercept"]
    + model.params["oi_c"] * oi_range
    + model.params["el_c"] * el_high
    + model.params["interaction"] * oi_range * el_high
)

# --------------------------------------------------
# 결과 폴더 생성
# --------------------------------------------------

os.makedirs(
    "../results/visualization",
    exist_ok=True
)

# --------------------------------------------------
# Plot
# --------------------------------------------------

plt.figure(figsize=(8,6))

plt.plot(
    oi_range,
    pred_low,
    label="Low Ethical Leadership (-1SD)"
)

plt.plot(
    oi_range,
    pred_high,
    label="High Ethical Leadership (+1SD)"
)

plt.xlabel(
    "Organizational Identification"
)

plt.ylabel(
    "UPB"
)

plt.title(
    "Moderating Effect of Ethical Leadership"
)

plt.legend()

plt.tight_layout()

# --------------------------------------------------
# 저장
# --------------------------------------------------

save_path = (
    "../results/visualization/"
    "interaction_plot.png"
)

plt.savefig(
    save_path,
    dpi=300
)

print("\nInteraction Plot 저장 완료")
print("\n저장 경로:")
print(save_path)