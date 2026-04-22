"""
绘图结果封装 — 增强的返回类型系统

提供统一的 PlotResult 类，支持：
- 元组解包: fig, ax = result
- 属性访问: result.fig, result.ax
- 链式调用: result.xlabel("X").ylabel("Y").save("fig")
- 自动完成友好的 API
"""

from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union, overload, Literal, Sequence, cast
import warnings

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
import numpy as np

from sciplot._core.layout import save as _save


class PlotResult:
    """
    绘图结果封装类

    统一包装 (Figure, Axes) 返回结果，提供：
    1. 元组解包兼容性: fig, ax = result
    2. 属性访问: result.fig, result.ax
    3. 链式调用支持
    4. 便捷的保存和显示方法

    示例:
        >>> # 传统用法（仍然支持）
        >>> fig, ax = sp.plot(x, y)

        >>> # 属性访问
        >>> result = sp.plot(x, y)
        >>> result.fig.savefig("fig.pdf")
        >>> result.ax.set_xlabel("X")

        >>> # 链式调用
        >>> sp.plot(x, y).xlabel("X").ylabel("Y").save("fig")

        >>> # 多子图支持
        >>> result = sp.paper_subplots(1, 2)
        >>> result.axes[0].plot(x, y)
        >>> result.axes[1].plot(x, y2)
    """

    def __init__(
        self,
        fig: Figure,
        ax: Union[Axes, np.ndarray],
        metadata: Optional[Dict[str, Any]] = None,
        auto_close: bool = False,
    ):
        self._fig = fig
        self._ax = ax
        self._metadata = metadata or {}
        self._is_array = isinstance(ax, np.ndarray)
        self._auto_close = auto_close

    def _get_target_ax(self, ax_index: int = 0) -> Axes:
        """根据 ax_index 获取目标子图，单子图时忽略索引。"""
        if not self._is_array:
            return cast(Axes, self._ax)

        flat_axes = list(cast(np.ndarray, self._ax).flat)
        if ax_index < 0 or ax_index >= len(flat_axes):
            raise IndexError(
                f"ax_index 超出范围: {ax_index}，可用范围 [0, {len(flat_axes) - 1}]"
            )
        return flat_axes[ax_index]

    # ═══════════════════════════════════════════════════════════════
    # 属性访问
    # ═══════════════════════════════════════════════════════════════

    @property
    def fig(self) -> Figure:
        """获取 Figure 对象"""
        return self._fig

    @property
    def figure(self) -> Figure:
        """获取 Figure 对象（别名）"""
        return self._fig

    @property
    def ax(self) -> Axes:
        """获取 Axes 对象（单个子图时）"""
        if self._is_array:
            ax_arr = cast(np.ndarray, self._ax)
            if ax_arr.size == 1:
                return cast(Axes, ax_arr.flat[0])
            raise AttributeError(
                f"此结果包含 {ax_arr.size} 个子图（形状 {ax_arr.shape}），"
                "请使用 result.axes 或 result.ax_array 访问。"
            )
        return cast(Axes, self._ax)

    @property
    def axes(self) -> Union[Axes, np.ndarray]:
        """获取 Axes 对象或数组"""
        return self._ax

    @property
    def ax_array(self) -> np.ndarray:
        """获取 Axes 数组（多子图时）"""
        if not self._is_array:
            raise AttributeError("单个子图请使用 result.ax 访问")
        return cast(np.ndarray, self._ax)

    @property
    def metadata(self) -> Dict[str, Any]:
        """获取结果元数据副本。"""
        return dict(self._metadata)

    # ═══════════════════════════════════════════════════════════════
    # 元组解包支持
    # ═══════════════════════════════════════════════════════════════

    def __iter__(self) -> Iterator[Union[Figure, Union[Axes, np.ndarray]]]:
        """支持元组解包: fig, ax = result"""
        yield self._fig
        yield self._ax

    def __len__(self) -> int:
        """返回元素数量（始终为2）"""
        return 2

    @overload
    def __getitem__(self, index: int) -> Union[Figure, Axes]: ...

    @overload
    def __getitem__(self, index: slice) -> Tuple[Any, ...]: ...

    def __getitem__(self, index: Union[int, slice]) -> Union[Figure, Union[Axes, np.ndarray], Tuple[Any, ...]]:
        """支持索引访问: result[0], result[1]"""
        if index == 0:
            return self._fig
        elif index == 1:
            return self._ax
        elif isinstance(index, slice):
            return (self._fig, self._ax)[index]
        else:
            raise IndexError("PlotResult 只支持索引 0 (fig) 和 1 (ax)")

    # ═══════════════════════════════════════════════════════════════
    # 链式调用方法（单个子图时）
    # ═══════════════════════════════════════════════════════════════

    def xlabel(self, label: str, **kwargs: Any) -> PlotResult:
        """设置 X 轴标签"""
        if self._is_array:
            for ax in self._ax.flat:
                ax.set_xlabel(label, **kwargs)
        else:
            self._ax.set_xlabel(label, **kwargs)
        return self

    def ylabel(self, label: str, **kwargs: Any) -> PlotResult:
        """设置 Y 轴标签"""
        if self._is_array:
            for ax in self._ax.flat:
                ax.set_ylabel(label, **kwargs)
        else:
            self._ax.set_ylabel(label, **kwargs)
        return self

    def title(self, title: str, **kwargs: Any) -> PlotResult:
        """设置标题"""
        if self._is_array:
            self._fig.suptitle(title, **kwargs)
        else:
            self._ax.set_title(title, **kwargs)
        return self

    def suptitle(self, title: str, **kwargs: Any) -> PlotResult:
        """设置图形总标题"""
        self._fig.suptitle(title, **kwargs)
        return self

    def xlim(self, left: Optional[float] = None, right: Optional[float] = None) -> PlotResult:
        """设置 X 轴范围"""
        if self._is_array:
            for ax in self._ax.flat:
                ax.set_xlim(left, right)
        else:
            self._ax.set_xlim(left, right)
        return self

    def ylim(self, bottom: Optional[float] = None, top: Optional[float] = None) -> PlotResult:
        """设置 Y 轴范围"""
        if self._is_array:
            for ax in self._ax.flat:
                ax.set_ylim(bottom, top)
        else:
            self._ax.set_ylim(bottom, top)
        return self

    def legend(self, **kwargs: Any) -> PlotResult:
        """添加图例"""
        if self._is_array:
            for ax in self._ax.flat:
                if ax.get_legend_handles_labels()[0]:
                    ax.legend(**kwargs)
        else:
            self._ax.legend(**kwargs)
        return self

    def grid(self, visible: bool = True, **kwargs: Any) -> PlotResult:
        """设置网格"""
        if self._is_array:
            for ax in self._ax.flat:
                ax.grid(visible, **kwargs)
        else:
            self._ax.grid(visible, **kwargs)
        return self

    def tick_params(self, **kwargs: Any) -> PlotResult:
        """设置刻度参数，默认刻度朝内。"""
        kwargs.setdefault("direction", "in")
        if self._is_array:
            for ax in self._ax.flat:
                ax.tick_params(**kwargs)
        else:
            self._ax.tick_params(**kwargs)
        return self

    def tight_layout(self, **kwargs: Any) -> PlotResult:
        """自动调整布局"""
        self._fig.tight_layout(**kwargs)
        return self

    # ═══════════════════════════════════════════════════════════════
    # 图层添加方法（单个子图时）
    # ═══════════════════════════════════════════════════════════════

    def plot(
        self,
        x: Union[List[float], np.ndarray],
        y: Union[List[float], np.ndarray],
        ax_index: int = 0,
        **kwargs: Any,
    ) -> PlotResult:
        """添加折线；多子图时可通过 ax_index 指定目标子图。"""
        target_ax = self._get_target_ax(ax_index)
        target_ax.plot(x, y, **kwargs)
        return self

    def scatter(
        self,
        x: Union[List[float], np.ndarray],
        y: Union[List[float], np.ndarray],
        ax_index: int = 0,
        **kwargs: Any,
    ) -> PlotResult:
        """添加散点；多子图时可通过 ax_index 指定目标子图。"""
        target_ax = self._get_target_ax(ax_index)
        target_ax.scatter(x, y, **kwargs)
        return self

    def axhline(self, y: float, **kwargs: Any) -> PlotResult:
        """添加水平线"""
        if self._is_array:
            for ax in self._ax.flat:
                ax.axhline(y, **kwargs)
        else:
            self._ax.axhline(y, **kwargs)
        return self

    def axvline(self, x: float, **kwargs: Any) -> PlotResult:
        """添加垂直线"""
        if self._is_array:
            for ax in self._ax.flat:
                ax.axvline(x, **kwargs)
        else:
            self._ax.axvline(x, **kwargs)
        return self

    def annotate(
        self,
        text: str,
        xy: Tuple[float, float],
        ax_index: int = 0,
        **kwargs: Any,
    ) -> PlotResult:
        """添加标注；多子图时可通过 ax_index 指定目标子图。"""
        target_ax = self._get_target_ax(ax_index)
        target_ax.annotate(text, xy, **kwargs)
        return self

    # ═══════════════════════════════════════════════════════════════
    # 最终操作
    # ═══════════════════════════════════════════════════════════════

    def save(
        self,
        name: str,
        dpi: Optional[Union[int, float]] = None,
        formats: Optional[Union[str, Sequence[str]]] = None,
        bbox_inches: str = "tight",
        dir: Optional[str] = None,
        tight: bool = True,
        **kwargs: Any,
    ) -> List[Path]:
        """
        保存图形

        参数:
            name: 文件名（不含扩展名）
            dpi: 分辨率；为 None 时读取配置默认值
            formats: 输出格式；为 None 时读取配置默认值
            bbox_inches: 边界处理，默认 "tight"
            dir: 保存目录
            tight: 是否自动调整布局，默认 True

        返回:
            保存的文件路径列表
        """
        if tight:
            try:
                self._fig.tight_layout()
            except ValueError as exc:
                warnings.warn(
                    f"tight_layout() 跳过: {exc}",
                    UserWarning,
                    stacklevel=2,
                )
            except Exception as exc:
                warnings.warn(f"tight_layout() 失败: {exc}", UserWarning, stacklevel=2)
        return _save(self._fig, name, dpi=dpi, formats=formats,
                     bbox_inches=bbox_inches, dir=dir, **kwargs)

    def show(self) -> None:
        """显示图形"""
        try:
            self._fig.tight_layout()
        except ValueError as exc:
            warnings.warn(
                f"tight_layout() 跳过: {exc}",
                UserWarning,
                stacklevel=2,
            )
        except Exception as exc:
            warnings.warn(f"tight_layout() 失败: {exc}", UserWarning, stacklevel=2)
        plt.show()

    def close(self) -> None:
        """关闭图形"""
        plt.close(self._fig)

    # ═══════════════════════════════════════════════════════════════
    # 便捷方法
    # ═══════════════════════════════════════════════════════════════

    def set_labels(self, xlabel: str = "", ylabel: str = "", title: str = "") -> PlotResult:
        """一次性设置 X/Y 标签和标题"""
        if xlabel:
            self.xlabel(xlabel)
        if ylabel:
            self.ylabel(ylabel)
        if title:
            self.title(title)
        return self

    def add_panel_labels(
        self,
        labels: Optional[List[str]] = None,
        style: str = "letter",
        x: float = -0.12,
        y: float = 1.05,
        **kwargs: Any,
    ) -> PlotResult:
        """
        为多子图添加面板标签 (a) (b) (c)...

        参数:
            labels: 自定义标签列表
            style: 标签样式 ('letter' | 'LETTER' | 'number' | 'roman')
            x, y: 标签位置（axes 坐标）
        """
        from sciplot._core.layout import add_panel_labels

        if self._is_array:
            add_panel_labels(self._ax, labels=labels, style=style, x=x, y=y, **kwargs)
        else:
            add_panel_labels([self._ax], labels=labels, style=style, x=x, y=y, **kwargs)
        return self

    # ═══════════════════════════════════════════════════════════════
    # 特殊方法
    # ═══════════════════════════════════════════════════════════════

    def __repr__(self) -> str:
        """字符串表示"""
        if self._is_array:
            return f"PlotResult(fig={self._fig!r}, axes=array{self._ax.shape})"
        return f"PlotResult(fig={self._fig!r}, ax={self._ax!r})"

    def __enter__(self) -> PlotResult:
        """支持上下文管理器"""
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Literal[False]:
        """退出上下文时根据 auto_close 设置决定是否关闭图形"""
        if self._auto_close:
            self.close()
        return False


class ComboPlotResult(PlotResult):
    """组合图结果，兼容 PlotResult 与三元组解包。"""

    def __init__(
        self,
        fig: Figure,
        ax_bar: Axes,
        ax_line: Optional[Axes] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(fig, ax_bar, metadata=metadata)
        self.ax_bar = ax_bar
        self.ax_line = ax_line

    @property
    def axes(self) -> Union[Axes, np.ndarray]:
        if self.ax_line is None:
            return self.ax_bar
        return np.array([self.ax_bar, self.ax_line], dtype=object)

    @property
    def ax_array(self) -> np.ndarray:
        if self.ax_line is None:
            raise AttributeError("单 Y 轴组合图没有 ax_array，请使用 result.ax 或 result.ax_bar")
        return np.array([self.ax_bar, self.ax_line], dtype=object)

    def __iter__(self) -> Iterator[Union[Figure, Optional[Axes]]]:
        """支持三元解包: fig, ax_bar, ax_line = result"""
        yield self._fig
        yield self.ax_bar
        yield self.ax_line

    def __len__(self) -> int:
        return 3

    @overload
    def __getitem__(self, index: int) -> Union[Figure, Optional[Axes]]: ...

    @overload
    def __getitem__(self, index: slice) -> Tuple[Any, ...]: ...

    def __getitem__(self, index: Union[int, slice]) -> Union[Figure, Optional[Axes], Tuple[Any, ...]]:
        values: Tuple[Figure, Axes, Optional[Axes]] = (self._fig, self.ax_bar, self.ax_line)
        if isinstance(index, slice):
            return values[index]
        if index in (0, 1, 2):
            return values[index]
        raise IndexError("ComboPlotResult 只支持索引 0 (fig)、1 (ax_bar)、2 (ax_line)")

    def ylabel_left(self, label: str, **kwargs: Any) -> ComboPlotResult:
        """设置左 Y 轴标签。"""
        self.ax_bar.set_ylabel(label, **kwargs)
        return self

    def ylabel_right(self, label: str, **kwargs: Any) -> ComboPlotResult:
        """设置右 Y 轴标签（仅双轴组合图生效）。"""
        if self.ax_line is not None:
            self.ax_line.set_ylabel(label, **kwargs)
        return self


class GridSpecResult:
    """
    GridSpec 结果封装

    包装 (Figure, GridSpec) 返回结果
    """

    def __init__(self, fig: Figure, gridspec: GridSpec):
        self._fig = fig
        self._gridspec = gridspec

    @property
    def fig(self) -> Figure:
        """获取 Figure 对象"""
        return self._fig

    @property
    def figure(self) -> Figure:
        """获取 Figure 对象（别名）"""
        return self._fig

    @property
    def gs(self) -> GridSpec:
        """获取 GridSpec 对象"""
        return self._gridspec

    @property
    def gridspec(self) -> GridSpec:
        """获取 GridSpec 对象（别名）"""
        return self._gridspec

    def add_subplot(self, *args: Any, **kwargs: Any) -> Axes:
        """添加子图"""
        return self._fig.add_subplot(*args, **kwargs)

    def __iter__(self) -> Iterator[Union[Figure, GridSpec]]:
        """支持元组解包: fig, gs = result"""
        yield self._fig
        yield self._gridspec

    def __len__(self) -> int:
        """返回元素数量（始终为2）"""
        return 2

    @overload
    def __getitem__(self, index: int) -> Union[Figure, GridSpec]: ...

    @overload
    def __getitem__(self, index: slice) -> Tuple[Any, ...]: ...

    def __getitem__(self, index: Union[int, slice]) -> Union[Figure, GridSpec, Tuple[Any, ...]]:
        """支持索引访问"""
        if index == 0:
            return self._fig
        elif index == 1:
            return self._gridspec
        elif isinstance(index, slice):
            return (self._fig, self._gridspec)[index]
        else:
            raise IndexError("GridSpecResult 只支持索引 0 (fig) 和 1 (gridspec)")

    def add_panel_labels(self, **kwargs: Any) -> GridSpecResult:
        """对当前 figure 的全部子图添加面板标签。"""
        from sciplot._core.layout import add_panel_labels

        add_panel_labels(self._fig.axes, **kwargs)
        return self

    def save(
        self,
        name: str,
        dpi: Optional[Union[int, float]] = None,
        formats: Optional[Union[str, Sequence[str]]] = None,
        tight: bool = True,
        **kwargs: Any,
    ) -> List[Path]:
        """保存图形"""
        if tight:
            try:
                self._fig.tight_layout()
            except ValueError as exc:
                warnings.warn(
                    f"tight_layout() 跳过: {exc}",
                    UserWarning,
                    stacklevel=2,
                )
            except Exception as exc:
                warnings.warn(f"tight_layout() 失败: {exc}", UserWarning, stacklevel=2)
        return _save(self._fig, name, dpi=dpi, formats=formats, **kwargs)

    def show(self) -> None:
        """显示图形"""
        try:
            self._fig.tight_layout()
        except ValueError as exc:
            warnings.warn(
                f"tight_layout() 跳过: {exc}",
                UserWarning,
                stacklevel=2,
            )
        except Exception as exc:
            warnings.warn(f"tight_layout() 失败: {exc}", UserWarning, stacklevel=2)
        plt.show()

    def __repr__(self) -> str:
        return f"GridSpecResult(fig={self._fig!r}, gridspec={self._gridspec!r})"


__all__ = [
    "PlotResult",
    "ComboPlotResult",
    "GridSpecResult",
]
