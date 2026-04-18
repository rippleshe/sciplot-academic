"""
Venn 图可视化扩展

用于绘制集合关系图。
需要额外安装：pip install sciplot-academic[venn] 或 pip install matplotlib-venn
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from sciplot._core.layout import new_figure
from sciplot._core.utils import apply_resolved_style
from sciplot._core.result import PlotResult


def _check_venn():
    """检查 matplotlib-venn 是否可用"""
    try:
        from matplotlib_venn import venn2, venn3
        return venn2, venn3
    except ImportError:
        raise ImportError(
            "Venn 图功能需要安装 matplotlib-venn。\n"
            "请运行: pip install matplotlib-venn 或 pip install sciplot-academic[venn]"
        )


def plot_venn2(
    subsets: Union[Tuple[int, int, int], Dict[str, int]],
    set_labels: Tuple[str, str] = ("A", "B"),
    title: str = "",
    alpha: float = 0.5,
    show_counts: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制双集合 Venn 图

    参数:
        subsets    : 子集大小
                     - 元组形式: (仅A, 仅B, AB交集)
                     - 字典形式: {"10": 仅A, "01": 仅B, "11": AB交集}
        set_labels : 集合标签，默认 ("A", "B")
        title      : 图标题
        alpha      : 填充透明度
        show_counts: 是否显示计数

    示例:
        >>> # 元组形式
        >>> fig, ax = sp.plot_venn2((10, 8, 5), set_labels=("方法A", "方法B"))
        >>> 
        >>> # 字典形式
        >>> fig, ax = sp.plot_venn2({"10": 10, "01": 8, "11": 5})
    """
    venn2, _ = _check_venn()

    effective_venue = apply_resolved_style(venue, palette)
    fig, ax = new_figure(effective_venue)

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

    v = venn2(
        subsets=subsets,
        set_labels=set_labels,
        ax=ax,
        **kwargs,
    )

    if v is not None:
        for i, patch in enumerate(v.patches):
            if patch is not None:
                patch.set_facecolor(colors[i % len(colors)])
                patch.set_alpha(alpha)

        if show_counts:
            for text in v.subset_labels:
                if text is not None:
                    text.set_fontsize(plt.rcParams.get("font.size", 9))

    ax.set_title(title)
    ax.set_axis_off()

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_venn3(
    subsets: Union[Tuple[int, int, int, int, int, int, int], Dict[str, int]],
    set_labels: Tuple[str, str, str] = ("A", "B", "C"),
    title: str = "",
    alpha: float = 0.5,
    show_counts: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制三集合 Venn 图

    参数:
        subsets    : 子集大小
                     - 元组形式: (仅A, 仅B, AB, 仅C, AC, BC, ABC)
                     - 字典形式: {"100": 仅A, "010": 仅B, ...}
        set_labels : 集合标签，默认 ("A", "B", "C")
        title      : 图标题
        alpha      : 填充透明度
        show_counts: 是否显示计数

    示例:
        >>> # 元组形式
        >>> fig, ax = sp.plot_venn3(
        ...     (10, 8, 5, 7, 4, 3, 2),
        ...     set_labels=("方法A", "方法B", "方法C")
        ... )
        >>> 
        >>> # 字典形式
        >>> fig, ax = sp.plot_venn3({
        ...     "100": 10, "010": 8, "110": 5,
        ...     "001": 7, "101": 4, "011": 3, "111": 2
        ... })
    """
    _, venn3 = _check_venn()

    effective_venue = apply_resolved_style(venue, palette)
    fig, ax = new_figure(effective_venue)

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

    v = venn3(
        subsets=subsets,
        set_labels=set_labels,
        ax=ax,
        **kwargs,
    )

    if v is not None:
        for i, patch in enumerate(v.patches):
            if patch is not None:
                patch.set_facecolor(colors[i % len(colors)])
                patch.set_alpha(alpha)

        if show_counts:
            for text in v.subset_labels:
                if text is not None:
                    text.set_fontsize(plt.rcParams.get("font.size", 9))

    ax.set_title(title)
    ax.set_axis_off()

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = ["plot_venn2", "plot_venn3"]
