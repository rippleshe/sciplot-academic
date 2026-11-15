"""
53_ml_forecast.py — ROC/PR 判别评估、概率校准与集合预测扇形图

展示 SciPlot v1.15.0 新增的 `plot_roc()`、`plot_calibration()` 与 `plot_fan()`。
"""

import numpy as np
import sciplot as sp

rng = np.random.default_rng(108)

# ── 模拟二分类诊断队列评估数据（真实伯努利采样保证概率校准可验证） ──
n = 550
true_prob = rng.beta(0.45, 0.45, size=n)
y_true = (rng.random(n) < true_prob).astype(int)
# 校准良好的模型贴近真实生成概率，基线模型因噪声偏高且温度过自信
prob_cal = np.clip(true_prob + rng.normal(0, 0.03, size=n), 0.01, 0.99)
prob_overconf = np.clip(0.5 + (prob_cal - 0.5) * 1.75 + 0.09, 0.01, 0.99)
prob_base = np.clip(true_prob + rng.normal(0, 0.24, size=n), 0.02, 0.98)

sp.setup_style("nature", "blue-sky", lang="en")
fig_roc, _ = sp.plot_roc(
    y_true,
    {"Proposed FusionNet": prob_cal, "ResNet Baseline": prob_base},
    mode="roc",
    show_threshold=True,
)
sp.save(fig_roc, "showcase/53_roc", formats=("png",), dpi=300)

sp.setup_style("nature", "coral-teal", lang="zh")
fig_cal, _ = sp.plot_calibration(
    y_true,
    {"校准后模型": prob_cal, "未校准基线": prob_overconf},
    n_bins=9,
    show_hist=True,
)
sp.save(fig_cal, "showcase/54_calibration", formats=("png",), dpi=300)

# ── 图 55：集合预测扇形图（历史观测 + 50/80/95% 置信区间） ─────────
sp.setup_style("nature", "coral-teal", lang="zh")
t_hist = np.arange(0, 18)
y_hist = 24.0 + 0.35 * t_hist + np.sin(t_hist * 0.5) * 0.9 + rng.normal(0, 0.35, size=18)
t_future = np.arange(17, 36)
increments = rng.normal(0.32, 0.65, size=(120, len(t_future)))
increments[:, 0] = 0.0
ensemble = y_hist[-1] + np.cumsum(increments, axis=1)

fig_fan, _ = sp.plot_fan(
    t_future,
    samples=ensemble,
    intervals=(50, 80, 95),
    history_x=t_hist,
    history_y=y_hist,
    xlabel="预测时间步 (天)",
    ylabel="监测指标估计值",
)
sp.save(fig_fan, "showcase/55_fan", formats=("png",), dpi=300)
