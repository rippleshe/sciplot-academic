"""
19_raincloud.py — 雨云图

展示 plot_raincloud()：原始数据点 + 箱线 + 半小提琴三合一。
场景：三种施肥方案下的作物产量分布对比。
"""

import numpy as np
import sciplot as sp

np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
rng = np.random.default_rng(42)
yields = [
    rng.normal(5.2, 0.6, 150),   # 对照组
    rng.normal(6.1, 0.8, 150),   # 方案A
    rng.normal(6.8, 0.7, 150),   # 方案B
]
labels = ["对照组", "方案A", "方案B"]

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("nature", "forest", lang="zh")

fig, ax = sp.plot_raincloud(
    yields,
    labels=labels,
    xlabel="产量 (t/ha)",
    ylabel="处理组",
    show_median=True,
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/19_raincloud", formats=("png",), dpi=300)
