"""
网络可视化扩展

用于绘制网络图、社区结构等。
需要额外安装：pip install sciplot-academic[network] 或 pip install networkx
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from sciplot._core.layout import new_figure
from sciplot._core.utils import apply_resolved_style
from sciplot._core.result import PlotResult


def _check_networkx():
    """检查 networkx 是否可用"""
    try:
        import networkx as nx
        return nx
    except ImportError:
        raise ImportError(
            "网络图功能需要安装 networkx。\n"
            "请运行: pip install networkx 或 pip install sciplot-academic[network]"
        )


def _get_layout(G, layout: str, **kwargs):
    """获取网络布局"""
    nx = _check_networkx()

    layout_funcs = {
        "spring": nx.spring_layout,
        "circular": nx.circular_layout,
        "spectral": nx.spectral_layout,
        "shell": nx.shell_layout,
        "kamada_kawai": nx.kamada_kawai_layout,
        "random": nx.random_layout,
    }

    if layout not in layout_funcs:
        raise ValueError(
            f"未知布局: '{layout}'。可用布局: {list(layout_funcs.keys())}"
        )

    layout_func = layout_funcs[layout]
    try:
        return layout_func(G, **kwargs)
    except TypeError:
        # 部分布局函数（如 circular/shell）在某些 networkx 版本不接受 seed。
        if "seed" in kwargs:
            fallback_kwargs = dict(kwargs)
            fallback_kwargs.pop("seed", None)
            return layout_func(G, **fallback_kwargs)
        raise


def plot_network(
    G: Any,
    layout: str = "spring",
    node_color_by: Optional[str] = None,
    node_size_by: Optional[str] = None,
    edge_weight_by: Optional[str] = None,
    labels: bool = True,
    node_size: float = 300,
    node_alpha: float = 0.8,
    edge_alpha: float = 0.5,
    edge_width: float = 1.0,
    with_arrows: bool = True,
    title: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制网络图

    参数:
        G            : networkx Graph 或 DiGraph 对象
        layout       : 布局算法
                       - "spring": 力导向布局（默认）
                       - "circular": 环形布局
                       - "spectral": 谱布局
                       - "shell": 同心圆布局
                       - "kamada_kawai": Kamada-Kawai 布局
                       - "random": 随机布局
        node_color_by: 按节点属性着色（如 "degree"）
        node_size_by : 按节点属性调整大小
        edge_weight_by: 按边权重调整粗细
        labels       : 是否显示节点标签
        node_size    : 基础节点大小，默认 300
        with_arrows  : 有向图是否显示箭头

    示例:
        >>> import networkx as nx
        >>> G = nx.karate_club_graph()
        >>> fig, ax = sp.plot_network(G, layout="spring", node_color_by="degree")
        >>> sp.save(fig, "network")
    """
    nx = _check_networkx()

    effective_venue = apply_resolved_style(venue, palette)
    fig, ax = new_figure(effective_venue)

    pos = _get_layout(G, layout, seed=42)

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

    if node_color_by is not None:
        if node_color_by == "degree":
            color_values = dict(G.degree())
        else:
            color_values = nx.get_node_attributes(G, node_color_by)

        if color_values:
            unique_values = set(color_values.values())
            if len(unique_values) <= 10:
                color_map = {v: colors[i % len(colors)] for i, v in enumerate(unique_values)}
                node_colors = [color_map.get(color_values.get(n, 0), colors[0]) for n in G.nodes()]
            else:
                norm = plt.Normalize(min(color_values.values()), max(color_values.values()))
                try:
                    cmap = plt.colormaps.get_cmap("viridis")
                except AttributeError:
                    # 低版本matplotlib兼容
                    cmap = plt.cm.get_cmap("viridis")
                node_colors = [cmap(norm(color_values.get(n, 0))) for n in G.nodes()]
        else:
            node_colors = colors[0]
    else:
        node_colors = colors[0]

    if node_size_by is not None:
        if node_size_by == "degree":
            size_values = dict(G.degree())
        else:
            size_values = nx.get_node_attributes(G, node_size_by)

        if size_values:
            min_size, max_size = min(size_values.values()), max(size_values.values())
            if max_size > min_size:
                size_range = 100, 1000
                node_sizes = [
                    size_range[0] + (size_values.get(n, min_size) - min_size) /
                    (max_size - min_size) * (size_range[1] - size_range[0])
                    for n in G.nodes()
                ]
            else:
                node_sizes = [node_size] * G.number_of_nodes()
        else:
            node_sizes = node_size
    else:
        node_sizes = node_size

    if edge_weight_by is not None:
        weight_values = nx.get_edge_attributes(G, edge_weight_by)
        if weight_values:
            min_w, max_w = min(weight_values.values()), max(weight_values.values())
            if max_w > min_w:
                width_range = 0.5, 3.0
                edge_widths = [
                    width_range[0] + (weight_values.get(e, min_w) - min_w) /
                    (max_w - min_w) * (width_range[1] - width_range[0])
                    for e in G.edges()
                ]
            else:
                edge_widths = [edge_width] * G.number_of_edges()
        else:
            edge_widths = edge_width
    else:
        edge_widths = edge_width

    is_directed = G.is_directed()

    nx.draw_networkx_edges(
        G, pos, ax=ax,
        alpha=edge_alpha,
        width=edge_widths,
        arrows=is_directed and with_arrows,
        edge_color="#888888",
    )

    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors,
        node_size=node_sizes,
        alpha=node_alpha,
    )

    if labels:
        nx.draw_networkx_labels(
            G, pos, ax=ax,
            font_size=plt.rcParams.get("font.size", 9) - 1,
        )

    ax.set_axis_off()
    if title:
        ax.set_title(title)

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_network_from_matrix(
    adj_matrix: np.ndarray,
    threshold: float = 0.0,
    labels: Optional[List[str]] = None,
    layout: str = "spring",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    从邻接矩阵绘制网络图

    参数:
        adj_matrix: 邻接矩阵（二维数组）
        threshold  : 边权重阈值，低于此值的边不绘制
        labels     : 节点标签列表
        layout     : 布局算法

    示例:
        >>> adj = np.random.rand(10, 10)
        >>> adj = (adj + adj.T) / 2  # 对称化
        >>> fig, ax = sp.plot_network_from_matrix(adj, threshold=0.5)
    """
    adj_matrix = np.asarray(adj_matrix)
    if adj_matrix.ndim != 2:
        raise ValueError(f"adj_matrix 必须是二维数组，当前维度: {adj_matrix.ndim}")
    if adj_matrix.shape[0] != adj_matrix.shape[1]:
        raise ValueError(
            f"adj_matrix 必须是方阵，当前形状: {adj_matrix.shape}"
        )

    nx = _check_networkx()

    n = adj_matrix.shape[0]
    G = nx.Graph()

    G.add_nodes_from(range(n))

    for i in range(n):
        for j in range(i + 1, n):
            weight = adj_matrix[i, j]
            if weight > threshold:
                G.add_edge(i, j, weight=weight)

    if labels is not None:
        if len(labels) != n:
            raise ValueError(f"labels 长度 ({len(labels)}) 与矩阵维度 ({n}) 不一致")
        mapping = {i: labels[i] for i in range(n)}
        G = nx.relabel_nodes(G, mapping)

    return plot_network(G, layout=layout, venue=venue, palette=palette, **kwargs)


def plot_network_communities(
    G: Any,
    communities: List[List[Any]],
    layout: str = "spring",
    title: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制带社区结构的网络图

    参数:
        G          : networkx Graph 对象
        communities: 社区列表，每个社区是节点列表
        layout     : 布局算法

    示例:
        >>> import networkx as nx
        >>> from networkx.algorithms.community import greedy_modularity_communities
        >>> G = nx.karate_club_graph()
        >>> communities = list(greedy_modularity_communities(G))
        >>> fig, ax = sp.plot_network_communities(G, communities)
    """
    nx = _check_networkx()

    effective_venue = apply_resolved_style(venue, palette)
    fig, ax = new_figure(effective_venue)

    pos = _get_layout(G, layout, seed=42)

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

    node_to_community = {}
    for i, community in enumerate(communities):
        for node in community:
            node_to_community[node] = i

    node_colors = [colors[node_to_community.get(n, 0) % len(colors)] for n in G.nodes()]

    nx.draw_networkx_edges(
        G, pos, ax=ax,
        alpha=0.3,
        edge_color="#CCCCCC",
    )

    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors,
        node_size=300,
        alpha=0.8,
    )

    nx.draw_networkx_labels(
        G, pos, ax=ax,
        font_size=plt.rcParams.get("font.size", 9) - 1,
    )

    ax.set_axis_off()
    if title:
        ax.set_title(title)

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = ["plot_network", "plot_network_from_matrix", "plot_network_communities"]
