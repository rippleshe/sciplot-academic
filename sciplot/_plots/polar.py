"""
极坐标图表 — 雷达图/蜘蛛图

用于多维评估、性能对比等场景。
"""

from __future__ import annotations

from typing import Any, List, Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from sciplot._core.layout import new_figure
from sciplot._core.utils import apply_resolved_style
from sciplot._core.result import PlotResult


def plot_radar(
    categories: List[str],
    values_list: List[List[float]],
    labels: Optional[List[str]] = None,
    fill: bool = True,
    alpha: float = 0.3,
    title: str = "",
    show_grid: bool = True,
    show_labels: bool = False,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制雷达图/蜘蛛图（多维评估对比）

    参数:
        categories : 维度标签列表（如 ["准确率", "召回率", "F1", "速度"]）
        values_list: 多组数据列表，每组是一个与 categories 等长的数值列表
        labels     : 各组数据的图例标签
        fill       : 是否填充区域，默认 True
        alpha      : 填充透明度，默认 0.3
        show_grid  : 是否显示网格线
        show_labels: 是否在顶点显示数值标签

    示例:
        >>> categories = ["准确率", "召回率", "F1", "速度", "稳定性"]
        >>> values_list = [
        ...     [0.95, 0.88, 0.91, 0.85, 0.92],  # 方法A
        ...     [0.92, 0.91, 0.91, 0.90, 0.88],  # 方法B
        ... ]
        >>> fig, ax = sp.plot_radar(
        ...     categories, values_list,
        ...     labels=["方法A", "方法B"],
        ...     title="性能对比"
        ... )
        >>> sp.save(fig, "radar")
    """
    if not categories:
        raise ValueError("参数 'categories' 不能为空列表")
    if not values_list:
        raise ValueError("参数 'values_list' 不能为空列表")

    n_cats = len(categories)
    for i, values in enumerate(values_list):
        if len(values) != n_cats:
            raise ValueError(
                f"values_list[{i}] 长度 ({len(values)}) "
                f"与 categories 长度 ({n_cats}) 不一致"
            )
        numeric_values = np.asarray(values, dtype=float)
        if not np.all(np.isfinite(numeric_values)):
            raise ValueError(f"values_list[{i}] 包含 NaN 或 Inf，无法绘制雷达图")

    if labels is None:
        labels = [f"系列 {i+1}" for i in range(len(values_list))]
    elif len(labels) != len(values_list):
        raise ValueError(
            f"labels 长度 ({len(labels)}) 与 values_list 长度 ({len(values_list)}) 不一致"
        )

    effective_venue = apply_resolved_style(venue, palette, lang)

    # 使用 venue 的尺寸计算雷达图尺寸
    from sciplot._core.style import VENUES
    _, (w, h), _ = VENUES.get(effective_venue or "nature", VENUES["nature"])
    size = min(w, h) * 1.2  # 雷达图保持方形
    fig = plt.figure(figsize=(size, size))
    ax = fig.add_subplot(111, projection="polar")

    angles = np.linspace(0, 2 * np.pi, n_cats, endpoint=False).tolist()
    angles += angles[:1]

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

    all_values = np.concatenate([np.asarray(values, dtype=float) for values in values_list])
    data_span = float(np.nanmax(all_values) - np.nanmin(all_values)) if all_values.size else 0.0
    offset = data_span * 0.08 if data_span > 0 else 0.08

    for i, (values, label) in enumerate(zip(values_list, labels)):
        values_closed = values + values[:1]
        color = colors[i % len(colors)]

        ax.plot(angles, values_closed, "o-", color=color, label=label, **kwargs)
        if fill:
            ax.fill(angles, values_closed, alpha=alpha, color=color)

        if show_labels and len(values_list) == 1:
            for angle, value in zip(angles[:-1], values):
                ax.annotate(
                    f"{value:.2f}",
                    xy=(angle, value),
                    xytext=(angle, value + offset),
                    ha="center", va="bottom",
                    fontsize=plt.rcParams.get("font.size", 9) - 1,
                )

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)

    if show_grid:
        ax.grid(True, linestyle="--", alpha=0.5)

    ax.set_title(title, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.1))

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = ["plot_radar"]

