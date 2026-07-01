"""
08_density.py — 多组核密度估计图

展示 SciPlot 的 plot_multi_density() 功能：4 个实验组的测量值分布。
使用 fill=True 填充密度曲线下方区域，Nature 默认样式，中文标签。
"""

import numpy as np
import sciplot as sp

# 可复现随机种子
np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
# 模拟 4 个实验组的测量值（如不同处理条件下的细胞直径，单位 μm）
n_samples = 300

# 对照组：均值 10，标准差 1.5
group_control = np.random.normal(loc=10.0, scale=1.5, size=n_samples)

# 处理组 A：均值 12，标准差 1.8（轻微增大）
group_a = np.random.normal(loc=12.0, scale=1.8, size=n_samples)

# 处理组 B：均值 9，标准差 1.2（略微减小，更集中）
group_b = np.random.normal(loc=9.0, scale=1.2, size=n_samples)

# 处理组 C：双峰分布（两种亚群）
n_half = n_samples // 2
group_c_sub1 = np.random.normal(loc=8.0, scale=0.8, size=n_half)
group_c_sub2 = np.random.normal(loc=13.0, scale=1.0, size=n_samples - n_half)
group_c = np.concatenate([group_c_sub1, group_c_sub2])

data_list = [group_control, group_a, group_b, group_c]
labels = ["对照组", "处理组 A", "处理组 B", "处理组 C"]

# ── 绘图 ──────────────────────────────────────────────────────
fig, ax = sp.plot_multi_density(
    data_list,
    labels=labels,
    xlabel="细胞直径 (μm)",
    ylabel="概率密度",
    title="不同处理条件下细胞直径分布",
    fill=True,
    alpha=0.3,
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/08_density", formats=("png",), dpi=300)
