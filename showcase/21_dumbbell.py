"""
21_dumbbell.py — 哑铃图

展示 plot_dumbbell()：训练前后成绩对比。
场景：六个学员的培训前后测评分数变化。
"""

import numpy as np
import sciplot as sp

np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
students = ["学员A", "学员B", "学员C", "学员D", "学员E", "学员F"]
before = np.array([62, 71, 55, 68, 74, 58])
after = np.array([81, 79, 74, 85, 83, 76])

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("thesis", "ocean", lang="zh")

fig, ax = sp.plot_dumbbell(
    students,
    before,
    after,
    xlabel="测评分数 (分)",
    ylabel="学员",
    start_label="培训前",
    end_label="培训后",
    show_values=True,
    sort_by="delta",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/21_dumbbell", formats=("png",), dpi=300)
