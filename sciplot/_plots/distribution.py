"""
分布图表 — 柱状图、分组柱状图、堆叠柱状图、水平柱状图、
          箱线图、小提琴图、直方图、组合图、显著性标注
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from sciplot._core.utils import (
    create_sciplot_figure,
    create_plot_result,
    validate_dict_not_empty,
    validate_array_like,
    validate_positive_number,
    boxplot_with_orientation,
    contrast_text_color,
    cycle_color,
    get_cycle_colors as _get_cycle_colors,
    new_styled_figure,
)
from sciplot._core.result import PlotResult, ComboPlotResult
from sciplot.utils.guards import polish_axis, style_patch_edges, truncate_tick_labels
from sciplot.utils.smart import auto_rotate_labels, smart_legend


# ============================================================================
# 柱状图（单组）
# ============================================================================

def plot_bar(
    categories: List[str],
    values: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    width: float = 0.6,
    show_values: bool = False,
    value_fmt: str = ".1f",
    yerr: Optional[Union[List[float], np.ndarray]] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制单组柱状图（柔填充深轮廓 + 干净 L 轴 + 可选误差棒/柱顶数值）

    参数:
        width      : 柱宽，默认 0.6
        show_values: 是否在柱顶直接标注数值
        value_fmt  : 柱顶数值格式，默认 ".1f"
        yerr       : 可选误差棒数组（与 values 等长）
        lang       : 语言设置

    示例:
        >>> fig, ax = sp.plot_bar(
        ...     ["方法A", "方法B", "方法C"],
        ...     np.array([82.3, 85.1, 88.7]),
        ...     xlabel="方法", ylabel="准确率 (%)",
        ...     palette="pastel-3", show_values=True,
        ... )
        >>> sp.save(fig, "accuracy_bar")
    """
    from sciplot.utils.guards import polish_axis, style_patch_edges

    # 输入验证 - 使用 EAFP 风格（Easier to Ask for Forgiveness than Permission）
    try:
        if len(categories) == 0:
            raise ValueError("参数 'categories' 不能为空列表")
        values_arr = np.asarray(values, dtype=float)
        if len(categories) != len(values_arr):
            raise ValueError(
                f"categories 长度 ({len(categories)}) 与 values 长度 ({len(values_arr)}) 不一致"
            )
        if not np.all(np.isfinite(values_arr)):
            raise ValueError("values 不能包含 NaN 或 Inf")
        width = validate_positive_number(width, "width", allow_zero=False)
        yerr_arr = None
        if yerr is not None:
            yerr_arr = np.asarray(yerr, dtype=float).ravel()
            if len(yerr_arr) != len(values_arr):
                raise ValueError(
                    f"yerr 长度 ({len(yerr_arr)}) 与 values 长度 ({len(values_arr)}) 不一致"
                )
    except TypeError as e:
        raise ValueError(f"参数类型错误: {e}") from e

    effective_venue, fig, ax = create_sciplot_figure(venue, palette, lang)
    colors = _get_cycle_colors()
    bar_colors = [cycle_color(colors, i) for i in range(len(categories))]
    # 显式 color 参数覆盖自动配色（避免 kwargs 与 bar_colors 冲突）
    explicit_color = kwargs.pop("color", None)
    if explicit_color is not None:
        bar_colors = explicit_color
    has_edge_override = "edgecolor" in kwargs or "ec" in kwargs
    has_alpha_override = "alpha" in kwargs
    bar_kwargs = dict(kwargs)
    if yerr_arr is not None:
        bar_kwargs.setdefault("yerr", yerr_arr)
        bar_kwargs.setdefault("capsize", 3)
        bar_kwargs.setdefault("error_kw", {"linewidth": 0.9, "ecolor": "#333333"})

    bars = ax.bar(categories, values_arr, width=width, color=bar_colors, **bar_kwargs)
    if not has_edge_override and not has_alpha_override:
        resolved_fills = (
            [explicit_color] * len(bars)
            if isinstance(explicit_color, str)
            else list(bar_colors)
            if isinstance(bar_colors, (list, tuple))
            else [cycle_color(colors, i) for i in range(len(bars))]
        )
        style_patch_edges(bars, resolved_fills, fill_alpha=0.86, darken_amount=0.26, linewidth=0.7)

    if show_values:
        span = float(np.ptp(values_arr)) if values_arr.size > 1 else abs(float(values_arr[0]))
        pad = max(span, 1.0) * 0.018
        for i, (bar, v) in enumerate(zip(bars, values_arr)):
            err_offset = float(yerr_arr[i]) if yerr_arr is not None else 0.0
            y_pos = (v + err_offset + pad) if v >= 0 else (v - err_offset - pad)
            va = "bottom" if v >= 0 else "top"
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                y_pos,
                f"{v:{value_fmt}}",
                ha="center",
                va=va,
                fontsize=max(6, int(plt.rcParams.get("font.size", 9)) - 1),
            )

    polish_axis(ax, categorical_axis="x", clean_spines=True, grid="y")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    auto_rotate_labels(ax, axis="x")
    return create_plot_result(fig, ax, venue, palette, lang)


# ============================================================================
# 分组柱状图（多组对比）
# ============================================================================

def plot_grouped_bar(
    groups: List[str],
    data: Dict[str, Union[List[float], np.ndarray]],
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    width: float = 0.8,
    gap: float = 0.05,
    show_values: bool = False,
    value_fmt: str = ".1f",
    legend_loc: str = "best",
    colors: Optional[Sequence[str]] = None,
    errors: Optional[Dict[str, Union[List[float], np.ndarray]]] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制分组柱状图（多方法/多指标对比，含可选误差棒与柔和深边层次）

    参数:
        groups    : 横轴分组标签（如 ["数据集A", "数据集B", "数据集C"])
        data      : {方法名: 对应各组的数值} 有序字典
                    如 {"BERT": [87, 89, 91], "GPT": [85, 90, 93]}
        width     : 每组所有柱的总宽（占一个间隔的比例），默认 0.8
        gap       : 组间额外间隙，默认 0.05
        show_values: True 则在柱顶显示数值
        value_fmt  : 数值格式字符串，默认 ".1f"
        legend_loc : 图例位置
        errors     : 可选误差棒字典 {方法名: 各组误差数组}
        lang       : 语言设置

    示例:
        >>> methods = {"ResNet": [82.3, 84.1, 86.5],
        ...            "ViT":    [85.7, 87.2, 89.0],
        ...            "本文":   [88.1, 90.3, 92.4]}
        >>> fig, ax = sp.plot_grouped_bar(
        ...     groups=["CIFAR-10", "CIFAR-100", "ImageNet"],
        ...     data=methods,
        ...     ylabel="Top-1 准确率 (%)",
        ...     palette="pastel-3",
        ... )
        >>> sp.save(fig, "compare_bar")
    """
    from sciplot.utils.guards import polish_axis, style_patch_edges

    # 输入验证
    if not groups:
        raise ValueError("参数 'groups' 不能为空列表")
    data = validate_dict_not_empty(data, "data")
    n_groups = len(groups)
    normalized_data: Dict[str, np.ndarray] = {}
    for series_name, values in data.items():
        values_arr = np.asarray(values, dtype=float).ravel()
        if len(values_arr) != n_groups:
            raise ValueError(
                f"数据系列 '{series_name}' 的长度 ({len(values_arr)}) "
                f"与 groups 长度 ({n_groups}) 不一致"
            )
        if not np.all(np.isfinite(values_arr)):
            raise ValueError(f"数据系列 '{series_name}' 不能包含 NaN 或 Inf")
        normalized_data[series_name] = values_arr
    width = validate_positive_number(width, "width", allow_zero=False)
    gap = validate_positive_number(gap, "gap", allow_zero=True)

    normalized_errors: Dict[str, np.ndarray] = {}
    if errors is not None:
        for series_name, err_vals in errors.items():
            err_arr = np.asarray(err_vals, dtype=float).ravel()
            if len(err_arr) != n_groups:
                raise ValueError(
                    f"errors['{series_name}'] 长度 ({len(err_arr)}) 与 groups 长度 ({n_groups}) 不一致"
                )
            normalized_errors[series_name] = err_arr

    fig, ax = new_styled_figure(venue, palette, lang)

    n_series = len(normalized_data)
    if width <= gap * (n_series - 1):
        raise ValueError(
            f"width={width} 过小，必须大于 gap*(系列数-1)={gap * (n_series - 1):.6g}，"
            "否则每个柱子的宽度将小于等于 0"
        )
    if colors is not None and len(colors) != n_series:
        raise ValueError(
            f"colors 长度 ({len(colors)}) 与系列数 ({n_series}) 不一致"
        )
    if colors is None:
        colors = _get_cycle_colors()

    bar_w = (width - gap * (n_series - 1)) / n_series
    group_centers = np.arange(n_groups)
    has_edge_override = "edgecolor" in kwargs or "ec" in kwargs
    has_alpha_override = "alpha" in kwargs

    for i, (series_name, values) in enumerate(normalized_data.items()):
        offsets = group_centers + (i - (n_series - 1) / 2) * (bar_w + gap)
        color = cycle_color(colors, i)
        bar_kwargs = dict(kwargs)
        err_arr = normalized_errors.get(series_name)
        if err_arr is not None:
            bar_kwargs.setdefault("yerr", err_arr)
            bar_kwargs.setdefault("capsize", 2.8)
            bar_kwargs.setdefault("error_kw", {"linewidth": 0.85, "ecolor": "#333333"})
        bars = ax.bar(
            offsets, values, width=bar_w,
            color=color, label=series_name, **bar_kwargs
        )
        if not has_edge_override and not has_alpha_override:
            style_patch_edges(bars, [color], fill_alpha=0.86, darken_amount=0.25, linewidth=0.68)
        if show_values:
            val_pad = max(float(np.ptp(values)) * 0.015, abs(float(np.max(np.abs(values)))) * 0.012, 1e-6)
            for idx_b, (bar, v) in enumerate(zip(bars, values)):
                err_off = float(err_arr[idx_b]) if err_arr is not None else 0.0
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + err_off + val_pad * 0.35,
                    f"{v:{value_fmt}}",
                    ha="center", va="bottom",
                    fontsize=max(6, int(plt.rcParams.get("font.size", 9)) - 1),
                )

    polish_axis(ax, categorical_axis="x", clean_spines=True, grid="y")
    ax.set_xticks(group_centers)
    ax.set_xticklabels(groups)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    auto_rotate_labels(ax, axis="x")
    smart_legend(ax, loc=legend_loc)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


# ============================================================================
# 箱线图
# ============================================================================

def plot_box(
    data: Union[np.ndarray, List[np.ndarray]],
    labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    showfliers: bool = True,
    show_points: bool = False,
    show_means: bool = False,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制箱线图（展示中位数、四分位距、异常值及可选原始散点叠加）

    参数:
        data       : 单个数组或数组列表，每个数组代表一组数据
        showfliers : 是否显示离群点，默认 True
        show_points: 是否叠加半透明抖动原始观测点，默认 False
        show_means : 是否在箱体中标注均值菱形，默认 False
        lang       : 语言设置

    示例:
        >>> fig, ax = sp.plot_box(
        ...     [scores_a, scores_b, scores_c],
        ...     labels=["算法A", "算法B", "算法C"],
        ...     ylabel="得分", palette="pastel-3", show_points=True,
        ... )
        >>> sp.save(fig, "boxplot")
    """
    from matplotlib.colors import to_hex
    from sciplot.utils import darken_color
    from sciplot.utils.guards import polish_axis

    if isinstance(data, (list, tuple)):
        if not data:
            raise ValueError("参数 'data' 不能为空列表")
        for i, values in enumerate(data):
            values_arr = np.asarray(values, dtype=float).ravel()
            if values_arr.size == 0:
                raise ValueError(f"data[{i}] 不能为空")
            if not np.all(np.isfinite(values_arr)):
                raise ValueError(f"data[{i}] 不能包含 NaN 或 Inf")
        if labels is not None and len(labels) != len(data):
            raise ValueError(
                f"labels 长度 ({len(labels)}) 与数据组数 ({len(data)}) 不一致"
            )
    else:
        data_arr = np.asarray(data, dtype=float)
        if data_arr.size == 0:
            raise ValueError("参数 'data' 不能为空")
        if not np.all(np.isfinite(data_arr)):
            raise ValueError("data 不能包含 NaN 或 Inf")

    fig, ax = new_styled_figure(venue, palette, lang)
    colors = _get_cycle_colors()
    # 显式 patch_artist 参数覆盖默认（避免 kwargs 与 True 冲突）
    patch_artist = bool(kwargs.pop("patch_artist", True))
    box_kwargs = dict(kwargs)
    box_kwargs.setdefault("medianprops", {"color": "#2D3436", "linewidth": 1.4})
    box_kwargs.setdefault("whiskerprops", {"color": "#4A5568", "linewidth": 0.95})
    box_kwargs.setdefault("capprops", {"color": "#4A5568", "linewidth": 0.95})
    if showfliers:
        box_kwargs.setdefault("flierprops", {
            "marker": "o", "markersize": 3.5, "alpha": 0.65,
            "markerfacecolor": "#718096", "markeredgecolor": "none",
        })
    if show_means:
        box_kwargs.setdefault("showmeans", True)
        box_kwargs.setdefault("meanprops", {
            "marker": "D", "markersize": 4.5,
            "markerfacecolor": "white", "markeredgecolor": "#2D3436",
        })

    bp = ax.boxplot(
        data, showfliers=showfliers,
        patch_artist=patch_artist, **box_kwargs
    )
    if patch_artist:
        for i, patch in enumerate(bp["boxes"]):
            c = cycle_color(colors, i)
            patch.set_facecolor(c)
            patch.set_alpha(0.72)
            try:
                patch.set_edgecolor(darken_color(to_hex(c), amount=0.28))
            except Exception:
                patch.set_edgecolor("#2D3436")
            patch.set_linewidth(0.95)

    if show_points:
        groups_seq = (
            [np.asarray(g, dtype=float).ravel() for g in data]
            if isinstance(data, (list, tuple))
            else ([np.asarray(data, dtype=float).ravel()] if np.asarray(data).ndim == 1
                  else [np.asarray(data, dtype=float)[:, c] for c in range(np.asarray(data).shape[1])])
        )
        rng = np.random.default_rng(42)
        for i, vals in enumerate(groups_seq):
            c = cycle_color(colors, i)
            jit = rng.uniform(-0.14, 0.14, size=vals.size)
            ax.scatter(
                (i + 1) + jit, vals,
                s=12, alpha=0.45, color=c,
                edgecolors="white", linewidths=0.35, zorder=4,
            )

    polish_axis(ax, categorical_axis="x", clean_spines=True, grid="y")
    if labels is not None:
        ax.set_xticklabels(labels)
        auto_rotate_labels(ax, axis="x")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


# ============================================================================
# 小提琴图
# ============================================================================

def _draw_violin_quartiles(
    ax: plt.Axes,
    pos: float,
    vals: np.ndarray,
    *,
    showmedians: bool = True,
    showmeans: bool = False,
    capsule_width: float = 4.2,
    mean_color: str = "#E76F51",
) -> None:
    """在小提琴轮廓内部绘制须线、IQR 胶囊与中位数/均值标记。"""
    q25, med, q75 = np.percentile(vals, [25, 50, 75])
    iqr = q75 - q25
    lo_w = max(float(vals.min()), q25 - 1.5 * iqr)
    hi_w = min(float(vals.max()), q75 + 1.5 * iqr)
    ax.vlines(pos, lo_w, hi_w, color="#2D3436", linewidth=0.95, zorder=3)
    ax.vlines(pos, q25, q75, color="#2D3436", linewidth=capsule_width, zorder=4)
    if showmedians:
        ax.scatter(
            [pos], [med], color="white", edgecolors="#2D3436",
            s=18, linewidths=0.8, zorder=5,
        )
    if showmeans:
        ax.scatter(
            [pos], [float(np.mean(vals))], marker="D",
            color=mean_color, edgecolors="white", s=20, linewidths=0.5, zorder=6,
        )


def plot_violin(
    data: Union[np.ndarray, List[np.ndarray]],
    labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    showmeans: bool = False,
    showmedians: bool = True,
    show_box: bool = True,
    show_points: bool = False,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制小提琴图（柔和轮廓 + 内嵌四分位胶囊 + 可选原始散点）

    参数:
        showmeans  : 是否显示均值标记，默认 False
        showmedians: 是否显示中位数标记，默认 True
        show_box   : 是否在琴身内部绘制 IQR 四分位短胶囊 + 白点中位数，默认 True
        show_points: 是否叠加半透明原始样本点，默认 False
        lang       : 语言设置

    示例:
        >>> fig, ax = sp.plot_violin(
        ...     [data_a, data_b],
        ...     labels=["Method A", "Method B"],
        ...     ylabel="Accuracy (%)", showmedians=True
        ... )
    """
    from matplotlib.colors import to_hex
    from sciplot.utils import darken_color
    from sciplot.utils.guards import polish_axis

    if isinstance(data, (list, tuple)):
        if not data:
            raise ValueError("参数 'data' 不能为空列表")
        groups_seq: List[np.ndarray] = []
        for i, values in enumerate(data):
            values_arr = np.asarray(values, dtype=float).ravel()
            if values_arr.size == 0:
                raise ValueError(f"data[{i}] 不能为空")
            if not np.all(np.isfinite(values_arr)):
                raise ValueError(f"data[{i}] 不能包含 NaN 或 Inf")
            groups_seq.append(values_arr)
        n_groups = len(groups_seq)
    else:
        data_arr = np.asarray(data, dtype=float)
        if data_arr.size == 0:
            raise ValueError("参数 'data' 不能为空")
        if not np.all(np.isfinite(data_arr)):
            raise ValueError("data 不能包含 NaN 或 Inf")
        if data_arr.ndim > 1:
            n_groups = data_arr.shape[1]
            groups_seq = [data_arr[:, j].ravel() for j in range(n_groups)]
        else:
            n_groups = 1
            groups_seq = [data_arr.ravel()]

    if labels is not None and len(labels) != n_groups:
        raise ValueError(
            f"labels 长度 ({len(labels)}) 与数据组数 ({n_groups}) 不一致"
        )

    fig, ax = new_styled_figure(venue, palette, lang)
    colors = _get_cycle_colors()

    parts = ax.violinplot(
        data, showmeans=showmeans, showmedians=showmedians, **kwargs
    )
    bodies: list = parts["bodies"]  # type: ignore[assignment]
    for i, pc in enumerate(bodies):
        c = cycle_color(colors, i)
        pc.set_facecolor(c)
        pc.set_alpha(0.55)
        try:
            pc.set_edgecolor(darken_color(to_hex(c), amount=0.28))
        except Exception:
            pc.set_edgecolor("#2D3436")
        pc.set_linewidth(0.95)

    # 统一小提琴内部极值/均值/中位线的视觉克制（避免亮紫色横杠喧宾夺主）
    for stat_key in ("cbars", "cmins", "cmaxes", "cmedians", "cmeans"):
        coll = parts.get(stat_key)
        if coll is not None:
            if show_box and stat_key in {"cbars", "cmins", "cmaxes", "cmedians"}:
                coll.set_visible(False)
            else:
                coll.set_color("#2D3436")
                coll.set_linewidth(0.95)

    if show_box:
        for i, vals in enumerate(groups_seq):
            _draw_violin_quartiles(
                ax,
                float(i + 1),
                vals,
                showmedians=showmedians,
                showmeans=showmeans,
                capsule_width=4.2,
            )

    if show_points:
        rng = np.random.default_rng(42)
        for i, vals in enumerate(groups_seq):
            c = cycle_color(colors, i)
            jit = rng.uniform(-0.10, 0.10, size=vals.size)
            ax.scatter(
                (i + 1) + jit, vals,
                s=10, alpha=0.40, color=c,
                edgecolors="white", linewidths=0.3, zorder=2,
            )

    polish_axis(ax, categorical_axis="x", clean_spines=True, grid="y")
    if labels is not None:
        ax.set_xticks(range(1, n_groups + 1))
        ax.set_xticklabels(labels)
        auto_rotate_labels(ax, axis="x")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


# ============================================================================
# 直方图
# ============================================================================

def plot_histogram(
    data: np.ndarray,
    bins: int = 30,
    xlabel: str = "",
    ylabel: str = "Frequency",
    title: str = "",
    density: bool = False,
    alpha: float = 0.78,
    show_kde: bool = False,
    show_median: bool = False,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制直方图（白边分离柱体 + 干净 L 轴 + 可选 KDE 密度与中位数线）

    参数:
        bins       : 柱数，默认 30
        density    : True 则归一化为概率密度
        show_kde   : True 时叠加核密度平滑曲线（需 scipy）
        show_median: True 时叠加中位数竖虚线与均值参考
        lang       : 语言设置

    示例:
        >>> fig, ax = sp.plot_histogram(
        ...     data, bins=40, density=True, show_kde=True,
        ...     xlabel="残差", ylabel="概率密度"
        ... )
    """
    from sciplot.utils.guards import polish_axis

    values = np.asarray(data, dtype=float).ravel()
    finite_values = values[np.isfinite(values)]
    if finite_values.size == 0:
        raise ValueError("data 至少需要 1 个有限数值")
    if not isinstance(bins, int) or bins <= 0:
        raise ValueError(f"bins 必须为正整数，实际值: {bins!r}")

    fig, ax = new_styled_figure(venue, palette, lang)
    colors = _get_cycle_colors()
    # 显式 color 参数覆盖自动配色（避免 kwargs 与 colors[0] 冲突）
    explicit_color = kwargs.pop("color", None)
    main_color = explicit_color if explicit_color is not None else colors[0]
    hist_kwargs = dict(kwargs)
    hist_kwargs.setdefault("edgecolor", "white")
    hist_kwargs.setdefault("linewidth", 0.6)

    effective_density = density or show_kde
    ax.hist(
        finite_values, bins=bins, density=effective_density, alpha=alpha,
        color=main_color, **hist_kwargs
    )

    if show_kde and finite_values.size >= 3 and np.ptp(finite_values) > 0:
        from scipy import stats as _sp_stats

        kde = _sp_stats.gaussian_kde(finite_values)
        x_eval = np.linspace(float(finite_values.min()), float(finite_values.max()), 200)
        line_c = colors[1] if len(colors) > 1 and main_color == colors[0] else "#2D3436"
        ax.plot(x_eval, kde(x_eval), color=line_c, linewidth=1.6, zorder=4)

    if show_median:
        med = float(np.median(finite_values))
        ax.axvline(med, color="#2D3436", linestyle="--", linewidth=1.1, zorder=5)

    polish_axis(ax, clean_spines=True, grid="y")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


# ============================================================================
# 堆叠柱状图
# ============================================================================

def plot_stacked_bar(
    categories: List[str],
    data: Dict[str, Union[List[float], np.ndarray]],
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    width: float = 0.6,
    show_values: bool = False,
    value_fmt: str = ".1f",
    legend_loc: str = "best",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制堆叠柱状图（展示各部分占总和的比例）

    参数:
        categories: 横轴分组标签
        data      : {系列名: 各组数值} 字典
        width     : 柱宽，默认 0.6
        show_values: 是否在柱上显示数值
        value_fmt : 数值格式，默认 ".1f"
        lang      : 语言设置

    示例:
        >>> data = {
        ...     "训练集": [80, 85, 90],
        ...     "验证集": [10, 8, 5],
        ...     "测试集": [10, 7, 5],
        ... }
        >>> fig, ax = sp.plot_stacked_bar(
        ...     ["模型A", "模型B", "模型C"],
        ...     data,
        ...     ylabel="样本数量",
        ...     show_values=True
        ... )
    """
    from sciplot.utils.guards import polish_axis

    if not categories:
        raise ValueError("参数 'categories' 不能为空列表")
    data = validate_dict_not_empty(data, "data")
    width = validate_positive_number(width, "width", allow_zero=False)

    n_groups = len(categories)
    normalized_data: Dict[str, np.ndarray] = {}
    for series_name, values in data.items():
        series_values = np.asarray(
            validate_array_like(values, f"data['{series_name}']"),
            dtype=float,
        )
        if len(series_values) != n_groups:
            raise ValueError(
                f"数据系列 '{series_name}' 的长度 ({len(series_values)}) "
                f"与 categories 长度 ({n_groups}) 不一致"
            )
        if not np.all(np.isfinite(series_values)):
            raise ValueError(f"数据系列 '{series_name}' 不能包含 NaN 或 Inf")
        normalized_data[series_name] = series_values

    fig, ax = new_styled_figure(venue, palette, lang)
    colors = _get_cycle_colors()

    x = np.arange(n_groups)
    bar_kwargs = dict(kwargs)
    bar_kwargs.setdefault("edgecolor", "white")
    bar_kwargs.setdefault("linewidth", 0.7)

    bottom = np.zeros(n_groups)
    for i, (series_name, values) in enumerate(normalized_data.items()):
        color = cycle_color(colors, i)
        bars = ax.bar(
            x, values, width=width,
            bottom=bottom, color=color, label=series_name, **bar_kwargs
        )
        if show_values:
            for j, (bar, v) in enumerate(zip(bars, values)):
                if v > 0:  # 只显示正值
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bottom[j] + v / 2,
                        f"{v:{value_fmt}}",
                        ha="center", va="center",
                        fontsize=plt.rcParams.get("font.size", 9) - 1,
                        color=contrast_text_color(color),
                    )
        bottom += values

    polish_axis(ax, categorical_axis="x", clean_spines=True, grid="y")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    auto_rotate_labels(ax, axis="x")
    smart_legend(ax, loc=legend_loc)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


# ============================================================================
# 水平柱状图
# ============================================================================

def plot_horizontal_bar(
    categories: List[str],
    values: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    height: float = 0.6,
    show_values: bool = False,
    value_fmt: str = ".1f",
    sort: bool = False,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制水平柱状图（适合类别较多的场景）

    参数:
        height     : 柱高，默认 0.6
        show_values: 是否在柱尾显示数值
        sort       : 是否按数值升序排序（最大值在顶部），默认 False

    示例:
        >>> fig, ax = sp.plot_horizontal_bar(
        ...     ["特征A", "特征B", "特征C", "特征D"],
        ...     [0.85, 0.72, 0.91, 0.68],
        ...     xlabel="重要性",
        ...     show_values=True,
        ...     sort=True
        ... )
    """
    if not categories:
        raise ValueError("参数 'categories' 不能为空列表")
    values_arr = np.asarray(values, dtype=float).ravel()
    if len(categories) != len(values_arr):
        raise ValueError(
            f"categories 长度 ({len(categories)}) 与 values 长度 ({len(values_arr)}) 不一致"
        )
    if values_arr.size == 0:
        raise ValueError("参数 'values' 不能为空")
    if not np.all(np.isfinite(values_arr)):
        raise ValueError("values 不能包含 NaN 或 Inf")
    height = validate_positive_number(height, "height", allow_zero=False)

    fig, ax = new_styled_figure(venue, palette, lang)
    colors = _get_cycle_colors()

    # 排序处理（升序，让最大值在顶部）
    if sort:
        sorted_indices = np.argsort(values_arr)  # 升序
        categories = [categories[i] for i in sorted_indices]
        values_arr = values_arr[sorted_indices]

    y = np.arange(len(categories))
    bar_colors = [cycle_color(colors, i) for i in range(len(categories))]
    has_edge_override = "edgecolor" in kwargs or "ec" in kwargs
    has_alpha_override = "alpha" in kwargs

    bars = ax.barh(y, values_arr, height=height, color=bar_colors, **kwargs)
    if not has_edge_override and not has_alpha_override:
        style_patch_edges(bars, bar_colors, fill_alpha=0.86, darken_amount=0.26, linewidth=0.7)

    if show_values:
        value_offset = max(float(np.max(np.abs(values_arr))) * 0.01, 1e-9)
        for bar, v in zip(bars, values_arr):
            text_x = bar.get_width() + (value_offset if bar.get_width() >= 0 else -value_offset)
            text_ha = "left" if bar.get_width() >= 0 else "right"
            ax.text(
                text_x,
                bar.get_y() + bar.get_height() / 2,
                f"{v:{value_fmt}}",
                ha=text_ha, va="center",
                fontsize=max(6, plt.rcParams.get("font.size", 9) - 1),
            )

    polish_axis(ax, categorical_axis="y", clean_spines=True, grid="x")
    ax.set_yticks(y)
    ax.set_yticklabels(categories)
    truncate_tick_labels(ax, axis="y", max_len=24)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


# ============================================================================
# 棒棒糖图
# ============================================================================

def plot_lollipop(
    categories: List[str],
    values: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    sort: bool = True,
    marker_size: float = 8,
    stem_width: float = 2.0,
    baseline: float = 0.0,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制棒棒糖图，用于类别排名与重要性展示。"""
    if not categories:
        raise ValueError("参数 'categories' 不能为空列表")

    values_arr = np.asarray(values, dtype=float)
    if values_arr.ndim != 1:
        raise ValueError("values 必须是一维数组")
    if len(categories) != len(values_arr):
        raise ValueError(
            f"categories 长度 ({len(categories)}) 与 values 长度 ({len(values_arr)}) 不一致"
        )
    if not np.all(np.isfinite(values_arr)):
        raise ValueError("values 不能包含 NaN 或 Inf")

    marker_size = validate_positive_number(marker_size, "marker_size", allow_zero=False)
    stem_width = validate_positive_number(stem_width, "stem_width", allow_zero=False)

    if sort:
        order = np.argsort(values_arr)
        categories = [categories[i] for i in order]
        values_arr = values_arr[order]

    fig, ax = new_styled_figure(venue, palette, lang)
    colors = _get_cycle_colors()
    main_color = colors[0]

    x = np.arange(len(categories))
    ax.hlines(y=baseline, xmin=-0.5, xmax=len(categories) - 0.5, color="#B8C0CC", linewidth=0.95, zorder=1)
    ax.vlines(x, baseline, values_arr, color=main_color, linewidth=stem_width, alpha=0.88, zorder=2)
    scatter_kw = dict(kwargs)
    scatter_kw.setdefault("edgecolors", "white")
    scatter_kw.setdefault("linewidths", 0.9)
    ax.scatter(x, values_arr, s=marker_size**2, color=main_color, zorder=3, **scatter_kw)

    polish_axis(ax, categorical_axis="x", clean_spines=True, grid="y")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    auto_rotate_labels(ax, axis="x")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


# ============================================================================
# 组合图（折线 + 柱状）
# ============================================================================

def plot_combo(
    x: np.ndarray,
    bar_data: Dict[str, Union[List[float], np.ndarray]],
    line_data: Optional[Dict[str, Union[List[float], np.ndarray]]] = None,
    xlabel: str = "",
    ylabel_left: str = "",
    ylabel_right: str = "",
    title: str = "",
    bar_width: float = 0.35,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> ComboPlotResult:
    """
    绘制组合图（柱状图 + 折线图，常用于双 Y 轴场景）

    参数:
        x           : 横轴标签数组
        bar_data    : 柱状图数据 {系列名: 数值列表}
        line_data   : 折线图数据 {系列名: 数值列表}，可选
        xlabel      : X 轴标签
        ylabel_left : 左 Y 轴标签（对应柱状图）
        ylabel_right: 右 Y 轴标签（对应折线图）
        bar_width   : 柱宽，默认 0.35
        venue       : 期刊样式
        palette     : 配色方案
        lang        : 语言设置

    返回:
        PlotResult: 包含 fig 和 axes 的结果对象
            - 单 Y 轴时: result.ax 为主坐标轴
            - 双 Y 轴时: result.ax_array[0] 为柱状图轴, result.ax_array[1] 为折线图轴

    示例:
        >>> # 单 Y 轴：柱状 + 折线
        >>> result = sp.plot_combo(
        ...     ["Q1", "Q2", "Q3", "Q4"],
        ...     bar_data={"销售额": [100, 120, 140, 160]},
        ...     line_data={"增长率": [5, 8, 12, 15]},
        ...     ylabel_left="销售额（万元）",
        ...     ylabel_right="增长率（%）",
        ... )
        >>> result.save("combo_chart")

        >>> # 双 Y 轴访问
        >>> result = sp.plot_combo(months, bar_data={"销量": sales}, line_data={"均价": prices})
        >>> ax_bar, ax_line = result.ax_array
    """
    # 兼容两种输入：{系列名: 数值} 字典，或单个数值数组（自动命名 "值"）
    if isinstance(bar_data, dict):
        if not bar_data:
            raise ValueError("bar_data 不能为空，至少需要一个柱状图系列")
        normalized_input = bar_data
    else:
        # 数组/列表：包成单系列字典
        normalized_input = {"值": bar_data}

    if len(x) == 0:
        raise ValueError("x 不能为空")
    bar_width = validate_positive_number(bar_width, "bar_width", allow_zero=False)

    n_groups = len(x)
    normalized_bar_data: Dict[str, np.ndarray] = {}
    for name, values in normalized_input.items():
        series_values = np.asarray(
            validate_array_like(values, f"bar_data['{name}']"),
            dtype=float,
        )
        if len(series_values) != n_groups:
            raise ValueError(
                f"bar_data['{name}'] 长度 ({len(series_values)}) 与 x 长度 ({n_groups}) 不一致"
            )
        if not np.all(np.isfinite(series_values)):
            raise ValueError(f"bar_data['{name}'] 不能包含 NaN 或 Inf")
        normalized_bar_data[name] = series_values

    normalized_line_data: Optional[Dict[str, np.ndarray]] = None
    if line_data is not None:
        if isinstance(line_data, dict):
            line_input = line_data
        else:
            line_input = {"值": line_data}
        normalized_line_data = {}
        for name, values in line_input.items():
            series_values = np.asarray(
                validate_array_like(values, f"line_data['{name}']"),
                dtype=float,
            )
            if len(series_values) != n_groups:
                raise ValueError(
                    f"line_data['{name}'] 长度 ({len(series_values)}) 与 x 长度 ({n_groups}) 不一致"
                )
            if not np.all(np.isfinite(series_values)):
                raise ValueError(f"line_data['{name}'] 不能包含 NaN 或 Inf")
            normalized_line_data[name] = series_values

    fig, ax_bar = new_styled_figure(venue, palette, lang)
    colors = _get_cycle_colors()

    n_bars = len(normalized_bar_data)
    indices = np.arange(n_groups)

    bar_width_eff = bar_width / n_bars
    for i, (name, values) in enumerate(normalized_bar_data.items()):
        offset = (i - (n_bars - 1) / 2) * bar_width_eff
        color = cycle_color(colors, i)
        ax_bar.bar(indices + offset, values, bar_width_eff, label=name, color=color, **kwargs)

    ax_bar.set_xticks(indices)
    ax_bar.set_xticklabels(x)
    ax_bar.set_xlabel(xlabel)
    ax_bar.set_ylabel(ylabel_left)

    ax_line = None
    if normalized_line_data:
        ax_line = ax_bar.twinx()

        line_colors = colors[n_bars:]
        if len(line_colors) < len(normalized_line_data):
            line_colors = colors

        for i, (name, values) in enumerate(normalized_line_data.items()):
            color = line_colors[i % len(line_colors)]
            ax_line.plot(indices, values, "o-", color=color, label=name, markersize=5)

        ax_line.set_ylabel(ylabel_right)

        lines1, labels1 = ax_bar.get_legend_handles_labels()
        lines2, labels2 = ax_line.get_legend_handles_labels()
        ax_bar.legend(lines1 + lines2, labels1 + labels2, loc="best")
    else:
        ax_bar.legend()

    if title:
        ax_bar.set_title(title)

    return ComboPlotResult(
        fig,
        ax_bar=ax_bar,
        ax_line=ax_line,
        metadata={"venue": venue, "palette": palette},
    )


# ============================================================================
# 显著性标注
# ============================================================================

def annotate_significance(
    ax: Axes,
    x1: float,
    x2: float,
    y: float,
    p_value: float,
    h: float = 0.02,
    tip_len: float = 0.01,
    color: str = "black",
    fontsize: Optional[int] = None,
    ns_text: str = "ns",
) -> None:
    """
    在箱线图/小提琴图上添加统计显著性标注（括号 + 星号）

    标注规则（国际通用）：
        p < 0.001 → ***
        p < 0.01  → **
        p < 0.05  → *
        p ≥ 0.05  → ns（not significant）

    参数:
        ax     : 目标坐标轴
        x1, x2 : 比较的两组在 x 轴上的坐标（通常是 1, 2, 3...）
        y      : 括号的 Y 坐标（数据坐标，与 y 轴数据单位相同）
                 默认 0.02，适合 y 轴范围为 [0, 1] 的场景
                 y 轴范围较大时（如 [0, 100]），建议设为 y_range * 0.03 左右
        p_value: p 值
        h      : 括号高度（数据坐标单位），默认 0.02
        tip_len: 括号端竖线长度（数据坐标单位），默认 0.01
        color  : 线条和文字颜色
        fontsize: 标注字号；None 则继承当前设置
        ns_text: p ≥ 0.05 时显示的文字，默认 "ns"

    示例:
        >>> fig, ax = sp.plot_box([d1, d2, d3], labels=["A", "B", "C"], ylabel="Score")
        >>> # 标注 A vs B 显著，A vs C 极显著
        >>> sp.annotate_significance(ax, 1, 2, y=max(d1.max(), d2.max()) + 0.5, p_value=0.03)
        >>> sp.annotate_significance(ax, 1, 3, y=max(d1.max(), d3.max()) + 1.5, p_value=0.0005)
        >>> sp.save(fig, "significance")
    """
    if not isinstance(p_value, (int, float, np.integer, np.floating)):
        raise ValueError(f"p_value 必须是 [0, 1] 范围内的数值，实际类型: {type(p_value).__name__}")

    p_value_float = float(p_value)
    if not np.isfinite(p_value_float) or not (0.0 <= p_value_float <= 1.0):
        raise ValueError(f"p_value 必须是 [0, 1] 范围内的数值，实际值: {p_value!r}")

    if x1 == x2:
        raise ValueError("x1 与 x2 不能相等，无法绘制显著性括号")

    if p_value_float < 0.001:
        marker = "***"
    elif p_value_float < 0.01:
        marker = "**"
    elif p_value_float < 0.05:
        marker = "*"
    else:
        marker = ns_text

    lw = plt.rcParams.get("lines.linewidth", 1.0)
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y],
            lw=lw, color=color, clip_on=False)

    fs_kw: Dict[str, Any] = {}
    if fontsize is not None:
        fs_kw["fontsize"] = fontsize

    ax.text(
        (x1 + x2) / 2, y + h + tip_len,
        marker,
        ha="center", va="bottom", color=color,
        **fs_kw,
    )


# ============================================================================
# 蜂群图
# ============================================================================

def _swarm_offsets(values: np.ndarray, width: float = 0.8) -> np.ndarray:
    """确定性蜂群布局：按值排序后交错分配到多行，形成紧凑蜂群形状。"""
    n = len(values)
    if n == 0:
        return np.empty(0)
    order = np.argsort(values, kind="stable")
    rows = max(1, int(np.ceil(np.sqrt(n))))

    row_of = np.empty(n, dtype=int)
    for i in range(n):
        row_of[i] = i % rows

    offsets = np.zeros(n)
    for r in range(rows):
        idxs = np.where(row_of == r)[0]
        cnt = len(idxs)
        if cnt <= 1:
            continue
        step = width / (cnt - 1)
        start = -width / 2
        for k, i in enumerate(idxs):
            offsets[i] = start + k * step

    result = np.empty(n)
    result[order] = offsets
    return result


def plot_beeswarm(
    data_list: List[np.ndarray],
    labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    method: str = "swarm",
    orient: str = "v",
    point_size: float = 4.0,
    alpha: float = 0.6,
    jitter_width: float = 0.25,
    show_box: bool = False,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制蜂群图（Beeswarm，原始数据点的紧凑分布展示）

    每个数据点以散点呈现：swarm 模式按值排序后交错排列成蜂群形状，
    展示数据的实际分布与密度；jitter 模式在组内随机抖动。
    可叠加箱线提供统计摘要。

    参数:
        data_list  : 多组数据列表，每组至少 1 个有限数值
        labels     : 各组标签；None 则自动生成 "Series N"
        method     : "swarm" 确定性蜂群 | "jitter" 随机抖动
        orient     : "v" 组沿 X 轴（垂直蜂群） | "h" 组沿 Y 轴（水平蜂群）
        point_size : 数据点大小
        alpha      : 数据点透明度
        jitter_width: jitter 模式的抖动幅度
        show_box   : 是否叠加箱线图

    示例:
        >>> fig, ax = sp.plot_beeswarm(
        ...     [ctrl, drug_a, drug_b], labels=["对照", "药物A", "药物B"],
        ...     ylabel="响应值", show_box=True,
        ... )
        >>> sp.save(fig, "beeswarm")
    """
    if not data_list:
        raise ValueError("参数 'data_list' 不能为空列表")
    if method not in {"swarm", "jitter"}:
        raise ValueError(f"method 仅支持 'swarm' / 'jitter'，实际值: {method!r}")
    if orient not in {"v", "h"}:
        raise ValueError(f"orient 仅支持 'v' / 'h'，实际值: {orient!r}")

    normalized_data: List[np.ndarray] = []
    for i, values in enumerate(data_list):
        arr = np.asarray(values, dtype=float)
        arr = arr[np.isfinite(arr)]
        if arr.size == 0:
            raise ValueError(f"data_list[{i}] 至少需要 1 个有效数据点")
        normalized_data.append(arr)

    if labels is None:
        labels = [f"Series {i + 1}" for i in range(len(normalized_data))]
    elif len(labels) != len(normalized_data):
        raise ValueError(
            f"labels 长度 ({len(labels)}) 与 data_list 长度 ({len(normalized_data)}) 不一致"
        )

    fig, ax = new_styled_figure(venue, palette, lang)

    colors = _get_cycle_colors()
    rng = np.random.default_rng(42)

    for i, (values, label) in enumerate(zip(normalized_data, labels)):
        color = cycle_color(colors, i)
        pos = float(i)

        if method == "swarm":
            offsets = _swarm_offsets(values)
        else:
            offsets = rng.uniform(-jitter_width, jitter_width, len(values))

        if orient == "v":
            ax.scatter(pos + offsets, values, s=point_size, alpha=alpha,
                       color=color, edgecolors="none", **kwargs)
        else:
            ax.scatter(values, pos + offsets, s=point_size, alpha=alpha,
                       color=color, edgecolors="none", **kwargs)

        if show_box:
            if orient == "v":
                boxplot_with_orientation(
                    ax, values, orientation="vertical", positions=[pos],
                    widths=0.35, patch_artist=True, showfliers=False,
                )
            else:
                boxplot_with_orientation(
                    ax, values, orientation="horizontal", positions=[pos],
                    widths=0.35, patch_artist=True, showfliers=False,
                )
            for patch in ax.patches[-1:]:
                patch.set_facecolor(color)
                patch.set_alpha(0.15)
                patch.set_edgecolor(color)

    if orient == "v":
        ax.set_xticks(np.arange(len(normalized_data)))
        ax.set_xticklabels(labels)
        ax.set_xlim(-0.6, len(normalized_data) - 0.4)
    else:
        ax.set_yticks(np.arange(len(normalized_data)))
        ax.set_yticklabels(labels)
        ax.set_ylim(-0.6, len(normalized_data) - 0.4)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_dumbbell(
    categories: List[str],
    start: np.ndarray,
    end: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    start_label: str = "Before",
    end_label: str = "After",
    show_values: bool = False,
    fmt: str = ".1f",
    sort_by: Optional[str] = "delta",
    line_alpha: float = 0.6,
    marker_size: float = 8.0,
    improve_color: str = "#E07B54",
    worsen_color: str = "#5B7DB1",
    neutral_color: str = "#999999",
    show_baseline: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制哑铃图（Dumbbell，两时点/两条件前后对比）

    每个类别一行：起点空心圆 + 终点实心圆 + 中间连线。
    连线按变化方向着色（改善暖色/恶化冷色），数值标签上下交替
    错位避免重叠，可叠加起点均值参考线。

    参数:
        categories : 类别标签列表
        start      : 起点数值（等长）
        end        : 终点数值（等长）
        start_label: 起点图例标签
        end_label  : 终点图例标签
        show_values: 是否在终点旁显示数值与变化量
        fmt        : 数值格式
        sort_by    : 排序方式："delta" 按变化量 | "start" | "end" | None 保持原序
        line_alpha : 连线透明度
        marker_size: 圆点大小
        improve_color: 改善（end > start）连线颜色，默认暖色
        worsen_color : 恶化（end < start）连线颜色，默认冷色
        neutral_color: 持平连线颜色
        show_baseline: 是否绘制起点均值参考虚线

    示例:
        >>> fig, ax = sp.plot_dumbbell(
        ...     ["方法A", "方法B", "方法C"],
        ...     before_scores, after_scores,
        ...     xlabel="得分", start_label="训练前", end_label="训练后",
        ...     show_values=True,
        ... )
        >>> sp.save(fig, "dumbbell")
    """
    if not categories:
        raise ValueError("参数 'categories' 不能为空列表")

    start_arr = np.asarray(start, dtype=float).ravel()
    end_arr = np.asarray(end, dtype=float).ravel()
    if len(start_arr) != len(categories) or len(end_arr) != len(categories):
        raise ValueError(
            "categories、start、end 长度必须一致"
        )
    if not np.all(np.isfinite(start_arr)) or not np.all(np.isfinite(end_arr)):
        raise ValueError("start 和 end 不能包含 NaN 或 Inf")

    if sort_by is not None and sort_by not in {"delta", "start", "end"}:
        raise ValueError(
            f"sort_by 仅支持 'delta' / 'start' / 'end' / None，实际值: {sort_by!r}"
        )

    if sort_by == "delta":
        order = np.argsort(end_arr - start_arr)
    elif sort_by == "start":
        order = np.argsort(start_arr)
    elif sort_by == "end":
        order = np.argsort(end_arr)
    else:
        order = np.arange(len(categories))

    cats = [categories[i] for i in order]
    starts = start_arr[order]
    ends = end_arr[order]

    fig, ax = new_styled_figure(venue, palette, lang)
    colors = _get_cycle_colors()

    y = np.arange(len(cats))
    # 连线：按变化方向着色
    deltas = ends - starts
    line_colors = np.where(
        deltas > 1e-9, improve_color,
        np.where(deltas < -1e-9, worsen_color, neutral_color),
    )
    for yi, (s_val, e_val) in enumerate(zip(starts, ends)):
        ax.plot([s_val, e_val], [yi, yi], color=line_colors[yi],
                linewidth=2.0, alpha=line_alpha, zorder=1)

    # 起点均值参考线
    if show_baseline:
        baseline = float(np.mean(starts))
        ax.axvline(x=baseline, color="#CCCCCC", linestyle=":", linewidth=1.0, zorder=0)

    # 起点空心圆 + 终点实心圆（双编码）
    ax.scatter(starts, y, s=marker_size**2, facecolors="white",
               edgecolors=colors[0], linewidths=1.5,
               label=start_label, zorder=3)
    ax.scatter(ends, y, s=marker_size**2, color=colors[1 % len(colors)],
               edgecolors="white", linewidths=0.8,
               label=end_label, zorder=3)

    if show_values:
        fontsize = max(6, plt.rcParams.get("font.size", 9) - 1)
        for idx, (yi, (s_val, e_val)) in enumerate(zip(y, zip(starts, ends))):
            delta = e_val - s_val
            # 上下交替偏移避免相邻标签重叠
            dy = 0.22 if idx % 2 == 0 else -0.22
            ax.text(
                e_val, yi + dy, f"{e_val:{fmt}} ({delta:+.1f})",
                ha="left", va="center", fontsize=fontsize, color="#444444",
            )

    polish_axis(ax, categorical_axis="y", clean_spines=True, grid="x")
    ax.set_yticks(y)
    ax.set_yticklabels(cats)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.legend(loc="best", frameon=False)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_diverging_bar(
    categories: List[str],
    values: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    threshold: float = 0.0,
    positive_color: Optional[str] = None,
    negative_color: Optional[str] = None,
    show_values: bool = False,
    fmt: str = ".1f",
    sort: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制发散条形图（Diverging Bar，正负对比水平条形）

    以 threshold 为分界向两侧发散：正值一侧一种颜色、负值另一侧
    另一种颜色，适合满意度、净变化、效应量等正负双向数据。

    参数:
        categories    : 类别标签列表
        values        : 数值（等长，可正可负）
        threshold     : 发散分界值，默认 0
        positive_color: 正值条形颜色；None 取配色第一色
        negative_color: 负值条形颜色；None 取配色第二色
        show_values   : 是否在条尾显示数值
        sort          : 是否按数值排序（默认 True，便于阅读）

    示例:
        >>> # 满意度净推荐值（NPS）
        >>> fig, ax = sp.plot_diverging_bar(
        ...     ["功能A", "功能B", "功能C"],
        ...     np.array([42, -18, 35]),
        ...     xlabel="净推荐值", show_values=True,
        ... )
        >>> sp.save(fig, "diverging")
    """
    if not categories:
        raise ValueError("参数 'categories' 不能为空列表")

    values_arr = np.asarray(values, dtype=float).ravel()
    if len(values_arr) != len(categories):
        raise ValueError(
            f"categories 长度 ({len(categories)}) 与 values 长度 ({len(values_arr)}) 不一致"
        )
    if not np.all(np.isfinite(values_arr)):
        raise ValueError("values 不能包含 NaN 或 Inf")

    fig, ax = new_styled_figure(venue, palette, lang)
    colors = _get_cycle_colors()

    pos_color = positive_color if positive_color is not None else colors[0]
    neg_color = negative_color if negative_color is not None else colors[1 % len(colors)]

    if sort:
        order = np.argsort(values_arr)
        cats = [categories[i] for i in order]
        vals = values_arr[order]
    else:
        cats = list(categories)
        vals = values_arr

    y = np.arange(len(cats))
    bar_colors = [pos_color if v >= threshold else neg_color for v in vals]
    has_edge_override = "edgecolor" in kwargs or "ec" in kwargs
    has_alpha_override = "alpha" in kwargs
    bars = ax.barh(y, vals - threshold, left=threshold, color=bar_colors, **kwargs)
    if not has_edge_override and not has_alpha_override:
        style_patch_edges(bars, bar_colors, fill_alpha=0.86, darken_amount=0.26, linewidth=0.7)
    ax.axvline(x=threshold, color="#64748B", linestyle="--", linewidth=1.0, zorder=2)

    if show_values:
        fontsize = max(6, plt.rcParams.get("font.size", 9) - 1)
        for yi, v in enumerate(vals):
            if v >= threshold:
                ax.text(v + abs(v) * 0.02 + 0.01, yi, f"{v:{fmt}}",
                        ha="left", va="center", fontsize=fontsize)
            else:
                ax.text(v - abs(v) * 0.02 - 0.01, yi, f"{v:{fmt}}",
                        ha="right", va="center", fontsize=fontsize)

    polish_axis(ax, categorical_axis="y", clean_spines=True, grid="x")
    ax.set_yticks(y)
    ax.set_yticklabels(cats)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_waffle(
    categories: List[str],
    values: np.ndarray,
    rows: int = 10,
    cols: int = 10,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    colors: Optional[List[str]] = None,
    show_percent: bool = True,
    percent_fmt: str = ".0f",
    square: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制华夫图（Waffle Chart，100 格占比构成）

    将总量拆分为 rows×cols 个格子，每类按占比分配格数并着色，
    直观呈现构成比例，适合汇报/PPT 场景。

    参数:
        categories  : 类别标签列表
        values      : 各类数值（等长、非负；总和自动归一化）
        rows / cols : 格子行列数（默认 10×10 = 100 格）
        colors      : 每类颜色；None 用当前配色循环
        show_percent: 是否显示各类百分比
        percent_fmt : 百分比格式
        square      : 格子是否为正方形（保持纵横比）

    示例:
        >>> fig, ax = sp.plot_waffle(
        ...     ["训练", "验证", "测试"],
        ...     np.array([70, 15, 15]),
        ... )
        >>> sp.save(fig, "waffle")
    """
    if not categories:
        raise ValueError("参数 'categories' 不能为空列表")
    values_arr = np.asarray(values, dtype=float).ravel()
    if len(values_arr) != len(categories):
        raise ValueError(
            f"values 长度 ({len(values_arr)}) 与 categories 长度 ({len(categories)}) 不一致"
        )
    if not np.all(np.isfinite(values_arr)):
        raise ValueError("values 不能包含 NaN 或 Inf")
    if np.any(values_arr < 0):
        raise ValueError("values 不能包含负值")
    total_value = float(values_arr.sum())
    if total_value <= 0:
        raise ValueError("values 总和必须大于 0")
    if not isinstance(rows, int) or rows <= 0 or not isinstance(cols, int) or cols <= 0:
        raise ValueError("rows/cols 必须为正整数")

    # palette 是本次调用的参数，应在读取颜色循环前生效，避免受到上一张图
    # 全局 rcParams 的影响。
    fig, ax = new_styled_figure(venue, palette, lang)

    if colors is not None:
        if len(colors) != len(categories):
            raise ValueError(
                f"colors 长度 ({len(colors)}) 与 categories 长度 ({len(categories)}) 不一致"
            )
    else:
        cycle = _get_cycle_colors()
        colors = [cycle_color(cycle, i) for i in range(len(categories))]

    # 按比例分配格数（最后一项补齐差额）
    n_cells = rows * cols
    raw_counts = values_arr / total_value * n_cells
    counts = np.floor(raw_counts).astype(int)
    diff = n_cells - int(counts.sum())
    # 将差额分配给余数最大的类别
    if diff > 0:
        remainders = raw_counts - counts
        order = np.argsort(remainders)[::-1]
        for idx in order:
            if diff <= 0:
                break
            counts[idx] += 1
            diff -= 1

    # 逐格绘制（从左上开始，按类别顺序填充）
    cell_idx = 0
    patches_by_category: List[List[Any]] = [[] for _ in range(len(categories))]
    for r in range(rows):
        for c_i in range(cols):
            # 找到当前格属于哪个类别
            cat = 0
            acc = 0
            for k, cnt in enumerate(counts):
                acc += cnt
                if cell_idx < acc:
                    cat = k
                    break
            x, y = c_i, rows - 1 - r
            rect = plt.Rectangle(
                (x, y), 0.92, 0.92,
                facecolor=colors[cat], edgecolor="white", linewidth=0.5,
                **kwargs,
            )
            ax.add_patch(rect)
            patches_by_category[cat].append(rect)
            cell_idx += 1

    # 类别分隔线（可选）——在边界处加粗
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    if square:
        ax.set_aspect("equal")
    ax.set_axis_off()

    # 图例 + 百分比
    from matplotlib.patches import Patch

    labels_display = []
    for cat, cnt in zip(categories, counts):
        pct = cnt / n_cells * 100
        if show_percent:
            labels_display.append(f"{cat}  {pct:{percent_fmt}}%")
        else:
            labels_display.append(cat)
    handles = [Patch(facecolor=c, label=l) for c, l in zip(colors, labels_display)]
    ax.legend(handles=handles, loc="center left", bbox_to_anchor=(1.02, 0.5),
              frameon=False)

    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


# ============================================================================
# 帕累托图（贡献排序柱 + 累积占比曲线）
# ============================================================================

def plot_pareto(
    categories: List[str],
    values: Union[List[float], np.ndarray],
    xlabel: str = "",
    ylabel: str = "数值 / 频数",
    cum_ylabel: str = "累积占比 (%)",
    title: str = "",
    threshold: float = 80.0,
    show_values: bool = True,
    value_fmt: str = ".0f",
    line_color: Optional[str] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制帕累托图（降序柱状图 + 次轴累积百分比折线 + 80% 关键少数阈值线）。

    自动按数值降序排列类别，以柔和色彩区分处于累积阈值内的核心驱动因素，
    通过次坐标系叠加累积百分比折线并标注关键拐点，适合归因分解与关键瓶颈识别。

    参数:
        categories : 类别名称列表
        values     : 各类别非负数值列表或数组
        threshold  : 关键少数累积阈值（百分比，默认 80.0，传入 None 则不画参考线）
        show_values: 是否在柱顶标注原始数值
        value_fmt  : 数值格式字符串，默认 ``".0f"``
        line_color : 累积折线颜色；None 时选取次色或深灰强调色
    """
    from sciplot._core.layout import create_twinx
    from sciplot.utils.guards import polish_axis, style_patch_edges

    if not categories:
        raise ValueError("参数 'categories' 不能为空列表")
    vals_arr = np.asarray(values, dtype=float).ravel()
    if len(vals_arr) != len(categories):
        raise ValueError(
            f"categories 长度 ({len(categories)}) 与 values 长度 ({len(vals_arr)}) 不一致"
        )
    if not np.all(np.isfinite(vals_arr)):
        raise ValueError("values 不能包含 NaN 或 Inf")
    if np.any(vals_arr < 0):
        raise ValueError("帕累托图 values 必须非负")
    total = float(np.sum(vals_arr))
    if total <= 0:
        raise ValueError("values 总和必须大于 0")
    if threshold is not None and not (0.0 < float(threshold) <= 100.0):
        raise ValueError(f"threshold 必须在 (0, 100] 范围内，实际值: {threshold!r}")

    order = np.argsort(vals_arr)[::-1]
    sorted_vals = vals_arr[order]
    sorted_cats = [str(categories[i]) for i in order]
    cum_pct = np.cumsum(sorted_vals) / total * 100.0

    fig, ax = new_styled_figure(venue, palette, lang)
    colors = _get_cycle_colors()
    primary_c = colors[0]
    secondary_c = line_color or (colors[1] if len(colors) > 1 else "#C0392B")
    muted_c = "#CBD5E1"

    x = np.arange(len(sorted_cats))
    if threshold is not None:
        bar_fills = [
            primary_c if (i == 0 or cum_pct[i - 1] < float(threshold)) else muted_c
            for i in range(len(sorted_cats))
        ]
    else:
        bar_fills = [primary_c] * len(sorted_cats)

    bars = ax.bar(x, sorted_vals, width=0.64, color=bar_fills, **kwargs)
    style_patch_edges(bars, bar_fills, fill_alpha=0.88, darken_amount=0.25, linewidth=0.7)

    if show_values:
        max_v = float(sorted_vals.max())
        for bar, v in zip(bars, sorted_vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max_v * 0.018,
                f"{v:{value_fmt}}",
                ha="center", va="bottom",
                fontsize=max(6, int(plt.rcParams.get("font.size", 9)) - 1),
            )

    ax.set_xticks(x)
    ax.set_xticklabels(sorted_cats)
    ax.set_ylim(0, float(sorted_vals.max()) * 1.15)
    polish_axis(ax, categorical_axis="x", clean_spines=True, grid="y")

    ax2 = create_twinx(ax)
    ax2.plot(
        x, cum_pct, color=secondary_c, marker="o", markersize=4.5,
        markerfacecolor="white", markeredgewidth=1.3, linewidth=1.8, zorder=5,
        label=cum_ylabel,
    )
    ax2.set_ylim(0, 108)
    ax2.set_ylabel(cum_ylabel, color=secondary_c)
    ax2.tick_params(axis="y", which="both", colors=secondary_c, right=True)
    ax2.yaxis.set_minor_locator(plt.NullLocator())
    if "top" in ax2.spines:
        ax2.spines["top"].set_visible(False)

    if threshold is not None:
        thr = float(threshold)
        ax2.axhline(thr, color=secondary_c, linestyle="--", linewidth=0.95, alpha=0.75)
        ax2.text(
            len(sorted_cats) - 0.5, thr + 2.2, f"{thr:.0f}%",
            color=secondary_c, ha="right", va="bottom",
            fontsize=max(6, int(plt.rcParams.get("font.size", 9)) - 1),
        )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    auto_rotate_labels(ax, axis="x")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


# ============================================================================
# 分组小提琴图（Grouped Violin）
# ============================================================================

def plot_grouped_violin(
    categories: Sequence[str],
    series: Dict[str, Sequence[Sequence[float]]],
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    show_box: bool = True,
    show_mean: bool = False,
    show_points: bool = False,
    width: float = 0.74,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制双因素分组小提琴图（外层分组 × 内部条件分布对比）。

    每个大类内并排绘制多个条件的小提琴分布，统一叠加密度轮廓、深色边界、
    内嵌 IQR 四分位胶囊与白点中位数，并支持原始散点抖动叠加与极淡分组分隔线。

    参数:
        categories : 主分组名称序列（X 轴刻度标签）
        series     : 字典 ``{条件名: [每个主分组的样本序列, ...]}``
        xlabel     : X 轴标签
        ylabel     : Y 轴标签
        title      : 图标题
        show_box   : 是否在琴身内部绘制 IQR 四分位胶囊与白点中位数，默认 True
        show_mean  : 是否绘制均值菱形标记，默认 False
        show_points: 是否叠加半透明抖动原始样本点，默认 False
        width      : 单个大类占用的总水平宽度（默认 0.74）
        venue      : 期刊样式预设
        palette    : 配色方案名称
        lang       : 语言设置

    返回:
        PlotResult 对象，支持 ``fig, ax = sp.plot_grouped_violin(...)`` 解包。

    示例:
        >>> fig, ax = sp.plot_grouped_violin(
        ...     ["Stage I", "Stage II", "Stage III"],
        ...     {"Control": [c1, c2, c3], "Treatment": [t1, t2, t3]},
        ...     ylabel="Biomarker Level",
        ... )
    """
    from matplotlib.colors import to_hex
    from matplotlib.patches import Patch
    from sciplot.utils import darken_color
    from sciplot.utils.guards import polish_axis
    from sciplot.utils.smart import smart_legend

    cat_list = [str(c) for c in categories]
    if not cat_list:
        raise ValueError("参数 'categories' 不能为空")
    validate_dict_not_empty(series, "series")
    if not (0.1 <= width <= 0.98):
        raise ValueError(f"width 必须在 [0.1, 0.98] 范围内，实际值: {width!r}")

    n_cats = len(cat_list)
    series_names = list(series.keys())
    n_series = len(series_names)

    parsed_series: Dict[str, List[np.ndarray]] = {}
    for name, groups in series.items():
        if len(groups) != n_cats:
            raise ValueError(
                f"系列 '{name}' 的分组数量 ({len(groups)}) 与 categories 长度 ({n_cats}) 不一致"
            )
        arr_list: List[np.ndarray] = []
        for idx, g in enumerate(groups):
            arr = np.asarray(g, dtype=float).ravel()
            if arr.size == 0:
                raise ValueError(f"系列 '{name}' 第 {idx} 组样本不能为空")
            if not np.all(np.isfinite(arr)):
                raise ValueError(f"系列 '{name}' 第 {idx} 组不能包含 NaN 或 Inf")
            arr_list.append(arr)
        parsed_series[str(name)] = arr_list

    fig, ax = new_styled_figure(venue, palette, lang)
    colors = _get_cycle_colors()

    slot_w = width / n_series
    v_w = slot_w * 0.84
    rng = np.random.default_rng(42)

    if n_cats >= 2:
        for sep_idx in range(n_cats - 1):
            ax.axvline(sep_idx + 0.5, color="#CBD5E1", linestyle=":", linewidth=0.8, alpha=0.65, zorder=0)

    legend_handles: List[Patch] = []
    for j, name in enumerate(series_names):
        c = cycle_color(colors, j)
        try:
            edge_c = darken_color(to_hex(c), amount=0.28)
        except Exception:
            edge_c = "#2D3436"
        offset = (j - (n_series - 1) / 2.0) * slot_w

        for i, vals in enumerate(parsed_series[name]):
            pos = float(i) + offset
            violin_input = vals if vals.size >= 2 else np.array([vals[0], vals[0]])
            parts = ax.violinplot(
                [violin_input],
                positions=[pos],
                widths=v_w,
                showmeans=False,
                showmedians=False,
                showextrema=False,
                **kwargs,
            )
            for pc in parts["bodies"]:  # type: ignore[attr-defined]
                pc.set_facecolor(c)
                pc.set_alpha(0.55)
                pc.set_edgecolor(edge_c)
                pc.set_linewidth(0.95)
                pc.set_zorder(2)

            if show_box:
                _draw_violin_quartiles(
                    ax,
                    pos,
                    vals,
                    showmedians=True,
                    showmeans=show_mean,
                    capsule_width=max(2.4, min(3.8, v_w * 12.0)),
                )

            if show_points:
                jit = rng.uniform(-v_w * 0.16, v_w * 0.16, size=vals.size)
                ax.scatter(
                    pos + jit,
                    vals,
                    s=9,
                    alpha=0.38,
                    color=c,
                    edgecolors="white",
                    linewidths=0.3,
                    zorder=2,
                )

        legend_handles.append(
            Patch(facecolor=c, edgecolor=edge_c, alpha=0.65, linewidth=0.85, label=name)
        )

    ax.set_xticks(np.arange(n_cats))
    ax.set_xticklabels(cat_list)
    ax.set_xlim(-0.55, n_cats - 0.45)
    polish_axis(ax, categorical_axis="x", clean_spines=True, grid="y")
    auto_rotate_labels(ax, axis="x")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    if n_series > 1:
        ax.legend(handles=legend_handles, frameon=False)
        smart_legend(ax)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


# ============================================================================
# 镜像双向水平柱状图（Back-to-Back Bar / Mirror Bar）
# ============================================================================

def plot_back_to_back_bar(
    categories: Sequence[str],
    left_values: Sequence[float],
    right_values: Sequence[float],
    left_label: str = "Group A",
    right_label: str = "Group B",
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    show_values: bool = True,
    show_diff: bool = True,
    fmt: str = ".1f",
    sort_by: Optional[str] = None,
    bar_height: float = 0.62,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制镜像双向水平柱状图，用于两组在多个指标上的直观对称对比。

    左侧水平条以中心 0 轴向左延伸、右侧向右延伸，自动提供正值对称刻度、
    柱端数值标签与右侧净差异（``Δ = R - L``）摘要列，避免拥挤感。

    参数:
        categories  : 类别或指标名称列表
        left_values : 左侧组非负数值序列（与 categories 等长）
        right_values: 右侧组非负数值序列（与 categories 等长）
        left_label  : 左侧组名称，默认 "Group A"
        right_label : 右侧组名称，默认 "Group B"
        xlabel      : X 轴标签
        ylabel      : Y 轴标签
        title       : 图标题
        show_values : 是否在两侧柱体末端标注数值，默认 True
        show_diff   : 是否在右侧附加差异列 ``Δ = R - L``，默认 True
        fmt         : 数值格式化字符串，默认 ".1f"
        sort_by     : 可选排序方式：None / "left" / "right" / "diff"（降序置顶）
        bar_height  : 柱体高度，默认 0.62
        venue       : 期刊样式预设
        palette     : 配色方案名称
        lang        : 语言设置

    返回:
        PlotResult 对象。

    示例:
        >>> fig, ax = sp.plot_back_to_back_bar(
        ...     ["Accuracy", "Recall", "Precision", "F1"],
        ...     [82.4, 79.1, 84.0, 81.5],
        ...     [88.6, 85.4, 86.2, 85.8],
        ...     left_label="Baseline", right_label="Ours",
        ... )
    """
    from matplotlib.ticker import FuncFormatter
    from sciplot._core.utils import relative_fontsize
    from sciplot.utils.guards import polish_axis, style_patch_edges, truncate_tick_labels
    from sciplot.utils.smart import smart_legend

    cat_list = [str(c) for c in categories]
    if not cat_list:
        raise ValueError("参数 'categories' 不能为空")

    l_arr = np.asarray(left_values, dtype=float).ravel()
    r_arr = np.asarray(right_values, dtype=float).ravel()
    if l_arr.size != len(cat_list) or r_arr.size != len(cat_list):
        raise ValueError(
            f"left_values ({l_arr.size}) 与 right_values ({r_arr.size}) 长度必须与 categories ({len(cat_list)}) 一致"
        )
    if not np.all(np.isfinite(l_arr)) or not np.all(np.isfinite(r_arr)):
        raise ValueError("left_values 和 right_values 不能包含 NaN 或 Inf")
    if np.any(l_arr < 0) or np.any(r_arr < 0):
        raise ValueError("plot_back_to_back_bar 要求非负数值；含正负值的对比请使用 plot_diverging_bar")
    if sort_by not in {None, "left", "right", "diff"}:
        raise ValueError(f"sort_by 仅支持 None / 'left' / 'right' / 'diff'，实际值: {sort_by!r}")

    if sort_by is not None:
        key_arr = l_arr if sort_by == "left" else (r_arr if sort_by == "right" else np.abs(r_arr - l_arr))
        order = np.argsort(-key_arr, kind="stable")
        cat_list = [cat_list[i] for i in order]
        l_arr = l_arr[order]
        r_arr = r_arr[order]

    fig, ax = new_styled_figure(venue, palette, lang)
    colors = _get_cycle_colors()
    c_left = colors[0]
    c_right = colors[1] if len(colors) > 1 else "#E76F51"

    y = np.arange(len(cat_list), dtype=float)
    bar_kw = dict(kwargs)
    has_edge = "edgecolor" in bar_kw or "ec" in bar_kw
    has_alpha = "alpha" in bar_kw

    bars_l = ax.barh(y, -l_arr, height=bar_height, color=c_left, label=left_label, zorder=3, **bar_kw)
    bars_r = ax.barh(y, r_arr, height=bar_height, color=c_right, label=right_label, zorder=3, **bar_kw)
    if not has_edge and not has_alpha:
        style_patch_edges(bars_l, [c_left] * len(cat_list), fill_alpha=0.86, darken_amount=0.25, linewidth=0.75)
        style_patch_edges(bars_r, [c_right] * len(cat_list), fill_alpha=0.86, darken_amount=0.25, linewidth=0.75)

    ax.axvline(0.0, color="#334155", linewidth=1.05, zorder=4)

    max_extent = float(max(np.max(l_arr), np.max(r_arr), 1e-6))
    pad = max_extent * 0.025
    fs = relative_fontsize(-1, floor=6)

    if show_values:
        for yi, lv, rv in zip(y, l_arr, r_arr):
            ax.text(
                -lv - pad, yi, format(lv, fmt),
                ha="right", va="center", fontsize=fs, color="#334155", zorder=5,
            )
            ax.text(
                rv + pad, yi, format(rv, fmt),
                ha="left", va="center", fontsize=fs, color="#334155", zorder=5,
            )

    if show_diff:
        diff_fs = relative_fontsize(-1, floor=6)
        for yi, lv, rv in zip(y, l_arr, r_arr):
            delta = rv - lv
            d_color = c_right if delta > 1e-12 else (c_left if delta < -1e-12 else "#64748B")
            ax.text(
                1.02, yi, f"Δ{delta:+{fmt}}",
                transform=ax.get_yaxis_transform(),
                ha="left", va="center", fontsize=diff_fs,
                fontweight="bold", color=d_color, clip_on=False,
            )

    xlim_scale = 1.24 if show_values else 1.10
    ax.set_xlim(-max_extent * xlim_scale, max_extent * xlim_scale)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _pos: f"{abs(x):g}"))
    ax.set_yticks(y)
    ax.set_yticklabels(cat_list)
    ax.invert_yaxis()
    truncate_tick_labels(ax, axis="y", max_len=24)
    polish_axis(ax, categorical_axis="y", clean_spines=True, grid="x")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    smart_legend(ax)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


# ============================================================================
# 内部工具
# ============================================================================

# _get_cycle_colors 已从 sciplot._core.utils.get_cycle_colors 导入
# 文字对比色判断统一使用 sciplot._core.utils.contrast_text_color
