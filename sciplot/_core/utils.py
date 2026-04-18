"""
公共工具函数 — 样式解析、输入验证等

提供各模块共用的工具函数，避免代码重复。
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, Tuple, Union, List, Any, overload, TypeVar, Dict

import numpy as np
from numpy.typing import ArrayLike

K = TypeVar("K")
V = TypeVar("V")


def resolve_style_venue(
    venue: Optional[str],
    palette: Optional[str],
    default_venue: str = "nature",
    default_palette: str = "pastel",
) -> Tuple[Optional[str], bool]:
    """
    解析并应用样式参数。

    此函数用于统一处理各绘图函数的 venue/palette 参数，
    决定是否需要应用新样式或复用当前 rcParams。

    参数:
        venue: 期刊样式，如 "nature", "ieee", "thesis" 等
        palette: 配色方案，如 "pastel", "earth", "100yuan" 等
        default_venue: 默认期刊样式
        default_palette: 默认配色方案

    返回:
        Tuple[Optional[str], bool]:
            - 第一个元素：应使用的 venue（None 表示复用当前样式）
            - 第二个元素：是否需要应用样式

    使用示例:
        >>> effective_venue, should_apply = resolve_style_venue(venue, palette)
        >>> if should_apply:
        ...     setup_style(effective_venue, effective_palette)
        >>> fig, ax = new_figure(effective_venue)
    """
    if venue is None and palette is None:
        from sciplot._core.context import StyleContext
        if StyleContext.is_in_context():
            return None, False

    effective_venue = venue or default_venue
    effective_palette = palette or default_palette
    return effective_venue, True


def apply_resolved_style(
    venue: Optional[str],
    palette: Optional[str],
) -> Optional[str]:
    """
    解析并应用样式（便捷函数）。

    自动调用 setup_style 应用样式，返回应使用的 venue。

    参数:
        venue: 期刊样式
        palette: 配色方案

    返回:
        应使用的 venue（None 表示复用当前样式）
    """
    effective_venue, should_apply = resolve_style_venue(venue, palette)
    if should_apply:
        from sciplot._core.style import setup_style
        from sciplot._core.palette import DEFAULT_PALETTE
        effective_palette = palette or DEFAULT_PALETTE
        setup_style(effective_venue, effective_palette)
    return effective_venue


# ═══════════════════════════════════════════════════════════════
# 输入验证工具
# ═══════════════════════════════════════════════════════════════

def validate_array_like(
    data: Union[ArrayLike, Sequence[Any]],
    name: str,
    min_length: Optional[int] = None,
    allow_empty: bool = False,
) -> List[Any]:
    """
    验证输入是否为类数组结构。

    参数:
        data: 待验证的数据
        name: 参数名称（用于错误提示）
        min_length: 最小长度要求（必须为非负整数）
        allow_empty: 是否允许空数组

    返回:
        转换为列表的数据

    抛出:
        TypeError: data 为 None 或 min_length 类型错误时
        ValueError: 验证失败时
    """
    if data is None:
        raise TypeError(f"参数 '{name}' 不能为 None")

    if min_length is not None:
        if not isinstance(min_length, int) or min_length < 0:
            raise ValueError(
                f"min_length 必须为非负整数，实际值: {min_length!r}"
            )

    if isinstance(data, np.ndarray):
        result = data.tolist()
    elif isinstance(data, (list, tuple)):
        result = list(data)
    else:
        try:
            result = list(data)  # type: ignore
        except TypeError:
            raise TypeError(
                f"参数 '{name}' 必须是数组类型，实际类型: {type(data).__name__}"
            )

    if not allow_empty and len(result) == 0:
        raise ValueError(f"参数 '{name}' 不能为空数组")

    if min_length is not None and len(result) < min_length:
        raise ValueError(
            f"参数 '{name}' 长度不能小于 {min_length}，实际长度: {len(result)}"
        )

    return result


def validate_labels_match_data(
    labels: Optional[List[str]],
    data_list: List[Any],
    name_labels: str = "labels",
    name_data: str = "y_list",
) -> List[str]:
    """
    验证标签与数据长度匹配。

    参数:
        labels: 标签列表（None 则自动生成）
        data_list: 数据列表
        name_labels: 标签参数名
        name_data: 数据参数名

    返回:
        标签列表（自动生成或验证后的）

    抛出:
        ValueError: 长度不匹配时
    """
    n = len(data_list)

    if labels is None:
        return [f"Series {i + 1}" for i in range(n)]

    if len(labels) != n:
        raise ValueError(
            f"{name_labels} 长度 ({len(labels)}) 与 {name_data} 长度 ({n}) 不一致"
        )

    return labels


def validate_positive_number(
    value: Any,
    name: str,
    allow_zero: bool = False,
) -> float:
    """
    验证数值为正数。

    参数:
        value: 待验证的值
        name: 参数名称
        allow_zero: 是否允许零

    返回:
        转换为浮点数的值

    抛出:
        ValueError: 验证失败时
    """
    try:
        num = float(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"参数 '{name}' 必须是数值类型，实际值: {value!r}"
        )

    if allow_zero:
        if num < 0:
            raise ValueError(f"参数 '{name}' 必须为非负数，实际值: {num}")
    else:
        if num <= 0:
            raise ValueError(f"参数 '{name}' 必须为正数，实际值: {num}")

    return num


def validate_choice(
    value: Any,
    choices: List[str],
    name: str,
    case_sensitive: bool = False,
) -> str:
    """
    验证值在允许的选项中。

    参数:
        value: 待验证的值
        choices: 允许的选项列表
        name: 参数名称
        case_sensitive: 是否区分大小写

    返回:
        验证后的值（可能已转换大小写）

    抛出:
        TypeError: value 为 None 时
        ValueError: 值不在选项中时
    """
    if value is None:
        raise TypeError(f"参数 '{name}' 不能为 None")

    str_value = str(value)

    if not case_sensitive:
        str_value_lower = str_value.lower()
        choices_lower = [c.lower() for c in choices]
        if str_value_lower in choices_lower:
            idx = choices_lower.index(str_value_lower)
            return choices[idx]
    else:
        if str_value in choices:
            return str_value

    raise ValueError(
        f"参数 '{name}' 的值 '{value}' 无效。\n"
        f"可用选项: {choices}"
    )


def validate_dict_not_empty(
    data: Dict[K, V],
    name: str,
) -> Dict[K, V]:
    """
    验证字典不为空。

    参数:
        data: 待验证的字典
        name: 参数名称

    返回:
        验证后的字典

    抛出:
        TypeError: data 不是字典类型时
        ValueError: 字典为空时
    """
    if not isinstance(data, dict):
        raise TypeError(
            f"参数 '{name}' 必须是字典类型，实际类型: {type(data).__name__}"
        )

    if not data:
        raise ValueError(f"参数 '{name}' 不能为空字典")

    return data


__all__ = [
    "resolve_style_venue",
    "apply_resolved_style",
    "validate_array_like",
    "validate_labels_match_data",
    "validate_positive_number",
    "validate_choice",
    "validate_dict_not_empty",
]
