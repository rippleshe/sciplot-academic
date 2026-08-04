"""
简洁函数别名 — 更短的绘图函数名

提供常用绘图函数的简短别名，使代码更简洁。
所有别名都保持与原函数完全相同的参数和行为。

使用 functools.wraps 自动保持原函数的签名、文档和类型提示，
无需手动维护参数列表。
"""

from __future__ import annotations

import functools
from typing import Any, Callable, TypeVar

from sciplot._plots.basic import (
    plot_line,
    plot_multi,
    plot_multi_line,
    plot_scatter,
    plot_step,
    plot_area,
    plot_multi_area,
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
    plot_beeswarm,
    plot_dumbbell,
    plot_diverging_bar,
    plot_waffle,
)
from sciplot._plots.advanced import (
    plot_errorbar,
    plot_confidence,
    plot_heatmap,
    plot_bubble_heatmap,
    plot_bubble,
    plot_hexbin,
    plot_marginal,
    plot_packed_bubble,
    plot_chord,
)
from sciplot._plots.flow import plot_sankey, plot_waterfall, plot_alluvial
from sciplot._plots.proportions import plot_treemap, plot_donut, plot_sunburst
from sciplot._plots.sets import plot_upset
from sciplot._plots.polar import (
    plot_radar,
    plot_taylor,
    plot_circular_barplot,
)
from sciplot._plots.multivariate import (
    plot_ternary,
    plot_parallel,
)
from sciplot._plots.timeseries import (
    plot_timeseries,
    plot_multi_timeseries,
    plot_gantt,
    plot_calendar_heatmap,
    plot_streamgraph,
    plot_bump,
    plot_slope,
)
from sciplot._plots.statistical import (
    plot_density,
    plot_multi_density,
    plot_residuals,
    plot_qq,
    plot_bland_altman,
    plot_ridgeline,
    plot_raincloud,
    plot_volcano,
    plot_forest,
    plot_funnel,
)
from sciplot._ext.plot3d import (
    plot_waterfall3d,
    plot_surface,
    plot_contour,
)
from sciplot._ext.ml import (
    plot_confusion_matrix,
    plot_feature_importance,
    plot_learning_curve,
    plot_pca,
)
from sciplot._ext.network import (
    plot_network,
)
from sciplot._ext.venn import (
    plot_venn2,
    plot_venn3,
)

F = TypeVar("F", bound=Callable[..., Any])


def _make_alias(func: F) -> F:
    """创建函数别名，自动转发所有参数并保留原函数签名/文档/类型提示。

    使用 functools.wraps 确保：
    - IDE 自动补全显示原函数的参数列表
    - help() 显示原函数的文档
    - mypy/pyright 类型检查正常
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)
    wrapper.__qualname__ = wrapper.__qualname__.replace(func.__name__, f"<alias of {func.__name__}>")
    return wrapper  # type: ignore[return-value]


# ═══════════════════════════════════════════════════════════════
# 基础图表
# ═══════════════════════════════════════════════════════════════
line = _make_alias(plot_line)
scatter = _make_alias(plot_scatter)
step = _make_alias(plot_step)
area = _make_alias(plot_area)

# ═══════════════════════════════════════════════════════════════
# 多系列图表
# ═══════════════════════════════════════════════════════════════
multi = _make_alias(plot_multi)
multi_line = _make_alias(plot_multi_line)
multi_area = _make_alias(plot_multi_area)

# ═══════════════════════════════════════════════════════════════
# 分布统计图表
# ═══════════════════════════════════════════════════════════════
bar = _make_alias(plot_bar)
grouped_bar = _make_alias(plot_grouped_bar)
stacked_bar = _make_alias(plot_stacked_bar)
hbar = _make_alias(plot_horizontal_bar)
hist = _make_alias(plot_histogram)
box = _make_alias(plot_box)
violin = _make_alias(plot_violin)
beeswarm = _make_alias(plot_beeswarm)
dumbbell = _make_alias(plot_dumbbell)
diverging_bar = _make_alias(plot_diverging_bar)
waffle = _make_alias(plot_waffle)
lollipop = _make_alias(plot_lollipop)

# ═══════════════════════════════════════════════════════════════
# 高级图表
# ═══════════════════════════════════════════════════════════════
errorbar = _make_alias(plot_errorbar)
confidence = _make_alias(plot_confidence)
heatmap = _make_alias(plot_heatmap)
bubble_heatmap = _make_alias(plot_bubble_heatmap)
bubble = _make_alias(plot_bubble)
hexbin = _make_alias(plot_hexbin)
marginal = _make_alias(plot_marginal)
packed_bubble = _make_alias(plot_packed_bubble)
chord = _make_alias(plot_chord)
sankey = _make_alias(plot_sankey)
waterfall = _make_alias(plot_waterfall)
alluvial = _make_alias(plot_alluvial)
treemap = _make_alias(plot_treemap)
donut = _make_alias(plot_donut)
sunburst = _make_alias(plot_sunburst)
upset = _make_alias(plot_upset)
streamgraph = _make_alias(plot_streamgraph)
bump = _make_alias(plot_bump)
combo = _make_alias(plot_combo)

# ═══════════════════════════════════════════════════════════════
# 极坐标 / 时序 / 统计图表
# ═══════════════════════════════════════════════════════════════
radar = _make_alias(plot_radar)
taylor = _make_alias(plot_taylor)
circular_barplot = _make_alias(plot_circular_barplot)
ternary = _make_alias(plot_ternary)
parallel = _make_alias(plot_parallel)
pca = _make_alias(plot_pca)
slope = _make_alias(plot_slope)
surface = _make_alias(plot_surface)
contour = _make_alias(plot_contour)
confusion = _make_alias(plot_confusion_matrix)
learning_curve = _make_alias(plot_learning_curve)
feature_importance = _make_alias(plot_feature_importance)
venn2 = _make_alias(plot_venn2)
venn3 = _make_alias(plot_venn3)
network = _make_alias(plot_network)
timeseries = _make_alias(plot_timeseries)
multi_timeseries = _make_alias(plot_multi_timeseries)
gantt = _make_alias(plot_gantt)
calendar_heatmap = _make_alias(plot_calendar_heatmap)
density = _make_alias(plot_density)
multi_density = _make_alias(plot_multi_density)
residuals = _make_alias(plot_residuals)
qq = _make_alias(plot_qq)
bland_altman = _make_alias(plot_bland_altman)
ridgeline = _make_alias(plot_ridgeline)
raincloud = _make_alias(plot_raincloud)
volcano = _make_alias(plot_volcano)
forest = _make_alias(plot_forest)
funnel = _make_alias(plot_funnel)
waterfall3d = _make_alias(plot_waterfall3d)


__all__ = [
    "line", "scatter", "step", "area",
    "multi", "multi_line", "multi_area",
    "bar", "grouped_bar", "stacked_bar", "hbar",
    "hist", "box", "violin", "beeswarm", "dumbbell", "diverging_bar", "waffle", "lollipop",
    "errorbar", "confidence", "heatmap", "bubble_heatmap", "bubble", "hexbin", "marginal", "packed_bubble", "chord", "combo", "sankey", "treemap", "donut", "streamgraph", "waterfall", "alluvial", "bump", "sunburst", "upset",
    "radar", "taylor", "circular_barplot", "ternary", "timeseries", "multi_timeseries", "gantt", "calendar_heatmap",
    "parallel", "pca", "slope", "surface", "contour",
    "confusion", "learning_curve", "feature_importance",
    "venn2", "venn3", "network",
    "density", "multi_density",
    "residuals", "qq", "bland_altman", "ridgeline", "raincloud", "volcano", "forest", "funnel", "waterfall3d",
]
