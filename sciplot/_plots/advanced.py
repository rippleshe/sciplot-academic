"""
高级图表 — 误差条、置信区间、热力图
"""

from __future__ import annotations

from typing import Any, List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from sciplot._core.style import setup_style
from sciplot._core.palette import DEFAULT_PALETTE
from sciplot._core.layout import new_figure
from sciplot._core.utils import apply_resolved_style
from sciplot._core.result import PlotResult


def plot_errorbar(
    x: np.ndarray,
    y: np.ndarray,
    yerr: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    label: str = "",
    fmt: str = "o",
    capsize: float = 4,
    markersize: float = 5,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制误差条图（点 + 误差棒）

    参数:
        yerr    : Y 轴误差（标量 / 等长数组 / [下限数组, 上限数组]）
        fmt     : 数据点格式（'o' 圆点 | 's' 方块 | '^' 三角 | '-o' 线+点）
        capsize : 误差棒端帽宽度（points）

    示例:
        >>> fig, ax = sp.plot_errorbar(
        ...     x, y_mean, y_std,
        ...     xlabel="实验轮次", ylabel="损失 ± σ",
        ...     label="模型A", fmt="o-", capsize=4
        ... )
        >>> sp.save(fig, "errorbar")
    """
    effective_venue = apply_resolved_style(venue, palette)
    fig, ax = new_figure(effective_venue)
    ax.errorbar(
        x, y, yerr=yerr, fmt=fmt,
        capsize=capsize, markersize=markersize,
        label=label, **kwargs
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    if label:
        ax.legend()
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_confidence(
    x: np.ndarray,
    y_mean: np.ndarray,
    y_std: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    label_mean: str = "Mean",
    label_std: str = "±1σ",
    n_std: float = 1.0,
    alpha: float = 0.25,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制带置信区间（阴影带）的折线图

    参数:
        y_mean : 均值曲线
        y_std  : 标准差
        n_std  : 阴影带宽度（以标准差为单位），默认 1.0（±1σ）
                 设为 1.96 可画出 95% 置信区间
        alpha  : 阴影透明度，默认 0.25

    示例:
        >>> fig, ax = sp.plot_confidence(
        ...     epochs, train_loss_mean, train_loss_std,
        ...     xlabel="Epoch", ylabel="Loss",
        ...     label_mean="Training", label_std="±1σ"
        ... )

        >>> # 95% 置信区间
        >>> fig, ax = sp.plot_confidence(x, mean, se, n_std=1.96,
        ...     label_std="95% CI")
    """
    effective_venue = apply_resolved_style(venue, palette)
    fig, ax = new_figure(effective_venue)
    (line,) = ax.plot(x, y_mean, label=label_mean, **kwargs)
    color = line.get_color()
    ax.fill_between(
        x,
        y_mean - n_std * y_std,
        y_mean + n_std * y_std,
        alpha=alpha, color=color, label=label_std,
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.legend()
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_heatmap(
    data: np.ndarray,
    row_labels: Optional[List[str]] = None,
    col_labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    cmap: str = "Blues",
    show_values: bool = False,
    fmt: str = ".2f",
    colorbar_label: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制热力图（相关矩阵、混淆矩阵、参数扫描结果等）

    参数:
        data         : 二维数组
        row_labels   : 行标签列表（Y 轴）
        col_labels   : 列标签列表（X 轴）
        cmap         : 颜色映射（"Blues" | "viridis" | "RdBu_r" | "seismic"）
        show_values  : 是否在格子内显示数值
        fmt          : 数值格式，如 ".2f" / ".0f" / "d"
        colorbar_label: 颜色条标签

    示例:
        >>> corr = np.corrcoef(data.T)
        >>> fig, ax = sp.plot_heatmap(
        ...     corr, row_labels=feat_names, col_labels=feat_names,
        ...     cmap="RdBu_r", show_values=True, fmt=".2f",
        ...     title="相关系数矩阵"
        ... )
        >>> sp.save(fig, "correlation")
    """
    data = np.asarray(data)
    if data.ndim != 2:
        raise ValueError(f"data 必须是二维数组，当前维度: {data.ndim}")

    if row_labels is not None and len(row_labels) != data.shape[0]:
        raise ValueError(
            f"row_labels 长度 ({len(row_labels)}) 与行数 ({data.shape[0]}) 不一致"
        )
    if col_labels is not None and len(col_labels) != data.shape[1]:
        raise ValueError(
            f"col_labels 长度 ({len(col_labels)}) 与列数 ({data.shape[1]}) 不一致"
        )

    effective_venue = apply_resolved_style(venue, palette)
    fig, ax = new_figure(effective_venue)

    im = ax.imshow(data, cmap=cmap, aspect="auto", vmin=None, vmax=None, **kwargs)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    if colorbar_label:
        cbar.set_label(colorbar_label)

    # 轴标签
    if col_labels is not None:
        ax.set_xticks(np.arange(len(col_labels)))
        ax.set_xticklabels(col_labels, rotation=45, ha="right")
    if row_labels is not None:
        ax.set_yticks(np.arange(len(row_labels)))
        ax.set_yticklabels(row_labels)

    # 数值标注
    if show_values:
        fontsize = max(6, plt.rcParams.get("font.size", 9) - 1)
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                ax.text(
                    j, i, format(data[i, j], fmt),
                    ha="center", va="center", fontsize=fontsize,
                )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})
