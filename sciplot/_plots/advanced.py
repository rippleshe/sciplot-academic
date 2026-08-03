"""
高级图表 — 误差条、置信区间、热力图
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

import matplotlib.pyplot as plt
import numpy as np

from sciplot._core.layout import new_figure
from sciplot._core.utils import apply_resolved_style, get_cycle_colors
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
    lang: Optional[str] = None,
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
    # 输入验证
    x = np.asarray(x)
    y = np.asarray(y)
    if len(x) != len(y):
        raise ValueError(f"x 长度 ({len(x)}) 与 y 长度 ({len(y)}) 不一致")
    if hasattr(yerr, '__len__') and not isinstance(yerr, (int, float)):
        yerr_arr = np.asarray(yerr)
        if yerr_arr.ndim == 1 and len(yerr_arr) != len(y):
            raise ValueError(f"yerr 长度 ({len(yerr_arr)}) 与 y 长度 ({len(y)}) 不一致")

    effective_venue = apply_resolved_style(venue, palette, lang)
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
    label_std: Optional[str] = None,
    n_std: float = 1.0,
    alpha: float = 0.25,
    fill_kwargs: Optional[Dict[str, Any]] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制带置信区间（阴影带）的折线图

    参数:
        y_mean : 均值曲线
        y_std  : 标准差
        label_std: 阴影带标签，None 时根据 n_std 自动推断
        n_std  : 阴影带宽度（以标准差为单位），默认 1.0（±1σ）
                 设为 1.96 可画出 95% 置信区间
        alpha  : 阴影透明度，默认 0.25
        fill_kwargs: 传递给 ax.fill_between() 的额外参数（如 hatch、edgecolor）
        **kwargs: 传递给 ax.plot() 的额外参数（只影响线条）

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
    # 自动推断 label_std
    if label_std is None:
        if abs(n_std - 1.96) < 0.01:
            label_std = "95% CI"
        elif abs(n_std - 2.576) < 0.01:
            label_std = "99% CI"
        elif abs(n_std - 1.0) < 0.01:
            label_std = "±1σ"
        else:
            label_std = f"±{n_std:.2g}σ"

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)
    (line,) = ax.plot(x, y_mean, label=label_mean, **kwargs)
    color = line.get_color()
    effective_fill_kwargs: Dict[str, Any] = dict(fill_kwargs or {})
    effective_fill_kwargs.setdefault("alpha", alpha)
    effective_fill_kwargs.setdefault("color", color)
    effective_fill_kwargs.setdefault("label", label_std)
    ax.fill_between(
        x,
        y_mean - n_std * y_std,
        y_mean + n_std * y_std,
        **effective_fill_kwargs,
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
    annot_color: Optional[str] = None,
    colorbar_label: str = "",
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    aspect: Union[Literal["auto", "equal"], float, None] = "auto",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
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
        annot_color  : 数值文字颜色；None 时根据格子底色自动选择黑/白以保证对比度
        colorbar_label: 颜色条标签
        vmin         : 颜色映射最小值
        vmax         : 颜色映射最大值
        aspect       : 纵横比（"auto" | "equal"）

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

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

    im = ax.imshow(data, cmap=cmap, aspect=aspect, vmin=vmin, vmax=vmax, **kwargs)
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
        from matplotlib.colors import to_rgb

        fontsize = max(6, plt.rcParams.get("font.size", 9) - 1)
        norm = im.norm
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                cell_value = data[i, j]
                if annot_color is None:
                    # 依据格子实际渲染颜色的亮度自动选择黑/白文字，保证可读性。
                    rgba = im.cmap(norm(cell_value))
                    r, g, b = to_rgb(rgba)
                    luminance = 0.299 * r + 0.587 * g + 0.114 * b
                    text_color = "black" if luminance > 0.55 else "white"
                else:
                    text_color = annot_color
                ax.text(
                    j, i, format(cell_value, fmt),
                    ha="center", va="center", fontsize=fontsize,
                    color=text_color,
                )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_bubble_heatmap(
    data: np.ndarray,
    row_labels: Optional[List[str]] = None,
    col_labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    cmap: str = "viridis",
    background: bool = True,
    bg_alpha: float = 0.35,
    show_values: bool = False,
    fmt: str = ".2f",
    annot_color: Optional[str] = None,
    bubble_scale: float = 0.9,
    min_bubble_size: float = 1.5,
    edgecolor: str = "white",
    linewidth: float = 0.8,
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    colorbar_label: str = "",
    aspect: Union[Literal["auto", "equal"], float, None] = "auto",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制气泡热力图（格子底色 + 气泡大小双重编码数值）

    在传统热力图上叠加气泡：气泡大小与 |值| 成正比（平方根缩放），
    气泡颜色与值的大小（含正负）通过 cmap 映射，形成"大小 + 颜色"
    双重视觉通道，适合同时呈现量级与符号差异的数据。

    参数:
        data         : 二维数组
        row_labels   : 行标签列表（Y 轴）
        col_labels   : 列标签列表（X 轴）
        cmap         : 气泡与背景的颜色映射（"viridis" | "RdBu_r" 等）
        background   : 是否绘制格子底色（半透明），False 则只画气泡
        bg_alpha     : 背景底色透明度，默认 0.35
        show_values  : 是否在气泡内显示数值
        fmt          : 数值格式，如 ".2f" / ".0f"
        annot_color  : 数值文字颜色；None 时依据气泡颜色自动选择黑/白
        bubble_scale : 最大气泡直径占格子短边的比例，默认 0.9
        min_bubble_size: 非零值的最小气泡面积（points²），防止过小不可见
        edgecolor    : 气泡描边颜色，默认 "white"
        linewidth    : 气泡描边宽度，默认 0.8
        vmin / vmax  : 颜色映射范围
        colorbar_label: 颜色条标签
        aspect       : 纵横比（"auto" | "equal"）
        **kwargs     : 传递给 ax.scatter() 的额外参数（气泡）

    示例:
        >>> # 基因表达矩阵：气泡大小=表达量，颜色=表达水平
        >>> expr = np.random.rand(8, 10) * 10
        >>> fig, ax = sp.plot_bubble_heatmap(
        ...     expr,
        ...     row_labels=[f"基因{i}" for i in range(8)],
        ...     col_labels=[f"样本{i}" for i in range(10)],
        ...     cmap="RdBu_r", vmin=0, vmax=10,
        ...     show_values=True, fmt=".0f",
        ...     xlabel="样本", ylabel="基因",
        ... )
        >>> sp.save(fig, "bubble_heatmap")
    """
    from matplotlib.colors import Normalize, to_rgb

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
    if not 0.0 < bubble_scale <= 1.0:
        raise ValueError(
            f"bubble_scale 必须在 (0, 1] 范围内，实际值: {bubble_scale!r}"
        )

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

    finite_data = data[np.isfinite(data)]
    if finite_data.size == 0:
        raise ValueError("data 中不包含可用于绘图的有限数值")

    vmin_eff = float(finite_data.min()) if vmin is None else float(vmin)
    vmax_eff = float(finite_data.max()) if vmax is None else float(vmax)
    if vmin_eff == vmax_eff:
        vmax_eff = vmin_eff + 1.0  # 避免 Normalize 除零
    norm = Normalize(vmin=vmin_eff, vmax=vmax_eff)

    # 背景热力层（可选，半透明）
    im = None
    if background:
        masked = np.ma.masked_invalid(data)
        im = ax.imshow(
            masked, cmap=cmap, aspect=aspect,
            vmin=vmin_eff, vmax=vmax_eff, alpha=bg_alpha,
        )

    # 坐标轴刻度与标签
    if col_labels is not None:
        ax.set_xticks(np.arange(len(col_labels)))
        ax.set_xticklabels(col_labels, rotation=45, ha="right")
    if row_labels is not None:
        ax.set_yticks(np.arange(len(row_labels)))
        ax.set_yticklabels(row_labels)

    # ── 气泡层：大小编码 |值|，颜色编码值 ──
    n_rows, n_cols = data.shape
    js, is_ = np.meshgrid(np.arange(n_cols), np.arange(n_rows))
    flat_v = data.ravel()
    finite_mask = np.isfinite(flat_v)

    x_pts = js.ravel()[finite_mask]
    y_pts = is_.ravel()[finite_mask]
    vals = flat_v[finite_mask]

    max_abs = float(np.max(np.abs(vals))) if vals.size else 1.0
    if max_abs == 0:
        max_abs = 1.0

    # 计算格子显示尺寸（像素）→ 换算 scatter 面积（points²）
    dpi = float(fig.dpi)
    x_px_per_unit = float(np.abs(ax.transData.transform((1, 0))[0] - ax.transData.transform((0, 0))[0]))
    y_px_per_unit = float(np.abs(ax.transData.transform((0, 1))[1] - ax.transData.transform((0, 0))[1]))
    cell_px = min(x_px_per_unit, y_px_per_unit)
    px_per_pt = dpi / 72.0

    # 气泡面积与 |值| 成正比（直径与 sqrt(|值|) 成正比）
    rel = np.sqrt(np.abs(vals) / max_abs)
    radii_px = 0.5 * bubble_scale * cell_px * rel
    sizes_pt2 = (np.pi * radii_px**2) / (px_per_pt**2)
    # 非零值设最小面积防止不可见；零值不绘制气泡
    sizes_pt2 = np.where(vals != 0, np.maximum(sizes_pt2, min_bubble_size), 0.0)

    colors = [im.cmap(norm(v)) for v in vals] if im is not None else \
        [plt.colormaps.get_cmap(cmap)(norm(v)) for v in vals]

    scatter = ax.scatter(
        x_pts, y_pts, s=sizes_pt2, c=colors, alpha=1.0,
        edgecolors=edgecolor, linewidths=linewidth,
        zorder=3, **kwargs,
    )

    # 数值标注（依据气泡颜色自动选择对比色）
    if show_values:
        fontsize = max(6, plt.rcParams.get("font.size", 9) - 1)
        for x_p, y_p, v, rgba in zip(x_pts, y_pts, vals, colors):
            if annot_color is None:
                r, g, b = to_rgb(rgba)
                luminance = 0.299 * r + 0.587 * g + 0.114 * b
                text_color = "black" if luminance > 0.55 else "white"
            else:
                text_color = annot_color
            ax.text(
                x_p, y_p, format(v, fmt),
                ha="center", va="center", fontsize=fontsize,
                color=text_color, zorder=4,
            )

    # 颜色条：优先用背景层，否则用气泡 ScalarMappable
    if im is not None:
        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    else:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
    if colorbar_label:
        cbar.set_label(colorbar_label)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = [
    "plot_errorbar",
    "plot_confidence",
    "plot_heatmap",
    "plot_bubble_heatmap",
    "plot_bubble",
]


def plot_bubble(
    x: np.ndarray,
    y: np.ndarray,
    size: np.ndarray,
    color: Optional[np.ndarray] = None,
    labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    cmap: str = "viridis",
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    size_scale: float = 200.0,
    min_size: float = 2.0,
    alpha: float = 0.7,
    edgecolor: str = "white",
    linewidth: float = 0.8,
    show_values: bool = False,
    fmt: str = ".2f",
    colorbar_label: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制二维气泡图（气泡面积编码第三维数值）

    在散点图基础上用气泡面积编码 size 参数，可用 color 增加第四个
    颜色通道，适合同时展示多个维度的关系。

    参数:
        x, y         : 坐标数组（等长）
        size         : 气泡面积编码值（等长，允许 0/负值按绝对值处理）
        color        : 颜色通道数组（等长，连续数值）；None 则全部同色
        labels       : 分类标签列表（等长，用于图例，需与 x 等长）
        cmap         : 颜色映射（color 不为 None 时生效）
        vmin / vmax  : 颜色映射范围
        size_scale   : 最大气泡面积（points²），默认 200
        min_size     : 非零值的最小气泡面积（points²）
        alpha        : 透明度，默认 0.7
        edgecolor    : 气泡描边颜色，默认 "white"
        linewidth    : 气泡描边宽度，默认 0.8
        show_values  : 是否在气泡内显示数值（size 值）
        fmt          : 数值格式
        colorbar_label: 颜色条标签
        **kwargs     : 传递给 ax.scatter() 的额外参数

    示例:
        >>> # 气泡图：GDP vs 人口，气泡面积=产值
        >>> fig, ax = sp.plot_bubble(
        ...     gdp, population, size=output,
        ...     color=growth_rate,
        ...     xlabel="GDP", ylabel="人口",
        ...     colorbar_label="增长率",
        ... )
        >>> sp.save(fig, "bubble")
    """
    from matplotlib.colors import Normalize, to_rgb

    x_arr = np.asarray(x, dtype=float).ravel()
    y_arr = np.asarray(y, dtype=float).ravel()
    size_arr = np.asarray(size, dtype=float).ravel()

    n_points = len(x_arr)
    if len(y_arr) != n_points:
        raise ValueError(f"x 长度 ({n_points}) 与 y 长度 ({len(y_arr)}) 不一致")
    if len(size_arr) != n_points:
        raise ValueError(
            f"size 长度 ({len(size_arr)}) 与 x 长度 ({n_points}) 不一致"
        )
    if n_points == 0:
        raise ValueError("x/y/size 不能为空")
    if not np.all(np.isfinite(x_arr)) or not np.all(np.isfinite(y_arr)):
        raise ValueError("x 和 y 不能包含 NaN 或 Inf")

    if color is not None:
        color_arr = np.asarray(color).ravel()
        if color_arr.size != n_points:
            raise ValueError(
                f"color 长度 ({color_arr.size}) 与 x 长度 ({n_points}) 不一致"
            )
    else:
        color_arr = None

    if labels is not None:
        if len(labels) != n_points:
            raise ValueError(
                f"labels 长度 ({len(labels)}) 与 x 长度 ({n_points}) 不一致"
            )

    if not isinstance(size_scale, (int, float)) or size_scale <= 0:
        raise ValueError(f"size_scale 必须为正数，实际值: {size_scale!r}")

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

    # 气泡面积 ∝ |size|（线性缩放）
    max_abs = float(np.max(np.abs(size_arr))) if n_points else 1.0
    if max_abs == 0:
        max_abs = 1.0
    sizes = size_scale * np.abs(size_arr) / max_abs
    sizes = np.where(size_arr != 0, np.maximum(sizes, min_size), 0.0)

    if color_arr is not None:
        finite_color = color_arr[np.isfinite(color_arr)]
        if finite_color.size == 0:
            raise ValueError("color 中不包含可用于颜色映射的有限数值")
        vmin_eff = float(finite_color.min()) if vmin is None else float(vmin)
        vmax_eff = float(finite_color.max()) if vmax is None else float(vmax)
        if vmin_eff == vmax_eff:
            vmax_eff = vmin_eff + 1.0
        norm = Normalize(vmin=vmin_eff, vmax=vmax_eff)
        cmap_obj = plt.colormaps.get_cmap(cmap)
        scatter = ax.scatter(
            x_arr, y_arr, s=sizes, c=color_arr, cmap=cmap_obj,
            norm=norm, alpha=alpha, edgecolors=edgecolor,
            linewidths=linewidth, **kwargs,
        )
        cbar = fig.colorbar(scatter, ax=ax, fraction=0.046, pad=0.04)
        if colorbar_label:
            cbar.set_label(colorbar_label)
    else:
        colors = get_cycle_colors()
        scatter = ax.scatter(
            x_arr, y_arr, s=sizes, c=colors[0], alpha=alpha,
            edgecolors=edgecolor, linewidths=linewidth, **kwargs,
        )

    if labels is not None:
        # 分类着色：按标签覆盖颜色，并生成图例
        if color_arr is None:
            unique_labels: List[Any] = []
            seen: set = set()
            for lbl in labels:
                if lbl not in seen:
                    seen.add(lbl)
                    unique_labels.append(lbl)
            from matplotlib.lines import Line2D as _Line2D

            scatter.set_array(None)
            label_colors = {
                lbl: colors[i % len(colors)]
                for i, lbl in enumerate(unique_labels)
            }
            scatter.set_facecolors([label_colors[l] for l in labels])
            handles = [
                _Line2D([0], [0], marker="o", linestyle="",
                        markerfacecolor=label_colors[l], markersize=8, label=str(l))
                for l in unique_labels
            ]
            ax.legend(handles=handles, loc="best")

    if show_values:
        from matplotlib.colors import to_rgb as _to_rgb

        fontsize = max(6, plt.rcParams.get("font.size", 9) - 1)
        for idx, (x_p, y_p, v) in enumerate(zip(x_arr, y_arr, size_arr)):
            if color_arr is not None:
                # 依据数据点实际渲染颜色选择对比色
                rgba = cmap_obj(norm(float(color_arr[idx])))
                r, g, b = _to_rgb(rgba)
                luminance = 0.299 * r + 0.587 * g + 0.114 * b
                text_color = "black" if luminance > 0.55 else "white"
            else:
                text_color = "black"
            ax.text(
                x_p, y_p, format(v, fmt),
                ha="center", va="center", fontsize=fontsize,
                color=text_color, zorder=4,
            )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})
