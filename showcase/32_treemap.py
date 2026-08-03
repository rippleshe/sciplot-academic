"""
32_treemap.py — 矩形树图

展示 plot_treemap()：全球半导体市场按应用领域与细分市场的
营收占比（十亿美元，2025 年估算）。矩形面积编码占比，
squarify 算法保证接近正方形的高效布局。
"""

import numpy as np
import sciplot as sp

# ── 数据 ──────────────────────────────────────────────────────
segments = [
    "智能手机", "PC/平板", "服务器", "汽车电子", "工业控制",
    "通信设备", "消费电子", "物联网", "医疗电子", "航空航天",
    "数据中心", "存储", "网络", "显示驱动", "功率器件", "模拟芯片",
]
revenue = np.array([
    160, 85, 120, 95, 60,
    55, 45, 40, 25, 18,
    110, 50, 35, 30, 28, 22,
], dtype=float)

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("presentation", "forest", lang="zh")

fig, ax = sp.plot_treemap(
    segments,
    revenue,
    fmt=".0f",
    min_font=6.0,
    max_font=15.0,
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/32_treemap", formats=("png",), dpi=300)
