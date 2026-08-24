"""
48_composite_triptych.py — Nature 复合图模板：临床三联画（Triptych）

对齐 Nature 2024-2026 高频页面原型（clinical triptych）：
- 上行：两组时序曲线（纵向随访），共享图例条
- 中行：森林图风格效应量（虚线参考线 + 浅色分组带）
- 下行：紧凑汇总柱（二元/百分比）

使用 sp.figure_panels(template="triptych") 一次获得 3×2 网格、
行高比 [1, 0.9, 0.7]、8pt 加粗面板标签。
"""

import numpy as np
import sciplot as sp

rng = np.random.default_rng(48)

# ── 模拟数据 ──────────────────────────────────────────────────
weeks = np.arange(0, 13)
# 两组随访轨迹（均值 ± 波动）
group_a = 50 + 8 * np.log1p(weeks) + rng.normal(0, 1.2, 13)
group_b = 50 + 4 * np.log1p(weeks) + rng.normal(0, 1.2, 13)

# 森林图数据（6 个亚组效应）
subgroups = ["亚组 1", "亚组 2", "亚组 3", "亚组 4", "亚组 5", "亚组 6"]
fx = np.array([0.9, 0.6, 1.3, 0.75, 1.05, 0.45])
fse = np.array([0.18, 0.22, 0.25, 0.20, 0.23, 0.19])
flo = fx - 1.96 * fse
fhi = fx + 1.96 * fse

# 汇总柱数据（两列：有效率 / 不良事件率）
cat_a = np.array([72, 68, 75, 64, 70, 66])
cat_b = np.array([12, 15, 10, 18, 14, 16])

# ── 布局：临床三联画（3×2，共享模板） ─────────────────────────
fig, axes = sp.figure_panels(template="triptych", venue="thesis")

# ── 上行：时序曲线 ────────────────────────────────────────────
for ax, series, label, color in zip(
    axes[0],
    [group_a, group_b],
    ["治疗组", "对照组"],
    ["#C0392B", "#2E6DA4"],
):
    ax.plot(weeks, series, "-o", color=color, markersize=3,
            linewidth=1.5, label=label)
    ax.set_ylim(45, 85)
    ax.set_xlabel("周", fontsize=8)
    ax.set_ylabel("指标值", fontsize=8)
    ax.legend(frameon=False, fontsize=7, loc="lower right")
    ax.tick_params(labelsize=7)

# ── 中行：森林图（效应量） ────────────────────────────────────
for ax in axes[1]:
    ax.errorbar(fx, np.arange(6), xerr=[fx - flo, fhi - fx],
                fmt="D", color="#C0392B", markersize=4,
                elinewidth=1.2, capsize=2.5, capthick=1.0)
    ax.axvline(1.0, color="#444444", linestyle="--", linewidth=0.9)
    ax.set_yticks(np.arange(6))
    ax.set_yticklabels(subgroups, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel("效应量 (95% CI)", fontsize=8)
    ax.tick_params(labelsize=7)

# ── 下行：汇总柱 ──────────────────────────────────────────────
x_cat = np.arange(6)
for ax, vals, label, color in zip(
    axes[2],
    [cat_a, cat_b],
    ["有效率 (%)", "不良事件率 (%)"],
    ["#2E6DA4", "#C0392B"],
):
    ax.bar(x_cat, vals, color=color, width=0.6,
           edgecolor="white", linewidth=0.6)
    ax.set_ylim(0, 90)
    ax.set_xticks(x_cat)
    ax.set_xticklabels([f"G{i+1}" for i in range(6)], fontsize=7)
    ax.set_ylabel(label, fontsize=8)
    ax.tick_params(labelsize=7)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/48_composite_triptych", formats=("png",), dpi=300)
