"""
29_ternary.py — 三角相图

展示 plot_ternary()：土壤质地分类（砂/粉/黏 三组分）。
场景：80 个采样点的土壤机械组成，颜色编码有机质含量。
"""

import numpy as np
import sciplot as sp

np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
rng = np.random.default_rng(42)
n = 80
sand = rng.uniform(5, 90, n)
silt = rng.uniform(5, 85, n)
clay = np.clip(100 - sand - silt, 3, 60)
# 重新归一化
total = sand + silt + clay
sand, silt, clay = sand / total * 100, silt / total * 100, clay / total * 100

# 有机质含量（与黏粒正相关）
organic = 1.0 + clay * 0.08 + rng.normal(0, 0.8, n)

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("thesis", "forest", lang="zh")

fig, ax = sp.plot_ternary(
    sand,
    silt,
    clay,
    labels=["砂粒 (%)", "粉粒 (%)", "黏粒 (%)"],
    color_by=organic,
    colorbar_label="有机质 (%)",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/29_ternary", formats=("png",), dpi=300)
