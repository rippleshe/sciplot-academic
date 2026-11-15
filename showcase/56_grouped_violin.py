"""
56_grouped_violin.py — 多组跨条件分布对比（Grouped Violin + 箱线 + 散点）

展示 SciPlot v1.16.0 新增的 `plot_grouped_violin()`，
在同一画布中清晰比较疾病分期与三种干预策略的交互分布。
"""

import numpy as np
import sciplot as sp

rng = np.random.default_rng(2026)

sp.setup_style("nature", "coral-teal", lang="zh")

stages = ["I 期", "II 期", "III 期", "IV 期"]
means = {
    "常规对照": [18.5, 20.2, 21.8, 23.0],
    "标准方案": [21.0, 24.5, 27.2, 28.4],
    "联合靶向": [23.8, 29.5, 34.8, 37.6],
}
stds = {
    "常规对照": [2.2, 2.5, 2.8, 3.1],
    "标准方案": [2.4, 2.8, 3.2, 3.5],
    "联合靶向": [2.1, 2.6, 3.0, 3.2],
}

series = {
    name: [rng.normal(m, s, size=42) for m, s in zip(means[name], stds[name])]
    for name in means
}

fig, _ = sp.plot_grouped_violin(
    stages,
    series,
    xlabel="临床病理分期",
    ylabel="免疫应答综合评分",
    title="不同分期下三种治疗方案的应答分布特征",
    show_box=True,
    show_mean=True,
    show_points=True,
)
sp.save(fig, "showcase/56_grouped_violin", formats=("png",), dpi=300)
