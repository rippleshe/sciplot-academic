"""
3D 可视化扩展

用于绘制 3D 曲面、等高线图、3D 散点等。
需要额外安装：uv add sciplot-academic[3d] 或 pip install sciplot-academic[3d]
"""

from __future__ import annotations

from typing import Any, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from sciplot._core.result import PlotResult
from sciplot._core.utils import apply_resolved_style
from sciplot._core.layout import new_figure


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

    effective_venue = apply_resolved_style(venue, palette)
    fig = plt.figure(figsize=(8, 6))
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
    levels: int = 10,
    cmap: str = "viridis",
    filled: bool = False,
    show_labels: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
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

    返回:
        PlotResult: 包含 fig 和 ax 的绘图结果对象

    示例:
        >>> result = sp.plot_contour(X, Y, Z, levels=15, cmap="RdBu_r")
        >>> result.save("contour")

        >>> # 填充等高线
        >>> result = sp.plot_contour(X, Y, Z, filled=True, cmap="terrain")
    """
    effective_venue = apply_resolved_style(venue, palette)
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

    返回:
        PlotResult: 包含 fig 和 ax 的绘图结果对象

    示例:
        >>> # 简单 3D 散点
        >>> result = sp.plot_3d_scatter(x, y, z, xlabel="X", ylabel="Y", zlabel="Z")

        >>> # 按第四维度着色
        >>> result = sp.plot_3d_scatter(x, y, z, c=values, cmap="plasma")
    """
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  # 注册 3D projection

    effective_venue = apply_resolved_style(venue, palette)
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    scatter = ax.scatter(x, y, z, c=c, s=s, alpha=alpha, cmap=cmap, **kwargs)

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

    返回:
        PlotResult: 包含 fig 和 ax 的绘图结果对象

    示例:
        >>> result = sp.plot_wireframe(X, Y, Z, rstride=2, cstride=2)
        >>> result.save("wireframe")
    """
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  # 注册 3D projection

    effective_venue = apply_resolved_style(venue, palette)
    fig = plt.figure(figsize=(8, 6))
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
