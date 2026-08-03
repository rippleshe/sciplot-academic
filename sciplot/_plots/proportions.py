"""
占比构成图表 — 矩形树图、环形图
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np

from sciplot._core.utils import cycle_color, get_cycle_colors, new_styled_figure, relative_fontsize
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
        # 默认配色：单色系明度渐变（面积与颜色双编码，有序且美观）
        # 数值越大颜色越深，避免多色循环造成的杂乱感
        vmin = float(np.min(val_arr))
        vmax = float(np.max(val_arr))
        span = vmax - vmin
        if span <= 0:
            span = 1.0
        from sciplot.utils import darken_color, lighten_color

        base = get_cycle_colors()[0]
        color_list = []
        for v in val_arr:
            frac = (float(v) - vmin) / span  # 0=最浅, 1=最深
            # 浅端用亮化 35%，深端用加深 25%，形成平滑梯度
            if frac < 0.5:
                color_list.append(lighten_color(base, 0.35 - 0.5 * frac))
            else:
                color_list.append(darken_color(base, 0.5 * (frac - 0.5)))

    rects = _treemap_layout(list(val_arr), 0.0, 0.0, 1.0, 1.0)

    fig, ax = new_styled_figure(venue, palette, lang)

    total_val = float(val_arr.sum())

    # ── 矩形（先画底色，再画内描边增强层次） ──

    for (rx, ry, rw, rh), c, v, cat in zip(rects, color_list, val_arr, cat_arr):
        ax.add_patch(Rectangle(
            (rx, ry), rw, rh,
            facecolor=c, edgecolor="white",
            linewidth=1.6, zorder=1,
        ))
        # 文字：字号随矩形尺寸自适应（类别名 + 数值 + 百分比）
        if show_values and rw > 0.05 and rh > 0.035:
            label_txt = str(cat)
            fs_label = min(max_font, max(min_font, rw * 0.34 / max(1.0, len(label_txt))))
            if fs_label >= min_font:
                y_top = ry + rh / 2 + (0.014 if rh > 0.08 else 0.0)
                ax.text(rx + rw / 2, y_top, label_txt,
                        ha="center", va="center", fontsize=fs_label,
                        color="white", fontweight="bold", zorder=3)
            if rh > 0.07:
                pct = v / total_val * 100.0
                fs_val = max(min_font - 1.0, fs_label - 1.5)
                ax.text(rx + rw / 2, ry + rh / 2 - 0.016, f"{v:{fmt}}  ({pct:.0f}%)",
                        ha="center", va="center", fontsize=fs_val,
                        color="white", alpha=0.92, zorder=3)

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


# ============================================================================
# 旭日图（Sunburst，Part-of-a-whole 家族）
# ============================================================================

def plot_sunburst(
    labels: List[str],
    parents: List[Optional[str]],
    values: np.ndarray,
    title: str = "",
    colors: Optional[Sequence[str]] = None,
    show_labels: bool = True,
    label_min_angle: float = 8.0,
    ring_gap: float = 0.03,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制旭日图（Sunburst Chart，分层占比）

    同心环逐层展开层级占比：内环为顶层类别，外环为子类别，
    每段弧长正比于数值。适合展示“整体 → 分类 → 子类”的
    多级构成（如 门 → 纲 → 属 的分类学结构）。

    参数:
        labels  : 所有节点标签（含根节点，根为 "" 或自定义名）
        parents : 每个节点的父节点标签（根节点为 None）
        values  : 每个节点的数值（内部节点可为其子节点之和或任意值）
        colors  : 顶层类别颜色列表（按顶层节点顺序）；None 用配色循环
        show_labels: 是否在扇区显示标签
        label_min_angle: 扇区角度小于该值（度）时不显示标签
        ring_gap: 环间留白比例

    示例:
        >>> # 分类学结构：根 → 两门 → 六属
        >>> fig, ax = sp.plot_sunburst(
        ...     labels=["", "门A", "门B", "属A1", "属A2", "属B1", "属B2", "属B3"],
        ...     parents=[None, "", "", "门A", "门A", "门B", "门B", "门B"],
        ...     values=[100, 60, 40, 35, 25, 18, 12, 10],
        ... )
        >>> sp.save(fig, "sunburst")
    """
    lbl = [str(lb) for lb in labels]
    par = [None if p is None else str(p) for p in parents]
    val = np.asarray(values, dtype=float).ravel()

    n = len(lbl)
    if n == 0:
        raise ValueError("labels 不能为空")
    if len(par) != n or len(val) != n:
        raise ValueError("labels/parents/values 长度必须一致")
    if not np.all(np.isfinite(val)):
        raise ValueError("values 不能包含 NaN 或 Inf")
    if np.any(val < 0):
        raise ValueError("values 不能包含负值")

    # 构建父子索引映射
    index_of = {name: i for i, name in enumerate(lbl)}
    for i, p in enumerate(par):
        if p is not None and p not in index_of:
            raise ValueError(f"parents[{i}] '{p}' 不在 labels 中")

    children: Dict[int, List[int]] = {i: [] for i in range(n)}
    for i, p in enumerate(par):
        if p is not None:
            children[index_of[p]].append(i)

    # 计算深度（BFS）
    depth = [0] * n
    roots = [i for i in range(n) if par[i] is None]
    if not roots:
        raise ValueError("至少需要一个根节点（parents 为 None）")
    queue = list(roots)
    while queue:
        node = queue.pop(0)
        for c in children[node]:
            depth[c] = depth[node] + 1
            queue.append(c)
    max_depth = max(depth)

    # ── 配色：第一层分支分配色相，层内按深度明度渐变 ──
    from sciplot.utils import darken_color, lighten_color

    # 第一层（深度 1）为着色单元；若根直接是叶子则根自身着色
    level1 = [i for i in range(n) if depth[i] == 1]
    if not level1:
        level1 = list(roots)

    cycle = get_cycle_colors()
    if colors is None:
        branch_colors = [cycle_color(cycle, i) for i in range(len(level1))]
    else:
        if len(colors) != len(level1):
            raise ValueError(
                f"colors 长度 ({len(colors)}) 与第一层节点数 ({len(level1)}) 不一致"
            )
        branch_colors = list(colors)

    # 每个节点 → 所属第一层分支的索引
    branch_of: Dict[int, int] = {}
    for i in range(n):
        if depth[i] == 0:
            branch_of[i] = -1  # 根节点单独处理
            continue
        if depth[i] == 1:
            branch_of[i] = level1.index(i)
        else:
            # 向上追溯至深度 1
            anc = i
            while depth[anc] > 1:
                anc = index_of[par[anc]]  # type: ignore[index]
            branch_of[i] = level1.index(anc)

    node_color: Dict[int, str] = {}
    for i in range(n):
        if depth[i] == 0:
            node_color[i] = "#9AA5B1"  # 根节点中性灰
        else:
            base = branch_colors[branch_of[i]]
            # 每深一层加深 14%；第一层用亮色，叶子最深
            if depth[i] <= 1:
                node_color[i] = lighten_color(base, 0.10)
            else:
                node_color[i] = darken_color(base, 0.14 * (depth[i] - 1))

    fig, ax = new_styled_figure(venue, palette, lang)

    # 递归绘制扇区（从根开始，按数值分配角度）
    ring_width = 1.0 / (max_depth + 1) if max_depth > 0 else 1.0

    from matplotlib.patches import Wedge

    def _draw_node(idx: int, theta0: float, theta1: float, depth_idx: int) -> None:
        """绘制节点扇区（Wedge patch），递归绘制子节点。

        theta0/theta1 为弧度，从 12 点方向顺时针展开。
        根节点（depth 0）不绘制扇区，中心留白。
        """
        r_outer = 1.0 - depth_idx * ring_width
        r_inner = max(0.0, r_outer - ring_width + ring_gap)
        if depth_idx > 0 and theta1 - theta0 > 1e-9 and r_outer - r_inner > 1e-9:
            # 弧度(从12点顺时针) → 度(matplotlib 从+x 逆时针)
            deg0 = 90.0 - np.degrees(theta0)
            deg1 = 90.0 - np.degrees(theta1)
            w = Wedge((0.0, 0.0), r_outer, deg1, deg0,
                      width=r_outer - r_inner,
                      facecolor=node_color[idx], edgecolor="white",
                      linewidth=1.0, zorder=2)
            ax.add_patch(w)

            # 扇区标签（角度足够大才显示）
            if show_labels and np.degrees(theta1 - theta0) >= label_min_angle:
                mid = (theta0 + theta1) / 2
                r_mid = (r_inner + r_outer) / 2
                fs = relative_fontsize(-2, floor=6)
                # 12点顺时针坐标 → 笛卡尔
                x_t = r_mid * np.sin(mid)
                y_t = r_mid * np.cos(mid)
                ax.text(x_t, y_t, lbl[idx], ha="center", va="center",
                        fontsize=fs, color="white", fontweight="bold", zorder=5)

        total_child = sum(val[c] for c in children[idx])
        if total_child <= 0:
            return
        cursor = theta0
        # 子节点按出现顺序分配角度
        for c in children[idx]:
            frac = float(val[c]) / total_child
            child_span = (theta1 - theta0) * frac
            _draw_node(c, cursor, cursor + child_span, depth_idx + 1)
            cursor += child_span

    total_root = sum(float(val[r]) for r in roots)
    if total_root <= 0:
        raise ValueError("根节点 values 之和必须大于 0")
    cursor = 0.0
    for r in roots:
        frac = float(val[r]) / total_root
        _draw_node(r, cursor, cursor + 2 * np.pi * frac, 0)
        cursor += 2 * np.pi * frac

    ax.set_aspect("equal")
    ax.set_xlim(-1.08, 1.08)
    ax.set_ylim(-1.08, 1.08)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})

