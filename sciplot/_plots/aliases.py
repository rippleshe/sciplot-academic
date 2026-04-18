"""
简洁函数别名 — 更短的绘图函数名

提供常用绘图函数的简短别名，使代码更简洁。
所有别名都保持与原函数完全相同的参数和行为。
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from sciplot._plots.basic import (
    plot_line,
    plot,
    plot_multi,
    plot_multi_line,
    plot_scatter,
    plot_step,
    plot_area,
    plot_multi_area,
)
from sciplot._plots.distribution import (
    plot_bar,
    plot_grouped_bar,
    plot_stacked_bar,
    plot_horizontal_bar,
    plot_box,
    plot_violin,
    plot_histogram,
    plot_combo,
)
from sciplot._plots.advanced import (
    plot_errorbar,
    plot_confidence,
    plot_heatmap,
)

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.axes import Axes
    from typing import Dict, List, Optional, Sequence, Tuple
    import numpy as np


def line(
    x,
    y,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    label: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制折线图（plot_line 的别名）"""
    return plot_line(
        x,
        y,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        label=label,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def scatter(
    x,
    y,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    label: str = "",
    s: float = 20,
    alpha: float = 0.7,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制散点图（plot_scatter 的别名）"""
    return plot_scatter(
        x,
        y,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        label=label,
        s=s,
        alpha=alpha,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def step(
    x,
    y,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    label: str = "",
    where: str = "mid",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制阶梯图（plot_step 的别名）"""
    return plot_step(
        x,
        y,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        label=label,
        where=where,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def area(
    x,
    y,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    label: str = "",
    alpha: float = 0.3,
    fill: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制面积图（plot_area 的别名）"""
    return plot_area(
        x,
        y,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        label=label,
        alpha=alpha,
        fill=fill,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def multi(
    x,
    ys: Sequence,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    labels: Optional[Sequence[str]] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制多线折线图（plot_multi 的别名）"""
    return plot_multi(
        x,
        ys,
        labels=labels,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def multi_line(
    x,
    ys: Sequence,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    labels: Optional[Sequence[str]] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制多线折线图（plot_multi_line 的别名）"""
    return plot_multi_line(
        x,
        ys,
        labels=labels,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def multi_area(
    x,
    ys: Sequence,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    labels: Optional[Sequence[str]] = None,
    alpha: float = 0.3,
    stacked: bool = False,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制多系列面积图（plot_multi_area 的别名）"""
    return plot_multi_area(
        x,
        ys,
        labels=labels,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        stacked=stacked,
        alpha=alpha,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def bar(
    categories,
    values,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    width: float = 0.6,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制柱状图（plot_bar 的别名）"""
    return plot_bar(
        categories,
        values,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        width=width,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def grouped_bar(
    groups: List[str],
    data: Dict[str, Sequence],
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    width: float = 0.8,
    gap: float = 0.05,
    show_values: bool = False,
    value_fmt: str = ".1f",
    legend_loc: str = "best",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制分组柱状图（plot_grouped_bar 的别名）"""
    return plot_grouped_bar(
        groups,
        data,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        width=width,
        gap=gap,
        show_values=show_values,
        value_fmt=value_fmt,
        legend_loc=legend_loc,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def stacked_bar(
    categories: List[str],
    data: Dict[str, Sequence],
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    width: float = 0.6,
    show_values: bool = False,
    value_fmt: str = ".1f",
    legend_loc: str = "best",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制堆叠柱状图（plot_stacked_bar 的别名）"""
    return plot_stacked_bar(
        categories,
        data,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        width=width,
        show_values=show_values,
        value_fmt=value_fmt,
        legend_loc=legend_loc,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def hbar(
    categories: List[str],
    values,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    height: float = 0.6,
    show_values: bool = False,
    value_fmt: str = ".1f",
    sort: bool = False,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制水平柱状图（plot_horizontal_bar 的别名）"""
    return plot_horizontal_bar(
        categories,
        values,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        height=height,
        show_values=show_values,
        value_fmt=value_fmt,
        sort=sort,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def hist(
    x,
    bins: int = 30,
    xlabel: str = "",
    ylabel: str = "频率",
    title: str = "",
    density: bool = False,
    alpha: float = 0.75,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制直方图（plot_histogram 的别名）"""
    return plot_histogram(
        x,
        bins=bins,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        density=density,
        alpha=alpha,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def box(
    data,
    labels: Optional[Sequence[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    showfliers: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制箱线图（plot_box 的别名）"""
    return plot_box(
        data,
        labels=labels,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        showfliers=showfliers,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def violin(
    data,
    labels: Optional[Sequence[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    showmeans: bool = False,
    showmedians: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制小提琴图（plot_violin 的别名）"""
    return plot_violin(
        data,
        labels=labels,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        showmeans=showmeans,
        showmedians=showmedians,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def errorbar(
    x,
    y,
    yerr,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    label: str = "",
    fmt: str = "o",
    capsize: float = 4,
    markersize: float = 5,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制误差线图（plot_errorbar 的别名）"""
    return plot_errorbar(
        x,
        y,
        yerr,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        label=label,
        fmt=fmt,
        capsize=capsize,
        markersize=markersize,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def confidence(
    x,
    y_mean,
    y_std,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    label_mean: str = "Mean",
    label_std: str = "±1σ",
    n_std: float = 1.0,
    alpha: float = 0.25,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制置信区间图（plot_confidence 的别名）"""
    return plot_confidence(
        x,
        y_mean,
        y_std,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        label_mean=label_mean,
        label_std=label_std,
        n_std=n_std,
        alpha=alpha,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def heatmap(
    data,
    row_labels: Optional[List[str]] = None,
    col_labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    cmap: str = "Blues",
    show_values: bool = False,
    fmt: str = ".2f",
    colorbar_label: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制热力图（plot_heatmap 的别名）"""
    return plot_heatmap(
        data,
        row_labels=row_labels,
        col_labels=col_labels,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        cmap=cmap,
        show_values=show_values,
        fmt=fmt,
        colorbar_label=colorbar_label,
        venue=venue,
        palette=palette,
        **kwargs,
    )


def combo(
    x,
    bar_data: Dict[str, Sequence],
    line_data: Optional[Dict[str, Sequence]] = None,
    xlabel: str = "",
    ylabel_left: str = "",
    ylabel_right: str = "",
    title: str = "",
    bar_width: float = 0.35,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> Tuple[Figure, Axes, Any]:
    """绘制组合图（plot_combo 的别名）"""
    return plot_combo(
        x,
        bar_data,
        line_data=line_data,
        xlabel=xlabel,
        ylabel_left=ylabel_left,
        ylabel_right=ylabel_right,
        title=title,
        bar_width=bar_width,
        venue=venue,
        palette=palette,
        **kwargs,
    )


__all__ = [
    "line", "scatter", "step", "area",
    "multi", "multi_line", "multi_area",
    "bar", "grouped_bar", "stacked_bar", "hbar",
    "hist", "box", "violin",
    "errorbar", "confidence", "heatmap", "combo",
]
