"""
44_bump_alluvial.py — 排名变化图 + 冲积图
"""

import numpy as np
import sciplot as sp

rng = np.random.default_rng(44)

# ── Bump Chart：四个模型在 6 个 benchmark 上的排名演化 ────────
models = ["模型 A", "模型 B", "模型 C", "模型 D"]
benchmarks = ["B1", "B2", "B3", "B4", "B5", "B6"]
# 构造分数矩阵（各 benchmark 内排名会交错变化）
scores = np.zeros((4, 6))
for j in range(6):
    base = np.array([80, 82, 84, 86]) + rng.normal(0, 2.0, 4)
    scores[:, j] = base

fig, ax = sp.plot_bump(
    labels=models,
    values=scores,
    time_points=benchmarks,
    highlight="模型 C",
    xlabel="Benchmark",
    ylabel="排名",
)
sp.save(fig, "showcase/44_bump", formats=("png",), dpi=300)

# ── Alluvial：队列迁移（基线分组 → 干预 → 结局） ──────────────
fig2, ax2 = sp.plot_alluvial(
    stages=[["对照组", "治疗组"], ["完成", "脱落", "继续"], ["改善", "无变化"]],
    flows=[
        [(0, 0, 60), (0, 1, 12), (0, 2, 28), (1, 0, 55), (1, 2, 45)],
        [(0, 0, 78), (1, 1, 12), (2, 1, 15), (2, 0, 58)],
    ],
    title="",
)
sp.save(fig2, "showcase/45_alluvial", formats=("png",), dpi=300)
