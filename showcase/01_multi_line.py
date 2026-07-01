"""
01_multi_line.py — 多线对比图

展示 SciPlot 的 plot_multi() 功能：4 种算法在不同信噪比下的检测性能对比。
使用 pastel 配色，Nature 默认样式，中文标签。
"""

import numpy as np
import sciplot as sp

# 可复现随机种子
np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
# 模拟 4 种目标检测算法在不同信噪比 (SNR) 下的检测概率
snr_db = np.linspace(-10, 20, 50)  # 信噪比范围 -10 ~ 20 dB

# 算法 A：传统匹配滤波器 — 基线性能
base_a = 1 - np.exp(-0.15 * (snr_db + 10))
perf_a = base_a + np.random.normal(0, 0.015, len(snr_db))
perf_a = np.clip(perf_a, 0, 1)

# 算法 B：自适应波束成形 — 中等提升
base_b = 1 - np.exp(-0.20 * (snr_db + 10))
perf_b = base_b + np.random.normal(0, 0.012, len(snr_db))
perf_b = np.clip(perf_b, 0, 1)

# 算法 C：深度学习检测器 — 高性能
base_c = 1 - np.exp(-0.28 * (snr_db + 10))
perf_c = base_c + np.random.normal(0, 0.010, len(snr_db))
perf_c = np.clip(perf_c, 0, 1)

# 算法 D：本文方法 — 最优
base_d = 1 - np.exp(-0.35 * (snr_db + 10))
perf_d = base_d + np.random.normal(0, 0.008, len(snr_db))
perf_d = np.clip(perf_d, 0, 1)

# ── 绘图 ──────────────────────────────────────────────────────
fig, ax = sp.plot_multi(
    snr_db,
    [perf_a, perf_b, perf_c, perf_d],
    labels=["匹配滤波器", "自适应波束成形", "深度学习检测器", "本文方法"],
    xlabel="信噪比 (dB)",
    ylabel="检测概率",
    title="不同信噪比下各算法检测性能对比",
    palette="pastel",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/01_multi_line", formats=("png",), dpi=300)
