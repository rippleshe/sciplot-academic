"""
41_waterfall.py — 瀑布图

展示 plot_waterfall()：某公司年度利润增量分解（百万元）。
期初利润 80 → 各业务贡献/成本消耗 → 期末总计，
绿色=增量、红色=减量、深灰=总计，虚线连接累计轨迹。
"""

import sciplot as sp

# ── 数据 ──────────────────────────────────────────────────────
items = ["主营业务", "新品线", "海外市场", "原材料成本", "研发投入", "渠道费用"]
deltas = [35.0, 18.0, 12.0, -15.0, -10.0, -6.0]

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("presentation", "pastel", lang="zh")

fig, ax = sp.plot_waterfall(
    items,
    deltas,
    start_value=80.0,
    show_values=True,
    fmt=".0f",
    xlabel="利润构成项",
    ylabel="金额（百万元）",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/41_waterfall", formats=("png",), dpi=300)
