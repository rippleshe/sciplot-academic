"""
上下文管理器 — 临时样式切换

支持临时切换样式，退出上下文时自动恢复之前的样式设置。

示例:
    >>> import sciplot as sp
    >>>
    >>> # 基础用法
    >>> with sp.style_context("ieee", palette="earth"):
    ...     fig, ax = sp.plot(x, y)  # 使用 ieee + earth
    >>> # 退出后恢复默认

    >>> # 只修改部分参数
    >>> with sp.style_context(palette="100yuan"):
    ...     fig, ax = sp.plot(x, y)  # 只改配色

    >>> # 嵌套使用
    >>> with sp.style_context("nature"):
    ...     fig1, ax1 = sp.plot(x, y)  # nature 样式
    ...     with sp.style_context("ieee"):
    ...         fig2, ax2 = sp.plot(x, y)  # ieee 样式
    ...     fig3, ax3 = sp.plot(x, y)  # 恢复 nature 样式
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any, Literal
from contextlib import contextmanager
from types import TracebackType
import copy
import threading
import logging

import matplotlib.pyplot as plt
from matplotlib import rcParams

from sciplot._core.style import setup_style, VENUES
from sciplot._core.palette import apply_palette

_logger = logging.getLogger(__name__)


class StyleContext:
    """
    样式上下文管理器

    保存进入上下文前的样式状态，退出时自动恢复。
    支持嵌套使用，每层上下文独立管理自己的状态。
    线程安全：使用 threading.local() 实现线程隔离。
    """

    _local = threading.local()

    @classmethod
    def _get_stack(cls) -> List[Dict[str, Any]]:
        """获取当前线程的上下文栈"""
        if not hasattr(cls._local, "stack"):
            cls._local.stack = []
        return cls._local.stack

    def __init__(
        self,
        venue: Optional[str] = None,
        palette: Optional[str] = None,
        lang: Optional[str] = None,
        **rc_params: Any,
    ):
        """
        初始化样式上下文

        参数:
            venue: 期刊样式，如 "nature", "ieee", "thesis" 等
            palette: 配色方案，如 "pastel", "earth", "100yuan" 等
            lang: 语言设置，"zh" 或 "en"
            **rc_params: 其他 matplotlib rcParams 参数

        示例:
            >>> with StyleContext("ieee", palette="earth"):
            ...     fig, ax = sp.plot(x, y)
        """
        self.venue = venue
        self.palette = palette
        self.lang = lang
        self.rc_params = rc_params

        # 保存进入上下文前的状态
        self._saved_state: Optional[Dict[str, Any]] = None

    def __enter__(self) -> StyleContext:
        """进入上下文，保存当前状态并应用新样式"""
        # 保存当前 rcParams 的副本
        self._saved_state = copy.deepcopy(dict(rcParams))

        # 将当前状态压入栈
        stack = self._get_stack()
        stack.append(self._saved_state)

        try:
            # 应用新样式
            has_explicit_style = any(v is not None for v in (self.venue, self.palette, self.lang))
            if has_explicit_style:
                # 仅指定了 palette：不重置 venue/lang，只覆盖颜色循环
                if self.venue is None and self.lang is None and self.palette is not None:
                    apply_palette(self.palette)
                else:
                    setup_style(
                        venue=self.venue or "nature",
                        palette=self.palette or "pastel",
                        lang=self.lang if self.lang is not None else "zh",
                    )

            # 应用额外的 rcParams
            if self.rc_params:
                plt.rcParams.update(self.rc_params)
        except Exception:
            # __enter__ 失败时必须回滚全局样式并清理上下文栈，避免“悬挂上下文”。
            rcParams.update(self._saved_state)
            if stack and stack[-1] is self._saved_state:
                stack.pop()
            self._saved_state = None
            raise

        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Literal[False]:
        """
        退出上下文，恢复之前的样式

        参数:
            exc_type: 异常类型（如果有异常）
            exc_val: 异常值
            exc_tb: 异常回溯

        返回:
            False - 不抑制任何异常
        """
        stack = self._get_stack()
        if stack:
            saved_state = stack.pop()

            keys_to_delete = []
            for key in list(rcParams.keys()):
                if key not in saved_state:
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                try:
                    del rcParams[key]
                except (KeyError, ValueError) as e:
                    _logger.debug(f"无法删除 rcParams[{key!r}]: {e}")

            for key, value in saved_state.items():
                try:
                    rcParams[key] = value
                except (ValueError, KeyError) as e:
                    _logger.warning(f"无法恢复 rcParams[{key!r}]: {e}")

        self._saved_state = None

        return False

    @classmethod
    def get_current_context(cls) -> Optional[StyleContext]:
        """获取当前活动的上下文（如果有）"""
        if cls._get_stack():
            return cls
        return None

    @classmethod
    def is_in_context(cls) -> bool:
        """检查当前是否在样式上下文中"""
        return len(cls._get_stack()) > 0


# ═══════════════════════════════════════════════════════════════
# 便捷入口函数
# ═══════════════════════════════════════════════════════════════

def style_context(
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **rc_params: Any,
) -> StyleContext:
    """
    样式上下文管理器入口

    临时切换样式，退出时自动恢复。

    参数:
        venue: 期刊样式，如 "nature", "ieee", "thesis" 等
        palette: 配色方案，如 "pastel", "earth", "100yuan" 等
        lang: 语言设置，"zh" 或 "en"
        **rc_params: 其他 matplotlib rcParams 参数

    返回:
        StyleContext 上下文管理器

    示例:
        >>> import sciplot as sp
        >>>
        >>> # 基础用法
        >>> with sp.style_context("ieee", palette="earth"):
        ...     fig, ax = sp.plot(x, y)
        >>> # 退出后恢复默认

        >>> # 只修改配色
        >>> with sp.style_context(palette="100yuan"):
        ...     fig, ax = sp.plot(x, y)

        >>> # 自定义 rcParams
        >>> with sp.style_context(fontsize=14, linewidth=2):
        ...     fig, ax = sp.plot(x, y)
    """
    return StyleContext(venue, palette, lang, **rc_params)


# 别名，更短的名称
def context(
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **rc_params: Any,
) -> StyleContext:
    """
    style_context 的简写别名

    示例:
        >>> with sp.context("ieee"):
        ...     fig, ax = sp.plot(x, y)
    """
    return StyleContext(venue, palette, lang, **rc_params)


# 特定场景的便捷上下文

def ieee_context(
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> StyleContext:
    """
    IEEE 样式上下文

    参数:
        palette: 配色方案，默认 "pastel"
        lang: 语言设置，"zh" 或 "en"
        **kwargs: 其他 matplotlib rcParams 参数

    返回:
        StyleContext 上下文管理器

    示例:
        >>> with sp.ieee_context("earth"):
        ...     fig, ax = sp.plot(x, y)
    """
    return StyleContext("ieee", palette or "pastel", lang=lang, **kwargs)


def nature_context(
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> StyleContext:
    """
    Nature 样式上下文

    参数:
        palette: 配色方案，默认 "pastel"
        lang: 语言设置，"zh" 或 "en"
        **kwargs: 其他 matplotlib rcParams 参数

    返回:
        StyleContext 上下文管理器

    示例:
        >>> with sp.nature_context("earth"):
        ...     fig, ax = sp.plot(x, y)
    """
    return StyleContext("nature", palette or "pastel", lang=lang, **kwargs)


def thesis_context(
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> StyleContext:
    """
    学位论文样式上下文

    参数:
        palette: 配色方案，默认 "pastel"
        lang: 语言设置，"zh" 或 "en"
        **kwargs: 其他 matplotlib rcParams 参数

    返回:
        StyleContext 上下文管理器

    示例:
        >>> with sp.thesis_context("earth"):
        ...     fig, ax = sp.plot(x, y)
    """
    return StyleContext("thesis", palette or "pastel", lang=lang, **kwargs)


__all__ = [
    "StyleContext",
    "style_context",
    "context",
    "ieee_context",
    "nature_context",
    "thesis_context",
]
