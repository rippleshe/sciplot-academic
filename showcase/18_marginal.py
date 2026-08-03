"""
18_marginal.py — 边际分布图

展示 plot_marginal()：主散点 + 边缘直方图，标注相关系数。
场景：城市 GDP 与人均消费支出的关系。
"""

import numpy as np
import sciplot as sp

np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
n = 400
rnd = np.random.default_rng(42)
gdp = rnd.lognormal(mean=5.0, sigma=0.6, size=n)          # GDP（亿元）
consumption = 0.35 * gdp + rnd.normal(0, 20, n)           # 人均消费（千元）
consumption = np.clip(consumption, 5, None)

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("nature", "ocean", lang="zh")

fig, ax = sp.plot_marginal(
    gdp,
    consumption,
    marginal="hist",
    bins=35,
    show_corr=True,
    xlabel="GDP (亿元)",
    ylabel="人均消费 (千元)",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/18_marginal", formats=("png",), dpi=300)
