"""
23_packed_bubble.py — 打包气泡图

展示 plot_packed_bubble()：全球半导体市场份额构成（2024，%）。
颜色=公司总部所在国/地区分组，面积=市场份额，展示产业格局。
"""

import numpy as np
import sciplot as sp

# ── 数据生成 ──────────────────────────────────────────────────
companies = [
    "台积电", "三星", "英特尔", "高通", "博通", "英伟达",
    "SK海力士", "AMD", "德州仪器", "联发科", "美光", "英飞凌",
]
shares = np.array([31.0, 12.3, 9.6, 5.8, 5.1, 4.7,
                   4.2, 3.6, 3.1, 2.8, 2.4, 2.1])
hq = [
    "中国台湾", "韩国", "美国", "美国", "美国", "美国",
    "韩国", "美国", "美国", "中国台湾", "美国", "欧洲",
]

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("presentation", "ocean", lang="zh")

fig, ax = sp.plot_packed_bubble(
    companies,
    shares,
    color_by=hq,
    show_values=True,
    fmt=".1f",
    min_size_frac=0.25,
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/23_packed_bubble", formats=("png",), dpi=300)
