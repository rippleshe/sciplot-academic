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

配色体系（内置配色）:
    pastel / pastel-1~6  — 柔和粉彩（默认）
    ocean  / ocean-1~6   — 海洋蓝绿
    forest / forest-1~6  — 森林渐变
    sunset / sunset-1~5  — 日落暖色

子图布局选择:
    create_subplots  — 快速创建并按 venue 比例缩放，适合探索与草稿
    paper_subplots   — 严格按论文版心尺寸创建，适合投稿与定稿

面积图语义:
    plot_area(fill=True)   — 线条 + 填充
    plot_area(fill=False)  — 仅线条；alpha 参数仅在填充开启时生效

期刊样式:
    nature（默认）| ieee | aps | springer | thesis | presentation
"""

from __future__ import annotations

from pathlib import Path as _Path
from threading import Lock as _Lock
from types import MappingProxyType as _MappingProxyType
from typing import Any, Mapping, Sequence, Tuple


def _read_local_version() -> str:
    """优先读取源码仓库 pyproject.toml 中的版本。"""
    pyproject_path = _Path(__file__).resolve().parent.parent / "pyproject.toml"
    if not pyproject_path.exists():
        return ""

    try:
        import tomllib as _toml
    except ImportError:
        try:
            import tomli as _toml
        except ImportError:
            return ""

    try:
        with pyproject_path.open("rb") as f:
            data = _toml.load(f)
        version = data.get("project", {}).get("version", "")
        return str(version) if version is not None else ""
    except (OSError, ValueError, TypeError):
        return ""


_LOCAL_VERSION = _read_local_version()
if _LOCAL_VERSION:
    __version__ = _LOCAL_VERSION
else:
    try:
        from importlib.metadata import version as _get_version
        __version__ = _get_version("sciplot-academic")
    except Exception:
        __version__ = "unknown"
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
    list_rmb_palettes,
    list_diverging_palettes,
    list_color_schemes,
    auto_select_palette,
    DEFAULT_PALETTE,
    RESIDENT_PALETTES,
    PASTEL_PALETTE,
    EARTH_PALETTE,
    OCEAN_PALETTE,
    FOREST_PALETTE,
    SUNSET_PALETTE,
    RMB_PALETTES,
    DIVERGING_PALETTES,
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
    ComboPlotResult,
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

# ── 类型定义 (Type Definitions) ─────────────────────────────────
from sciplot._core.types import (
    # 基础类型
    Array,
    NumericArray,
    IntArray,
    BoolArray,
    OptionalArray,
    # 图表类型
    VenueType,
    LangType,
    PaletteType,
    CmapType,
    LineStyleType,
    MarkerType,
    LegendLocType,
    AlignType,
    VaAlignType,
    # 参数类型
    PlotKwargs,
    LabelsType,
    TitleType,
    XLabelType,
    YLabelType,
    ZLabelType,
    # 返回值类型
    ColorRGB,
    ColorRGBA,
    FigSize,
    ConfigDict,
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
    plot_lollipop,
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
    plot_slope,
)
from sciplot._plots.multivariate import (
    plot_parallel,
    plot_scatter_matrix,
)
from sciplot._plots.statistical import (
    plot_residuals,
    plot_qq,
    plot_bland_altman,
    plot_density,
    plot_multi_density,
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


_LAZY_EXT = {
    "plot_network": ("sciplot._ext.network", "networkx"),
    "plot_network_from_matrix": ("sciplot._ext.network", "networkx"),
    "plot_network_communities": ("sciplot._ext.network", "networkx"),
    "plot_dendrogram": ("sciplot._ext.hierarchical", "scipy"),
    "plot_clustermap": ("sciplot._ext.hierarchical", "scipy"),
    "plot_venn2": ("sciplot._ext.venn", "matplotlib-venn"),
    "plot_venn3": ("sciplot._ext.venn", "matplotlib-venn"),
}
_LAZY_EXT_LOCK = _Lock()


def __getattr__(name: str) -> Any:
    """延迟加载扩展模块。
    
    当访问需要额外依赖的函数时，动态导入相应模块。
    如果依赖未安装，提供详细的安装指导。
    """
    if name not in _LAZY_EXT:
        raise AttributeError(f"module 'sciplot' has no attribute {name!r}")
    
    with _LAZY_EXT_LOCK:
        if name in globals():
            return globals()[name]
        
        import importlib

        module_path, dep_name = _LAZY_EXT[name]
        try:
            mod = importlib.import_module(module_path)
            attr = getattr(mod, name)
        except ImportError as e:
            install_cmd_uv = f"uv pip install {dep_name}"
            install_cmd_pip = f"pip install {dep_name}"
            raise ImportError(
                f"sp.{name}() 需要安装 {dep_name}。\n"
                f"推荐安装方式: {install_cmd_uv}\n"
                f"或: {install_cmd_pip}"
            ) from e

        globals()[name] = attr
        return attr


def inspect() -> None:
    """输出 SciPlot 运行环境诊断信息。"""
    import importlib
    import importlib.util

    print(f"SciPlot Academic v{__version__} 环境诊断")
    print("=" * 38)

    def _check_pkg(import_name: str, display_name: str) -> None:
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            print(f"[MISS] {display_name:<16} 未安装")
            return
        try:
            mod = importlib.import_module(import_name)
            ver = getattr(mod, "__version__", "unknown")
        except Exception:
            ver = "unknown"
        print(f"[OK]   {display_name:<16} {ver}")

    _check_pkg("matplotlib", "matplotlib")
    _check_pkg("numpy", "numpy")
    _check_pkg("scienceplots", "scienceplots")
    _check_pkg("scipy", "scipy")
    _check_pkg("networkx", "networkx")
    _check_pkg("matplotlib_venn", "matplotlib-venn")
    _check_pkg("sklearn", "scikit-learn")

    try:
        from matplotlib import font_manager

        font_names = {f.name for f in font_manager.fontManager.ttflist}
        print("\n字体检查:")
        print("[OK]   SimSun" if "SimSun" in font_names else "[MISS] SimSun")
        print("[OK]   Times New Roman" if "Times New Roman" in font_names else "[MISS] Times New Roman")
    except Exception:
        print("\n字体检查: 无法读取字体列表")

    print("\n配色信息:")
    preview = ", ".join(list_palettes()[:12])
    print(f"已注册配色(前12个): {preview}")

    try:
        import matplotlib.pyplot as plt

        current_figsize = tuple(float(v) for v in plt.rcParams.get("figure.figsize", (0.0, 0.0)))
        guessed_venue = "unknown"
        for venue_name, venue_cfg in VENUES.items():
            v_w, v_h = venue_cfg.figsize
            if abs(current_figsize[0] - v_w) < 1e-6 and abs(current_figsize[1] - v_h) < 1e-6:
                guessed_venue = venue_name
                break

        from sciplot._core.style import get_current_lang

        active_lang = get_current_lang() or "unknown"
        print(
            "当前活跃: "
            f"figsize={current_figsize} (推断 venue≈{guessed_venue}), "
            f"lang={active_lang}"
        )
    except Exception:
        print("当前活跃: 无法读取 rcParams 状态")

    print(
        f"当前默认: venue={get_config('venue')}, "
        f"palette={get_config('palette')}, lang={get_config('lang')}"
    )


def _freeze_palette_mapping(data: Mapping[str, Sequence[str]]) -> _MappingProxyType:
    """导出层提供只读映射，值保持 List 类型不变（与 get_palette() 一致）。"""
    return _MappingProxyType(data)


# 对外公开常量使用只读视图；如需可变副本请使用 get_palette()。
PASTEL_PALETTE: Mapping[str, Tuple[str, ...]] = _freeze_palette_mapping(PASTEL_PALETTE)
EARTH_PALETTE: Mapping[str, Tuple[str, ...]] = _freeze_palette_mapping(EARTH_PALETTE)
OCEAN_PALETTE: Mapping[str, Tuple[str, ...]] = _freeze_palette_mapping(OCEAN_PALETTE)
FOREST_PALETTE: Mapping[str, Tuple[str, ...]] = _freeze_palette_mapping(FOREST_PALETTE)
SUNSET_PALETTE: Mapping[str, Tuple[str, ...]] = _freeze_palette_mapping(SUNSET_PALETTE)
RMB_PALETTES: Mapping[str, Tuple[str, ...]] = _freeze_palette_mapping(RMB_PALETTES)
DIVERGING_PALETTES: Mapping[str, Tuple[str, ...]] = _freeze_palette_mapping(DIVERGING_PALETTES)
RESIDENT_PALETTES: Mapping[str, Tuple[str, ...]] = _freeze_palette_mapping(RESIDENT_PALETTES)
ALL_PALETTES = tuple(ALL_PALETTES)
LINE_STYLES = tuple(LINE_STYLES)
MARKERS = tuple(MARKERS)


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
    "list_forest_subsets", "list_sunset_subsets", "list_rmb_palettes",
    "list_diverging_palettes", "list_color_schemes",
    "auto_select_palette",

    # ── 布局 ──
    "new_figure", "save",
    "create_subplots", "paper_subplots", "create_gridspec", "create_twinx",
    "add_panel_labels", "list_paper_layouts",

    # ── 链式调用 ──
    "style", "palette", "chain", "inspect",
    "PlotChain", "FigureWrapper",

    # ── 上下文管理器 ──
    "style_context", "context",
    "ieee_context", "nature_context", "thesis_context",
    "StyleContext",

    # ── 返回类型 ──
    "PlotResult", "ComboPlotResult", "GridSpecResult",

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
    "plot_bar", "plot_grouped_bar", "plot_stacked_bar", "plot_horizontal_bar", "plot_lollipop",
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
    "plot_timeseries", "plot_multi_timeseries", "plot_slope",

    # ── 多维图表 ──
    "plot_parallel", "plot_scatter_matrix",

    # ── 统计图表 ──
    "plot_residuals", "plot_qq", "plot_bland_altman", "plot_density", "plot_multi_density",

    # ── 机器学习扩展 ──
    "plot_pca", "plot_confusion_matrix",
    "plot_feature_importance", "plot_learning_curve",

    # ── 3D 扩展 ──
    "plot_surface", "plot_contour", "plot_3d_scatter", "plot_wireframe",

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
    "FOREST_PALETTE", "SUNSET_PALETTE", "RMB_PALETTES", "DIVERGING_PALETTES",
    "LINE_STYLES", "MARKERS", "DEFAULT_PALETTE", "ALL_PALETTES",

    # ── 状态 ──
    "HAS_SCIENCEPLOTS",

    # ── 延迟加载扩展 ──
    "plot_network",
    "plot_network_from_matrix",
    "plot_network_communities",
    "plot_dendrogram",
    "plot_clustermap",
    "plot_venn2",
    "plot_venn3",
]

