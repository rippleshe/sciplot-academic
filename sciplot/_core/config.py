"""
配置持久化系统 — 全局默认值与配置文件支持

支持从 pyproject.toml 和 .sciplot.toml 读取配置，实现项目级别的默认设置。

配置优先级（高→低）：
    函数参数 > 代码设置 > 配置文件 > 内置默认

示例:
    >>> import sciplot as sp
    >>>
    >>> # 代码设置默认值
    >>> sp.set_defaults(venue="ieee", palette="earth")
    >>>
    >>> # 从文件加载配置
    >>> sp.load_config()  # 自动查找 pyproject.toml 或 .sciplot.toml
    >>>
    >>> # 获取当前配置
    >>> sp.get_config("venue")  # "ieee"
"""

from __future__ import annotations

import logging
import threading
import warnings
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union, cast, Type
from matplotlib.figure import Figure

# 配置模块日志记录器
_logger = logging.getLogger(__name__)

_CONFIG_LOCK = threading.Lock()
_TOML_IMPORT_WARNED = False
_SUPPORTED_SAVE_FORMATS: Optional[frozenset[str]] = None
_FORMATS_LOCK = threading.Lock()


def _get_supported_formats() -> frozenset[str]:
    """延迟获取支持的文件格式，避免导入时创建Figure实例。"""
    global _SUPPORTED_SAVE_FORMATS
    if _SUPPORTED_SAVE_FORMATS is not None:
        return _SUPPORTED_SAVE_FORMATS
    with _FORMATS_LOCK:
        if _SUPPORTED_SAVE_FORMATS is not None:
            return _SUPPORTED_SAVE_FORMATS
        try:
            import matplotlib
            backend = matplotlib.get_backend()
            if backend in matplotlib.rcsetup.interactive_bk:
                matplotlib.use('Agg', force=False)
            from matplotlib.figure import Figure
            fig = Figure()
            _SUPPORTED_SAVE_FORMATS = frozenset(fig.canvas.get_supported_filetypes().keys())
            import matplotlib.pyplot as plt
            plt.close(fig)
        except Exception:
            _SUPPORTED_SAVE_FORMATS = frozenset({'png', 'pdf', 'svg', 'eps', 'ps', 'jpg', 'jpeg', 'tif', 'tiff'})
        return _SUPPORTED_SAVE_FORMATS


def _load_toml_module() -> Any:
    """按优先级加载 TOML 解析器（tomllib -> tomli）。"""
    global _TOML_IMPORT_WARNED

    try:
        import tomllib as toml_module
        return toml_module
    except ImportError:
        pass

    try:
        import tomli as toml_module
        return toml_module
    except ImportError:
        if not _TOML_IMPORT_WARNED:
            warnings.warn(
                "配置文件功能需要 Python 3.11+ 或安装 tomli: pip install tomli",
                UserWarning,
                stacklevel=3,
            )
            _TOML_IMPORT_WARNED = True
        return None

_CONFIG_TYPES: Dict[str, Tuple[Type[Any], ...]] = {
    "venue": (str,),
    "palette": (str,),
    "lang": (str,),
    "dpi": (int,),
    "formats": (tuple, list),
}

_DEFAULTS_TEMPLATE: Dict[str, Any] = {
    "venue": "nature",
    "palette": "pastel",
    "lang": "zh",
    "dpi": 1200,
    "formats": ("pdf", "png"),
}


def _normalize_formats(formats: Union[Tuple[str, ...], List[str]]) -> Tuple[str, ...]:
    """规范化并校验 formats 配置。"""
    normalized = tuple(formats)
    if not normalized:
        raise ValueError("配置项 'formats' 不能为空")
    supported_formats = _get_supported_formats()
    result = []
    for fmt in normalized:
        if not isinstance(fmt, str) or not fmt.strip():
            raise ValueError(
                "配置项 'formats' 必须是非空字符串序列"
            )
        canonical = fmt.strip().lower()
        if canonical.startswith("."):
            canonical = canonical[1:]
        if canonical not in supported_formats:
            raise ValueError(
                f"配置项 'formats' 包含不支持的格式: {fmt!r}。"
                f"可用格式: {sorted(supported_formats)}"
            )
        result.append(canonical)
    return tuple(result)


def _normalize_config_value(key: str, value: Any) -> Any:
    """对配置值做标准化与语义校验。"""
    if key == "formats":
        return _normalize_formats(value)

    if key == "dpi":
        if value <= 0:
            raise ValueError("配置项 'dpi' 必须为正整数")
        return value

    if key == "venue":
        from sciplot._core.style import VENUES
        if value not in VENUES:
            raise ValueError(
                f"配置项 'venue' 取值无效: {value!r}，可用选项: {list(VENUES.keys())}"
            )
        return value

    if key == "palette":
        from sciplot._core.palette import list_palettes
        available_palettes = list_palettes()
        if value not in available_palettes:
            raise ValueError(
                f"配置项 'palette' 取值无效: {value!r}，可用选项: {available_palettes}"
            )
        return value

    if key == "lang":
        from sciplot._core.style import LANGUAGES
        if value not in LANGUAGES:
            raise ValueError(
                f"配置项 'lang' 取值无效: {value!r}，可用选项: {list(LANGUAGES.keys())}"
            )
        return value

    return value


class SciPlotConfig:
    """
    SciPlot 配置管理类

    管理全局默认值，支持从配置文件加载。

    线程安全说明:
        使用 threading.Lock 保护共享状态。在多线程环境下，
        配置的读取和修改是线程安全的。
    """

    _defaults: Dict[str, Any] = dict(_DEFAULTS_TEMPLATE)
    _user_settings: Dict[str, Any] = {}
    _file_settings: Dict[str, Any] = {}
    _config_loaded: bool = False

    @classmethod
    def set_defaults(cls, **kwargs: Any) -> None:
        """
        设置全局默认值

        参数:
            **kwargs: 配置项键值对
                - venue: 期刊样式 ("nature", "ieee", "thesis")
                - palette: 配色方案 ("pastel", "earth", "ocean")
                - lang: 语言 ("zh", "en")
                - dpi: 保存分辨率
                - formats: 保存格式元组

        抛出:
            ValueError: 配置项名称无效或类型不匹配

        示例:
            >>> sp.set_defaults(venue="ieee", palette="earth", dpi=600)
        """
        valid_keys = set(cls._defaults.keys())
        with _CONFIG_LOCK:
            for key, value in kwargs.items():
                if key not in valid_keys:
                    raise ValueError(
                        f"未知配置项: '{key}'。有效配置项: {sorted(valid_keys)}"
                    )
                expected_types = _CONFIG_TYPES.get(key)
                if expected_types and not isinstance(value, expected_types):
                    raise ValueError(
                        f"配置项 '{key}' 类型错误: 期望 {expected_types}, 实际 {type(value).__name__}"
                    )
                cls._user_settings[key] = _normalize_config_value(key, value)

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        获取配置值（按优先级）

        优先级：代码设置 > 配置文件 > 内置默认

        参数:
            key: 配置项名称，支持嵌套键（如 'style.venue'）
            default: 默认值，当配置项不存在时返回

        返回:
            配置值

        示例:
            >>> sp.get_config("venue")  # "nature"
        """
        with _CONFIG_LOCK:
            if "." in key:
                section, sub_key = key.split(".", 1)
                for settings in [cls._user_settings, cls._file_settings, cls._defaults]:
                    section_data = settings.get(section)
                    if isinstance(section_data, dict) and sub_key in section_data:
                        return section_data[sub_key]
                return default
            if key in cls._user_settings:
                return cls._user_settings[key]
            if key in cls._file_settings:
                return cls._file_settings[key]
            if key in cls._defaults:
                return cls._defaults[key]
        return default

    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """
        获取所有配置（合并后的结果）

        返回:
            合并后的配置字典
        """
        with _CONFIG_LOCK:
            result = dict(cls._defaults)
            result.update(cls._file_settings)
            result.update(cls._user_settings)
        return result

    @classmethod
    def reset(cls) -> None:
        """
        重置所有用户设置和文件设置

        示例:
            >>> sp.reset_config()
        """
        with _CONFIG_LOCK:
            cls._user_settings.clear()
            cls._file_settings.clear()
            cls._config_loaded = False

    @classmethod
    def load_from_file(cls, path: Optional[Union[str, Path]] = None) -> bool:
        """
        从配置文件加载设置

        参数:
            path: 配置文件路径。如果为 None，自动查找配置文件。

        返回:
            是否成功加载配置

        示例:
            >>> sp.load_config()  # 自动查找
            >>> sp.load_config("path/to/config.toml")  # 指定路径
        """
        if path is not None:
            config_path = Path(path).expanduser()
            if not config_path.exists():
                raise FileNotFoundError(f"配置文件不存在: {config_path}")
            return cls._load_config_file(config_path)

        found_config_path = cls._find_config_file()
        if found_config_path is not None:
            return cls._load_config_file(found_config_path)

        return False

    @classmethod
    def _find_config_file(cls) -> Optional[Path]:
        """
        查找配置文件

        查找顺序：
        1. 当前目录的 .sciplot.toml
        2. 当前目录的 pyproject.toml
        3. 向上遍历父目录查找

        返回:
            配置文件路径，如果未找到返回 None
        """
        cwd = Path.cwd()

        for directory in [cwd] + list(cwd.parents):
            sciplot_toml = directory / ".sciplot.toml"
            if sciplot_toml.exists():
                return sciplot_toml

            pyproject_toml = directory / "pyproject.toml"
            if pyproject_toml.exists():
                data = cls._read_toml(pyproject_toml)
                if data and "tool" in data and "sciplot" in data["tool"]:
                    return pyproject_toml

        return None

    @classmethod
    def _load_config_file(cls, path: Path) -> bool:
        """
        加载配置文件

        参数:
            path: 配置文件路径

        返回:
            是否成功加载
        """
        data = cls._read_toml(path)
        if data is None:
            return False

        if path.name == "pyproject.toml":
            config = data.get("tool", {}).get("sciplot", {})
        else:
            config = data

        if not config:
            return False

        applied_count = 0
        with _CONFIG_LOCK:
            for key, value in config.items():
                if key in cls._defaults:
                    expected_types = _CONFIG_TYPES.get(key)
                    if expected_types and not isinstance(value, expected_types):
                        continue
                    try:
                        value = _normalize_config_value(key, value)
                    except ValueError:
                        continue
                    cls._file_settings[key] = value
                    applied_count += 1
            cls._config_loaded = applied_count > 0

        return applied_count > 0

    @classmethod
    def _read_toml(cls, path: Path) -> Optional[Dict[str, Any]]:
        """
        读取 TOML 文件

        参数:
            path: 文件路径

        返回:
            解析后的字典，失败返回 None
        """
        toml_module = _load_toml_module()
        if toml_module is None:
            _logger.debug("TOML 解析模块不可用，跳过配置文件读取")
            return None

        try:
            with open(path, "rb") as f:
                return cast(Dict[str, Any], toml_module.load(f))
        except OSError as e:
            _logger.warning(f"无法读取配置文件 {path}: {e}")
            return None
        except toml_module.TOMLDecodeError as e:
            _logger.error(f"配置文件 {path} 格式错误: {e}")
            return None

    @classmethod
    def is_loaded(cls) -> bool:
        """
        检查是否已加载配置文件

        返回:
            是否已成功加载配置文件
        """
        with _CONFIG_LOCK:
            return cls._config_loaded


def set_defaults(**kwargs: Any) -> None:
    """
    设置全局默认值

    参数:
        **kwargs: 配置项键值对

    示例:
        >>> import sciplot as sp
        >>> sp.set_defaults(venue="ieee", palette="earth")
    """
    SciPlotConfig.set_defaults(**kwargs)


def get_config(key: Optional[str] = None) -> Any:
    """
    获取配置值

    参数:
        key: 配置项名称。如果为 None，返回所有配置。

    返回:
        配置值或配置字典

    示例:
        >>> sp.get_config("venue")  # "nature"
        >>> sp.get_config()  # {"venue": "nature", ...}
    """
    if key is None:
        return SciPlotConfig.get_all()
    return SciPlotConfig.get(key)


def load_config(path: Optional[Union[str, Path]] = None) -> bool:
    """
    从配置文件加载设置

    参数:
        path: 配置文件路径。如果为 None，自动查找配置文件。

    返回:
        是否成功加载配置

    示例:
        >>> sp.load_config()  # 自动查找
    """
    return SciPlotConfig.load_from_file(path)


def reset_config() -> None:
    """
    重置所有用户设置和文件设置

    示例:
        >>> sp.reset_config()
    """
    SciPlotConfig.reset()


__all__ = [
    "SciPlotConfig",
    "set_defaults",
    "get_config",
    "load_config",
    "reset_config",
]
