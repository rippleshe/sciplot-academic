"""
时序图表 — 时间序列专用图

支持事件标注、背景区域、滚动均值等时序数据特有功能。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Sequence
import warnings

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import numpy as np
from datetime import date, datetime, timedelta

from sciplot._core.layout import new_figure
from sciplot._core.utils import apply_resolved_style, get_cycle_colors
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

    colors = get_cycle_colors()
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

    colors = get_cycle_colors()

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

    colors = get_cycle_colors()
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


def plot_gantt(
    tasks: List[str],
    start: Union[Sequence[Any], np.ndarray],
    duration: Optional[Union[Sequence[float], np.ndarray]] = None,
    end: Optional[Union[Sequence[Any], np.ndarray]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    color_by: Optional[Union[List[str], np.ndarray]] = None,
    show_labels: bool = True,
    alpha: float = 0.85,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制甘特图（Gantt，任务进度时间线）

    每个任务一行水平条形，起点为 start、宽度为 duration（或由 end 推导），
    支持数值时间轴（天数/小时）与 datetime 时间轴。

    参数:
        tasks     : 任务名称列表
        start     : 任务开始时间（数值或 datetime/date 序列）
        duration  : 任务持续时长；数值轴为数值，日期轴为 timedelta 或天数
        end       : 任务结束时间（与 duration 二选一，优先 duration）
        color_by  : 每任务颜色或类别标签（等长）；None 用配色循环
        show_labels: 是否显示任务名称
        alpha     : 条形透明度

    示例:
        >>> # 数值时间轴（天数）
        >>> fig, ax = sp.plot_gantt(
        ...     ["数据采集", "模型训练", "论文撰写"],
        ...     start=[0, 10, 30], duration=[10, 20, 20],
        ...     xlabel="天数",
        ... )
        >>> sp.save(fig, "gantt")

        >>> # datetime 时间轴
        >>> import datetime
        >>> starts = [datetime.date(2024, 1, 1), datetime.date(2024, 1, 15)]
        >>> fig, ax = sp.plot_gantt(
        ...     ["阶段1", "阶段2"], start=starts, duration=[14, 21],
        ... )
    """
    if not tasks:
        raise ValueError("参数 'tasks' 不能为空列表")

    start_arr = np.asarray(start)
    if start_arr.ndim != 1 or len(start_arr) != len(tasks):
        raise ValueError(
            f"start 长度 ({len(start_arr)}) 与 tasks 长度 ({len(tasks)}) 不一致"
        )

    # 检测日期轴
    is_datetime = False
    if len(start_arr) > 0:
        first = start_arr[0]
        if isinstance(first, (datetime, date, np.datetime64)) or (
            hasattr(first, "dtype") and np.issubdtype(first.dtype, np.datetime64)
        ):
            is_datetime = True

    # 解析 duration / end
    if duration is not None and end is not None:
        raise ValueError("duration 与 end 只能二选一，不能同时提供")

    if duration is not None:
        dur_arr = np.asarray(duration, dtype=float).ravel()
        if len(dur_arr) != len(tasks):
            raise ValueError(
                f"duration 长度 ({len(dur_arr)}) 与 tasks 长度 ({len(tasks)}) 不一致"
            )
        if not np.all(np.isfinite(dur_arr)) or np.any(dur_arr <= 0):
            raise ValueError("duration 必须全部为正的有限数值")
        if is_datetime:
            # datetime 轴：duration 视为天数
            ends = [s + timedelta(days=float(d)) for s, d in zip(start_arr, dur_arr)]
        else:
            ends = [float(s) + float(d) for s, d in zip(start_arr, dur_arr)]
    elif end is not None:
        end_arr = np.asarray(end)
        if len(end_arr) != len(tasks):
            raise ValueError(
                f"end 长度 ({len(end_arr)}) 与 tasks 长度 ({len(tasks)}) 不一致"
            )
        if is_datetime:
            ends = list(end_arr)
        else:
            ends = [float(e) for e in end_arr]
            starts_float = [float(s) for s in start_arr]
            if np.any(np.asarray(ends) <= np.asarray(starts_float)):
                raise ValueError("end 必须全部大于 start")
    else:
        raise ValueError("必须提供 duration 或 end 之一")

    if is_datetime:
        starts_plot = [mdates.date2num(s) for s in start_arr]
        ends_plot = [mdates.date2num(e) for e in ends]
        widths = [e - s for s, e in zip(starts_plot, ends_plot)]
        if any(w <= 0 for w in widths):
            raise ValueError("end 必须全部大于 start")
    else:
        starts_plot = [float(s) for s in start_arr]
        widths = [e - s for s, e in zip(starts_plot, ends)]
        if any(w <= 0 for w in widths):
            raise ValueError("end 必须全部大于 start")

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)
    colors = get_cycle_colors()

    # 颜色解析：color_by 为类别时按类别着色
    if color_by is not None:
        c_arr = np.asarray(color_by).ravel()
        if len(c_arr) != len(tasks):
            raise ValueError(
                f"color_by 长度 ({len(c_arr)}) 与 tasks 长度 ({len(tasks)}) 不一致"
            )
        unique_vals = sorted(set(c_arr), key=str)
        color_map = {v: colors[i % len(colors)] for i, v in enumerate(unique_vals)}
        bar_colors = [color_map[v] for v in c_arr]
        legend_handles = [
            Patch(facecolor=c, label=str(v), alpha=alpha)
            for v, c in color_map.items()
        ]
    else:
        bar_colors = [colors[i % len(colors)] for i in range(len(tasks))]
        legend_handles = None

    y = np.arange(len(tasks))
    ax.barh(y, widths, left=starts_plot, color=bar_colors, alpha=alpha, **kwargs)

    if show_labels:
        ax.set_yticks(y)
        ax.set_yticklabels(tasks)
    else:
        ax.set_yticks([])

    if is_datetime:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    if legend_handles:
        ax.legend(handles=legend_handles, loc="lower right", frameon=False)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_calendar_heatmap(
    dates: Union[Sequence[Any], np.ndarray],
    values: Union[Sequence[float], np.ndarray],
    cmap: str = "YlOrRd",
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    colorbar_label: str = "",
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    weekday_start: int = 0,
    show_month_lines: bool = True,
    lang: Optional[str] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制日历热图（Calendar Heatmap，全年活动强度按周排列）

    每天一个格子：横轴为周序号，纵轴为星期，颜色编码数值，
    适合展示全年规律性活动（打卡、提交、流量、事件密度）。

    参数:
        dates          : 日期序列（datetime/date 或字符串日期）
        values         : 与日期对应的数值（等长，允许 0）
        cmap           : 颜色映射，默认 "YlOrRd"
        vmin / vmax    : 颜色映射范围
        colorbar_label : 颜色条标签
        weekday_start  : 周起始日（0=周一，6=周日），默认 0
        show_month_lines: 是否绘制月份分隔线
        lang           : 语言设置（星期标签语言，默认跟随当前）

    示例:
        >>> import datetime
        >>> dates = [datetime.date(2024, 1, 1) + datetime.timedelta(days=i)
        ...          for i in range(366)]
        >>> values = np.random.poisson(2, 366)
        >>> fig, ax = sp.plot_calendar_heatmap(
        ...     dates, values, colorbar_label="事件数",
        ... )
        >>> sp.save(fig, "calendar")
    """
    dates_arr = list(dates)
    values_arr = np.asarray(values, dtype=float).ravel()
    if len(dates_arr) != len(values_arr):
        raise ValueError(
            f"dates 长度 ({len(dates_arr)}) 与 values 长度 ({len(values_arr)}) 不一致"
        )
    if len(dates_arr) == 0:
        raise ValueError("dates/values 不能为空")
    if not np.all(np.isfinite(values_arr)):
        raise ValueError("values 不能包含 NaN 或 Inf")
    if weekday_start not in {0, 6}:
        raise ValueError(f"weekday_start 仅支持 0（周一）或 6（周日），实际值: {weekday_start!r}")

    # 统一转为 datetime.date
    parsed_dates: List[date] = []
    for d in dates_arr:
        if isinstance(d, np.datetime64):
            parsed_dates.append(d.astype("M8[D]").astype(object))  # type: ignore[arg-type]
        elif isinstance(d, datetime):
            parsed_dates.append(d.date())
        elif isinstance(d, date):
            parsed_dates.append(d)
        elif isinstance(d, str):
            try:
                parsed_dates.append(datetime.strptime(d, "%Y-%m-%d").date())
            except ValueError:
                raise ValueError(f"无法解析日期字符串: {d!r}（需要 YYYY-MM-DD 格式）")
        else:
            raise TypeError(
                f"dates 元素必须是 datetime/date/字符串，实际类型: {type(d).__name__}"
            )

    first_year = min(d.year for d in parsed_dates)
    last_year = max(d.year for d in parsed_dates)
    weeks_per_year = 54  # 53 周 + 1 格年间隔

    xs: List[float] = []
    ys: List[int] = []
    vals: List[float] = []
    for d, v in zip(parsed_dates, values_arr):
        year_offset = (d.year - first_year) * weeks_per_year
        day_of_year = d.timetuple().tm_yday - 1
        week = day_of_year // 7
        weekday = d.weekday()
        # 调整周起始日：0=周一保持，6=周日时把周日移到首
        y_pos = (weekday + 1) % 7 if weekday_start == 0 else weekday
        xs.append(float(year_offset + week))
        ys.append(y_pos)
        vals.append(float(v))

    # 月份分隔线位置
    month_line_x: List[float] = []
    month_labels: List[str] = []
    for year in range(first_year, last_year + 1):
        for month in range(1, 13):
            try:
                first_day = date(year, month, 1)
            except ValueError:
                continue
            year_offset = (year - first_year) * weeks_per_year
            month_line_x.append(year_offset + (first_day.timetuple().tm_yday - 1) // 7 - 0.5)
            month_labels.append(f"{month}月")

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

    # 格子尺寸（像素）→ scatter 面积
    dpi = float(fig.dpi)
    x_px = float(np.abs(ax.transData.transform((1, 0))[0] - ax.transData.transform((0, 0))[0]))
    y_px = float(np.abs(ax.transData.transform((0, 1))[1] - ax.transData.transform((0, 0))[1]))
    cell_px = min(x_px, y_px) * 0.92
    px_per_pt = dpi / 72.0
    cell_size_pt2 = (cell_px / px_per_pt) ** 2

    scatter = ax.scatter(
        xs, ys, c=vals, cmap=cmap, vmin=vmin, vmax=vmax,
        marker="s", s=cell_size_pt2, edgecolors="none", **kwargs,
    )
    cbar = fig.colorbar(scatter, ax=ax, fraction=0.046, pad=0.04)
    if colorbar_label:
        cbar.set_label(colorbar_label)

    if show_month_lines and month_line_x:
        for x_pos in month_line_x:
            ax.axvline(x=x_pos, color="#999999", linewidth=0.6, alpha=0.5)
        # 月份刻度：取每月线位置，标签用月份
        ax.set_xticks(month_line_x)
        ax.set_xticklabels(month_labels, fontsize=max(5, plt.rcParams.get("font.size", 9) - 3))
    else:
        ax.set_xticks([])

    # 星期标签
    weekday_names_zh = ["一", "二", "三", "四", "五", "六", "日"]
    weekday_names_en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    if weekday_start == 6:
        weekday_names_zh = ["日", "一", "二", "三", "四", "五", "六"]
        weekday_names_en = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    from sciplot._core.style import get_current_lang

    active_lang = lang or get_current_lang() or "zh"
    names = weekday_names_zh if active_lang in {"zh", "zh-cn"} else weekday_names_en
    ax.set_yticks(range(7))
    ax.set_yticklabels(names, fontsize=max(5, plt.rcParams.get("font.size", 9) - 3))

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = ["plot_timeseries", "plot_multi_timeseries", "plot_slope", "plot_gantt", "plot_calendar_heatmap"]
