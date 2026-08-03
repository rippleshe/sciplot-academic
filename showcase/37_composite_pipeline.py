"""
37_composite_pipeline.py — Nature 复合图模板：流水线（Pipeline）

布局原型：pipeline（方法学论文的流程叙事）。
5 个阶段横向排列：数据采集 → 预处理 → 特征工程 → 模型训练 → 评估，
阶段间用箭头连接（ConnectionPatch），面板标签 (a)-(e)。
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
import sciplot as sp

rng = np.random.default_rng(13)

# ── 布局：1×5 流水线（模板一键生成） ─────────────────────────
sp.setup_style("thesis", "ocean", lang="zh")
fig, axes = sp.figure_panels(template="pipeline", venue="thesis")
axes = np.atleast_1d(axes)
for ax in axes:
    ax.tick_params(direction="in")

# ── (a) 数据采集：原始信号分布（含噪声） ─────────────────────
raw = rng.normal(0.5, 0.28, 800)
axes[0].hist(raw, bins=30, color="#9DB8D2", edgecolor="white", linewidth=0.4)
axes[0].set_title("数据采集\n原始分布", fontsize=8)
axes[0].set_xticks([])
axes[0].tick_params(labelsize=6)

# ── (b) 预处理：去噪后分布更集中 ─────────────────────────────
clean = rng.normal(0.5, 0.12, 800)
axes[1].hist(clean, bins=30, color="#5B9BD5", edgecolor="white", linewidth=0.4)
axes[1].set_title("预处理\n去噪分布", fontsize=8)
axes[1].set_xticks([])
axes[1].tick_params(labelsize=6)

# ── (c) 特征工程：特征重要性排序 ─────────────────────────────
feats = [f"F{i}" for i in range(1, 7)]
imp = np.array([0.32, 0.21, 0.16, 0.12, 0.11, 0.08])
axes[2].barh(feats, imp, color="#4A7DB8", edgecolor="white", linewidth=0.4)
axes[2].set_title("特征工程\n重要性", fontsize=8)
axes[2].tick_params(axis="y", labelsize=6)

# ── (d) 模型训练：损失收敛 ───────────────────────────────────
epochs = np.arange(1, 61)
loss = 1.2 * np.exp(-epochs / 18) + 0.08 + rng.normal(0, 0.01, 60)
axes[3].plot(epochs, loss, color="#E07B54", linewidth=1.5)
axes[3].set_title("模型训练\n损失收敛", fontsize=8)
axes[3].tick_params(labelsize=6)

# ── (e) 评估：混淆矩阵（对角主导） ───────────────────────────
cm = 0.85 * np.eye(3) + rng.uniform(0.02, 0.06, (3, 3))
np.fill_diagonal(cm, np.diag(cm))
axes[4].imshow(cm, cmap="Blues", vmin=0, vmax=1)
axes[4].set_title("评估\n混淆矩阵", fontsize=8)
axes[4].set_xticks([])
axes[4].set_yticks([])

# ── 阶段间箭头 ───────────────────────────────────────────────
for i in range(4):
    cp = ConnectionPatch(
        xyA=(1.0, 0.5), coordsA=axes[i].transAxes,
        xyB=(0.0, 0.5), coordsB=axes[i + 1].transAxes,
        color="#666666", linewidth=1.2, arrowstyle="-|>",
        mutation_scale=12, zorder=5,
    )
    fig.add_artist(cp)

# ── 保存（面板标签已由模板自动添加 8pt） ──────────────────────
sp.save(fig, "showcase/37_composite_pipeline", formats=("png",), dpi=300)
