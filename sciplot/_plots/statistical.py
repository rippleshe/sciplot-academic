"""
统计图表 — 残差图、QQ图、Bland-Altman图

用于统计检验、模型诊断、方法一致性分析等。
"""

from __future__ import annotations

from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from sciplot._core.layout import new_figure
from sciplot._core.utils import apply_resolved_style
from sciplot._core.result import PlotResult


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

    effective_venue = apply_resolved_style(venue, palette)
    fig, ax = new_figure(effective_venue)

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

    ax.scatter(y_pred, residuals, alpha=0.6, color=colors[0], **kwargs)

    if show_zero_line:
        ax.axhline(y=0, color="gray", linestyle="--", linewidth=1)

    if show_loess and len(y_pred) > 5:
        try:
            from statsmodels.nonparametric.smoothers_lowess import lowess
            sorted_idx = np.argsort(y_pred)
            smoothed = lowess(residuals[sorted_idx], y_pred[sorted_idx], frac=0.6)
            ax.plot(smoothed[:, 0], smoothed[:, 1], color=colors[1 % len(colors)],
                   linewidth=2, label="LOESS")
            ax.legend()
        except ImportError:
            pass

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

    示例:
        >>> data = np.random.normal(0, 1, 100)
        >>> fig, ax = sp.plot_qq(data, title="正态性检验")
    """
    from scipy import stats

    data = np.asarray(data, dtype=float)
    data = data[np.isfinite(data)]

    if len(data) < 3:
        raise ValueError("数据点太少，至少需要 3 个有效值")

    dist_map = {
        "norm": (stats.norm, ()),
        "expon": (stats.expon, ()),
        "uniform": (stats.uniform, ()),
        "t": (stats.t, (10,)),
    }

    if distribution not in dist_map:
        raise ValueError(
            f"未知分布: {distribution}。可选: {list(dist_map.keys())}"
        )

    effective_venue = apply_resolved_style(venue, palette)
    fig, ax = new_figure(effective_venue)

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

    dist_obj, sparams = dist_map[distribution]
    (osm, osr), (slope, intercept, _r) = stats.probplot(
        data,
        dist=dist_obj,
        sparams=sparams,
        plot=None,
    )

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

    示例:
        >>> method_a = np.array([1.1, 2.0, 3.2, 4.1, 5.0])
        >>> method_b = np.array([1.0, 2.1, 3.0, 4.0, 5.2])
        >>> fig, ax = sp.plot_bland_altman(method_a, method_b,
        ...     title="两种方法一致性分析")
    """
    from scipy import stats

    y1 = np.asarray(y1)
    y2 = np.asarray(y2)

    if len(y1) != len(y2):
        raise ValueError(
            f"y1 长度 ({len(y1)}) 与 y2 长度 ({len(y2)}) 不一致"
        )

    mean_vals = (y1 + y2) / 2
    diff_vals = y1 - y2

    mean_diff = np.mean(diff_vals)
    std_diff = np.std(diff_vals, ddof=1)

    upper_loa = mean_diff + 1.96 * std_diff
    lower_loa = mean_diff - 1.96 * std_diff

    effective_venue = apply_resolved_style(venue, palette)
    fig, ax = new_figure(effective_venue)

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

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


__all__ = ["plot_residuals", "plot_qq", "plot_bland_altman"]
