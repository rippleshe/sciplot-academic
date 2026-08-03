"""
高级图表 — 误差条、置信区间、热力图
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize

from sciplot._core.layout import add_colorbar
from sciplot._core.utils import (
    apply_resolved_style,
    boxplot_with_orientation,
    contrast_text_color,
    get_cmap_safe,
    get_cycle_colors,
    cycle_color,
    polar_to_cart,
    new_styled_figure,
)
from sciplot._core.result import PlotResult


def _resolve_norm(
    vmin: Optional[float],
    vmax: Optional[float],
    data: np.ndarray,
) -> Normalize:
    """解析 vmin/vmax（None 时从数据推断），并避免 vmin==vmax 除零。"""
    finite = data[np.isfinite(data)]
    vmin_eff = float(finite.min()) if vmin is None else float(vmin)
    vmax_eff = float(finite.max()) if vmax is None else float(vmax)
    if vmin_eff == vmax_eff:
        vmax_eff = vmin_eff + 1.0  # 避免 Normalize 除零
    return Normalize(vmin=vmin_eff, vmax=vmax_eff)


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

    fig, ax = new_styled_figure(venue, palette, lang)
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
    # 输入转数组：plot/fill_between 需要 numpy 运算（list 直接相减会崩）
    x = np.asarray(x, dtype=float)
    y_mean = np.asarray(y_mean, dtype=float)
    y_std = np.asarray(y_std, dtype=float)
    if len(x) != len(y_mean) or len(x) != len(y_std):
        raise ValueError(
            f"x/y_mean/y_std 长度必须一致，实际为 "
            f"x={len(x)}, y_mean={len(y_mean)}, y_std={len(y_std)}"
        )
    if np.any(~np.isfinite(y_std)) or np.any(y_std < 0):
        raise ValueError("y_std 必须全部为非负的有限数值")

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

    fig, ax = new_styled_figure(venue, palette, lang)
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
    if label_mean or (label_std is not None and label_std):
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

    fig, ax = new_styled_figure(venue, palette, lang)

    im = ax.imshow(data, cmap=cmap, aspect=aspect, vmin=vmin, vmax=vmax, **kwargs)
    cbar = add_colorbar(fig, im, ax=ax)
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
                    text_color = contrast_text_color(rgba)
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

    fig, ax = new_styled_figure(venue, palette, lang)

    finite_data = data[np.isfinite(data)]
    if finite_data.size == 0:
        raise ValueError("data 中不包含可用于绘图的有限数值")

    norm = _resolve_norm(vmin, vmax, finite_data)

    # 背景热力层（可选，半透明）
    im = None
    if background:
        masked = np.ma.masked_invalid(data)
        im = ax.imshow(
            masked, cmap=cmap, aspect=aspect,
            vmin=norm.vmin, vmax=norm.vmax, alpha=bg_alpha,
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
        [get_cmap_safe(cmap)(norm(v)) for v in vals]

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
                text_color = contrast_text_color(rgba)
            else:
                text_color = annot_color
            ax.text(
                x_p, y_p, format(v, fmt),
                ha="center", va="center", fontsize=fontsize,
                color=text_color, zorder=4,
            )

    # 颜色条：优先用背景层，否则用气泡 ScalarMappable
    if im is not None:
        cbar = add_colorbar(fig, im, ax=ax)
    else:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = add_colorbar(fig, sm, ax=ax)
    if colorbar_label:
        cbar.set_label(colorbar_label)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def _pack_bubbles(
    sizes: np.ndarray,
    max_tries: int = 3000,
    min_size_frac: float = 0.22,
) -> Tuple[np.ndarray, np.ndarray]:
    """贪心圆形打包：按大小降序，沿黄金角螺旋放置并检测碰撞。

    返回 (positions, radii)，位置已归一化到 [-1, 1] 区间。
    min_size_frac 保证最小气泡可见（相对最大气泡的半径下限）。
    """
    n = len(sizes)
    order = np.argsort(sizes)[::-1]
    radii = np.sqrt(sizes / float(np.max(sizes)))
    # 小气泡半径下限：避免跨数量级数据时小类完全不可见
    min_r = float(radii.max()) * min_size_frac
    radii = np.maximum(radii, min_r)

    # 面积和决定整体尺度：让打包区域大致落在单位圆内
    total_area = float(np.sum(np.pi * radii**2))
    scale = 1.0 / max(1.0, np.sqrt(total_area / np.pi))
    radii = radii * scale * 0.9

    pos = np.zeros((n, 2))
    placed: list = []
    golden = np.pi * (3 - np.sqrt(5))

    for idx, i in enumerate(order):
        if idx == 0:
            pos[i] = (0.0, 0.0)
            placed.append(i)
            continue
        angle = golden * idx
        spiral_r = (radii[i] + radii[order[0]]) * 0.4
        best: Optional[Tuple[float, float]] = None
        for _ in range(max_tries):
            cand = (spiral_r * np.cos(angle), spiral_r * np.sin(angle))
            ok = True
            for j in placed:
                dist = np.hypot(cand[0] - pos[j][0], cand[1] - pos[j][1])
                if dist < (radii[i] + radii[j]) * 0.98:
                    ok = False
                    break
            if ok:
                best = cand
                break
            angle += golden * 0.6
            spiral_r *= 1.02
        if best is None:
            # 兜底：放到最远未占用方向（极少触发）
            best = (spiral_r * np.cos(angle), spiral_r * np.sin(angle))
        pos[i] = best
        placed.append(i)

    # 归一化到 [-1, 1]
    max_abs = float(np.max(np.abs(pos))) if n else 1.0
    if max_abs > 0:
        pos = pos / max_abs * 0.95
    return pos, radii


def plot_packed_bubble(
    labels: List[str],
    sizes: np.ndarray,
    colors: Optional[List[str]] = None,
    color_by: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    alpha: float = 0.88,
    show_values: bool = True,
    fmt: str = ".0f",
    min_font: float = 6.0,
    max_font: float = 16.0,
    min_size_frac: float = 0.22,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制打包气泡图（Packed Bubble，圆面积编码数值的紧凑占比展示）

    圆形面积与数值成正比，按大小降序贪心打包（黄金角螺旋 + 碰撞检测），
    气泡带浅阴影与白色描边；文字依据底色亮度自动选黑/白保证对比度。

    参数:
        labels      : 各项标签（等长）
        sizes       : 各项数值（等长，>0）
        colors      : 每项颜色；None 用当前配色循环
        color_by    : 类别标签（等长）；提供时按类别着色并生成图例
        show_values : 是否在气泡内显示数值
        fmt         : 数值格式
        min_font / max_font: 气泡内文字字号随面积缩放的范围
        min_size_frac: 最小气泡半径相对最大气泡的比例（保证小类可见）

    示例:
        >>> fig, ax = sp.plot_packed_bubble(
        ...     ["计算", "存储", "网络", "人力", "运维"],
        ...     np.array([40, 25, 15, 12, 8]),
        ...     color_by=["核心", "核心", "支撑", "支撑", "支撑"],
        ... )
        >>> sp.save(fig, "packed_bubble")
    """
    if not labels:
        raise ValueError("参数 'labels' 不能为空列表")
    sizes_arr = np.asarray(sizes, dtype=float).ravel()
    if len(sizes_arr) != len(labels):
        raise ValueError(
            f"sizes 长度 ({len(sizes_arr)}) 与 labels 长度 ({len(labels)}) 不一致"
        )
    if not np.all(np.isfinite(sizes_arr)):
        raise ValueError("sizes 不能包含 NaN 或 Inf")
    if np.any(sizes_arr <= 0):
        raise ValueError("sizes 必须全部为正数")

    if colors is not None:
        if len(colors) != len(labels):
            raise ValueError(
                f"colors 长度 ({len(colors)}) 与 labels 长度 ({len(labels)}) 不一致"
            )
    else:
        cycle = get_cycle_colors()
        colors = [cycle_color(cycle, i) for i in range(len(labels))]

    categorical_legend = None
    if color_by is not None:
        if len(color_by) != len(labels):
            raise ValueError(
                f"color_by 长度 ({len(color_by)}) 与 labels 长度 ({len(labels)}) 不一致"
            )
        # 类别优先：color_by 覆盖 colors 分配（按输入首次出现顺序）
        unique_groups = list(dict.fromkeys(color_by))
        cycle = get_cycle_colors()
        group_map = {g: cycle_color(cycle, i) for i, g in enumerate(unique_groups)}
        colors = [group_map[g] for g in color_by]
        categorical_legend = group_map
    if not 0 < min_size_frac < 1:
        raise ValueError(f"min_size_frac 必须在 (0, 1) 范围内，实际值: {min_size_frac!r}")

    fig, ax = new_styled_figure(venue, palette, lang)

    pos, radii = _pack_bubbles(sizes_arr, min_size_frac=min_size_frac)
    fontsize = plt.rcParams.get("font.size", 9)

    from matplotlib.colors import to_rgb

    for i, (label, size) in enumerate(zip(labels, sizes_arr)):
        r = radii[i]
        # 浅阴影（右下偏移的暗圆）
        shadow = plt.Circle(
            (pos[i][0] - 0.015, pos[i][1] - 0.015), r,
            facecolor="#000000", alpha=0.10, edgecolor="none", zorder=0,
        )
        ax.add_patch(shadow)
        circle = plt.Circle(
            pos[i], r, facecolor=colors[i], alpha=alpha,
            edgecolor="white", linewidth=1.2, zorder=1, **kwargs,
        )
        ax.add_patch(circle)
        # 文字对比度：依据底色亮度选黑/白（packed 气泡文字面积极小，阈值略高）
        text_color = contrast_text_color(colors[i], threshold=0.62)
        fs = max(min_font, min(max_font, fontsize * (0.7 + 1.3 * (r / max(radii)))))
        ax.text(
            pos[i][0], pos[i][1], label,
            ha="center", va="center", fontsize=fs, color=text_color,
            fontweight="bold", zorder=3,
        )
        if show_values:
            ax.text(
                pos[i][0], pos[i][1] - r * 0.45, f"{size:{fmt}}",
                ha="center", va="center", fontsize=max(5, fs - 2),
                color=text_color, zorder=3,
            )

    if categorical_legend is not None:
        from matplotlib.patches import Patch

        handles = [
            Patch(facecolor=c, label=str(g), alpha=alpha)
            for g, c in categorical_legend.items()
        ]
        ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=8)

    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.25, 1.25)
    ax.set_aspect("equal")
    ax.set_axis_off()
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_chord(
    matrix: np.ndarray,
    labels: Optional[List[str]] = None,
    title: str = "",
    width: float = 0.07,
    gap: float = 0.01,
    alpha: float = 0.5,
    min_flow: float = 0.0,
    color_by: Optional[List[str]] = None,
    show_values: bool = False,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制弦图（Chord Diagram，节点间流量/共现关系）

    节点沿圆周排列，弧长编码节点总流量；节点间弦（渐变宽度多边形）
    宽度编码流量、颜色取自源节点，源端宽而目标端收窄，
    适合展示转移矩阵、共现关系、资源流向。

    参数:
        matrix     : 流量/共现矩阵 (n, n)，要求非负
        labels     : 节点标签（等长）；None 则用序号
        width      : 外圈弧宽（占单位半径比例），默认 0.07
        gap        : 弧段间最小间隙（弧度），默认 0.01
        alpha      : 弦透明度
        min_flow   : 最小流量阈值，低于该值的弦不绘制（过滤噪声）
        color_by   : 节点分类标签（等长）；提供时按类别着色并生成图例
        show_values: 是否在弧外显示各节点总量

    示例:
        >>> # 城市间迁移流量（按区域分组着色）
        >>> fig, ax = sp.plot_chord(
        ...     flow_matrix,
        ...     labels=["北京", "上海", "广州", "深圳", "成都"],
        ...     color_by=["华北", "华东", "华南", "华南", "西南"],
        ...     min_flow=1.0,
        ... )
        >>> sp.save(fig, "chord")
    """
    mat = np.asarray(matrix, dtype=float)
    if mat.ndim != 2 or mat.shape[0] != mat.shape[1]:
        raise ValueError(f"matrix 必须是方阵，当前形状: {mat.shape}")
    n = mat.shape[0]
    if n < 2:
        raise ValueError(f"matrix 至少需要 2 个节点，当前: {n}")
    if not np.all(np.isfinite(mat)):
        raise ValueError("matrix 不能包含 NaN 或 Inf")
    if np.any(mat < 0):
        raise ValueError("matrix 不能包含负值（弦图只支持非负流量）")
    if labels is not None:
        if len(labels) != n:
            raise ValueError(
                f"labels 长度 ({len(labels)}) 与矩阵维度 ({n}) 不一致"
            )
    else:
        labels = [str(i + 1) for i in range(n)]
    if not 0 < width < 1:
        raise ValueError(f"width 必须在 (0, 1) 范围内，实际值: {width!r}")
    if min_flow < 0:
        raise ValueError(f"min_flow 必须为非负数，实际值: {min_flow!r}")
    if color_by is not None:
        if len(color_by) != n:
            raise ValueError(
                f"color_by 长度 ({len(color_by)}) 与矩阵维度 ({n}) 不一致"
            )

    effective_venue = apply_resolved_style(venue, palette, lang)
    from sciplot._core.style import VENUES

    venue_cfg = VENUES.get(effective_venue or "nature", VENUES["nature"])
    size = max(venue_cfg.figsize) * 1.25
    fig, ax = plt.subplots(figsize=(size, size))

    colors = get_cycle_colors()

    # 节点颜色：color_by 分类或默认逐节点
    if color_by is not None:
        unique_groups = sorted(set(color_by), key=str)
        group_map = {g: cycle_color(colors, i) for i, g in enumerate(unique_groups)}
        node_colors = [group_map[g] for g in color_by]
        categorical_legend = group_map
    else:
        node_colors = [cycle_color(colors, i) for i in range(n)]
        categorical_legend = None

    # 节点总流量（行 + 列）
    totals = mat.sum(axis=1) + mat.sum(axis=0)
    total_flow = float(totals.sum())
    if total_flow <= 0:
        raise ValueError("matrix 总流量为零，无法绘制弦图")

    # 弧段角度分配（从 -90° 顺时针）
    arc_starts: List[float] = []
    arc_ends: List[float] = []
    angle = -np.pi / 2
    for i in range(n):
        frac = float(totals[i]) / total_flow
        arc_len = frac * 2 * np.pi
        # 预留 gap
        if i > 0:
            angle += gap
        arc_starts.append(angle)
        arc_ends.append(angle + arc_len)
        angle += arc_len

    # ── 外圈弧段 ──
    for i in range(n):
        start, end = arc_starts[i], arc_ends[i]
        color = node_colors[i]
        seg = np.linspace(start, end, 100)
        r_in = 1.0
        r_out = 1.0 + width
        xs = np.concatenate([r_out * np.cos(seg), r_in * np.cos(seg[::-1])])
        ys = np.concatenate([r_out * np.sin(seg), r_in * np.sin(seg[::-1])])
        ax.fill(xs, ys, color=color, alpha=0.95, edgecolor="none")
        ax.plot(r_out * np.cos(seg), r_out * np.sin(seg),
                color=color, linewidth=1.2)

    # ── 弦（渐变宽度多边形：源端宽编码流量，目标端收窄） ──
    max_flow = float(mat.max()) if mat.size else 1.0
    if max_flow <= 0:
        max_flow = 1.0

    def _bezier_curve(
        p0: Tuple[float, float], p3: Tuple[float, float], n_pts: int = 48
    ) -> Tuple[np.ndarray, np.ndarray]:
        """三次贝塞尔（控制点取半径 0.5 处）。"""
        p1 = (p0[0] * 0.5, p0[1] * 0.5)
        p2 = (p3[0] * 0.5, p3[1] * 0.5)
        t = np.linspace(0, 1, n_pts)
        bx = ((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0]
              + 3 * (1 - t) * t**2 * p2[0] + t**3 * p3[0])
        by = ((1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1]
              + 3 * (1 - t) * t**2 * p2[1] + t**3 * p3[1])
        return bx, by

    for i in range(n):
        row_total = float(mat[i].sum())
        for j in range(n):
            flow = float(mat[i, j])
            if flow <= 0 or i == j or flow < min_flow:
                continue
            # 源端角度：按该流量占 i 行总出量的比例定位在弧段内
            src_frac = flow / row_total if row_total > 0 else 0.5
            src_theta = arc_starts[i] + (arc_ends[i] - arc_starts[i]) * min(0.85, max(0.15, src_frac))
            tgt_theta = arc_starts[j] + (arc_ends[j] - arc_starts[j]) * 0.35
            # 源端宽度 ∝ 流量，目标端固定窄宽（视觉层次）
            half_w = max(0.004, flow / max_flow * 0.03)
            p0a = polar_to_cart(src_theta - half_w, 1.0)
            p0b = polar_to_cart(src_theta + half_w, 1.0)
            p3a = polar_to_cart(tgt_theta - 0.007, 1.0)
            p3b = polar_to_cart(tgt_theta + 0.007, 1.0)
            bx_top, by_top = _bezier_curve(p0a, p3a)
            bx_bot, by_bot = _bezier_curve(p0b, p3b)
            poly_x = np.concatenate([bx_top, bx_bot[::-1]])
            poly_y = np.concatenate([by_top, by_bot[::-1]])
            ax.fill(poly_x, poly_y, color=node_colors[i], alpha=alpha,
                    edgecolor="none", zorder=2)

    # ── 标签与数值 ──
    label_r = 1.0 + width + 0.06
    fontsize = max(7, plt.rcParams.get("font.size", 9) - 1)
    for i in range(n):
        mid = (arc_starts[i] + arc_ends[i]) / 2
        x, y = polar_to_cart(mid, label_r)
        ha = "left" if np.cos(mid) >= 0 else "right"
        va = "bottom" if np.sin(mid) >= 0 else "top"
        ax.text(x, y, labels[i], ha=ha, va=va, fontsize=fontsize,
                color=node_colors[i], fontweight="bold")
        if show_values:
            ax.text(x, y - (0.06 if np.sin(mid) >= 0 else -0.06),
                    f"{totals[i]:.0f}", ha=ha, va=va,
                    fontsize=max(6, fontsize - 2), color="#555555")

    # ── 分类图例 ──
    if categorical_legend is not None:
        from matplotlib.patches import Patch

        handles = [
            Patch(facecolor=c, label=str(g), alpha=0.9)
            for g, c in categorical_legend.items()
        ]
        ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=8)

    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.35)
    ax.set_aspect("equal")
    ax.set_axis_off()
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = [
    "plot_errorbar",
    "plot_confidence",
    "plot_heatmap",
    "plot_bubble_heatmap",
    "plot_bubble",
    "plot_hexbin",
    "plot_marginal",
    "plot_packed_bubble",
    "plot_chord",
]


def plot_marginal(
    x: np.ndarray,
    y: np.ndarray,
    marginal: str = "hist",
    bins: int = 30,
    color: Optional[str] = None,
    alpha: float = 0.6,
    size_ratio: float = 0.22,
    show_corr: bool = False,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制边际分布图（主散点 + 顶部/右侧边缘分布，论文高频组合）

    主区域展示两个变量的散点关系，顶部与右侧分别展示 X/Y 的边缘分布
    （直方图 / 箱线图 / KDE 曲线），可一键叠加相关系数标注。

    参数:
        x, y      : 坐标数组（等长，不含 NaN/Inf）
        marginal  : 边缘分布类型："hist" 直方图 | "box" 箱线图 | "kde" KDE 曲线
        bins      : 直方图柱数（marginal="hist" 时生效），默认 30
        color     : 主色；None 时取当前配色第一色
        alpha     : 散点透明度，默认 0.6
        size_ratio: 边缘图占对应轴的比例，默认 0.22
        show_corr : 是否在主图标注皮尔逊相关系数 r，默认 False
        **kwargs  : 传递给 ax.scatter() 的额外参数

    示例:
        >>> fig, ax = sp.plot_marginal(
        ...     height, weight,
        ...     marginal="hist", bins=40,
        ...     xlabel="身高 (cm)", ylabel="体重 (kg)",
        ...     show_corr=True,
        ... )
        >>> sp.save(fig, "marginal")
    """
    x_arr = np.asarray(x, dtype=float).ravel()
    y_arr = np.asarray(y, dtype=float).ravel()

    n_points = len(x_arr)
    if len(y_arr) != n_points:
        raise ValueError(f"x 长度 ({n_points}) 与 y 长度 ({len(y_arr)}) 不一致")
    if n_points == 0:
        raise ValueError("x/y 不能为空")
    if not np.all(np.isfinite(x_arr)) or not np.all(np.isfinite(y_arr)):
        raise ValueError("x 和 y 不能包含 NaN 或 Inf")

    if marginal not in {"hist", "box", "kde"}:
        raise ValueError(
            f"marginal 仅支持 'hist' / 'box' / 'kde'，实际值: {marginal!r}"
        )
    if not isinstance(bins, int) or bins <= 0:
        raise ValueError(f"bins 必须为正整数，实际值: {bins!r}")
    if not 0.0 < size_ratio < 1.0:
        raise ValueError(f"size_ratio 必须在 (0, 1) 范围内，实际值: {size_ratio!r}")

    kde_module = None
    if marginal == "kde":
        try:
            from scipy import stats as kde_module
        except ImportError as exc:
            raise ImportError(
                "marginal='kde' 需要安装 scipy。请运行: uv pip install scipy"
            ) from exc

    effective_venue = apply_resolved_style(venue, palette, lang)
    from sciplot._core.style import VENUES

    venue_cfg = VENUES.get(effective_venue or "nature", VENUES["nature"])
    fig = plt.figure(figsize=venue_cfg.figsize)

    main_ratio = 1.0 - size_ratio
    gs = fig.add_gridspec(
        2, 2,
        width_ratios=(main_ratio, size_ratio),
        height_ratios=(size_ratio, main_ratio),
        wspace=0.06, hspace=0.06,
    )
    ax_main = fig.add_subplot(gs[1, 0])
    ax_x = fig.add_subplot(gs[0, 0], sharex=ax_main)
    ax_y = fig.add_subplot(gs[1, 1], sharey=ax_main)

    colors = get_cycle_colors()
    main_color = color if color is not None else colors[0]

    ax_main.scatter(x_arr, y_arr, s=20, alpha=alpha, color=main_color, **kwargs)

    # ── X 边缘分布（顶部） ──
    if marginal == "hist":
        ax_x.hist(x_arr, bins=bins, color=main_color, alpha=0.8)
    elif marginal == "box":
        boxplot_with_orientation(
            ax_x, x_arr, orientation="horizontal", patch_artist=True, widths=0.6,
        )
        for patch in ax_x.patches[:1]:
            patch.set_facecolor(main_color)
            patch.set_alpha(0.6)
    else:
        assert kde_module is not None  # marginal="kde" 时已确保导入
        x_kde = kde_module.gaussian_kde(x_arr)
        x_eval = np.linspace(x_arr.min(), x_arr.max(), 200)
        ax_x.plot(x_eval, x_kde(x_eval), color=main_color)
        ax_x.fill_between(x_eval, x_kde(x_eval), color=main_color, alpha=0.3)

    # ── Y 边缘分布（右侧） ──
    if marginal == "hist":
        ax_y.hist(y_arr, bins=bins, orientation="horizontal", color=main_color, alpha=0.8)
    elif marginal == "box":
        boxplot_with_orientation(
            ax_y, y_arr, orientation="vertical", patch_artist=True, widths=0.6,
        )
        for patch in ax_y.patches[:1]:
            patch.set_facecolor(main_color)
            patch.set_alpha(0.6)
    else:
        assert kde_module is not None  # marginal="kde" 时已确保导入
        y_kde = kde_module.gaussian_kde(y_arr)
        y_eval = np.linspace(y_arr.min(), y_arr.max(), 200)
        ax_y.plot(y_kde(y_eval), y_eval, color=main_color)
        ax_y.fill_betweenx(y_eval, y_kde(y_eval), color=main_color, alpha=0.3)

    # 边缘轴清理
    ax_x.tick_params(labelbottom=False)
    ax_y.tick_params(labelleft=False)
    for m_ax in (ax_x, ax_y):
        m_ax.tick_params(direction="in")
        m_ax.grid(False)

    if show_corr:
        r_value = float(np.corrcoef(x_arr, y_arr)[0, 1])
        ax_main.text(
            0.05, 0.95, f"r = {r_value:.3f}",
            transform=ax_main.transAxes, ha="left", va="top",
            fontsize=plt.rcParams.get("font.size", 9) + 1,
        )

    ax_main.set_xlabel(xlabel)
    ax_main.set_ylabel(ylabel)
    if title:
        ax_main.set_title(title)
    ax_main.tick_params(direction="in")
    return PlotResult(fig, ax_main, metadata={"venue": venue, "palette": palette})


def plot_hexbin(
    x: np.ndarray,
    y: np.ndarray,
    gridsize: int = 30,
    bins: Optional[Union[str, int]] = None,
    cmap: str = "viridis",
    mincnt: int = 1,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    colorbar_label: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制六边形密度图（Hexbin，大样本散点密度可视化）

    将二维平面划分为六边形网格，以颜色深浅编码落入每个格子的
    样本数量，避免大样本散点图过度绘制的问题。

    参数:
        x, y          : 坐标数组（等长，不含 NaN/Inf）
        gridsize      : 网格规模（单方向格数），默认 30
        bins          : 计数变换：None 原始计数 | "log" 对数 | 整数分段
        cmap          : 颜色映射，默认 "viridis"
        mincnt        : 最少计数阈值，低于该值的格子不绘制
        colorbar_label: 颜色条标签
        **kwargs      : 传递给 ax.hexbin() 的额外参数

    示例:
        >>> # 十万个样本的二维密度
        >>> x = np.random.randn(100000)
        >>> y = np.random.randn(100000) * 0.8 + x * 0.5
        >>> fig, ax = sp.plot_hexbin(
        ...     x, y, gridsize=40, bins="log",
        ...     xlabel="X", ylabel="Y",
        ...     colorbar_label="样本数 (log)",
        ... )
        >>> sp.save(fig, "hexbin")
    """
    x_arr = np.asarray(x, dtype=float).ravel()
    y_arr = np.asarray(y, dtype=float).ravel()

    n_points = len(x_arr)
    if len(y_arr) != n_points:
        raise ValueError(f"x 长度 ({n_points}) 与 y 长度 ({len(y_arr)}) 不一致")
    if n_points == 0:
        raise ValueError("x/y 不能为空")
    if not np.all(np.isfinite(x_arr)) or not np.all(np.isfinite(y_arr)):
        raise ValueError("x 和 y 不能包含 NaN 或 Inf")
    if not isinstance(gridsize, int) or gridsize <= 0:
        raise ValueError(f"gridsize 必须为正整数，实际值: {gridsize!r}")
    if not isinstance(mincnt, int) or mincnt < 0:
        raise ValueError(f"mincnt 必须为非负整数，实际值: {mincnt!r}")

    fig, ax = new_styled_figure(venue, palette, lang)

    hb = ax.hexbin(
        x_arr, y_arr, gridsize=gridsize, bins=bins, cmap=cmap,
        mincnt=mincnt, **kwargs,
    )
    cbar = add_colorbar(fig, hb, ax=ax)
    if colorbar_label:
        cbar.set_label(colorbar_label)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


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
        labels       : 分类标签列表（等长，用于图例；仅当 color 为 None 时生效）
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

    fig, ax = new_styled_figure(venue, palette, lang)

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
        norm = _resolve_norm(vmin, vmax, finite_color)
        cmap_obj = get_cmap_safe(cmap)
        scatter = ax.scatter(
            x_arr, y_arr, s=sizes, c=color_arr, cmap=cmap_obj,
            norm=norm, alpha=alpha, edgecolors=edgecolor,
            linewidths=linewidth, **kwargs,
        )
        cbar = add_colorbar(fig, scatter, ax=ax)
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
                lbl: cycle_color(colors, i)
                for i, lbl in enumerate(unique_labels)
            }
            # set_facecolors 仅存在于 PathCollection 子类，scatter 返回类型按基类标注
            scatter.set_facecolors([label_colors[l] for l in labels])  # type: ignore[attr-defined]
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
                text_color = contrast_text_color(rgba)
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

# ============================================================================
# 桑基图（Sankey，Flow 家族）
# ============================================================================

def plot_sankey(
    sources: Sequence[Any],
    targets: Sequence[Any],
    values: Sequence[float],
    labels: Optional[Sequence[str]] = None,
    node_colors: Optional[Sequence[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    node_width: float = 0.1,
    node_alpha: float = 0.9,
    flow_alpha: float = 0.55,
    min_flow: float = 0.0,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制桑基图（Sankey Diagram，能量/物质/流量流向）。

    纯 matplotlib 实现，无额外依赖。节点按最长路径分层，
    节点高度与流量带宽度均正比于流量值。

    参数:
        sources    : 每条流的源节点（名称或任意可哈希值）
        targets    : 每条流的目标节点
        values     : 每条流的流量（非负）
        labels     : 节点显示名（与节点集合等长或为 dict）；默认用节点本身
        node_colors: 节点颜色列表（按节点出现顺序）；默认取当前配色循环
        node_width : 节点矩形宽度（归一化坐标）
        node_alpha : 节点不透明度
        flow_alpha : 流量带不透明度
        min_flow   : 小于该值的流被过滤（避免视觉噪音）

    示例:
        >>> fig, ax = sp.plot_sankey(
        ...     ["A", "A", "B"], ["B", "C", "C"], [40, 30, 20],
        ...     labels=["能源", "转化", "终端"],
        ... )
    """
    from matplotlib.patches import PathPatch, Rectangle
    from matplotlib.path import Path

    src_arr = list(sources)
    tgt_arr = list(targets)
    val_arr = np.asarray(values, dtype=float)
    if len(src_arr) != len(tgt_arr) or len(src_arr) != len(val_arr):
        raise ValueError(
            f"sources/targets/values 长度必须一致: "
            f"{len(src_arr)}/{len(tgt_arr)}/{len(val_arr)}"
        )
    if val_arr.size == 0:
        raise ValueError("sources/targets/values 不能为空")
    if not np.all(np.isfinite(val_arr)):
        raise ValueError("values 不能包含 NaN 或 Inf")
    if np.any(val_arr < 0):
        raise ValueError("values 不能包含负值（流量必须非负）")
    if not (0.0 < node_width < 1.0):
        raise ValueError(f"node_width 必须在 (0, 1) 范围内，实际值: {node_width!r}")
    if min_flow < 0:
        raise ValueError(f"min_flow 必须非负，实际值: {min_flow!r}")

    # 过滤小流量
    keep = val_arr >= min_flow
    if not np.any(keep):
        raise ValueError("过滤 min_flow 后没有剩余流量，请调低 min_flow")
    src_arr = [s for s, k in zip(src_arr, keep) if k]
    tgt_arr = [t for t, k in zip(tgt_arr, keep) if k]
    val_arr = val_arr[keep]

    # 节点集合（按出现顺序）
    node_list: List[Any] = []
    for s, t in zip(src_arr, tgt_arr):
        if s not in node_list:
            node_list.append(s)
        if t not in node_list:
            node_list.append(t)
    n_nodes = len(node_list)
    node_index = {n: i for i, n in enumerate(node_list)}

    if labels is not None:
        if isinstance(labels, dict):
            label_of = {n: str(labels[n]) for n in node_list}
        elif len(labels) != n_nodes:
            raise ValueError(
                f"labels 长度 ({len(labels)}) 与节点数 ({n_nodes}) 不一致"
            )
        else:
            label_of = {n: str(labels[i]) for i, n in enumerate(node_list)}
    else:
        label_of = {n: str(n) for n in node_list}

    if node_colors is not None:
        if len(node_colors) < n_nodes:
            raise ValueError(
                f"node_colors 长度 ({len(node_colors)}) 小于节点数 ({n_nodes})"
            )
        color_of = {n: node_colors[i] for i, n in enumerate(node_list)}
    else:
        cycle = get_cycle_colors()
        color_of = {n: cycle_color(cycle, i) for i, n in enumerate(node_list)}

    # 层级分配：最长路径（源 → 目标）
    preds: Dict[Any, List[Any]] = {n: [] for n in node_list}
    for s, t in zip(src_arr, tgt_arr):
        if t not in preds[s]:
            preds[s].append(t)
    level: Dict[Any, int] = {n: 0 for n in node_list}
    changed = True
    while changed:
        changed = False
        for s, t in zip(src_arr, tgt_arr):
            if level[t] <= level[s]:
                level[t] = level[s] + 1
                changed = True
    max_level = max(level.values())

    # 节点流量（流入/流出取大者作为高度基准）
    inflow: Dict[Any, float] = {n: 0.0 for n in node_list}
    outflow: Dict[Any, float] = {n: 0.0 for n in node_list}
    for s, t, v in zip(src_arr, tgt_arr, val_arr):
        outflow[s] += float(v)
        inflow[t] += float(v)
    node_value = {n: max(inflow[n], outflow[n]) for n in node_list}

    # 逐层布局：层内按流量降序，节点高度 ∝ 流量
    total_value = float(max(sum(outflow.values()), sum(inflow.values()), 1e-9))
    layers: Dict[int, List[Any]] = {}
    for n in node_list:
        layers.setdefault(level[n], []).append(n)
    for lv in layers:
        layers[lv].sort(key=lambda n: -node_value[n])

    max_layer_h = 0.0
    layer_heights: Dict[int, float] = {}
    for lv, nodes in layers.items():
        h = sum(node_value[n] for n in nodes) / total_value
        layer_heights[lv] = h
        max_layer_h = max(max_layer_h, h)

    x_stride = node_width * 2.5
    node_pos: Dict[Any, Tuple[float, float]] = {}
    for lv, nodes in layers.items():
        x = lv * x_stride
        y_cursor = (max_layer_h - layer_heights[lv]) / 2
        for n in nodes:
            h = node_value[n] / total_value
            node_pos[n] = (x, y_cursor)
            y_cursor += h + 0.02

    # 流出/流入偏移游标（用于流量带锚点）
    out_cursor: Dict[Any, float] = {n: 0.0 for n in node_list}
    in_cursor: Dict[Any, float] = {n: 0.0 for n in node_list}

    fig, ax = new_styled_figure(venue, palette, lang)

    # ── 流量带（先画，zorder 低于节点） ──
    for s, t, v in zip(src_arr, tgt_arr, val_arr):
        x_s, y_s = node_pos[s]
        x_t, y_t = node_pos[t]
        h_s = node_value[s] / total_value
        h_t = node_value[t] / total_value
        y_s0 = y_s + h_s - (out_cursor[s] + v / total_value)
        y_t0 = y_t + h_t - (in_cursor[t] + v / total_value)
        out_cursor[s] += v / total_value
        in_cursor[t] += v / total_value
        w = v / total_value
        # 垂直居中于带，半带宽
        b_s = w / 2
        b_t = w / 2
        xm = (x_s + node_width + x_t) / 2
        verts = [
            (x_s + node_width, y_s0 + b_s),
            (xm, y_s0 + b_s),
            (xm, y_t0 + b_t),
            (x_t, y_t0 + b_t),
            (x_t, y_t0 - b_t),
            (xm, y_t0 - b_t),
            (xm, y_s0 - b_s),
            (x_s + node_width, y_s0 - b_s),
        ]
        codes = [
            Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
            Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
        ]
        ax.add_patch(PathPatch(
            Path(verts, codes),
            facecolor=color_of[s], alpha=flow_alpha,
            edgecolor="none", zorder=1,
        ))

    # ── 节点矩形 ──
    for n in node_list:
        x, y = node_pos[n]
        h = node_value[n] / total_value
        ax.add_patch(Rectangle(
            (x, y), node_width, h,
            facecolor=color_of[n], alpha=node_alpha,
            edgecolor="white", linewidth=0.8, zorder=3,
        ))

    # ── 节点标签（末层在左，其余在右） ──
    fs = max(7, plt.rcParams.get("font.size", 9) - 1)
    for n in node_list:
        x, y = node_pos[n]
        h = node_value[n] / total_value
        if level[n] == max_level:
            ax.text(x - 0.005, y + h / 2, label_of[n],
                    ha="right", va="center", fontsize=fs, zorder=4)
        else:
            ax.text(x + node_width + 0.005, y + h / 2, label_of[n],
                    ha="left", va="center", fontsize=fs, zorder=4)

    ax.set_xlim(-0.3, max_level * x_stride + node_width + 0.3)
    ax.set_ylim(-0.05, max_layer_h + 0.08)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})

# ============================================================================
# 矩形树图（Treemap，Part-of-a-whole 家族）
# ============================================================================

def _treemap_layout(
    sizes: List[float],
    x: float,
    y: float,
    w: float,
    h: float,
) -> List[Tuple[float, float, float, float]]:
    """Bruls 等 (2000) squarify 算法：返回与 sizes 同序的 (x, y, w, h) 列表。"""
    if not sizes:
        return []
    total = sum(sizes)
    if total <= 0:
        raise ValueError("sizes 之和必须大于 0")
    scaled = [s / total * (w * h) for s in sizes]
    rects: List[Tuple[float, float, float, float]] = []

    def _worst_ratio(row: List[float], length: float) -> float:
        s = sum(row)
        if s <= 0:
            return float("inf")
        s2 = sum(v * v for v in row)
        return max(length * length * s2 / (s * s * s),
                   (s * s * s) / (length * length * s2))

    def _layout(items: List[float], cx: float, cy: float, cw: float, ch: float) -> None:
        if not items:
            return
        if len(items) == 1:
            rects.append((cx, cy, cw, ch))
            return
        if cw >= ch:
            # 水平行放置
            row = [items[0]]
            i = 1
            while i < len(items):
                if _worst_ratio(row + [items[i]], cw) <= _worst_ratio(row, cw):
                    row.append(items[i])
                    i += 1
                else:
                    break
            row_h = sum(row) / cw
            rx = cx
            for v in row:
                rects.append((rx, cy, v / row_h, row_h))
                rx += v / row_h
            _layout(items[i:], cx, cy + row_h, cw, ch - row_h)
        else:
            # 垂直列放置
            col = [items[0]]
            i = 1
            while i < len(items):
                if _worst_ratio(col + [items[i]], ch) <= _worst_ratio(col, ch):
                    col.append(items[i])
                    i += 1
                else:
                    break
            col_w = sum(col) / ch
            cy2 = cy
            for v in col:
                rects.append((cx, cy2, col_w, v / col_w))
                cy2 += v / col_w
            _layout(items[i:], cx + col_w, cy, cw - col_w, ch)

    _layout(scaled, x, y, w, h)
    return rects


def plot_treemap(
    categories: List[str],
    values: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    colors: Optional[Sequence[str]] = None,
    show_values: bool = True,
    fmt: str = ".0f",
    min_font: float = 6.0,
    max_font: float = 16.0,
    border_color: str = "white",
    border_width: float = 1.2,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制矩形树图（Treemap，面积编码占比）。

    纯 matplotlib 实现 squarify 算法，无额外依赖。矩形面积正比于数值，
    颜色默认取当前配色循环，文字字号随面积自适应。

    参数:
        categories : 类别名列表
        values     : 数值（非负，和必须大于 0）
        colors     : 颜色列表（与类别等长）；默认取当前配色循环
        show_values: 是否在矩形内显示数值
        fmt        : 数值格式
        min_font/max_font: 文字字号下限/上限（面积过小的矩形不显示文字）

    示例:
        >>> fig, ax = sp.plot_treemap(
        ...     ["A", "B", "C", "D"], [40, 30, 20, 10],
        ... )
    """
    from matplotlib.patches import Rectangle

    cat_arr = list(categories)
    val_arr = np.asarray(values, dtype=float).ravel()
    if len(cat_arr) != len(val_arr):
        raise ValueError(
            f"categories 长度 ({len(cat_arr)}) 与 values 长度 ({len(val_arr)}) 不一致"
        )
    if len(cat_arr) == 0:
        raise ValueError("categories/values 不能为空")
    if not np.all(np.isfinite(val_arr)):
        raise ValueError("values 不能包含 NaN 或 Inf")
    if np.any(val_arr < 0):
        raise ValueError("values 不能包含负值")
    if float(val_arr.sum()) <= 0:
        raise ValueError("values 之和必须大于 0")

    if colors is not None:
        if len(colors) != len(cat_arr):
            raise ValueError(
                f"colors 长度 ({len(colors)}) 与 categories 长度 ({len(cat_arr)}) 不一致"
            )
        color_list = list(colors)
    else:
        cycle = get_cycle_colors()
        color_list = [cycle_color(cycle, i) for i in range(len(cat_arr))]

    rects = _treemap_layout(list(val_arr), 0.0, 0.0, 1.0, 1.0)

    fig, ax = new_styled_figure(venue, palette, lang)

    # ── 矩形 ──
    for (rx, ry, rw, rh), c, v, cat in zip(rects, color_list, val_arr, cat_arr):
        ax.add_patch(Rectangle(
            (rx, ry), rw, rh,
            facecolor=c, edgecolor=border_color,
            linewidth=border_width, zorder=1,
        ))
        # 文字：面积过小或过扁则不显示
        if show_values and rw > 0.06 and rh > 0.03:
            area_frac = rw * rh
            fs = max(min_font, min(max_font, 14 * (0.5 + 1.6 * np.sqrt(area_frac))))
            label_txt = f"{cat}"
            if len(label_txt) * fs * 0.013 < rw and fs >= min_font:
                ax.text(rx + rw / 2, ry + rh / 2 + 0.018, label_txt,
                        ha="center", va="center", fontsize=fs,
                        color="white", fontweight="bold", zorder=3)
            if len(f"{v:{fmt}}") * fs * 0.013 < rw:
                ax.text(rx + rw / 2, ry + rh / 2 - 0.022, f"{v:{fmt}}",
                        ha="center", va="center", fontsize=fs - 2,
                        color="white", alpha=0.9, zorder=3)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})

# ============================================================================
# 环形图（Donut，Part-of-a-whole 家族）
# ============================================================================

def plot_donut(
    categories: List[str],
    values: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    colors: Optional[Sequence[str]] = None,
    hole_ratio: float = 0.6,
    show_values: bool = True,
    fmt: str = ".1f",
    show_percent: bool = True,
    percent_fmt: str = ".1f",
    start_angle: float = 90.0,
    label_radius: float = 1.15,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制环形图（Donut Chart，占比构成）。

    饼图的变体：中心挖空形成环形，常被 Nature 风格图表用于
    “整体构成 + 高亮关键份额”。纯 matplotlib 实现。

    参数:
        categories   : 类别名列表
        values       : 数值（非负，和必须大于 0）
        colors       : 颜色列表（与类别等长）；默认取当前配色循环
        hole_ratio   : 中心空洞占比（0~1），越大环越细
        show_values  : 是否在环内显示数值
        show_percent : 是否在类别标签后附百分比
        start_angle  : 起始角度（度，默认 90 从正上方开始）
        label_radius : 类别标签的半径位置

    示例:
        >>> fig, ax = sp.plot_donut(
        ...     ["A", "B", "C"], [55, 30, 15],
        ... )
    """
    cat_arr = list(categories)
    val_arr = np.asarray(values, dtype=float).ravel()
    if len(cat_arr) != len(val_arr):
        raise ValueError(
            f"categories 长度 ({len(cat_arr)}) 与 values 长度 ({len(val_arr)}) 不一致"
        )
    if len(cat_arr) == 0:
        raise ValueError("categories/values 不能为空")
    if not np.all(np.isfinite(val_arr)):
        raise ValueError("values 不能包含 NaN 或 Inf")
    if np.any(val_arr < 0):
        raise ValueError("values 不能包含负值")
    if float(val_arr.sum()) <= 0:
        raise ValueError("values 之和必须大于 0")
    if not (0.0 < hole_ratio < 1.0):
        raise ValueError(f"hole_ratio 必须在 (0, 1) 范围内，实际值: {hole_ratio!r}")

    if colors is not None:
        if len(colors) != len(cat_arr):
            raise ValueError(
                f"colors 长度 ({len(colors)}) 与 categories 长度 ({len(cat_arr)}) 不一致"
            )
        color_list = list(colors)
    else:
        cycle = get_cycle_colors()
        color_list = [cycle_color(cycle, i) for i in range(len(cat_arr))]

    fig, ax = new_styled_figure(venue, palette, lang)

    total = float(val_arr.sum())
    autopct = None
    pct_txt = None
    if show_percent:
        def pct_txt(pct: float) -> str:
            return f"{pct:{percent_fmt}}%"

    wedges, *_ = ax.pie(
        val_arr,
        colors=color_list,
        startangle=start_angle,
        wedgeprops=dict(width=1.0 - hole_ratio, edgecolor="white", linewidth=1.5),
        autopct=pct_txt,
        pctdistance=1.0 - hole_ratio / 2,
        labels=None,
        **kwargs,
    )
    for w in wedges:
        w.set_zorder(2)

    # 数值放环内中部
    if show_values:
        fs = max(7, plt.rcParams.get("font.size", 9) - 1)
        for w, v in zip(wedges, val_arr):
            ang = np.deg2rad((w.theta1 + w.theta2) / 2)
            r = 1.0 - hole_ratio / 2
            ax.text(r * np.cos(ang), r * np.sin(ang), f"{v:{fmt}}",
                    ha="center", va="center", fontsize=fs,
                    color="white", fontweight="bold", zorder=5)

    # 类别标签放外圈
    fs_label = max(7, plt.rcParams.get("font.size", 9) - 1)
    for w, cat in zip(wedges, cat_arr):
        ang = np.deg2rad((w.theta1 + w.theta2) / 2)
        x = label_radius * np.cos(ang)
        y = label_radius * np.sin(ang)
        ha = "left" if x >= 0 else "right"
        va = "bottom" if y >= 0 else "top"
        ax.text(x, y, cat, ha=ha, va=va, fontsize=fs_label, zorder=5)

    ax.set_aspect("equal")
    ax.set_xlim(-label_radius * 1.15, label_radius * 1.15)
    ax.set_ylim(-label_radius * 1.15, label_radius * 1.15)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})
