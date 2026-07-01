"""
07_radar.py — 雷达图（多维模型性能对比）

展示 SciPlot 的 plot_radar() 功能：3 种分类模型在 6 个评估指标上的性能对比。
使用 fill=True 填充区域，Nature 默认样式，中文标签。
"""

import numpy as np
import sciplot as sp

# 可复现随机种子
np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
# 6 个评估指标
metrics = ["准确率", "精确率", "召回率", "F1 分数", "AUC", "特异度"]

# 模型 A：逻辑回归（基线模型）
model_lr = [0.82, 0.79, 0.76, 0.77, 0.85, 0.88]

# 模型 B：随机森林（集成方法）
model_rf = [0.88, 0.86, 0.84, 0.85, 0.92, 0.91]

# 模型 C：深度神经网络（最优模型）
model_dnn = [0.93, 0.91, 0.90, 0.90, 0.96, 0.95]

values_list = [model_lr, model_rf, model_dnn]
labels = ["逻辑回归", "随机森林", "深度神经网络"]

# ── 绘图 ──────────────────────────────────────────────────────
fig, ax = sp.plot_radar(
    metrics,
    values_list,
    labels=labels,
    fill=True,
    alpha=0.25,
    title="分类模型性能对比",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/07_radar", formats=("png",), dpi=300)
