"""
59_tornado.py — 单因素敏感性龙卷风图（Tornado Diagram）

展示 SciPlot v1.16.0 新增的 `plot_tornado()`：
按参数波动幅度从上到下排序，围绕基准值直观刻画关键驱动因子的上下行弹性。
"""

import sciplot as sp

sp.setup_style("nature", "coral-teal", lang="zh")

params = [
    "电价补贴力度 (±25%)",
    "电解槽投资成本 (±20%)",
    "年有效利用小时数 (±15%)",
    "绿氢运输管网距离 (±30%)",
    "碳交易市场配额价格 (±25%)",
    "催化剂衰减率 (±40%)",
    "基准折现率 (±1.5%)",
    "运维人工与耗材 (±20%)",
]
# 相对于基准净现值 baseline = 42.0（百万元）的下行与上行结果
low_vals = [27.5, 51.8, 30.2, 46.5, 34.8, 44.1, 45.2, 43.4]
high_vals = [58.6, 33.4, 53.5, 36.2, 50.4, 39.3, 38.6, 40.5]

fig, _ = sp.plot_tornado(
    params,
    low_vals,
    high_vals,
    baseline=42.0,
    low_label="低估值情形",
    high_label="高估值情形",
    xlabel="项目净现值 NPV (百万元)",
    title="绿氢合成氨系统经济性单因素敏感性分析",
    sort_by_swing=True,
    show_values=True,
    fmt=".1f",
)
sp.save(fig, "showcase/59_tornado", formats=("png",), dpi=300)
