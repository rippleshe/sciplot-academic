"""
39_streamgraph.py — 流图

展示 plot_streamgraph()：某平台 2000-2024 年访问流量构成演变
（亿次/年）。wiggle 基线让图层呈河流形态，直观呈现
“Web 见顶、移动端崛起”的结构性迁移。
"""

import numpy as np
import sciplot as sp

# ── 数据 ──────────────────────────────────────────────────────
years = np.arange(2000, 2025)
web = 10 + 3.0 * (years - 2000) + 2 * np.sin(years) + 4 * np.cos(years * 0.4)
mobile = 2 + 8.0 * np.tanh((years - 2008) / 2.5)
pc = 40 - 0.8 * (years - 2000)
web = np.maximum(web, 0)
mobile = np.maximum(mobile, 0)
pc = np.maximum(pc, 0)

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("presentation", "ocean", lang="zh")

fig, ax = sp.plot_streamgraph(
    years,
    [web, mobile, pc],
    labels=["Web", "移动端", "PC"],
    baseline="wiggle",
    xlabel="年份",
    ylabel="流量（亿次/年）",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/39_streamgraph", formats=("png",), dpi=300)
