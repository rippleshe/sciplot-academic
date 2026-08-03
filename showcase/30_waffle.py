"""
30_waffle.py — 华夫图

展示 plot_waffle()：实验室年度经费构成（万元）。
场景：6 个支出方向的占比（100 格）。
"""

import numpy as np
import sciplot as sp

# ── 数据生成 ──────────────────────────────────────────────────
directions = ["设备购置", "试剂耗材", "测试分析", "差旅会议", "人员劳务", "其他"]
budgets = np.array([45, 22, 14, 8, 7, 4])

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("presentation", "pastel", lang="zh")

fig, ax = sp.plot_waffle(
    directions,
    budgets,
    rows=10,
    cols=10,
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/30_waffle", formats=("png",), dpi=300)
