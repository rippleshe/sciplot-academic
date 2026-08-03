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
from sciplot._plots.flow import plot_sankey, plot_waterfall
from sciplot._plots.proportions import plot_treemap, plot_donut
from sciplot._plots.polar import (
    plot_radar,
    plot_taylor,
    plot_circular_barplot,
)
from sciplot._plots.multivariate import (
    plot_ternary,
)
from sciplot._plots.timeseries import (
    plot_timeseries,
    plot_multi_timeseries,
    plot_gantt,
    plot_calendar_heatmap,
    plot_streamgraph,
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
)
from sciplot._ext.plot3d import (
    plot_waterfall3d,
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
treemap = _make_alias(plot_treemap)
donut = _make_alias(plot_donut)
streamgraph = _make_alias(plot_streamgraph)
combo = _make_alias(plot_combo)

# ═══════════════════════════════════════════════════════════════
# 极坐标 / 时序 / 统计图表
# ═══════════════════════════════════════════════════════════════
radar = _make_alias(plot_radar)
taylor = _make_alias(plot_taylor)
circular_barplot = _make_alias(plot_circular_barplot)
ternary = _make_alias(plot_ternary)
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
waterfall3d = _make_alias(plot_waterfall3d)


__all__ = [
    "line", "scatter", "step", "area",
    "multi", "multi_line", "multi_area",
    "bar", "grouped_bar", "stacked_bar", "hbar",
    "hist", "box", "violin", "beeswarm", "dumbbell", "diverging_bar", "waffle", "lollipop",
    "errorbar", "confidence", "heatmap", "bubble_heatmap", "bubble", "hexbin", "marginal", "packed_bubble", "chord", "combo", "sankey", "treemap", "donut", "streamgraph", "waterfall",
    "radar", "taylor", "circular_barplot", "ternary", "timeseries", "multi_timeseries", "gantt", "calendar_heatmap",
    "density", "multi_density",
    "residuals", "qq", "bland_altman", "ridgeline", "raincloud", "volcano", "waterfall3d",
]
