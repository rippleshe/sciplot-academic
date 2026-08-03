"""
16_ridgeline.py — 山脊图

展示 plot_ridgeline()：四个实验组小鼠的血清标志物浓度分布堆叠对比，
直观呈现处理效应导致分布中心右移与展宽变化。
"""

import numpy as np
import sciplot as sp

np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
# 4 组小鼠（每组 400 只）的血清标志物浓度 (ng/mL)
groups = [
    np.random.normal(100, 15, 400),     # 对照组
    np.random.normal(118, 18, 400),     # 低剂量
    np.random.normal(142, 22, 400),     # 中剂量
    np.random.normal(175, 28, 400),     # 高剂量
]
group_names = ["对照组", "低剂量", "中剂量", "高剂量"]

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("nature", "forest", lang="zh")

fig, ax = sp.plot_ridgeline(
    groups,
    labels=group_names,
    xlabel="血清标志物浓度 (ng/mL)",
    ylabel="实验组",
    overlap=0.35,
    show_median=True,
    title="不同剂量组标志物浓度分布",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/16_ridgeline", formats=("png",), dpi=300)
