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
    >>> with sp.style_context("ieee", palette="forest"):
    ...     fig, ax = sp.plot(x, y)

简洁别名（新功能）:
    >>> fig, ax = sp.line(x, y)      # 同 plot_line
    >>> fig, ax = sp.scatter(x, y)   # 同 plot_scatter
    >>> fig, ax = sp.bar(x, y)       # 同 plot_bar

配色体系（四大内置配色系）:
    pastel / pastel-1~6  — 柔和粉彩（默认）
    ocean  / ocean-1~6   — 海洋蓝绿
    forest / forest-1~6  — 森林渐变
    sunset / sunset-1~5  — 日落暖色

期刊样式:
    nature（默认）| ieee | aps | springer | thesis | presentation
"""

__version__ = "1.7.4"
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
    list_forest_subsets,
    list_sunset_subsets,
    list_color_schemes,
    auto_select_palette,
    DEFAULT_PALETTE,
    RESIDENT_PALETTES,
    PASTEL_PALETTE,
    EARTH_PALETTE,
    OCEAN_PALETTE,
    FOREST_PALETTE,
    SUNSET_PALETTE,
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

# ── 返回类型 (Result Types) ────────────────────────────────────
from sciplot._core.result import (
    PlotResult,
    GridSpecResult,
)

# ── 公共工具函数 (Utilities) ───────────────────────────────────
from sciplot._core.utils import (
    validate_array_like,
    validate_labels_match_data,
    validate_positive_number,
    validate_choice,
    validate_dict_not_empty,
)

# ── 配置系统 (Configuration) ────────────────────────────────────
from sciplot._core.config import (
    SciPlotConfig,
    set_defaults,
    get_config,
    load_config,
    reset_config,
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
from sciplot._plots.polar import (
    plot_radar,
)
from sciplot._plots.timeseries import (
    plot_timeseries,
    plot_multi_timeseries,
)
from sciplot._plots.multivariate import (
    plot_parallel,
)
from sciplot._plots.statistical import (
    plot_residuals,
    plot_qq,
    plot_bland_altman,
)

# ── 扩展模块 (Extensions) ──────────────────────────────────────
from sciplot._ext.ml import (
    plot_pca,
    plot_confusion_matrix,
    plot_feature_importance,
    plot_learning_curve,
)
from sciplot._ext.plot3d import (
    plot_surface,
    plot_contour,
    plot_3d_scatter,
    plot_wireframe,
)
from sciplot._ext.network import (
    plot_network,
    plot_network_from_matrix,
    plot_network_communities,
)
from sciplot._ext.hierarchical import (
    plot_dendrogram,
    plot_clustermap,
)
from sciplot._ext.venn import (
    plot_venn2,
    plot_venn3,
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


def palette(palette_name: str) -> PlotChain:
    """
    链式调用入口 - 设置配色方案
    
    参数:
        palette_name: 配色名称，如 "pastel", "ocean", "forest", "sunset" 等
        
    返回:
        PlotChain 对象支持链式调用
        
    示例:
        >>> fig = sp.palette("ocean").plot(x, y).save("output")
    """
    return _palette_chain(palette_name)


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
    "list_forest_subsets", "list_sunset_subsets", "list_color_schemes",
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

    # ── 返回类型 ──
    "PlotResult", "GridSpecResult",

    # ── 验证工具 ──
    "validate_array_like", "validate_labels_match_data",
    "validate_positive_number", "validate_choice", "validate_dict_not_empty",

    # ── 配置系统 ──
    "SciPlotConfig", "set_defaults", "get_config", "load_config", "reset_config",

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

    # ── 极坐标图表 ──
    "plot_radar",

    # ── 时序图表 ──
    "plot_timeseries", "plot_multi_timeseries",

    # ── 多维图表 ──
    "plot_parallel",

    # ── 统计图表 ──
    "plot_residuals", "plot_qq", "plot_bland_altman",

    # ── 机器学习扩展 ──
    "plot_pca", "plot_confusion_matrix",
    "plot_feature_importance", "plot_learning_curve",

    # ── 3D 扩展 ──
    "plot_surface", "plot_contour", "plot_3d_scatter", "plot_wireframe",

    # ── 网络图扩展 ──
    "plot_network", "plot_network_from_matrix", "plot_network_communities",

    # ── 层次聚类扩展 ──
    "plot_dendrogram", "plot_clustermap",

    # ── Venn 图扩展 ──
    "plot_venn2", "plot_venn3",

    # ── 颜色工具 ──
    "hex_to_rgb", "rgb_to_hex",
    "lighten_color", "darken_color", "generate_gradient",

    # ── 智能辅助 ──
    "auto_rotate_labels", "smart_legend",
    "optimize_layout", "adjust_subplots",
    "suggest_figsize", "check_color_contrast",

    # ── 常量 ──
    "VENUES", "PAPER_LAYOUTS", "LANGUAGES",
    "RESIDENT_PALETTES",
    "PASTEL_PALETTE", "EARTH_PALETTE", "OCEAN_PALETTE",
    "FOREST_PALETTE", "SUNSET_PALETTE",
    "LINE_STYLES", "MARKERS", "DEFAULT_PALETTE", "ALL_PALETTES",

    # ── 状态 ──
    "HAS_SCIENCEPLOTS",
]
