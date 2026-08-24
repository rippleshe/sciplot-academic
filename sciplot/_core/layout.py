"""
布局管理 — 图形创建、子图排布、保存、面板标签
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Tuple, Union, cast

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec

from sciplot._core.style import VENUES
from sciplot._core.utils import _ensure_non_empty_prop_cycle, apply_resolved_style

if TYPE_CHECKING:
    from sciplot._core.result import GridSpecResult


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


# Windows 保留设备名（含带扩展名的变体，如 CON.png），
# 避免写入控制台设备或产生不可索引文件
_WINDOWS_RESERVED_NAMES = frozenset({
    "con", "prn", "aux", "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
})


# ============================================================================
# 基础图形创建
# ============================================================================

def new_figure(
    venue: Optional[str] = None,
    figsize: Optional[Tuple[float, float]] = None,
    **kwargs: Any,
) -> Tuple[Figure, Axes]:
    """
    创建新图形，自动套用 venue 默认尺寸

    参数:
        venue  : 期刊预设（'nature' | 'ieee' | 'aps' | 'springer' | 'thesis' | 'presentation'）；
                 为 None 时复用当前 rcParams.figure.figsize
        figsize: 自定义 (宽, 高) 英寸，传入则覆盖 venue 默认值
        **kwargs: 传递给 plt.subplots()

    返回:
        (Figure, Axes) 或 (Figure, ndarray[Axes])（当 kwargs 含 nrows/ncols 时）

    示例:
        >>> fig, ax = sp.new_figure("ieee")
        >>> fig, ax = sp.new_figure(figsize=(5.0, 3.5))
        >>> fig, axes = sp.new_figure("thesis", nrows=1, ncols=2, sharex=True)
    """
    # 图形创建是取色安全入口：空颜色循环会导致 matplotlib 内部 nth-color
    # 取色时 ZeroDivisionError，故在任何 subplots 前保证 prop_cycle 非空
    _ensure_non_empty_prop_cycle()

    if venue is None:
        if figsize is None:
            return cast(Tuple[Figure, Axes], plt.subplots(**kwargs))
        return cast(Tuple[Figure, Axes], plt.subplots(figsize=figsize, **kwargs))

    if venue not in VENUES:
        raise ValueError(f"未知 venue '{venue}'，可用选项: {list(VENUES.keys())}")
    default_figsize = VENUES[venue].figsize
    size = figsize if figsize is not None else default_figsize
    return cast(Tuple[Figure, Axes], plt.subplots(figsize=size, **kwargs))


# ============================================================================
# 子图布局
# ============================================================================

def create_subplots(
    nrows: int = 1,
    ncols: int = 1,
    venue: str = "nature",
    sharex: bool = False,
    sharey: bool = False,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
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
        palette     : 配色方案
        lang        : 语言设置

    示例:
        >>> fig, axes = sp.create_subplots(2, 2, venue="ieee", sharex=True)
        >>> axes[0, 0].plot(x, y)
    """
    from sciplot._core.utils import apply_resolved_style
    from sciplot._core.config import get_config

    # 当 palette 未显式传入时，读取配置默认值
    if palette is None:
        cfg_palette = get_config("palette")
        if isinstance(cfg_palette, str) and cfg_palette:
            palette = cfg_palette

    effective_venue = apply_resolved_style(venue, palette, lang)
    # 回退为指定的 venue（apply_resolved_style 在上下文中可能返回 None）
    resolved_venue = effective_venue or venue

    base_figsize = VENUES[resolved_venue].figsize
    figsize = (base_figsize[0] * ncols * 0.85, base_figsize[1] * nrows * 0.85)

    fig, axes = plt.subplots(
        nrows=nrows, ncols=ncols, figsize=figsize,
        sharex=sharex, sharey=sharey, **kwargs
    )
    return fig, axes


def paper_subplots(
    nrows: int = 1,
    ncols: int = 1,
    venue: str = "nature",
    figsize: Optional[Tuple[float, float]] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
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
        palette     : 配色方案
        lang        : 语言设置

    示例:
        >>> # Word 论文 1×2 子图，精确匹配 A4 版心
        >>> fig, axes = sp.paper_subplots(1, 2, venue="thesis")
        >>> axes[0].plot(x, y1); axes[0].set_title("(a)")
        >>> axes[1].plot(x, y2); axes[1].set_title("(b)")
        >>> sp.save(fig, "thesis_1x2", formats=("png",), dpi=1200)

        >>> # IEEE 2×2 子图
        >>> fig, axes = sp.paper_subplots(2, 2, venue="ieee")
    """
    from sciplot._core.utils import apply_resolved_style
    from sciplot._core.config import get_config

    if palette is None:
        cfg_palette = get_config("palette")
        if isinstance(cfg_palette, str) and cfg_palette:
            palette = cfg_palette

    effective_venue = apply_resolved_style(venue, palette, lang)
    resolved_venue = effective_venue or venue

    if figsize is not None:
        final_figsize: Tuple[float, float] = figsize
    else:
        layout_key = f"{nrows}x{ncols}"
        venue_layouts = PAPER_LAYOUTS.get(resolved_venue, {})
        layout_figsize = venue_layouts.get(layout_key)
        if layout_figsize is None:
            # 回退：基于 venue 默认尺寸等比缩放
            base_fs = VENUES.get(resolved_venue, VENUES["nature"]).figsize
            final_figsize = (base_fs[0] * ncols * 0.85, base_fs[1] * nrows * 0.85)
        else:
            final_figsize = layout_figsize

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=final_figsize, **kwargs)
    return fig, axes


def add_colorbar(
    fig: Figure,
    mappable: Any,
    label: str = "",
    ax: Optional[Axes] = None,
    fraction: float = 0.046,
    pad: float = 0.04,
    **kwargs: Any,
):
    """创建 colorbar 并设置统一的辅助信息层级。

    默认保持稳定的版心占用（fraction=0.046, pad=0.04）；3D 图可传
    ``shrink=0.5, aspect=10`` 覆盖。colorbar 应弱于主轴，因此 outline 与
    tick 线宽默认略低于正文坐标轴，但不会改写用户显式传入的几何参数。
    """
    if not np.isfinite(fraction) or fraction <= 0:
        raise ValueError(f"fraction 必须是正的有限数，实际值: {fraction!r}")
    if not np.isfinite(pad) or pad < 0:
        raise ValueError(f"pad 必须是非负有限数，实际值: {pad!r}")

    cbar = fig.colorbar(mappable, ax=ax, fraction=fraction, pad=pad, **kwargs)
    if label:
        cbar.set_label(label)

    axes_lw = float(plt.rcParams.get("axes.linewidth", 0.8))
    tick_lw = float(plt.rcParams.get("ytick.major.width", axes_lw))
    plt.setp(cbar.outline, linewidth=max(0.4, axes_lw * 0.8))
    cbar.ax.tick_params(
        width=max(0.4, tick_lw * 0.8),
        labelsize=max(5.0, float(plt.rcParams.get("font.size", 9)) - 1.0),
    )
    return cbar


# ============================================================================
# 复合图模板（Nature 级多面板布局原型）
# ============================================================================

COMPOSITE_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "condition_matrix": {
        "description": "条件矩阵：行/列双因子组合实验（如药物×剂量）",
        "nrows": 2, "ncols": 3,
        "widths": None, "heights": None,
        "hspace": 0.35, "wspace": 0.28,
        "sharex": False, "sharey": True,
        "label_size": 8,
    },
    "time_march": {
        "description": "时间推进：同一系统随时间演化的快照序列",
        "nrows": 2, "ncols": 2,
        "widths": None, "heights": None,
        "hspace": 0.32, "wspace": 0.28,
        "sharex": False, "sharey": False,
        "label_size": 8,
    },
    "comparative": {
        "description": "对照双列：基线 vs 改进方法的并排对比",
        "nrows": 1, "ncols": 2,
        "widths": [1, 1], "heights": None,
        "hspace": 0.30, "wspace": 0.30,
        "sharex": False, "sharey": True,
        "label_size": 8,
    },
    "pipeline": {
        "description": "流水线：方法学论文的流程叙事（阶段间用箭头连接）",
        "nrows": 1, "ncols": 5,
        "widths": None, "heights": None,
        "hspace": 0.30, "wspace": 0.62,
        "sharex": False, "sharey": False,
        "label_size": 8,
    },
    "triptych": {
        "description": "临床三联画：上行时序、中行森林图、下行汇总柱（Nature 高频页面）",
        "nrows": 3, "ncols": 2,
        "widths": [1, 1], "heights": [1.0, 0.9, 0.7],
        "hspace": 0.50, "wspace": 0.30,
        "sharex": False, "sharey": False,
        "label_size": 8,
    },
}


def list_composite_templates() -> Dict[str, Dict[str, Any]]:
    """列出所有内置复合图模板及其规格。

    返回:
        {模板名: {description, nrows, ncols, hspace, wspace, ...}}

    示例:
        >>> sp.list_composite_templates()
        {'condition_matrix': {'description': ..., 'nrows': 2, ...}}
    """
    return {name: dict(cfg) for name, cfg in COMPOSITE_TEMPLATES.items()}


# ============================================================================
# 不对称 Hero 布局（主面板 + 卫星面板）
# ============================================================================

HERO_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "hero_right": {
        "description": "左侧主面板 + 右侧 2×1 卫星（主图占 2/3 宽）",
        "grid": (2, 2),
        "width_ratios": [2.0, 1.0],
        "height_ratios": [1.0, 1.0],
        "hero": (slice(0, 2), 0),
        "satellites": [(0, 1), (1, 1)],
        "hspace": 0.30, "wspace": 0.25,
    },
    "hero_top": {
        "description": "顶部通栏主面板 + 底部 3 列卫星",
        "grid": (2, 3),
        "width_ratios": [1.0, 1.0, 1.0],
        "height_ratios": [1.3, 1.0],
        "hero": (0, slice(0, 3)),
        "satellites": [(1, 0), (1, 1), (1, 2)],
        "hspace": 0.35, "wspace": 0.25,
    },
    "hub_spoke": {
        "description": "3×3 网格：中心主面板 + 上/左/右/下四个卫星",
        "grid": (3, 3),
        "width_ratios": [1.0, 1.0, 1.0],
        "height_ratios": [1.0, 1.0, 1.0],
        "hero": (1, 1),
        "satellites": [(0, 1), (1, 0), (1, 2), (2, 1)],
        "hspace": 0.45, "wspace": 0.35,
    },
}


def list_hero_templates() -> Dict[str, Dict[str, Any]]:
    """列出所有内置不对称 Hero 布局模板。

    返回:
        {模板名: {description, grid, hero, satellites, ...}}

    示例:
        >>> sp.list_hero_templates()
        {'hero_right': {'description': ..., 'grid': (2, 2), ...}}
    """
    return {name: dict(cfg) for name, cfg in HERO_TEMPLATES.items()}


def hero_layout(
    template: str = "hero_right",
    venue: str = "nature",
    panel_labels: bool = True,
    label_style: str = "letter",
    label_size: Optional[int] = 8,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    figsize: Optional[Tuple[float, float]] = None,
    **kwargs: Any,
) -> "GridSpecResult":
    """创建不对称 Hero 布局：一个主导面板 + 若干卫星面板。

    Nature 高频页面原型：主图承载核心结论（Hero），卫星面板
    回答次要问题。非等分网格避免 dashboard 感。

    模板:
        - 'hero_right': 左侧主面板（2/3 宽）+ 右侧 2×1 卫星
        - 'hero_top'  : 顶部通栏主面板 + 底部 3 列卫星
        - 'hub_spoke' : 3×3 中心主面板 + 四向卫星

    返回:
        GridSpecResult，支持:
        - .fig  / .figure
        - .ax_hero          （主面板）
        - .ax_satellite(i)  （第 i 个卫星面板）
        - .satellites       （卫星列表）

    示例:
        >>> fig, gs = sp.hero_layout("hero_right", venue="thesis")
        >>> sp.plot_scatter(x, y, ax=gs.ax_hero)
        >>> sp.plot_box(data, ax=gs.ax_satellite(0))
        >>> sp.save(fig, "fig_hero")
    """
    from sciplot._core.result import GridSpecResult
    from sciplot._core.style import VENUES

    if template not in HERO_TEMPLATES:
        raise ValueError(
            f"未知 hero template '{template}'，可用选项: {list(HERO_TEMPLATES.keys())}"
        )

    apply_resolved_style(venue, palette, lang)
    cfg = HERO_TEMPLATES[template]
    nrows, ncols = cfg["grid"]
    if figsize is None and venue in VENUES:
        figsize = VENUES[venue].figsize

    fig = plt.figure(figsize=figsize)
    gs = GridSpec(
        nrows, ncols,
        figure=fig,
        width_ratios=cfg["width_ratios"],
        height_ratios=cfg["height_ratios"],
        hspace=cfg["hspace"],
        wspace=cfg["wspace"],
        **kwargs,
    )

    result = GridSpecResult(fig, gs)

    # 主面板与卫星
    hero_spec = cfg["hero"]
    ax_hero = fig.add_subplot(gs[hero_spec[0], hero_spec[1]])
    ax_hero.grid(False)
    result._ax_hero = ax_hero  # type: ignore[attr-defined]

    sat_axes: List[Axes] = []
    for (r, c) in cfg["satellites"]:
        ax = fig.add_subplot(gs[r, c])
        ax.grid(False)
        sat_axes.append(ax)
    result._satellites = sat_axes  # type: ignore[attr-defined]

    if panel_labels:
        add_panel_labels([ax_hero, *sat_axes], style=label_style,
                         fontsize=label_size)

    return result


def figure_panels(
    nrows: int = 1,
    ncols: int = 1,
    venue: str = "nature",
    template: Optional[str] = None,
    widths: Optional[Sequence[float]] = None,
    heights: Optional[Sequence[float]] = None,
    hspace: Optional[float] = None,
    wspace: Optional[float] = None,
    panel_labels: bool = True,
    label_style: str = "letter",
    label_size: Optional[int] = None,
    sharex: Optional[bool] = None,
    sharey: Optional[bool] = None,
    figsize: Optional[Tuple[float, float]] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> Tuple[Figure, np.ndarray]:
    """创建 Nature 级多面板复合图布局（面板自动编号 a/b/c）。

    设计规范（对齐 Nature 投稿惯例）：
    - 面板按阅读顺序自动加粗标签 (a) (b) (c)…，默认 8pt（Nature 规范）
    - widths/heights 控制行列相对比例（如主面板 2/3、注释面板 1/3）
    - hspace/wspace 控制面板间距，默认大于 Matplotlib 默认值以避免标签挤压
    - venue 决定基准 figsize（nature 双栏 183mm 宽等）

    template 参数（复合图模板，一次性获得顶刊级网格结构）：
    - 'condition_matrix': 2×3 条件矩阵（行/列双因子，共享 y 轴）
    - 'time_march'      : 2×2 时间推进快照
    - 'comparative'     : 1×2 对照双列（基线 vs 改进，共享 y 轴）
    - 'pipeline'        : 1×5 流水线（阶段叙事）
    - 'triptych'        : 3×2 临床三联画（时序 + 森林 + 汇总）

    参数:
        nrows/ncols: 面板行列数（template 未指定时生效）
        venue       : 期刊预设（默认 nature）
        template    : 复合图模板名；None 时使用手动网格参数
        widths      : 各列相对宽度，如 [1, 1.5]；None 时等宽
        heights     : 各行相对高度；None 时等高
        hspace/wspace: 面板垂直/水平间距（None 用模板或默认值）
        panel_labels: 是否自动加面板标签
        label_style : 标签样式（letter/LETTER/number/roman）
        label_size  : 面板标签字号（pt）；None 时模板优先，再继承 rcParams
        sharex/sharey: 面板间共享轴（None 用模板或默认 False）
        figsize     : 自定义尺寸；None 用 venue 默认

    示例:
        >>> # 主图占 2/3 宽 + 右侧注释面板的 2 面板布局
        >>> fig, axes = sp.figure_panels(1, 2, widths=[2, 1])
        >>> sp.plot_scatter(x1, y1, ax=axes[0])
        >>> sp.plot_box(data, ax=axes[1])
        >>> sp.save(fig, "fig_composite")

        >>> # 使用条件矩阵模板（2×3，共享 y 轴，8pt 标签）
        >>> fig, axes = sp.figure_panels(template="condition_matrix", venue="thesis")
        >>> for ax in axes.flat:
        ...     ax.scatter(x, y)
        >>> sp.save(fig, "fig_condition_matrix")
    """
    from sciplot._core.style import VENUES

    # ── 模板解析：template 优先，显式参数覆盖模板值 ──
    tmpl: Optional[Dict[str, Any]] = None
    if template is not None:
        if template not in COMPOSITE_TEMPLATES:
            raise ValueError(
                f"未知 template '{template}'，可用选项: {list(COMPOSITE_TEMPLATES.keys())}"
            )
        tmpl = COMPOSITE_TEMPLATES[template]
        nrows = int(tmpl["nrows"])
        ncols = int(tmpl["ncols"])
        if widths is None:
            widths = tmpl.get("widths")
        if heights is None:
            heights = tmpl.get("heights")
        if hspace is None:
            hspace = float(tmpl.get("hspace", 0.30))
        if wspace is None:
            wspace = float(tmpl.get("wspace", 0.25))
        if sharex is None:
            sharex = bool(tmpl.get("sharex", False))
        if sharey is None:
            sharey = bool(tmpl.get("sharey", False))
        if label_size is None:
            label_size = tmpl.get("label_size")

    if hspace is None:
        hspace = 0.30
    if wspace is None:
        wspace = 0.25
    if sharex is None:
        sharex = False
    if sharey is None:
        sharey = False

    if nrows <= 0 or ncols <= 0:
        raise ValueError(f"nrows/ncols 必须为正整数，实际: {nrows}x{ncols}")
    if widths is not None and len(widths) != ncols:
        raise ValueError(f"widths 长度 ({len(widths)}) 与 ncols ({ncols}) 不一致")
    if heights is not None and len(heights) != nrows:
        raise ValueError(f"heights 长度 ({len(heights)}) 与 nrows ({nrows}) 不一致")

    apply_resolved_style(venue, palette, lang)
    if figsize is None and venue in VENUES:
        figsize = VENUES[venue].figsize

    gridspec_kw: Dict[str, Any] = dict(hspace=hspace, wspace=wspace)
    if widths is not None:
        gridspec_kw["width_ratios"] = list(widths)
    if heights is not None:
        gridspec_kw["height_ratios"] = list(heights)

    fig, axes = plt.subplots(
        nrows, ncols,
        figsize=figsize,
        sharex=sharex,
        sharey=sharey,
        gridspec_kw=gridspec_kw,
        **kwargs,
    )

    if panel_labels:
        add_panel_labels(axes, style=label_style, fontsize=label_size)
    return fig, axes


def create_gridspec(
    nrows: int = 1,
    ncols: int = 1,
    venue: str = "nature",
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> "GridSpecResult":
    """
    创建 GridSpec 不规则子图布局

    参数:
        nrows, ncols: 行列数
        venue       : 期刊预设
        palette     : 配色方案
        lang        : 语言设置

    示例:
        >>> fig, gs = sp.create_gridspec(2, 3, venue="nature")
        >>> ax_top = fig.add_subplot(gs[0, :])   # 顶部通栏
        >>> ax_bl  = fig.add_subplot(gs[1, 0])
        >>> ax_bm  = fig.add_subplot(gs[1, 1])
        >>> ax_br  = fig.add_subplot(gs[1, 2])
        >>> for ax in fig.axes: ax.tick_params(direction="in")
        >>> sp.save(fig, "gridspec")
    """
    from sciplot._core.utils import apply_resolved_style
    from sciplot._core.result import GridSpecResult
    from sciplot._core.config import get_config

    if palette is None:
        cfg_palette = get_config("palette")
        if isinstance(cfg_palette, str) and cfg_palette:
            palette = cfg_palette

    effective_venue = apply_resolved_style(venue, palette, lang)
    resolved_venue = effective_venue or venue

    figsize = VENUES[resolved_venue].figsize
    fig = plt.figure(figsize=figsize)
    gs = GridSpec(nrows, ncols, figure=fig, **kwargs)
    return GridSpecResult(fig, gs)


def create_twinx(ax: Axes) -> Axes:
    """
    创建共享 X 轴的副 Y 轴（双 Y 轴）

    示例:
        >>> sp.setup_style("ieee", "pastel-2")
        >>> fig, ax1 = sp.new_figure("ieee")
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
    def _int_to_roman(num: int) -> str:
        if num <= 0:
            raise ValueError("roman 序号必须为正整数")
        if num > 3999:
            raise ValueError("roman 序号不能超过 3999")
        vals = [
            (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
            (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
            (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
        ]
        result = []
        left = num
        for value, symbol in vals:
            while left >= value:
                result.append(symbol)
                left -= value
        return "".join(result).lower()

    def _int_to_letters(num: int, upper: bool = False) -> str:
        if num <= 0:
            raise ValueError("letter 序号必须为正整数")
        chars: List[str] = []
        idx = num
        while idx > 0:
            idx -= 1
            chars.append(chr(ord("a") + (idx % 26)))
            idx //= 26
        text = "".join(reversed(chars))
        return text.upper() if upper else text

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
            final_labels = [f"({_int_to_letters(i + 1)})" for i in range(n)]
        elif style == "LETTER":
            final_labels = [f"({_int_to_letters(i + 1, upper=True)})" for i in range(n)]
        elif style == "number":
            final_labels = [f"({i + 1})" for i in range(n)]
        elif style == "roman":
            final_labels = [f"({_int_to_roman(i + 1)})" for i in range(n)]
        else:
            raise ValueError(
                f"未知 style '{style}'，可选: 'letter' | 'LETTER' | 'number' | 'roman'"
            )

    for ax, lbl in zip(ax_list, final_labels):
        # 根据 x 坐标自动推断对齐方式
        ha = "right" if x <= 0 else "left"
        kw: Dict[str, Any] = dict(
            fontweight=fontweight,
            va="top",
            ha=ha,
        )
        if fontsize is not None:
            kw["fontsize"] = fontsize
        if hasattr(ax, "get_zlabel"):
            # 3D 子图：Axes3D.text() 签名不同，使用 text2D 以 axes 坐标定位
            ax.text2D(x, y, lbl, transform=ax.transAxes, **kw)
        else:
            kw["transform"] = ax.transAxes
            ax.text(x, y, lbl, **kw)


# ============================================================================
# 保存
# ============================================================================

def _normalize_output_formats(formats: Union[str, Sequence[str]]) -> Tuple[str, ...]:
    """规范化输出格式参数，兼容单字符串输入。"""
    if isinstance(formats, str):
        normalized = (formats,)
    else:
        normalized = tuple(formats)

    if not normalized:
        raise ValueError("formats 不能为空")

    result: List[str] = []
    for fmt in normalized:
        if not isinstance(fmt, str) or not fmt.strip():
            raise ValueError("formats 必须是非空字符串或字符串序列")
        result.append(fmt.strip().lower())

    return tuple(result)

def save(
    fig: Figure,
    name: str,
    dpi: Optional[Union[int, float]] = None,
    formats: Optional[Union[str, Sequence[str]]] = None,
    bbox_inches: str = "tight",
    dir: Optional[str] = None,
    close: bool = False,
    audit: Optional[bool] = None,
    **kwargs: Any,
) -> List[Path]:
    """
    保存图形（同时输出多种格式）

    参数:
        fig        : Matplotlib 图形对象
        name       : 文件名（不含扩展名），可包含子目录路径
        dpi        : 位图分辨率；为 None 时读取配置默认值
        formats    : 输出格式元组；为 None 时读取配置默认值
                     支持："pdf" | "png" | "svg" | "eps"
        bbox_inches: 默认 "tight"，自动裁剪多余白边
        dir        : 保存目录；为 None 则保存到当前工作目录
        close      : 保存后是否自动关闭图形释放内存，默认 False
        audit      : 保存前是否执行投稿质量审计（审稿七宗罪防线）；
                     None 时读取配置默认值（默认 True）

    返回:
        List[Path]: 已保存文件的路径列表

    示例:
        >>> sp.save(fig, "fig1")                              # → fig1.pdf + fig1.png
        >>> sp.save(fig, "word稿", formats=("png",), dpi=1200) # 仅 PNG
        >>> sp.save(fig, "投稿", formats=("pdf",))             # 仅 PDF
        >>> sp.save(fig, "fig", dir="outputs/figures")        # 保存到指定目录
        >>> sp.save(fig, "nested/dir/fig")                    # 自动创建嵌套目录
        >>> sp.save(fig, "batch", close=True)                 # 保存后自动关闭
        >>> sp.save(fig, "fig", audit=False)                  # 跳过质量审计
    """
    from sciplot._core.config import get_config

    VECTOR_FORMATS = {"pdf", "svg", "eps"}
    resolved_formats = formats if formats is not None else get_config("formats")
    normalized_formats = _normalize_output_formats(resolved_formats)
    resolved_dpi = dpi if dpi is not None else get_config("dpi")

    supported_formats = set(fig.canvas.get_supported_filetypes().keys())
    invalid_formats = [fmt for fmt in normalized_formats if fmt not in supported_formats]
    if invalid_formats:
        raise ValueError(
            f"不支持的输出格式: {invalid_formats}。可用格式: {sorted(supported_formats)}"
        )

    if any(fmt not in VECTOR_FORMATS for fmt in normalized_formats):
        if not isinstance(resolved_dpi, (int, float)) or resolved_dpi <= 0:
            raise ValueError(f"dpi 必须为正数，实际值: {resolved_dpi!r}")

    # 保存前投稿质量审计（审稿七宗罪防线，不中断保存）
    # 默认只检查必拒项：字号下限 + 多面板标签缺失；
    # 轴标签等软性检查请显式调用 sp.audit_figure() 全量审计。
    if audit is None:
        cfg_audit = get_config("audit")
        audit = bool(cfg_audit) if isinstance(cfg_audit, bool) else True
    if audit:
        try:
            from sciplot._core.audit import audit_figure

            audit_figure(fig, verbose=True, check_axis_labels=False)
        except Exception:
            pass

    # 处理 name 可能包含路径的情况
    name_path = Path(name)
    if name_path.name in {"", ".", ".."}:
        raise ValueError("name 必须是有效文件名")

    # Windows 保留设备名检查（模块级常量，含带扩展名的变体）
    stem_lower = name_path.stem.lower()
    if stem_lower in _WINDOWS_RESERVED_NAMES:
        raise ValueError(
            f"name 使用了 Windows 保留设备名 '{stem_lower}'，请更换文件名"
        )

    if dir:
        if name_path.is_absolute():
            raise ValueError("指定 dir 时，name 不能为绝对路径")

        base_dir = Path(dir).expanduser().resolve()
        save_dir = (base_dir / name_path.parent).resolve()
        try:
            save_dir.relative_to(base_dir)
        except ValueError as exc:
            raise ValueError("name 不能通过路径回退跳出 dir 指定目录") from exc
    else:
        save_dir = name_path.parent if name_path.parent != Path(".") else Path.cwd()
        if not save_dir.is_absolute():
            save_dir = Path.cwd() / save_dir

    # 确保目录存在（递归创建）
    save_dir.mkdir(parents=True, exist_ok=True)

    # 纯文件名（不含路径）
    filename = name_path.name

    saved_paths: List[Path] = []
    for fmt in normalized_formats:
        path = save_dir / f"{filename}.{fmt}"
        extra = {} if fmt in VECTOR_FORMATS else {"dpi": resolved_dpi}
        fig.savefig(path, bbox_inches=bbox_inches, format=fmt, **extra, **kwargs)
        saved_paths.append(path)

    if close:
        plt.close(fig)

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
