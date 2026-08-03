"""
36_composite_hub_spoke.py — Nature 复合图模板：中心-辐条（Hub-and-Spoke）

布局原型：hub-and-spoke（中心总览 + 卫星细节）。
使用 sp.hero_layout("hub_spoke") 获得 3×3 网格：
中心主面板 + 上/左/右/下四个卫星面板，自动加 8pt 面板标签。
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
import sciplot as sp

rng = np.random.default_rng(7)

# ── 模拟数据 ──────────────────────────────────────────────────
# 中心：5 个类别的 F1 分数（雷达）
classes = ["正常", "轻度", "中度", "重度", "危重"]
f1_scores = np.array([0.94, 0.88, 0.85, 0.81, 0.76])

# 特征重要性（8 特征）
features = ["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8"]
importance = np.array([0.22, 0.18, 0.15, 0.12, 0.10, 0.09, 0.08, 0.06])

# 混淆矩阵（5×5，对角强）
cm = rng.uniform(0.5, 1.0, (5, 5)) * np.eye(5)
off = rng.uniform(0.02, 0.06, (5, 5))
np.fill_diagonal(off, 0)
cm = cm + off
cm = cm / cm.sum(axis=1, keepdims=True)

# 学习曲线
train_sizes = np.array([20, 40, 80, 160, 320, 640])
train_score = 1.0 - 0.25 * np.exp(-train_sizes / 120)
val_score = 1.0 - 0.28 * np.exp(-train_sizes / 140) - 0.02

# PR 曲线
recall = np.linspace(0, 1, 60)
precision = 0.90 - 0.25 * recall + 0.15 * recall**2 + rng.normal(0, 0.01, 60)
precision = np.clip(precision, 0, 1)

# ── 布局：hero_layout hub_spoke（中心 + 四卫星） ───────────────
sp.setup_style("thesis", "ocean", lang="zh")
result = sp.hero_layout("hub_spoke", venue="thesis")
ax_center = result.ax_hero
ax_top, ax_left, ax_right, ax_bottom = result.satellites

# ── 中心：雷达图（模型整体 F1） ──────────────────────────────
angles = np.linspace(0, 2 * np.pi, len(classes), endpoint=False).tolist()
values = f1_scores.tolist()
angles_c = angles + angles[:1]
values_c = values + values[:1]
ax_center.plot(angles_c, values_c, color="#2E6DA4", linewidth=1.8)
ax_center.fill(angles_c, values_c, color="#2E6DA4", alpha=0.18)
ax_center.set_xticks(angles)
ax_center.set_xticklabels(classes, fontsize=6.5)
ax_center.set_ylim(0, 1.0)
ax_center.set_title("模型总览（各类 F1）", fontsize=9)
ax_center.grid(True, linestyle="--", alpha=0.4)

# ── 卫星 1（上）：特征重要性 ─────────────────────────────────
ax_top.barh(features[::-1], importance[::-1], color="#5B9BD5",
            edgecolor="white", linewidth=0.4)
ax_top.set_title("特征重要性", fontsize=8)
ax_top.tick_params(axis="y", labelsize=6)

# ── 卫星 2（左）：混淆矩阵（归一化） ─────────────────────────
ax_left.imshow(cm, cmap="Blues", vmin=0, vmax=1)
ax_left.set_xticks(range(5))
ax_left.set_yticks(range(5))
ax_left.set_xticklabels([""] * 5, fontsize=5)
ax_left.set_yticklabels(classes, fontsize=5)
ax_left.set_title("混淆矩阵", fontsize=8)

# ── 卫星 3（右）：学习曲线 ───────────────────────────────────
ax_right.plot(train_sizes, train_score, "o-", color="#E07B54", markersize=3, label="训练")
ax_right.plot(train_sizes, val_score, "s-", color="#2E6DA4", markersize=3, label="验证")
ax_right.set_xscale("log")
ax_right.set_title("学习曲线", fontsize=8)
ax_right.tick_params(labelsize=6)
ax_right.legend(fontsize=5.5, frameon=False, loc="lower right")

# ── 卫星 4（下）：PR 曲线 ────────────────────────────────────
ax_bottom.plot(recall, precision, color="#5B7DB1", linewidth=1.5)
ax_bottom.fill_between(recall, precision, 0, color="#5B7DB1", alpha=0.12)
ax_bottom.set_title("PR 曲线", fontsize=8)
ax_bottom.tick_params(labelsize=6)

# ── 辐条连线（中心 → 卫星，fig 坐标） ───────────────────────
for sat in [ax_top, ax_left, ax_right, ax_bottom]:
    cp = ConnectionPatch(
        xyA=(0.5, 0.5), coordsA=ax_center.transAxes,
        xyB=(0.5, 0.5), coordsB=sat.transAxes,
        color="#BBBBBB", linewidth=0.8, linestyle="--", zorder=0,
    )
    result.fig.add_artist(cp)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(result.fig, "showcase/36_composite_hub_spoke", formats=("png",), dpi=300)
