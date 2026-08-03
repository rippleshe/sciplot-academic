"""
26_calendar_heatmap.py — 日历热图

展示 plot_calendar_heatmap()：全年代码提交活跃度。
场景：Git 仓库 2024 年每日提交次数。
"""

import datetime

import numpy as np
import sciplot as sp

np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
rng = np.random.default_rng(42)
dates = [datetime.date(2024, 1, 1) + datetime.timedelta(days=i) for i in range(366)]

# 工作日提交多，周末少；夏天偏少、年底冲刺
commits = np.zeros(366)
for i, d in enumerate(dates):
    base = 3 if d.weekday() < 5 else 1
    seasonal = 1.0 if 6 <= d.month <= 8 else 1.6
    if d.month == 12:
        seasonal = 2.0
    commits[i] = rng.poisson(base * seasonal)

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("thesis", "ocean", lang="zh")

fig, ax = sp.plot_calendar_heatmap(
    dates,
    commits,
    cmap="YlOrRd",
    colorbar_label="提交次数",
    weekday_start=0,
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/26_calendar_heatmap", formats=("png",), dpi=300)
