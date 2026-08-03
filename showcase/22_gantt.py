"""
22_gantt.py — 甘特图

展示 plot_gantt()：项目任务时间线。
场景：科研项目 8 周执行计划。
"""

import numpy as np
import sciplot as sp

# ── 数据生成 ──────────────────────────────────────────────────
tasks = ["文献调研", "数据采集", "模型开发", "实验验证", "论文撰写", "投稿准备"]
start = [0, 1, 2, 4, 5, 7]
duration = [1.5, 3, 2.5, 2, 1.5, 1]
phases = ["前期", "前期", "中期", "中期", "后期", "后期"]

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("thesis", "pastel", lang="zh")

fig, ax = sp.plot_gantt(
    tasks,
    start=start,
    duration=duration,
    color_by=phases,
    xlabel="周次",
    ylabel="任务",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/22_gantt", formats=("png",), dpi=300)
