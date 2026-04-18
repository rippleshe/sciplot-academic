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

from sciplot._core.style import setup_style, reset_style
from sciplot._core.palette import apply_palette
from sciplot._core.layout import new_figure, save as _save


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
        self._venue = venue or "nature"
        self._palette = palette or "pastel"
        self._lang = lang
        self._figsize: Optional[Tuple[float, float]] = None
        self._fig: Optional[Figure] = None
        self._ax: Optional[Axes] = None
        self._style_applied = False

    def _apply_style(self) -> None:
        """应用当前样式设置"""
        if not self._style_applied:
            setup_style(self._venue, self._palette, self._lang)
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
        (line,) = self._ax.plot(x, y, **kwargs)
        color = line.get_color()
        alpha = kwargs.get('alpha', 0.3)
        self._ax.fill_between(x, y, alpha=alpha, color=color)
        return FigureWrapper(self._fig, self._ax, self)


class FigureWrapper:
    """
    图形包装器 - 支持继续添加图层和最终操作

    由 PlotChain 的绘图方法返回，支持：
    - 继续添加图层（plot, scatter 等）
    - 设置标签、标题、图例
    - 保存图形
    """

    def __init__(self, fig: Figure, ax: Axes, chain: PlotChain):
        self._fig = fig
        self._ax = ax
        self._chain = chain

    # ═══════════════════════════════════════════════════════════════
    # 继续添加图层（返回 self 支持链式调用）
    # ═══════════════════════════════════════════════════════════════

    def plot(self, x, y, **kwargs) -> FigureWrapper:
        """添加折线"""
        self._ax.plot(x, y, **kwargs)
        return self

    def scatter(self, x, y, **kwargs) -> FigureWrapper:
        """添加散点"""
        self._ax.scatter(x, y, **kwargs)
        return self

    def bar(self, x, height, **kwargs) -> FigureWrapper:
        """添加柱状图"""
        self._ax.bar(x, height, **kwargs)
        return self

    def fill_between(self, x, y1, y2=None, **kwargs) -> FigureWrapper:
        """填充区域"""
        if y2 is None:
            y2 = 0
        self._ax.fill_between(x, y1, y2, **kwargs)
        return self

    def errorbar(self, x, y, yerr=None, xerr=None, **kwargs) -> FigureWrapper:
        """添加误差线"""
        self._ax.errorbar(x, y, yerr=yerr, xerr=xerr, **kwargs)
        return self

    def axhline(self, y, **kwargs) -> FigureWrapper:
        """添加水平线"""
        self._ax.axhline(y, **kwargs)
        return self

    def axvline(self, x, **kwargs) -> FigureWrapper:
        """添加垂直线"""
        self._ax.axvline(x, **kwargs)
        return self

    def annotate(self, text, xy, **kwargs) -> FigureWrapper:
        """添加标注"""
        self._ax.annotate(text, xy, **kwargs)
        return self

    # ═══════════════════════════════════════════════════════════════
    # 设置方法（返回 self 支持链式调用）
    # ═══════════════════════════════════════════════════════════════

    def xlabel(self, label: str, **kwargs) -> FigureWrapper:
        """设置 X 轴标签"""
        self._ax.set_xlabel(label, **kwargs)
        return self

    def ylabel(self, label: str, **kwargs) -> FigureWrapper:
        """设置 Y 轴标签"""
        self._ax.set_ylabel(label, **kwargs)
        return self

    def title(self, title: str, **kwargs) -> FigureWrapper:
        """设置标题"""
        self._ax.set_title(title, **kwargs)
        return self

    def xlim(self, left: Optional[float] = None, right: Optional[float] = None) -> FigureWrapper:
        """设置 X 轴范围"""
        self._ax.set_xlim(left, right)
        return self

    def ylim(self, bottom: Optional[float] = None, top: Optional[float] = None) -> FigureWrapper:
        """设置 Y 轴范围"""
        self._ax.set_ylim(bottom, top)
        return self

    def legend(self, **kwargs) -> FigureWrapper:
        """添加图例"""
        self._ax.legend(**kwargs)
        return self

    def grid(self, visible: bool = True, **kwargs) -> FigureWrapper:
        """设置网格"""
        self._ax.grid(visible, **kwargs)
        return self

    def tight_layout(self) -> FigureWrapper:
        """自动调整布局"""
        self._fig.tight_layout()
        return self

    # ═══════════════════════════════════════════════════════════════
    # 最终操作（返回结果，结束链式调用）
    # ═══════════════════════════════════════════════════════════════

    def save(self, name: str, *, dpi: int = 1200, **kwargs):
        """
        保存图形

        参数:
            name: 文件名（不含扩展名）
            dpi: 分辨率，默认 1200（印刷级）
            **kwargs: 传递给 savefig 的其他参数

        返回:
            保存的文件路径列表

        示例:
            >>> sp.plot(x, y).save("figure", dpi=600)
        """
        self._fig.tight_layout()
        paths = _save(self._fig, name, dpi=dpi, **kwargs)
        return paths

    def show(self) -> None:
        """显示图形"""
        self._fig.tight_layout()
        plt.show()

    def get_figure(self) -> Figure:
        """获取 Figure 对象（用于进一步自定义）"""
        return self._fig

    def get_axes(self) -> Axes:
        """获取 Axes 对象（用于进一步自定义）"""
        return self._ax

    def unwrap(self) -> Tuple[Figure, Axes]:
        """解包为 (fig, ax) 元组"""
        return self._fig, self._ax


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
