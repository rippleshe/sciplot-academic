"""
时序图表 — 时间序列专用图

支持事件标注、背景区域、滚动均值等时序数据特有功能。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Sequence
import warnings

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


def _normalize_events(events: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """校验并标准化事件标注配置。"""
    if not events:
        return []
    if not isinstance(events, list):
        raise TypeError("events 必须是字典列表")

    normalized: List[Dict[str, Any]] = []
    for i, event in enumerate(events):
        if not isinstance(event, dict):
            raise TypeError(f"events[{i}] 必须是字典")
        if "time" not in event or event.get("time") is None:
            raise ValueError(f"events[{i}] 缺少必需字段 'time'")
        normalized.append(
            {
                "time": event["time"],
                "label": event.get("label", ""),
                "color": event.get("color", "red"),
            }
        )
    return normalized


def _normalize_shade_regions(
    shade_regions: Optional[List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """校验并标准化背景区域配置。"""
    if not shade_regions:
        return []
    if not isinstance(shade_regions, list):
        raise TypeError("shade_regions 必须是字典列表")

    normalized: List[Dict[str, Any]] = []
    for i, region in enumerate(shade_regions):
        if not isinstance(region, dict):
            raise TypeError(f"shade_regions[{i}] 必须是字典")
        if "start" not in region or region.get("start") is None:
            raise ValueError(f"shade_regions[{i}] 缺少必需字段 'start'")
        if "end" not in region or region.get("end") is None:
            raise ValueError(f"shade_regions[{i}] 缺少必需字段 'end'")
        normalized.append(
            {
                "start": region["start"],
                "end": region["end"],
                "color": region.get("color", "#CCCCCC"),
                "alpha": region.get("alpha", 0.2),
            }
        )
    return normalized


def _is_numeric_time_value(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    return isinstance(value, (int, float, np.number))


def _is_datetime_time_value(value: Any) -> bool:
    return isinstance(value, (datetime, date, np.datetime64))


def _validate_time_value_for_axis(value: Any, x_type: str, field_name: str) -> None:
    if x_type == "datetime":
        if not _is_datetime_time_value(value):
            raise TypeError(
                f"{field_name} 必须是 datetime/date 类型，实际类型: {type(value).__name__}"
            )
    else:
        if not _is_numeric_time_value(value):
            raise TypeError(
                f"{field_name} 必须是数值类型，实际类型: {type(value).__name__}"
            )


def _validate_annotations_axis_compatibility(
    events: List[Dict[str, Any]],
    regions: List[Dict[str, Any]],
    x_type: str,
) -> None:
    for i, event in enumerate(events):
        _validate_time_value_for_axis(event["time"], x_type, f"events[{i}]['time']")

    for i, region in enumerate(regions):
        _validate_time_value_for_axis(region["start"], x_type, f"shade_regions[{i}]['start']")
        _validate_time_value_for_axis(region["end"], x_type, f"shade_regions[{i}]['end']")


def plot_timeseries(
    t: Union[Sequence[Any], np.ndarray],
    y: Union[Sequence[Any], np.ndarray],
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
    lang: Optional[str] = None,
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
    y = np.asarray(y, dtype=float)

    if len(t) != len(y):
        raise ValueError(f"t 长度 ({len(t)}) 与 y 长度 ({len(y)}) 不一致")
    if np.any(np.isinf(y)):
        warnings.warn(
            "y 数据包含 Inf 值，可能导致图形显示异常",
            UserWarning,
            stacklevel=2,
        )
    if rolling_mean is not None:
        if not isinstance(rolling_mean, int):
            raise TypeError(f"rolling_mean 必须是整数或 None，实际类型: {type(rolling_mean).__name__}")
        if rolling_mean <= 0:
            raise ValueError(f"rolling_mean 必须为正整数，实际值: {rolling_mean}")

    events_normalized = _normalize_events(events)
    regions_normalized = _normalize_shade_regions(shade_regions)

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

    x_type = _detect_x_type(t)
    _validate_annotations_axis_compatibility(events_normalized, regions_normalized, x_type)

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]
    main_color = colors[0]

    for region in regions_normalized:
        ax.axvspan(
            region["start"],
            region["end"],
            color=region["color"],
            alpha=region["alpha"],
            zorder=0,
        )

    ax.plot(t, y, label=label, marker=marker, color=main_color, **kwargs)
    has_legend_item = bool(label)

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
        has_legend_item = True

    for event in events_normalized:
        event_time = event["time"]
        event_label = event["label"]
        event_color = event["color"]

        ax.axvline(x=event_time, color=event_color, linestyle="--", alpha=0.7)

        ax.annotate(
            event_label,
            xy=(event_time, 0.95),
            xycoords=("data", "axes fraction"),
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
    if has_legend_item:
        ax.legend()
    ax.tick_params(direction="in")

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_multi_timeseries(
    t: Union[Sequence[Any], np.ndarray],
    y_list: List[np.ndarray],
    labels: Optional[List[str]] = None,
    events: Optional[List[Dict[str, Any]]] = None,
    shade_regions: Optional[List[Dict[str, Any]]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
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
    if not y_list:
        raise ValueError("参数 'y_list' 不能为空列表")

    if labels is None:
        labels = [f"系列 {i+1}" for i in range(len(y_list))]
    elif len(labels) != len(y_list):
        raise ValueError(
            f"labels 长度 ({len(labels)}) 与 y_list 长度 ({len(y_list)}) 不一致"
        )

    events_normalized = _normalize_events(events)
    regions_normalized = _normalize_shade_regions(shade_regions)

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

    x_type = _detect_x_type(t)
    _validate_annotations_axis_compatibility(events_normalized, regions_normalized, x_type)

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

    for region in regions_normalized:
        ax.axvspan(
            region["start"],
            region["end"],
            color=region["color"],
            alpha=region["alpha"],
            zorder=0,
        )

    for i, (y, lbl) in enumerate(zip(y_list, labels)):
        y = np.asarray(y, dtype=float)
        if len(t) != len(y):
            raise ValueError(f"t 长度 ({len(t)}) 与 y_list[{i}] 长度 ({len(y)}) 不一致")
        if np.any(np.isinf(y)):
            warnings.warn(
                f"y_list[{i}] 包含 Inf 值，可能导致图形显示异常",
                UserWarning,
                stacklevel=2,
            )
        ax.plot(t, y, label=lbl, color=colors[i % len(colors)], **kwargs)

    for event in events_normalized:
        event_time = event["time"]
        event_label = event["label"]
        event_color = event["color"]
        ax.axvline(x=event_time, color=event_color, linestyle="--", alpha=0.7)
        ax.annotate(
            event_label,
            xy=(event_time, 0.95),
            xycoords=("data", "axes fraction"),
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


def plot_slope(
    labels: List[str],
    before: Union[List[float], np.ndarray],
    after: Union[List[float], np.ndarray],
    left_label: str = "Before",
    right_label: str = "After",
    show_diff: bool = True,
    show_grid: bool = False,
    title: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制斜率图，展示两时点或两条件变化。"""
    if not labels:
        raise ValueError("参数 'labels' 不能为空列表")

    before_arr = np.asarray(before, dtype=float)
    after_arr = np.asarray(after, dtype=float)

    if before_arr.ndim != 1 or after_arr.ndim != 1:
        raise ValueError("before 和 after 必须是一维数组")
    if len(labels) != len(before_arr) or len(labels) != len(after_arr):
        raise ValueError(
            "labels、before、after 长度必须一致"
        )
    if not np.all(np.isfinite(before_arr)) or not np.all(np.isfinite(after_arr)):
        raise ValueError("before 和 after 不能包含 NaN 或 Inf")

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]
    if not colors:
        colors = ["#1f77b4", "#ff7f0e"]

    x_positions = np.array([0.0, 1.0])
    left_x, right_x = x_positions

    for i, (name, b_val, a_val) in enumerate(zip(labels, before_arr, after_arr)):
        color = colors[i % len(colors)]
        ax.plot(x_positions, [b_val, a_val], marker="o", color=color, alpha=0.85, **kwargs)

        ax.text(left_x - 0.03, b_val, f"{name}", ha="right", va="center")
        if show_diff:
            diff = a_val - b_val
            ax.text(right_x + 0.03, a_val, f"{a_val:.2f} ({diff:+.2f})", ha="left", va="center")
        else:
            ax.text(right_x + 0.03, a_val, f"{a_val:.2f}", ha="left", va="center")

    y_min = float(np.nanmin(np.concatenate([before_arr, after_arr])))
    y_max = float(np.nanmax(np.concatenate([before_arr, after_arr])))
    y_margin = (y_max - y_min) * 0.08 if y_max > y_min else max(abs(y_max) * 0.08, 0.5)

    ax.set_xlim(-0.25, 1.25)
    ax.set_ylim(y_min - y_margin, y_max + y_margin)
    ax.set_xticks([left_x, right_x])
    ax.set_xticklabels([left_label, right_label])
    if title:
        ax.set_title(title)
    if show_grid:
        ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.tick_params(direction="in")

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = ["plot_timeseries", "plot_multi_timeseries", "plot_slope"]
