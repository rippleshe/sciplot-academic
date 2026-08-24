"""
50_composite_hero.py — Nature 复合图模板：不对称 Hero 布局

Nature 高频页面原型（asymmetric mixed-modality）：一个主导面板
承载核心结论（Hero），卫星面板回答次要问题。
使用 sp.hero_layout() 获得 2/3 宽主面板 + 右侧 2×1 卫星。
"""

import numpy as np
import sciplot as sp

rng = np.random.default_rng(50)

# ── 模拟数据 ──────────────────────────────────────────────────
x = np.linspace(0, 12, 120)
# 主面板：剂量-响应曲线（四组）
doses = [0.5, 1.0, 2.0, 4.0]
curves = []
for d in doses:
    base = 100 * (1 - np.exp(-x * d / 4))
    curves.append(base + rng.normal(0, 2.5, 120))

# 卫星 1：IC50 分布（箱线）
ic50 = np.array([rng.normal(m, 0.25, 30) for m in (2.2, 1.6, 1.1, 0.7)])

# 卫星 2：稳态浓度 vs 剂量（散点 + 回归）
dose_pts = np.array([0.5, 1.0, 2.0, 4.0])
conc = dose_pts * rng.uniform(1.8, 2.3, 4)

# ── Hero 布局：左侧主面板 + 右侧双卫星 ────────────────────────
result = sp.hero_layout("hero_right", venue="thesis")

ax_hero = result.ax_hero
colors = sp.get_palette("pastel-4")
for d, c, y in zip(doses, colors, curves):
    ax_hero.plot(x, y, color=c, linewidth=1.6, label=f"{d} mg/kg")
ax_hero.set_xlabel("时间 (h)", fontsize=8)
ax_hero.set_ylabel("响应 (%)", fontsize=8)
ax_hero.set_ylim(0, 120)
ax_hero.legend(frameon=False, fontsize=7, loc="lower right")

ax_ic50 = result.ax_satellite(0)
ax_ic50.boxplot(ic50, patch_artist=True, showfliers=False,
                medianprops=dict(color="#333333"),
                boxprops=dict(facecolor="#D6E4F0", edgecolor="#2E6DA4"))
ax_ic50.set_xticks(range(1, 5))
ax_ic50.set_xticklabels([f"{d:.1f}" for d in doses], fontsize=7)
ax_ic50.set_xlabel("剂量 (mg/kg)", fontsize=8)
ax_ic50.set_ylabel("IC50", fontsize=8)
ax_ic50.tick_params(labelsize=7)

ax_conc = result.ax_satellite(1)
ax_conc.scatter(dose_pts, conc, s=36, color="#C0392B",
                edgecolors="white", linewidths=0.5, zorder=3)
ax_conc.plot(dose_pts, conc, color="#C0392B", linewidth=0.9, alpha=0.6)
ax_conc.set_xlabel("剂量 (mg/kg)", fontsize=8)
ax_conc.set_ylabel("稳态浓度", fontsize=8)
ax_conc.tick_params(labelsize=7)

sp.save(result.fig, "showcase/50_composite_hero", formats=("png",), dpi=300)
