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

# 森林图数据（6 个亚组：主要终点 vs 次要终点，避免左右面板重复）
subgroups = ["< 65 岁", ">= 65 岁", "女性", "男性", "早中期", "晚进展期"]
fx_pri = np.array([0.82, 0.64, 1.18, 0.72, 0.96, 0.54])
fse_pri = np.array([0.16, 0.19, 0.21, 0.17, 0.20, 0.15])
flo_pri, fhi_pri = fx_pri - 1.96 * fse_pri, fx_pri + 1.96 * fse_pri

fx_sec = np.array([0.94, 0.78, 1.05, 0.85, 1.12, 0.68])
fse_sec = np.array([0.14, 0.17, 0.18, 0.16, 0.19, 0.16])
flo_sec, fhi_sec = fx_sec - 1.96 * fse_sec, fx_sec + 1.96 * fse_sec

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
    ax.plot(weeks, series, "-o", color=color, markersize=3.4,
            markeredgecolor="white", markeredgewidth=0.6,
            linewidth=1.5, label=label)
    ax.set_ylim(45, 85)
    ax.set_xlabel("随访周数", fontsize=8)
    ax.set_ylabel("指标值", fontsize=8)
    ax.legend(frameon=False, fontsize=7, loc="lower right")
    ax.tick_params(labelsize=7)
    sp.polish_axis(ax, clean_spines=True, grid="y")

# ── 中行：森林图（左：主要终点；右：次要终点） ─────────────────
forest_specs = [
    (axes[1, 0], fx_pri, flo_pri, fhi_pri, "#C0392B", "主要终点 HR (95% CI)"),
    (axes[1, 1], fx_sec, flo_sec, fhi_sec, "#2E6DA4", "次要终点 HR (95% CI)"),
]
for idx, (ax, fx, flo, fhi, col, xlab) in enumerate(forest_specs):
    ax.errorbar(fx, np.arange(6), xerr=[fx - flo, fhi - fx],
                fmt="D", color=col, markeredgecolor="white", markeredgewidth=0.5,
                markersize=4.2, elinewidth=1.2, capsize=2.5, capthick=1.0)
    ax.axvline(1.0, color="#64748B", linestyle="--", linewidth=0.9)
    ax.set_yticks(np.arange(6))
    if idx == 0:
        ax.set_yticklabels(subgroups, fontsize=7)
    else:
        ax.set_yticklabels([])
    ax.invert_yaxis()
    ax.set_xlim(0.15, 1.75)
    ax.set_xlabel(xlab, fontsize=8)
    ax.tick_params(labelsize=7)
    sp.polish_axis(ax, categorical_axis="y", clean_spines=True, grid="x")

# ── 下行：汇总柱 ──────────────────────────────────────────────
x_cat = np.arange(6)
for ax, vals, label, color in zip(
    axes[2],
    [cat_a, cat_b],
    ["有效率 (%)", "不良事件率 (%)"],
    ["#2E6DA4", "#C0392B"],
):
    bars = ax.bar(x_cat, vals, color=color, width=0.6)
    ax.set_ylim(0, 90)
    ax.set_xticks(x_cat)
    ax.set_xticklabels([f"G{i+1}" for i in range(6)], fontsize=7)
    ax.set_ylabel(label, fontsize=8)
    ax.tick_params(labelsize=7)
    sp.style_patch_edges(bars, [color])
    sp.polish_axis(ax, categorical_axis="x", clean_spines=True, grid="y")

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/48_composite_triptych", formats=("png",), dpi=300)
