"""
3D 可视化扩展

用于绘制 3D 曲面、等高线图、3D 散点等。
基于 matplotlib.mpl_toolkits.mplot3d，无需额外安装依赖。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Tuple, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from sciplot._core.layout import add_colorbar
from sciplot._core.result import PlotResult
from sciplot._core.utils import apply_resolved_style, cycle_color, get_cycle_colors, new_styled_figure
from sciplot._core.style import VENUES


def _validate_grid_shapes(X: np.ndarray, Y: np.ndarray, Z: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """校验并标准化网格输入，要求三者形状一致且为二维。"""
    X_arr = np.asarray(X)
    Y_arr = np.asarray(Y)
    Z_arr = np.asarray(Z)

    if X_arr.ndim != 2 or Y_arr.ndim != 2 or Z_arr.ndim != 2:
        raise ValueError("X、Y、Z 必须是二维网格数组")

    if X_arr.shape != Y_arr.shape or X_arr.shape != Z_arr.shape:
        raise ValueError(
            f"X/Y/Z 形状必须一致，实际为 X{X_arr.shape}, Y{Y_arr.shape}, Z{Z_arr.shape}"
        )

    return X_arr, Y_arr, Z_arr


def _get_3d_figsize(venue: Optional[str]) -> Tuple[float, float]:
    """获取3D图形的尺寸，基于venue设置。"""
    if venue and venue in VENUES:
        w, h = VENUES[venue].figsize
        # 3D图通常需要更大的尺寸来展示深度
        return (w * 1.2, h * 1.2)
    # 默认尺寸
    return (8.0, 6.0)


def _new_3d_figure(
    venue: Optional[str],
    palette: Optional[str] = None,
    lang: Optional[str] = None,
) -> Tuple[Figure, Any]:
    """创建 3D 图形与坐标轴（注册 3D projection，应用完整样式）。"""
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  # 注册 3D projection

    effective_venue = apply_resolved_style(venue, palette, lang)
    figsize = _get_3d_figsize(effective_venue)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")
    return fig, ax


def plot_surface(
    X: np.ndarray,
    Y: np.ndarray,
    Z: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    zlabel: str = "",
    title: str = "",
    cmap: str = "viridis",
    alpha: float = 1.0,
    elev: float = 30,
    azim: float = -60,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制 3D 曲面图

    参数:
        X, Y   : 网格坐标（由 np.meshgrid 生成）
        Z      : 高度值矩阵
        xlabel : X 轴标签
        ylabel : Y 轴标签
        zlabel : Z 轴标签
        title  : 图表标题
        cmap   : 颜色映射，默认 "viridis"
        alpha  : 透明度，默认 1.0
        elev   : 仰角（垂直视角），默认 30
        azim   : 方位角（水平旋转），默认 -60
        venue  : 期刊样式
        palette: 配色方案
        lang   : 语言设置

    返回:
        PlotResult: 包含 fig 和 ax 的绘图结果对象

    示例:
        >>> import numpy as np
        >>> x = np.linspace(-5, 5, 50)
        >>> y = np.linspace(-5, 5, 50)
        >>> X, Y = np.meshgrid(x, y)
        >>> Z = np.sin(np.sqrt(X**2 + Y**2))
        >>> result = sp.plot_surface(X, Y, Z, xlabel="X", ylabel="Y", zlabel="Z")
        >>> result.save("surface3d")
    """
    X, Y, Z = _validate_grid_shapes(X, Y, Z)

    fig, ax = _new_3d_figure(venue, palette, lang)

    surf = ax.plot_surface(X, Y, Z, cmap=cmap, alpha=alpha, **kwargs)
    add_colorbar(fig, surf, ax=ax, shrink=0.5, aspect=10)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    if title:
        ax.set_title(title)

    ax.view_init(elev=elev, azim=azim)
    ax.grid(False)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_contour(
    X: np.ndarray,
    Y: np.ndarray,
    Z: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    levels: Union[int, Sequence[float]] = 10,
    cmap: str = "viridis",
    filled: bool = False,
    show_labels: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制等高线图

    参数:
        X, Y       : 网格坐标
        Z          : 高度值矩阵
        xlabel     : X 轴标签
        ylabel     : Y 轴标签
        title      : 图表标题
        levels     : 等高线层级数，默认 10
        cmap       : 颜色映射
        filled     : True 则填充等高线区域，False 只画线
        show_labels: 是否显示等高线数值标签
        venue      : 期刊样式
        palette    : 配色方案
        lang       : 语言设置

    返回:
        PlotResult: 包含 fig 和 ax 的绘图结果对象

    示例:
        >>> result = sp.plot_contour(X, Y, Z, levels=15, cmap="RdBu_r")
        >>> result.save("contour")

        >>> # 填充等高线
        >>> result = sp.plot_contour(X, Y, Z, filled=True, cmap="terrain")
    """
    X, Y, Z = _validate_grid_shapes(X, Y, Z)

    if isinstance(levels, int):
        if levels <= 0:
            raise ValueError(f"levels 必须为正整数，实际值: {levels}")
    elif isinstance(levels, (list, tuple, np.ndarray)):
        levels_arr = np.asarray(levels, dtype=float).ravel()
        if levels_arr.size == 0:
            raise ValueError("levels 序列不能为空")
        if not np.all(np.isfinite(levels_arr)):
            raise ValueError("levels 序列不能包含 NaN 或 Inf")
        levels = levels_arr.tolist()
    else:
        raise ValueError(
            f"levels 必须是正整数或数值序列，实际类型: {type(levels).__name__}"
        )

    fig, ax = new_styled_figure(venue, palette, lang)

    if filled:
        cs = ax.contourf(X, Y, Z, levels=levels, cmap=cmap, **kwargs)
    else:
        cs = ax.contour(X, Y, Z, levels=levels, cmap=cmap, **kwargs)

    if show_labels and not filled:
        ax.clabel(cs, inline=True, fontsize=8)

    add_colorbar(fig, cs, ax=ax)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_3d_scatter(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    c: Optional[np.ndarray] = None,
    xlabel: str = "",
    ylabel: str = "",
    zlabel: str = "",
    title: str = "",
    s: Union[float, np.ndarray] = 20,
    alpha: float = 0.7,
    cmap: str = "viridis",
    elev: float = 30,
    azim: float = -60,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制 3D 散点图

    参数:
        x, y, z: 坐标数组
        c      : 颜色映射值；None 则所有点同色。
                 支持：数值标量 / 单元素数组（所有点渲染为同一颜色）、
                 等长数值数组（按值着色 + 颜色条）、颜色字符串（如 "red"）。
        xlabel : X 轴标签
        ylabel : Y 轴标签
        zlabel : Z 轴标签
        title  : 图表标题
        s      : 点大小，默认 20（可以是标量或数组）
        alpha  : 透明度，默认 0.7
        cmap   : 颜色映射（当 c 不为 None 时有效）
        elev   : 仰角
        azim   : 方位角
        venue  : 期刊样式
        palette: 配色方案
        lang   : 语言设置

    返回:
        PlotResult: 包含 fig 和 ax 的绘图结果对象

    示例:
        >>> # 简单 3D 散点
        >>> result = sp.plot_3d_scatter(x, y, z, xlabel="X", ylabel="Y", zlabel="Z")

        >>> # 按第四维度着色
        >>> result = sp.plot_3d_scatter(x, y, z, c=values, cmap="plasma")
    """
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  # 注册 3D projection

    x_arr = np.asarray(x).ravel()
    y_arr = np.asarray(y).ravel()
    z_arr = np.asarray(z).ravel()

    n_points = len(x_arr)
    if len(y_arr) != n_points or len(z_arr) != n_points:
        raise ValueError(
            f"x/y/z 长度必须一致，实际为 x={n_points}, y={len(y_arr)}, z={len(z_arr)}"
        )

    c_arr = c
    c_mappable = False
    if c is not None:
        if isinstance(c, str):
            # 颜色字符串：单色渲染，不参与颜色映射
            c_arr = c
        elif isinstance(c, (list, tuple, np.ndarray)):
            c_arr = np.asarray(c).ravel()
            if c_arr.size not in (1, n_points):
                raise ValueError(
                    f"颜色数组 c 长度必须为 1 或与数据点数量一致，实际为 {c_arr.size}"
                )
            if c_arr.size == 1:
                # 单元素数组：广播为等长数组，按单一颜色渲染
                c_arr = np.full(n_points, c_arr[0])
            else:
                c_mappable = True
        else:
            # 数值标量：广播为等长数组，按单一颜色渲染（3D scatter 不接受标量 c）
            try:
                scalar_val = float(c)
            except (TypeError, ValueError):
                raise ValueError(
                    f"参数 'c' 必须是颜色字符串、数值标量或数组，实际类型: {type(c).__name__}"
                )
            c_arr = np.full(n_points, scalar_val)

    s_arr = s
    if isinstance(s, (list, tuple, np.ndarray)):
        s_arr = np.asarray(s).ravel()
        if s_arr.size not in (1, n_points):
            raise ValueError(
                f"点大小数组 s 长度必须为 1 或与数据点数量一致，实际为 {s_arr.size}"
            )

    fig, ax = _new_3d_figure(venue, palette, lang)

    scatter_kwargs: Dict[str, Any] = dict(alpha=alpha, **kwargs)
    if c_mappable:
        # 仅在 c 为可映射数组时传入 cmap，避免无数据时 matplotlib 发出
        # "No data for colormapping provided via 'c'" 警告。
        scatter_kwargs["cmap"] = cmap
    scatter = ax.scatter(x_arr, y_arr, z_arr, c=c_arr, s=s_arr, **scatter_kwargs)

    if c_mappable:
        add_colorbar(fig, scatter, ax=ax, shrink=0.5, aspect=10)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    if title:
        ax.set_title(title)

    ax.view_init(elev=elev, azim=azim)
    ax.grid(False)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_wireframe(
    X: np.ndarray,
    Y: np.ndarray,
    Z: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    zlabel: str = "",
    title: str = "",
    color: str = "#333333",
    alpha: float = 0.8,
    rstride: int = 1,
    cstride: int = 1,
    elev: float = 30,
    azim: float = -60,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制 3D 线框图

    参数:
        X, Y       : 网格坐标
        Z          : 高度值矩阵
        xlabel     : X 轴标签
        ylabel     : Y 轴标签
        zlabel     : Z 轴标签
        title      : 图表标题
        color      : 线框颜色
        alpha      : 透明度
        rstride    : 行步长，控制网格密度
        cstride    : 列步长，控制网格密度
        elev       : 仰角
        azim       : 方位角
        venue      : 期刊样式
        palette    : 配色方案
        lang       : 语言设置

    返回:
        PlotResult: 包含 fig 和 ax 的绘图结果对象

    示例:
        >>> result = sp.plot_wireframe(X, Y, Z, rstride=2, cstride=2)
        >>> result.save("wireframe")
    """
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  # 注册 3D projection

    X, Y, Z = _validate_grid_shapes(X, Y, Z)
    if not isinstance(rstride, int) or rstride <= 0:
        raise ValueError(f"rstride 必须为正整数，实际值: {rstride!r}")
    if not isinstance(cstride, int) or cstride <= 0:
        raise ValueError(f"cstride 必须为正整数，实际值: {cstride!r}")

    fig, ax = _new_3d_figure(venue, palette, lang)

    ax.plot_wireframe(
        X, Y, Z, color=color, alpha=alpha,
        rstride=rstride, cstride=cstride, **kwargs
    )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    if title:
        ax.set_title(title)

    ax.view_init(elev=elev, azim=azim)
    ax.grid(False)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_waterfall3d(
    x: np.ndarray,
    y_list: List[np.ndarray],
    labels: Optional[List[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    zlabel: str = "",
    title: str = "",
    fill: bool = True,
    fill_alpha: float = 0.3,
    linewidth: float = 1.2,
    spacing: float = 1.0,
    baseline: float = 0.0,
    elev: float = 25,
    azim: float = -60,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制 3D 瀑布图（多组曲线沿第三轴堆叠，光谱/频谱经典展示方式）

    每组曲线沿 Y 轴按 spacing 间隔摆放，Z 轴为数值；
    可选在曲线与 baseline 之间填充半透明色带，适合对比多组信号的
    形状变化（如拉曼光谱、色谱、时频分布）。

    参数:
        x          : 共享的 X 轴数据（一维）
        y_list     : 多组 Y 轴数值列表，每组长度与 x 一致
        labels     : 各组标签；None 则自动生成 "Series N"
        xlabel     : X 轴标签
        ylabel     : Y 轴标签（组轴，建议如 "组序号" / "样本"）
        zlabel     : Z 轴标签（数值轴）
        fill       : 是否在曲线与 baseline 之间填充色带，默认 True
        fill_alpha : 填充透明度，默认 0.3
        linewidth  : 曲线线宽，默认 1.2
        spacing    : 相邻组的 Y 轴间隔，默认 1.0
        baseline   : 填充色带的下边界，默认 0.0
        elev / azim: 3D 视角
        **kwargs   : 传递给 ax.plot() 的额外参数（如 marker）

    示例:
        >>> # 多组光谱堆叠对比
        >>> x = np.linspace(400, 4000, 500)  # 波数
        >>> spectra = [
        ...     np.exp(-((x - 1200) / 150) ** 2) + 0.05 * np.random.randn(500),
        ...     np.exp(-((x - 1600) / 150) ** 2) + 0.05 * np.random.randn(500),
        ...     np.exp(-((x - 2000) / 150) ** 2) + 0.05 * np.random.randn(500),
        ... ]
        >>> fig, ax = sp.plot_waterfall3d(
        ...     x, spectra, labels=["样品A", "样品B", "样品C"],
        ...     xlabel="波数 (cm⁻¹)", ylabel="样品", zlabel="强度",
        ...     fill=True, fill_alpha=0.25,
        ... )
        >>> sp.save(fig, "waterfall3d")
    """
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  # 注册 3D projection
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    x_arr = np.asarray(x, dtype=float)
    if x_arr.ndim != 1:
        raise ValueError(f"x 必须是一维数组，当前维度: {x_arr.ndim}")
    if x_arr.size == 0:
        raise ValueError("x 不能为空")
    if not np.all(np.isfinite(x_arr)):
        raise ValueError("x 不能包含 NaN 或 Inf")

    if not y_list:
        raise ValueError("参数 'y_list' 不能为空列表")

    if labels is None:
        labels = [f"Series {i + 1}" for i in range(len(y_list))]
    elif len(labels) != len(y_list):
        raise ValueError(
            f"labels 长度 ({len(labels)}) 与 y_list 长度 ({len(y_list)}) 不一致"
        )

    if not isinstance(spacing, (int, float)) or spacing <= 0:
        raise ValueError(f"spacing 必须为正数，实际值: {spacing!r}")

    normalized: List[np.ndarray] = []
    for i, y in enumerate(y_list):
        y_arr = np.asarray(y, dtype=float)
        if y_arr.ndim != 1:
            raise ValueError(f"y_list[{i}] 必须是一维数组，当前维度: {y_arr.ndim}")
        if len(y_arr) != len(x_arr):
            raise ValueError(
                f"y_list[{i}] 长度 ({len(y_arr)}) 与 x 长度 ({len(x_arr)}) 不一致"
            )
        if not np.all(np.isfinite(y_arr)):
            raise ValueError(f"y_list[{i}] 不能包含 NaN 或 Inf")
        normalized.append(y_arr)

    fig, ax = _new_3d_figure(venue, palette, lang)

    colors = get_cycle_colors()
    if not colors:
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    for i, (y_arr, label) in enumerate(zip(normalized, labels)):
        group_pos = i * float(spacing)
        color = cycle_color(colors, i)

        ax.plot(
            x_arr,
            np.full_like(x_arr, group_pos),
            y_arr,
            color=color,
            linewidth=linewidth,
            label=label,
            **kwargs,
        )

        if fill:
            # 曲线与 baseline 之间的填充带
            verts = [
                list(zip(x_arr, np.full_like(x_arr, group_pos), y_arr)),
                list(zip(x_arr[::-1], np.full_like(x_arr, group_pos), np.full_like(x_arr, baseline))),
            ]
            poly = Poly3DCollection(
                verts, alpha=fill_alpha, facecolor=color, linewidths=0.0
            )
            ax.add_collection3d(poly)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    if title:
        ax.set_title(title)

    ax.view_init(elev=elev, azim=azim)
    ax.grid(False)
    if labels:
        ax.legend(loc="upper right", fontsize=plt.rcParams.get("font.size", 9) - 1)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = [
    "plot_surface",
    "plot_contour",
    "plot_3d_scatter",
    "plot_wireframe",
    "plot_waterfall3d",
]

