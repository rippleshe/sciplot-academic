"""
40_circular_barplot.py — 环形条形图

展示 plot_circular_barplot()：12 个城市年降雨量（cm）环形排名。
条形围绕圆周排列，长度编码数值，外圈水平标签易读。
"""

import numpy as np
import sciplot as sp

# ── 数据 ──────────────────────────────────────────────────────
cities = ["上海", "广州", "深圳", "成都", "杭州", "武汉",
          "北京", "西安", "兰州", "乌鲁木齐", "拉萨", "哈尔滨"]
rainfall = np.array([116.0, 182.0, 193.0, 87.0, 145.0, 126.0,
                     57.0, 58.0, 32.0, 29.0, 45.0, 52.0])

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("presentation", "pastel", lang="zh")

fig, ax = sp.plot_circular_barplot(
    cities,
    rainfall,
    sort=True,
    show_values=True,
    fmt=".0f",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/40_circular_barplot", formats=("png",), dpi=300)
