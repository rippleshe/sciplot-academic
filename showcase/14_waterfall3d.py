"""
14_waterfall3d.py — 3D 瀑布图

展示 plot_waterfall3d()：多组拉曼光谱沿第三轴堆叠，直观对比
不同合成条件下材料的特征峰位置与强度变化。
"""

import numpy as np
import sciplot as sp

# ── 数据生成 ──────────────────────────────────────────────────
# 模拟 4 个合成温度下的拉曼光谱（400–4000 cm⁻¹）
x = np.linspace(400, 4000, 500)

def raman_spectrum(centers, widths, heights, baseline=0.02):
    """叠加多个洛伦兹峰 + 基线噪声"""
    rng = np.random.default_rng(42)
    spec = np.full_like(x, baseline)
    for c, w, h in zip(centers, widths, heights):
        spec += h / (1 + ((x - c) / w) ** 2)
    return spec + 0.01 * rng.standard_normal(len(x))

# 不同温度下特征峰位置与强度变化
spectra = [
    raman_spectrum([800, 1350, 1600], [30, 25, 20], [0.9, 0.7, 0.5]),   # 低温：弱 D 峰
    raman_spectrum([800, 1350, 1600, 2700], [30, 25, 20, 35], [0.9, 1.1, 0.6, 0.4]),  # 中温
    raman_spectrum([800, 1350, 1580, 2700], [30, 25, 18, 35], [0.9, 1.5, 0.9, 0.6]),  # 高温
    raman_spectrum([800, 1350, 1580, 2930], [30, 25, 18, 40], [0.9, 1.8, 1.2, 0.8]),  # 更高温
]

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("thesis", "ocean", lang="zh")

fig, ax = sp.plot_waterfall3d(
    x,
    spectra,
    labels=["400 °C", "600 °C", "800 °C", "1000 °C"],
    xlabel="拉曼位移 (cm-1)",
    ylabel="合成温度",
    zlabel="强度 (a.u.)",
    fill=True,
    fill_alpha=0.25,
    spacing=1.0,
    title="不同合成温度下的拉曼光谱",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/14_waterfall3d", formats=("png",), dpi=300)
