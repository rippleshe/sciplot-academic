"""
布局管理 — 图形创建、子图排布、保存、面板标签
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec

from sciplot._core.style import VENUES


# ============================================================================
# 论文子图尺寸配置（单位：英寸）
# 键格式："{nrows}x{ncols}"
# ============================================================================

PAPER_LAYOUTS: Dict[str, Dict[str, Tuple[float, float]]] = {
    "thesis": {          # A4 版心宽 6.1in ≈ 15.5cm
        "1x1": (6.1, 4.3),
        "1x2": (6.1, 3.0),
        "1x3": (6.1, 2.4),
        "2x1": (4.0, 5.5),
        "2x2": (6.1, 5.0),
        "2x3": (6.1, 4.0),
        "3x1": (4.0, 7.5),
        "3x2": (6.1, 6.5),
    },
    "ieee": {            # 单栏 3.5in，双栏通栏 7.16in
        "1x1": (3.5, 3.0),
        "1x2": (3.5, 1.8),
        "1x3": (3.5, 1.4),
        "2x1": (3.5, 4.5),
        "2x2": (3.5, 3.0),
        "2x3": (3.5, 2.4),
        "wide-1x1": (7.16, 3.0),   # 双栏通栏图
        "wide-1x2": (7.16, 2.0),
        "wide-2x2": (7.16, 4.5),
    },
    "nature": {          # 单栏 3.5in (89mm)，双栏全图 7.0in (178mm)
        "1x1": (7.0, 5.0),
        "1x2": (7.0, 3.0),
        "1x3": (7.0, 2.4),
        "2x1": (3.5, 5.0),
        "2x2": (7.0, 5.0),
        "2x3": (7.0, 4.0),
        "single-1x1": (3.5, 2.8),  # 单栏图
    },
    "aps": {             # 单栏 3.4in (86mm)
        "1x1": (3.4, 2.8),
        "1x2": (3.4, 1.6),
        "2x1": (3.4, 4.5),
        "2x2": (3.4, 2.8),
        "wide-1x1": (7.0, 2.8),
    },
    "springer": {
        "1x1": (6.0, 4.5),
        "1x2": (6.0, 2.6),
        "2x2": (6.0, 4.2),
    },
    "presentation": {
        "1x1": (8.0, 5.5),
        "1x2": (8.0, 3.5),
        "2x2": (8.0, 5.0),
    },
}


# ============================================================================
# 基础图形创建
# ============================================================================

def new_figure(
    venue: str = "nature",
    figsize: Optional[Tuple[float, float]] = None,
    **kwargs: Any,
) -> Tuple[Figure, Axes]:
    """
    创建新图形，自动套用 venue 默认尺寸

    参数:
        venue  : 期刊预设（'nature' | 'ieee' | 'aps' | 'springer' | 'thesis' | 'presentation'）
        figsize: 自定义 (宽, 高) 英寸，传入则覆盖 venue 默认值
        **kwargs: 传递给 plt.subplots()

    返回:
        (Figure, Axes) 或 (Figure, ndarray[Axes])（当 kwargs 含 nrows/ncols 时）

    示例:
        >>> fig, ax = sp.new_figure("ieee")
        >>> fig, ax = sp.new_figure(figsize=(5.0, 3.5))
        >>> fig, axes = sp.new_figure("thesis", nrows=1, ncols=2, sharex=True)
    """
    if venue not in VENUES:
        raise ValueError(f"未知 venue '{venue}'，可用选项: {list(VENUES.keys())}")
    _, default_figsize, _ = VENUES[venue]
    size = figsize if figsize is not None else default_figsize
    return plt.subplots(figsize=size, **kwargs)


# ============================================================================
# 子图布局
# ============================================================================

def create_subplots(
    nrows: int = 1,
    ncols: int = 1,
    venue: str = "nature",
    sharex: bool = False,
    sharey: bool = False,
    **kwargs: Any,
) -> Tuple[Figure, Union[Axes, np.ndarray]]:
    """
    创建规则网格子图布局（尺寸自动按 venue 比例等比缩放）

    适合快速布局，不要求严格匹配论文版心宽度时使用。
    要求精确匹配版心请用 paper_subplots()。

    参数:
        nrows, ncols: 行列数
        venue       : 期刊预设（影响字号和比例）
        sharex/sharey: 是否共享坐标轴

    示例:
        >>> fig, axes = sp.create_subplots(2, 2, venue="ieee", sharex=True)
        >>> axes[0, 0].plot(x, y)
    """
    from sciplot._core.style import setup_style
    setup_style(venue)

    _, base_figsize, _ = VENUES[venue]
    figsize = (base_figsize[0] * ncols * 0.85, base_figsize[1] * nrows * 0.85)

    fig, axes = plt.subplots(
        nrows=nrows, ncols=ncols, figsize=figsize,
        sharex=sharex, sharey=sharey, **kwargs
    )
    _set_ticks_inward(axes)
    return fig, axes


def paper_subplots(
    nrows: int = 1,
    ncols: int = 1,
    venue: str = "thesis",
    figsize: Optional[Tuple[float, float]] = None,
    **kwargs: Any,
) -> Tuple[Figure, Union[Axes, np.ndarray]]:
    """
    创建严格符合论文版心宽度的子图布局（推荐）

    使用预标定的尺寸表（PAPER_LAYOUTS），确保插入 Word/LaTeX 时不变形。
    如果预设中没有对应布局，自动回退到等比例计算。

    参数:
        nrows, ncols: 行列数
        venue       : 论文类型（'thesis' | 'ieee' | 'nature' | 'aps' | 'springer'）
        figsize     : 覆盖预设尺寸（可选）

    示例:
        >>> # Word 论文 1×2 子图，精确匹配 A4 版心
        >>> fig, axes = sp.paper_subplots(1, 2, venue="thesis")
        >>> axes[0].plot(x, y1); axes[0].set_title("(a)")
        >>> axes[1].plot(x, y2); axes[1].set_title("(b)")
        >>> sp.save(fig, "thesis_1x2", formats=("png",), dpi=1200)

        >>> # IEEE 2×2 子图
        >>> fig, axes = sp.paper_subplots(2, 2, venue="ieee")
    """
    from sciplot._core.style import setup_style
    setup_style(venue)

    if figsize is not None:
        final_figsize = figsize
    else:
        layout_key = f"{nrows}x{ncols}"
        venue_layouts = PAPER_LAYOUTS.get(venue, {})
        final_figsize = venue_layouts.get(layout_key)
        if final_figsize is None:
            # 回退：基于 venue 默认尺寸等比缩放
            _, base_fs, _ = VENUES.get(venue, VENUES["nature"])
            final_figsize = (base_fs[0] * ncols * 0.85, base_fs[1] * nrows * 0.85)

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=final_figsize, **kwargs)
    _set_ticks_inward(axes)
    return fig, axes


def create_gridspec(
    nrows: int = 1,
    ncols: int = 1,
    venue: str = "nature",
    **kwargs: Any,
) -> Tuple[Figure, GridSpec]:
    """
    创建 GridSpec 不规则子图布局

    示例:
        >>> fig, gs = sp.create_gridspec(2, 3, venue="nature")
        >>> ax_top = fig.add_subplot(gs[0, :])   # 顶部通栏
        >>> ax_bl  = fig.add_subplot(gs[1, 0])
        >>> ax_bm  = fig.add_subplot(gs[1, 1])
        >>> ax_br  = fig.add_subplot(gs[1, 2])
        >>> for ax in fig.axes: ax.tick_params(direction="in")
        >>> sp.save(fig, "gridspec")
    """
    from sciplot._core.style import setup_style
    setup_style(venue)
    _, figsize, _ = VENUES[venue]
    fig = plt.figure(figsize=figsize)
    gs = GridSpec(nrows, ncols, figure=fig, **kwargs)
    return fig, gs


def create_twinx(ax: Axes) -> Axes:
    """
    创建共享 X 轴的副 Y 轴（双 Y 轴）

    示例:
        >>> fig, ax1 = sp.new_figure("ieee")
        >>> sp.setup_style("ieee", "pastel-2")
        >>> ax1.plot(x, temp, color="#cdb4db", label="温度")
        >>> ax1.set_ylabel("温度 (K)", color="#cdb4db")
        >>> ax2 = sp.create_twinx(ax1)
        >>> ax2.plot(x, pressure, color="#ffc8dd", label="压力")
        >>> ax2.set_ylabel("压力 (Pa)", color="#ffc8dd")
        >>> sp.save(fig, "dual_axis")
    """
    ax2 = ax.twinx()
    ax2.tick_params(direction="in")
    return ax2


# ============================================================================
# 面板标签
# ============================================================================

def add_panel_labels(
    axes: Union[Axes, np.ndarray, Sequence[Axes]],
    labels: Optional[List[str]] = None,
    style: str = "letter",
    x: float = -0.12,
    y: float = 1.05,
    fontsize: Optional[int] = None,
    fontweight: str = "bold",
) -> None:
    """
    为多子图自动添加面板标签（(a) (b) (c) 或 A B C 等）

    参数:
        axes     : 子图对象（单个 / ndarray / list）
        labels   : 自定义标签列表；为 None 时按 style 自动生成
        style    : 自动生成样式
                   'letter'     → (a) (b) (c) …（默认，最常见）
                   'LETTER'     → (A) (B) (C) …
                   'number'     → (1) (2) (3) …
                   'roman'      → (i) (ii) (iii) …
        x, y     : 标签位置（axes 坐标，x<0 表示轴框左侧）
        fontsize : 字号；为 None 则继承当前 rcParams
        fontweight: 字重，默认 'bold'

    示例:
        >>> fig, axes = sp.paper_subplots(1, 3, venue="thesis")
        >>> # ... 绘图 ...
        >>> sp.add_panel_labels(axes)   # 自动加 (a) (b) (c)
        >>> sp.save(fig, "fig_multi")

        >>> # 自定义标签
        >>> sp.add_panel_labels(axes, labels=["实验组", "对照组", "空白组"],
        ...                     x=-0.18, y=1.08)
    """
    _ROMAN = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x",
              "xi", "xii", "xiii", "xiv", "xv", "xvi"]
    _LETTER = list("abcdefghijklmnopqrstuvwxyz")

    # 展开 axes
    if isinstance(axes, np.ndarray):
        ax_list = list(axes.flat)
    elif isinstance(axes, Axes):
        ax_list = [axes]
    else:
        ax_list = list(axes)

    n = len(ax_list)

    if labels is not None:
        if len(labels) != n:
            raise ValueError(
                f"labels 长度 ({len(labels)}) 与子图数量 ({n}) 不匹配"
            )
        final_labels = labels
    else:
        if style == "letter":
            final_labels = [f"({_LETTER[i]})" for i in range(n)]
        elif style == "LETTER":
            final_labels = [f"({_LETTER[i].upper()})" for i in range(n)]
        elif style == "number":
            final_labels = [f"({i + 1})" for i in range(n)]
        elif style == "roman":
            final_labels = [f"({_ROMAN[i]})" for i in range(n)]
        else:
            raise ValueError(
                f"未知 style '{style}'，可选: 'letter' | 'LETTER' | 'number' | 'roman'"
            )

    for ax, lbl in zip(ax_list, final_labels):
        kw: Dict[str, Any] = dict(
            transform=ax.transAxes,
            fontweight=fontweight,
            va="top",
            ha="right",
        )
        if fontsize is not None:
            kw["fontsize"] = fontsize
        ax.text(x, y, lbl, **kw)


# ============================================================================
# 保存
# ============================================================================

def save(
    fig: Figure,
    name: str,
    dpi: int = 1200,
    formats: Tuple[str, ...] = ("pdf", "png"),
    bbox_inches: str = "tight",
    dir: Optional[str] = None,
    **kwargs: Any,
) -> List[Path]:
    """
    保存图形（同时输出多种格式）

    参数:
        fig        : Matplotlib 图形对象
        name       : 文件名（不含扩展名）
        dpi        : 位图分辨率，默认 1200（印刷级）
        formats    : 输出格式元组，默认 ("pdf", "png")
                     支持："pdf" | "png" | "svg" | "eps"
        bbox_inches: 默认 "tight"，自动裁剪多余白边
        dir        : 保存目录；为 None 则保存到当前工作目录

    返回:
        List[Path]: 已保存文件的路径列表

    示例:
        >>> sp.save(fig, "fig1")                              # → fig1.pdf + fig1.png
        >>> sp.save(fig, "word稿", formats=("png",), dpi=1200) # 仅 PNG
        >>> sp.save(fig, "投稿", formats=("pdf",))             # 仅 PDF
        >>> sp.save(fig, "fig", dir="outputs/figures")        # 保存到指定目录
    """
    VECTOR_FORMATS = {"pdf", "svg", "eps"}
    save_dir = Path(dir) if dir else Path.cwd()
    save_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: List[Path] = []
    for fmt in formats:
        path = save_dir / f"{name}.{fmt}"
        extra = {} if fmt in VECTOR_FORMATS else {"dpi": dpi}
        fig.savefig(path, bbox_inches=bbox_inches, format=fmt, **extra, **kwargs)
        saved_paths.append(path)
    return saved_paths


# ============================================================================
# 工具
# ============================================================================

def list_paper_layouts(
    venue: Optional[str] = None,
) -> Dict[str, Dict[str, Tuple[float, float]]]:
    """
    列出论文子图布局预设尺寸

    参数:
        venue: 指定期刊只看该期刊的布局；为 None 则返回全部

    示例:
        >>> sp.list_paper_layouts("thesis")
        {'thesis': {'1x1': (6.1, 4.3), '1x2': (6.1, 3.0), ...}}
    """
    if venue:
        return {venue: PAPER_LAYOUTS.get(venue, {})}
    return PAPER_LAYOUTS


# ============================================================================
# 内部工具
# ============================================================================

def _set_ticks_inward(axes: Union[Axes, np.ndarray]) -> None:
    """将所有子图的刻度设为朝内"""
    if isinstance(axes, np.ndarray):
        for ax in axes.flat:
            ax.tick_params(direction="in")
    elif isinstance(axes, Axes):
        axes.tick_params(direction="in")
