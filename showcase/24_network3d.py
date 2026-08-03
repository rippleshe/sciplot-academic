"""
24_network3d.py — 3D 网络图

展示 plot_network3d()：蛋白质互作网络的立体展示。
节点高度编码表达量，颜色编码功能模块。
"""

import numpy as np
import networkx as nx
import sciplot as sp

np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
n = 40
rng = np.random.default_rng(42)

# 随机无标度网络（幂律度分布更接近真实互作网络）
G = nx.barabasi_albert_graph(n, 2, seed=42)

# 节点属性：表达量 + 功能模块
expression = rng.lognormal(mean=1.0, sigma=0.7, size=n)
modules = [f"模块{chr(ord('A') + (i % 4))}" for i in range(n)]
nx.set_node_attributes(G, {i: float(expression[i]) for i in G.nodes}, "expression")
nx.set_node_attributes(G, {i: modules[i] for i in G.nodes}, "module")

# ── 绘图 ──────────────────────────────────────────────────────
sp.setup_style("thesis", "sunset", lang="zh")

fig, ax = sp.plot_network3d(
    G,
    z_by="expression",
    node_color_by="module",
    node_size_by="expression",
    labels=10,
    show_legend=True,
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/24_network3d", formats=("png",), dpi=300)
