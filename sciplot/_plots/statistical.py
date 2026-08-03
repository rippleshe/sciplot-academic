"""
统计图表 — 残差图、QQ图、Bland-Altman图

用于统计检验、模型诊断、方法一致性分析等。
"""

from __future__ import annotations

import warnings
from typing import Any, List, Optional
from statistics import NormalDist

import numpy as np

from sciplot._core.layout import new_figure
from sciplot._core.utils import (
    apply_resolved_style,
    get_cycle_colors as _get_cycle_colors,
    _ensure_non_empty_prop_cycle,
)
from sciplot._core.result import PlotResult


# _get_cycle_colors 和 _ensure_non_empty_prop_cycle 已从 sciplot._core.utils 导入


def _try_import_scipy_stats() -> Any:
    """尝试导入 scipy.stats，失败时返回 None。"""
    try:
        from scipy import stats
        return stats
    except ImportError:
        return None


def _check_scipy_stats() -> Any:
    """检查 scipy.stats 可用性并返回模块对象。"""
    stats = _try_import_scipy_stats()
    if stats is not None:
        return stats
    raise ImportError(
        "统计图表功能需要安装 scipy。\n"
        "请运行: uv pip install scipy 或 pip install scipy"
    )


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
    title: str = "残差图",
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

    effective_venue = apply_resolved_style(venue, palette, lang)
    _ensure_non_empty_prop_cycle()
    fig, ax = new_figure(effective_venue)

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
    ax.tick_params(direction="in")

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_qq(
    data: np.ndarray,
    distribution: str = "norm",
    xlabel: str = "理论分位数",
    ylabel: str = "样本分位数",
    title: str = "Q-Q 图",
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
    stats = _try_import_scipy_stats()

    data = np.asarray(data, dtype=float)
    data = data[np.isfinite(data)]

    if len(data) < 3:
        raise ValueError("数据点太少，至少需要 3 个有效值")

    dist_map = {"norm", "expon", "uniform", "t"}

    if distribution not in dist_map:
        raise ValueError(
            f"未知分布: {distribution}。可选: {sorted(dist_map)}"
        )

    effective_venue = apply_resolved_style(venue, palette, lang)
    _ensure_non_empty_prop_cycle()
    fig, ax = new_figure(effective_venue)

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
    ax.tick_params(direction="in")

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_bland_altman(
    y1: np.ndarray,
    y2: np.ndarray,
    xlabel: str = "均值",
    ylabel: str = "差值",
    title: str = "Bland-Altman 图",
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

    effective_venue = apply_resolved_style(venue, palette, lang)
    _ensure_non_empty_prop_cycle()
    fig, ax = new_figure(effective_venue)

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
    ax.tick_params(direction="in")

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

    effective_venue = apply_resolved_style(venue, palette, lang)
    _ensure_non_empty_prop_cycle()
    fig, ax = new_figure(effective_venue)

    if values.min() == values.max():
        # 常数序列：gaussian_kde 在零方差数据上会抛出 LinAlgError，
        # 退化为绘制垂直线，表示全部质量集中于此点。
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
    ax.tick_params(direction="in")
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

    effective_venue = apply_resolved_style(venue, palette, lang)
    _ensure_non_empty_prop_cycle()
    fig, ax = new_figure(effective_venue)

    all_values = np.concatenate(normalized_data)
    x_eval = np.linspace(all_values.min(), all_values.max(), 256)

    for values, label in zip(normalized_data, labels):
        if values.min() == values.max():
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
    ax.legend()
    ax.tick_params(direction="in")
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

    effective_venue = apply_resolved_style(venue, palette, lang)
    _ensure_non_empty_prop_cycle()
    fig, ax = new_figure(effective_venue)

    colors = _get_cycle_colors()

    all_values = np.concatenate(normalized_data)
    x_eval = np.linspace(all_values.min(), all_values.max(), 256)
    step = 1.0 - overlap

    for i, (values, label) in enumerate(zip(normalized_data, labels)):
        base = i * step
        color = colors[i % len(colors)]

        if values.min() == values.max():
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
    ax.legend()
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = [
    "plot_residuals",
    "plot_qq",
    "plot_bland_altman",
    "plot_density",
    "plot_multi_density",
    "plot_ridgeline",
]
