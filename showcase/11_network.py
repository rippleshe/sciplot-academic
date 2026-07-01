"""
11_network.py — 社区结构网络图

展示 SciPlot 的 plot_network_communities() 功能：构建一个含 3 个社区
（每社区 8–10 个节点）的社交网络，使用力导向布局可视化社区结构。
使用 pastel 配色，Nature 默认样式，中文标签。
"""

import numpy as np
import networkx as nx
import sciplot as sp

# 可复现随机种子
np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
# 构建含 3 个社区的网络
# 社区内连接概率高，社区间连接概率低 → 自然形成社区结构
community_sizes = [10, 9, 8]  # 三个社区的节点数
p_intra = 0.7   # 社区内连接概率
p_inter = 0.08  # 社区间连接概率

n_total = sum(community_sizes)
G = nx.Graph()

# 添加节点并标注社区
node_id = 0
communities = []
for c_idx, size in enumerate(community_sizes):
    community_nodes = list(range(node_id, node_id + size))
    communities.append(community_nodes)
    for n in community_nodes:
        G.add_node(n, community=c_idx)
    node_id += size

# 社区内边
for community_nodes in communities:
    for i in community_nodes:
        for j in community_nodes:
            if i < j and np.random.random() < p_intra:
                G.add_edge(i, j)

# 社区间边
for c1 in range(len(communities)):
    for c2 in range(c1 + 1, len(communities)):
        for i in communities[c1]:
            for j in communities[c2]:
                if np.random.random() < p_inter:
                    G.add_edge(i, j)

# 设置节点标签（中文）
community_labels = ["信号处理", "图像识别", "自然语言"]
label_map = {}
for c_idx, community_nodes in enumerate(communities):
    for local_idx, n in enumerate(community_nodes):
        label_map[n] = f"{community_labels[c_idx][:2]}{local_idx + 1}"
nx.relabel_nodes(G, label_map, copy=False)

# 重建社区列表（使用新标签）
communities_relabeled = []
offset = 0
for c_idx, size in enumerate(community_sizes):
    comm = [f"{community_labels[c_idx][:2]}{i + 1}" for i in range(size)]
    communities_relabeled.append(comm)
    offset += size

# ── 网络可视化 ────────────────────────────────────────────────
fig, ax = sp.plot_network_communities(
    G,
    communities_relabeled,
    layout="spring",
    title="科研合作网络社区结构",
    venue="nature",
    palette="pastel",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/11_network", formats=("png",), dpi=300)
