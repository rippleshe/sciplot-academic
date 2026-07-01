"""
10_3d_surface.py — 3D 曲面图

展示 SciPlot 的 plot_surface() 功能：绘制二维 sinc 函数的三维曲面，
模拟光学衍射的强度分布。选用合适的视角和配色以突出曲面结构。
使用 pastel 配色，Nature 默认样式，中文标签。
"""

import numpy as np
import sciplot as sp

# 可复现随机种子
np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
# 二维 sinc 函数：sinc(r) = sin(r) / r，模拟圆孔衍射的强度分布
resolution = 80
x = np.linspace(-8, 8, resolution)
y = np.linspace(-8, 8, resolution)
X, Y = np.meshgrid(x, y)

# 计算到原点的距离
R = np.sqrt(X**2 + Y**2)

# sinc 函数（处理 r=0 的奇点）
Z = np.where(R == 0, 1.0, np.sin(R) / R)
Z = Z**2  # 衍射强度 ∝ sinc²(r)，取值 [0, 1]

# 加入轻微噪声模拟实验数据
Z_noisy = Z + np.random.normal(0, 0.005, Z.shape)
Z_noisy = np.clip(Z_noisy, 0, None)  # 强度非负

# ── 3D 曲面绘制 ───────────────────────────────────────────────
result = sp.plot_surface(
    X, Y, Z_noisy,
    xlabel="X 坐标 (μm)",
    ylabel="Y 坐标 (μm)",
    zlabel="归一化强度",
    title="二维 sinc 函数曲面（圆孔衍射模型）",
    cmap="viridis",
    alpha=0.9,
    elev=35,        # 仰角
    azim=-45,       # 方位角
    venue="nature",
)

fig = result.fig
ax = result.ax

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/10_3d_surface", formats=("png",), dpi=300)
