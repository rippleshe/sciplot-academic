"""
38_composite_time_march.py — Nature 复合图模板：时间推进（Time-March）

布局原型：time-march（同一系统随时间演化的快照序列）。
2×2 网格展示污染物浓度扩散的 4 个时刻，共享 vmin/vmax 与色标，
时间戳标注在每面板角落，直观呈现“扩散-稀释”过程。
"""

import numpy as np
import matplotlib.pyplot as plt
import sciplot as sp

# ── 模拟二维扩散场（简化高斯扩散模型） ────────────────────────
grid = 60
x = np.linspace(-3, 3, grid)
y = np.linspace(-3, 3, grid)
X, Y = np.meshgrid(x, y)
r = np.sqrt(X**2 + Y**2)

def plume(t: float) -> np.ndarray:
    """点源扩散：随 t 增大，峰高降低、宽度增加（质量守恒）。"""
    sigma = 0.35 + 0.55 * np.sqrt(t)
    return np.exp(-(r**2) / (2 * sigma**2)) / (2 * np.pi * sigma**2)

times = [1.0, 4.0, 12.0, 24.0]
fields = [plume(t) for t in times]
vmin, vmax = 0.0, float(np.max(fields[0]))

# ── 布局：2×2 时间快照 ────────────────────────────────────────
sp.setup_style("thesis", "ocean", lang="zh")
fig, axes = plt.subplots(2, 2, figsize=(5.6, 5.0),
                         gridspec_kw=dict(hspace=0.32, wspace=0.28))
axes = np.atleast_2d(axes)

cmap = plt.get_cmap("YlOrRd")
for ax, t, fld in zip(axes.flat, times, fields):
    im = ax.imshow(fld, extent=[0, 1, 0, 1], cmap=cmap,
                   vmin=vmin, vmax=vmax, origin="lower")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.tick_params(direction="in")
    # 时间戳（角落标注）
    ax.text(0.03, 0.93, f"t = {t:.0f} h", transform=ax.transAxes,
            fontsize=8, color="#7A2E10", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                      edgecolor="none", alpha=0.75))
    ax.set_title(f"时刻 {t:.0f}", fontsize=9)

# ── 统一色标（底部通栏） ──────────────────────────────────────
cbar = fig.colorbar(im, ax=axes, fraction=0.030, pad=0.06, aspect=40)
cbar.set_label("浓度 (归一化)", fontsize=8)
cbar.ax.tick_params(labelsize=7)

# ── 面板标签 ─────────────────────────────────────────────────
for ax, lbl in zip(axes.flat, ["a", "b", "c", "d"]):
    ax.text(-0.14, 1.08, f"({lbl})", transform=ax.transAxes,
            fontweight="bold", fontsize=11)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/38_composite_time_march", formats=("png",), dpi=300)
