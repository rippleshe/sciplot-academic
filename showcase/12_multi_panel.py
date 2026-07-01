"""
12_multi_panel.py — 多面板组合图

展示 SciPlot 的 paper_subplots() + add_panel_labels() 功能：
创建 2×2 子图布局，分别绘制折线图、柱状图、散点图、热力图，
并添加 (a)(b)(c)(d) 面板标签。
使用 pastel 配色，Nature 默认样式，中文标签。
"""

import numpy as np
import sciplot as sp
import matplotlib.pyplot as plt

# 可复现随机种子
np.random.seed(42)

# ── 创建 2×2 子图布局 ────────────────────────────────────────
fig, axes = sp.paper_subplots(2, 2, venue="nature")

# ═══════════════════════════════════════════════════════════════
# (a) 折线图：不同温度下的反应速率
# ═══════════════════════════════════════════════════════════════
ax = axes[0, 0]
time = np.linspace(0, 60, 100)  # 反应时间 (min)

# 阿伦尼乌斯模型：k = A * exp(-Ea/RT)
k_300 = 0.05 * np.exp(-0.02 * time) + np.random.normal(0, 0.003, len(time))
k_320 = 0.08 * np.exp(-0.015 * time) + np.random.normal(0, 0.004, len(time))
k_340 = 0.12 * np.exp(-0.010 * time) + np.random.normal(0, 0.005, len(time))

colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]
ax.plot(time, k_300, label="300 K", color=colors[0])
ax.plot(time, k_320, label="320 K", color=colors[1])
ax.plot(time, k_340, label="340 K", color=colors[2])
ax.set_xlabel("反应时间 (min)")
ax.set_ylabel("反应速率 (mol·L⁻¹·s⁻¹)")
ax.legend()
ax.tick_params(direction="in")

# ═══════════════════════════════════════════════════════════════
# (b) 柱状图：不同催化剂的转化率
# ═══════════════════════════════════════════════════════════════
ax = axes[0, 1]
catalysts = ["Pt/C", "Pd/C", "Ru/C", "Ir/C", "Au/C"]
conversion = np.array([92.3, 85.7, 78.4, 88.1, 65.2])
errors = np.array([2.1, 3.4, 4.2, 2.8, 5.0])

bar_colors = [colors[i % len(colors)] for i in range(len(catalysts))]
bars = ax.bar(catalysts, conversion, yerr=errors, capsize=4,
              color=bar_colors, alpha=0.85, error_kw={"linewidth": 1})
ax.set_xlabel("催化剂类型")
ax.set_ylabel("转化率 (%)")
ax.set_ylim(0, 105)
ax.tick_params(direction="in")

# ═══════════════════════════════════════════════════════════════
# (c) 散点图：粒径 vs 催化活性
# ═══════════════════════════════════════════════════════════════
ax = axes[1, 0]
n_particles = 60
particle_size = np.random.uniform(2, 20, n_particles)  # nm
# 活性随粒径增大而降低（反比关系 + 噪声）
activity = 150 / particle_size + np.random.normal(0, 2, n_particles)

ax.scatter(particle_size, activity, s=25, alpha=0.7, color=colors[3])
# 拟合趋势线
z = np.polyfit(particle_size, activity, 2)
p = np.poly1d(z)
x_fit = np.linspace(2, 20, 100)
ax.plot(x_fit, p(x_fit), "--", color="#666666", linewidth=1, label="趋势拟合")
ax.set_xlabel("纳米粒径 (nm)")
ax.set_ylabel("催化活性 (μmol·g⁻¹·s⁻¹)")
ax.legend()
ax.tick_params(direction="in")

# ═══════════════════════════════════════════════════════════════
# (d) 热力图：实验条件参数扫描
# ═══════════════════════════════════════════════════════════════
ax = axes[1, 1]
temperatures = ["25°C", "50°C", "75°C", "100°C", "125°C"]
pressures = ["1 atm", "2 atm", "3 atm", "5 atm", "8 atm"]

# 模拟产率矩阵（温度↑压力↑→产率↑，但有最优区间）
T = np.arange(5)
P = np.arange(5)
T_grid, P_grid = np.meshgrid(T, P)
yield_data = 60 + 25 * (1 - np.exp(-0.5 * T_grid)) * (1 - np.exp(-0.3 * P_grid)) \
             + np.random.normal(0, 2, (5, 5))
yield_data = np.clip(yield_data, 40, 100)

im = ax.imshow(yield_data, cmap="YlOrRd", aspect="auto")
fig.colorbar(im, ax=ax, label="产率 (%)", fraction=0.046, pad=0.04)
ax.set_xticks(np.arange(len(temperatures)))
ax.set_xticklabels(temperatures, rotation=45, ha="right")
ax.set_yticks(np.arange(len(pressures)))
ax.set_yticklabels(pressures)
ax.set_xlabel("反应温度")
ax.set_ylabel("反应压力")

# 标注数值
for i in range(yield_data.shape[0]):
    for j in range(yield_data.shape[1]):
        ax.text(j, i, f"{yield_data[i, j]:.0f}",
                ha="center", va="center", fontsize=7,
                color="white" if yield_data[i, j] > 75 else "black")

# ── 添加面板标签 ──────────────────────────────────────────────
sp.add_panel_labels(axes)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/12_multi_panel", formats=("png",), dpi=300)
