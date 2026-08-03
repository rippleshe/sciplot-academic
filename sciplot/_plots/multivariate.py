"""
多维图表 — 平行坐标图

用于展示多个样本在多个特征维度上的分布规律。
"""

from __future__ import annotations

from typing import Any, List, Optional, Union, cast

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D

from sciplot._core.layout import add_colorbar
from sciplot._core.style import VENUES, get_current_venue
from sciplot._core.utils import apply_resolved_style, cycle_color, get_cmap_safe, get_cycle_colors, new_styled_figure
from sciplot._core.result import PlotResult


def _normalize_minmax(data: np.ndarray) -> np.ndarray:
    """Min-Max 归一化到 [0, 1]"""
    min_val = np.min(data)
    max_val = np.max(data)
    if max_val == min_val:
        return np.zeros_like(data)
    return (data - min_val) / (max_val - min_val)


def _normalize_zscore(data: np.ndarray) -> np.ndarray:
    """Z-Score 标准化"""
    mean_val = np.mean(data)
    std_val = np.std(data)
    if std_val == 0:
        return np.zeros_like(data)
    return (data - mean_val) / std_val


def plot_parallel(
    data: np.ndarray,
    columns: Optional[List[str]] = None,
    labels: Optional[List[str]] = None,
    color_by: Optional[Union[int, str]] = None,
    normalize: str = "minmax",
    show_colorbar: bool = True,
    alpha: float = 0.5,
    linewidth: float = 1.0,
    title: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制平行坐标图（多维特征比较）

    参数:
        data     : 二维数组 (n_samples, n_features) 或 DataFrame
        columns  : 特征名称列表；若 data 为 DataFrame 则自动获取
        labels   : 样本标签列表（用于图例）
        color_by : 按某列着色：
                   - int: 列索引
                   - str: 列名（需提供 columns）
                   - None: 不区分颜色
        normalize: 归一化方式
                   - "minmax": Min-Max 归一化到 [0, 1]（默认）
                   - "zscore": Z-Score 标准化
                   - "none": 不归一化
        show_colorbar: 连续着色时是否显示 colorbar，默认 True
        alpha    : 线条透明度，默认 0.5
        linewidth: 线条宽度，默认 1.0

    示例:
        >>> # 基本用法
        >>> data = np.random.randn(50, 5)  # 50个样本，5个特征
        >>> fig, ax = sp.plot_parallel(
        ...     data,
        ...     columns=["特征A", "特征B", "特征C", "特征D", "特征E"],
        ...     title="平行坐标图"
        ... )
        >>> 
        >>> # 按类别着色
        >>> fig, ax = sp.plot_parallel(
        ...     data,
        ...     columns=["A", "B", "C", "D"],
        ...     color_by=0,  # 按第一列着色
        ... )
    """
    categorical_color_values: Optional[np.ndarray] = None
    if hasattr(data, "iloc"):
        df = cast(Any, data)
        if labels is None and hasattr(df, "index"):
            labels = [str(idx) for idx in df.index]
        if isinstance(color_by, str) and color_by in df.columns:
            col_series = df[color_by]
            try:
                col_is_numeric = np.issubdtype(col_series.dtype, np.number)
            except TypeError:
                # pandas 3.x 的 StringDtype 等无法被 issubdtype 解释
                col_is_numeric = False
            if not col_is_numeric:
                # 分类着色列：从数值数据中剔除，仅用于着色
                categorical_color_values = np.asarray(col_series.to_numpy())
                df = df.drop(columns=[color_by])
                color_by = None
        # 只保留数值列（混合类型 DataFrame 自动提取）；无 select_dtypes 的
        # 轻量 DataFrame 模拟对象（全数值）直接使用 .values 兼容旧行为
        select_dtypes = getattr(df, "select_dtypes", None)
        if select_dtypes is not None:
            df_numeric = df.select_dtypes(include=[np.number])
            if df_numeric.shape[1] == 0:
                raise ValueError("data 中不包含数值列")
            if columns is not None:
                # 用户显式提供的 columns：剔除被移走的非数值列
                df_cols = set(df_numeric.columns)
                columns = [c for c in columns if c in df_cols]
                if len(columns) != df_numeric.shape[1]:
                    raise ValueError(
                        f"columns 长度 ({len(columns)}) 与数值特征数 ({df_numeric.shape[1]}) 不一致"
                    )
            else:
                columns = list(df_numeric.columns)
            data = df_numeric.values
        else:
            # 轻量 DataFrame 模拟对象：直接取 .values（假定全数值）
            data = df.values

    data = np.asarray(data)

    if data.ndim != 2:
        raise ValueError(f"data 必须是二维数组，当前维度: {data.ndim}")

    if not np.issubdtype(data.dtype, np.number):
        raise ValueError("data 必须是数值型二维数组")

    n_samples, n_features = data.shape

    if columns is None:
        columns = [f"特征 {i+1}" for i in range(n_features)]
    elif len(columns) != n_features:
        raise ValueError(
            f"columns 长度 ({len(columns)}) 与特征数 ({n_features}) 不一致"
        )

    if normalize == "minmax":
        data_norm = np.column_stack([
            _normalize_minmax(data[:, j]) for j in range(n_features)
        ])
    elif normalize == "zscore":
        data_norm = np.column_stack([
            _normalize_zscore(data[:, j]) for j in range(n_features)
        ])
    elif normalize == "none":
        data_norm = data
    else:
        raise ValueError(f"未知的归一化方式: {normalize}。可选: 'minmax', 'zscore', 'none'")

    fig, ax = new_styled_figure(venue, palette, lang)

    x = np.arange(n_features)

    if categorical_color_values is not None:
        # DataFrame 分类列着色（数值列已提取，此路径只按类别分配颜色）
        unique_vals = sorted(set(categorical_color_values), key=str)
        colors = get_cycle_colors()
        cat_map = {v: cycle_color(colors, i) for i, v in enumerate(unique_vals)}
        for i in range(n_samples):
            ax.plot(
                x, data_norm[i, :], alpha=alpha,
                color=cat_map.get(categorical_color_values[i], colors[0]),
                linewidth=linewidth, **kwargs,
            )
        legend_handles = [
            Line2D([0], [0], color=cat_map[v], linewidth=linewidth, label=str(v))
            for v in unique_vals
        ]
        ax.legend(handles=legend_handles, title="")
    elif color_by is not None:
        if isinstance(color_by, str):
            if columns is None:
                raise ValueError("color_by 为列名时必须提供 columns")
            try:
                color_idx = columns.index(color_by)
            except ValueError:
                raise ValueError(f"列名 '{color_by}' 不在 columns 中")
        else:
            color_idx = int(color_by)
            if not (-n_features <= color_idx < n_features):
                raise ValueError(
                    f"color_by 索引越界: {color_idx}，有效范围: [{-n_features}, {n_features - 1}]"
                )
            if color_idx < 0:
                color_idx += n_features

        color_values = np.asarray(data[:, color_idx])
        unique_values = np.unique(color_values)
        is_numeric_color = np.issubdtype(color_values.dtype, np.number)
        colors = get_cycle_colors()

        if (not is_numeric_color) or len(unique_values) <= 10:
            color_map = {v: cycle_color(colors, i) for i, v in enumerate(unique_values)}

            for i in range(n_samples):
                color = color_map.get(color_values[i], colors[0])
                ax.plot(x, data_norm[i, :], alpha=alpha, color=color, linewidth=linewidth, **kwargs)

            legend_handles = []
            for v in unique_values:
                legend_handles.append(
                    Line2D([0], [0], color=color_map[v], linewidth=linewidth, label=str(v))
                )
            ax.legend(handles=legend_handles, title=columns[color_idx])
        else:
            finite_values = color_values[np.isfinite(color_values)]
            if finite_values.size == 0:
                raise ValueError("color_by 列全为 NaN 或 Inf，无法进行连续映射")

            cmap = get_cmap_safe("viridis")
            norm = Normalize(vmin=float(finite_values.min()), vmax=float(finite_values.max()))

            for i in range(n_samples):
                val = color_values[i]
                color = cmap(norm(val)) if np.isfinite(val) else colors[0]
                ax.plot(x, data_norm[i, :], alpha=alpha, color=color, linewidth=linewidth, **kwargs)

            if show_colorbar:
                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])
                cbar = add_colorbar(fig, sm, ax=ax)
                cbar.set_label(columns[color_idx])
    else:
        for i in range(n_samples):
            ax.plot(x, data_norm[i, :], alpha=alpha, linewidth=linewidth, **kwargs)

    ax.set_xticks(x)
    ax.set_xticklabels(columns, rotation=45, ha="right")
    ax.set_xlim(-0.5, n_features - 0.5)

    finite_values = data_norm[np.isfinite(data_norm)]
    if finite_values.size == 0:
        raise ValueError("data 中不包含可用于绘图的有限数值")

    if normalize == "minmax":
        ax.set_ylim(-0.05, 1.05)
        y_label = "归一化值"
    elif normalize == "zscore":
        y_min = float(finite_values.min())
        y_max = float(finite_values.max())
        y_margin = (y_max - y_min) * 0.05 if y_max > y_min else 0.5
        ax.set_ylim(y_min - y_margin, y_max + y_margin)
        y_label = "标准化值 (Z-score)"
    else:
        y_min = float(finite_values.min())
        y_max = float(finite_values.max())
        y_margin = (y_max - y_min) * 0.05 if y_max > y_min else 0.5
        ax.set_ylim(y_min - y_margin, y_max + y_margin)
        y_label = "原始值"

    ax.set_ylabel(y_label)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")

    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_scatter_matrix(
    data: np.ndarray,
    columns: Optional[List[str]] = None,
    color_by: Optional[np.ndarray] = None,
    diag: str = "hist",
    alpha: float = 0.5,
    s: float = 10,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
) -> PlotResult:
    """绘制散点矩阵，展示多特征两两关系。"""
    values = np.asarray(data, dtype=float)
    if values.ndim != 2:
        raise ValueError(f"data 必须是二维数组，当前维度: {values.ndim}")

    n_samples, n_features = values.shape
    if n_features < 2:
        raise ValueError(f"至少需要 2 个特征，当前: {n_features}")

    if columns is None:
        columns = [f"特征 {i + 1}" for i in range(n_features)]
    elif len(columns) != n_features:
        raise ValueError(
            f"columns 长度 ({len(columns)}) 与特征数 ({n_features}) 不一致"
        )

    if color_by is not None:
        color_values = np.asarray(color_by)
        if color_values.ndim != 1 or len(color_values) != n_samples:
            raise ValueError("color_by 必须是一维且长度与样本数一致")
    else:
        color_values = None

    diag = diag.lower()
    if diag not in {"hist", "kde", "none"}:
        raise ValueError("diag 仅支持 'hist'、'kde'、'none'")

    scipy_stats_module = None
    if diag == "kde":
        try:
            from scipy import stats as scipy_stats_module
        except ImportError as e:
            raise ImportError(
                "diag='kde' 需要安装 scipy。请运行: uv pip install scipy 或 pip install scipy"
            ) from e

    effective_venue = apply_resolved_style(venue, palette, lang)
    active_venue = effective_venue or get_current_venue() or "nature"
    venue_cfg = VENUES.get(active_venue, VENUES["nature"])
    scale = max(1.0, n_features / 2.0)
    fig_w = max(4.0, min(14.0, venue_cfg.figsize[0] * scale))
    fig_h = max(4.0, min(14.0, venue_cfg.figsize[1] * scale))
    fig, axes = plt.subplots(
        n_features,
        n_features,
        squeeze=False,
        figsize=(fig_w, fig_h),
    )

    if color_values is not None:
        is_numeric = np.issubdtype(color_values.dtype, np.number)
        unique_vals = np.unique(color_values)
        if (not is_numeric) or len(unique_vals) <= 10:
            colors = get_cycle_colors()
            color_map = {v: cycle_color(colors, i) for i, v in enumerate(unique_vals)}
            scatter_colors = [color_map[v] for v in color_values]
            cmap = None
        else:
            cmap = "viridis"
            scatter_colors = color_values.astype(float)
    else:
        scatter_colors = None
        cmap = None

    for row in range(n_features):
        for col in range(n_features):
            ax = axes[row, col]
            x_col = values[:, col]
            y_col = values[:, row]

            if row == col:
                if diag == "hist":
                    ax.hist(x_col, bins=20, alpha=0.75)
                elif diag == "kde":
                    finite = x_col[np.isfinite(x_col)]
                    if finite.size >= 2 and scipy_stats_module is not None:
                        kde = scipy_stats_module.gaussian_kde(finite)
                        x_eval = np.linspace(finite.min(), finite.max(), 200)
                        y_eval = kde(x_eval)
                        ax.plot(x_eval, y_eval)
                        ax.fill_between(x_eval, y_eval, alpha=0.2)
                # diag == "none" 时保持空白
            else:
                ax.scatter(
                    x_col,
                    y_col,
                    c=scatter_colors,
                    cmap=cmap,
                    s=s,
                    alpha=alpha,
                    edgecolors="none",
                )

            if row == n_features - 1:
                ax.set_xlabel(columns[col])
            else:
                ax.set_xticklabels([])

            if col == 0:
                ax.set_ylabel(columns[row])
            else:
                ax.set_yticklabels([])

            ax.tick_params(direction="in")
            ax.grid(False)

    fig.tight_layout()
    return PlotResult(fig, axes, metadata={"venue": effective_venue, "palette": palette})


def plot_ternary(
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
    labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    color_by: Optional[np.ndarray] = None,
    cmap: str = "viridis",
    colorbar_label: str = "",
    grid: bool = True,
    grid_levels: int = 4,
    alpha: float = 0.7,
    show_colorbar: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制三角相图（Ternary Diagram，三组分占比）

    三个组分归一化后投影到等边三角形内，每个点代表一个
    三组分混合配比，适合材料配方、土壤质地、相平衡等场景。

    参数:
        a, b, c      : 三组分含量（等长、非负；行和自动归一化）
        labels       : 三个顶点标签，默认 ["A", "B", "C"]
        color_by     : 连续着色通道（等长）
        cmap         : 颜色映射
        colorbar_label: 颜色条标签
        grid         : 是否绘制平行网格线
        grid_levels  : 每个方向的网格线数，默认 4
        alpha        : 散点透明度
        show_colorbar: 是否显示颜色条

    示例:
        >>> # 三组分材料配比
        >>> fig, ax = sp.plot_ternary(
        ...     a, b, c, labels=["组分A", "组分B", "组分C"],
        ...     color_by=性能值,
        ... )
        >>> sp.save(fig, "ternary")
    """
    a_arr = np.asarray(a, dtype=float).ravel()
    b_arr = np.asarray(b, dtype=float).ravel()
    c_arr = np.asarray(c, dtype=float).ravel()

    n = len(a_arr)
    if len(b_arr) != n or len(c_arr) != n:
        raise ValueError("a/b/c 长度必须一致")
    if n == 0:
        raise ValueError("a/b/c 不能为空")
    if not np.all(np.isfinite(a_arr)) or not np.all(np.isfinite(b_arr)) \
            or not np.all(np.isfinite(c_arr)):
        raise ValueError("a/b/c 不能包含 NaN 或 Inf")
    if np.any(a_arr < 0) or np.any(b_arr < 0) or np.any(c_arr < 0):
        raise ValueError("a/b/c 不能包含负值（组分占比必须非负）")
    row_sums = a_arr + b_arr + c_arr
    if np.any(row_sums <= 0):
        raise ValueError("a/b/c 每行之和必须大于 0")

    if labels is not None:
        if len(labels) != 3:
            raise ValueError(f"labels 必须恰好 3 个顶点标签，当前: {len(labels)}")
    else:
        labels = ["A", "B", "C"]

    if color_by is not None:
        color_arr = np.asarray(color_by).ravel()
        if color_arr.size != n:
            raise ValueError(
                f"color_by 长度 ({color_arr.size}) 与数据长度 ({n}) 不一致"
            )
    else:
        color_arr = None
    if not isinstance(grid_levels, int) or grid_levels <= 0:
        raise ValueError(f"grid_levels 必须为正整数，实际值: {grid_levels!r}")

    # 归一化 + 三角投影（B 在 (1,0)，C 在 (0.5, √3/2)）
    norm = row_sums[:, None]
    a_n = a_arr / norm[:, 0]
    b_n = b_arr / norm[:, 0]
    c_n = c_arr / norm[:, 0]
    xs = (2 * b_n + c_n) / 2
    ys = c_n * (np.sqrt(3) / 2)

    effective_venue = apply_resolved_style(venue, palette, lang)
    from sciplot._core.style import VENUES

    venue_cfg = VENUES.get(effective_venue or "nature", VENUES["nature"])
    size = max(venue_cfg.figsize) * 0.95
    fig, ax = plt.subplots(figsize=(size, size * 0.92))

    # 三角形边框
    tri = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, np.sqrt(3) / 2], [0.0, 0.0]])
    ax.plot(tri[:, 0], tri[:, 1], color="#444444", linewidth=1.2, zorder=1)

    # 网格线（平行于三边）
    if grid:
        for k in range(1, grid_levels + 1):
            frac = k / (grid_levels + 1)
            # 平行于 BC（a 恒定）
            x0, y0 = 0.5 * frac, frac * np.sqrt(3) / 2
            x1, y1 = 1 - 0.5 * frac, frac * np.sqrt(3) / 2
            ax.plot([x0, x1], [y0, y1], color="#CCCCCC", linewidth=0.5, zorder=1)
            # 平行于 AC（b 恒定）
            x2, y2 = 0.5 * frac, frac * np.sqrt(3) / 2
            ax.plot([x2 - 0.5 * frac, x2], [y2, 0.0], color="#CCCCCC", linewidth=0.5, zorder=1)
            # 平行于 AB（c 恒定）
            x3, y3 = 1 - 0.5 * frac, frac * np.sqrt(3) / 2
            ax.plot([x3, x3 - 0.5 * frac], [y3, 0.0], color="#CCCCCC", linewidth=0.5, zorder=1)

    # 散点
    if color_arr is not None:
        scatter = ax.scatter(xs, ys, c=color_arr, cmap=cmap, alpha=alpha,
                             edgecolors="none", zorder=3, **kwargs)
        if show_colorbar:
            cbar = add_colorbar(fig, scatter, ax=ax)
            if colorbar_label:
                cbar.set_label(colorbar_label)
    else:
        colors = get_cycle_colors()
        ax.scatter(xs, ys, c=colors[0], alpha=alpha,
                   edgecolors="none", zorder=3, **kwargs)

    # 顶点标签
    fontsize = plt.rcParams.get("font.size", 9) + 1
    ax.text(0.0, -0.08, labels[0], ha="center", va="top", fontsize=fontsize, fontweight="bold")
    ax.text(1.0, -0.08, labels[1], ha="center", va="top", fontsize=fontsize, fontweight="bold")
    ax.text(0.5, np.sqrt(3) / 2 + 0.06, labels[2], ha="center", va="bottom",
            fontsize=fontsize, fontweight="bold")

    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.12, np.sqrt(3) / 2 + 0.12)
    ax.set_aspect("equal")
    ax.set_axis_off()
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = ["plot_parallel", "plot_scatter_matrix", "plot_ternary"]
