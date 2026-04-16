"""
SciPlot Academic — 期刊级科研绘图库

安装:
    pip install sciplot-academic
    uv pip install sciplot-academic

快速上手:
    >>> import sciplot as sp
    >>> import numpy as np
    >>> x = np.linspace(0, 10, 200)
    >>> fig, ax = sp.plot(x, np.sin(x), xlabel="时间 (s)", ylabel="电压 (V)")
    >>> sp.save(fig, "结果图")

链式调用（新功能）:
    >>> fig = sp.style("nature").palette("pastel").plot(x, y).save("output")

上下文管理器（新功能）:
    >>> with sp.style_context("ieee", palette="earth"):
    ...     fig, ax = sp.plot(x, y)

简洁别名（新功能）:
    >>> fig, ax = sp.line(x, y)      # 同 plot_line
    >>> fig, ax = sp.scatter(x, y)   # 同 plot_scatter
    >>> fig, ax = sp.bar(x, y)       # 同 plot_bar

配色体系（三大常驻系列 + 人民币系列）:
    pastel / pastel-1/2/3/4  — 柔和粉彩（默认）
    earth  / earth-1/2/3/4   — 大地色系
    ocean  / ocean-1/2/3/4   — 海洋蓝绿
    100yuan / 50yuan / ...    — 人民币系列

期刊样式:
    nature（默认）| ieee | aps | springer | thesis | presentation
"""

__version__ = "1.7.1"
__author__ = "SciPlot Team"

import warnings as _warnings

try:
    import scienceplots as _sp  # noqa: F401
    HAS_SCIENCEPLOTS = True
except ImportError:
    _warnings.warn(
        "scienceplots 未安装，请运行: pip install scienceplots",
        ImportWarning,
        stacklevel=2,
    )
    HAS_SCIENCEPLOTS = False

# ── 核心 ──────────────────────────────────────────────────────
from sciplot._core.style import (
    setup_style,
    reset_style,
    get_venue_info,
    list_venues,
    list_languages,
    VENUES,
    LANGUAGES,
)
from sciplot._core.palette import (
    apply_palette as _apply_palette,   # 内部用，不直接暴露
    set_custom_palette,
    register_color_scheme,
    get_palette,
    get_color_scheme,
    list_palettes,
    list_all_palettes,
    list_resident_palettes,
    list_pastel_subsets,
    list_earth_subsets,
    list_ocean_subsets,
    list_rmb_palettes,
    list_color_schemes,
    auto_select_palette,
    DEFAULT_PALETTE,
    RMB_PALETTES,
    RESIDENT_PALETTES,
    PASTEL_PALETTE,
    EARTH_PALETTE,
    OCEAN_PALETTE,
    ALL_PALETTES,
)
from sciplot._core.layout import (
    new_figure,
    create_subplots,
    paper_subplots,
    create_gridspec,
    create_twinx,
    add_panel_labels,
    save,
    list_paper_layouts,
    PAPER_LAYOUTS,
)

# ── 链式调用 (Fluent Interface) ────────────────────────────────
from sciplot._core.fluent import (
    PlotChain,
    FigureWrapper,
    style as _style_chain,
    palette as _palette_chain,
    chain,
)

# ── 上下文管理器 (Context Manager) ─────────────────────────────
from sciplot._core.context import (
    StyleContext,
    style_context,
    context,
    ieee_context,
    nature_context,
    thesis_context,
)

# ── 图表 ──────────────────────────────────────────────────────
from sciplot._plots.basic import (
    plot_line,
    plot,
    plot_multi,
    plot_multi_line,
    plot_scatter,
    plot_step,
    plot_area,
    plot_multi_area,
    LINE_STYLES,
    MARKERS,
)
from sciplot._plots.distribution import (
    plot_bar,
    plot_grouped_bar,
    plot_stacked_bar,
    plot_horizontal_bar,
    plot_box,
    plot_violin,
    plot_histogram,
    plot_combo,
    annotate_significance,
)
from sciplot._plots.advanced import (
    plot_errorbar,
    plot_confidence,
    plot_heatmap,
)

# ── 简洁别名 (Aliases) ────────────────────────────────────────
from sciplot._plots.aliases import (
    # 基础图表
    line,
    scatter,
    step,
    area,
    # 多系列图表
    multi,
    multi_line,
    multi_area,
    # 分布统计图表
    bar,
    grouped_bar,
    stacked_bar,
    hbar,
    hist,
    box,
    violin,
    # 高级图表
    errorbar,
    confidence,
    heatmap,
    combo,
)

# ── 工具 ──────────────────────────────────────────────────────
from sciplot.utils import (
    # 颜色工具
    hex_to_rgb,
    rgb_to_hex,
    lighten_color,
    darken_color,
    generate_gradient,
    # 智能辅助
    auto_rotate_labels,
    smart_legend,
    optimize_layout,
    adjust_subplots,
    suggest_figsize,
    check_color_contrast,
)


# ═══════════════════════════════════════════════════════════════
# 便捷入口函数
# ═══════════════════════════════════════════════════════════════

def style(venue: str) -> PlotChain:
    """
    链式调用入口 - 设置期刊样式
    
    参数:
        venue: 期刊样式，如 "nature", "ieee", "thesis" 等
        
    返回:
        PlotChain 对象支持链式调用
        
    示例:
        >>> import sciplot as sp
        >>> fig = sp.style("nature").palette("pastel").plot(x, y).save("output")
    """
    return _style_chain(venue)


def palette(palette: str) -> PlotChain:
    """
    链式调用入口 - 设置配色方案
    
    参数:
        palette: 配色名称，如 "pastel", "earth", "100yuan" 等
        
    返回:
        PlotChain 对象支持链式调用
        
    示例:
        >>> fig = sp.palette("earth").plot(x, y).save("output")
    """
    return _palette_chain(palette)


__all__ = [
    "__version__",

    # ── 样式 ──
    "setup_style", "reset_style", "get_venue_info",
    "list_venues", "list_languages",

    # ── 配色 ──
    "set_custom_palette", "register_color_scheme",
    "get_palette", "get_color_scheme",
    "list_palettes", "list_all_palettes", "list_resident_palettes",
    "list_pastel_subsets", "list_earth_subsets", "list_ocean_subsets",
    "list_rmb_palettes", "list_color_schemes",
    "auto_select_palette",

    # ── 布局 ──
    "new_figure", "save",
    "create_subplots", "paper_subplots", "create_gridspec", "create_twinx",
    "add_panel_labels", "list_paper_layouts",

    # ── 链式调用 ──
    "style", "palette", "chain",
    "PlotChain", "FigureWrapper",

    # ── 上下文管理器 ──
    "style_context", "context",
    "ieee_context", "nature_context", "thesis_context",
    "StyleContext",

    # ── 折线 / 散点 / 面积（完整名称）──
    "plot", "plot_line", "plot_multi", "plot_multi_line",
    "plot_scatter", "plot_step",
    "plot_area", "plot_multi_area",

    # ── 折线 / 散点 / 面积（简洁别名）──
    "line", "scatter", "step", "area",
    "multi", "multi_line", "multi_area",

    # ── 分布 / 统计（完整名称）──
    "plot_bar", "plot_grouped_bar", "plot_stacked_bar", "plot_horizontal_bar",
    "plot_box", "plot_violin", "plot_histogram",
    "plot_combo", "annotate_significance",

    # ── 分布 / 统计（简洁别名）──
    "bar", "grouped_bar", "stacked_bar", "hbar",
    "hist", "box", "violin",
    "combo",

    # ── 高级（完整名称）──
    "plot_errorbar", "plot_confidence", "plot_heatmap",

    # ── 高级（简洁别名）──
    "errorbar", "confidence", "heatmap",

    # ── 颜色工具 ──
    "hex_to_rgb", "rgb_to_hex",
    "lighten_color", "darken_color", "generate_gradient",

    # ── 智能辅助 ──
    "auto_rotate_labels", "smart_legend",
    "optimize_layout", "adjust_subplots",
    "suggest_figsize", "check_color_contrast",

    # ── 常量 ──
    "VENUES", "PAPER_LAYOUTS", "LANGUAGES",
    "RMB_PALETTES", "RESIDENT_PALETTES",
    "PASTEL_PALETTE", "EARTH_PALETTE", "OCEAN_PALETTE",
    "LINE_STYLES", "MARKERS", "DEFAULT_PALETTE", "ALL_PALETTES",

    # ── 状态 ──
    "HAS_SCIENCEPLOTS",
]
