"""
42_forest_funnel.py — Meta 分析标配：森林图 + 漏斗图
"""

import numpy as np
import sciplot as sp

rng = np.random.default_rng(42)

# ── 模拟数据：8 项研究的效应量与 95% CI ───────────────────────
studies = [f"研究 {i}" for i in range(1, 9)]
effect = rng.normal(0.72, 0.12, 8).clip(0.3, 1.2)
se = rng.uniform(0.08, 0.22, 8)
ci_low = effect - 1.96 * se
ci_high = effect + 1.96 * se
# 合并效应（逆方差加权）
w = 1.0 / se**2
pooled = float(np.sum(w * effect) / np.sum(w))
pooled_se = float(np.sqrt(1.0 / np.sum(w)))

# ── 森林图 ────────────────────────────────────────────────────
fig, ax = sp.plot_forest(
    effect, ci_low, ci_high,
    labels=studies,
    summary=(pooled, pooled - 1.96 * pooled_se, pooled + 1.96 * pooled_se),
    xlabel="效应量 (95% CI)",
    reference=0.5,
)
sp.save(fig, "showcase/42_forest", formats=("png",), dpi=300)

# ── 漏斗图（发表偏倚检测） ────────────────────────────────────
fig2, ax2 = sp.plot_funnel(
    effect, se,
    ci_low=ci_low, ci_high=ci_high,
    reference=pooled,
    xlabel="效应量",
    ylabel="标准误",
)
sp.save(fig2, "showcase/43_funnel", formats=("png",), dpi=300)
