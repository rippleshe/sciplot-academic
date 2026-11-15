"""
58_method_heatmap.py — 多方法 × 多指标归一化基准矩阵热力图

展示 SciPlot v1.16.0 新增的 `plot_method_heatmap()`：
自动统一“越大越好 / 越小越好”指标方向并列归一化，
在格子内呈现原始真实数值，高亮每项最优模型并附带综合评分榜与排序。
"""

import numpy as np
import sciplot as sp

sp.setup_style("nature", "okabe-ito", lang="en")

methods = [
    "Proposed GraphFormer",
    "ViT-Base",
    "Swin-Tiny",
    "ConvNeXt-S",
    "ResNet-50",
    "XGBoost-Tabular",
]
metrics = [
    "Accuracy (%)",
    "Macro-F1 (%)",
    "ROC-AUC (%)",
    "Latency (ms)",
    "Params (M)",
]

# 真实量纲下的跨模型基准矩阵（前 3 项越大越好，后 2 项越小越好）
scores = np.array(
    [
        [94.2, 92.8, 96.7, 11.4, 18.2],
        [91.8, 90.1, 94.5, 24.8, 86.0],
        [92.6, 91.2, 95.3, 18.5, 28.3],
        [91.4, 89.6, 94.1, 15.2, 49.6],
        [88.7, 86.4, 91.8, 9.8, 25.6],
        [87.2, 85.1, 90.4, 4.2, 3.1],
    ]
)

direction = {
    "Accuracy (%)": True,
    "Macro-F1 (%)": True,
    "ROC-AUC (%)": True,
    "Latency (ms)": False,
    "Params (M)": False,
}

fig, _ = sp.plot_method_heatmap(
    scores,
    methods=methods,
    metrics=metrics,
    higher_is_better=direction,
    show_overall=True,
    highlight_best=True,
    show_rank=True,
    sort_by_overall=True,
    title="Cross-Metric Benchmark Comparison (Raw Values + Column-Normalized Shade)",
)
sp.save(fig, "showcase/58_method_heatmap", formats=("png",), dpi=300)
