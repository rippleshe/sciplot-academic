"""
占比构成图表 — 矩形树图、环形图
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np

from sciplot._core.utils import cycle_color, get_cycle_colors, new_styled_figure
from sciplot._core.result import PlotResult

# ============================================================================
# 矩形树图（Treemap，Part-of-a-whole 家族）
# ============================================================================

def _treemap_layout(
    sizes: List[float],
    x: float,
    y: float,
    w: float,
    h: float,
) -> List[Tuple[float, float, float, float]]:
    """Bruls 等 (2000) squarify 算法：返回与 sizes 同序的 (x, y, w, h) 列表。"""
    if not sizes:
        return []
    total = sum(sizes)
    if total <= 0:
        raise ValueError("sizes 之和必须大于 0")
    scaled = [s / total * (w * h) for s in sizes]
    rects: List[Tuple[float, float, float, float]] = []

    def _worst_ratio(row: List[float], length: float) -> float:
        s = sum(row)
        if s <= 0:
            return float("inf")
        s2 = sum(v * v for v in row)
        return max(length * length * s2 / (s * s * s),
                   (s * s * s) / (length * length * s2))

    def _layout(items: List[float], cx: float, cy: float, cw: float, ch: float) -> None:
        if not items:
            return
        if len(items) == 1:
            rects.append((cx, cy, cw, ch))
            return
        if cw >= ch:
            # 水平行放置
            row = [items[0]]
            i = 1
            while i < len(items):
                if _worst_ratio(row + [items[i]], cw) <= _worst_ratio(row, cw):
                    row.append(items[i])
                    i += 1
                else:
                    break
            row_h = sum(row) / cw
            rx = cx
            for v in row:
                rects.append((rx, cy, v / row_h, row_h))
                rx += v / row_h
            _layout(items[i:], cx, cy + row_h, cw, ch - row_h)
        else:
            # 垂直列放置
            col = [items[0]]
            i = 1
            while i < len(items):
                if _worst_ratio(col + [items[i]], ch) <= _worst_ratio(col, ch):
                    col.append(items[i])
                    i += 1
                else:
                    break
            col_w = sum(col) / ch
            cy2 = cy
            for v in col:
                rects.append((cx, cy2, col_w, v / col_w))
                cy2 += v / col_w
            _layout(items[i:], cx + col_w, cy, cw - col_w, ch)

    _layout(scaled, x, y, w, h)
    return rects


def plot_treemap(
    categories: List[str],
    values: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    colors: Optional[Sequence[str]] = None,
    show_values: bool = True,
    fmt: str = ".0f",
    min_font: float = 6.0,
    max_font: float = 16.0,
    border_color: str = "white",
    border_width: float = 1.2,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制矩形树图（Treemap，面积编码占比）。

    纯 matplotlib 实现 squarify 算法，无额外依赖。矩形面积正比于数值，
    颜色默认取当前配色循环，文字字号随面积自适应。

    参数:
        categories : 类别名列表
        values     : 数值（非负，和必须大于 0）
        colors     : 颜色列表（与类别等长）；默认取当前配色循环
        show_values: 是否在矩形内显示数值
        fmt        : 数值格式
        min_font/max_font: 文字字号下限/上限（面积过小的矩形不显示文字）

    示例:
        >>> fig, ax = sp.plot_treemap(
        ...     ["A", "B", "C", "D"], [40, 30, 20, 10],
        ... )
    """
    from matplotlib.patches import Rectangle

    cat_arr = list(categories)
    val_arr = np.asarray(values, dtype=float).ravel()
    if len(cat_arr) != len(val_arr):
        raise ValueError(
            f"categories 长度 ({len(cat_arr)}) 与 values 长度 ({len(val_arr)}) 不一致"
        )
    if len(cat_arr) == 0:
        raise ValueError("categories/values 不能为空")
    if not np.all(np.isfinite(val_arr)):
        raise ValueError("values 不能包含 NaN 或 Inf")
    if np.any(val_arr < 0):
        raise ValueError("values 不能包含负值")
    if float(val_arr.sum()) <= 0:
        raise ValueError("values 之和必须大于 0")

    if colors is not None:
        if len(colors) != len(cat_arr):
            raise ValueError(
                f"colors 长度 ({len(colors)}) 与 categories 长度 ({len(cat_arr)}) 不一致"
            )
        color_list = list(colors)
    else:
        cycle = get_cycle_colors()
        color_list = [cycle_color(cycle, i) for i in range(len(cat_arr))]

    rects = _treemap_layout(list(val_arr), 0.0, 0.0, 1.0, 1.0)

    fig, ax = new_styled_figure(venue, palette, lang)

    # ── 矩形 ──
    for (rx, ry, rw, rh), c, v, cat in zip(rects, color_list, val_arr, cat_arr):
        ax.add_patch(Rectangle(
            (rx, ry), rw, rh,
            facecolor=c, edgecolor=border_color,
            linewidth=border_width, zorder=1,
        ))
        # 文字：字号随矩形尺寸自适应（类别名占宽约 30%，数值行更小）
        if show_values and rw > 0.04 and rh > 0.03:
            label_txt = f"{cat}"
            fs_label = min(max_font, max(min_font, rw * 0.30 / max(1.0, len(label_txt))))
            if fs_label >= min_font:
                y_top = ry + rh / 2 + (0.012 if rh > 0.07 else 0.0)
                ax.text(rx + rw / 2, y_top, label_txt,
                        ha="center", va="center", fontsize=fs_label,
                        color="white", fontweight="bold", zorder=3)
            if rh > 0.06:
                fs_val = max(min_font - 1.0, fs_label - 2.0)
                ax.text(rx + rw / 2, ry + rh / 2 - 0.014, f"{v:{fmt}}",
                        ha="center", va="center", fontsize=fs_val,
                        color="white", alpha=0.9, zorder=3)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})

# ============================================================================
# 环形图（Donut，Part-of-a-whole 家族）
# ============================================================================

def plot_donut(
    categories: List[str],
    values: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    colors: Optional[Sequence[str]] = None,
    hole_ratio: float = 0.6,
    show_values: bool = True,
    fmt: str = ".1f",
    show_percent: bool = True,
    percent_fmt: str = ".1f",
    start_angle: float = 90.0,
    label_radius: float = 1.08,
    center_text: Optional[str] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制环形图（Donut Chart，占比构成）。

    饼图的变体：中心挖空形成环形，常被 Nature 风格图表用于
    “整体构成 + 高亮关键份额”。纯 matplotlib 实现。

    参数:
        categories   : 类别名列表
        values       : 数值（非负，和必须大于 0）
        colors       : 颜色列表（与类别等长）；默认取当前配色循环
        hole_ratio   : 中心空洞占比（0~1），越大环越细
        show_values  : 是否在环内显示数值
        show_percent : 是否在类别标签后附百分比
        start_angle  : 起始角度（度，默认 90 从正上方开始）
        label_radius : 类别标签的半径位置
        center_text  : 环中心显示的文字（如总和）；None 不显示

    示例:
        >>> fig, ax = sp.plot_donut(
        ...     ["A", "B", "C"], [55, 30, 15],
        ...     center_text="100",
        ... )
    """
    cat_arr = list(categories)
    val_arr = np.asarray(values, dtype=float).ravel()
    if len(cat_arr) != len(val_arr):
        raise ValueError(
            f"categories 长度 ({len(cat_arr)}) 与 values 长度 ({len(val_arr)}) 不一致"
        )
    if len(cat_arr) == 0:
        raise ValueError("categories/values 不能为空")
    if not np.all(np.isfinite(val_arr)):
        raise ValueError("values 不能包含 NaN 或 Inf")
    if np.any(val_arr < 0):
        raise ValueError("values 不能包含负值")
    if float(val_arr.sum()) <= 0:
        raise ValueError("values 之和必须大于 0")
    if not (0.0 < hole_ratio < 1.0):
        raise ValueError(f"hole_ratio 必须在 (0, 1) 范围内，实际值: {hole_ratio!r}")

    if colors is not None:
        if len(colors) != len(cat_arr):
            raise ValueError(
                f"colors 长度 ({len(colors)}) 与 categories 长度 ({len(cat_arr)}) 不一致"
            )
        color_list = list(colors)
    else:
        cycle = get_cycle_colors()
        color_list = [cycle_color(cycle, i) for i in range(len(cat_arr))]

    fig, ax = new_styled_figure(venue, palette, lang)

    total = float(val_arr.sum())

    wedges, *_ = ax.pie(
        val_arr,
        colors=color_list,
        startangle=start_angle,
        wedgeprops=dict(width=1.0 - hole_ratio, edgecolor="white", linewidth=1.5),
        labels=None,
        **kwargs,
    )
    for w in wedges:
        w.set_zorder(2)

    # 数值放环内中部（扇区角度过小时跳过，避免文字溢出扇区）
    if show_values:
        fs = max(7, plt.rcParams.get("font.size", 9) - 1)
        for w, v in zip(wedges, val_arr):
            arc_deg = abs(w.theta2 - w.theta1)
            if arc_deg < 22.0:
                continue  # 过窄扇区不写数值，避免溢出
            ang = np.deg2rad((w.theta1 + w.theta2) / 2)
            r = 1.0 - hole_ratio / 2
            ax.text(r * np.cos(ang), r * np.sin(ang), f"{v:{fmt}}",
                    ha="center", va="center", fontsize=fs,
                    color="white", fontweight="bold", zorder=5)

    # 外圈标签：类别名 + 可选百分比（避免与环内数值重叠）
    fs_label = max(7, plt.rcParams.get("font.size", 9) - 1)
    for w, cat, v in zip(wedges, cat_arr, val_arr):
        ang = np.deg2rad((w.theta1 + w.theta2) / 2)
        x = label_radius * np.cos(ang)
        y = label_radius * np.sin(ang)
        # 标签从环边向外延伸：右侧 ha=left，左侧 ha=right，
        # 并预留足够的画布余量避免文字被裁剪
        if np.cos(ang) >= 0:
            ha = "left"
            x = x + 0.02
        else:
            ha = "right"
            x = x - 0.02
        va = "bottom" if y >= 0 else "top"
        if show_percent:
            pct = v / total * 100.0
            label_txt = f"{cat}  {pct:{percent_fmt}}%"
        else:
            label_txt = cat
        ax.text(x, y, label_txt, ha=ha, va=va, fontsize=fs_label, zorder=5)

    # 环中心文字（如总和/主指标）
    if center_text is not None:
        fs_center = max(11, plt.rcParams.get("font.size", 9) + 3)
        ax.text(0, 0, center_text, ha="center", va="center",
                fontsize=fs_center, fontweight="bold", color="#333333", zorder=6)

    ax.set_aspect("equal")
    margin = label_radius + 0.6  # 为外圈标签预留文字空间
    ax.set_xlim(-margin, margin)
    ax.set_ylim(-margin, margin)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})

