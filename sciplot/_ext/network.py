"""
网络可视化扩展

用于绘制网络图、社区结构等。
需要额外安装：pip install sciplot-academic[network] 或 pip install networkx
"""

from __future__ import annotations

import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize

from sciplot._core.layout import new_figure
from sciplot._core.utils import apply_resolved_style, get_cycle_colors
from sciplot._core.result import PlotResult


def _check_networkx():
    """检查 networkx 是否可用"""
    try:
        import networkx as nx
        return nx
    except ImportError as e:
        raise ImportError(
            "网络图功能需要安装 networkx。\n"
            "推荐安装方式: uv pip install networkx\n"
            "或: pip install networkx\n"
            "或安装完整扩展: uv pip install sciplot-academic[network]"
        ) from e


def _coerce_numeric_attr(values) -> Optional[dict]:
    """尝试将属性字典的值全部转为数值；含非数值项时返回 None。"""
    coerced = {}
    for k, v in values.items():
        try:
            coerced[k] = float(v)
        except (TypeError, ValueError):
            return None
    return coerced


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
    labels: Union[bool, int] = True,
    node_size: float = 300,
    node_alpha: float = 0.8,
    edge_alpha: float = 0.5,
    edge_width: float = 1.0,
    with_arrows: bool = True,
    title: str = "",
    seed: Optional[int] = 42,
    layout_kwargs: Optional[Dict[str, Any]] = None,
    node_size_range: Tuple[float, float] = (100, 1000),
    edge_width_range: Tuple[float, float] = (0.5, 3.0),
    show_colorbar: bool = False,
    show_legend: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
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
        node_color_by: 按节点属性着色（"degree" 或任意属性）；
                       数值属性类别 >10 时连续着色，否则/非数值时分类着色
        node_size_by : 按节点属性调整大小（须为数值属性）
        edge_weight_by: 按边权重调整粗细（须为数值属性）
        labels       : 节点标签；True 全部显示，False 不显示，
                       整数 N 时只显示度最大的前 N 个节点（大图性能友好）
        node_size    : 基础节点大小，默认 300
        with_arrows  : 有向图是否显示箭头
        seed         : 布局随机种子，None 则每次随机；默认 42 保证可复现
        layout_kwargs: 透传给布局函数的额外参数（如 spring 的 k、iterations）
        node_size_range: 属性映射到节点大小的范围，默认 (100, 1000)
        edge_width_range: 属性映射到边宽的范围，默认 (0.5, 3.0)
        show_colorbar: 连续着色时是否显示颜色条，默认 False
        show_legend  : 分类着色时是否显示图例，默认 True
        lang         : 语言设置（如 "zh", "en"），用于中文字体支持

    示例:
        >>> import networkx as nx
        >>> G = nx.karate_club_graph()
        >>> fig, ax = sp.plot_network(G, layout="spring", node_color_by="degree")
        >>> sp.save(fig, "network")
    """
    nx = _check_networkx()
    layout_kw = dict(layout_kwargs or {})
    if seed is not None:
        layout_kw.setdefault("seed", seed)
    pos = _get_layout(G, layout, **layout_kw)

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

    colors = get_cycle_colors()

    # ── 节点着色 ──
    categorical_colors: Optional[Dict[Any, str]] = None
    continuous_mappable = None
    if node_color_by is not None:
        if node_color_by == "degree":
            color_values = dict(G.degree())
        else:
            color_values = nx.get_node_attributes(G, node_color_by)

        if color_values:
            numeric_attr = _coerce_numeric_attr(color_values)
            unique_values = sorted(set(color_values.values()), key=str)  # 确定性排序
            if numeric_attr is None or len(unique_values) <= 10:
                # 分类着色：非数值属性或类别数较少时按类别映射（顺序稳定）
                color_map = {v: colors[i % len(colors)] for i, v in enumerate(unique_values)}
                node_colors = [color_map.get(color_values.get(n, 0), colors[0]) for n in G.nodes()]
                categorical_colors = color_map
            else:
                norm = Normalize(min(numeric_attr.values()), max(numeric_attr.values()))
                try:
                    cmap = plt.colormaps.get_cmap("viridis")
                except AttributeError:
                    cmap = plt.cm.get_cmap("viridis")  # type: ignore[attr-defined]
                node_colors = [cmap(norm(numeric_attr.get(n, 0))) for n in G.nodes()]
                if show_colorbar:
                    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                    sm.set_array([])
                    continuous_mappable = sm
        else:
            node_colors = colors[0]
    else:
        node_colors = colors[0]

    # ── 节点大小 ──
    if node_size_by is not None:
        if node_size_by == "degree":
            size_values = dict(G.degree())
        else:
            size_values = nx.get_node_attributes(G, node_size_by)

        if size_values:
            numeric_size = _coerce_numeric_attr(size_values)
            if numeric_size is None:
                warnings.warn(
                    f"节点属性 '{node_size_by}' 包含非数值项，已回退为默认节点大小。",
                    UserWarning, stacklevel=2,
                )
                node_sizes = node_size
            else:
                min_size, max_size = min(numeric_size.values()), max(numeric_size.values())
                if max_size > min_size:
                    size_range = node_size_range
                    node_sizes = [
                        size_range[0] + (numeric_size.get(n, min_size) - min_size) /
                        (max_size - min_size) * (size_range[1] - size_range[0])
                        for n in G.nodes()
                    ]
                else:
                    node_sizes = [node_size] * G.number_of_nodes()
        else:
            node_sizes = node_size
    else:
        node_sizes = node_size

    # ── 边宽 ──
    if edge_weight_by is not None:
        weight_values = nx.get_edge_attributes(G, edge_weight_by)
        if weight_values:
            numeric_weight = _coerce_numeric_attr(weight_values)
            if numeric_weight is None:
                warnings.warn(
                    f"边属性 '{edge_weight_by}' 包含非数值项，已回退为默认边宽。",
                    UserWarning, stacklevel=2,
                )
                edge_widths = edge_width
            else:
                min_w, max_w = min(numeric_weight.values()), max(numeric_weight.values())
                if max_w > min_w:
                    width_range = edge_width_range
                    edge_widths = [
                        width_range[0] + (numeric_weight.get(e, min_w) - min_w) /
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

    # ── 节点标签：支持 top-N（按度降序）与大图性能 ──
    label_nodes: Optional[set] = None
    if isinstance(labels, int) and not isinstance(labels, bool):
        if labels > 0:
            top_nodes = sorted(G.nodes(), key=lambda n: G.degree(n), reverse=True)[:labels]
            label_nodes = set(top_nodes)
    elif labels is True:
        label_nodes = None  # 全部

    if label_nodes is not None or labels is True:
        # 获取字体设置，确保中文正常显示
        font_family = plt.rcParams.get("font.family", "serif")
        if isinstance(font_family, list):
            font_family = font_family[0]
        if font_family == "serif":
            serif_fonts = plt.rcParams.get("font.serif", [])
            if serif_fonts:
                font_family = serif_fonts[0]

        if label_nodes is not None:
            label_dict = {n: str(n) for n in label_nodes}
            nx.draw_networkx_labels(
                G, pos, labels=label_dict, ax=ax,
                font_size=plt.rcParams.get("font.size", 9) - 1,
                font_family=font_family,
            )
        else:
            nx.draw_networkx_labels(
                G, pos, ax=ax,
                font_size=plt.rcParams.get("font.size", 9) - 1,
                font_family=font_family,
            )

    # ── 连续着色的颜色条 ──
    if continuous_mappable is not None:
        cbar = fig.colorbar(continuous_mappable, ax=ax, fraction=0.046, pad=0.04)
        if node_color_by is not None:
            cbar.set_label(node_color_by)

    # ── 分类着色的图例 ──
    if categorical_colors is not None and show_legend:
        from matplotlib.patches import Patch

        handles = [
            Patch(facecolor=c, label=str(v), alpha=node_alpha)
            for v, c in categorical_colors.items()
        ]
        ax.legend(handles=handles, loc="best", frameon=False)

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
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    从邻接矩阵绘制网络图

    参数:
        adj_matrix: 邻接矩阵（二维数组）
        threshold  : 边权重阈值，低于此值的边不绘制
        labels     : 节点标签列表
        layout     : 布局算法
        lang       : 语言设置（如 "zh", "en"），用于中文字体支持

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

    return plot_network(G, layout=layout, venue=venue, palette=palette, lang=lang, **kwargs)


def plot_network_communities(
    G: Any,
    communities: List[List[Any]],
    layout: str = "spring",
    title: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制带社区结构的网络图

    参数:
        G          : networkx Graph 对象
        communities: 社区列表，每个社区是节点列表
        layout     : 布局算法
        lang       : 语言设置（如 "zh", "en"），用于中文字体支持

    示例:
        >>> import networkx as nx
        >>> from networkx.algorithms.community import greedy_modularity_communities
        >>> G = nx.karate_club_graph()
        >>> communities = list(greedy_modularity_communities(G))
        >>> fig, ax = sp.plot_network_communities(G, communities)
    """
    nx = _check_networkx()
    pos = _get_layout(G, layout, seed=42)

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

    colors = get_cycle_colors()

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

    # 获取字体设置，确保中文正常显示
    font_family = plt.rcParams.get("font.family", "serif")
    if isinstance(font_family, list):
        font_family = font_family[0]
    # 如果是 serif，尝试获取具体的 serif 字体列表中的第一个
    if font_family == "serif":
        serif_fonts = plt.rcParams.get("font.serif", [])
        if serif_fonts:
            font_family = serif_fonts[0]

    nx.draw_networkx_labels(
        G, pos, ax=ax,
        font_size=plt.rcParams.get("font.size", 9) - 1,
        font_family=font_family,
    )

    ax.set_axis_off()
    if title:
        ax.set_title(title)

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = ["plot_network", "plot_network_from_matrix", "plot_network_communities"]
