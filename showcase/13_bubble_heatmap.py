"""
13_bubble_heatmap.py — 气泡热力图

展示 plot_bubble_heatmap()：用"气泡大小 + 格子底色"双重通道编码矩阵数值。
场景：8 种药物 × 10 个细胞系 的半数抑制浓度（IC50, log10 μM），
气泡越大抑制越强，颜色从蓝（弱）到红（强）。
"""

import numpy as np
import sciplot as sp

np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
# 8 种候选药物对 10 个细胞系的 IC50（log10 μM，越小药效越强 → 用负值）
drugs = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"]
cell_lines = [f"CL-{i}" for i in range(1, 11)]

# 每种药物有基础效力，细胞系有敏感性差异
base_potency = np.linspace(-3.0, 1.0, len(drugs))  # 药物间差异
line_sensitivity = np.random.normal(0, 0.6, len(cell_lines))  # 细胞系差异
noise = np.random.normal(0, 0.25, (len(drugs), len(cell_lines)))
ic50 = base_potency[:, None] + line_sensitivity[None, :] + noise
ic50 = np.clip(ic50, -4.5, 2.5)

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("nature", "ocean", lang="zh")

fig, ax = sp.plot_bubble_heatmap(
    ic50,
    row_labels=drugs,
    col_labels=cell_lines,
    cmap="RdBu_r",
    vmin=-4, vmax=2,
    show_values=True,
    fmt=".1f",
    bubble_scale=0.85,
    colorbar_label="log10(IC50)",
    xlabel="细胞系",
    ylabel="药物",
    title="药物-细胞系敏感性矩阵",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/13_bubble_heatmap", formats=("png",), dpi=300)
