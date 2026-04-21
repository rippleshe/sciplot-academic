"""
类型定义模块 — 共享类型别名和类型变量

提供项目中使用的类型别名，增强代码可读性和类型检查。
"""

from __future__ import annotations

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)

import numpy as np
from numpy.typing import ArrayLike, NDArray

# ═══════════════════════════════════════════════════════════════
# 基础类型别名
# ═══════════════════════════════════════════════════════════════

# 数值类型变量（用于泛型）
NumberType = TypeVar("NumberType", int, float, np.number)

# 数组类型 - 使用泛型支持更广泛的数值类型
Array = Union[List[NumberType], Tuple[NumberType, ...], np.ndarray]
# 更宽泛的数值数组类型，接受所有 numpy 数值类型
NumericArray = NDArray[np.number]
IntArray = NDArray[np.integer]
BoolArray = NDArray[np.bool_]

# 可选数组
OptionalArray = Optional[Union[ArrayLike, Sequence[float]]]

# ═══════════════════════════════════════════════════════════════
# 图表相关类型
# ═══════════════════════════════════════════════════════════════

# 期刊样式类型
VenueType = Literal["nature", "ieee", "aps", "springer", "thesis", "presentation"]

# 语言类型
LangType = Literal["zh", "zh-cn", "en"]

# 内置配色方案类型（包含子集）
BuiltinPaletteType = Literal[
    # 常驻系列
    "pastel", "pastel-1", "pastel-2", "pastel-3", "pastel-4", "pastel-5", "pastel-6",
    "earth", "earth-1", "earth-2", "earth-3", "earth-4",
    "ocean", "ocean-1", "ocean-2", "ocean-3", "ocean-4", "ocean-5", "ocean-6",
    "forest", "forest-1", "forest-2", "forest-3", "forest-4", "forest-5", "forest-6",
    "sunset", "sunset-1", "sunset-2", "sunset-3", "sunset-4", "sunset-5",
    # 人民币系列
    "100yuan", "50yuan", "20yuan", "10yuan", "5yuan", "1yuan",
    # 发散配色
    "rdbu", "coolwarm",
]

# 运行时可接受任意字符串（支持用户自定义配色名称）
PaletteType = str

# 颜色映射类型
CmapType = Literal[
    "viridis", "plasma", "inferno", "magma", "cividis",
    "Blues", "Greens", "Oranges", "Reds", "Purples",
    "RdBu_r", "RdYlBu", "RdYlGn", "Spectral",
    "seismic", "coolwarm", "bwr",
    "terrain", "ocean", "jet", "rainbow",
]

# 线型类型
LineStyleType = Literal["-", "--", "-.", ":", "solid", "dashed", "dashdot", "dotted"]

# 标记类型
MarkerType = Literal[
    "o", "s", "^", "D", "v", "<", ">", "p", "*", "h", "H", "+", "x", "X", "d", "|", "_",
    ".", ",", "1", "2", "3", "4", "8",
]

# 图例位置类型
LegendLocType = Literal[
    "best", "upper right", "upper left", "lower left", "lower right",
    "right", "center left", "center right", "lower center", "upper center", "center",
]

# 对齐方式类型
AlignType = Literal["left", "center", "right"]
VaAlignType = Literal["top", "center", "bottom", "baseline"]

# ═══════════════════════════════════════════════════════════════
# 函数参数类型
# ═══════════════════════════════════════════════════════════════

# 绘图函数通用参数
PlotKwargs = Dict[str, Any]

# 标签列表
LabelsType = Optional[List[str]]

# 标题和轴标签
TitleType = str
XLabelType = str
YLabelType = str
ZLabelType = str

# ═══════════════════════════════════════════════════════════════
# 返回值类型
# ═══════════════════════════════════════════════════════════════

# 元组类型
ColorRGB = Tuple[float, float, float]  # RGB 颜色值 (0-1)
ColorRGBA = Tuple[float, float, float, float]  # RGBA 颜色值 (0-1)
FigSize = Tuple[float, float]  # 图形尺寸 (宽, 高)

# 配置类型
ConfigDict = Dict[str, Any]

# ═══════════════════════════════════════════════════════════════
# 协议定义 (用于结构化类型检查)
# ═══════════════════════════════════════════════════════════════

class HasLen(Protocol):
    """具有长度的协议"""
    def __len__(self) -> int: ...


class PlotFunction(Protocol):
    """绘图函数协议"""
    def __call__(
        self,
        *args: Any,
        venue: Optional[str] = None,
        palette: Optional[str] = None,
        lang: Optional[str] = None,
        **kwargs: Any,
    ) -> Any: ...


# ═══════════════════════════════════════════════════════════════
# 类型变量
# ═══════════════════════════════════════════════════════════════

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
# NumberType 已移至基础类型别名部分
ArrayType = TypeVar("ArrayType", bound=ArrayLike)


# ═══════════════════════════════════════════════════════════════
# 导出
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # 基础类型
    "Array",
    "NumericArray",
    "IntArray",
    "BoolArray",
    "OptionalArray",
    # 图表类型
    "VenueType",
    "LangType",
    "BuiltinPaletteType",
    "PaletteType",
    "CmapType",
    "LineStyleType",
    "MarkerType",
    "LegendLocType",
    "AlignType",
    "VaAlignType",
    # 参数类型
    "PlotKwargs",
    "LabelsType",
    "TitleType",
    "XLabelType",
    "YLabelType",
    "ZLabelType",
    # 返回值类型
    "ColorRGB",
    "ColorRGBA",
    "FigSize",
    "ConfigDict",
    # 协议
    "HasLen",
    "PlotFunction",
    # 类型变量
    "T",
    "T_co",
    "NumberType",
    "ArrayType",
]
