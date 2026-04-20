"""
分布图表 — 柱状图、分组柱状图、堆叠柱状图、水平柱状图、
          箱线图、小提琴图、直方图、组合图、显著性标注
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from sciplot._core.style import setup_style
from sciplot._core.palette import DEFAULT_PALETTE
from sciplot._core.layout import new_figure
from sciplot._core.utils import (
    apply_resolved_style,
    validate_dict_not_empty,
    validate_array_like,
    validate_positive_number,
)
from sciplot._core.result import PlotResult, ComboPlotResult


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
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制单组柱状图（每个柱子自动赋不同颜色）

    参数:
        lang: 语言设置

    示例:
        >>> fig, ax = sp.plot_bar(
        ...     ["方法A", "方法B", "方法C"],
        ...     np.array([82.3, 85.1, 88.7]),
        ...     xlabel="方法", ylabel="准确率 (%)",
        ...     palette="pastel-3"
        ... )
        >>> sp.save(fig, "accuracy_bar")
    """
    # 输入验证
    if not categories:
        raise ValueError("参数 'categories' 不能为空列表")
    values = np.asarray(validate_array_like(values, "values"), dtype=float)
    if len(categories) != len(values):
        raise ValueError(
            f"categories 长度 ({len(categories)}) 与 values 长度 ({len(values)}) 不一致"
        )
    if not np.all(np.isfinite(values)):
        raise ValueError("values 不能包含 NaN 或 Inf")
    width = validate_positive_number(width, "width", allow_zero=False)

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)
    colors = _get_cycle_colors()
    bar_colors = [colors[i % len(colors)] for i in range(len(categories))]
    ax.bar(categories, values, width=width, color=bar_colors, **kwargs)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


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
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
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
        lang       : 语言设置

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
    # 输入验证
    if not groups:
        raise ValueError("参数 'groups' 不能为空列表")
    data = validate_dict_not_empty(data, "data")
    n_groups = len(groups)
    normalized_data: Dict[str, np.ndarray] = {}
    for series_name, values in data.items():
        values_arr = np.asarray(values, dtype=float).ravel()
        if len(values_arr) != n_groups:
            raise ValueError(
                f"数据系列 '{series_name}' 的长度 ({len(values_arr)}) "
                f"与 groups 长度 ({n_groups}) 不一致"
            )
        if not np.all(np.isfinite(values_arr)):
            raise ValueError(f"数据系列 '{series_name}' 不能包含 NaN 或 Inf")
        normalized_data[series_name] = values_arr
    width = validate_positive_number(width, "width", allow_zero=False)
    gap = validate_positive_number(gap, "gap", allow_zero=True)

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)
    colors = _get_cycle_colors()

    n_series = len(normalized_data)
    if width <= gap * (n_series - 1):
        raise ValueError(
            f"width={width} 过小，必须大于 gap*(系列数-1)={gap * (n_series - 1):.6g}，"
            "否则每个柱子的宽度将小于等于 0"
        )
    bar_w = (width - gap * (n_series - 1)) / n_series
    group_centers = np.arange(n_groups)

    for i, (series_name, values) in enumerate(normalized_data.items()):
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
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


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
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制箱线图（展示中位数、四分位距和离群值）

    参数:
        data      : 单个数组或数组列表，每个数组代表一组数据
        showfliers: 是否显示离群点，默认 True
        lang      : 语言设置

    示例:
        >>> fig, ax = sp.plot_box(
        ...     [scores_a, scores_b, scores_c],
        ...     labels=["算法A", "算法B", "算法C"],
        ...     ylabel="得分", palette="pastel-3"
        ... )
        >>> sp.save(fig, "boxplot")
    """
    if isinstance(data, (list, tuple)):
        if not data:
            raise ValueError("参数 'data' 不能为空列表")
        for i, values in enumerate(data):
            values_arr = np.asarray(values, dtype=float).ravel()
            if values_arr.size == 0:
                raise ValueError(f"data[{i}] 不能为空")
            if not np.all(np.isfinite(values_arr)):
                raise ValueError(f"data[{i}] 不能包含 NaN 或 Inf")
        if labels is not None and len(labels) != len(data):
            raise ValueError(
                f"labels 长度 ({len(labels)}) 与数据组数 ({len(data)}) 不一致"
            )
    else:
        data_arr = np.asarray(data, dtype=float)
        if data_arr.size == 0:
            raise ValueError("参数 'data' 不能为空")
        if not np.all(np.isfinite(data_arr)):
            raise ValueError("data 不能包含 NaN 或 Inf")

    effective_venue = apply_resolved_style(venue, palette, lang)
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
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


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
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制小提琴图（比箱线图更直观地展示数据分布形状）

    参数:
        showmeans  : 是否显示均值线，默认 False
        showmedians: 是否显示中位数线，默认 True
        lang       : 语言设置

    示例:
        >>> fig, ax = sp.plot_violin(
        ...     [data_a, data_b],
        ...     labels=["Method A", "Method B"],
        ...     ylabel="Accuracy (%)", showmedians=True
        ... )
    """
    if isinstance(data, (list, tuple)):
        if not data:
            raise ValueError("参数 'data' 不能为空列表")
        for i, values in enumerate(data):
            if np.asarray(values).size == 0:
                raise ValueError(f"data[{i}] 不能为空")
        n_groups = len(data)
    else:
        data_arr = np.asarray(data)
        if data_arr.size == 0:
            raise ValueError("参数 'data' 不能为空")
        n_groups = data_arr.shape[1] if data_arr.ndim > 1 else 1

    if labels is not None and len(labels) != n_groups:
        raise ValueError(
            f"labels 长度 ({len(labels)}) 与数据组数 ({n_groups}) 不一致"
        )

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)
    colors = _get_cycle_colors()

    parts = ax.violinplot(
        data, showmeans=showmeans, showmedians=showmedians, **kwargs
    )
    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(colors[i % len(colors)])
        pc.set_alpha(0.75)

    if labels is not None:
        ax.set_xticks(range(1, n_groups + 1))
        ax.set_xticklabels(labels)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


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
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制直方图

    参数:
        bins   : 柱数，默认 30
        density: True 则归一化为概率密度
        lang   : 语言设置

    示例:
        >>> fig, ax = sp.plot_histogram(
        ...     data, bins=40, density=True,
        ...     xlabel="残差", ylabel="概率密度"
        ... )
    """
    values = np.asarray(data, dtype=float).ravel()
    finite_values = values[np.isfinite(values)]
    if finite_values.size == 0:
        raise ValueError("data 至少需要 1 个有限数值")
    if not isinstance(bins, int) or bins <= 0:
        raise ValueError(f"bins 必须为正整数，实际值: {bins!r}")

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)
    colors = _get_cycle_colors()
    ax.hist(finite_values, bins=bins, density=density, alpha=alpha,
            color=colors[0], **kwargs)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


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
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制堆叠柱状图（展示各部分占总和的比例）

    参数:
        categories: 横轴分组标签
        data      : {系列名: 各组数值} 字典
        width     : 柱宽，默认 0.6
        show_values: 是否在柱上显示数值
        value_fmt : 数值格式，默认 ".1f"
        lang      : 语言设置

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
    if not categories:
        raise ValueError("参数 'categories' 不能为空列表")
    data = validate_dict_not_empty(data, "data")
    width = validate_positive_number(width, "width", allow_zero=False)

    n_groups = len(categories)
    normalized_data: Dict[str, np.ndarray] = {}
    for series_name, values in data.items():
        series_values = np.asarray(
            validate_array_like(values, f"data['{series_name}']"),
            dtype=float,
        )
        if len(series_values) != n_groups:
            raise ValueError(
                f"数据系列 '{series_name}' 的长度 ({len(series_values)}) "
                f"与 categories 长度 ({n_groups}) 不一致"
            )
        if not np.all(np.isfinite(series_values)):
            raise ValueError(f"数据系列 '{series_name}' 不能包含 NaN 或 Inf")
        normalized_data[series_name] = series_values

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)
    colors = _get_cycle_colors()

    x = np.arange(n_groups)

    bottom = np.zeros(n_groups)
    for i, (series_name, values) in enumerate(normalized_data.items()):
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
        bottom += values

    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.legend(loc=legend_loc)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


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
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制水平柱状图（适合类别较多的场景）

    参数:
        height     : 柱高，默认 0.6
        show_values: 是否在柱尾显示数值
        sort       : 是否按数值升序排序（最大值在顶部），默认 False

    示例:
        >>> fig, ax = sp.plot_horizontal_bar(
        ...     ["特征A", "特征B", "特征C", "特征D"],
        ...     [0.85, 0.72, 0.91, 0.68],
        ...     xlabel="重要性",
        ...     show_values=True,
        ...     sort=True
        ... )
    """
    if not categories:
        raise ValueError("参数 'categories' 不能为空列表")
    values_arr = np.asarray(values, dtype=float).ravel()
    if len(categories) != len(values_arr):
        raise ValueError(
            f"categories 长度 ({len(categories)}) 与 values 长度 ({len(values_arr)}) 不一致"
        )
    if values_arr.size == 0:
        raise ValueError("参数 'values' 不能为空")
    if not np.all(np.isfinite(values_arr)):
        raise ValueError("values 不能包含 NaN 或 Inf")
    height = validate_positive_number(height, "height", allow_zero=False)

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)
    colors = _get_cycle_colors()

    # 排序处理（升序，让最大值在顶部）
    if sort:
        sorted_indices = np.argsort(values_arr)  # 升序
        categories = [categories[i] for i in sorted_indices]
        values_arr = values_arr[sorted_indices]

    y = np.arange(len(categories))
    bar_colors = [colors[i % len(colors)] for i in range(len(categories))]

    bars = ax.barh(y, values_arr, height=height, color=bar_colors, **kwargs)

    if show_values:
        value_offset = max(float(np.max(np.abs(values_arr))) * 0.01, 1e-9)
        for bar, v in zip(bars, values_arr):
            text_x = bar.get_width() + (value_offset if bar.get_width() >= 0 else -value_offset)
            text_ha = "left" if bar.get_width() >= 0 else "right"
            ax.text(
                text_x,
                bar.get_y() + bar.get_height() / 2,
                f"{v:{value_fmt}}",
                ha=text_ha, va="center",
                fontsize=plt.rcParams.get("font.size", 9) - 1,
            )

    ax.set_yticks(y)
    ax.set_yticklabels(categories)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


# ============================================================================
# 棒棒糖图
# ============================================================================

def plot_lollipop(
    categories: List[str],
    values: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    sort: bool = True,
    marker_size: float = 8,
    stem_width: float = 2.0,
    baseline: float = 0.0,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制棒棒糖图，用于类别排名与重要性展示。"""
    if not categories:
        raise ValueError("参数 'categories' 不能为空列表")

    values_arr = np.asarray(values, dtype=float)
    if values_arr.ndim != 1:
        raise ValueError("values 必须是一维数组")
    if len(categories) != len(values_arr):
        raise ValueError(
            f"categories 长度 ({len(categories)}) 与 values 长度 ({len(values_arr)}) 不一致"
        )
    if not np.all(np.isfinite(values_arr)):
        raise ValueError("values 不能包含 NaN 或 Inf")

    marker_size = validate_positive_number(marker_size, "marker_size", allow_zero=False)
    stem_width = validate_positive_number(stem_width, "stem_width", allow_zero=False)

    if sort:
        order = np.argsort(values_arr)
        categories = [categories[i] for i in order]
        values_arr = values_arr[order]

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)
    colors = _get_cycle_colors()
    main_color = colors[0]

    x = np.arange(len(categories))
    ax.hlines(y=baseline, xmin=-0.5, xmax=len(categories) - 0.5, color="#BFBFBF", linewidth=1)
    ax.vlines(x, baseline, values_arr, color=main_color, linewidth=stem_width, alpha=0.9)
    ax.scatter(x, values_arr, s=marker_size**2, color=main_color, zorder=3, **kwargs)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha="right")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


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
    lang: Optional[str] = None,
    **kwargs: Any,
) -> ComboPlotResult:
    """
    绘制组合图（柱状图 + 折线图，常用于双 Y 轴场景）

    参数:
        x           : 横轴标签数组
        bar_data    : 柱状图数据 {系列名: 数值列表}
        line_data   : 折线图数据 {系列名: 数值列表}，可选
        xlabel      : X 轴标签
        ylabel_left : 左 Y 轴标签（对应柱状图）
        ylabel_right: 右 Y 轴标签（对应折线图）
        bar_width   : 柱宽，默认 0.35
        venue       : 期刊样式
        palette     : 配色方案
        lang        : 语言设置

    返回:
        PlotResult: 包含 fig 和 axes 的结果对象
            - 单 Y 轴时: result.ax 为主坐标轴
            - 双 Y 轴时: result.ax_array[0] 为柱状图轴, result.ax_array[1] 为折线图轴

    示例:
        >>> # 单 Y 轴：柱状 + 折线
        >>> result = sp.plot_combo(
        ...     ["Q1", "Q2", "Q3", "Q4"],
        ...     bar_data={"销售额": [100, 120, 140, 160]},
        ...     line_data={"增长率": [5, 8, 12, 15]},
        ...     ylabel_left="销售额（万元）",
        ...     ylabel_right="增长率（%）",
        ... )
        >>> result.save("combo_chart")

        >>> # 双 Y 轴访问
        >>> result = sp.plot_combo(months, bar_data={"销量": sales}, line_data={"均价": prices})
        >>> ax_bar, ax_line = result.ax_array
    """
    if not bar_data:
        raise ValueError("bar_data 不能为空，至少需要一个柱状图系列")

    if len(x) == 0:
        raise ValueError("x 不能为空")
    bar_width = validate_positive_number(bar_width, "bar_width", allow_zero=False)

    n_groups = len(x)
    normalized_bar_data: Dict[str, np.ndarray] = {}
    for name, values in bar_data.items():
        series_values = np.asarray(
            validate_array_like(values, f"bar_data['{name}']"),
            dtype=float,
        )
        if len(series_values) != n_groups:
            raise ValueError(
                f"bar_data['{name}'] 长度 ({len(series_values)}) 与 x 长度 ({n_groups}) 不一致"
            )
        if not np.all(np.isfinite(series_values)):
            raise ValueError(f"bar_data['{name}'] 不能包含 NaN 或 Inf")
        normalized_bar_data[name] = series_values

    normalized_line_data: Optional[Dict[str, np.ndarray]] = None
    if line_data:
        normalized_line_data = {}
        for name, values in line_data.items():
            series_values = np.asarray(
                validate_array_like(values, f"line_data['{name}']"),
                dtype=float,
            )
            if len(series_values) != n_groups:
                raise ValueError(
                    f"line_data['{name}'] 长度 ({len(series_values)}) 与 x 长度 ({n_groups}) 不一致"
                )
            if not np.all(np.isfinite(series_values)):
                raise ValueError(f"line_data['{name}'] 不能包含 NaN 或 Inf")
            normalized_line_data[name] = series_values

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax_bar = new_figure(effective_venue)
    colors = _get_cycle_colors()

    n_bars = len(normalized_bar_data)
    indices = np.arange(n_groups)

    bar_width_eff = bar_width / n_bars
    for i, (name, values) in enumerate(normalized_bar_data.items()):
        offset = (i - (n_bars - 1) / 2) * bar_width_eff
        color = colors[i % len(colors)]
        ax_bar.bar(indices + offset, values, bar_width_eff, label=name, color=color, **kwargs)

    ax_bar.set_xticks(indices)
    ax_bar.set_xticklabels(x)
    ax_bar.set_xlabel(xlabel)
    ax_bar.set_ylabel(ylabel_left)

    ax_line = None
    if normalized_line_data:
        ax_line = ax_bar.twinx()
        ax_line.tick_params(direction="in")

        line_colors = colors[n_bars:]
        if len(line_colors) < len(normalized_line_data):
            line_colors = colors

        for i, (name, values) in enumerate(normalized_line_data.items()):
            color = line_colors[i % len(line_colors)]
            ax_line.plot(indices, values, "o-", color=color, label=name, markersize=5)

        ax_line.set_ylabel(ylabel_right)

        lines1, labels1 = ax_bar.get_legend_handles_labels()
        lines2, labels2 = ax_line.get_legend_handles_labels()
        ax_bar.legend(lines1 + lines2, labels1 + labels2, loc="best")
    else:
        ax_bar.legend()

    if title:
        ax_bar.set_title(title)
    ax_bar.tick_params(direction="in")

    return ComboPlotResult(
        fig,
        ax_bar=ax_bar,
        ax_line=ax_line,
        metadata={"venue": venue, "palette": palette},
    )


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
        y      : 括号的 Y 坐标（数据坐标，与 y 轴数据单位相同）
                 默认 0.02，适合 y 轴范围为 [0, 1] 的场景
                 y 轴范围较大时（如 [0, 100]），建议设为 y_range * 0.03 左右
        p_value: p 值
        h      : 括号高度（数据坐标单位），默认 0.02
        tip_len: 括号端竖线长度（数据坐标单位），默认 0.01
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
    colors = []
    for c in prop_cycle:
        if "color" in c:
            colors.append(c["color"])
    # 如果没有找到颜色，使用默认颜色
    if not colors:
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    return colors


def _is_dark_color(color: str) -> bool:
    """判断颜色是否为深色（用于决定文字用白色还是黑色）"""
    try:
        import matplotlib.colors as mcolors
        rgb = mcolors.to_rgb(color)
        r, g, b = rgb
        # 计算亮度（YIQ 公式）
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return brightness < 0.502  # 归一化后的阈值
    except (ValueError, AttributeError):
        return False
