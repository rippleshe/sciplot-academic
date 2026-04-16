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

from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import copy

import matplotlib.pyplot as plt
from matplotlib import rcParams

from sciplot._core.style import setup_style, VENUES
from sciplot._core.palette import apply_palette


class StyleContext:
    """
    样式上下文管理器
    
    保存进入上下文前的样式状态，退出时自动恢复。
    支持嵌套使用，每层上下文独立管理自己的状态。
    """
    
    # 类级别的栈，用于支持嵌套上下文
    _context_stack: List[Dict[str, Any]] = []
    
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
        StyleContext._context_stack.append(self._saved_state)
        
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
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文，恢复之前的样式"""
        # 从栈中弹出当前状态
        if StyleContext._context_stack:
            saved_state = StyleContext._context_stack.pop()
            
            # 恢复 rcParams
            # 先清空当前设置，再恢复保存的状态
            for key in list(rcParams.keys()):
                if key in saved_state:
                    try:
                        rcParams[key] = saved_state[key]
                    except Exception:
                        # 某些参数可能无法恢复，忽略错误
                        pass
                else:
                    # 如果参数是新添加的，尝试删除
                    try:
                        del rcParams[key]
                    except Exception:
                        pass
            
            # 确保所有保存的参数都被恢复
            for key, value in saved_state.items():
                try:
                    rcParams[key] = value
                except Exception:
                    pass
        
        # 清理
        self._saved_state = None
        
        # 不吞掉异常
        return False
    
    @classmethod
    def get_current_context(cls) -> Optional[StyleContext]:
        """获取当前活动的上下文（如果有）"""
        # 这个方法可以用于检查当前是否在上下文中
        # 以及获取当前上下文的设置
        if cls._context_stack:
            return cls
        return None
    
    @classmethod
    def is_in_context(cls) -> bool:
        """检查当前是否在样式上下文中"""
        return len(cls._context_stack) > 0


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

def ieee_context(palette: Optional[str] = None, **kwargs) -> StyleContext:
    """IEEE 样式上下文"""
    return StyleContext("ieee", palette or "pastel", **kwargs)


def nature_context(palette: Optional[str] = None, **kwargs) -> StyleContext:
    """Nature 样式上下文"""
    return StyleContext("nature", palette or "pastel", **kwargs)


def thesis_context(palette: Optional[str] = None, **kwargs) -> StyleContext:
    """学位论文样式上下文"""
    return StyleContext("thesis", palette or "pastel", **kwargs)


__all__ = [
    "StyleContext",
    "style_context",
    "context",
    "ieee_context",
    "nature_context",
    "thesis_context",
]
