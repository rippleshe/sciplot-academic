"""
SciPlot 图表模块
"""

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

__all__ = [
    # 折线 / 散点 / 面积
    "plot_line",
    "plot",
    "plot_multi",
    "plot_multi_line",
    "plot_scatter",
    "plot_step",
    "plot_area",
    "plot_multi_area",
    # 分布 / 统计
    "plot_bar",
    "plot_grouped_bar",
    "plot_stacked_bar",
    "plot_horizontal_bar",
    "plot_lollipop",
    "plot_box",
    "plot_violin",
    "plot_histogram",
    "plot_combo",
    "annotate_significance",
    # 高级
    "plot_errorbar",
    "plot_confidence",
    "plot_heatmap",
    # 极坐标
    "plot_radar",
    # 时序
    "plot_timeseries",
    "plot_multi_timeseries",
    "plot_slope",
    # 多维
    "plot_parallel",
    "plot_scatter_matrix",
    # 统计
    "plot_residuals",
    "plot_qq",
    "plot_bland_altman",
    "plot_density",
    "plot_multi_density",
    # 常量
    "LINE_STYLES",
    "MARKERS",
]
