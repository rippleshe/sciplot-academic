"""
15_bubble.py — 二维气泡图

展示 plot_bubble()：气泡面积编码第三维（研发投入），颜色编码第四维（营收增速）。
场景：40 家科技公司的投入-产出分析。
"""

import numpy as np
import sciplot as sp

np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
n = 40
rnd = np.random.default_rng(42)

# 研发投入 (亿元)
rd_invest = rnd.uniform(0.5, 15, n)
# 营收 (亿元)：与投入正相关
revenue = 8 * rd_invest + rnd.normal(0, 12, n)
revenue = np.clip(revenue, 1, None)
# 营收增速 (%)：小公司更高
growth = 40 - 2.2 * rd_invest + rnd.normal(0, 12, n)
growth = np.clip(growth, -15, 80)
# 员工数 (百人)：与规模相关，作为气泡面积维度
headcount = 8 * revenue + rnd.uniform(0, 50, n)

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("ieee", "pastel", lang="zh")

fig, ax = sp.plot_bubble(
    rd_invest,
    revenue,
    size=headcount,          # 气泡面积 = 员工规模
    color=growth,            # 气泡颜色 = 增速
    xlabel="研发投入 (亿元)",
    ylabel="营收 (亿元)",
    colorbar_label="营收增速 (%)",
    size_scale=400,
    alpha=0.75,
    title="科技公司投入-产出气泡图",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/15_bubble", formats=("png",), dpi=300)
