"""
多维图表 — 平行坐标图

用于展示多个样本在多个特征维度上的分布规律。
"""

from __future__ import annotations

from typing import Any, List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from sciplot._core.layout import new_figure
from sciplot._core.style import VENUES, get_current_venue
from sciplot._core.utils import apply_resolved_style
from sciplot._core.result import PlotResult


def _normalize_minmax(data: np.ndarray) -> np.ndarray:
    """Min-Max 归一化到 [0, 1]"""
    min_val = np.min(data)
    max_val = np.max(data)
    if max_val == min_val:
        return np.zeros_like(data)
    return (data - min_val) / (max_val - min_val)


def _normalize_zscore(data: np.ndarray) -> np.ndarray:
    """Z-Score 标准化"""
    mean_val = np.mean(data)
    std_val = np.std(data)
    if std_val == 0:
        return np.zeros_like(data)
    return (data - mean_val) / std_val


def plot_parallel(
    data: np.ndarray,
    columns: Optional[List[str]] = None,
    labels: Optional[List[str]] = None,
    color_by: Optional[Union[int, str]] = None,
    normalize: str = "minmax",
    show_colorbar: bool = True,
    alpha: float = 0.5,
    linewidth: float = 1.0,
    title: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制平行坐标图（多维特征比较）

    参数:
        data     : 二维数组 (n_samples, n_features) 或 DataFrame
        columns  : 特征名称列表；若 data 为 DataFrame 则自动获取
        labels   : 样本标签列表（用于图例）
        color_by : 按某列着色：
                   - int: 列索引
                   - str: 列名（需提供 columns）
                   - None: 不区分颜色
        normalize: 归一化方式
                   - "minmax": Min-Max 归一化到 [0, 1]（默认）
                   - "zscore": Z-Score 标准化
                   - "none": 不归一化
        show_colorbar: 连续着色时是否显示 colorbar，默认 True
        alpha    : 线条透明度，默认 0.5
        linewidth: 线条宽度，默认 1.0

    示例:
        >>> # 基本用法
        >>> data = np.random.randn(50, 5)  # 50个样本，5个特征
        >>> fig, ax = sp.plot_parallel(
        ...     data,
        ...     columns=["特征A", "特征B", "特征C", "特征D", "特征E"],
        ...     title="平行坐标图"
        ... )
        >>> 
        >>> # 按类别着色
        >>> fig, ax = sp.plot_parallel(
        ...     data,
        ...     columns=["A", "B", "C", "D"],
        ...     color_by=0,  # 按第一列着色
        ... )
    """
    if hasattr(data, "iloc"):
        if columns is None:
            columns = list(data.columns)
        if labels is None and hasattr(data, "index"):
            labels = [str(idx) for idx in data.index]
        data = data.values

    data = np.asarray(data)

    if data.ndim != 2:
        raise ValueError(f"data 必须是二维数组，当前维度: {data.ndim}")

    if not np.issubdtype(data.dtype, np.number):
        raise ValueError("data 必须是数值型二维数组")

    n_samples, n_features = data.shape

    if columns is None:
        columns = [f"特征 {i+1}" for i in range(n_features)]
    elif len(columns) != n_features:
        raise ValueError(
            f"columns 长度 ({len(columns)}) 与特征数 ({n_features}) 不一致"
        )

    if normalize == "minmax":
        data_norm = np.column_stack([
            _normalize_minmax(data[:, j]) for j in range(n_features)
        ])
    elif normalize == "zscore":
        data_norm = np.column_stack([
            _normalize_zscore(data[:, j]) for j in range(n_features)
        ])
    elif normalize == "none":
        data_norm = data
    else:
        raise ValueError(f"未知的归一化方式: {normalize}。可选: 'minmax', 'zscore', 'none'")

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

    x = np.arange(n_features)

    if color_by is not None:
        if isinstance(color_by, str):
            if columns is None:
                raise ValueError("color_by 为列名时必须提供 columns")
            try:
                color_idx = columns.index(color_by)
            except ValueError:
                raise ValueError(f"列名 '{color_by}' 不在 columns 中")
        else:
            color_idx = int(color_by)
            if not (-n_features <= color_idx < n_features):
                raise ValueError(
                    f"color_by 索引越界: {color_idx}，有效范围: [{-n_features}, {n_features - 1}]"
                )
            if color_idx < 0:
                color_idx += n_features

        color_values = np.asarray(data[:, color_idx])
        unique_values = np.unique(color_values)
        is_numeric_color = np.issubdtype(color_values.dtype, np.number)
        colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

        if (not is_numeric_color) or len(unique_values) <= 10:
            color_map = {v: colors[i % len(colors)] for i, v in enumerate(unique_values)}

            for i in range(n_samples):
                color = color_map.get(color_values[i], colors[0])
                ax.plot(x, data_norm[i, :], alpha=alpha, color=color, linewidth=linewidth, **kwargs)

            legend_handles = []
            for v in unique_values:
                legend_handles.append(
                    Line2D([0], [0], color=color_map[v], linewidth=linewidth, label=str(v))
                )
            ax.legend(handles=legend_handles, title=columns[color_idx])
        else:
            finite_values = color_values[np.isfinite(color_values)]
            if finite_values.size == 0:
                raise ValueError("color_by 列全为 NaN 或 Inf，无法进行连续映射")

            try:
                cmap = plt.colormaps.get_cmap("viridis")
            except AttributeError:
                cmap = plt.cm.get_cmap("viridis")
            norm = plt.Normalize(vmin=finite_values.min(), vmax=finite_values.max())

            for i in range(n_samples):
                val = color_values[i]
                color = cmap(norm(val)) if np.isfinite(val) else colors[0]
                ax.plot(x, data_norm[i, :], alpha=alpha, color=color, linewidth=linewidth, **kwargs)

            if show_colorbar:
                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])
                cbar = fig.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
                cbar.set_label(columns[color_idx])
    else:
        for i in range(n_samples):
            ax.plot(x, data_norm[i, :], alpha=alpha, linewidth=linewidth, **kwargs)

    ax.set_xticks(x)
    ax.set_xticklabels(columns, rotation=45, ha="right")
    ax.set_xlim(-0.5, n_features - 0.5)

    finite_values = data_norm[np.isfinite(data_norm)]
    if finite_values.size == 0:
        raise ValueError("data 中不包含可用于绘图的有限数值")

    if normalize == "minmax":
        ax.set_ylim(-0.05, 1.05)
        y_label = "归一化值"
    elif normalize == "zscore":
        y_min = float(finite_values.min())
        y_max = float(finite_values.max())
        y_margin = (y_max - y_min) * 0.05 if y_max > y_min else 0.5
        ax.set_ylim(y_min - y_margin, y_max + y_margin)
        y_label = "标准化值 (Z-score)"
    else:
        y_min = float(finite_values.min())
        y_max = float(finite_values.max())
        y_margin = (y_max - y_min) * 0.05 if y_max > y_min else 0.5
        ax.set_ylim(y_min - y_margin, y_max + y_margin)
        y_label = "原始值"

    ax.set_ylabel(y_label)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_scatter_matrix(
    data: np.ndarray,
    columns: Optional[List[str]] = None,
    color_by: Optional[np.ndarray] = None,
    diag: str = "hist",
    alpha: float = 0.5,
    s: float = 10,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
) -> PlotResult:
    """绘制散点矩阵，展示多特征两两关系。"""
    values = np.asarray(data, dtype=float)
    if values.ndim != 2:
        raise ValueError(f"data 必须是二维数组，当前维度: {values.ndim}")

    n_samples, n_features = values.shape
    if n_features < 2:
        raise ValueError(f"至少需要 2 个特征，当前: {n_features}")

    if columns is None:
        columns = [f"特征 {i + 1}" for i in range(n_features)]
    elif len(columns) != n_features:
        raise ValueError(
            f"columns 长度 ({len(columns)}) 与特征数 ({n_features}) 不一致"
        )

    if color_by is not None:
        color_values = np.asarray(color_by)
        if color_values.ndim != 1 or len(color_values) != n_samples:
            raise ValueError("color_by 必须是一维且长度与样本数一致")
    else:
        color_values = None

    diag = diag.lower()
    if diag not in {"hist", "kde", "none"}:
        raise ValueError("diag 仅支持 'hist'、'kde'、'none'")

    if diag == "kde":
        try:
            from scipy import stats as scipy_stats
        except ImportError as e:
            raise ImportError(
                "diag='kde' 需要安装 scipy。请运行: pip install scipy"
            ) from e
    else:
        scipy_stats = None

    effective_venue = apply_resolved_style(venue, palette, lang)
    active_venue = effective_venue or get_current_venue() or "nature"
    venue_cfg = VENUES.get(active_venue, VENUES["nature"])
    scale = max(1.0, n_features / 2.0)
    fig_w = max(4.0, min(14.0, venue_cfg.figsize[0] * scale))
    fig_h = max(4.0, min(14.0, venue_cfg.figsize[1] * scale))
    fig, axes = plt.subplots(
        n_features,
        n_features,
        squeeze=False,
        figsize=(fig_w, fig_h),
    )

    if color_values is not None:
        is_numeric = np.issubdtype(color_values.dtype, np.number)
        unique_vals = np.unique(color_values)
        if (not is_numeric) or len(unique_vals) <= 10:
            colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]
            color_map = {v: colors[i % len(colors)] for i, v in enumerate(unique_vals)}
            scatter_colors = [color_map[v] for v in color_values]
            cmap = None
        else:
            cmap = "viridis"
            scatter_colors = color_values.astype(float)
    else:
        scatter_colors = None
        cmap = None

    for row in range(n_features):
        for col in range(n_features):
            ax = axes[row, col]
            x_col = values[:, col]
            y_col = values[:, row]

            if row == col:
                if diag == "hist":
                    ax.hist(x_col, bins=20, alpha=0.75)
                elif diag == "kde":
                    finite = x_col[np.isfinite(x_col)]
                    if finite.size >= 2 and scipy_stats is not None:
                        kde = scipy_stats.gaussian_kde(finite)
                        x_eval = np.linspace(finite.min(), finite.max(), 200)
                        y_eval = kde(x_eval)
                        ax.plot(x_eval, y_eval)
                        ax.fill_between(x_eval, y_eval, alpha=0.2)
                # diag == "none" 时保持空白
            else:
                ax.scatter(
                    x_col,
                    y_col,
                    c=scatter_colors,
                    cmap=cmap,
                    s=s,
                    alpha=alpha,
                    edgecolors="none",
                )

            if row == n_features - 1:
                ax.set_xlabel(columns[col])
            else:
                ax.set_xticklabels([])

            if col == 0:
                ax.set_ylabel(columns[row])
            else:
                ax.set_yticklabels([])

            ax.tick_params(direction="in")

    fig.tight_layout()
    return PlotResult(fig, axes, metadata={"venue": effective_venue, "palette": palette})


__all__ = ["plot_parallel", "plot_scatter_matrix"]
