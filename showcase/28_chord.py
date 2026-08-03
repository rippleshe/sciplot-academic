"""
28_chord.py — 弦图

展示 plot_chord()：五大城市间人才流动（万人/年）。
场景：城市群人才迁移流量矩阵。
"""

import numpy as np
import sciplot as sp

# ── 数据生成 ──────────────────────────────────────────────────
cities = ["北京", "上海", "广州", "深圳", "成都"]
# 非对称流量矩阵：行=出发，列=到达（万人/年）
flow = np.array([
    [0,   18,  6,  10,  4],
    [12,  0,   5,   8,  3],
    [4,   3,   0,  14,  2],
    [8,   6,  12,  0,   3],
    [3,   2,   2,   4,  0],
], dtype=float)

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("presentation", "sunset", lang="zh")

fig, ax = sp.plot_chord(
    flow,
    labels=cities,
    show_values=True,
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/28_chord", formats=("png",), dpi=300)
