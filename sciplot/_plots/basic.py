"""
基础图表 — 折线图、散点图、阶梯图、面积图
"""

from __future__ import annotations

from typing import Any, List, Optional, Union

import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from sciplot._core.style import setup_style
from sciplot._core.palette import DEFAULT_PALETTE, RESIDENT_PALETTES
from sciplot._core.layout import new_figure
from sciplot._core.utils import apply_resolved_style, validate_labels_match_data
from sciplot._core.result import PlotResult


LINE_STYLES: List[str] = ["-", "--", "-.", ":"]
MARKERS: List[str] = ["o", "s", "^", "D", "v", "<", ">", "p", "*", "h"]
_AUTO_SUBSET_BASES = {"pastel", "earth", "ocean", "forest", "sunset"}
_LINE2D_KWARGS = set(Line2D([], []).properties().keys()) | set(getattr(Line2D, "_alias_map", {}).keys())


def _resolve_auto_subset_palette(palette: Optional[str], n_series: int) -> str:
    """根据系列数自动选择内置配色子集。"""
    effective_palette = palette or DEFAULT_PALETTE
    if "-" in effective_palette:
        return effective_palette

    if effective_palette in _AUTO_SUBSET_BASES:
        candidate = f"{effective_palette}-{n_series}"
        if candidate in RESIDENT_PALETTES:
            return candidate

    return effective_palette


def _validate_xy_lengths(x: np.ndarray, y: np.ndarray, x_name: str = "x", y_name: str = "y") -> None:
    """校验 x/y 长度一致，避免 matplotlib 抛出难以定位的底层错误。"""
    if len(x) != len(y):
        raise ValueError(
            f"{x_name} 长度 ({len(x)}) 与 {y_name} 长度 ({len(y)}) 不一致"
        )


def plot_line(
    x: np.ndarray,
    y: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    label: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制单条折线图

    参数:
        lang: 语言设置，如 "zh", "en" 等

    示例:
        >>> x = np.linspace(0, 10, 200)
        >>> fig, ax = sp.plot(x, np.sin(x), xlabel="时间 (s)", ylabel="幅度", label="sin(x)")
        >>> sp.save(fig, "result")
    """
    _validate_xy_lengths(x, y)

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)
    ax.plot(x, y, label=label, **kwargs)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    if label:
        ax.legend()
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


# 简化别名
plot = plot_line


def plot_multi(
    x: Union[np.ndarray, List[np.ndarray]],
    y_list: List[np.ndarray],
    labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制多条折线图（智能选配色子集）

    智能配色规则（pastel / earth / ocean）：
        N ≤ 4 → 自动选 palette-N 子集（如 pastel-2）
        N = 5 → 使用完整 5 色
        N ≥ 6 → 直接循环完整配色（建议手动指定如 ocean）

    参数:
        x      : X 轴数据（共享一个数组）或 X 数据列表（每条线各自的 X）
        y_list : Y 轴数据列表 [y1, y2, ...]
        labels : 图例标签列表；为 None 则自动生成 "Series 1, 2, …"
        palette: 默认 pastel；也可用 earth / ocean / 人民币系列
        lang   : 语言设置

    示例:
        >>> # 2 条线 → 自动用 pastel-2
        >>> fig, ax = sp.plot_multi(x, [y1, y2], labels=["方法A", "方法B"],
        ...                         xlabel="时间 (s)", ylabel="准确率 (%)")

        >>> # 3 条线用 earth 系列
        >>> fig, ax = sp.plot_multi(x, [y1, y2, y3], palette="earth",
        ...                         labels=["A", "B", "C"])
    """
    if not y_list:
        raise ValueError("参数 'y_list' 不能为空列表")

    n = len(y_list)
    effective_palette = _resolve_auto_subset_palette(palette, n)

    return plot_multi_line(
        x, y_list,
        labels=labels, xlabel=xlabel, ylabel=ylabel, title=title,
        venue=venue, palette=effective_palette, lang=lang,
        use_linestyles=False, **kwargs,
    )


def plot_multi_line(
    x: Union[np.ndarray, List[np.ndarray]],
    y_list: List[np.ndarray],
    labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    use_linestyles: bool = False,
    show_legend: bool = True,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制多线折线图（完整参数版）

    参数:
        use_linestyles: True 时在不同颜色外叠加线型循环（- -- -. :），
                        提升黑白打印/色盲可读性
        show_legend   : 是否显示图例，默认 True；当 labels 为自动生成时可设为 False
        lang          : 语言设置

    示例:
        >>> fig, ax = sp.plot_multi_line(
        ...     x, [y1, y2, y3],
        ...     labels=["Train", "Val", "Test"],
        ...     palette="ocean-3", use_linestyles=True
        ... )
    """
    if not y_list:
        raise ValueError("参数 'y_list' 不能为空列表")

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

    labels = validate_labels_match_data(labels, y_list)

    if isinstance(x, list) and len(x) != len(y_list):
        raise ValueError(
            f"x 列表长度 ({len(x)}) 与 y_list 长度 ({len(y_list)}) 不一致"
        )

    for i, (y, lbl) in enumerate(zip(y_list, labels)):
        xi = x if isinstance(x, np.ndarray) else x[i]
        _validate_xy_lengths(xi, y, x_name=("x" if isinstance(x, np.ndarray) else f"x[{i}]"), y_name=f"y_list[{i}]")
        ls = LINE_STYLES[i % len(LINE_STYLES)] if use_linestyles else "-"
        ax.plot(xi, y, label=lbl, linestyle=ls, **kwargs)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    if show_legend:
        ax.legend()
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_scatter(
    x: np.ndarray,
    y: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    label: str = "",
    s: float = 20,
    alpha: float = 0.7,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制散点图

    参数:
        s    : 点大小，默认 20
        alpha: 透明度，默认 0.7
        lang : 语言设置

    示例:
        >>> fig, ax = sp.plot_scatter(x, y, xlabel="X", ylabel="Y",
        ...                           label="样本", s=30, alpha=0.6)
        >>> sp.save(fig, "scatter")
    """
    _validate_xy_lengths(x, y)

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)
    sc = ax.scatter(x, y, s=s, alpha=alpha, label=label, **kwargs)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    if label:
        ax.legend()
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_step(
    x: np.ndarray,
    y: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    label: str = "",
    where: str = "mid",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制阶梯图（累积分布函数 CDF、直方型折线等常见于物理/统计论文）

    参数:
        where: 台阶位置
               'mid'  → 台阶在 x 中点（默认，直方图风格）
               'pre'  → 台阶在左端
               'post' → 台阶在右端
        lang : 语言设置

    示例:
        >>> # 绘制 CDF
        >>> sorted_data = np.sort(data)
        >>> cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
        >>> fig, ax = sp.plot_step(sorted_data, cdf,
        ...     xlabel="值", ylabel="累积概率", label="CDF")
        >>> sp.save(fig, "cdf")
    """
    _validate_xy_lengths(x, y)

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)
    ax.step(x, y, where=where, label=label, **kwargs)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    if label:
        ax.legend()
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_area(
    x: np.ndarray,
    y: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    label: str = "",
    alpha: float = 0.3,
    fill: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制面积图（折线下方填充）

    参数:
        alpha: 填充区域透明度，默认 0.3；fill=False 时忽略
        fill : 是否填充面积，默认 True；False 则只画线
        lang : 语言设置

    示例:
        >>> # 简单面积图
        >>> fig, ax = sp.plot_area(x, y, xlabel="时间", ylabel="数值",
        ...                        label="指标A", alpha=0.4)
        >>> sp.save(fig, "area_chart")

        >>> # 多组面积图（堆叠效果）
        >>> fig, ax = sp.plot_area(x, y1, label="A", alpha=0.3)
        >>> ax.fill_between(x, y1, y1+y2, alpha=0.3, label="B")
        >>> ax.legend()
        >>> sp.save(fig, "stacked_area")
    """
    _validate_xy_lengths(x, y)

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

    (line,) = ax.plot(x, y, label=label, **kwargs)

    if fill:
        color = line.get_color()
        ax.fill_between(x, y, alpha=alpha, color=color)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    if label:
        ax.legend()
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_multi_area(
    x: np.ndarray,
    y_list: List[np.ndarray],
    labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    stacked: bool = False,
    alpha: float = 0.3,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制多组面积图（支持堆叠模式）

    参数:
        stacked: True 则绘制堆叠面积图，False 则各组独立
        alpha  : 填充透明度，默认 0.3
        lang   : 语言设置

    示例:
        >>> # 独立面积图
        >>> fig, ax = sp.plot_multi_area(x, [y1, y2, y3],
        ...     labels=["A", "B", "C"], xlabel="时间", ylabel="数值")

        >>> # 堆叠面积图
        >>> fig, ax = sp.plot_multi_area(x, [y1, y2, y3],
        ...     labels=["A", "B", "C"], stacked=True, alpha=0.5)
        >>> sp.save(fig, "stacked_area")
    """
    import matplotlib.pyplot as plt

    if not y_list:
        raise ValueError("参数 'y_list' 不能为空列表")

    n = len(y_list)
    effective_palette = _resolve_auto_subset_palette(palette, n)

    effective_venue = apply_resolved_style(venue, effective_palette, lang)
    fig, ax = new_figure(effective_venue)

    labels = validate_labels_match_data(labels, y_list)

    # 验证数组长度一致性
    x_len = len(x)
    for i, y in enumerate(y_list):
        if len(y) != x_len:
            raise ValueError(
                f"y_list[{i}] 长度 ({len(y)}) 与 x 长度 ({x_len}) 不一致"
            )

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

    if stacked:
        # 堆叠面积图
        y_stack = np.zeros(len(x))
        for i, (y, lbl) in enumerate(zip(y_list, labels)):
            color = colors[i % len(colors)]
            fill_kwargs = dict(kwargs)
            fill_kwargs.pop("label", None)
            fill_kwargs.setdefault("alpha", alpha)
            fill_kwargs.setdefault("color", color)
            ax.fill_between(x, y_stack, y_stack + y, label=lbl, **fill_kwargs)
            y_stack = y_stack + y
    else:
        # 独立面积图：绘制边界线 + 半透明填充
        for i, (y, lbl) in enumerate(zip(y_list, labels)):
            color = colors[i % len(colors)]

            line_kwargs = {k: v for k, v in kwargs.items() if k in _LINE2D_KWARGS}
            line_kwargs.pop("label", None)
            line_kwargs.setdefault("color", color)
            (line,) = ax.plot(x, y, **line_kwargs)

            fill_kwargs = dict(kwargs)
            fill_kwargs.pop("label", None)
            fill_kwargs["alpha"] = alpha
            fill_kwargs.setdefault("color", line.get_color())
            ax.fill_between(x, y, label=lbl, **fill_kwargs)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.legend()
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": effective_palette})


__all__ = [
    "plot_line",
    "plot",
    "plot_multi",
    "plot_multi_line",
    "plot_scatter",
    "plot_step",
    "plot_area",
    "plot_multi_area",
]
