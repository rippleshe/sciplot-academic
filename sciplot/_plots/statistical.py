"""
统计图表 — 残差图、QQ图、Bland-Altman图

用于统计检验、模型诊断、方法一致性分析等。
"""

from __future__ import annotations

import warnings
from typing import Any, List, Optional
from statistics import NormalDist

import matplotlib.pyplot as plt
import numpy as np

from sciplot._core.utils import (
    boxplot_with_orientation,
    get_cycle_colors as _get_cycle_colors,
    new_styled_figure,
)
from sciplot._core.result import PlotResult


# _get_cycle_colors 已从 sciplot._core.utils 导入（其内部保证 prop_cycle 非空）


def _is_constant(values: np.ndarray) -> bool:
    """判断序列是否为常数序列。

    gaussian_kde 在零方差数据上会抛出 LinAlgError，各分布图函数
    因此需要先检测常数序列并退化为垂直线/水平线。
    """
    return float(values.min()) == float(values.max())


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
    ax.tick_params(direction="in")

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
    ax.tick_params(direction="in")

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

    fig, ax = new_styled_figure(venue, palette, lang)

    colors = _get_cycle_colors()

    all_values = np.concatenate(normalized_data)
    x_eval = np.linspace(all_values.min(), all_values.max(), 256)
    step = 1.0 - overlap

    for i, (values, label) in enumerate(zip(normalized_data, labels)):
        base = i * step
        color = colors[i % len(colors)]

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
    ax.legend()
    ax.tick_params(direction="in")
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
        color = colors[i % len(colors)]
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
    ax.tick_params(direction="in")
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

    ax.scatter(fc, neg_log10p, c=colors, alpha=alpha, s=18, edgecolors="none", **kwargs)

    if show_thresholds:
        ax.axvline(x=fc_threshold, color="#888888", linestyle="--", linewidth=0.8)
        ax.axvline(x=-fc_threshold, color="#888888", linestyle="--", linewidth=0.8)
        ax.axhline(y=-np.log10(p_threshold), color="#888888", linestyle="--", linewidth=0.8)

    # 标注最显著的 top_n 个特征（显著性优先，其次按 |fc|）
    if annotate_top and labels is not None and top_n > 0:
        score = neg_log10p + np.abs(fc) * 0.1
        top_idx = np.argsort(score)[::-1][:top_n]
        fontsize = max(6, plt.rcParams.get("font.size", 9) - 2)
        for idx in top_idx:
            ax.annotate(
                str(labels[idx]),
                xy=(fc[idx], neg_log10p[idx]),
                xytext=(5, 5), textcoords="offset points",
                fontsize=fontsize,
            )

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
    ax.legend(handles=handles, loc="upper left", frameon=False)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
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
]
