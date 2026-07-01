"""
02_grouped_bar.py — 分组柱状图

展示 SciPlot 的 plot_grouped_bar() 功能：4 种分类模型在 3 个数据集上的
准确率、F1 分数和 AUC 对比。柱顶显示数值。
"""

import numpy as np
import sciplot as sp

# 可复现随机种子
np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
# 模拟 4 种分类模型在 3 个基准数据集上的性能指标
datasets = ["CIFAR-10", "CIFAR-100", "ImageNet"]

# 各模型的真实表现范围（带少量随机扰动）
model_data = {
    "ResNet-50":   np.array([92.1, 74.3, 76.0]) + np.random.normal(0, 0.15, 3),
    "ViT-B/16":    np.array([93.4, 77.2, 79.8]) + np.random.normal(0, 0.15, 3),
    "Swin-T":      np.array([94.0, 78.9, 81.3]) + np.random.normal(0, 0.15, 3),
    "本文方法":     np.array([95.2, 81.5, 83.7]) + np.random.normal(0, 0.15, 3),
}

# 保留一位小数
for key in model_data:
    model_data[key] = np.round(model_data[key], 1)

# ── 绘图 ──────────────────────────────────────────────────────
fig, ax = sp.plot_grouped_bar(
    groups=datasets,
    data=model_data,
    xlabel="数据集",
    ylabel="Top-1 准确率 (%)",
    title="各模型在基准数据集上的分类性能对比",
    show_values=True,
    value_fmt=".1f",
    palette="pastel",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/02_grouped_bar", formats=("png",), dpi=300)
