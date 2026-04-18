"""
时序图表 — 时间序列专用图

支持事件标注、背景区域、滚动均值等时序数据特有功能。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from datetime import date, datetime

from sciplot._core.layout import new_figure
from sciplot._core.utils import apply_resolved_style
from sciplot._core.result import PlotResult


def _is_datetime(data: np.ndarray) -> bool:
    """判断数据是否为 datetime 类型"""
    if len(data) == 0:
        return False
    first = data[0]
    if isinstance(first, (datetime, date, np.datetime64)):
        return True
    if hasattr(first, "dtype") and np.issubdtype(first.dtype, np.datetime64):
        return True
    return False


def _detect_x_type(t: np.ndarray) -> str:
    """自动检测 x 轴类型"""
    if _is_datetime(t):
        return "datetime"
    return "numeric"


def plot_timeseries(
    t: Union[List, np.ndarray],
    y: Union[List, np.ndarray],
    events: Optional[List[Dict[str, Any]]] = None,
    shade_regions: Optional[List[Dict[str, Any]]] = None,
    rolling_mean: Optional[int] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    label: str = "",
    marker: Optional[str] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制时序图（支持事件标注、背景区域、滚动均值）

    参数:
        t            : 时间轴数据（datetime 或数值）
        y            : 数值序列
        events       : 事件标注列表，每个元素为 {"time": x, "label": "事件名", "color": "..."}
        shade_regions: 背景区域列表，每个元素为 {"start": x, "end": y, "color": "...", "alpha": 0.2}
        rolling_mean : 滚动均值窗口大小，None 则不绘制
        marker       : 数据点标记样式
        xlabel       : X 轴标签（datetime 类型会自动格式化）
        ylabel       : Y 轴标签
        title        : 图标题
        label        : 数据系列标签

    示例:
        >>> import datetime
        >>> dates = [datetime.date(2024, 1, i) for i in range(1, 32)]
        >>> values = np.random.randn(31).cumsum()
        >>> 
        >>> # 简单时序图
        >>> fig, ax = sp.plot_timeseries(dates, values, xlabel="日期", ylabel="数值")
        >>> 
        >>> # 带事件标注和背景区域
        >>> fig, ax = sp.plot_timeseries(
        ...     dates, values,
        ...     events=[
        ...         {"time": datetime.date(2024, 1, 10), "label": "上线"},
        ...         {"time": datetime.date(2024, 1, 20), "label": "更新"},
        ...     ],
        ...     shade_regions=[
        ...         {"start": datetime.date(2024, 1, 5), "end": datetime.date(2024, 1, 15)},
        ...     ],
        ...     rolling_mean=7,
        ... )
    """
    t = np.asarray(t)
    y = np.asarray(y)

    if len(t) != len(y):
        raise ValueError(f"t 长度 ({len(t)}) 与 y 长度 ({len(y)}) 不一致")

    effective_venue = apply_resolved_style(venue, palette)
    fig, ax = new_figure(effective_venue)

    x_type = _detect_x_type(t)

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]
    main_color = colors[0]

    if shade_regions:
        for i, region in enumerate(shade_regions):
            start = region.get("start")
            end = region.get("end")
            color = region.get("color", "#CCCCCC")
            alpha = region.get("alpha", 0.2)
            ax.axvspan(start, end, color=color, alpha=alpha, zorder=0)

    ax.plot(t, y, label=label, marker=marker, color=main_color, **kwargs)

    if rolling_mean and rolling_mean > 1 and len(y) >= rolling_mean:
        rolling = np.convolve(y, np.ones(rolling_mean) / rolling_mean, mode="valid")
        rolling_t = t[rolling_mean - 1:]
        ax.plot(
            rolling_t, rolling,
            label=f"滚动均值 (n={rolling_mean})",
            color=colors[1 % len(colors)] if len(colors) > 1 else main_color,
            linestyle="--",
            linewidth=2,
        )

    if events:
        for i, event in enumerate(events):
            event_time = event.get("time")
            event_label = event.get("label", "")
            event_color = event.get("color", "red")

            ax.axvline(x=event_time, color=event_color, linestyle="--", alpha=0.7)

            y_pos = ax.get_ylim()[1] * 0.95
            ax.annotate(
                event_label,
                xy=(event_time, y_pos),
                xytext=(5, 0),
                textcoords="offset points",
                ha="left", va="top",
                fontsize=plt.rcParams.get("font.size", 9) - 1,
                color=event_color,
            )

    if x_type == "datetime":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    if label or rolling_mean:
        ax.legend()
    ax.tick_params(direction="in")

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_multi_timeseries(
    t: Union[List, np.ndarray],
    y_list: List[np.ndarray],
    labels: Optional[List[str]] = None,
    events: Optional[List[Dict[str, Any]]] = None,
    shade_regions: Optional[List[Dict[str, Any]]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制多条时序曲线

    参数:
        t            : 时间轴数据（共享）
        y_list       : 多组数值序列列表
        labels       : 各序列的标签
        events       : 事件标注列表
        shade_regions: 背景区域列表

    示例:
        >>> fig, ax = sp.plot_multi_timeseries(
        ...     dates, [train_loss, val_loss],
        ...     labels=["Train", "Validation"],
        ...     ylabel="Loss",
        ... )
    """
    t = np.asarray(t)

    if labels is None:
        labels = [f"系列 {i+1}" for i in range(len(y_list))]
    elif len(labels) != len(y_list):
        raise ValueError(
            f"labels 长度 ({len(labels)}) 与 y_list 长度 ({len(y_list)}) 不一致"
        )

    effective_venue = apply_resolved_style(venue, palette)
    fig, ax = new_figure(effective_venue)

    x_type = _detect_x_type(t)

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

    if shade_regions:
        for region in shade_regions:
            start = region.get("start")
            end = region.get("end")
            color = region.get("color", "#CCCCCC")
            alpha = region.get("alpha", 0.2)
            ax.axvspan(start, end, color=color, alpha=alpha, zorder=0)

    for i, (y, lbl) in enumerate(zip(y_list, labels)):
        y = np.asarray(y)
        if len(t) != len(y):
            raise ValueError(f"t 长度 ({len(t)}) 与 y_list[{i}] 长度 ({len(y)}) 不一致")
        ax.plot(t, y, label=lbl, color=colors[i % len(colors)], **kwargs)

    if events:
        for event in events:
            event_time = event.get("time")
            event_label = event.get("label", "")
            event_color = event.get("color", "red")
            ax.axvline(x=event_time, color=event_color, linestyle="--", alpha=0.7)
            y_pos = ax.get_ylim()[1] * 0.95
            ax.annotate(
                event_label,
                xy=(event_time, y_pos),
                xytext=(5, 0),
                textcoords="offset points",
                ha="left", va="top",
                fontsize=plt.rcParams.get("font.size", 9) - 1,
                color=event_color,
            )

    if x_type == "datetime":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.legend()
    ax.tick_params(direction="in")

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = ["plot_timeseries", "plot_multi_timeseries"]
