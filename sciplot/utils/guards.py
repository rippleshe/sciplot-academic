"""
视觉下限守卫与出版级渲染润色工具。

提供坐标轴净化（去除分类轴多余次刻度与冗余脊线）、标签防重叠排斥、
象限自适应角标定位、色块柔填深边润色，以及保存/审计前图形质量自检。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator, NullLocator
from matplotlib.transforms import Bbox

from sciplot.utils import darken_color


def _is_dark_axes(ax: Axes) -> bool:
    """判断当前坐标轴是否处于深色背景主题下。"""
    from matplotlib.colors import to_rgb

    try:
        r, g, b = to_rgb(ax.get_facecolor())
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        return lum < 0.45
    except Exception:
        return False


def _ensure_drawn_renderer(fig: Figure) -> Optional[Any]:
    """安全触发一次画布渲染以获取真实文本与元素边界框。"""
    canvas = getattr(fig, "canvas", None)
    if canvas is None:
        return None
    try:
        canvas.draw()
        return canvas.get_renderer()
    except Exception:
        return None


def polish_axis(
    ax: Axes,
    *,
    categorical_axis: Optional[str] = None,
    clean_spines: bool = True,
    grid: Union[bool, str, None] = None,
    grid_alpha: float = 0.24,
    max_num_ticks: Optional[int] = None,
    spine_color: Optional[str] = None,
) -> Axes:
    """净化并润色坐标轴刻度、边框与背景参考网格。

    重要设计：仅调整当前 ``ax`` 实例，不改动全局 ``plt.rcParams``，
    既能彻底消除分类柱状图/箱线图/小提琴图上的锯齿状次刻度与冗余边框，
    又能保持投稿场景的全局样式契约稳定。

    参数:
        ax              : 目标 matplotlib Axes
        categorical_axis: 需清除次刻度的分类轴，``'x'`` | ``'y'`` | ``'both'`` | ``None``
        clean_spines    : True 时隐藏顶部和右侧边框及对应刻度（L 形开放框）
        grid            : 启用背景虚线辅助网格，``'x'`` | ``'y'`` | ``'both'`` | ``True`` | ``False`` | ``None``
        grid_alpha      : 网格透明度，默认 0.24
        max_num_ticks   : 数值轴最大主刻度数量（防止刻度挤成黑块）
        spine_color     : 可选自定义边框线颜色；None 时依深/浅背景自适应
    """
    is_dark = _is_dark_axes(ax)
    resolved_spine = spine_color or ("#AEB6BF" if is_dark else "#2F3542")
    resolved_grid = "#FFFFFF" if is_dark else "#B8C0CC"
    resolved_grid_alpha = min(grid_alpha, 0.16) if is_dark else grid_alpha

    # 1. 清除分类轴上的次刻度（消除柱间锯齿线）及对侧多余刻度
    if categorical_axis in {"x", "both"}:
        ax.xaxis.set_minor_locator(NullLocator())
        ax.tick_params(axis="x", which="both", top=False)
    if categorical_axis in {"y", "both"}:
        ax.yaxis.set_minor_locator(NullLocator())
        ax.tick_params(axis="y", which="both", right=False)

    # 2. L 形开放框：隐藏 top/right 脊线并同步关闭对侧刻度
    if clean_spines:
        for hidden in ("top", "right"):
            if hidden in ax.spines:
                ax.spines[hidden].set_visible(False)
        ax.tick_params(axis="x", which="both", top=False)
        ax.tick_params(axis="y", which="both", right=False)

    for visible in ("left", "bottom", "top", "right"):
        if visible in ax.spines and ax.spines[visible].get_visible():
            ax.spines[visible].set_edgecolor(resolved_spine)

    # 3. 限制过密数值主刻度（保留分类轴 FixedLocator 不动）
    if max_num_ticks is not None and max_num_ticks >= 3:
        if categorical_axis not in {"x", "both"}:
            ax.xaxis.set_major_locator(MaxNLocator(nbins=max_num_ticks, prune=None))
        if categorical_axis not in {"y", "both"}:
            ax.yaxis.set_major_locator(MaxNLocator(nbins=max_num_ticks, prune=None))

    # 4. 轻量级背景虚线参考网
    if grid:
        grid_axis = "both" if grid is True else str(grid)
        if grid_axis in {"x", "y", "both"}:
            ax.set_axisbelow(True)
            ax.grid(
                True,
                which="major",
                axis=grid_axis,
                linestyle="--",
                linewidth=0.55,
                alpha=resolved_grid_alpha,
                color=resolved_grid,
            )

    return ax


def style_patch_edges(
    patches: Sequence[Any],
    colors: Sequence[str],
    *,
    fill_alpha: float = 0.84,
    darken_amount: float = 0.26,
    linewidth: float = 0.75,
) -> None:
    """为填充多边形/柱条赋予“柔填充 + 深轮廓”的层次感。"""
    from matplotlib.colors import to_hex

    if not patches or not colors:
        return
    for i, patch in enumerate(patches):
        base = colors[i % len(colors)]
        try:
            edge = darken_color(to_hex(base), amount=darken_amount)
        except Exception:
            edge = base
        if hasattr(patch, "set_facecolor"):
            patch.set_facecolor(base)
        if hasattr(patch, "set_alpha"):
            patch.set_alpha(fill_alpha)
        if hasattr(patch, "set_edgecolor"):
            patch.set_edgecolor(edge)
        if hasattr(patch, "set_linewidth"):
            patch.set_linewidth(linewidth)


def truncate_tick_labels(
    ax: Axes,
    axis: str = "y",
    max_len: int = 24,
    suffix: str = "...",
) -> None:
    """截断过长的分类刻度文字，防止挤压绘图区空间。"""
    if max_len < 4:
        return
    if axis == "x":
        labels = [t.get_text() for t in ax.get_xticklabels()]
        trimmed = [
            lbl if len(lbl) <= max_len else lbl[: max_len - len(suffix)] + suffix
            for lbl in labels
        ]
        if trimmed != labels:
            ax.set_xticklabels(trimmed)
    elif axis == "y":
        labels = [t.get_text() for t in ax.get_yticklabels()]
        trimmed = [
            lbl if len(lbl) <= max_len else lbl[: max_len - len(suffix)] + suffix
            for lbl in labels
        ]
        if trimmed != labels:
            ax.set_yticklabels(trimmed)


def pick_best_corner(
    ax: Axes,
    x_data: Sequence[float],
    y_data: Sequence[float],
    *,
    prefer: Sequence[str] = ("upper left", "lower right", "upper right", "lower left"),
) -> str:
    """在数据点最稀疏的象限中选择角标或图例位置。"""
    x_arr = np.asarray(x_data, dtype=float)
    y_arr = np.asarray(y_data, dtype=float)
    valid = np.isfinite(x_arr) & np.isfinite(y_arr)
    if not np.any(valid):
        return prefer[0]
    xv = x_arr[valid]
    yv = y_arr[valid]
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    x_span = max(abs(x_max - x_min), 1e-12)
    y_span = max(abs(y_max - y_min), 1e-12)
    nx = (xv - x_min) / x_span
    ny = (yv - y_min) / y_span

    corner_boxes = {
        "upper left": (0.0, 0.38, 0.65, 1.0),
        "upper right": (0.62, 1.0, 0.65, 1.0),
        "lower left": (0.0, 0.38, 0.0, 0.35),
        "lower right": (0.62, 1.0, 0.0, 0.35),
    }

    best_loc = prefer[0]
    best_count = float("inf")
    for order_idx, loc in enumerate(prefer):
        x0, x1, y0, y1 = corner_boxes[loc]
        hits = int(np.sum((nx >= x0) & (nx <= x1) & (ny >= y0) & (ny <= y1)))
        # 平局时保留 prefer 的优先级微调
        score = hits + order_idx * 0.01
        if score < best_count:
            best_count = score
            best_loc = loc
    return best_loc


def smart_labels(
    ax: Axes,
    texts: Sequence[Any],
    *,
    anchor_xy: Optional[Sequence[Tuple[float, float]]] = None,
    add_connectors: bool = True,
    connector_color: str = "#666666",
    max_iter: int = 80,
    pad_px: float = 4.0,
) -> None:
    """基于边界框排斥的轻量级标注防重叠调整。

    通过画布像素坐标系对重叠的 ``Text`` 对象执行迭代推开与轴内夹紧，
    当标签偏离锚点较远时可选绘制纤细引导线，彻底避免文字互相压盖。
    """
    if len(texts) <= 1 and anchor_xy is None:
        return
    renderer = _ensure_drawn_renderer(ax.figure)
    if renderer is None:
        return

    ax_bbox = ax.get_window_extent(renderer)
    if ax_bbox.width <= 1 or ax_bbox.height <= 1:
        return

    inv = ax.transData.inverted()
    orig_positions: List[Tuple[float, float]] = [
        (float(t.get_position()[0]), float(t.get_position()[1])) for t in texts
    ]

    # 若存在图例，将其纳入避让障碍区
    obstacle_boxes: List[Bbox] = []
    legend = ax.get_legend()
    if legend is not None:
        try:
            obstacle_boxes.append(legend.get_window_extent(renderer).padded(3.0))
        except Exception:
            pass

    for _ in range(max_iter):
        moved = False
        bboxes: List[Bbox] = []
        for t in texts:
            try:
                bboxes.append(t.get_window_extent(renderer).padded(pad_px * 0.5))
            except Exception:
                bboxes.append(Bbox.from_bounds(0, 0, 1, 1))

        # 文本间两两推开
        for i in range(len(texts)):
            bi = bboxes[i]
            dx_acc, dy_acc = 0.0, 0.0
            for j in range(len(texts)):
                if i == j:
                    continue
                bj = bboxes[j]
                if bi.overlaps(bj):
                    moved = True
                    cx_i = 0.5 * (bi.x0 + bi.x1)
                    cy_i = 0.5 * (bi.y0 + bi.y1)
                    cx_j = 0.5 * (bj.x0 + bj.x1)
                    cy_j = 0.5 * (bj.y0 + bj.y1)
                    ox = min(bi.x1, bj.x1) - max(bi.x0, bj.x0)
                    oy = min(bi.y1, bj.y1) - max(bi.y0, bj.y0)
                    if oy <= ox * 1.4:
                        direction = 1.0 if cy_i >= cy_j else -1.0
                        dy_acc += direction * max(2.0, oy * 0.55)
                    else:
                        direction = 1.0 if cx_i >= cx_j else -1.0
                        dx_acc += direction * max(2.0, ox * 0.55)

            # 避开图例矩形
            for ob in obstacle_boxes:
                if bi.overlaps(ob):
                    moved = True
                    if bi.y0 < ob.y0:
                        dy_acc -= max(4.0, (bi.y1 - ob.y0) * 0.65)
                    else:
                        dx_acc += max(4.0, (ob.x1 - bi.x0) * 0.65)

            if dx_acc != 0.0 or dy_acc != 0.0:
                tx_d, ty_d = texts[i].get_position()
                px, py = ax.transData.transform((tx_d, ty_d))
                new_px = float(np.clip(
                    px + dx_acc,
                    ax_bbox.x0 + bi.width * 0.52,
                    ax_bbox.x1 - bi.width * 0.52,
                ))
                new_py = float(np.clip(
                    py + dy_acc,
                    ax_bbox.y0 + bi.height * 0.55,
                    ax_bbox.y1 - bi.height * 0.55,
                ))
                nx_d, ny_d = inv.transform((new_px, new_py))
                texts[i].set_position((float(nx_d), float(ny_d)))

        if not moved:
            break

    # 若文本偏离原始点较多，绘出细腻引导线
    if add_connectors:
        points = anchor_xy if anchor_xy is not None else orig_positions
        for idx, (text_artist, (ax_x, ax_y)) in enumerate(zip(texts, points)):
            tx_d, ty_d = text_artist.get_position()
            p_orig = ax.transData.transform((ax_x, ax_y))
            p_now = ax.transData.transform((tx_d, ty_d))
            dist_px = float(np.hypot(p_now[0] - p_orig[0], p_now[1] - p_orig[1]))
            if dist_px > 12.0:
                ax.annotate(
                    "",
                    xy=(ax_x, ax_y),
                    xytext=(tx_d, ty_d),
                    arrowprops={
                        "arrowstyle": "-",
                        "color": connector_color,
                        "lw": 0.65,
                        "alpha": 0.6,
                        "shrinkA": 2,
                        "shrinkB": 3,
                    },
                    zorder=max(1, int(text_artist.get_zorder()) - 1),
                )


def inspect_figure_guards(fig: Figure) -> List[str]:
    """对已绘制图形执行非破坏式视觉异常巡检，返回人类可读告警列表。

    巡检维度：
    1. 轴外越界 ``transAxes`` 文本（会导致 ``bbox_inches='tight'`` 撑大空白）。
    2. 非辅助轴上可能发生的大量文本遮挡重叠。
    """
    issues: List[str] = []
    renderer = _ensure_drawn_renderer(fig)
    if renderer is None:
        return issues

    for idx, ax in enumerate(fig.axes, start=1):
        if not ax.get_visible() or getattr(ax, "_sciplot_auxiliary", False):
            continue
        # 检查 axes 坐标系中严重越界的文本
        for txt in ax.texts:
            content = txt.get_text().strip()
            if not content:
                continue
            if txt.get_transform() == ax.transAxes:
                tx, ty = txt.get_position()
                if tx < -0.25 or tx > 1.25 or ty < -0.25 or ty > 1.25:
                    issues.append(
                        f"子图 #{idx} 含轴外越界文本 ({tx:.2f}, {ty:.2f}): {content!r}"
                    )

        # 检查 X 轴水平刻度标签碰撞
        try:
            xlabels = [
                lbl for lbl in ax.get_xticklabels()
                if lbl.get_visible() and lbl.get_text().strip()
                and abs(lbl.get_rotation()) < 5
            ]
            if len(xlabels) >= 6:
                boxes = [lbl.get_window_extent(renderer) for lbl in xlabels]
                boxes.sort(key=lambda b: b.x0)
                colliding = sum(
                    1 for i in range(len(boxes) - 1) if boxes[i].x1 > boxes[i + 1].x0 + 1.0
                )
                if colliding >= max(2, len(boxes) // 4):
                    issues.append(
                        f"子图 #{idx} X 轴有 {colliding} 处水平刻度标签疑似拥挤重叠，建议使用 auto_rotate_labels 或精简刻度"
                    )
        except Exception:
            pass

    return issues


__all__ = [
    "polish_axis",
    "style_patch_edges",
    "truncate_tick_labels",
    "pick_best_corner",
    "smart_labels",
    "inspect_figure_guards",
]
