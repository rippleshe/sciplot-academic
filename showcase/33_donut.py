"""
33_donut.py — 环形图

展示 plot_donut()：某高校科研经费来源构成（百万元）。
中心挖空的环形设计，外圈类别标签 + 环内数值 + 百分比，
适合“整体构成”叙事。
"""

import sciplot as sp

# ── 数据 ──────────────────────────────────────────────────────
sources = ["国家基金", "省部级项目", "企业横向", "国际合作", "校内配套"]
amounts = [48.0, 22.0, 18.0, 7.0, 5.0]

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("presentation", "pastel", lang="zh")

fig, ax = sp.plot_donut(
    sources,
    amounts,
    hole_ratio=0.62,
    fmt=".1f",
    show_percent=True,
    center_text="100 百万元",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/33_donut", formats=("png",), dpi=300)
