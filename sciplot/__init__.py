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

配色体系（三大常驻系列 + 人民币系列）:
    pastel / pastel-1/2/3/4  — 柔和粉彩（默认）
    earth  / earth-1/2/3/4   — 大地色系
    ocean  / ocean-1/2/3/4   — 海洋蓝绿
    100yuan / 50yuan / ...    — 人民币系列

期刊样式:
    nature（默认）| ieee | aps | springer | thesis | presentation
"""

__version__ = "1.6.0"
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
    get_palette,
    list_palettes,
    list_all_palettes,
    list_resident_palettes,
    list_pastel_subsets,
    list_earth_subsets,
    list_ocean_subsets,
    list_rmb_palettes,
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

# ── 图表 ──────────────────────────────────────────────────────
from sciplot._plots.basic import (
    plot_line,
    plot,
    plot_multi,
    plot_multi_line,
    plot_scatter,
    plot_step,
    LINE_STYLES,
    MARKERS,
)
from sciplot._plots.distribution import (
    plot_bar,
    plot_grouped_bar,
    plot_box,
    plot_violin,
    plot_histogram,
    annotate_significance,
)
from sciplot._plots.advanced import (
    plot_errorbar,
    plot_confidence,
    plot_heatmap,
)

# ── 工具 ──────────────────────────────────────────────────────
from sciplot.utils import (
    hex_to_rgb,
    rgb_to_hex,
    lighten_color,
    darken_color,
    generate_gradient,
)


__all__ = [
    "__version__",

    # ── 样式 ──
    "setup_style", "reset_style", "get_venue_info",
    "list_venues", "list_languages",

    # ── 配色 ──
    "set_custom_palette", "get_palette",
    "list_palettes", "list_all_palettes", "list_resident_palettes",
    "list_pastel_subsets", "list_earth_subsets", "list_ocean_subsets",
    "list_rmb_palettes",

    # ── 布局 ──
    "new_figure", "save",
    "create_subplots", "paper_subplots", "create_gridspec", "create_twinx",
    "add_panel_labels", "list_paper_layouts",

    # ── 折线 / 散点 ──
    "plot", "plot_line", "plot_multi", "plot_multi_line",
    "plot_scatter", "plot_step",

    # ── 分布 / 统计 ──
    "plot_bar", "plot_grouped_bar",
    "plot_box", "plot_violin", "plot_histogram",
    "annotate_significance",

    # ── 高级 ──
    "plot_errorbar", "plot_confidence", "plot_heatmap",

    # ── 颜色工具 ──
    "hex_to_rgb", "rgb_to_hex",
    "lighten_color", "darken_color", "generate_gradient",

    # ── 常量 ──
    "VENUES", "PAPER_LAYOUTS", "LANGUAGES",
    "RMB_PALETTES", "RESIDENT_PALETTES",
    "PASTEL_PALETTE", "EARTH_PALETTE", "OCEAN_PALETTE",
    "LINE_STYLES", "MARKERS", "DEFAULT_PALETTE", "ALL_PALETTES",

    # ── 状态 ──
    "HAS_SCIENCEPLOTS",
]
