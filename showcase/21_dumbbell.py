"""
21_dumbbell.py — 哑铃图

展示 plot_dumbbell()：2023 vs 2024 十大城市空气质量改善对比。
连线按改善/恶化着色，起点均值参考线，标签上下交替错位。
"""

import numpy as np
import sciplot as sp

# ── 数据生成 ──────────────────────────────────────────────────
cities = [
    "北京", "上海", "广州", "深圳", "成都", "杭州",
    "武汉", "西安", "郑州", "沈阳",
]
pm25_2023 = np.array([41, 32, 28, 24, 36, 30, 44, 52, 58, 47])
pm25_2024 = np.array([34, 29, 27, 22, 33, 26, 40, 46, 51, 40])

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("thesis", "ocean", lang="zh")

fig, ax = sp.plot_dumbbell(
    cities,
    pm25_2023,
    pm25_2024,
    xlabel="PM2.5 年均浓度 (μg/m³)",
    ylabel="城市",
    start_label="2023 年",
    end_label="2024 年",
    show_values=True,
    sort_by="delta",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/21_dumbbell", formats=("png",), dpi=300)
