"""
17_hexbin.py — 六边形密度图

展示 plot_hexbin()：20000 个样本的二维联合分布（模拟高维数据
投影后的密度），解决大样本散点过度绘制问题。
"""

import numpy as np
import sciplot as sp

np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
# 模拟三个混合簇的 2D 投影（20000 点）
rnd = np.random.default_rng(42)
n = 20000

# 簇 1：主簇
x1 = rnd.normal(0, 1.2, int(n * 0.6))
y1 = rnd.normal(0, 1.0, int(n * 0.6))
# 簇 2：右上小簇
x2 = rnd.normal(4, 0.8, int(n * 0.25))
y2 = rnd.normal(3, 0.7, int(n * 0.25))
# 簇 3：左下拖尾
x3 = rnd.normal(-3, 1.5, int(n * 0.15))
y3 = rnd.normal(-2, 1.8, int(n * 0.15))

x = np.concatenate([x1, x2, x3])
y = np.concatenate([y1, y2, y3])

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("ieee", "ocean", lang="zh")

fig, ax = sp.plot_hexbin(
    x,
    y,
    gridsize=45,
    bins="log",
    cmap="viridis",
    xlabel="t-SNE 维度 1",
    ylabel="t-SNE 维度 2",
    colorbar_label="样本数 (log)",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/17_hexbin", formats=("png",), dpi=300)
