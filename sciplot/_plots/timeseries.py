"""
时序图表 — 时间序列专用图

支持事件标注、背景区域、滚动均值等时序数据特有功能。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union, Sequence
import warnings

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import numpy as np
from datetime import date, datetime, timedelta

from sciplot._core.layout import add_colorbar
from sciplot._core.utils import cycle_color, get_cycle_colors, new_styled_figure, validate_labels_match_data, relative_fontsize
from sciplot._core.result import PlotResult


def _coerce_to_date(value: Any, field_name: str = "dates") -> date:
    """将 datetime/date/np.datetime64/str 统一转为 datetime.date。"""
    if isinstance(value, np.datetime64):
        return value.astype("M8[D]").astype(object)  # type: ignore[arg-type]
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"无法解析日期字符串: {value!r}（需要 YYYY-MM-DD 格式）")
    raise TypeError(
        f"{field_name} 元素必须是 datetime/date/字符串，实际类型: {type(value).__name__}"
    )


def _is_datetime_value(value: Any) -> bool:
    """判断单个值是否为 datetime 类型（含 pandas 的 Timestamp 等带 dtype 的对象）。"""
    if isinstance(value, (datetime, date, np.datetime64)):
        return True
    return hasattr(value, "dtype") and np.issubdtype(value.dtype, np.datetime64)


def _is_datetime(data: np.ndarray) -> bool:
    """判断数据是否为 datetime 类型"""
    if len(data) == 0:
        return False
    return _is_datetime_value(data[0])


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


def _validate_time_value_for_axis(value: Any, x_type: str, field_name: str) -> None:
    if x_type == "datetime":
        if not _is_datetime_value(value):
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

    fig, ax = new_styled_figure(venue, palette, lang)

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

    fig, ax = new_styled_figure(venue, palette, lang)

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
        ax.plot(t, y, label=lbl, color=cycle_color(colors, i), **kwargs)

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

    fig, ax = new_styled_figure(venue, palette, lang)

    colors = get_cycle_colors()
    if not colors:
        colors = ["#1f77b4", "#ff7f0e"]

    x_positions = np.array([0.0, 1.0])
    left_x, right_x = x_positions

    for i, (name, b_val, a_val) in enumerate(zip(labels, before_arr, after_arr)):
        color = cycle_color(colors, i)
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
    groups: Optional[List[str]] = None,
    milestones: Optional[Dict[str, float]] = None,
    dependencies: Optional[List[Tuple[int, int]]] = None,
    now: Optional[float] = None,
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
    可选元素：阶段分组背景色带、里程碑菱形标记、任务依赖箭头、当前时间线。

    参数:
        tasks        : 任务名称列表
        start        : 任务开始时间（数值或 datetime/date 序列）
        duration     : 任务持续时长；数值轴为数值，日期轴为 timedelta 或天数
        end          : 任务结束时间（与 duration 二选一，优先 duration）
        color_by     : 每任务颜色或类别标签（等长）；None 用配色循环
        groups       : 任务所属阶段（等长）；提供时绘制阶段背景色带
        milestones   : {里程碑名称: 时间}，绘制菱形标记与虚线连接
        dependencies : 依赖关系 [(上游任务索引, 下游任务索引)]，绘制箭头
        now          : 当前时间位置，绘制红色时间线
        show_labels  : 是否显示任务名称
        alpha        : 条形透明度

    示例:
        >>> # 数值时间轴（天数）
        >>> fig, ax = sp.plot_gantt(
        ...     ["数据采集", "模型训练", "论文撰写"],
        ...     start=[0, 10, 30], duration=[10, 20, 20],
        ...     milestones={"中期检查": 22}, dependencies=[(0, 1)], now=15,
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
        if _is_datetime_value(first):
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

    fig, ax = new_styled_figure(venue, palette, lang)
    colors = get_cycle_colors()

    # 颜色解析：color_by 为类别时按类别着色
    if color_by is not None:
        c_arr = np.asarray(color_by).ravel()
        if len(c_arr) != len(tasks):
            raise ValueError(
                f"color_by 长度 ({len(c_arr)}) 与 tasks 长度 ({len(tasks)}) 不一致"
            )
        unique_vals = sorted(set(c_arr), key=str)
        color_map = {v: cycle_color(colors, i) for i, v in enumerate(unique_vals)}
        bar_colors = [color_map[v] for v in c_arr]
        legend_handles = [
            Patch(facecolor=c, label=str(v), alpha=alpha)
            for v, c in color_map.items()
        ]
    else:
        bar_colors = [cycle_color(colors, i) for i in range(len(tasks))]
        legend_handles = None

    # groups / milestones / dependencies / now 校验
    if groups is not None:
        if len(groups) != len(tasks):
            raise ValueError(
                f"groups 长度 ({len(groups)}) 与 tasks 长度 ({len(tasks)}) 不一致"
            )
    if dependencies is not None:
        for dep in dependencies:
            if len(dep) != 2 or not all(
                isinstance(i, int) and 0 <= i < len(tasks) for i in dep
            ):
                raise ValueError(
                    f"dependencies 必须为 [(上游索引, 下游索引)]，实际项: {dep!r}"
                )

    y = np.arange(len(tasks))

    # 阶段背景色带
    if groups is not None:
        from matplotlib.patches import Patch as _Patch

        unique_groups = list(dict.fromkeys(groups))
        group_colors = [cycle_color(colors, i) for i in range(len(unique_groups))]
        group_map = dict(zip(unique_groups, group_colors))
        for i, g in enumerate(groups):
            ax.axhspan(
                i - 0.5, i + 0.5, color=group_map[g], alpha=0.08, zorder=0,
            )
        # 阶段图例
        legend_handles = legend_handles or []
        legend_handles += [
            _Patch(facecolor=c, label=str(g), alpha=0.5)
            for g, c in zip(unique_groups, group_colors)
        ]

    ax.barh(y, widths, left=starts_plot, color=bar_colors, alpha=alpha, zorder=2, **kwargs)

    # 任务依赖箭头（L 形：上游右端 → 下游左端）
    if dependencies:
        for up_idx, down_idx in dependencies:
            x_from = starts_plot[up_idx] + widths[up_idx]
            x_to = starts_plot[down_idx]
            y_from = float(up_idx)
            y_to = float(down_idx)
            mid_y = y_from + (y_to - y_from) * 0.5
            if abs(y_to - y_from) < 0.5:
                # 相邻任务：直接水平箭头
                ax.annotate(
                    "", xy=(x_to, y_to), xytext=(x_from, y_from),
                    arrowprops=dict(arrowstyle="->", color="#888888", lw=0.8),
                    zorder=1,
                )
            else:
                # 跨行：先水平、再垂直、再水平
                ax.plot([x_from, x_to], [y_from, y_from], color="#AAAAAA",
                        linewidth=0.8, zorder=1)
                ax.plot([x_to, x_to], [y_from, y_to], color="#AAAAAA",
                        linewidth=0.8, zorder=1)
                ax.annotate(
                    "", xy=(x_to, y_to), xytext=(x_to, y_to - 0.1),
                    arrowprops=dict(arrowstyle="->", color="#AAAAAA", lw=0.8),
                    zorder=1,
                )

    # 里程碑（菱形 + 虚线连接）
    if milestones:
        for m_name, m_time in milestones.items():
            ax.axvline(x=m_time, color="#E07B54", linestyle=":",
                       linewidth=1.0, alpha=0.8, zorder=1)
            ax.scatter([m_time], [-0.55], marker="D", s=45, color="#E07B54",
                       edgecolors="white", linewidths=0.8, zorder=4)
            ax.text(m_time, -0.95, m_name, ha="center", va="top",
                    fontsize=max(6, plt.rcParams.get("font.size", 9) - 2),
                    color="#E07B54")

    # 当前时间线
    if now is not None:
        ax.axvline(x=now, color="#D62728", linewidth=1.2, zorder=3)
        ax.text(now, len(tasks) - 0.35, "现在", ha="center", va="bottom",
                fontsize=max(6, plt.rcParams.get("font.size", 9) - 2),
                color="#D62728")

    if show_labels:
        ax.set_yticks(y)
        ax.set_yticklabels(tasks)
    else:
        ax.set_yticks([])

    # 里程碑位于任务区下方，扩展 y 范围容纳
    if milestones:
        ax.set_ylim(-1.25, len(tasks) - 0.4)
    else:
        ax.set_ylim(-0.5, len(tasks) - 0.5)

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
    parsed_dates = [_coerce_to_date(d) for d in dates_arr]

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

    fig, ax = new_styled_figure(venue, palette, lang)

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
    cbar = add_colorbar(fig, scatter, ax=ax)
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


def plot_streamgraph(
    x: np.ndarray,
    y_list: Sequence[np.ndarray],
    labels: Optional[Sequence[str]] = None,
    baseline: str = "wiggle",
    alpha: float = 0.85,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制流图（Streamgraph，类别的时序构成演变）。

    堆叠面积图的变体：基线按列偏移，形成“河流”形态，
    适合展示多类别随时间占比/数量的连续演变（Python Graph
    Gallery 的 Evolution 家族经典类型）。纯 matplotlib 实现。

    参数:
        x        : 时间轴（等长数组）
        y_list   : 每类一条序列
        labels   : 类别名
        baseline : 基线策略
                   'wiggle' → 逐列平滑偏移（默认，河流形态最平滑）
                   'center' → 整体居中对称
                   'zero'   → 从零堆叠（普通堆叠面积图）
        alpha    : 图层不透明度

    示例:
        >>> fig, ax = sp.plot_streamgraph(
        ...     years, [y_web, y_mobile, y_pc],
        ...     labels=["Web", "移动端", "PC"],
        ... )
    """
    x_arr = np.asarray(x, dtype=float).ravel()
    series = [np.asarray(y, dtype=float).ravel() for y in y_list]
    if len(series) == 0:
        raise ValueError("y_list 不能为空")
    n_pts = len(x_arr)
    for i, y in enumerate(series):
        if len(y) != n_pts:
            raise ValueError(
                f"y_list[{i}] 长度 ({len(y)}) 与 x 长度 ({n_pts}) 不一致"
            )
        if not np.all(np.isfinite(y)):
            raise ValueError(f"y_list[{i}] 不能包含 NaN 或 Inf")
        if np.any(y < 0):
            raise ValueError(f"y_list[{i}] 不能包含负值（流图要求非负）")
    if baseline not in {"wiggle", "center", "zero"}:
        raise ValueError(f"baseline 仅支持 'wiggle' / 'center' / 'zero'，实际值: {baseline!r}")

    labels = validate_labels_match_data(labels, series)

    stacked = np.vstack(series)  # (n_series, n_pts)
    totals = stacked.sum(axis=0)

    # 基线偏移（Byron-Wattenberg 流图基线）
    if baseline == "zero":
        offset = np.zeros(n_pts)
    elif baseline == "center":
        offset = -totals / 2.0
    else:  # wiggle：center 基础上做逐列平滑，使相邻层面积平衡
        offset = -totals / 2.0
        # 多轮松弛：相邻列基线差最小化
        for _ in range(12):
            new_offset = offset.copy()
            new_offset[1:-1] = 0.5 * (offset[:-2] + offset[2:])
            offset = new_offset
        # 端点保持，整体再居中
        offset = offset - np.mean(offset)

    bases = offset + np.cumsum(stacked, axis=0) - stacked
    tops = bases + stacked

    fig, ax = new_styled_figure(venue, palette, lang)
    colors = get_cycle_colors()

    # 从最上层往下画（视觉上较新的类别在上）
    for i in range(len(series) - 1, -1, -1):
        ax.fill_between(
            x_arr, bases[i], tops[i],
            color=cycle_color(colors, i), alpha=alpha,
            label=labels[i], linewidth=0.4,
            edgecolor="white", zorder=2,
        )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    if labels is not None:
        ax.legend(frameon=False)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_bump(
    labels: List[str],
    values: Union[np.ndarray, List[List[float]]],
    time_points: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "排名",
    title: str = "",
    highlight: Optional[str] = None,
    highlight_color: str = "#C0392B",
    base_color: str = "#9AA5B1",
    linewidth: float = 1.6,
    marker_size: float = 5.0,
    show_end_labels: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制排名变化图（Bump Chart，时间序列排名演化）

    横轴为时间点，纵轴为排名（1 在顶部），每条曲线代表一个
    对象的排名随时间的变化。端点放大标记，末尾直接标注名称
    （Nature 常用“直接标注优先于图例”）。
    支持高亮单条曲线（其余置灰），用于突出某个对象的轨迹。

    参数:
        labels      : 对象名称列表（与 values 行数一致）
        values      : 对象×时间点的数值矩阵（自动转为排名）；
                      若已传入排名矩阵（1 为最优），请先转置输入
        time_points : 时间点标签；None 时用 1..n
        highlight   : 高亮对象名（其余曲线置灰）；None 不高亮
        highlight_color: 高亮曲线颜色，默认深红
        base_color  : 非高亮曲线颜色，默认灰蓝
        show_end_labels: 是否在曲线末端直接标注名称

    示例:
        >>> # 三个模型在 5 个 benchmark 上的排名变化
        >>> fig, ax = sp.plot_bump(
        ...     labels=["模型 A", "模型 B", "模型 C"],
        ...     values=[[85, 88, 90, 87, 92],
        ...             [90, 85, 82, 88, 86],
        ...             [78, 92, 95, 93, 94]],
        ...     time_points=["T1", "T2", "T3", "T4", "T5"],
        ...     highlight="模型 C",
        ... )
        >>> sp.save(fig, "bump")
    """
    mat = np.asarray(values, dtype=float)
    if mat.ndim != 2:
        raise ValueError("values 必须是二维数组（对象 × 时间点）")
    n_items, n_time = mat.shape
    if n_items == 0 or n_time == 0:
        raise ValueError("values 不能为空")
    if len(labels) != n_items:
        raise ValueError(f"labels 长度 ({len(labels)}) 与 values 行数 ({n_items}) 不一致")
    if time_points is not None and len(time_points) != n_time:
        raise ValueError(
            f"time_points 长度 ({len(time_points)}) 与列数 ({n_time}) 不一致"
        )
    if not np.all(np.isfinite(mat)):
        raise ValueError("values 不能包含 NaN 或 Inf")
    if highlight is not None and highlight not in labels:
        raise ValueError(f"highlight '{highlight}' 不在 labels 中")

    # 数值 → 排名（每列内：值越大排名越靠前）
    ranks = np.zeros_like(mat, dtype=int)
    for j in range(n_time):
        order = np.argsort(-mat[:, j], kind="stable")
        ranks[order, j] = np.arange(1, n_items + 1)

    x = np.arange(n_time, dtype=float)

    fig, ax = new_styled_figure(venue, palette, lang)

    colors = get_cycle_colors()

    def _series_color(i: int) -> str:
        if highlight is not None and labels[i] == highlight:
            return highlight_color
        if highlight is not None:
            return base_color
        return cycle_color(colors, i)

    # ── 曲线：先画非高亮（垫底、细、半透明），高亮最后（粗、实） ──
    order = sorted(range(n_items),
                   key=lambda i: 1 if (highlight is not None and labels[i] == highlight) else 0)
    for i in order:
        c = _series_color(i)
        is_hl = highlight is not None and labels[i] == highlight
        lw = (linewidth + 1.0) if is_hl else (linewidth * 0.85 if highlight else linewidth)
        alpha = 1.0 if is_hl else (0.55 if highlight is not None else 0.9)
        z = 4 if is_hl else 2
        # 曲线本体
        ax.plot(x, ranks[i], color=c, linewidth=lw, alpha=alpha, zorder=z,
                solid_capstyle="round")
        # 每个时间点的排名小圆点（高亮对象更大）
        ms = marker_size + (2.2 if is_hl else 0.0)
        ax.scatter(x, ranks[i], s=ms ** 2 * 1.6, color=c, alpha=alpha,
                   edgecolors="white", linewidths=0.8, zorder=z + 1)

    # ── 起点/终点大圆点（强调轨迹端点） ──
    for i in range(n_items):
        c = _series_color(i)
        is_hl = highlight is not None and labels[i] == highlight
        z = 5 if is_hl else 3
        for xi in (0, n_time - 1):
            ax.scatter(x[xi], ranks[i, xi], s=(marker_size + 3.5) ** 2,
                       color=c, edgecolors="white", linewidths=1.2, zorder=z)

    # ── 末端直接标注（名称 + 当前排名） ──
    if show_end_labels:
        fs = relative_fontsize(-1, floor=6)
        for i in range(n_items):
            c = _series_color(i)
            is_hl = highlight is not None and labels[i] == highlight
            lbl = f"{labels[i]}"
            ax.text(x[-1] + 0.18, ranks[i, -1], lbl,
                    va="center", ha="left", fontsize=fs,
                    color=c, fontweight="bold" if is_hl else "normal",
                    clip_on=False)
            # 末端排名数值（浅色小字，紧贴端点上方）
            ax.text(x[-1] - 0.02, ranks[i, -1] - 0.32, f"{ranks[i, -1]}",
                    va="bottom", ha="center", fontsize=relative_fontsize(-3, floor=5),
                    color=c, alpha=0.85, clip_on=False)

    ax.set_xticks(x)
    if time_points is not None:
        ax.set_xticklabels(time_points)
    ax.set_yticks(np.arange(1, n_items + 1))
    ax.invert_yaxis()  # 排名 1 在顶部
    ax.set_xlim(-0.4, n_time - 0.6 + (1.1 if show_end_labels else 0.0))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = ["plot_timeseries", "plot_multi_timeseries", "plot_slope", "plot_gantt", "plot_calendar_heatmap", "plot_streamgraph", "plot_bump"]
