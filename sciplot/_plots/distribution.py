"""
分布图表 — 柱状图、分组柱状图、箱线图、小提琴图、直方图、显著性标注
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from sciplot._core.style import setup_style
from sciplot._core.palette import DEFAULT_PALETTE
from sciplot._core.layout import new_figure


# ============================================================================
# 柱状图（单组）
# ============================================================================

def plot_bar(
    categories: List[str],
    values: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    width: float = 0.6,
    venue: str = "nature",
    palette: str = DEFAULT_PALETTE,
    **kwargs: Any,
) -> Tuple[Figure, Axes]:
    """
    绘制单组柱状图（每个柱子自动赋不同颜色）

    示例:
        >>> fig, ax = sp.plot_bar(
        ...     ["方法A", "方法B", "方法C"],
        ...     np.array([82.3, 85.1, 88.7]),
        ...     xlabel="方法", ylabel="准确率 (%)",
        ...     palette="pastel-3"
        ... )
        >>> sp.save(fig, "accuracy_bar")
    """
    setup_style(venue, palette)
    fig, ax = new_figure(venue)
    colors = _get_cycle_colors()
    bar_colors = [colors[i % len(colors)] for i in range(len(categories))]
    ax.bar(categories, values, width=width, color=bar_colors, **kwargs)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return fig, ax


# ============================================================================
# 分组柱状图（多组对比）
# ============================================================================

def plot_grouped_bar(
    groups: List[str],
    data: Dict[str, Union[List[float], np.ndarray]],
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    width: float = 0.8,
    gap: float = 0.05,
    show_values: bool = False,
    value_fmt: str = ".1f",
    legend_loc: str = "best",
    venue: str = "nature",
    palette: str = DEFAULT_PALETTE,
    **kwargs: Any,
) -> Tuple[Figure, Axes]:
    """
    绘制分组柱状图（多方法/多指标对比，论文最常见）

    参数:
        groups    : 横轴分组标签（如 ["数据集A", "数据集B", "数据集C"]）
        data      : {方法名: 对应各组的数值} 有序字典
                    如 {"BERT": [87, 89, 91], "GPT": [85, 90, 93]}
        width     : 每组所有柱的总宽（占一个间隔的比例），默认 0.8
        gap       : 组间额外间隙，默认 0.05
        show_values: True 则在柱顶显示数值
        value_fmt  : 数值格式字符串，默认 ".1f"
        legend_loc : 图例位置

    示例:
        >>> methods = {"ResNet": [82.3, 84.1, 86.5],
        ...            "ViT":    [85.7, 87.2, 89.0],
        ...            "本文":   [88.1, 90.3, 92.4]}
        >>> fig, ax = sp.plot_grouped_bar(
        ...     groups=["CIFAR-10", "CIFAR-100", "ImageNet"],
        ...     data=methods,
        ...     ylabel="Top-1 准确率 (%)",
        ...     palette="pastel-3",
        ... )
        >>> sp.save(fig, "compare_bar")
    """
    setup_style(venue, palette)
    fig, ax = new_figure(venue)
    colors = _get_cycle_colors()

    n_groups = len(groups)
    n_series = len(data)
    bar_w = (width - gap * (n_series - 1)) / n_series
    group_centers = np.arange(n_groups)

    for i, (series_name, values) in enumerate(data.items()):
        offsets = group_centers + (i - (n_series - 1) / 2) * (bar_w + gap)
        color = colors[i % len(colors)]
        bars = ax.bar(
            offsets, values, width=bar_w,
            color=color, label=series_name, **kwargs
        )
        if show_values:
            for bar, v in zip(bars, values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                    f"{v:{value_fmt}}",
                    ha="center", va="bottom",
                    fontsize=plt.rcParams.get("font.size", 9) - 1,
                )

    ax.set_xticks(group_centers)
    ax.set_xticklabels(groups)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.legend(loc=legend_loc)
    ax.tick_params(direction="in")
    return fig, ax


# ============================================================================
# 箱线图
# ============================================================================

def plot_box(
    data: Union[np.ndarray, List[np.ndarray]],
    labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    showfliers: bool = True,
    venue: str = "nature",
    palette: str = DEFAULT_PALETTE,
    **kwargs: Any,
) -> Tuple[Figure, Axes]:
    """
    绘制箱线图（展示中位数、四分位距和离群值）

    参数:
        data      : 单个数组或数组列表，每个数组代表一组数据
        showfliers: 是否显示离群点，默认 True

    示例:
        >>> fig, ax = sp.plot_box(
        ...     [scores_a, scores_b, scores_c],
        ...     labels=["算法A", "算法B", "算法C"],
        ...     ylabel="得分", palette="pastel-3"
        ... )
        >>> sp.save(fig, "boxplot")
    """
    setup_style(venue, palette)
    fig, ax = new_figure(venue)
    colors = _get_cycle_colors()

    bp = ax.boxplot(
        data, labels=labels, showfliers=showfliers,
        patch_artist=True, **kwargs
    )
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(colors[i % len(colors)])
        patch.set_alpha(0.75)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return fig, ax


# ============================================================================
# 小提琴图
# ============================================================================

def plot_violin(
    data: Union[np.ndarray, List[np.ndarray]],
    labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    showmeans: bool = False,
    showmedians: bool = True,
    venue: str = "nature",
    palette: str = DEFAULT_PALETTE,
    **kwargs: Any,
) -> Tuple[Figure, Axes]:
    """
    绘制小提琴图（比箱线图更直观地展示数据分布形状）

    参数:
        showmeans  : 是否显示均值线，默认 False
        showmedians: 是否显示中位数线，默认 True

    示例:
        >>> fig, ax = sp.plot_violin(
        ...     [data_a, data_b],
        ...     labels=["Method A", "Method B"],
        ...     ylabel="Accuracy (%)", showmedians=True
        ... )
    """
    setup_style(venue, palette)
    fig, ax = new_figure(venue)
    colors = _get_cycle_colors()

    parts = ax.violinplot(
        data, showmeans=showmeans, showmedians=showmedians, **kwargs
    )
    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(colors[i % len(colors)])
        pc.set_alpha(0.75)

    if labels:
        ax.set_xticks(range(1, len(labels) + 1))
        ax.set_xticklabels(labels)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return fig, ax


# ============================================================================
# 直方图
# ============================================================================

def plot_histogram(
    data: np.ndarray,
    bins: int = 30,
    xlabel: str = "",
    ylabel: str = "Frequency",
    title: str = "",
    density: bool = False,
    alpha: float = 0.75,
    venue: str = "nature",
    palette: str = DEFAULT_PALETTE,
    **kwargs: Any,
) -> Tuple[Figure, Axes]:
    """
    绘制直方图

    参数:
        bins   : 柱数，默认 30
        density: True 则归一化为概率密度

    示例:
        >>> fig, ax = sp.plot_histogram(
        ...     data, bins=40, density=True,
        ...     xlabel="残差", ylabel="概率密度"
        ... )
    """
    setup_style(venue, palette)
    fig, ax = new_figure(venue)
    colors = _get_cycle_colors()
    ax.hist(data, bins=bins, density=density, alpha=alpha,
            color=colors[0], **kwargs)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return fig, ax


# ============================================================================
# 显著性标注
# ============================================================================

def annotate_significance(
    ax: Axes,
    x1: float,
    x2: float,
    y: float,
    p_value: float,
    h: float = 0.02,
    tip_len: float = 0.01,
    color: str = "black",
    fontsize: Optional[int] = None,
    ns_text: str = "ns",
) -> None:
    """
    在箱线图/小提琴图上添加统计显著性标注（括号 + 星号）

    标注规则（国际通用）：
        p < 0.001 → ***
        p < 0.01  → **
        p < 0.05  → *
        p ≥ 0.05  → ns（not significant）

    参数:
        ax     : 目标坐标轴
        x1, x2 : 比较的两组在 x 轴上的坐标（通常是 1, 2, 3...）
        y      : 括号的 Y 坐标（通常设为两组中最高值 + 一点余量）
        p_value: p 值
        h      : 括号高度（axes 单位），默认 0.02
        tip_len: 括号端竖线长度（axes 单位），默认 0.01
        color  : 线条和文字颜色
        fontsize: 标注字号；None 则继承当前设置
        ns_text: p ≥ 0.05 时显示的文字，默认 "ns"

    示例:
        >>> fig, ax = sp.plot_box([d1, d2, d3], labels=["A", "B", "C"], ylabel="Score")
        >>> # 标注 A vs B 显著，A vs C 极显著
        >>> sp.annotate_significance(ax, 1, 2, y=max(d1.max(), d2.max()) + 0.5, p_value=0.03)
        >>> sp.annotate_significance(ax, 1, 3, y=max(d1.max(), d3.max()) + 1.5, p_value=0.0005)
        >>> sp.save(fig, "significance")
    """
    if p_value < 0.001:
        marker = "***"
    elif p_value < 0.01:
        marker = "**"
    elif p_value < 0.05:
        marker = "*"
    else:
        marker = ns_text

    lw = plt.rcParams.get("lines.linewidth", 1.0)
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y],
            lw=lw, color=color, clip_on=False)

    fs_kw: Dict[str, Any] = {}
    if fontsize is not None:
        fs_kw["fontsize"] = fontsize

    ax.text(
        (x1 + x2) / 2, y + h + tip_len,
        marker,
        ha="center", va="bottom", color=color,
        **fs_kw,
    )


# ============================================================================
# 内部工具
# ============================================================================

def _get_cycle_colors() -> List[str]:
    """从当前 rcParams 的 prop_cycle 中提取颜色列表"""
    prop_cycle = plt.rcParams["axes.prop_cycle"]
    return [c["color"] for c in prop_cycle]
