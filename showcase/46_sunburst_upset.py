"""
46_sunburst_upset.py — 旭日图 + UpSet 图（集合交集）
"""

import numpy as np
import sciplot as sp

# ── Sunburst：分类学结构（门 → 纲 → 属） ─────────────────────
fig, ax = sp.plot_sunburst(
    labels=["", "变形菌门", "厚壁菌门", "放线菌门",
            "α-变形菌", "γ-变形菌", "芽孢杆菌", "梭菌",
            "α-1", "α-2", "γ-1", "γ-2", "γ-3"],
    parents=[None, "", "", "",
             "变形菌门", "变形菌门", "厚壁菌门", "厚壁菌门",
             "α-变形菌", "α-变形菌", "γ-变形菌", "γ-变形菌", "γ-变形菌"],
    values=[100, 45, 35, 20,
            25, 20, 22, 13,
            14, 11, 8, 7, 5],
)
sp.save(fig, "showcase/46_sunburst", formats=("png",), dpi=300)

# ── UpSet：三个组学数据集的基因交集 ───────────────────────────
rng = np.random.default_rng(46)
rna = {f"G{i}" for i in range(1, 30)}
prot = {f"G{i}" for i in range(12, 40)}
chip = {f"G{i}" for i in range(25, 55)}

fig2, ax2 = sp.plot_upset({
    "RNA-seq": rna,
    "蛋白质组": prot,
    "ChIP-seq": chip,
})
sp.save(fig2, "showcase/47_upset", formats=("png",), dpi=300)
