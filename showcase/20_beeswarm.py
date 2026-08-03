"""
20_beeswarm.py — 蜂群图

展示 plot_beeswarm()：原始数据点的紧凑蜂群分布。
场景：四个班级的考试成绩分布对比。
"""

import numpy as np
import sciplot as sp

np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
rng = np.random.default_rng(42)
scores = [
    rng.normal(72, 12, 90),
    rng.normal(78, 10, 85),
    rng.normal(75, 15, 95),
    rng.normal(83, 9, 80),
]
labels = ["1班", "2班", "3班", "4班"]

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("ieee", "pastel", lang="zh")

fig, ax = sp.plot_beeswarm(
    scores,
    labels=labels,
    ylabel="考试成绩 (分)",
    show_box=True,
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/20_beeswarm", formats=("png",), dpi=300)
