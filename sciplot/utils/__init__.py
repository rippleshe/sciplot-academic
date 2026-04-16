"""
工具函数 — 颜色处理、Axes 便利操作
"""

from __future__ import annotations

from typing import List, Tuple


# ============================================================================
# 颜色处理工具
# ============================================================================

def hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
    """
    HEX 颜色转 RGB（0-1 浮点范围）

    示例:
        >>> hex_to_rgb("#cdb4db")
        (0.804, 0.706, 0.859)
    """
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"无效 HEX 颜色: '{hex_color}'")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return r / 255.0, g / 255.0, b / 255.0


def rgb_to_hex(r: float, g: float, b: float) -> str:
    """
    RGB（0-1 浮点）转 HEX 颜色字符串

    示例:
        >>> rgb_to_hex(0.8, 0.5, 0.3)
        '#cc7f4d'
    """
    return "#{:02x}{:02x}{:02x}".format(
        int(r * 255), int(g * 255), int(b * 255)
    )


def lighten_color(hex_color: str, amount: float = 0.3) -> str:
    """
    将颜色变浅（混入白色）

    参数:
        hex_color: 原始 HEX 颜色
        amount   : 变浅幅度，0-1，越大越浅；默认 0.3

    示例:
        >>> lighten_color("#264653", 0.4)
        '#6f8b96'
    """
    r, g, b = hex_to_rgb(hex_color)
    r = r + (1 - r) * amount
    g = g + (1 - g) * amount
    b = b + (1 - b) * amount
    return rgb_to_hex(r, g, b)


def darken_color(hex_color: str, amount: float = 0.3) -> str:
    """
    将颜色加深（混入黑色）

    参数:
        hex_color: 原始 HEX 颜色
        amount   : 加深幅度，0-1，越大越深；默认 0.3

    示例:
        >>> darken_color("#cdb4db", 0.3)
        '#906f9a'
    """
    r, g, b = hex_to_rgb(hex_color)
    r = r * (1 - amount)
    g = g * (1 - amount)
    b = b * (1 - amount)
    return rgb_to_hex(r, g, b)


def generate_gradient(
    start: str,
    end: str,
    n: int,
) -> List[str]:
    """
    在两个颜色之间生成 n 步渐变色列表

    参数:
        start: 起始 HEX 颜色
        end  : 终止 HEX 颜色
        n    : 生成颜色数量（包含首尾）

    示例:
        >>> colors = generate_gradient("#cdb4db", "#264653", 5)
        >>> sp.set_custom_palette(colors, name="custom_grad")
    """
    if n < 2:
        raise ValueError("n 至少为 2")
    r1, g1, b1 = hex_to_rgb(start)
    r2, g2, b2 = hex_to_rgb(end)
    result = []
    for i in range(n):
        t = i / (n - 1)
        result.append(rgb_to_hex(
            r1 + (r2 - r1) * t,
            g1 + (g2 - g1) * t,
            b1 + (b2 - b1) * t,
        ))
    return result


# 从 smart 模块导入智能辅助功能
from sciplot.utils.smart import (
    auto_rotate_labels,
    smart_legend,
    optimize_layout,
    adjust_subplots,
    suggest_figsize,
    check_color_contrast,
)

__all__ = [
    # 颜色工具
    "hex_to_rgb",
    "rgb_to_hex",
    "lighten_color",
    "darken_color",
    "generate_gradient",
    # 智能辅助
    "auto_rotate_labels",
    "smart_legend",
    "optimize_layout",
    "adjust_subplots",
    "suggest_figsize",
    "check_color_contrast",
]
