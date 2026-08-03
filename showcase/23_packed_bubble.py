"""
23_packed_bubble.py — 打包气泡图

展示 plot_packed_bubble()：科研经费分配构成。
场景：某重点实验室年度经费按方向分配（万元）。
"""

import numpy as np
import sciplot as sp

# ── 数据生成 ──────────────────────────────────────────────────
directions = ["设备购置", "人才引进", "基础研究", "应用开发", "学术交流", "运维保障"]
budgets = np.array([480, 260, 320, 180, 90, 70])

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("presentation", "ocean", lang="zh")

fig, ax = sp.plot_packed_bubble(
    directions,
    budgets,
    xlabel="",
    ylabel="",
    show_values=True,
    fmt=".0f",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/23_packed_bubble", formats=("png",), dpi=300)
