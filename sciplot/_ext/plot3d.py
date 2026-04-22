"""
3D 可视化扩展

用于绘制 3D 曲面、等高线图、3D 散点等。
需要额外安装：uv add sciplot-academic[3d] 或 pip install sciplot-academic[3d]
"""

from __future__ import annotations

from typing import Any, Optional, Union, Tuple, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from sciplot._core.result import PlotResult
from sciplot._core.utils import apply_resolved_style
from sciplot._core.layout import new_figure
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
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  # 注册 3D projection

    X, Y, Z = _validate_grid_shapes(X, Y, Z)

    effective_venue = apply_resolved_style(venue, palette, lang)
    figsize = _get_3d_figsize(effective_venue)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")

    surf = ax.plot_surface(X, Y, Z, cmap=cmap, alpha=alpha, **kwargs)
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    if title:
        ax.set_title(title)

    ax.view_init(elev=elev, azim=azim)
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
        levels = levels_arr
    else:
        raise ValueError(
            f"levels 必须是正整数或数值序列，实际类型: {type(levels).__name__}"
        )

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

    if filled:
        cs = ax.contourf(X, Y, Z, levels=levels, cmap=cmap, **kwargs)
    else:
        cs = ax.contour(X, Y, Z, levels=levels, cmap=cmap, **kwargs)

    if show_labels and not filled:
        ax.clabel(cs, inline=True, fontsize=8)

    fig.colorbar(cs, ax=ax, fraction=0.046, pad=0.04)

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
        c      : 颜色映射值，None 则所有点同色
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
    if c is not None and isinstance(c, (list, tuple, np.ndarray)):
        c_arr = np.asarray(c).ravel()
        if c_arr.size not in (1, n_points):
            raise ValueError(
                f"颜色数组 c 长度必须为 1 或与数据点数量一致，实际为 {c_arr.size}"
            )

    s_arr = s
    if isinstance(s, (list, tuple, np.ndarray)):
        s_arr = np.asarray(s).ravel()
        if s_arr.size not in (1, n_points):
            raise ValueError(
                f"点大小数组 s 长度必须为 1 或与数据点数量一致，实际为 {s_arr.size}"
            )

    effective_venue = apply_resolved_style(venue, palette, lang)
    figsize = _get_3d_figsize(effective_venue)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")

    scatter = ax.scatter(x_arr, y_arr, z_arr, c=c_arr, s=s_arr, alpha=alpha, cmap=cmap, **kwargs)

    if c is not None:
        fig.colorbar(scatter, ax=ax, shrink=0.5, aspect=10)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    if title:
        ax.set_title(title)

    ax.view_init(elev=elev, azim=azim)
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

    effective_venue = apply_resolved_style(venue, palette, lang)
    figsize = _get_3d_figsize(effective_venue)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")

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
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = [
    "plot_surface",
    "plot_contour",
    "plot_3d_scatter",
    "plot_wireframe",
]

