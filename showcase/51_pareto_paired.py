"""
51_pareto_paired.py — 帕累托归因分析 + 配对个体轨迹对照

展示 SciPlot v1.15.0 新增的 `plot_pareto()` 与 `plot_paired()`，
配合 vivid-illustration 精选高分离配色（blue-sky / coral-teal）。
"""

import numpy as np
import sciplot as sp

rng = np.random.default_rng(42)

# ── 图 51：帕累托归因图（故障诱因权重排序 + 累积 80% 线） ────────
sp.setup_style("nature", "blue-sky", lang="zh")
causes = ["传感器漂移", "通信丢包", "电源波纹", "温度过载", "固件异常", "机械磨损", "其他"]
counts = [142, 86, 48, 22, 14, 9, 5]

fig1, _ = sp.plot_pareto(
    causes,
    counts,
    xlabel="故障原因类别",
    ylabel="累计频次 (次)",
    threshold=80.0,
    show_values=True,
)
sp.save(fig1, "showcase/51_pareto", formats=("png",), dpi=300)

# ── 图 52：配对个体变化图（干预前 vs 干预后个体响应与 p 值） ────
sp.setup_style("nature", "coral-teal", lang="zh")
n_subj = 28
before = rng.normal(62.0, 8.5, n_subj)
# 大多数显著提升，少量下降展现个体异质性
delta = rng.normal(9.5, 5.2, n_subj)
after = before + delta

fig2, _ = sp.plot_paired(
    before,
    after,
    labels=("治疗前 (Baseline)", "治疗后 (Week 12)"),
    ylabel="临床功能评分 (分)",
    show_box=True,
    show_mean=True,
    show_stats=True,
)
sp.save(fig2, "showcase/52_paired", formats=("png",), dpi=300)
