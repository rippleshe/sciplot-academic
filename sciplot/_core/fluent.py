"""
链式调用 (Fluent Interface) — 流畅的绘图API

提供链式调用风格的绘图接口，支持：
    sp.style("nature").palette("pastel").plot(x, y).save("output")
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from sciplot._core.style import setup_style, get_current_lang, VALID_LANGS
from sciplot._core.config import get_config
from sciplot._core.palette import DEFAULT_PALETTE
from sciplot._core.layout import new_figure
from sciplot._core.result import PlotResult


class PlotChain:
    """
    链式调用构建器

    用于构建流畅的绘图调用链，支持样式设置、绘图、保存等操作。

    示例:
        >>> import sciplot as sp
        >>> fig = sp.style("nature").palette("pastel").plot(x, y).save("output")

        >>> # 多图层
        >>> chain = sp.style("ieee").palette("earth")
        >>> fig = chain.plot(x, y, label="线1").scatter(x2, y2, label="散点").legend().save("output")
    """

    def __init__(
        self,
        venue: Optional[str] = None,
        palette: Optional[str] = None,
        lang: Optional[str] = None,
    ):
        resolved_venue = venue if venue is not None else get_config("venue")
        resolved_palette = palette if palette is not None else get_config("palette")

        self._venue = resolved_venue if isinstance(resolved_venue, str) and resolved_venue else "nature"
        self._palette = (
            resolved_palette
            if isinstance(resolved_palette, str) and resolved_palette
            else DEFAULT_PALETTE
        )
        self._lang = lang
        self._figsize: Optional[Tuple[float, float]] = None
        self._fig: Optional[Figure] = None
        self._ax: Optional[Axes] = None
        self._style_applied = False

    def _apply_style(self) -> None:
        """应用当前样式设置"""
        if not self._style_applied:
            effective_lang = self._lang
            if effective_lang is None:
                current_lang = get_current_lang()
                effective_lang = current_lang if current_lang in VALID_LANGS else "zh"
            setup_style(self._venue, self._palette, effective_lang)
            self._style_applied = True

    def _ensure_figure(self) -> Tuple[Figure, Axes]:
        """确保图形已创建"""
        if self._fig is None:
            self._apply_style()
            if self._figsize:
                self._fig, self._ax = plt.subplots(figsize=self._figsize)
            else:
                self._fig, self._ax = new_figure(self._venue)
        return self._fig, self._ax

    # ═══════════════════════════════════════════════════════════════
    # 样式设置方法（返回 self 支持链式调用）
    # ═══════════════════════════════════════════════════════════════

    def style(self, venue: str) -> PlotChain:
        """
        设置期刊样式

        参数:
            venue: 期刊样式，如 "nature", "ieee", "thesis" 等

        返回:
            self 支持链式调用

        示例:
            >>> sp.style("nature").plot(x, y)
        """
        if self._fig is not None:
            raise RuntimeError(
                "style() 必须在调用任何绘图方法之前设置。"
                "当前图形已创建，无法在同一链中切换样式。"
            )
        self._venue = venue
        self._style_applied = False
        return self

    def palette(self, palette: str) -> PlotChain:
        """
        设置配色方案

        参数:
            palette: 配色名称，如 "pastel", "earth", "100yuan" 等

        返回:
            self 支持链式调用

        示例:
            >>> sp.palette("earth").plot(x, y)
        """
        if self._fig is not None:
            raise RuntimeError(
                "palette() 必须在调用任何绘图方法之前设置。"
                "当前图形已创建，无法在同一链中切换配色。"
            )
        self._palette = palette
        self._style_applied = False
        return self

    def lang(self, lang: str) -> PlotChain:
        """
        设置语言

        参数:
            lang: "zh" 或 "en"

        返回:
            self 支持链式调用
        """
        if self._fig is not None:
            raise RuntimeError(
                "lang() 必须在调用任何绘图方法之前设置。"
                "当前图形已创建，无法在同一链中切换语言。"
            )
        self._lang = lang
        self._style_applied = False
        return self

    def figsize(self, width: float, height: float) -> PlotChain:
        """
        设置图形尺寸

        参数:
            width: 宽度（英寸）
            height: 高度（英寸）

        返回:
            self 支持链式调用

        示例:
            >>> sp.figsize(10, 6).plot(x, y)
        """
        if self._fig is not None:
            raise RuntimeError(
                "figsize() 必须在调用任何绘图方法之前设置。"
                "当前图形已创建，无法修改尺寸。"
            )
        self._figsize = (width, height)
        return self

    # ═══════════════════════════════════════════════════════════════
    # 绘图方法（返回 FigureWrapper 支持继续操作）
    # ═══════════════════════════════════════════════════════════════

    def plot(self, x, y, **kwargs) -> FigureWrapper:
        """绘制折线图"""
        self._ensure_figure()
        self._ax.plot(x, y, **kwargs)
        return FigureWrapper(self._fig, self._ax, self)

    def scatter(self, x, y, **kwargs) -> FigureWrapper:
        """绘制散点图"""
        self._ensure_figure()
        self._ax.scatter(x, y, **kwargs)
        return FigureWrapper(self._fig, self._ax, self)

    def bar(self, x, height, **kwargs) -> FigureWrapper:
        """绘制柱状图"""
        self._ensure_figure()
        self._ax.bar(x, height, **kwargs)
        return FigureWrapper(self._fig, self._ax, self)

    def hist(self, x, **kwargs) -> FigureWrapper:
        """绘制直方图"""
        self._ensure_figure()
        self._ax.hist(x, **kwargs)
        return FigureWrapper(self._fig, self._ax, self)

    def boxplot(self, data, **kwargs) -> FigureWrapper:
        """绘制箱线图"""
        self._ensure_figure()
        self._ax.boxplot(data, **kwargs)
        return FigureWrapper(self._fig, self._ax, self)

    def fill_between(self, x, y1, y2=None, **kwargs) -> FigureWrapper:
        """填充区域"""
        self._ensure_figure()
        if y2 is None:
            y2 = 0
        self._ax.fill_between(x, y1, y2, **kwargs)
        return FigureWrapper(self._fig, self._ax, self)

    def errorbar(self, x, y, yerr=None, xerr=None, **kwargs) -> FigureWrapper:
        """绘制误差线图"""
        self._ensure_figure()
        self._ax.errorbar(x, y, yerr=yerr, xerr=xerr, **kwargs)
        return FigureWrapper(self._fig, self._ax, self)

    def area(self, x, y, **kwargs) -> FigureWrapper:
        """绘制面积图"""
        self._ensure_figure()
        alpha = kwargs.pop('alpha', 0.3)
        (line,) = self._ax.plot(x, y, **kwargs)
        color = line.get_color()
        self._ax.fill_between(x, y, alpha=alpha, color=color)
        return FigureWrapper(self._fig, self._ax, self)


class FigureWrapper(PlotResult):
    """Fluent API 返回类型，基于 PlotResult 扩展。"""

    def __init__(self, fig: Figure, ax: Axes, chain: PlotChain):
        super().__init__(fig, ax, metadata={"venue": chain._venue, "palette": chain._palette})
        self._chain = chain

    def get_figure(self) -> Figure:
        """获取 Figure 对象（用于进一步自定义）"""
        return self.fig

    def get_axes(self) -> Axes:
        """获取 Axes 对象（用于进一步自定义）"""
        return self.ax

    def unwrap(self) -> Tuple[Figure, Axes]:
        """解包为 (fig, ax) 元组"""
        return self.fig, self.ax


# ═══════════════════════════════════════════════════════════════
# 便捷入口函数
# ═══════════════════════════════════════════════════════════════

def style(venue: str) -> PlotChain:
    """
    链式调用入口 - 设置期刊样式

    参数:
        venue: 期刊样式，如 "nature", "ieee", "thesis" 等

    返回:
        PlotChain 对象支持链式调用

    示例:
        >>> import sciplot as sp
        >>> fig = sp.style("nature").palette("pastel").plot(x, y).save("output")
    """
    return PlotChain(venue=venue)


def palette(palette: str) -> PlotChain:
    """
    链式调用入口 - 设置配色方案

    参数:
        palette: 配色名称，如 "pastel", "earth", "100yuan" 等

    返回:
        PlotChain 对象支持链式调用

    示例:
        >>> fig = sp.palette("earth").plot(x, y).save("output")
    """
    return PlotChain(palette=palette)


def chain(
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
) -> PlotChain:
    """
    链式调用入口 - 通用入口

    参数:
        venue: 期刊样式
        palette: 配色方案
        lang: 语言设置

    返回:
        PlotChain 对象支持链式调用

    示例:
        >>> fig = sp.chain("ieee", "earth").plot(x, y).save("output")
    """
    return PlotChain(venue=venue, palette=palette, lang=lang)


__all__ = [
    "PlotChain",
    "FigureWrapper",
    "style",
    "palette",
    "chain",
]
