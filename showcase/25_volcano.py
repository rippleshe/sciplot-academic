"""
25_volcano.py — 火山图

展示 plot_volcano()：差异表达基因分析。
场景：处理组 vs 对照组的转录组差异表达（1200 个基因）。
"""

import numpy as np
import sciplot as sp

np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
rng = np.random.default_rng(42)
n = 1200
log2fc = rng.normal(0, 0.7, n)
p_values = 10 ** (-rng.uniform(0, 3.5, n))

# 掺入显著差异基因
n_sig = 60
log2fc[:n_sig] = rng.choice([-1, 1], n_sig) * rng.uniform(1.2, 3.0, n_sig)
p_values[:n_sig] = 10 ** (-rng.uniform(2.5, 8, n_sig))

genes = [f"GENE_{i:04d}" for i in range(n)]

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("nature", "pastel", lang="en")

fig, ax = sp.plot_volcano(
    log2fc,
    p_values,
    labels=genes,
    fc_threshold=1.0,
    p_threshold=0.05,
    xlabel="log2(Fold Change)",
    ylabel="-log10(p)",
    top_n=6,
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/25_volcano", formats=("png",), dpi=300)
