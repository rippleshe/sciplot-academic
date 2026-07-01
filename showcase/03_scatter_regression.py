"""
03_scatter_regression.py — 散点回归图

展示 SciPlot 的 plot_scatter() 功能：土壤有机碳含量与微生物呼吸速率的关系，
附带线性回归拟合线和 95% 置信区间。
"""

import numpy as np
import sciplot as sp

# 可复现随机种子
np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
# 模拟 60 个土壤样本：有机碳含量 (g/kg) vs 微生物呼吸速率 (mg CO₂/kg/h)
n_samples = 60
soc = np.random.uniform(5, 45, n_samples)  # 土壤有机碳 5 ~ 45 g/kg

# 线性关系 + 异方差噪声（高碳时变异更大）
noise_scale = 0.3 + 0.02 * soc
respiration = 1.2 * soc + 8.0 + np.random.normal(0, 1, n_samples) * noise_scale

# ── 线性回归 ──────────────────────────────────────────────────
slope, intercept = np.polyfit(soc, respiration, 1)
x_fit = np.linspace(soc.min(), soc.max(), 200)
y_fit = slope * x_fit + intercept

# 95% 置信区间（Bootstrap 近似）
n_boot = 1000
y_boot = np.zeros((n_boot, len(x_fit)))
for i in range(n_boot):
    idx = np.random.choice(n_samples, n_samples, replace=True)
    s, ic = np.polyfit(soc[idx], respiration[idx], 1)
    y_boot[i] = s * x_fit + ic
ci_lower = np.percentile(y_boot, 2.5, axis=0)
ci_upper = np.percentile(y_boot, 97.5, axis=0)

# R² 计算
y_pred = slope * soc + intercept
ss_res = np.sum((respiration - y_pred) ** 2)
ss_tot = np.sum((respiration - np.mean(respiration)) ** 2)
r_squared = 1 - ss_res / ss_tot

# ── 绘图 ──────────────────────────────────────────────────────
fig, ax = sp.plot_scatter(
    soc, respiration,
    xlabel="土壤有机碳含量 (g/kg)",
    ylabel="微生物呼吸速率 (mg CO2/kg/h)",
    title="土壤有机碳与微生物呼吸速率的关系",
    label="实测样本",
    s=25,
    alpha=0.7,
)

# 手动添加回归线和置信区间
ax.plot(x_fit, y_fit, color="#D62728", linewidth=1.5, label=f"线性拟合 (R²={r_squared:.3f})")
ax.fill_between(x_fit, ci_lower, ci_upper, color="#D62728", alpha=0.15, label="95% 置信区间")
ax.legend()

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/03_scatter_regression", formats=("png",), dpi=300)
