"""
57_back_to_back_bar.py — 双向背靠背对比条形图（Back-to-Back / Mirror Bar）

展示 SciPlot v1.16.0 新增的 `plot_back_to_back_bar()`（别名 `mirror_bar`）：
以正值绝对刻度对称展示实验组与对照组的指标占比，并自动标注净差值 Δ。
"""

import sciplot as sp

sp.setup_style("nature", "blue-sky", lang="zh")

dimensions = [
    "临床缓解率",
    "一年无进展率",
    "生物标志物阳转",
    "生活质量改善",
    "免疫浸润提升",
    "耐受性良好",
    "快速起效比例",
    "二次复发控制",
]

control_pct = [42.5, 38.0, 29.4, 51.2, 34.8, 63.0, 27.5, 45.6]
treat_pct = [68.4, 61.5, 57.8, 72.0, 64.2, 74.5, 53.6, 66.8]

fig, _ = sp.plot_back_to_back_bar(
    dimensions,
    control_pct,
    treat_pct,
    left_label="标准对照队列 (%)",
    right_label="联合干预队列 (%)",
    xlabel="患者响应比例 (%)",
    title="临床干预队列与对照队列多维度疗效镜像对比",
    show_values=True,
    show_diff=True,
    fmt=".1f",
    sort_by="diff",
)
sp.save(fig, "showcase/57_back_to_back_bar", formats=("png",), dpi=300)
