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

__all__ = [
    # 折线 / 散点
    "plot_line",
    "plot",
    "plot_multi",
    "plot_multi_line",
    "plot_scatter",
    "plot_step",
    # 分布 / 统计
    "plot_bar",
    "plot_grouped_bar",
    "plot_box",
    "plot_violin",
    "plot_histogram",
    "annotate_significance",
    # 高级
    "plot_errorbar",
    "plot_confidence",
    "plot_heatmap",
    # 常量
    "LINE_STYLES",
    "MARKERS",
]
