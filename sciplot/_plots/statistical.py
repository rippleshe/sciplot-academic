"""
统计图表 — 残差图、QQ图、Bland-Altman图

用于统计检验、模型诊断、方法一致性分析等。
"""

from __future__ import annotations

import warnings
from typing import Any, Dict, List, Optional, Tuple
from statistics import NormalDist

import matplotlib.pyplot as plt
import numpy as np

from sciplot._core.utils import (
    boxplot_with_orientation,
    get_cycle_colors as _get_cycle_colors,
    cycle_color,
    new_styled_figure,
    relative_fontsize,
    _try_import_optional,
    _require_optional,
)
from sciplot._core.result import PlotResult
from sciplot.utils.smart import smart_legend


# _get_cycle_colors 已从 sciplot._core.utils 导入（其内部保证 prop_cycle 非空）


def _is_constant(values: np.ndarray) -> bool:
    """判断序列是否为常数序列。

    gaussian_kde 在零方差数据上会抛出 LinAlgError，各分布图函数
    因此需要先检测常数序列并退化为垂直线/水平线。
    """
    return float(values.min()) == float(values.max())


def _check_scipy_stats() -> Any:
    """检查 scipy.stats 可用性并返回模块对象。"""
    return _require_optional("scipy.stats", "统计图表功能")


def _theoretical_quantiles_without_scipy(
    n_points: int,
    distribution: str,
) -> np.ndarray:
    """在未安装 scipy 时生成常见分布的理论分位数。"""
    probs = (np.arange(1, n_points + 1) - 0.5) / n_points

    if distribution == "norm":
        return np.array([NormalDist().inv_cdf(float(p)) for p in probs], dtype=float)

    if distribution == "expon":
        return -np.log1p(-probs)

    if distribution == "uniform":
        return probs

    if distribution == "t":
        # df=10 的 Cornish-Fisher 近似，兼顾精度与无 scipy 兼容性。
        df = 10.0
        z = np.array([NormalDist().inv_cdf(float(p)) for p in probs], dtype=float)
        z2 = z * z
        z3 = z2 * z
        z5 = z3 * z2
        return (
            z
            + (z3 + z) / (4.0 * df)
            + (5.0 * z5 + 16.0 * z3 + 3.0 * z) / (96.0 * df * df)
        )

    raise ValueError(f"未知分布: {distribution}")


def plot_residuals(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    xlabel: str = "预测值",
    ylabel: str = "残差",
    title: str = "",
    show_zero_line: bool = True,
    show_loess: bool = False,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制残差图（预测值 vs 残差）

    参数:
        y_true        : 真实值
        y_pred        : 预测值
        xlabel        : X 轴标签
        ylabel        : Y 轴标签
        title         : 图标题
        show_zero_line: 是否显示零线参考
        show_loess    : 是否显示 LOESS 平滑曲线（需要 statsmodels）
        lang          : 语言设置

    示例:
        >>> y_true = np.array([1, 2, 3, 4, 5])
        >>> y_pred = np.array([1.1, 2.2, 2.9, 4.1, 4.8])
        >>> fig, ax = sp.plot_residuals(y_true, y_pred, title="模型残差分析")
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    if len(y_true) != len(y_pred):
        raise ValueError(
            f"y_true 长度 ({len(y_true)}) 与 y_pred 长度 ({len(y_pred)}) 不一致"
        )

    residuals = y_true - y_pred

    fig, ax = new_styled_figure(venue, palette, lang)

    colors = _get_cycle_colors()

    ax.scatter(y_pred, residuals, alpha=0.6, color=colors[0], **kwargs)

    if show_zero_line:
        ax.axhline(y=0, color="gray", linestyle="--", linewidth=1)

    if show_loess and len(y_pred) > 5:
        try:
            from statsmodels.nonparametric.smoothers_lowess import lowess  # type: ignore[import-untyped]
            sorted_idx = np.argsort(y_pred)
            smoothed = lowess(residuals[sorted_idx], y_pred[sorted_idx], frac=0.6)
            ax.plot(smoothed[:, 0], smoothed[:, 1], color=colors[1 % len(colors)],
                   linewidth=2, label="LOESS")
            ax.legend()
        except ImportError:
            warnings.warn(
                "show_loess=True 需要安装 statsmodels，已跳过 LOESS 曲线。\n"
                "请运行: pip install statsmodels",
                UserWarning,
                stacklevel=3,
            )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_qq(
    data: np.ndarray,
    distribution: str = "norm",
    xlabel: str = "理论分位数",
    ylabel: str = "样本分位数",
    title: str = "",
    show_line: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制 Q-Q 图（检验数据分布）

    参数:
        data        : 样本数据
        distribution: 理论分布类型
                      - "norm": 正态分布（默认）
                      - "expon": 指数分布
                      - "uniform": 均匀分布
                      - "t": t 分布
        xlabel      : X 轴标签
        ylabel      : Y 轴标签
        title       : 图标题
        show_line   : 是否显示参考线
        lang        : 语言设置

    示例:
        >>> data = np.random.normal(0, 1, 100)
        >>> fig, ax = sp.plot_qq(data, title="正态性检验")
    """
    stats = _try_import_optional("scipy.stats")

    data = np.asarray(data, dtype=float)
    data = data[np.isfinite(data)]

    if len(data) < 3:
        raise ValueError("数据点太少，至少需要 3 个有效值")

    dist_map = {"norm", "expon", "uniform", "t"}

    if distribution not in dist_map:
        raise ValueError(
            f"未知分布: {distribution}。可选: {sorted(dist_map)}"
        )

    fig, ax = new_styled_figure(venue, palette, lang)

    colors = _get_cycle_colors()

    if stats is not None:
        scipy_dist_map = {
            "norm": (stats.norm, ()),
            "expon": (stats.expon, ()),
            "uniform": (stats.uniform, ()),
            "t": (stats.t, (10,)),
        }
        dist_obj, sparams = scipy_dist_map[distribution]
        (osm, osr), (slope, intercept, _r) = stats.probplot(
            data,
            dist=dist_obj,
            sparams=sparams,
            plot=None,
        )
    else:
        warnings.warn(
            "未安装 scipy，plot_qq 使用近似分位数计算。",
            UserWarning,
            stacklevel=2,
        )
        osr = np.sort(data)
        osm = _theoretical_quantiles_without_scipy(len(osr), distribution)
        slope, intercept = np.polyfit(osm, osr, 1)

    ax.scatter(osm, osr, alpha=0.6, color=colors[0], **kwargs)

    if show_line:
        x_line = np.array([osm.min(), osm.max()])
        y_line = slope * x_line + intercept
        ax.plot(x_line, y_line, color=colors[1 % len(colors)], linestyle="--", linewidth=2)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_bland_altman(
    y1: np.ndarray,
    y2: np.ndarray,
    xlabel: str = "均值",
    ylabel: str = "差值",
    title: str = "",
    show_ci: bool = True,
    ci: float = 0.95,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制 Bland-Altman 图（两种测量方法的一致性分析）

    参数:
        y1     : 第一种方法的测量值
        y2     : 第二种方法的测量值
        xlabel : X 轴标签
        ylabel : Y 轴标签
        title  : 图标题
        show_ci: 是否显示一致性界限的置信区间
        ci     : 置信水平，默认 0.95
        lang   : 语言设置

    示例:
        >>> method_a = np.array([1.1, 2.0, 3.2, 4.1, 5.0])
        >>> method_b = np.array([1.0, 2.1, 3.0, 4.0, 5.2])
        >>> fig, ax = sp.plot_bland_altman(method_a, method_b,
        ...     title="两种方法一致性分析")
    """
    stats = _check_scipy_stats()

    y1 = np.asarray(y1)
    y2 = np.asarray(y2)

    if len(y1) != len(y2):
        raise ValueError(
            f"y1 长度 ({len(y1)}) 与 y2 长度 ({len(y2)}) 不一致"
        )
    if len(y1) < 2:
        raise ValueError(
            f"Bland-Altman 分析至少需要 2 个数据点，当前: {len(y1)}"
        )

    mean_vals = (y1 + y2) / 2
    diff_vals = y1 - y2

    mean_diff = float(np.mean(diff_vals))
    std_diff = float(np.std(diff_vals, ddof=1))

    upper_loa = mean_diff + 1.96 * std_diff
    lower_loa = mean_diff - 1.96 * std_diff

    fig, ax = new_styled_figure(venue, palette, lang)

    colors = _get_cycle_colors()

    ax.scatter(mean_vals, diff_vals, alpha=0.6, color=colors[0], **kwargs)

    ax.axhline(y=mean_diff, color=colors[1 % len(colors)], linestyle="-",
              linewidth=2, label=f"均值差 = {mean_diff:.3f}")
    ax.axhline(y=upper_loa, color=colors[2 % len(colors)], linestyle="--",
              linewidth=1.5, label=f"+1.96 SD = {upper_loa:.3f}")
    ax.axhline(y=lower_loa, color=colors[2 % len(colors)], linestyle="--",
              linewidth=1.5, label=f"-1.96 SD = {lower_loa:.3f}")

    if show_ci:
        n = len(diff_vals)
        se_loa = np.sqrt(3 * std_diff**2 / n)
        z = stats.norm.ppf((1 + ci) / 2)

        upper_ci_upper = upper_loa + z * se_loa
        upper_ci_lower = upper_loa - z * se_loa
        lower_ci_upper = lower_loa + z * se_loa
        lower_ci_lower = lower_loa - z * se_loa

        mean_min, mean_max = mean_vals.min(), mean_vals.max()
        x_ci = np.array([mean_min, mean_max])

        ax.fill_between(x_ci, upper_ci_lower, upper_ci_upper,
                       color=colors[2 % len(colors)], alpha=0.1)
        ax.fill_between(x_ci, lower_ci_lower, lower_ci_upper,
                       color=colors[2 % len(colors)], alpha=0.1)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.legend(loc="best")

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_density(
    data: np.ndarray,
    xlabel: str = "",
    ylabel: str = "Density",
    title: str = "",
    bw_method: Optional[float] = None,
    fill: bool = True,
    alpha: float = 0.3,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制核密度估计曲线。

    参数:
        lang: 语言设置
    """
    stats = _check_scipy_stats()

    values = np.asarray(data, dtype=float)
    values = values[np.isfinite(values)]
    if values.size < 2:
        raise ValueError("plot_density 至少需要 2 个有效数据点")

    fig, ax = new_styled_figure(venue, palette, lang)

    if _is_constant(values):
        # 常数序列：退化为绘制垂直线，表示全部质量集中于此点。
        colors = _get_cycle_colors()
        ax.axvline(x=float(values[0]), color=colors[0], linestyle="--", linewidth=1.5)
    else:
        kde = stats.gaussian_kde(values, bw_method=bw_method)
        x_eval = np.linspace(values.min(), values.max(), 256)
        y_eval = kde(x_eval)

        (line,) = ax.plot(x_eval, y_eval, **kwargs)
        if fill:
            ax.fill_between(x_eval, y_eval, alpha=alpha, color=line.get_color())

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_multi_density(
    data_list: List[np.ndarray],
    labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "Density",
    title: str = "",
    bw_method: Optional[float] = None,
    fill: bool = False,
    alpha: float = 0.2,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制多组核密度估计曲线。

    参数:
        fill: 是否绘制密度曲线下方填充，默认 False
        alpha: 填充透明度，仅在 fill=True 时生效
        lang: 语言设置
    """
    stats = _check_scipy_stats()
    if not data_list:
        raise ValueError("data_list 不能为空")

    normalized_data = []
    for i, values in enumerate(data_list):
        arr = np.asarray(values, dtype=float)
        arr = arr[np.isfinite(arr)]
        if arr.size < 2:
            raise ValueError(f"data_list[{i}] 至少需要 2 个有效数据点")
        normalized_data.append(arr)

    if labels is None:
        labels = [f"Series {i + 1}" for i in range(len(normalized_data))]
    elif len(labels) != len(normalized_data):
        raise ValueError(
            f"labels 长度 ({len(labels)}) 与 data_list 长度 ({len(normalized_data)}) 不一致"
        )

    fig, ax = new_styled_figure(venue, palette, lang)

    all_values = np.concatenate(normalized_data)
    x_eval = np.linspace(all_values.min(), all_values.max(), 256)

    for values, label in zip(normalized_data, labels):
        if _is_constant(values):
            # 常数序列：KDE 退化，绘制垂直线表示质量集中。
            ax.axvline(x=float(values[0]), linestyle="--", linewidth=1.5, label=label)
            continue
        kde = stats.gaussian_kde(values, bw_method=bw_method)
        y_eval = kde(x_eval)
        (line,) = ax.plot(x_eval, y_eval, label=label, **kwargs)
        if fill:
            ax.fill_between(x_eval, y_eval, alpha=alpha, color=line.get_color())

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    smart_legend(ax)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_ridgeline(
    data_list: List[np.ndarray],
    labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    overlap: float = 0.3,
    fill: bool = True,
    alpha: float = 0.55,
    bw_method: Optional[float] = None,
    show_median: bool = False,
    median_color: str = "#444444",
    median_alpha: float = 0.85,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制山脊图（Ridgeline / Joyplot，多组分布堆叠对比）

    每组数据的 KDE 曲线沿 Y 轴堆叠，各组互相重叠错开，
    适合一次对比多个分布的形状、中心与展宽（如不同条件下的
    响应分布、多实验重复）。

    参数:
        data_list  : 多组数据列表，每组至少 2 个有限数值
        labels     : 各组标签；None 则自动生成 "Series N"
        overlap    : 相邻山脊的重叠比例（0~1，越小越分离），默认 0.3
        fill       : 是否填充山脊内部，默认 True
        alpha      : 填充透明度，默认 0.55
        bw_method  : KDE 带宽参数，透传 scipy.stats.gaussian_kde
        show_median: 是否在各山脊上标注中位数刻度线
        median_color: 中位数刻度线颜色
        median_alpha: 中位数刻度线透明度
        lang       : 语言设置

    示例:
        >>> # 多条件分布对比
        >>> groups = [
        ...     np.random.normal(0, 1, 300),
        ...     np.random.normal(0.8, 1.2, 300),
        ...     np.random.normal(1.6, 0.8, 300),
        ... ]
        >>> fig, ax = sp.plot_ridgeline(
        ...     groups, labels=["对照组", "处理A", "处理B"],
        ...     xlabel="响应值", ylabel="组",
        ...     show_median=True,
        ... )
        >>> sp.save(fig, "ridgeline")
    """
    stats = _check_scipy_stats()
    if not data_list:
        raise ValueError("data_list 不能为空")

    if not isinstance(overlap, (int, float)) or not (0.0 <= overlap < 1.0):
        raise ValueError(
            f"overlap 必须在 [0, 1) 范围内，实际值: {overlap!r}"
        )

    normalized_data: List[np.ndarray] = []
    for i, values in enumerate(data_list):
        arr = np.asarray(values, dtype=float)
        arr = arr[np.isfinite(arr)]
        if arr.size < 2:
            raise ValueError(f"data_list[{i}] 至少需要 2 个有效数据点")
        normalized_data.append(arr)

    if labels is None:
        labels = [f"Series {i + 1}" for i in range(len(normalized_data))]
    elif len(labels) != len(normalized_data):
        raise ValueError(
            f"labels 长度 ({len(labels)}) 与 data_list 长度 ({len(normalized_data)}) 不一致"
        )

    fig, ax = new_styled_figure(venue, palette, lang)

    colors = _get_cycle_colors()

    all_values = np.concatenate(normalized_data)
    x_eval = np.linspace(all_values.min(), all_values.max(), 256)
    step = 1.0 - overlap

    for i, (values, label) in enumerate(zip(normalized_data, labels)):
        base = i * step
        color = cycle_color(colors, i)

        if _is_constant(values):
            # 常数序列：KDE 退化，绘制垂直线表示质量集中。
            ax.plot([values[0], values[0]], [base, base + 0.85],
                    color=color, linewidth=1.5, label=label, **kwargs)
            if show_median:
                ax.axvline(x=float(values[0]), ymin=(base + 0.1) / (base + 1.2),
                           ymax=(base + 0.9) / (base + 1.2),
                           color=median_color, alpha=median_alpha, linewidth=1.0)
            continue

        kde = stats.gaussian_kde(values, bw_method=bw_method)
        y_eval = kde(x_eval)
        y_norm = y_eval / y_eval.max()

        ax.plot(x_eval, base + y_norm, color=color, linewidth=1.4, label=label, **kwargs)
        if fill:
            ax.fill_between(x_eval, base, base + y_norm, color=color, alpha=alpha)

        if show_median:
            median_val = float(np.median(values))
            ax.axvline(
                x=median_val, ymin=(base + 0.08) / (base + 1.2),
                ymax=(base + 0.95) / (base + 1.2),
                color=median_color, alpha=median_alpha, linewidth=1.0,
            )

    ax.set_yticks([i * step for i in range(len(normalized_data))])
    ax.set_yticklabels(labels)
    ax.set_ylim(-0.15, (len(normalized_data) - 1) * step + 1.15)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    smart_legend(ax)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_raincloud(
    data_list: List[np.ndarray],
    labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    orientation: str = "h",
    show_points: bool = True,
    show_box: bool = True,
    show_violin: bool = True,
    show_median: bool = True,
    point_alpha: float = 0.35,
    point_size: float = 4.0,
    point_jitter: float = 0.08,
    box_width: float = 0.15,
    violin_scale: float = 0.35,
    violin_alpha: float = 0.45,
    bw_method: Optional[float] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制雨云图（Raincloud：原始数据点 + 箱线 + 半小提琴三合一）

    每个分组同时展示：原始数据点（左侧“雨滴”）、箱线（中部摘要）、
    半小提琴（右侧分布形状），兼顾原始数据透明度与统计摘要，
    是现代论文高频的分布对比方式（Allen et al., 2021）。

    参数:
        data_list   : 多组数据列表，每组至少 2 个有限数值
        labels      : 各组标签；None 则自动生成 "Series N"
        orientation : "h" 分组沿 Y 轴（水平），"v" 分组沿 X 轴（垂直）
        show_points : 是否显示原始数据点
        show_box    : 是否显示箱线
        show_violin : 是否显示半小提琴
        show_median : 是否显示中位数刻度线
        point_alpha : 数据点透明度
        point_size  : 数据点大小
        point_jitter: 数据点抖动幅度（分组方向）
        box_width   : 箱线宽度
        violin_scale: 半小提琴高度（相对组距），默认 0.35
        violin_alpha: 半小提琴透明度
        bw_method   : KDE 带宽参数

    示例:
        >>> fig, ax = sp.plot_raincloud(
        ...     [ctrl, drug_a, drug_b], labels=["对照", "药物A", "药物B"],
        ...     xlabel="响应值", ylabel="组",
        ... )
        >>> sp.save(fig, "raincloud")
    """
    stats = _check_scipy_stats()
    if not data_list:
        raise ValueError("data_list 不能为空")
    if orientation not in {"h", "v"}:
        raise ValueError(f"orientation 仅支持 'h' / 'v'，实际值: {orientation!r}")

    normalized_data: List[np.ndarray] = []
    for i, values in enumerate(data_list):
        arr = np.asarray(values, dtype=float)
        arr = arr[np.isfinite(arr)]
        if arr.size < 2:
            raise ValueError(f"data_list[{i}] 至少需要 2 个有效数据点")
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

        if orientation == "h":
            # ── 原始数据点（左侧） ──
            if show_points:
                jitter = rng.uniform(-point_jitter, point_jitter, len(values))
                ax.scatter(
                    values, pos - 0.28 + jitter,
                    s=point_size, alpha=point_alpha, color=color,
                    edgecolors="none",
                )

            # ── 箱线（中部） ──
            if show_box:
                boxplot_with_orientation(
                    ax, values, orientation="horizontal", positions=[pos],
                    widths=box_width, patch_artist=True, showfliers=False,
                )
                for patch in ax.patches[-1:]:
                    patch.set_facecolor(color)
                    patch.set_alpha(0.35)

            # ── 半小提琴（右侧） ──
            if show_violin:
                if _is_constant(values):
                    ax.plot([values[0], values[0]], [pos, pos + violin_scale * 2],
                            color=color, linewidth=1.2)
                else:
                    kde = stats.gaussian_kde(values, bw_method=bw_method)
                    x_eval = np.linspace(values.min(), values.max(), 200)
                    d = kde(x_eval)
                    d = d / d.max() * violin_scale
                    ax.fill_between(x_eval, pos, pos + d, color=color, alpha=violin_alpha)
                    ax.plot(x_eval, pos + d, color=color, linewidth=1.0)

            # ── 中位数刻度 ──
            if show_median:
                median_val = float(np.median(values))
                ax.plot([median_val, median_val], [pos + 0.02, pos + violin_scale * 2 - 0.02],
                        color="#333333", linewidth=1.0, alpha=0.9)
        else:
            # 垂直版本：镜像布局（点在下、箱线居中、小提琴在上）
            if show_points:
                jitter = rng.uniform(-point_jitter, point_jitter, len(values))
                ax.scatter(
                    pos - 0.28 + jitter, values,
                    s=point_size, alpha=point_alpha, color=color,
                    edgecolors="none",
                )

            if show_box:
                boxplot_with_orientation(
                    ax, values, orientation="vertical", positions=[pos],
                    widths=box_width, patch_artist=True, showfliers=False,
                )
                for patch in ax.patches[-1:]:
                    patch.set_facecolor(color)
                    patch.set_alpha(0.35)

            if show_violin:
                if _is_constant(values):
                    ax.plot([pos, pos + violin_scale * 2], [values[0], values[0]],
                            color=color, linewidth=1.2)
                else:
                    kde = stats.gaussian_kde(values, bw_method=bw_method)
                    y_eval = np.linspace(values.min(), values.max(), 200)
                    d = kde(y_eval)
                    d = d / d.max() * violin_scale
                    ax.fill_betweenx(y_eval, pos, pos + d, color=color, alpha=violin_alpha)
                    ax.plot(pos + d, y_eval, color=color, linewidth=1.0)

            if show_median:
                median_val = float(np.median(values))
                ax.plot([pos + 0.02, pos + violin_scale * 2 - 0.02], [median_val, median_val],
                        color="#333333", linewidth=1.0, alpha=0.9)

    # 坐标轴标签与范围
    if orientation == "h":
        ax.set_yticks(np.arange(len(normalized_data)))
        ax.set_yticklabels(labels)
        ax.set_ylim(-0.6, len(normalized_data) - 0.4)
    else:
        ax.set_xticks(np.arange(len(normalized_data)))
        ax.set_xticklabels(labels)
        ax.set_xlim(-0.6, len(normalized_data) - 0.4)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_volcano(
    log2fc: np.ndarray,
    p_values: np.ndarray,
    labels: Optional[List[str]] = None,
    xlabel: str = "log2(Fold Change)",
    ylabel: str = "-log10(p)",
    title: str = "",
    fc_threshold: float = 1.0,
    p_threshold: float = 0.05,
    color_up: str = "#D62728",
    color_down: str = "#1F77B4",
    color_ns: str = "#BBBBBB",
    alpha: float = 0.6,
    annotate_top: bool = True,
    top_n: int = 8,
    show_thresholds: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制火山图（Volcano Plot，组学/大规模差异分析）

    横轴为 log2 倍数变化（效应大小），纵轴为 -log10(p)（显著性），
    按阈值将点分为显著上调 / 显著下调 / 不显著三类着色，
    并可标注最显著的若干特征。

    参数:
        log2fc       : log2 倍数变化数组
        p_values     : 显著性 p 值数组（与 log2fc 等长，允许 0）
        labels       : 特征标签（等长，用于标注）；None 则不标注
        fc_threshold : 倍数变化阈值，默认 1.0（即 2 倍）
        p_threshold  : 显著性阈值，默认 0.05
        color_up     : 显著上调颜色，默认红
        color_down   : 显著下调颜色，默认蓝
        color_ns     : 不显著颜色，默认灰
        alpha        : 散点透明度
        annotate_top : 是否标注最显著的 top_n 个特征
        top_n        : 标注数量，默认 8
        show_thresholds: 是否绘制阈值参考线

    示例:
        >>> # 差异表达基因分析
        >>> fig, ax = sp.plot_volcano(
        ...     log2fc, p_values, labels=gene_names,
        ...     fc_threshold=1.0, p_threshold=0.05,
        ...     xlabel="log2(FC)", ylabel="-log10(p)",
        ... )
        >>> sp.save(fig, "volcano")
    """
    fc = np.asarray(log2fc, dtype=float).ravel()
    p = np.asarray(p_values, dtype=float).ravel()

    n = len(fc)
    if len(p) != n:
        raise ValueError(
            f"log2fc 长度 ({n}) 与 p_values 长度 ({len(p)}) 不一致"
        )
    if n == 0:
        raise ValueError("log2fc/p_values 不能为空")
    if not np.all(np.isfinite(fc)):
        raise ValueError("log2fc 不能包含 NaN 或 Inf")
    if np.any(p < 0) or np.any(~np.isfinite(p[p > 0])):
        raise ValueError("p_values 必须为 [0, 1] 范围内的有限数值")
    if np.any(p > 1.0):
        raise ValueError("p_values 必须为 [0, 1] 范围内的有限数值")
    if labels is not None and len(labels) != n:
        raise ValueError(
            f"labels 长度 ({len(labels)}) 与数据长度 ({n}) 不一致"
        )
    if not 0 < p_threshold <= 1:
        raise ValueError(f"p_threshold 必须在 (0, 1] 范围内，实际值: {p_threshold!r}")
    if fc_threshold <= 0:
        raise ValueError(f"fc_threshold 必须为正数，实际值: {fc_threshold!r}")

    # -log10(p)，p=0 时用最小非零 p 的对数值（避免 inf）
    nonzero_p = p[p > 0]
    if nonzero_p.size == 0:
        neg_log10p = np.full(n, 10.0)
    else:
        min_log = -np.log10(float(nonzero_p.min()))
        # 避免对 p==0 计算 log10（np.where 会全量求值）
        safe_p = np.where(p > 0, p, 1.0)
        with np.errstate(divide="ignore"):
            neg_log10p = np.where(p > 0, -np.log10(safe_p), min_log + 0.5)

    # 三分类着色
    is_sig = p <= p_threshold
    is_up = is_sig & (fc >= fc_threshold)
    is_down = is_sig & (fc <= -fc_threshold)
    colors = np.where(is_up, color_up, np.where(is_down, color_down, color_ns))

    fig, ax = new_styled_figure(venue, palette, lang)

    scatter_kwargs: Dict[str, Any] = {"s": 18, "edgecolors": "none"}
    scatter_kwargs.update(kwargs)
    # 分类颜色和显式 alpha 是 volcano API 的语义参数；即使 kwargs 中出现同名键，
    # 也不允许产生重复关键字或悄悄覆盖三分类编码。
    scatter_kwargs["c"] = colors
    scatter_kwargs["alpha"] = alpha
    ax.scatter(fc, neg_log10p, **scatter_kwargs)

    if show_thresholds:
        ax.axvline(x=fc_threshold, color="#888888", linestyle="--", linewidth=0.8)
        ax.axvline(x=-fc_threshold, color="#888888", linestyle="--", linewidth=0.8)
        ax.axhline(y=-np.log10(p_threshold), color="#888888", linestyle="--", linewidth=0.8)

    # 图例（语言跟随当前设置）
    from matplotlib.patches import Patch

    from sciplot._core.style import get_current_lang

    active_lang = lang or get_current_lang() or "zh"
    if active_lang in {"zh", "zh-cn"}:
        legend_labels = ["显著上调", "显著下调", "不显著"]
    else:
        legend_labels = ["Up-regulated", "Down-regulated", "Not significant"]
    handles = [
        Patch(facecolor=color_up, label=legend_labels[0], alpha=alpha),
        Patch(facecolor=color_down, label=legend_labels[1], alpha=alpha),
        Patch(facecolor=color_ns, label=legend_labels[2], alpha=alpha),
    ]
    legend = ax.legend(handles=handles, loc="upper left", frameon=False)

    # 标注最显著的 top_n 个特征（显著性优先，其次按 |fc|）。
    # 这里必须在图例创建之后做，因为 legend 本身也是实际版面的障碍物。
    # 旧实现把 data-coordinate 距离直接当成 offset points，既不能保证文字之间
    # 不碰撞，也无法避免图例与上边界；现在直接基于 renderer 的像素 bounding box
    # 逐个试放，保证标注与已放文字、图例、坐标轴边界之间留出真实间距。
    if annotate_top and labels is not None and top_n > 0:
        score = neg_log10p + np.abs(fc) * 0.1
        top_idx = np.argsort(score)[::-1][:top_n]
        fontsize = max(6.0, float(plt.rcParams.get("font.size", 9)) - 2.0)

        # 给顶部标注留出约 9% 的数据高度。margins 不改变零点/阈值语义，
        # 只扩展自动 y limit；用户后续仍可显式 set_ylim 覆盖。
        ax.margins(x=0.025, y=0.09)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        axes_bbox = ax.get_window_extent(renderer=renderer)
        legend_bbox = legend.get_window_extent(renderer=renderer).expanded(1.04, 1.08)

        # 优先把文字放在点的“内侧”：左半边向右、右半边向左，降低轴外裁剪概率。
        vertical_offsets = (7, 18, -9, 30, -20, 43, -33, 57, -47)
        horizontal_offsets = (6, 13, 21)
        placed_bboxes: List[Any] = []

        def _bbox_inside_axes(box: Any, padding: float = 2.0) -> bool:
            return (
                box.x0 >= axes_bbox.x0 + padding
                and box.x1 <= axes_bbox.x1 - padding
                and box.y0 >= axes_bbox.y0 + padding
                and box.y1 <= axes_bbox.y1 - padding
            )

        for idx in sorted(top_idx, key=lambda i: -neg_log10p[i]):
            x0, y0 = float(fc[idx]), float(neg_log10p[idx])
            side = 1 if x0 < 0 else -1
            ha = "left" if side > 0 else "right"
            accepted = None

            for dx_abs in horizontal_offsets:
                if accepted is not None:
                    break
                for dy in vertical_offsets:
                    annotation = ax.annotate(
                        str(labels[idx]),
                        xy=(x0, y0),
                        xytext=(side * dx_abs, dy),
                        textcoords="offset points",
                        ha=ha,
                        va="center",
                        fontsize=fontsize,
                        annotation_clip=True,
                    )
                    fig.canvas.draw()
                    box = annotation.get_window_extent(renderer=renderer).expanded(1.03, 1.08)
                    collides = box.overlaps(legend_bbox) or any(
                        box.overlaps(prev) for prev in placed_bboxes
                    )
                    if _bbox_inside_axes(box) and not collides:
                        accepted = (annotation, box)
                        break
                    annotation.remove()

            # 极端拥挤时宁可少标一个，也不要输出互相盖住、越界的文字。
            if accepted is not None:
                placed_bboxes.append(accepted[1])

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_forest(
    effect: np.ndarray,
    ci_low: np.ndarray,
    ci_high: np.ndarray,
    labels: Optional[List[str]] = None,
    summary: Optional[Tuple[float, float, float]] = None,
    reference: float = 0.0,
    xlabel: str = "效应量 (95% CI)",
    title: str = "",
    summary_label: Optional[str] = None,
    show_value_labels: bool = True,
    value_format: str = "{:.2f}",
    color: Optional[str] = None,
    summary_color: str = "#C0392B",
    band_alpha: float = 0.35,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制森林图（Forest Plot，Meta 分析 / 多队列效应对比）

    每行一项研究/队列：点表示效应量，横线表示 95% 置信区间；
    中心竖线为参考线（如无效线 0 或合并效应），
    底部可加菱形表示合并效应（summary 参数）。
    行背景交替灰色带，便于跨行对比（Nature 高频排版）。

    参数:
        effect   : 各研究效应量数组
        ci_low   : 各研究 95% CI 下限（与 effect 等长）
        ci_high  : 各研究 95% CI 上限（与 effect 等长）
        labels   : 研究名称（等长）；None 时用序号
        summary  : (合并效应, CI下限, CI上限)；None 则不绘制合并菱形
        reference: 参考线位置（默认 0.0，即无效线）
        xlabel   : 横轴标签
        title    : 图标题
        summary_label: 合并行标签（默认 "汇总" / "Summary"，跟随语言）
        show_value_labels: 是否在右侧显示数值标签
        value_format: 数值标签格式
        color    : 点/线颜色；None 用主题色循环第一个
        summary_color: 合并菱形颜色（默认深红，突出 Meta 结论）
        band_alpha: 交替行背景透明度

    示例:
        >>> # Meta 分析：各研究效应量与合并效应
        >>> fig, ax = sp.plot_forest(
        ...     effect=[0.8, 0.5, 1.1, 0.6, 0.9],
        ...     ci_low=[0.3, 0.1, 0.7, 0.2, 0.5],
        ...     ci_high=[1.3, 0.9, 1.5, 1.0, 1.3],
        ...     labels=["研究 1", "研究 2", "研究 3", "研究 4", "研究 5"],
        ...     summary=(0.72, 0.52, 0.92),
        ... )
        >>> sp.save(fig, "forest")
    """
    eff = np.asarray(effect, dtype=float).ravel()
    lo = np.asarray(ci_low, dtype=float).ravel()
    hi = np.asarray(ci_high, dtype=float).ravel()

    n = len(eff)
    if n == 0:
        raise ValueError("effect 不能为空")
    if len(lo) != n or len(hi) != n:
        raise ValueError(
            f"ci_low/ci_high 长度 ({len(lo)}/{len(hi)}) 与 effect ({n}) 不一致"
        )
    if not np.all(np.isfinite(eff)) or not np.all(np.isfinite(lo)) or not np.all(np.isfinite(hi)):
        raise ValueError("effect/ci_low/ci_high 不能包含 NaN 或 Inf")
    if np.any(lo > hi):
        raise ValueError("ci_low 必须小于等于 ci_high")
    if labels is not None and len(labels) != n:
        raise ValueError(f"labels 长度 ({len(labels)}) 与数据长度 ({n}) 不一致")
    if summary is not None:
        if len(summary) != 3:
            raise ValueError("summary 必须是 (effect, ci_low, ci_high) 三元组")
        if not all(np.isfinite(v) for v in summary):
            raise ValueError("summary 不能包含 NaN 或 Inf")
        if summary[1] > summary[2]:
            raise ValueError("summary CI 下限必须小于等于上限")

    fig, ax = new_styled_figure(venue, palette, lang)
    line_color = color or _get_cycle_colors()[0]

    # 行位置：研究从上到下，序号增大向下
    ys = np.arange(n, 0, -1, dtype=float)
    # 交替行背景（浅灰带）
    for i in range(n):
        if i % 2 == 1:
            ax.axhspan(ys[i] - 0.5, ys[i] + 0.5, color="#999999",
                       alpha=band_alpha, zorder=0)

    # 置信区间线
    ax.hlines(ys, lo, hi, color=line_color, linewidth=1.6, zorder=3)
    # 效应量点（菱形或方形标记）
    ax.scatter(eff, ys, marker="D", s=42, color=line_color,
               edgecolors="white", linewidths=0.6, zorder=4)

    # 参考线（无效线 / 合并线）
    ax.axvline(reference, color="#444444", linestyle="--", linewidth=1.0, zorder=2)

    # 右侧数值标签（x 用 axes 坐标，y 用数据坐标）
    if show_value_labels:
        fontsize = relative_fontsize(-1, floor=6)
        for i in range(n):
            text = f"{value_format.format(eff[i])} [{value_format.format(lo[i])}, {value_format.format(hi[i])}]"
            ax.text(1.01, ys[i], text, transform=ax.get_yaxis_transform(),
                    fontsize=fontsize, va="center", ha="left",
                    color="#333333", clip_on=False)

    # 左侧研究标签
    label_list: List[str]
    if labels is None:
        label_list = [f"{i + 1}" for i in range(n)]
    else:
        label_list = [str(lb) for lb in labels]

    # 合并效应（底部菱形）
    plot_ymax = float(n) + 0.5
    if summary is not None:
        summary_effect, summary_lo, summary_hi = summary
        # 菱形顶点：左右 = CI 边界，上下 = 菱形高度
        diamond_h = 0.38
        sy = 0.0
        ax.fill([summary_lo, summary_effect, summary_hi, summary_effect],
                [sy, sy + diamond_h, sy, sy - diamond_h],
                color=summary_color, edgecolor="black", linewidth=0.7, zorder=5)
        # 汇总行背景（浅色）
        ax.axhspan(-0.55, 0.55, color=summary_color, alpha=0.12, zorder=0)
        # 汇总行标签
        if summary_label is None:
            from sciplot._core.style import get_current_lang

            active_lang = lang or get_current_lang() or "zh"
            summary_label = "汇总" if active_lang in {"zh", "zh-cn"} else "Summary"
        plot_ymax = max(plot_ymax, 0.8)
    else:
        summary_effect = None

    # 设置 y 轴：研究行在上，汇总行（如有）在下
    ymin = -0.75 if summary is not None else 0.5
    ax.set_ylim(ymin, plot_ymax)

    # 研究名标签（x 用 axes 坐标，y 用数据坐标；transAxes 会把数据值
    # 误当归一化坐标导致 tight 边界异常拉伸）
    for i in range(n):
        ax.text(-0.02, ys[i], label_list[i], transform=ax.get_yaxis_transform(),
                fontsize=relative_fontsize(-1, floor=6),
                va="center", ha="right", clip_on=False)
    if summary is not None and summary_label:
        ax.text(-0.02, 0.0, summary_label, transform=ax.get_yaxis_transform(),
                fontsize=relative_fontsize(0, floor=6),
                va="center", ha="right", fontweight="bold",
                color=summary_color, clip_on=False)

    ax.set_yticks([])
    ax.set_xlabel(xlabel)
    if title:
        ax.set_title(title)

    # 右侧数值区留白：数据区右侧留出标签空间（axes 坐标 1.0 之外）
    xlim = ax.get_xlim()
    span = xlim[1] - xlim[0]
    ax.set_xlim(xlim[0], xlim[1] + span * 0.30)

    meta: Dict[str, Any] = {"venue": venue, "palette": palette}
    if summary is not None:
        meta["summary"] = tuple(summary)
    return PlotResult(fig, ax, metadata=meta)


def plot_funnel(
    effect: np.ndarray,
    se: np.ndarray,
    ci_low: Optional[np.ndarray] = None,
    ci_high: Optional[np.ndarray] = None,
    reference: Optional[float] = None,
    xlabel: str = "效应量",
    ylabel: str = "标准误",
    title: str = "",
    show_ci_triangle: bool = True,
    show_legend: bool = True,
    point_color: Optional[str] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制漏斗图（Funnel Plot，发表偏倚检测）

    横轴为效应量，纵轴为标准误（倒置：精度高的研究在上方）。
    无偏倚时各研究对称分布于合并效应两侧，呈倒漏斗形。
    可叠加 95% 置信三角带辅助判断对称性。

    参数:
        effect   : 各研究效应量数组
        se       : 各研究标准误（与 effect 等长，必须 > 0）
        ci_low/ci_high: 各研究 95% CI（可选，用于画 CI 短线）
        reference: 参考线（合并效应）位置；None 时用加权均值
        show_ci_triangle: 是否绘制 95% 置信三角带
        show_legend: 是否显示图例
        point_color: 点颜色；None 用主题色循环第一个

    示例:
        >>> # Meta 分析发表偏倚检查
        >>> fig, ax = sp.plot_funnel(
        ...     effect=[0.8, 0.5, 1.1, 0.6, 0.9],
        ...     se=[0.25, 0.30, 0.20, 0.28, 0.22],
        ... )
        >>> sp.save(fig, "funnel")
    """
    eff = np.asarray(effect, dtype=float).ravel()
    se_arr = np.asarray(se, dtype=float).ravel()

    n = len(eff)
    if n == 0:
        raise ValueError("effect 不能为空")
    if len(se_arr) != n:
        raise ValueError(f"se 长度 ({len(se_arr)}) 与 effect ({n}) 不一致")
    if not np.all(np.isfinite(eff)) or not np.all(np.isfinite(se_arr)):
        raise ValueError("effect/se 不能包含 NaN 或 Inf")
    if np.any(se_arr <= 0):
        raise ValueError("se 必须全部为正数")
    if ci_low is not None or ci_high is not None:
        if ci_low is None or ci_high is None:
            raise ValueError("ci_low 与 ci_high 必须同时提供")
        lo = np.asarray(ci_low, dtype=float).ravel()
        hi = np.asarray(ci_high, dtype=float).ravel()
        if len(lo) != n or len(hi) != n:
            raise ValueError("ci_low/ci_high 长度与 effect 不一致")
        if np.any(lo > hi):
            raise ValueError("ci_low 必须小于等于 ci_high")
    else:
        lo = hi = None

    fig, ax = new_styled_figure(venue, palette, lang)
    point_color_final = point_color or _get_cycle_colors()[0]

    # 参考线：显式给定或逆方差加权均值
    if reference is None:
        w = 1.0 / (se_arr**2)
        reference = float(np.sum(w * eff) / np.sum(w))

    # 95% 置信三角带（±1.96·SE，随 SE 线性展开；分层描边更精致）
    if show_ci_triangle:
        se_max = float(np.max(se_arr))
        se_range = np.linspace(0.02, se_max * 1.15, 120)
        upper = reference + 1.96 * se_range
        lower = reference - 1.96 * se_range
        ax.fill_betweenx(se_range, lower, upper,
                         color="#9AA5B1", alpha=0.16, zorder=1,
                         label="95% 置信区间" if show_legend else None)
        # 三角带边界线（细虚线，增强视觉结构）
        ax.plot(upper, se_range, color="#9AA5B1", linewidth=0.7,
                linestyle=":", zorder=1)
        ax.plot(lower, se_range, color="#9AA5B1", linewidth=0.7,
                linestyle=":", zorder=1)

    # CI 短线（可选）
    if lo is not None and hi is not None:
        ax.hlines(se_arr, lo, hi, color="#8A93A0", linewidth=0.9, zorder=2)

    # 散点：点大小随精度（1/SE²）增大，突出高精度研究
    weights = 1.0 / (se_arr**2)
    sizes = 24 + 46 * (weights / np.max(weights))
    ax.scatter(eff, se_arr, s=sizes, color=point_color_final, alpha=0.8,
               edgecolors="white", linewidths=0.6, zorder=3,
               label="研究" if show_legend else None)

    # 参考线
    ax.axvline(reference, color="#333333", linestyle="--", linewidth=1.1, zorder=4,
               label="合并效应" if show_legend else None)

    # 倒置 y 轴：精度高的研究在上
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    if show_legend:
        ax.legend(loc="upper right", frameon=False, fontsize="small")

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = [
    "plot_residuals",
    "plot_qq",
    "plot_bland_altman",
    "plot_density",
    "plot_multi_density",
    "plot_ridgeline",
    "plot_raincloud",
    "plot_volcano",
    "plot_forest",
    "plot_funnel",
]
