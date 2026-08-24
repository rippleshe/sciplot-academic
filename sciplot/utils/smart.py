"""
智能辅助工具 — 自动布局优化、智能图例、标签旋转等
"""

from __future__ import annotations

from typing import Any, List, Mapping, Optional, Tuple, cast
import math
import re

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

_HEX_PATTERN = re.compile(r"^[0-9A-Fa-f]{3}$|^[0-9A-Fa-f]{6}$")
_REDUNDANT_LINESTYLES = ("-", "--", "-.", ":")


def _series_line_kwargs(
    kwargs: Mapping[str, Any],
    index: int,
    color_count: int,
    *,
    force_cycle: bool = False,
) -> dict[str, Any]:
    """为多系列线图补充可辨识线型，同时尊重用户显式样式。

    默认只有颜色循环耗尽后才切换线型；``force_cycle=True`` 时每个系列都
    循环线型。若用户已经传入 ``linestyle`` / ``ls``，则完全保留用户设置。
    """
    result = dict(kwargs)
    if "linestyle" in result or "ls" in result:
        return result
    if color_count <= 0:
        raise ValueError(f"color_count 必须是正整数，实际值: {color_count!r}")

    style_index = index if force_cycle else index // color_count
    result["linestyle"] = _REDUNDANT_LINESTYLES[style_index % len(_REDUNDANT_LINESTYLES)]
    return result


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
    if axis not in {"x", "y"}:
        raise ValueError(f"axis 必须是 'x' 或 'y'，实际值: {axis!r}")

    renderer = None
    try:
        ax.figure.canvas.draw()
        get_renderer = getattr(ax.figure.canvas, "get_renderer", None)
        if callable(get_renderer):
            renderer = get_renderer()
    except Exception:
        # 无显示后端或特殊环境下 draw 可能失败，降级到旧的字符数启发式。
        renderer = None

    def _overlaps(labels: list) -> bool:
        if renderer is None:
            return False
        visible = [
            label for label in labels
            if label.get_visible() and bool(label.get_text())
        ]
        if len(visible) < 2:
            return False
        boxes = [label.get_window_extent(renderer=renderer) for label in visible]
        return any(a.overlaps(b) for a, b in zip(boxes, boxes[1:]))

    if axis == "x":
        labels = ax.get_xticklabels()
        tick_labels = [t.get_text() for t in labels]

        heuristic = (
            len(tick_labels) > max_labels
            or any(len(str(l)) > threshold for l in tick_labels)
        )
        # renderer 可用时只在“真的碰撞”时旋转；字符数只作为无渲染环境的回退。
        should_rotate = _overlaps(labels) if renderer is not None else heuristic

        if should_rotate:
            plt.setp(ax.get_xticklabels(), rotation=rotation, ha="right")
    else:
        labels = ax.get_yticklabels()
        tick_labels = [t.get_text() for t in labels]

        heuristic = (
            len(tick_labels) > max_labels
            or any(len(str(l)) > threshold for l in tick_labels)
        )
        should_rotate = _overlaps(labels) if renderer is not None else heuristic

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

    if ncols is not None:
        if not isinstance(ncols, int) or ncols <= 0:
            raise ValueError(f"ncols 必须是正整数或 None，实际值: {ncols!r}")

    # 自动计算列数
    if ncols is None:
        # 每列约 4 项：5–8 项两列、9–12 项三列；最多 4 列避免横向过宽。
        ncols = min(4, max(1, math.ceil(len(handles) / 4)))

    if outside:
        ax.legend(
            handles, labels,
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            ncol=ncols,
        )
        return

    legend = ax.legend(handles, labels, loc=loc, ncol=ncols)

    # 极窄单栏中的大型 legend 不应横穿数据区。仅对默认 loc="best" 自动介入；
    # 用户显式指定位置时保持原意。通过真实 renderer bbox 判断，而不是按字符数猜。
    get_figwidth = getattr(ax.figure, "get_figwidth", None)
    if loc != "best" or len(handles) < 9 or not callable(get_figwidth):
        return
    if float(get_figwidth()) > 4.5:
        return
    try:
        ax.figure.canvas.draw()
        get_renderer = getattr(ax.figure.canvas, "get_renderer", None)
        if not callable(get_renderer):
            return
        renderer = get_renderer()
        legend_box = legend.get_window_extent(renderer=renderer)
        axes_box = ax.get_window_extent(renderer=renderer)
    except Exception:
        return

    text_boxes = [text.get_window_extent(renderer=renderer) for text in legend.get_texts()]
    max_text_width = max((box.width for box in text_boxes), default=0.0)
    dense_inside = (
        legend_box.width >= axes_box.width * 0.85
        or (
            legend_box.height >= axes_box.height * 0.22
            and max_text_width >= axes_box.width * 0.28
        )
    )
    if not dense_inside:
        return

    # 图外下方比图外右侧更适合单栏：保持正文宽度，用纵向空间换可读性。
    # 从至多两列开始试放，必要时降到单列，直到真实宽度能装进主轴。
    for candidate_ncols in range(min(2, ncols), 0, -1):
        legend = ax.legend(
            handles,
            labels,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.12),
            borderaxespad=0.0,
            ncol=candidate_ncols,
        )
        try:
            ax.figure.canvas.draw()
            legend_box = legend.get_window_extent(renderer=renderer)
        except Exception:
            break
        if legend_box.width <= axes_box.width * 1.05:
            break


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
    if not isinstance(n_items, int) or n_items < 0:
        raise ValueError(f"n_items 必须是非负整数，实际值: {n_items!r}")
    if item_width <= 0:
        raise ValueError(f"item_width 必须为正数，实际值: {item_width!r}")
    if min_width <= 0 or max_width <= 0:
        raise ValueError(
            f"min_width 和 max_width 必须为正数，实际值: min_width={min_width!r}, max_width={max_width!r}"
        )
    if max_width < min_width:
        raise ValueError(
            f"max_width 必须大于等于 min_width，实际值: min_width={min_width!r}, max_width={max_width!r}"
        )
    if height_ratio <= 0:
        raise ValueError(f"height_ratio 必须为正数，实际值: {height_ratio!r}")

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
    if not isinstance(threshold, (int, float)) or not math.isfinite(float(threshold)) or threshold <= 0:
        raise ValueError(f"threshold 必须是正数，实际值: {threshold!r}")

    def _normalize_hex(hex_color: str, name: str) -> str:
        if not isinstance(hex_color, str) or not hex_color.strip():
            raise ValueError(f"{name} 必须是 HEX 颜色字符串，实际值: {hex_color!r}")
        h = hex_color.strip().lstrip("#")
        if not _HEX_PATTERN.fullmatch(h):
            raise ValueError(f"{name} 不是合法 HEX 颜色: {hex_color!r}")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return h

    def _luminance(hex_color: str) -> float:
        h = _normalize_hex(hex_color, "颜色")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

        # 转换为 sRGB
        rf, gf, bf = r / 255.0, g / 255.0, b / 255.0

        # 应用 gamma 校正
        def _correct(c: float) -> float:
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        r, g, b = _correct(rf), _correct(gf), _correct(bf)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    bg_hex = _normalize_hex(bg_color, "bg_color")
    fg_hex = _normalize_hex(fg_color, "fg_color")
    L1 = _luminance(bg_hex)
    L2 = _luminance(fg_hex)

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
