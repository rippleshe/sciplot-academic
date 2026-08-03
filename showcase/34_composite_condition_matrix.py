"""
34_composite_condition_matrix.py — Nature 复合图模板：条件矩阵（2×3）

布局原型：condition matrix（治疗组合矩阵）。
2 行（药物 A/B）× 3 列（剂量 0/1/2）共 6 个面板，
共享 y 轴方便纵向比较；面板标签 (a)-(f) 按阅读顺序自动生成。
"""

import numpy as np
import sciplot as sp

rng = np.random.default_rng(11)

# ── 模拟数据：药物 × 剂量 → 响应分布 ──────────────────────────
drugs = ["药物 A", "药物 B"]
doses = ["对照", "低剂量", "高剂量"]
# 每组 40 个样本：药物 A 剂量效应更强，药物 B 平台期更早
effects = {
    ("药物 A", "对照"): rng.normal(0.30, 0.06, 40),
    ("药物 A", "低剂量"): rng.normal(0.55, 0.07, 40),
    ("药物 A", "高剂量"): rng.normal(0.82, 0.05, 40),
    ("药物 B", "对照"): rng.normal(0.32, 0.06, 40),
    ("药物 B", "低剂量"): rng.normal(0.62, 0.06, 40),
    ("药物 B", "高剂量"): rng.normal(0.70, 0.08, 40),
}
# 双编码配色：行（药物）= 色相，列（剂量）= 明度梯度
# 药物 A（暖色系）：浅 → 深；药物 B（冷色系）：浅 → 深
dose_colors = {
    ("药物 A", "对照"): "#F5C9AB", ("药物 A", "低剂量"): "#E79B6B", ("药物 A", "高剂量"): "#D96A3A",
    ("药物 B", "对照"): "#BCD0E6", ("药物 B", "低剂量"): "#7FA8D0", ("药物 B", "高剂量"): "#4A7DB8",
}
mean_colors = {
    ("药物 A", "对照"): "#B85C2E", ("药物 A", "低剂量"): "#B85C2E", ("药物 A", "高剂量"): "#B85C2E",
    ("药物 B", "对照"): "#3A628F", ("药物 B", "低剂量"): "#3A628F", ("药物 B", "高剂量"): "#3A628F",
}

# ── 布局：2×3 条件矩阵 ────────────────────────────────────────
fig, axes = sp.figure_panels(2, 3, venue="thesis", sharey=True, hspace=0.35, wspace=0.28)

for ax, (i, j) in zip(axes.flat, [(r, c) for r in range(2) for c in range(3)]):
    drug = drugs[i]
    dose = doses[j]
    data = effects[(drug, dose)]
    # 蜂群式抖动散点 + 均值线（面板内 matplotlib 原生）
    x_jitter = rng.normal(0, 0.02, len(data))
    ax.scatter(np.full(len(data), 0) + x_jitter, data,
               s=14, alpha=0.65, color=dose_colors[(drug, dose)],
               edgecolors="white", linewidths=0.4)
    ax.axhline(float(np.mean(data)), color=mean_colors[(drug, dose)],
               linestyle="--", linewidth=1.0)
    ax.set_ylim(0.0, 1.05)
    ax.set_xticks([])
    ax.tick_params(direction="in")
    ax.set_title(dose, fontsize=9)

# 行标签（左侧）与 y 轴标签
axes[0, 0].set_ylabel("药物 A\n响应值", fontsize=9)
axes[1, 0].set_ylabel("药物 B\n响应值", fontsize=9)
axes[1, 0].set_xlabel("剂量组", fontsize=9)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/34_composite_condition_matrix", formats=("png",), dpi=300)
