"""
智能辅助工具 — 自动布局优化、智能图例、标签旋转等
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def auto_rotate_labels(
    ax: Axes,
    axis: str = "x",
    max_labels: int = 10,
    threshold: int = 6,
    rotation: float = 45,
) -> None:
    """
    自动旋转轴标签以避免重叠

    参数:
        axis      : "x" 或 "y"
        max_labels: 最大标签数，超过则自动旋转
        threshold : 标签长度阈值，超过则自动旋转
        rotation  : 旋转角度，默认 45 度

    示例:
        >>> fig, ax = sp.plot_bar(categories, values)
        >>> sp.auto_rotate_labels(ax)  # 自动检测并旋转 X 轴标签
    """
    if axis == "x":
        labels = ax.get_xticklabels()
        tick_labels = [t.get_text() for t in labels]

        should_rotate = (
            len(tick_labels) > max_labels
            or any(len(str(l)) > threshold for l in tick_labels)
        )

        if should_rotate:
            plt.setp(ax.get_xticklabels(), rotation=rotation, ha="right")
    else:
        labels = ax.get_yticklabels()
        tick_labels = [t.get_text() for t in labels]

        should_rotate = (
            len(tick_labels) > max_labels
            or any(len(str(l)) > threshold for l in tick_labels)
        )

        if should_rotate:
            plt.setp(ax.get_yticklabels(), rotation=rotation, ha="right")


def smart_legend(
    ax: Axes,
    loc: str = "best",
    outside: bool = False,
    ncols: Optional[int] = None,
) -> None:
    """
    智能图例位置调整

    参数:
        loc     : 图例位置，默认 "best"
        outside : True 则将图例放在图外右侧
        ncols   : 图例列数，None 则自动计算

    示例:
        >>> fig, ax = sp.plot_multi(x, [y1, y2, y3, y4, y5])
        >>> sp.smart_legend(ax, ncols=2)  # 2 列图例

        >>> # 图例放外面
        >>> sp.smart_legend(ax, outside=True)
    """
    handles, labels = ax.get_legend_handles_labels()

    if not handles:
        return

    # 自动计算列数
    if ncols is None:
        ncols = max(1, len(handles) // 4)

    if outside:
        ax.legend(
            handles, labels,
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            ncol=ncols,
        )
    else:
        ax.legend(handles, labels, loc=loc, ncol=ncols)


def optimize_layout(fig: Figure, tight: bool = True) -> None:
    """
    自动优化图形布局，减少白边

    参数:
        tight: True 则使用 tight_layout

    示例:
        >>> fig, axes = sp.paper_subplots(2, 2)
        >>> # ... 绘图 ...
        >>> sp.optimize_layout(fig)
        >>> sp.save(fig, "optimized")
    """
    if tight:
        fig.tight_layout()


def adjust_subplots(
    fig: Figure,
    hspace: float = 0.3,
    wspace: float = 0.3,
    top: float = 0.95,
    bottom: float = 0.08,
    left: float = 0.1,
    right: float = 0.95,
) -> None:
    """
    精细调整子图间距

    参数:
        hspace: 垂直间距
        wspace: 水平间距
        top   : 顶部边距
        bottom: 底部边距
        left  : 左边距
        right : 右边距

    示例:
        >>> fig, axes = sp.paper_subplots(2, 2)
        >>> sp.adjust_subplots(fig, hspace=0.4, wspace=0.4)
    """
    fig.subplots_adjust(
        hspace=hspace, wspace=wspace,
        top=top, bottom=bottom, left=left, right=right,
    )


def suggest_figsize(
    n_items: int,
    item_width: float = 0.5,
    min_width: float = 4.0,
    max_width: float = 10.0,
    height_ratio: float = 0.7,
) -> Tuple[float, float]:
    """
    根据数据量建议合适的图形尺寸

    参数:
        n_items      : 数据项数量（如柱状图的柱子数）
        item_width   : 每项占用的宽度（英寸）
        min_width    : 最小宽度
        max_width    : 最大宽度
        height_ratio : 高宽比

    返回:
        (width, height) 建议尺寸

    示例:
        >>> # 20 个柱子的柱状图
        >>> figsize = sp.suggest_figsize(20, item_width=0.4)
        >>> fig, ax = plt.subplots(figsize=figsize)
    """
    width = max(min_width, min(max_width, n_items * item_width))
    height = width * height_ratio
    return width, height


def check_color_contrast(
    bg_color: str,
    fg_color: str,
    threshold: float = 4.5,
) -> Tuple[bool, float]:
    """
    检查颜色对比度是否符合 WCAG 标准

    参数:
        bg_color : 背景色 HEX
        fg_color : 前景色 HEX
        threshold: 对比度阈值，默认 4.5（AA 级标准）

    返回:
        (是否通过, 对比度值)

    示例:
        >>> passed, ratio = sp.check_color_contrast("#FFFFFF", "#000000")
        >>> print(f"对比度: {ratio:.2f}, 通过: {passed}")
    """
    def _luminance(hex_color: str) -> float:
        h = hex_color.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

        # 转换为 sRGB
        r, g, b = r / 255.0, g / 255.0, b / 255.0

        # 应用 gamma 校正
        def _correct(c: float) -> float:
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        r, g, b = _correct(r), _correct(g), _correct(b)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    L1 = _luminance(bg_color)
    L2 = _luminance(fg_color)

    lighter = max(L1, L2)
    darker = min(L1, L2)

    contrast = (lighter + 0.05) / (darker + 0.05)
    passed = contrast >= threshold

    return passed, contrast


__all__ = [
    "auto_rotate_labels",
    "smart_legend",
    "optimize_layout",
    "adjust_subplots",
    "suggest_figsize",
    "check_color_contrast",
]
