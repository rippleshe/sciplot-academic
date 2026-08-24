"""
49_colorblind_okabe_ito.py — 色盲安全：Okabe-Ito 调色板 + 模拟对比

展示新内置的 Okabe-Ito 色盲安全调色板，以及 simulate_colorblind()
的模拟效果（绿色弱视角），强调"审稿七宗罪"之一的配色防线。
"""

import numpy as np
import matplotlib.pyplot as plt
import sciplot as sp

# ── 数据：四个类别的折线 ──────────────────────────────────────
rng = np.random.default_rng(49)
x = np.linspace(0, 10, 80)
series = [
    x * 0.35 + rng.normal(0, 0.4, 80),
    x * 0.25 + 3.0 + rng.normal(0, 0.4, 80),
    x * 0.15 + 6.0 + rng.normal(0, 0.4, 80),
    x * 0.05 + 9.0 + rng.normal(0, 0.4, 80),
]
labels = ["类别 1", "类别 2", "类别 3", "类别 4"]
colors = sp.OKABE_ITO["okabe-ito-4"]

# 显式套用样式（含中文字体），避免手写 subplots 时字体缺失
sp.setup_style("nature", "okabe-ito", lang="zh")

# ── 上半：Okabe-Ito 调色板（正常视角） ────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(6.5, 5.2),
                         gridspec_kw=dict(hspace=0.45))

ax = axes[0]
for s, c, lb in zip(series, colors, labels):
    ax.plot(x, s, color=c, linewidth=1.6, label=lb)
ax.set_title("Okabe-Ito 调色板（正常视角）", fontsize=10)
ax.legend(frameon=False, fontsize=8)
ax.tick_params(direction="in", labelsize=8)

# ── 下半：绿色弱（deuteranopia）模拟视角 ──────────────────────
ax2 = axes[1]
sim = sp.simulate_colorblind(colors, "deuteranopia")
for s, c, lb in zip(series, sim, labels):
    ax2.plot(x, s, color=c, linewidth=1.6, label=lb)
ax2.set_title("绿色弱 (Deuteranopia) 模拟视角", fontsize=10)
ax2.legend(frameon=False, fontsize=8)
ax2.tick_params(direction="in", labelsize=8)

# 论文式双面板必须有明确阅读顺序；使用库内统一面板标签而不是手写文本。
sp.add_panel_labels(axes, x=-0.08, y=1.08)

# ── 审计报告标注 ──────────────────────────────────────────────
report = sp.audit_palette("okabe-ito")
fig.suptitle(f"色盲安全审计: safe={report['safe']}，"
             f"n={report['n_colors']} 色全部可区分",
             fontsize=11, y=0.98)

sp.save(fig, "showcase/49_colorblind_okabe_ito", formats=("png",), dpi=300)
