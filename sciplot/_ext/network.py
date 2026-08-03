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
from matplotlib.patches import Patch

from sciplot._core.layout import add_colorbar
from sciplot._core.utils import apply_resolved_style, cycle_color, get_cmap_safe, get_cycle_colors, new_styled_figure
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


def _get_label_font_family() -> str:
    """获取当前 rcParams 中最具体的字体族（支持中文回退链）。"""
    font_family = plt.rcParams.get("font.family", "serif")
    if isinstance(font_family, list):
        font_family = font_family[0]
    if font_family == "serif":
        serif_fonts = plt.rcParams.get("font.serif", [])
        if serif_fonts:
            font_family = serif_fonts[0]
    return str(font_family)


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


def _resolve_node_colors(G, node_color_by, colors):
    """解析节点着色，返回 (node_colors, 分类色映射, 连续色映射信息)。

    分类色映射: Dict[value, color]（非 None 时按类别着色）
    连续色映射信息: (cmap, norm) 或 None
    """
    nx = _check_networkx()
    categorical_map: Optional[Dict[Any, str]] = None
    continuous_info = None

    if node_color_by is None:
        return colors[0], categorical_map, continuous_info

    if node_color_by == "degree":
        color_values = dict(G.degree())
    else:
        color_values = nx.get_node_attributes(G, node_color_by)

    if not color_values:
        return colors[0], categorical_map, continuous_info

    numeric_attr = _coerce_numeric_attr(color_values)
    unique_values = sorted(set(color_values.values()), key=str)  # 确定性排序
    if numeric_attr is None or len(unique_values) <= 10:
        categorical_map = {v: cycle_color(colors, i) for i, v in enumerate(unique_values)}
        node_colors = [categorical_map.get(color_values.get(n, 0), colors[0]) for n in G.nodes()]
        return node_colors, categorical_map, continuous_info

    norm = Normalize(min(numeric_attr.values()), max(numeric_attr.values()))
    cmap = get_cmap_safe("viridis")
    node_colors = [cmap(norm(numeric_attr.get(n, 0))) for n in G.nodes()]
    return node_colors, categorical_map, (cmap, norm)


def _resolve_node_sizes(G, node_size_by, node_size, size_range) -> Union[float, List[float]]:
    """解析节点尺寸映射；属性非数值时警告并回退默认。"""
    nx = _check_networkx()
    if node_size_by is None:
        return node_size

    if node_size_by == "degree":
        size_values = dict(G.degree())
    else:
        size_values = nx.get_node_attributes(G, node_size_by)

    if not size_values:
        return node_size

    numeric_size = _coerce_numeric_attr(size_values)
    if numeric_size is None:
        warnings.warn(
            f"节点属性 '{node_size_by}' 包含非数值项，已回退为默认节点大小。",
            UserWarning, stacklevel=2,
        )
        return node_size

    min_size, max_size = min(numeric_size.values()), max(numeric_size.values())
    if max_size <= min_size:
        return [node_size] * G.number_of_nodes()
    return [
        size_range[0] + (numeric_size.get(n, min_size) - min_size) /
        (max_size - min_size) * (size_range[1] - size_range[0])
        for n in G.nodes()
    ]


def _resolve_edge_widths(G, edge_weight_by, edge_width, width_range) -> Union[float, List[float]]:
    """解析边宽映射；属性非数值时警告并回退默认。"""
    nx = _check_networkx()
    if edge_weight_by is None:
        return edge_width

    weight_values = nx.get_edge_attributes(G, edge_weight_by)
    if not weight_values:
        return edge_width

    numeric_weight = _coerce_numeric_attr(weight_values)
    if numeric_weight is None:
        warnings.warn(
            f"边属性 '{edge_weight_by}' 包含非数值项，已回退为默认边宽。",
            UserWarning, stacklevel=2,
        )
        return edge_width

    min_w, max_w = min(numeric_weight.values()), max(numeric_weight.values())
    if max_w <= min_w:
        return [edge_width] * G.number_of_edges()
    return [
        width_range[0] + (numeric_weight.get(e, min_w) - min_w) /
        (max_w - min_w) * (width_range[1] - width_range[0])
        for e in G.edges()
    ]


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

    fig, ax = new_styled_figure(venue, palette, lang)

    colors = get_cycle_colors()

    # ── 节点着色 / 尺寸 / 边宽（共享辅助函数） ──
    node_colors, categorical_colors, continuous_info = _resolve_node_colors(
        G, node_color_by, colors
    )
    node_sizes = _resolve_node_sizes(G, node_size_by, node_size, node_size_range)
    edge_widths = _resolve_edge_widths(G, edge_weight_by, edge_width, edge_width_range)
    continuous_mappable = None
    if continuous_info is not None and show_colorbar:
        cmap, norm = continuous_info
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        continuous_mappable = sm

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
        font_family = _get_label_font_family()

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
        cbar = add_colorbar(fig, continuous_mappable, ax=ax)
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


def plot_network3d(
    G: Any,
    layout: str = "spring",
    node_color_by: Optional[str] = None,
    node_size_by: Optional[str] = None,
    z_by: Optional[str] = None,
    labels: Union[bool, int] = True,
    node_size: float = 200,
    node_alpha: float = 0.85,
    edge_alpha: float = 0.35,
    edge_width: float = 1.0,
    title: str = "",
    seed: Optional[int] = 42,
    layout_kwargs: Optional[Dict[str, Any]] = None,
    node_size_range: Tuple[float, float] = (60, 600),
    show_colorbar: bool = False,
    show_legend: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制 3D 网络图（节点立体分布，展示层级/属性纵向差异）

    基于 2D 布局将节点映射到 X/Y 平面，Z 轴由节点属性（z_by）或 0 决定，
    边以半透明线段连接。适合展示带层级属性的网络（如蛋白质互作 + 表达量、
    社交网络 + 活跃度）。

    参数:
        G            : networkx Graph 或 DiGraph 对象
        layout       : 布局算法（同 plot_network）
        node_color_by: 按节点属性着色（"degree" 或任意属性）
        node_size_by : 按节点属性调整大小
        z_by         : Z 轴坐标来源（节点属性名或 "degree"）；None 则平铺于 0
        labels       : 节点标签；True 全部 / False 不显示 / 整数 N 显示度最大的前 N 个
        node_size    : 基础节点大小，默认 200
        seed         : 布局随机种子，默认 42
        layout_kwargs: 透传给布局函数的额外参数
        node_size_range: 属性→尺寸映射范围，默认 (60, 600)
        show_colorbar: 连续着色时显示颜色条
        show_legend  : 分类着色时显示图例

    示例:
        >>> # 蛋白质互作网络：节点高度=表达量
        >>> fig, ax = sp.plot_network3d(
        ...     G, z_by="expression", node_color_by="module",
        ... )
        >>> sp.save(fig, "network3d")
    """
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  # 注册 3D projection
    from sciplot._ext.plot3d import _get_3d_figsize

    nx = _check_networkx()
    layout_kw = dict(layout_kwargs or {})
    if seed is not None:
        layout_kw.setdefault("seed", seed)
    pos = _get_layout(G, layout, **layout_kw)

    # Z 坐标：节点属性或 degree，非数值回退 0
    if z_by == "degree":
        z_values = dict(G.degree())
    elif z_by is not None:
        z_values = nx.get_node_attributes(G, z_by)
    else:
        z_values = {}

    if z_values:
        numeric_z = _coerce_numeric_attr(z_values)
        if numeric_z is None:
            warnings.warn(
                f"节点属性 '{z_by}' 包含非数值项，Z 坐标回退为 0。",
                UserWarning, stacklevel=2,
            )
            z_coords = {n: 0.0 for n in G.nodes()}
        else:
            z_coords = {n: float(numeric_z.get(n, 0.0)) for n in G.nodes()}
    else:
        z_coords = {n: 0.0 for n in G.nodes()}

    effective_venue = apply_resolved_style(venue, palette, lang)
    figsize = _get_3d_figsize(effective_venue)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")

    colors = get_cycle_colors()
    node_colors, categorical_colors, continuous_info = _resolve_node_colors(
        G, node_color_by, colors
    )
    node_sizes = _resolve_node_sizes(G, node_size_by, node_size, node_size_range)

    # 边：逐条细而淡的线段（消除塑料感：低 alpha、浅色、细线）
    xyz = {n: (pos[n][0], pos[n][1], z_coords[n]) for n in G.nodes()}
    for u, v in G.edges():
        ax.plot(
            [xyz[u][0], xyz[v][0]],
            [xyz[u][1], xyz[v][1]],
            [xyz[u][2], xyz[v][2]],
            color="#B8B8B8", alpha=min(edge_alpha, 0.3),
            linewidth=min(edge_width, 0.9), zorder=1,
        )

    xs = [xyz[n][0] for n in G.nodes()]
    ys = [xyz[n][1] for n in G.nodes()]
    zs = [xyz[n][2] for n in G.nodes()]

    # 节点：开启 depthshade（真实深度感），半透明 + 浅色描边
    from matplotlib.colors import to_rgba, to_rgb

    if isinstance(node_colors, str):
        node_colors_list = [node_colors] * G.number_of_nodes()
    else:
        node_colors_list = list(node_colors)
    edge_colors = []
    for c in node_colors_list:
        try:
            r, g, b = to_rgb(c)
        except (ValueError, TypeError):
            r, g, b = to_rgb(to_rgba(c)[:3])
        # 与白色混合 55%：柔和描边
        edge_colors.append((0.55 + 0.45 * r, 0.55 + 0.45 * g, 0.55 + 0.45 * b, 0.9))

    scatter_kwargs: Dict[str, Any] = dict(
        s=node_sizes, c=node_colors, alpha=node_alpha, depthshade=True,
        edgecolors=edge_colors, linewidths=0.5,
    )
    scatter_kwargs.update(kwargs)
    ax.scatter(xs, ys, zs, **scatter_kwargs)

    # 标签（top-N 或全部）
    label_nodes: Optional[set] = None
    if isinstance(labels, int) and not isinstance(labels, bool):
        if labels > 0:
            top = sorted(G.nodes(), key=lambda n: G.degree(n), reverse=True)[:labels]
            label_nodes = set(top)
    elif labels is True:
        label_nodes = None

    if label_nodes is not None or labels is True:
        font_family = _get_label_font_family()
        fontsize = plt.rcParams.get("font.size", 9) - 1
        for n in G.nodes():
            if label_nodes is not None and n not in label_nodes:
                continue
            ax.text(
                xyz[n][0], xyz[n][1], xyz[n][2], str(n),
                fontsize=fontsize, fontfamily=font_family,
                ha="center", va="center", zorder=5,
                bbox=dict(
                    boxstyle="round,pad=0.12", facecolor="white",
                    edgecolor="none", alpha=0.6,
                ),
            )

    # 连续着色 colorbar / 分类图例
    if continuous_info is not None and show_colorbar:
        cmap, norm = continuous_info
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = add_colorbar(fig, sm, ax=ax, shrink=0.5, aspect=10)
        if node_color_by is not None:
            cbar.set_label(node_color_by)

    if categorical_colors is not None and show_legend:
        from matplotlib.patches import Patch

        handles = [
            Patch(facecolor=c, label=str(v), alpha=node_alpha)
            for v, c in categorical_colors.items()
        ]
        ax.legend(handles=handles, loc="upper right", frameon=False)

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
    communities: Optional[List[List[Any]]] = None,
    layout: str = "spring",
    labels: Union[bool, int] = True,
    node_size: float = 300,
    title: str = "",
    seed: Optional[int] = 42,
    layout_kwargs: Optional[Dict[str, Any]] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制带社区结构的网络图

    参数:
        G          : networkx Graph 对象
        communities: 社区列表，每个社区是节点列表；
                     None 时自动用 greedy_modularity_communities 检测
        layout     : 布局算法
        labels     : 节点标签；True 全部 / False 不显示 / 整数 N 显示度最大的前 N 个
        node_size  : 节点大小，默认 300
        seed       : 布局随机种子，默认 42
        layout_kwargs: 透传给布局函数的额外参数
        lang       : 语言设置（如 "zh", "en"），用于中文字体支持

    示例:
        >>> import networkx as nx
        >>> G = nx.karate_club_graph()
        >>> # 自动检测社区
        >>> fig, ax = sp.plot_network_communities(G)
        >>> # 手动指定社区
        >>> communities = [list(c) for c in nx.community.greedy_modularity_communities(G)]
        >>> fig, ax = sp.plot_network_communities(G, communities)
    """
    nx = _check_networkx()
    layout_kw = dict(layout_kwargs or {})
    if seed is not None:
        layout_kw.setdefault("seed", seed)
    pos = _get_layout(G, layout, **layout_kw)

    if communities is None:
        try:
            from networkx.algorithms.community import greedy_modularity_communities
        except ImportError:
            greedy_modularity_communities = None  # type: ignore[assignment]
        if greedy_modularity_communities is None:
            raise ImportError(
                "自动社区检测需要 networkx.algorithms.community，请升级 networkx"
            )
        detected = list(greedy_modularity_communities(G))
        if not detected:
            detected = [list(G.nodes())]
        communities = [list(c) for c in detected]

    fig, ax = new_styled_figure(venue, palette, lang)

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

    node_sizes = node_size if isinstance(node_size, (int, float)) else 300
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors,
        node_size=node_sizes,
        alpha=0.8,
    )

    # 标签（top-N 或全部）
    label_nodes: Optional[set] = None
    if isinstance(labels, int) and not isinstance(labels, bool):
        if labels > 0:
            top = sorted(G.nodes(), key=lambda n: G.degree(n), reverse=True)[:labels]
            label_nodes = set(top)
    elif labels is True:
        label_nodes = None

    if label_nodes is not None or labels is True:
        font_family = _get_label_font_family()

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

    # 社区图例
    legend_handles = []
    for i, community in enumerate(communities):
        legend_handles.append(
            Patch(facecolor=cycle_color(colors, i), label=f"社区 {i + 1}", alpha=0.8)
        )
    ax.legend(handles=legend_handles, loc="best", frameon=False)

    ax.set_axis_off()
    if title:
        ax.set_title(title)

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = ["plot_network", "plot_network3d", "plot_network_from_matrix", "plot_network_communities"]
