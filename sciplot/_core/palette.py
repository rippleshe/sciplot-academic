"""
配色管理 — 配色方案定义与应用

配色体系说明
============
SciPlot 有三类内置配色，均不依赖 SciencePlots：

  三大常驻系列（各含 1-4 色子集，推荐优先使用）
    pastel  — 柔和粉彩，默认，适合大多数论文场景
    earth   — 大地色系，适合土木/环境/材料类图表
    ocean   — 海洋蓝绿，适合水文/海洋/气象类图表

  人民币系列（各 5 色，灵感来自人民币纸币）
    100yuan / 50yuan / 20yuan / 10yuan / 5yuan / 1yuan

  自定义（用户运行时注册）
    set_custom_palette(colors, name)

注意：本版本已移除 rainbow-N 和 Paul Tol 配色，
后续如需增加新配色系，直接向 RESIDENT_PALETTES 添加即可。
"""

from __future__ import annotations

from typing import Dict, List, Optional

import matplotlib.pyplot as plt
from matplotlib import cycler
import warnings


# ============================================================================
# 用户自定义配色存储（单例）
# ============================================================================

class _UserPaletteStore:
    """用户自定义配色存储器（单例模式）"""
    _palettes: Dict[str, List[str]] = {}

    @classmethod
    def set(cls, name: str, colors: List[str]) -> None:
        """注册一个配色及其所有子集"""
        cls._palettes[name] = colors
        for i in range(1, len(colors) + 1):
            cls._palettes[f"{name}-{i}"] = colors[:i]

    @classmethod
    def get(cls, name: str) -> Optional[List[str]]:
        return cls._palettes.get(name)

    @classmethod
    def get_all_names(cls) -> List[str]:
        return list(cls._palettes.keys())

    @classmethod
    def has(cls, name: str) -> bool:
        return name in cls._palettes


# ============================================================================
# 人民币配色 — 灵感来源于人民币纸币主色调
# ============================================================================

RMB_PALETTES: Dict[str, List[str]] = {
    "100yuan": ["#780018", "#AA0033", "#DD0022", "#CC0044", "#FA8095"],  # 红色系
    "50yuan":  ["#25362B", "#276E3D", "#56B76A", "#3C4061", "#8E8E99"],  # 绿色系
    "20yuan":  ["#532F1A", "#6B4E25", "#7F5643", "#796A5D", "#BE9A62"],  # 棕色系
    "10yuan":  ["#242F4D", "#465A66", "#6382AA", "#828E99", "#7F606D"],  # 蓝色系
    "5yuan":   ["#413A4C", "#63576F", "#56B76A", "#6F8DB1", "#B3A479"],  # 紫色系
    "1yuan":   ["#3C3F27", "#5A5745", "#9DA780", "#937539", "#C5AB71"],  # 橄榄绿系
}

# ============================================================================
# 三大常驻配色系（每种都有 1-4 色子集）
# ============================================================================

# 1. Pastel 柔和粉彩（默认首选）
PASTEL_PALETTE: Dict[str, List[str]] = {
    "pastel":   ["#cdb4db", "#ffc8dd", "#ffafcc", "#bde0fe", "#a2d2ff"],
    "pastel-1": ["#cdb4db"],
    "pastel-2": ["#cdb4db", "#ffc8dd"],
    "pastel-3": ["#cdb4db", "#ffc8dd", "#ffafcc"],
    "pastel-4": ["#cdb4db", "#ffc8dd", "#ffafcc", "#bde0fe"],
}

# 2. Earth 大地色系
EARTH_PALETTE: Dict[str, List[str]] = {
    "earth":   ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"],
    "earth-1": ["#264653"],
    "earth-2": ["#264653", "#2a9d8f"],
    "earth-3": ["#264653", "#2a9d8f", "#e9c46a"],
    "earth-4": ["#264653", "#2a9d8f", "#e9c46a", "#f4a261"],
}

# 3. Ocean 海洋蓝绿
OCEAN_PALETTE: Dict[str, List[str]] = {
    "ocean":   ["#88afd8", "#90bfcf", "#afd1bf", "#cfe5bb", "#e0eeb8"],
    "ocean-1": ["#88afd8"],
    "ocean-2": ["#88afd8", "#90bfcf"],
    "ocean-3": ["#88afd8", "#90bfcf", "#afd1bf"],
    "ocean-4": ["#88afd8", "#90bfcf", "#afd1bf", "#cfe5bb"],
}

# 合并所有常驻配色（顺序：pastel 优先展示）
RESIDENT_PALETTES: Dict[str, List[str]] = {
    **PASTEL_PALETTE,
    **EARTH_PALETTE,
    **OCEAN_PALETTE,
}

# 所有内置配色名（不含用户自定义）
ALL_BUILTIN_PALETTES: List[str] = (
    list(RESIDENT_PALETTES.keys()) + list(RMB_PALETTES.keys())
)

# 向后兼容别名
ALL_PALETTES = ALL_BUILTIN_PALETTES

DEFAULT_PALETTE = "pastel"


# ============================================================================
# 配色应用
# ============================================================================

def apply_palette(palette: str) -> None:
    """
    将指定配色应用到 matplotlib rcParams（内部函数）

    优先级：
      1. 三大常驻配色系（pastel / earth / ocean 及其子集）
      2. 人民币配色
      3. 用户自定义配色
    """
    if palette in RESIDENT_PALETTES:
        plt.rcParams["axes.prop_cycle"] = cycler(color=RESIDENT_PALETTES[palette])
    elif palette in RMB_PALETTES:
        plt.rcParams["axes.prop_cycle"] = cycler(color=RMB_PALETTES[palette])
    elif _UserPaletteStore.has(palette):
        plt.rcParams["axes.prop_cycle"] = cycler(color=_UserPaletteStore.get(palette))
    else:
        raise ValueError(
            f"未知配色方案 '{palette}'。\n"
            f"内置配色：{ALL_BUILTIN_PALETTES}\n"
            f"调用 sp.list_palettes() 查看所有可用选项（含自定义）。"
        )


# ============================================================================
# 公开 API
# ============================================================================

def set_custom_palette(
    colors: List[str],
    name: str = "custom",
) -> None:
    """
    注册用户自定义配色方案

    注册后自动生成 1-N 色子集，可在 setup_style / 各绘图函数中使用。

    参数:
        colors: HEX 颜色列表，如 ["#E74C3C", "#3498DB", "#2ECC71"]
        name  : 配色名称，默认 "custom"；
                注册后可用 name / name-1 / name-2 / ... 调用

    示例:
        >>> sp.set_custom_palette(["#E74C3C", "#3498DB", "#2ECC71"], name="traffic")
        >>> sp.setup_style(palette="traffic")       # 3 色完整版
        >>> sp.setup_style(palette="traffic-2")    # 只取前 2 色
    """
    if not colors:
        raise ValueError("颜色列表不能为空")
    for c in colors:
        if not (c.startswith("#") and len(c) in (4, 7)):
            raise ValueError(
                f"颜色格式错误：'{c}'，请使用 HEX 格式（如 '#FF0000'）"
            )
    if len(colors) > 8:
        warnings.warn(
            f"自定义配色建议不超过 8 色，当前 {len(colors)} 色；"
            f"超过 5 色时请确保视觉区分度足够。",
            UserWarning,
            stacklevel=2,
        )
    _UserPaletteStore.set(name, colors)


def get_palette(name: str) -> List[str]:
    """
    获取指定配色方案的 HEX 颜色列表

    示例:
        >>> sp.get_palette("pastel")
        ['#cdb4db', '#ffc8dd', '#ffafcc', '#bde0fe', '#a2d2ff']
        >>> sp.get_palette("100yuan")
        ['#780018', '#AA0033', '#DD0022', '#CC0044', '#FA8095']
    """
    for store in (RESIDENT_PALETTES, RMB_PALETTES):
        if name in store:
            return store[name]
    if _UserPaletteStore.has(name):
        return _UserPaletteStore.get(name)
    raise ValueError(
        f"未知配色方案 '{name}'。调用 sp.list_palettes() 查看所有可用选项。"
    )


def list_palettes() -> List[str]:
    """列出所有可用配色方案名称（含用户自定义）"""
    return ALL_BUILTIN_PALETTES + _UserPaletteStore.get_all_names()


def list_all_palettes() -> List[str]:
    """list_palettes() 的别名（向后兼容）"""
    return list_palettes()


def list_resident_palettes() -> List[str]:
    """列出三大常驻配色系（pastel / earth / ocean 及其子集）"""
    return list(RESIDENT_PALETTES.keys())


def list_pastel_subsets() -> List[str]:
    """列出 pastel 系列名称"""
    return list(PASTEL_PALETTE.keys())


def list_earth_subsets() -> List[str]:
    """列出 earth 系列名称"""
    return list(EARTH_PALETTE.keys())


def list_ocean_subsets() -> List[str]:
    """列出 ocean 系列名称"""
    return list(OCEAN_PALETTE.keys())


def list_rmb_palettes() -> List[str]:
    """列出人民币配色方案名称"""
    return list(RMB_PALETTES.keys())
