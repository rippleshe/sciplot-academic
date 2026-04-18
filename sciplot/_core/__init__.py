"""
SciPlot 核心模块
"""

from sciplot._core.registry import (
    PlotterMetadata,
    PLOTTER_REGISTRY,
    register_plotter,
    get_plotter,
    list_plotters,
)
from sciplot._core.style import setup_style, reset_style
from sciplot._core.palette import (
    apply_palette,
    set_custom_palette,
    get_palette,
    list_palettes,
    list_resident_palettes,
    list_pastel_subsets,
    list_earth_subsets,
    list_ocean_subsets,
    list_forest_subsets,
    list_sunset_subsets,
    list_all_palettes,
)
from sciplot._core.layout import (
    new_figure,
    create_subplots,
    paper_subplots,
    create_gridspec,
    create_twinx,
    add_panel_labels,
    save,
)
from sciplot._core.config import (
    SciPlotConfig,
    set_defaults,
    get_config,
    load_config,
    reset_config,
)

__all__ = [
    "PlotterMetadata",
    "PLOTTER_REGISTRY",
    "register_plotter",
    "get_plotter",
    "list_plotters",
    "setup_style",
    "reset_style",
    "apply_palette",
    "set_custom_palette",
    "get_palette",
    "list_palettes",
    "list_resident_palettes",
    "list_pastel_subsets",
    "list_earth_subsets",
    "list_ocean_subsets",
    "list_forest_subsets",
    "list_sunset_subsets",
    "list_all_palettes",
    "new_figure",
    "create_subplots",
    "paper_subplots",
    "create_gridspec",
    "create_twinx",
    "add_panel_labels",
    "save",
    "SciPlotConfig",
    "set_defaults",
    "get_config",
    "load_config",
    "reset_config",
]
