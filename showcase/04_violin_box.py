"""
04_violin_box.py — 小提琴图

展示 SciPlot 的 plot_violin() 功能：4 种不同处理条件下水稻产量的分布比较。
显示均值线，展示数据分布形状。
"""

import numpy as np
import sciplot as sp

# 可复现随机种子
np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
# 模拟 4 种施肥处理下水稻产量 (t/ha) 的田间试验数据
n_reps = 80  # 每组 80 个重复

# 对照组：常规施肥，产量中等
control = np.random.normal(loc=7.2, scale=0.8, size=n_reps)

# 处理 1：有机肥替代，产量略高且更稳定
organic = np.random.normal(loc=7.8, scale=0.5, size=n_reps)

# 处理 2：缓释肥，产量高但变异较大
slow_release = np.random.normal(loc=8.3, scale=1.0, size=n_reps)

# 处理 3：有机肥 + 缓释肥配施，产量最高且稳定
combined = np.random.normal(loc=8.9, scale=0.6, size=n_reps)

data = [control, organic, slow_release, combined]
labels = ["对照（常规施肥）", "有机肥替代", "缓释肥", "配施处理"]

# ── 绘图 ──────────────────────────────────────────────────────
fig, ax = sp.plot_violin(
    data,
    labels=labels,
    xlabel="施肥处理",
    ylabel="水稻产量 (t/ha)",
    title="不同施肥处理对水稻产量分布的影响",
    showmeans=True,
    palette="pastel",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/04_violin_box", formats=("png",), dpi=300)
