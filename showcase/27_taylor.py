"""
27_taylor.py — 泰勒图

展示 plot_taylor()：三种降水预报模型的综合评估。
场景：气象模型对比（观测站点数据 500 天）。
"""

import numpy as np
import sciplot as sp

np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
rng = np.random.default_rng(42)
n = 500
obs = rng.normal(5, 2.0, n)  # 日降水量 (mm)

pred_persist = 0.72 * obs + rng.normal(0, 1.6, n)   # 持续性预报
pred_wrf = 0.85 * obs + rng.normal(0, 1.1, n)       # WRF 模式
pred_ml = 0.93 * obs + rng.normal(0, 0.7, n)        # 机器学习订正

models = {
    "持续性预报": pred_persist,
    "WRF 模式": pred_wrf,
    "ML 订正": pred_ml,
}

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("ieee", "ocean", lang="zh")

fig, ax = sp.plot_taylor(
    obs,
    models,
    obs_name="观测",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/27_taylor", formats=("png",), dpi=300)
