"""
配色管理 — 配色方案定义与应用

配色体系说明
============
SciPlot 内置多套精选配色方案，均不依赖 SciencePlots：

  pastel  — 柔和粉彩（6 色），适合大多数论文场景
  ocean   — 海洋蓝绿（6 色），适合水文/海洋/气象类图表
  forest  — 森林渐变（6 色），适合生态/环保/农业类图表
  sunset  — 日落暖色（5 色），适合能量/热力/温度类图表

基础色系自动生成 1-N 色子集（如 pastel-1 ~ pastel-6）。

  自定义（用户运行时注册）
    set_custom_palette(colors, name)  — 注册单色组
    register_color_scheme(name, scheme)  — 注册完整配色方案

  扩展配色系（用户自定义完整方案）
    通过 register_color_scheme() 注册后可使用 scheme-name 调用
"""

from __future__ import annotations

import re
import threading
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
from matplotlib import cycler
from matplotlib.colors import LinearSegmentedColormap
import warnings

_HEX_COLOR_PATTERN = re.compile(r'^#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?$')


def _validate_hex_color(color: str) -> bool:
    """
    验证 HEX 颜色格式是否有效
    
    参数:
        color: 颜色字符串
    
    返回:
        是否为有效的 HEX 颜色
    """
    return bool(_HEX_COLOR_PATTERN.match(color))


# ============================================================================
# 用户自定义配色存储（单例）
# ============================================================================

class _UserPaletteStore:
    """用户自定义配色存储器（单例模式）"""
    _lock = threading.RLock()
    _palettes: Dict[str, List[str]] = {}
    _schemes: Dict[str, Dict[str, List[str]]] = {}  # 完整配色方案存储

    @classmethod
    def set(cls, name: str, colors: List[str]) -> None:
        """注册一个配色及其所有子集"""
        safe_colors = list(colors)
        with cls._lock:
            cls._palettes[name] = safe_colors
            for i in range(1, len(safe_colors) + 1):
                cls._palettes[f"{name}-{i}"] = safe_colors[:i]

    @classmethod
    def get(cls, name: str) -> Optional[List[str]]:
        with cls._lock:
            colors = cls._palettes.get(name)
            return list(colors) if colors is not None else None

    @classmethod
    def get_all_names(cls) -> List[str]:
        with cls._lock:
            return list(cls._palettes.keys())

    @classmethod
    def has(cls, name: str) -> bool:
        with cls._lock:
            return name in cls._palettes

    @classmethod
    def register_scheme(cls, name: str, scheme: Dict[str, List[str]]) -> None:
        """注册完整的配色方案"""
        safe_scheme = {key: list(colors) for key, colors in scheme.items()}
        with cls._lock:
            cls._schemes[name] = safe_scheme
            # 同时注册到 palettes 以便直接使用
            for key, colors in safe_scheme.items():
                cls._palettes[f"{name}-{key}"] = list(colors)
            # 注册默认完整版
            if "quintuple" in safe_scheme:
                cls._palettes[name] = list(safe_scheme["quintuple"])
            elif "quadruple" in safe_scheme:
                cls._palettes[name] = list(safe_scheme["quadruple"])
            elif "triple" in safe_scheme:
                cls._palettes[name] = list(safe_scheme["triple"])

    @classmethod
    def get_scheme(cls, name: str) -> Optional[Dict[str, List[str]]]:
        """获取完整的配色方案"""
        with cls._lock:
            scheme = cls._schemes.get(name)
            if scheme is None:
                return None
            return {key: list(colors) for key, colors in scheme.items()}

    @classmethod
    def has_scheme(cls, name: str) -> bool:
        """检查是否存在配色方案"""
        with cls._lock:
            return name in cls._schemes

    @classmethod
    def list_schemes(cls) -> List[str]:
        """列出所有注册的配色方案"""
        with cls._lock:
            return list(cls._schemes.keys())

    @classmethod
    def auto_select(cls, name: str, n: int) -> Optional[List[str]]:
        """根据数据量自动选择合适的配色

        优先级：
        1. 精确匹配 name-n
        2. 从配色方案中选择最接近的
        3. 返回默认配色
        """
        with cls._lock:
            # 尝试精确匹配
            exact = cls._palettes.get(f"{name}-{n}")
            if exact:
                return list(exact)

            # 从配色方案中选择
            scheme = cls._schemes.get(name)
            if scheme:
                key_map = {1: "single", 2: "double", 3: "triple",
                           4: "quadruple", 5: "quintuple", 6: "sextuple"}
                key = key_map.get(n, "quintuple")
                if key in scheme:
                    return list(scheme[key])
                # 回退到最大可用
                for k in ["quintuple", "quadruple", "triple", "double", "single"]:
                    if k in scheme:
                        colors = scheme[k]
                        if len(colors) >= n:
                            return list(colors[:n])
                        return list(colors)

        return None


# ============================================================================
# 内置配色系（基础色系具备 1-N 子集）
# ============================================================================

# 1. Pastel 柔和粉彩（默认首选）
PASTEL_PALETTE: Dict[str, List[str]] = {
    "pastel":   ["#845EC2", "#D65DB1", "#FF6F91", "#FF9671", "#FFC75F", "#F9F871"],
    "pastel-1": ["#845EC2"],
    "pastel-2": ["#845EC2", "#D65DB1"],
    "pastel-3": ["#845EC2", "#D65DB1", "#FF6F91"],
    "pastel-4": ["#845EC2", "#D65DB1", "#FF6F91", "#FF9671"],
    "pastel-5": ["#845EC2", "#D65DB1", "#FF6F91", "#FF9671", "#FFC75F"],
    "pastel-6": ["#845EC2", "#D65DB1", "#FF6F91", "#FF9671", "#FFC75F", "#F9F871"],
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
    "ocean":   ["#5E98C2", "#26B3D1", "#00CCCB", "#56E2B0", "#A6F18C", "#F9F871"],
    "ocean-1": ["#5E98C2"],
    "ocean-2": ["#5E98C2", "#26B3D1"],
    "ocean-3": ["#5E98C2", "#26B3D1", "#00CCCB"],
    "ocean-4": ["#5E98C2", "#26B3D1", "#00CCCB", "#56E2B0"],
    "ocean-5": ["#5E98C2", "#26B3D1", "#00CCCB", "#56E2B0", "#A6F18C"],
    "ocean-6": ["#5E98C2", "#26B3D1", "#00CCCB", "#56E2B0", "#A6F18C", "#F9F871"],
}

# 4. Forest 森林渐变
FOREST_PALETTE: Dict[str, List[str]] = {
    "forest":   ["#5EC299", "#00B3A2", "#00A2AD", "#0090B8", "#007DBD", "#0067B9"],
    "forest-1": ["#5EC299"],
    "forest-2": ["#5EC299", "#00B3A2"],
    "forest-3": ["#5EC299", "#00B3A2", "#00A2AD"],
    "forest-4": ["#5EC299", "#00B3A2", "#00A2AD", "#0090B8"],
    "forest-5": ["#5EC299", "#00B3A2", "#00A2AD", "#0090B8", "#007DBD"],
    "forest-6": ["#5EC299", "#00B3A2", "#00A2AD", "#0090B8", "#007DBD", "#0067B9"],
}

# 5. Sunset 日落暖色
SUNSET_PALETTE: Dict[str, List[str]] = {
    "sunset":   ["#D44132", "#F45E4A", "#FF7A62", "#FF967C", "#FFB296"],
    "sunset-1": ["#D44132"],
    "sunset-2": ["#D44132", "#F45E4A"],
    "sunset-3": ["#D44132", "#F45E4A", "#FF7A62"],
    "sunset-4": ["#D44132", "#F45E4A", "#FF7A62", "#FF967C"],
    "sunset-5": ["#D44132", "#F45E4A", "#FF7A62", "#FF967C", "#FFB296"],
}

# 6. RMB 人民币主题配色（特色）
RMB_PALETTES: Dict[str, List[str]] = {
    "100yuan": ["#780018", "#AA0033", "#DD0022", "#CC0044", "#FA8095"],
    "50yuan":  ["#25362B", "#276E3D", "#56B76A", "#3C4061", "#8E8E99"],
    "20yuan":  ["#532F1A", "#6B4E25", "#7F5643", "#796A5D", "#BE9A62"],
    "10yuan":  ["#242F4D", "#465A66", "#6382AA", "#828E99", "#7F606D"],
    "5yuan":   ["#413A4C", "#63576F", "#56B76A", "#6F8DB1", "#B3A479"],
    "1yuan":   ["#3C3F27", "#5A5745", "#9DA780", "#937539", "#C5AB71"],
}

# 7. 发散型配色（热力图/相关矩阵）
DIVERGING_PALETTES: Dict[str, List[str]] = {
    "rdbu": ["#8B1C2D", "#C44B5E", "#E8A0AA", "#F5F5F5", "#A0C8E0", "#4B7BA8", "#1C3D6B"],
    "coolwarm": ["#3A5FCC", "#7A9EF0", "#C8D8F8", "#F5F5F5", "#F8C8C8", "#F07A7A", "#CC3A3A"],
}

# 合并所有内置配色
RESIDENT_PALETTES: Dict[str, List[str]] = {
    **PASTEL_PALETTE,
    **EARTH_PALETTE,
    **OCEAN_PALETTE,
    **FOREST_PALETTE,
    **SUNSET_PALETTE,
    **RMB_PALETTES,
    **DIVERGING_PALETTES,
}


def _register_diverging_cmaps() -> None:
    """将 SciPlot 发散配色注册为 matplotlib colormap。"""
    for name, colors in DIVERGING_PALETTES.items():
        # 检查是否已存在同名colormap
        try:
            existing = plt.colormaps.get_cmap(name)
            if existing is not None:
                continue
        except (KeyError, ValueError):
            pass
        except AttributeError:
            # 低版本matplotlib可能没有get_cmap方法
            pass

        cmap = LinearSegmentedColormap.from_list(name, colors)
        try:
            plt.colormaps.register(cmap, name=name)
        except (ValueError, KeyError):
            # 重复注册或名称冲突时静默跳过
            pass
        except AttributeError:
            # 低版本matplotlib可能没有register方法
            try:
                import matplotlib
                matplotlib.cm.register_cmap(name=name, cmap=cmap)
            except Exception:
                pass


_register_diverging_cmaps()

# 所有内置配色名（不含用户自定义）
ALL_BUILTIN_PALETTES: List[str] = list(RESIDENT_PALETTES.keys())

# 向后兼容别名
ALL_PALETTES = ALL_BUILTIN_PALETTES

DEFAULT_PALETTE = "pastel"


# ============================================================================
# 配色应用
# ============================================================================

def apply_palette(palette: str, n_colors: Optional[int] = None) -> None:
    """
    将指定配色应用到 matplotlib rcParams（内部函数）

    优先级：
      1. 四大内置配色（pastel / ocean / forest / sunset 及其子集）
      2. 用户自定义配色
      3. 用户自定义配色方案（自动选择）

    参数:
        palette: 配色名称
        n_colors: 如果指定，尝试自动选择合适数量的颜色（用于配色方案）
    """
    colors = None

    # 1. 内置配色
    if palette in RESIDENT_PALETTES:
        colors = RESIDENT_PALETTES[palette]
    # 2. 用户自定义配色
    elif _UserPaletteStore.has(palette):
        colors = _UserPaletteStore.get(palette)
    # 3. 尝试自动选择（配色方案）
    elif n_colors is not None and _UserPaletteStore.has_scheme(palette):
        colors = _UserPaletteStore.auto_select(palette, n_colors)

    if colors is None:
        raise ValueError(
            f"未知配色方案 '{palette}'。\n"
            f"内置配色：{ALL_BUILTIN_PALETTES}\n"
            f"调用 sp.list_palettes() 查看所有可用选项（含自定义）。"
        )

    plt.rcParams["axes.prop_cycle"] = cycler(color=colors)


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
        if not _validate_hex_color(c):
            raise ValueError(
                f"颜色格式错误：'{c}'，请使用有效的 HEX 格式（如 '#FF0000' 或 '#F00'）"
            )
    if len(colors) < 2:
        warnings.warn(
            "配色建议至少包含 2 种颜色",
            UserWarning,
            stacklevel=2,
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
        ['#845EC2', '#D65DB1', '#FF6F91', '#FF9671', '#FFC75F', '#F9F871']
        >>> sp.get_palette("ocean")
        ['#5E98C2', '#26B3D1', '#00CCCB', '#56E2B0', '#A6F18C', '#F9F871']
    """
    if name in RESIDENT_PALETTES:
        return list(RESIDENT_PALETTES[name])
    if _UserPaletteStore.has(name):
        colors = _UserPaletteStore.get(name)
        if colors is not None:
            return colors
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
    """列出所有内置配色（含基础色系、RMB、发散型等）"""
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


def list_forest_subsets() -> List[str]:
    """列出 forest 系列名称"""
    return list(FOREST_PALETTE.keys())


def list_sunset_subsets() -> List[str]:
    """列出 sunset 系列名称"""
    return list(SUNSET_PALETTE.keys())


def list_rmb_palettes() -> List[str]:
    """列出人民币配色方案名称"""
    return list(RMB_PALETTES.keys())


def list_diverging_palettes() -> List[str]:
    """列出发散型配色方案名称"""
    return list(DIVERGING_PALETTES.keys())


def register_color_scheme(
    name: str,
    scheme: Dict[str, List[str]],
) -> None:
    """
    注册完整的配色方案（支持单/双/三/四/五色自动选择）

    配色方案格式：
        {
            "single":    ["#264653"],           # 1色
            "double":    ["#264653", "#2a9d8f"], # 2色
            "triple":    [...],                  # 3色
            "quadruple": [...],                  # 4色
            "quintuple": [...],                  # 5色
            "sextuple":  [...],                  # 6色（可选）
        }

    注册后可通过以下方式使用：
        - sp.setup_style(palette="myscheme")           # 使用完整版
        - sp.setup_style(palette="myscheme-triple")    # 明确指定3色
        - sp.plot_multi(x, [y1, y2, y3], palette="myscheme")  # 自动选择3色

    参数:
        name: 配色方案名称，如 "mytheme"
        scheme: 配色方案字典，包含 single/double/triple/quadruple/quintuple

    示例:
        >>> my_scheme = {
        ...     "single": ["#264653"],
        ...     "double": ["#264653", "#2a9d8f"],
        ...     "triple": ["#264653", "#2a9d8f", "#e9c46a"],
        ...     "quadruple": ["#264653", "#2a9d8f", "#e9c46a", "#f4a261"],
        ...     "quintuple": ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"],
        ... }
        >>> sp.register_color_scheme("earth_pro", my_scheme)
        >>> sp.setup_style(palette="earth_pro-triple")  # 使用3色版
    """
    # 验证 scheme 格式
    required_keys = ["single", "double", "triple"]
    for key in required_keys:
        if key not in scheme:
            raise ValueError(f"配色方案必须包含 '{key}' 键")

    # 验证颜色格式
    for key, colors in scheme.items():
        if not isinstance(colors, list):
            raise ValueError(f"'{key}' 必须是颜色列表")
        for c in colors:
            if not (isinstance(c, str) and _validate_hex_color(c)):
                raise ValueError(
                    f"颜色格式错误：'{c}'，请使用有效的 HEX 格式（如 '#FF0000' 或 '#F00'）"
                )

    _UserPaletteStore.register_scheme(name, scheme)


def get_color_scheme(name: str) -> Dict[str, List[str]]:
    """
    获取已注册的配色方案

    示例:
        >>> scheme = sp.get_color_scheme("mytheme")
        >>> scheme["triple"]
        ['#264653', '#2a9d8f', '#e9c46a']
    """
    scheme = _UserPaletteStore.get_scheme(name)
    if scheme is None:
        raise ValueError(f"未找到配色方案 '{name}'。可用方案: {list_color_schemes()}")
    return scheme


def list_color_schemes() -> List[str]:
    """列出所有已注册的配色方案名称"""
    return _UserPaletteStore.list_schemes()


def auto_select_palette(name: str, n: int) -> List[str]:
    """
    根据数据量自动选择合适的配色

    参数:
        name: 配色方案名称
        n: 需要的颜色数量

    返回:
        最适合的配色列表

    示例:
        >>> colors = sp.auto_select_palette("mytheme", 3)  # 返回3色配色
    """
    colors = _UserPaletteStore.auto_select(name, n)
    if colors is None:
        raise ValueError(f"无法为 '{name}' 选择 {n} 色配色")
    return colors


