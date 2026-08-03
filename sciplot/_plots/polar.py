"""
极坐标图表 — 雷达图/蜘蛛图

用于多维评估、性能对比等场景。
"""

from __future__ import annotations

from typing import Any, List, Optional

import matplotlib.pyplot as plt
import numpy as np

from sciplot._core.utils import apply_resolved_style, get_cycle_colors
from sciplot._core.result import PlotResult


def plot_radar(
    categories: List[str],
    values_list: List[List[float]],
    labels: Optional[List[str]] = None,
    fill: bool = True,
    alpha: float = 0.3,
    title: str = "",
    show_grid: bool = True,
    show_labels: bool = False,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制雷达图/蜘蛛图（多维评估对比）

    参数:
        categories : 维度标签列表（如 ["准确率", "召回率", "F1", "速度"]）
        values_list: 多组数据列表，每组是一个与 categories 等长的数值列表
        labels     : 各组数据的图例标签
        fill       : 是否填充区域，默认 True
        alpha      : 填充透明度，默认 0.3
        show_grid  : 是否显示网格线
        show_labels: 是否在顶点显示数值标签（仅单组数据时生效）

    示例:
        >>> categories = ["准确率", "召回率", "F1", "速度", "稳定性"]
        >>> values_list = [
        ...     [0.95, 0.88, 0.91, 0.85, 0.92],  # 方法A
        ...     [0.92, 0.91, 0.91, 0.90, 0.88],  # 方法B
        ... ]
        >>> fig, ax = sp.plot_radar(
        ...     categories, values_list,
        ...     labels=["方法A", "方法B"],
        ...     title="性能对比"
        ... )
        >>> sp.save(fig, "radar")
    """
    if not categories:
        raise ValueError("参数 'categories' 不能为空列表")

    # 兼容 ndarray 输入：1D 视为单组，2D 视为多组
    if isinstance(values_list, np.ndarray):
        if values_list.ndim == 1:
            values_list = [values_list.tolist()]
        elif values_list.ndim == 2:
            values_list = values_list.tolist()
        else:
            raise ValueError(
                f"values_list 必须是 1D（单组）或 2D（多组）数据，当前维度: {values_list.ndim}"
            )

    if not values_list:
        raise ValueError("参数 'values_list' 不能为空列表")

    n_cats = len(categories)
    normalized_values: List[List[float]] = []
    for i, values in enumerate(values_list):
        values_arr = np.asarray(values, dtype=float)
        if values_arr.ndim != 1:
            raise ValueError(
                f"values_list[{i}] 必须是一维数据，当前维度: {values_arr.ndim}"
            )
        if len(values_arr) != n_cats:
            raise ValueError(
                f"values_list[{i}] 长度 ({len(values_arr)}) "
                f"与 categories 长度 ({n_cats}) 不一致"
            )
        if not np.all(np.isfinite(values_arr)):
            raise ValueError(f"values_list[{i}] 包含 NaN 或 Inf，无法绘制雷达图")
        normalized_values.append(values_arr.tolist())

    values_list = normalized_values

    if labels is None:
        labels = [f"系列 {i+1}" for i in range(len(values_list))]
    elif len(labels) != len(values_list):
        raise ValueError(
            f"labels 长度 ({len(labels)}) 与 values_list 长度 ({len(values_list)}) 不一致"
        )

    effective_venue = apply_resolved_style(venue, palette, lang)

    # 使用 venue 的尺寸计算雷达图尺寸
    from sciplot._core.style import VENUES
    w, h = VENUES.get(effective_venue or "nature", VENUES["nature"]).figsize
    size = min(w, h) * 1.2  # 雷达图保持方形
    fig = plt.figure(figsize=(size, size))
    ax = fig.add_subplot(111, projection="polar")

    angles = np.linspace(0, 2 * np.pi, n_cats, endpoint=False).tolist()
    angles += angles[:1]

    colors = get_cycle_colors()

    all_values = np.concatenate([np.asarray(values, dtype=float) for values in values_list])
    data_span = float(np.nanmax(all_values) - np.nanmin(all_values)) if all_values.size else 0.0
    offset = data_span * 0.08 if data_span > 0 else 0.08

    for i, (values, label) in enumerate(zip(values_list, labels)):
        values_closed = values + values[:1]
        color = colors[i % len(colors)]

        ax.plot(angles, values_closed, "o-", color=color, label=label, **kwargs)
        if fill:
            ax.fill(angles, values_closed, alpha=alpha, color=color)

        if show_labels and len(values_list) == 1:
            for angle, value in zip(angles[:-1], values):
                ax.annotate(
                    f"{value:.2f}",
                    xy=(angle, value),
                    xytext=(angle, value + offset),
                    ha="center", va="bottom",
                    fontsize=plt.rcParams.get("font.size", 9) - 1,
                )

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)

    if show_grid:
        ax.grid(True, linestyle="--", alpha=0.5)

    ax.set_title(title, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.1))

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_taylor(
    observations: np.ndarray,
    models: Dict[str, np.ndarray],
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    obs_name: str = "观测",
    marker: str = "o",
    show_corr_lines: bool = True,
    show_std_lines: bool = True,
    show_rms_lines: bool = True,
    rms_levels: Optional[List[float]] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制泰勒图（Taylor Diagram，模型/方法综合评估）

    极坐标同时展示三个指标：角度编码与观测的相关系数，半径编码
    标准差比（模型/观测），到观测点的距离编码归一化 RMS 误差。
    气象、水文、遥感等领域模型评估的经典图表。

    参数:
        observations : 观测序列（一维）
        models       : {模型名: 预测序列}，每组与观测等长
        obs_name     : 观测点在图中显示的名称
        marker       : 模型点标记样式
        show_corr_lines: 是否绘制相关系数参考线
        show_std_lines: 是否绘制标准差比参考弧
        show_rms_lines: 是否绘制 RMS 误差参考弧
        rms_levels   : 自定义 RMS 参考层级（默认 [0.5, 1.0, 1.5, 2.0]）

    示例:
        >>> # 三种模型与观测的对比评估
        >>> fig, ax = sp.plot_taylor(
        ...     obs, {"模型A": pred_a, "模型B": pred_b, "模型C": pred_c},
        ...     title="模型评估",
        ... )
        >>> sp.save(fig, "taylor")
    """
    if not models:
        raise ValueError("models 不能为空字典")

    obs = np.asarray(observations, dtype=float).ravel()
    if obs.size < 3:
        raise ValueError("observations 至少需要 3 个数据点")
    if not np.all(np.isfinite(obs)):
        raise ValueError("observations 不能包含 NaN 或 Inf")
    obs_std = float(np.std(obs, ddof=1))
    if obs_std == 0:
        raise ValueError("observations 方差为零，无法计算相关系数与标准差比")

    stats_list: List[Dict[str, float]] = []
    for name, pred in models.items():
        pred_arr = np.asarray(pred, dtype=float).ravel()
        if len(pred_arr) != len(obs):
            raise ValueError(
                f"模型 '{name}' 长度 ({len(pred_arr)}) 与 observations 长度 ({len(obs)}) 不一致"
            )
        if not np.all(np.isfinite(pred_arr)):
            raise ValueError(f"模型 '{name}' 不能包含 NaN 或 Inf")
        pred_std = float(np.std(pred_arr, ddof=1))
        corr = float(np.corrcoef(obs, pred_arr)[0, 1])
        rms = float(np.sqrt(np.mean((pred_arr - obs) ** 2))) / obs_std
        stats_list.append({
            "name": name,
            "corr": float(np.clip(corr, -1.0, 1.0)),
            "std_ratio": pred_std / obs_std,
            "rms": rms,
        })

    effective_venue = apply_resolved_style(venue, palette, lang)
    from sciplot._core.style import VENUES

    venue_cfg = VENUES.get(effective_venue or "nature", VENUES["nature"])
    size = max(venue_cfg.figsize) * 1.3
    fig = plt.figure(figsize=(size, size))
    ax = fig.add_subplot(111, projection="polar")

    colors = get_cycle_colors()
    max_std = max([s["std_ratio"] for s in stats_list] + [1.0])
    plot_radius = min(2.0, max(1.4, max_std * 1.25))

    # ── 参考网格 ──
    if show_corr_lines:
        for corr_val in [0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 0.99]:
            theta_line = np.arccos(corr_val)
            ax.plot([0, theta_line], [0, plot_radius], color="#BBBBBB",
                    linewidth=0.6, linestyle="--", zorder=1)
            ax.text(theta_line, plot_radius * 1.03, f"{corr_val:g}",
                    fontsize=max(6, plt.rcParams.get("font.size", 9) - 3),
                    ha="center", va="bottom", color="#666666")

    if show_std_lines:
        theta_circle = np.linspace(0, np.pi / 2, 120)
        for std_val in [0.5, 1.0, 1.5]:
            if std_val > plot_radius:
                continue
            ax.plot(theta_circle, np.full_like(theta_circle, std_val),
                    color="#BBBBBB", linewidth=0.6, zorder=1)
            ax.text(0.02, std_val, f"{std_val:g}",
                    fontsize=max(6, plt.rcParams.get("font.size", 9) - 3),
                    va="bottom", color="#666666")

    if show_rms_lines:
        levels = rms_levels if rms_levels is not None else [0.5, 1.0, 1.5, 2.0]
        for rms_val in levels:
            # 以观测点 (θ=0, ρ=1) 为圆心、rms 为半径的弧（仅右半平面）
            thetas = np.linspace(0, np.pi / 2, 120)
            rhos = []
            for th in thetas:
                sin2 = np.sin(th) ** 2
                disc = rms_val**2 - sin2
                if disc < 0:
                    break
                rhos.append(np.cos(th) + np.sqrt(disc))
            if len(rhos) >= 2:
                ax.plot(thetas[:len(rhos)], rhos, color="#AAAAAA",
                        linewidth=0.6, linestyle=":", zorder=1)
                ax.text(0.02, rhos[-1], f"{rms_val:g}",
                        fontsize=max(6, plt.rcParams.get("font.size", 9) - 3),
                        va="bottom", color="#777777")

    # ── 观测点 ──
    ax.scatter(0, 1.0, s=90, color="black", marker="*",
               label=obs_name, zorder=5)

    # ── 模型点 ──
    for i, s in enumerate(stats_list):
        theta = np.arccos(s["corr"])
        color = colors[i % len(colors)]
        ax.scatter(theta, s["std_ratio"], s=70, color=color,
                   marker=marker, label=s["name"], zorder=5, **kwargs)
        ax.annotate(
            s["name"], xy=(theta, s["std_ratio"]),
            xytext=(6, 4), textcoords="offset points",
            fontsize=max(6, plt.rcParams.get("font.size", 9) - 2),
            color=color,
        )

    ax.set_rmax(plot_radius)
    ax.set_thetamin(0)
    ax.set_thetamax(90)
    ax.set_rticks([])
    ax.set_xticks([])
    ax.grid(False)
    if title:
        ax.set_title(title, pad=16)
    ax.legend(loc="upper right", bbox_to_anchor=(1.18, 1.08), frameon=False, fontsize=8)

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = ["plot_radar", "plot_taylor"]

