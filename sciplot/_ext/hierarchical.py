"""
层次聚类可视化扩展

用于绘制树状图、聚类热力图等。
需要额外安装：uv add scipy 或 pip install scipy
"""

from __future__ import annotations

from typing import Any, List, Optional, Union
import warnings

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from sciplot._core.layout import new_figure
from sciplot._core.style import VENUES
from sciplot._core.utils import apply_resolved_style
from sciplot._core.result import PlotResult


def _try_import_scipy():
    """尝试导入 scipy.cluster.hierarchy，失败时返回 None。"""
    try:
        from scipy.cluster import hierarchy
        return hierarchy
    except ImportError:
        return None


def _check_scipy():
    """
    检查 scipy 是否可用
    
    返回:
        hierarchy 模块对象
    
    抛出:
        ImportError: 未安装 scipy 时
    """
    hierarchy = _try_import_scipy()
    if hierarchy is not None:
        return hierarchy
    raise ImportError(
        "层次聚类功能需要安装 scipy。\n"
        "请运行: uv add scipy 或 pip install scipy"
    )


def plot_dendrogram(
    data_or_linkage: Union[np.ndarray, Any],
    labels: Optional[List[str]] = None,
    orientation: str = "top",
    color_threshold: Optional[float] = None,
    title: str = "",
    leaf_rotation: float = 90,
    leaf_font_size: Optional[float] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制树状图（层次聚类）

    参数:
        data_or_linkage: 数据矩阵 (n_samples, n_features) 或 linkage 矩阵
        labels        : 叶节点标签列表
        orientation   : 树的方向
                        - "top": 从上到下（默认）
                        - "bottom": 从下到上
                        - "left": 从左到右
                        - "right": 从右到左
        color_threshold: 颜色阈值，决定在哪个高度切割聚类
        leaf_rotation : 叶标签旋转角度
        leaf_font_size: 叶标签字体大小
        venue         : 期刊样式
        palette       : 配色方案

    返回:
        PlotResult: 包含 fig 和 ax 的绘图结果对象

    抛出:
        ImportError: 未安装 scipy 时
        ValueError: 数据格式错误时

    示例:
        >>> from scipy.cluster.hierarchy import linkage
        >>> data = np.random.randn(20, 5)
        >>> Z = linkage(data, method='ward')
        >>> result = sp.plot_dendrogram(Z, labels=[f"样本{i}" for i in range(20)])
        >>> result.save("dendrogram")
    """
    hierarchy = _check_scipy()

    if isinstance(data_or_linkage, np.ndarray):
        if data_or_linkage.ndim == 2 and data_or_linkage.shape[1] == 4:
            Z = data_or_linkage
        elif data_or_linkage.ndim == 2 and data_or_linkage.shape[1] > 4:
            Z = hierarchy.linkage(data_or_linkage, method='ward')
        else:
            raise ValueError(
                f"data_or_linkage 必须是 linkage 矩阵 (n-1, 4) 或数据矩阵 (n, m)。\n"
                f"实际收到: shape={data_or_linkage.shape}"
            )
    else:
        Z = np.asarray(data_or_linkage)
        if Z.ndim != 2 or Z.shape[1] != 4:
            raise ValueError(
                f"data_or_linkage 必须是 linkage 矩阵 (n-1, 4) 或数据矩阵 (n, m)。\n"
                f"实际收到: type={type(data_or_linkage).__name__}"
            )

    effective_venue = apply_resolved_style(venue, palette)
    fig, ax = new_figure(effective_venue)

    if leaf_font_size is None:
        leaf_font_size = plt.rcParams.get("font.size", 9) - 1

    hierarchy.dendrogram(
        Z,
        labels=labels,
        orientation=orientation,
        color_threshold=color_threshold,
        leaf_rotation=leaf_rotation,
        leaf_font_size=leaf_font_size,
        ax=ax,
        **kwargs,
    )

    if orientation in ("top", "bottom"):
        ax.set_xlabel("样本")
        ax.set_ylabel("距离")
    else:
        ax.set_xlabel("距离")
        ax.set_ylabel("样本")

    if title:
        ax.set_title(title)

    ax.tick_params(direction="in")

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_clustermap(
    data: np.ndarray,
    row_labels: Optional[List[str]] = None,
    col_labels: Optional[List[str]] = None,
    row_cluster: bool = True,
    col_cluster: bool = True,
    cmap: str = "viridis",
    title: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制聚类热力图（热力图 + 行/列树状图）

    参数:
        data       : 二维数据矩阵
        row_labels : 行标签
        col_labels : 列标签
        row_cluster: 是否对行聚类
        col_cluster: 是否对列聚类
        cmap       : 颜色映射
        title      : 图表标题
        venue      : 期刊样式
        palette    : 配色方案

    返回:
        PlotResult: 包含 fig 和 ax 的绘图结果对象
            - result.ax 为主热力图的坐标轴
            - 行/列树状图的坐标轴可通过 fig.axes 访问

    抛出:
        ImportError: 未安装 scipy 时

    示例:
        >>> data = np.random.randn(10, 8)
        >>> result = sp.plot_clustermap(data, row_cluster=True, col_cluster=True)
        >>> result.save("clustermap")
    """
    data = np.asarray(data, dtype=float)
    if data.ndim != 2:
        raise ValueError(f"data 必须是二维数组，当前维度: {data.ndim}")
    n_rows, n_cols = data.shape

    if n_rows == 0 or n_cols == 0:
        raise ValueError(f"data 不能为空矩阵，实际形状: {data.shape}")

    if row_labels is not None and len(row_labels) != n_rows:
        raise ValueError(
            f"row_labels 长度 ({len(row_labels)}) 与数据行数 ({n_rows}) 不一致"
        )

    if col_labels is not None and len(col_labels) != n_cols:
        raise ValueError(
            f"col_labels 长度 ({len(col_labels)}) 与数据列数 ({n_cols}) 不一致"
        )

    row_cluster = row_cluster and n_rows > 1
    col_cluster = col_cluster and n_cols > 1

    hierarchy = None
    if row_cluster or col_cluster:
        hierarchy = _try_import_scipy()
        if hierarchy is None:
            warnings.warn(
                "未检测到 scipy，plot_clustermap 已降级为普通热力图（跳过层次聚类）。",
                UserWarning,
                stacklevel=2,
            )
            row_cluster = False
            col_cluster = False

    effective_venue = apply_resolved_style(venue, palette)
    _, base_figsize, _ = VENUES.get(effective_venue or "nature", VENUES["nature"])
    heatmap_scale = max(base_figsize)
    fig = plt.figure(figsize=(heatmap_scale, heatmap_scale))

    if row_cluster:
        row_Z = hierarchy.linkage(data, method='ward')
        row_order = hierarchy.leaves_list(row_Z)
        data = data[row_order, :]
        if row_labels is not None:
            row_labels = [row_labels[i] for i in row_order]

    if col_cluster:
        col_Z = hierarchy.linkage(data.T, method='ward')
        col_order = hierarchy.leaves_list(col_Z)
        data = data[:, col_order]
        if col_labels is not None:
            col_labels = [col_labels[i] for i in col_order]

    dendro_width = 1.5
    dendro_height = 1.5
    heatmap_width = 6
    heatmap_height = 6

    ax_heatmap = fig.add_axes([
        dendro_width / 10,
        dendro_height / 10,
        heatmap_width / 10,
        heatmap_height / 10,
    ])

    im = ax_heatmap.imshow(data, cmap=cmap, aspect="auto", **kwargs)

    if col_labels is not None:
        ax_heatmap.set_xticks(np.arange(len(col_labels)))
        ax_heatmap.set_xticklabels(col_labels, rotation=45, ha="right")
    if row_labels is not None:
        ax_heatmap.set_yticks(np.arange(len(row_labels)))
        ax_heatmap.set_yticklabels(row_labels)

    ax_heatmap.tick_params(direction="in")

    fig.colorbar(im, ax=ax_heatmap, fraction=0.046, pad=0.04)

    if row_cluster:
        ax_row = fig.add_axes([
            0.05,
            dendro_height / 10,
            dendro_width / 10 - 0.1,
            heatmap_height / 10,
        ])
        hierarchy.dendrogram(row_Z, orientation="left", no_labels=True, ax=ax_row)
        ax_row.set_axis_off()

    if col_cluster:
        ax_col = fig.add_axes([
            dendro_width / 10,
            (dendro_height + heatmap_height) / 10 + 0.05,
            heatmap_width / 10,
            dendro_height / 10 - 0.1,
        ])
        hierarchy.dendrogram(col_Z, no_labels=True, ax=ax_col)
        ax_col.set_axis_off()

    if title:
        fig.suptitle(title, y=0.98)

    return PlotResult(fig, ax_heatmap, metadata={"venue": venue, "palette": palette})


__all__ = ["plot_dendrogram", "plot_clustermap"]

