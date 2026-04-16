"""
分布图表 — 柱状图、分组柱状图、堆叠柱状图、水平柱状图、
          箱线图、小提琴图、直方图、组合图、显著性标注
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


def _resolve_style_venue(
    venue: Optional[str],
    palette: Optional[str],
) -> Optional[str]:
    """解析并应用样式，必要时复用 style_context 的当前 rcParams。"""
    if venue is None and palette is None:
        from sciplot._core.context import StyleContext
        if StyleContext.is_in_context():
            return None

    effective_venue = venue or "nature"
    effective_palette = palette or DEFAULT_PALETTE
    setup_style(effective_venue, effective_palette)
    return effective_venue


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
    venue: Optional[str] = None,
    palette: Optional[str] = None,
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
    effective_venue = _resolve_style_venue(venue, palette)
    fig, ax = new_figure(effective_venue)
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
    venue: Optional[str] = None,
    palette: Optional[str] = None,
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
    effective_venue = _resolve_style_venue(venue, palette)
    fig, ax = new_figure(effective_venue)
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
    venue: Optional[str] = None,
    palette: Optional[str] = None,
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
    effective_venue = _resolve_style_venue(venue, palette)
    fig, ax = new_figure(effective_venue)
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
    venue: Optional[str] = None,
    palette: Optional[str] = None,
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
    effective_venue = _resolve_style_venue(venue, palette)
    fig, ax = new_figure(effective_venue)
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
    venue: Optional[str] = None,
    palette: Optional[str] = None,
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
    effective_venue = _resolve_style_venue(venue, palette)
    fig, ax = new_figure(effective_venue)
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
# 堆叠柱状图
# ============================================================================

def plot_stacked_bar(
    categories: List[str],
    data: Dict[str, Union[List[float], np.ndarray]],
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    width: float = 0.6,
    show_values: bool = False,
    value_fmt: str = ".1f",
    legend_loc: str = "best",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs: Any,
) -> Tuple[Figure, Axes]:
    """
    绘制堆叠柱状图（展示各部分占总和的比例）

    参数:
        categories: 横轴分组标签
        data      : {系列名: 各组数值} 字典
        width     : 柱宽，默认 0.6
        show_values: 是否在柱上显示数值
        value_fmt : 数值格式，默认 ".1f"

    示例:
        >>> data = {
        ...     "训练集": [80, 85, 90],
        ...     "验证集": [10, 8, 5],
        ...     "测试集": [10, 7, 5],
        ... }
        >>> fig, ax = sp.plot_stacked_bar(
        ...     ["模型A", "模型B", "模型C"],
        ...     data,
        ...     ylabel="样本数量",
        ...     show_values=True
        ... )
    """
    effective_venue = _resolve_style_venue(venue, palette)
    fig, ax = new_figure(effective_venue)
    colors = _get_cycle_colors()

    n_groups = len(categories)
    n_series = len(data)
    x = np.arange(n_groups)

    bottom = np.zeros(n_groups)
    for i, (series_name, values) in enumerate(data.items()):
        color = colors[i % len(colors)]
        bars = ax.bar(
            x, values, width=width,
            bottom=bottom, color=color, label=series_name, **kwargs
        )
        if show_values:
            for j, (bar, v) in enumerate(zip(bars, values)):
                if v > 0:  # 只显示正值
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bottom[j] + v / 2,
                        f"{v:{value_fmt}}",
                        ha="center", va="center",
                        fontsize=plt.rcParams.get("font.size", 9) - 1,
                        color="white" if _is_dark_color(color) else "black",
                    )
        bottom += np.array(values)

    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.legend(loc=legend_loc)
    ax.tick_params(direction="in")
    return fig, ax


# ============================================================================
# 水平柱状图
# ============================================================================

def plot_horizontal_bar(
    categories: List[str],
    values: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    height: float = 0.6,
    show_values: bool = False,
    value_fmt: str = ".1f",
    sort: bool = False,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs: Any,
) -> Tuple[Figure, Axes]:
    """
    绘制水平柱状图（适合类别较多的场景）

    参数:
        height     : 柱高，默认 0.6
        show_values: 是否在柱尾显示数值
        sort       : 是否按数值降序排序，默认 False

    示例:
        >>> fig, ax = sp.plot_horizontal_bar(
        ...     ["特征A", "特征B", "特征C", "特征D"],
        ...     [0.85, 0.72, 0.91, 0.68],
        ...     xlabel="重要性",
        ...     show_values=True,
        ...     sort=True
        ... )
    """
    effective_venue = _resolve_style_venue(venue, palette)
    fig, ax = new_figure(effective_venue)
    colors = _get_cycle_colors()

    # 排序处理
    if sort:
        sorted_indices = np.argsort(values)[::-1]
        categories = [categories[i] for i in sorted_indices]
        values = np.array(values)[sorted_indices]

    y = np.arange(len(categories))
    bar_colors = [colors[i % len(colors)] for i in range(len(categories))]

    bars = ax.barh(y, values, height=height, color=bar_colors, **kwargs)

    if show_values:
        for bar, v in zip(bars, values):
            ax.text(
                bar.get_width() + 0.01 * max(values),
                bar.get_y() + bar.get_height() / 2,
                f"{v:{value_fmt}}",
                ha="left", va="center",
                fontsize=plt.rcParams.get("font.size", 9) - 1,
            )

    ax.set_yticks(y)
    ax.set_yticklabels(categories)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return fig, ax


# ============================================================================
# 组合图（折线 + 柱状）
# ============================================================================

def plot_combo(
    x: np.ndarray,
    bar_data: Dict[str, Union[List[float], np.ndarray]],
    line_data: Optional[Dict[str, Union[List[float], np.ndarray]]] = None,
    xlabel: str = "",
    ylabel_left: str = "",
    ylabel_right: str = "",
    title: str = "",
    bar_width: float = 0.35,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs: Any,
) -> Tuple[Figure, Axes, Optional[Axes]]:
    """
    绘制组合图（柱状图 + 折线图，常用于双 Y 轴场景）

    参数:
        bar_data    : 柱状图数据 {系列名: 数值列表}
        line_data   : 折线图数据 {系列名: 数值列表}，可选
        ylabel_left : 左 Y 轴标签（对应柱状图）
        ylabel_right: 右 Y 轴标签（对应折线图）
        bar_width   : 柱宽，默认 0.35

    返回:
        (fig, ax_bar, ax_line) 其中 ax_line 仅在 line_data 不为 None 时返回

    示例:
        >>> # 单 Y 轴：柱状 + 折线
        >>> fig, ax, _ = sp.plot_combo(
        ...     ["Q1", "Q2", "Q3", "Q4"],
        ...     bar_data={"销售额": [100, 120, 140, 160]},
        ...     line_data={"增长率": [5, 8, 12, 15]},
        ...     ylabel_left="销售额（万元）",
        ...     ylabel_right="增长率（%）",
        ... )

        >>> # 双 Y 轴：柱状 + 折线
        >>> fig, ax1, ax2 = sp.plot_combo(
        ...     months,
        ...     bar_data={"销量": sales},
        ...     line_data={"均价": prices},
        ... )
        >>> ax1.set_ylabel("销量（件）")
        >>> ax2.set_ylabel("均价（元）")
    """
    if not bar_data:
        raise ValueError("bar_data 不能为空，至少需要一个柱状图系列")

    effective_venue = _resolve_style_venue(venue, palette)
    fig, ax_bar = new_figure(effective_venue)
    colors = _get_cycle_colors()

    n_groups = len(x)
    n_bars = len(bar_data)
    indices = np.arange(n_groups)

    # 绘制柱状图
    bar_width_eff = bar_width / n_bars
    for i, (name, values) in enumerate(bar_data.items()):
        offset = (i - (n_bars - 1) / 2) * bar_width_eff
        color = colors[i % len(colors)]
        ax_bar.bar(indices + offset, values, bar_width_eff, label=name, color=color, **kwargs)

    ax_bar.set_xticks(indices)
    ax_bar.set_xticklabels(x)
    ax_bar.set_xlabel(xlabel)
    ax_bar.set_ylabel(ylabel_left)

    # 绘制折线图（如果有）
    ax_line = None
    if line_data:
        ax_line = ax_bar.twinx()
        ax_line.tick_params(direction="in")

        # 折线使用后续颜色
        line_colors = colors[n_bars:]
        if len(line_colors) < len(line_data):
            line_colors = colors  # 循环使用

        for i, (name, values) in enumerate(line_data.items()):
            color = line_colors[i % len(line_colors)]
            ax_line.plot(indices, values, "o-", color=color, label=name, markersize=5)

        ax_line.set_ylabel(ylabel_right)

        # 合并图例
        lines1, labels1 = ax_bar.get_legend_handles_labels()
        lines2, labels2 = ax_line.get_legend_handles_labels()
        ax_bar.legend(lines1 + lines2, labels1 + labels2, loc="best")
    else:
        ax_bar.legend()

    if title:
        ax_bar.set_title(title)
    ax_bar.tick_params(direction="in")

    return fig, ax_bar, ax_line


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


def _is_dark_color(hex_color: str) -> bool:
    """判断颜色是否为深色（用于决定文字用白色还是黑色）"""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    # 计算亮度（YIQ 公式）
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return brightness < 128
