"""
35_composite_comparative.py — Nature 复合图模板：对照双列（1×2）

布局原型：comparative columns（条件 A vs 条件 B 对照）。
左列：基线方法；右列：改进方法。两列共享 y 轴，
面板内用同色系的折线/柱对比，保持一致的视觉语言。
"""

import numpy as np
import sciplot as sp

rng = np.random.default_rng(21)

# ── 模拟数据：两个模型在 8 个数据集上的性能 ────────────────────
datasets = [f"D{i + 1}" for i in range(8)]
acc_base = rng.uniform(0.72, 0.86, 8)
acc_prop = acc_base + rng.uniform(0.04, 0.09, 8)

# ── 布局：1×2 对照双列 ────────────────────────────────────────
fig, axes = sp.figure_panels(1, 2, venue="thesis", widths=[1, 1], sharey=True, wspace=0.30)

# 左：基线准确率（浅色柱 + 数值标注）
x = np.arange(len(datasets))
axes[0].bar(x, acc_base, width=0.62, color="#9DB8D2", edgecolor="white", linewidth=0.6)
axes[0].set_ylim(0.6, 1.0)
axes[0].set_xticks(x)
axes[0].set_xticklabels(datasets, fontsize=7)
axes[0].set_ylabel("准确率", fontsize=9)
axes[0].tick_params(direction="in")
axes[0].set_title("基线模型", fontsize=10)

# 右：改进方法（深色柱 + 增益标注）
axes[1].bar(x, acc_prop, width=0.62, color="#3E7CB1", edgecolor="white", linewidth=0.6)
axes[1].set_ylim(0.6, 1.0)
axes[1].set_xticks(x)
axes[1].set_xticklabels(datasets, fontsize=7)
axes[1].tick_params(direction="in")
axes[1].set_title("本文方法", fontsize=10)
for xi, (b, p) in enumerate(zip(acc_base, acc_prop)):
    axes[1].text(xi, p + 0.012, f"+{(p - b) * 100:.1f}%",
                 ha="center", fontsize=6, color="#2C5F8A")

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/35_composite_comparative", formats=("png",), dpi=300)
