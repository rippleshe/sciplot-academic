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
from sciplot.utils.smart import auto_rotate_labels


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
        `**kwargs`: 传递给 ax.plot() 的额外参数（只影响线条）

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
        ax.set_xticklabels(col_labels)
        auto_rotate_labels(ax, axis="x")
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
                if not np.isfinite(cell_value):
                    continue  # NaN 掩膜格（如上三角）不写文字
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
        ax.set_xticklabels(col_labels)
        auto_rotate_labels(ax, axis="x")
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

    # 先应用当前调用的 venue/palette，再读取颜色循环。这样单次函数调用的
    # palette 参数始终是自包含的，不依赖上一张图留下的 rcParams 状态。
    fig, ax = new_styled_figure(venue, palette, lang)

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
    if not np.isfinite(min_font) or min_font <= 0:
        raise ValueError(f"min_font 必须为正有限数，实际值: {min_font!r}")
    if not np.isfinite(max_font) or max_font < min_font:
        raise ValueError(
            f"max_font 必须为有限数且不小于 min_font，实际值: {max_font!r}"
        )

    pos, radii = _pack_bubbles(sizes_arr, min_size_frac=min_size_frac)
    fontsize = float(plt.rcParams.get("font.size", 9))
    max_radius = float(max(radii))
    _, fig_h = fig.get_size_inches()
    axes_box = ax.get_position()
    y_span = 2.5

    # 文本 fit 依赖最终 data→display transform，必须在 renderer 测量之前锁定轴范围。
    # 旧顺序在默认 [0, 1] 坐标上测字，随后再切到 [-1.25, 1.25]，会让“像素级适配”
    # 失去意义并重新产生跨气泡文字碰撞。
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.25, 1.25)
    ax.set_aspect("equal")

    from matplotlib.colors import to_rgb

    for i, (label, size) in enumerate(zip(labels, sizes_arr)):
        r = radii[i]
        # 浅阴影（右下偏移的暗圆）
        shadow = plt.Circle(
            (pos[i][0] - 0.015, pos[i][1] - 0.015), r,
            facecolor="#000000", alpha=0.10, edgecolor="none", zorder=0,
        )
        ax.add_patch(shadow)
        circle_kwargs = {
            "facecolor": colors[i],
            "alpha": alpha,
            "edgecolor": "white",
            "linewidth": 1.2,
            "zorder": 1,
        }
        circle_kwargs.update(kwargs)
        circle = plt.Circle(pos[i], r, **circle_kwargs)
        ax.add_patch(circle)
        # 文字对比度：依据底色亮度选黑/白（packed 气泡文字面积极小，阈值略高）。
        # 字号同时受半径和真实可用直径约束；旧实现只看半径，长标签会跨出圆并
        # 与相邻气泡文字碰撞。
        text_color = contrast_text_color(colors[i], threshold=0.62)
        radial_fs = fontsize * (0.7 + 1.3 * (r / max_radius))
        height_pt = 2.0 * r / y_span * axes_box.height * fig_h * 72.0
        height_cap = height_pt * (0.34 if show_values else 0.52)
        fs = min(max_font, radial_fs, height_cap)

        # min_font 是“可读下限”，不是强制把文字塞进过小气泡的理由。
        # 若标签在下限字号仍无法容纳，宁可省略标签，保留数值和图例/外部说明。
        # 文字宽度不能只靠字符数估计：中文、英文、字体 fallback 的真实宽度差异很大，
        # 因此先创建文字，再用 renderer 的像素 bbox 反算一次字号，使其真正落在圆内。
        if fs >= min_font:
            label_y = pos[i][1] + (r * 0.13 if show_values else 0.0)
            label_artist = ax.text(
                pos[i][0], label_y, label,
                ha="center", va="center", fontsize=fs, color=text_color,
                fontweight="bold", zorder=3,
            )
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
            text_box = label_artist.get_window_extent(renderer=renderer)
            circle_box = circle.get_window_extent(renderer=renderer)
            # 标签略上移时圆的可用弦长小于直径，留 20% 安全边界能避免相邻
            # 相切气泡之间的文字在视觉上“串台”。
            width_ratio = (circle_box.width * 0.78) / max(text_box.width, 1.0)
            height_ratio = (circle_box.height * (0.34 if show_values else 0.52)) / max(
                text_box.height, 1.0
            )
            fit_ratio = min(1.0, width_ratio, height_ratio)
            if fit_ratio < 1.0:
                fitted_fs = fs * fit_ratio * 0.96
                if fitted_fs < min_font:
                    label_artist.remove()
                else:
                    label_artist.set_fontsize(fitted_fs)
        if show_values:
            value_fs = min(max(5.0, min_font - 1.0), max(5.0, fs - 1.5))
            ax.text(
                pos[i][0], pos[i][1] - r * 0.34, f"{size:{fmt}}",
                ha="center", va="center", fontsize=value_fs,
                color=text_color, zorder=3,
            )

    if categorical_legend is not None:
        from matplotlib.patches import Patch

        handles = [
            Patch(facecolor=c, label=str(g), alpha=alpha)
            for g, c in categorical_legend.items()
        ]
        ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=8)

    ax.set_axis_off()
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def _compute_chord_geometry(
    matrix: np.ndarray,
    min_flow: float,
    gap: float,
) -> Tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    Dict[Tuple[int, int], Tuple[float, float]],
    Dict[Tuple[int, int], Tuple[float, float]],
]:
    """计算守恒的 Chord 弧段与有向流槽位。"""
    visible = np.asarray(matrix, dtype=float).copy()
    np.fill_diagonal(visible, 0.0)
    visible[visible < min_flow] = 0.0

    n = visible.shape[0]
    total_gap = gap * n
    if total_gap >= 2 * np.pi:
        raise ValueError(
            "gap 过大：所有节点间隙之和必须小于 2π，"
            f"当前 n*gap={total_gap:.3f}"
        )

    out_totals = visible.sum(axis=1)
    in_totals = visible.sum(axis=0)
    totals = out_totals + in_totals
    total_flow = float(totals.sum())
    if total_flow <= 0:
        raise ValueError("matrix 总流量为零或 min_flow 过滤后无可见流量，无法绘制弦图")

    available_angle = 2 * np.pi - total_gap
    arc_lengths = totals / total_flow * available_angle
    arc_starts = np.empty(n, dtype=float)
    arc_ends = np.empty(n, dtype=float)
    angle = -np.pi / 2
    for i in range(n):
        arc_starts[i] = angle
        arc_ends[i] = angle + float(arc_lengths[i])
        angle = arc_ends[i] + gap

    # 每个节点的弧段按“出流槽在前、入流槽在后”完整切分。
    # 同一条有向流在源端和目标端都占与 flow 成比例的真实角宽。
    scales = np.divide(
        arc_lengths,
        totals,
        out=np.zeros_like(arc_lengths),
        where=totals > 0,
    )
    source_slots: Dict[Tuple[int, int], Tuple[float, float]] = {}
    target_slots: Dict[Tuple[int, int], Tuple[float, float]] = {}

    source_cursor = arc_starts.copy()
    for i in range(n):
        for j in range(n):
            flow = float(visible[i, j])
            if flow <= 0:
                continue
            start = float(source_cursor[i])
            end = start + flow * float(scales[i])
            source_slots[(i, j)] = (start, end)
            source_cursor[i] = end

    target_cursor = arc_starts + out_totals * scales
    for j in range(n):
        for i in range(n):
            flow = float(visible[i, j])
            if flow <= 0:
                continue
            start = float(target_cursor[j])
            end = start + flow * float(scales[j])
            target_slots[(i, j)] = (start, end)
            target_cursor[j] = end

    return visible, totals, arc_starts, arc_ends, source_slots, target_slots


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

    节点沿圆周排列，弧长编码过滤后的可见总流量；节点间弦在源端与目标端
    都按真实流量占用对应弧段槽位，颜色取自源节点。适合展示转移矩阵、
    共现关系、资源流向。

    参数:
        matrix     : 流量/共现矩阵 (n, n)，要求非负
        labels     : 节点标签（等长）；None 则用序号
        width      : 外圈弧宽（占单位半径比例），默认 0.07
        gap        : 每个节点弧段后的固定间隙（弧度），默认 0.01
        alpha      : 弦透明度
        min_flow   : 最小流量阈值；低于该值的流从弦、外圈总量和显示数值中一并过滤
        color_by   : 节点分类标签（等长）；提供时按类别着色并生成图例
        show_values: 是否在弧外显示各节点过滤后的可见总量

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
    if not np.isfinite(min_flow) or min_flow < 0:
        raise ValueError(f"min_flow 必须为非负数，实际值: {min_flow!r}")
    if not np.isfinite(gap) or gap < 0:
        raise ValueError(f"gap 必须为非负有限数（弧度），实际值: {gap!r}")
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
        unique_groups = list(dict.fromkeys(color_by))
        group_map = {g: cycle_color(colors, i) for i, g in enumerate(unique_groups)}
        node_colors = [group_map[g] for g in color_by]
        categorical_legend = group_map
    else:
        node_colors = [cycle_color(colors, i) for i in range(n)]
        categorical_legend = None

    (
        visible,
        totals,
        arc_starts,
        arc_ends,
        source_slots,
        target_slots,
    ) = _compute_chord_geometry(mat, min_flow=min_flow, gap=gap)

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

    # ── 弦：源端与目标端均按真实可见流量占用弧段槽位 ──
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
        for j in range(n):
            flow = float(visible[i, j])
            if flow <= 0:
                continue
            src_start, src_end = source_slots[(i, j)]
            tgt_start, tgt_end = target_slots[(i, j)]
            # 交叉连接两端边界，可在圆内形成无扭结的带状流。
            p0a = polar_to_cart(src_start, 1.0)
            p0b = polar_to_cart(src_end, 1.0)
            p3a = polar_to_cart(tgt_end, 1.0)
            p3b = polar_to_cart(tgt_start, 1.0)
            bx_top, by_top = _bezier_curve(p0a, p3a)
            bx_bot, by_bot = _bezier_curve(p0b, p3b)
            poly_x = np.concatenate([bx_top, bx_bot[::-1]])
            poly_y = np.concatenate([by_top, by_bot[::-1]])
            ax.fill(poly_x, poly_y, color=node_colors[i], alpha=alpha,
                    edgecolor="none", zorder=2)

    # ── 标签与数值 ──
    label_r = 1.0 + width + 0.075
    fontsize = max(7.0, float(plt.rcParams.get("font.size", 9)) - 1.0)
    for i in range(n):
        mid = (arc_starts[i] + arc_ends[i]) / 2
        x, y = polar_to_cart(mid, label_r)
        ha = "left" if np.cos(mid) >= 0 else "right"
        va = "bottom" if np.sin(mid) >= 0 else "top"
        label_text = (
            f"{labels[i]}\n{totals[i]:.0f}"
            if show_values
            else str(labels[i])
        )
        ax.text(
            x, y, label_text, ha=ha, va=va, fontsize=fontsize,
            color="#2F2F2F", fontweight="bold", linespacing=0.95,
        )

    # ── 分类图例 ──
    if categorical_legend is not None:
        from matplotlib.patches import Patch

        handles = [
            Patch(facecolor=c, label=str(g), alpha=0.9)
            for g, c in categorical_legend.items()
        ]
        ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=8)

    ax.set_xlim(-1.40, 1.40)
    ax.set_ylim(-1.40, 1.40)
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
    setattr(fig, "_sciplot_skip_tight_layout", True)

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
    # 顶部/右侧是主散点的边际分布，不是独立论文面板。显式标记后，
    # save() 的科研质量审计不会误要求它们添加 (a)/(b) 面板标签。
    setattr(ax_x, "_sciplot_auxiliary", True)
    setattr(ax_y, "_sciplot_auxiliary", True)

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
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})
