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

import threading
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

try:
    import tomllib
except ImportError:
    import tomli as tomllib

_CONFIG_LOCK = threading.Lock()

_CONFIG_TYPES: Dict[str, Tuple[type, ...]] = {
    "venue": (str,),
    "palette": (str,),
    "lang": (str,),
    "dpi": (int,),
    "formats": (tuple, list),
}


def _normalize_formats(formats: Union[Tuple[str, ...], list]) -> Tuple[str, ...]:
    """规范化并校验 formats 配置。"""
    normalized = tuple(formats)
    if not normalized:
        raise ValueError("配置项 'formats' 不能为空")
    for fmt in normalized:
        if not isinstance(fmt, str) or not fmt.strip():
            raise ValueError(
                "配置项 'formats' 必须是非空字符串序列"
            )
    return tuple(fmt.strip().lower() for fmt in normalized)


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

    _defaults: Dict[str, Any] = {
        "venue": "nature",
        "palette": "pastel",
        "lang": "zh",
        "dpi": 1200,
        "formats": ("pdf", "png"),
    }

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
    def get(cls, key: str) -> Any:
        """
        获取配置值（按优先级）

        优先级：代码设置 > 配置文件 > 内置默认

        参数:
            key: 配置项名称

        返回:
            配置值

        抛出:
            KeyError: 配置项名称无效

        示例:
            >>> sp.get_config("venue")  # "nature"
        """
        with _CONFIG_LOCK:
            if key in cls._user_settings:
                return cls._user_settings[key]
            if key in cls._file_settings:
                return cls._file_settings[key]
            if key in cls._defaults:
                return cls._defaults[key]
        raise KeyError(f"未知配置项: '{key}'")

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
            config_path = Path(path)
            if not config_path.exists():
                raise FileNotFoundError(f"配置文件不存在: {config_path}")
            return cls._load_config_file(config_path)

        config_path = cls._find_config_file()
        if config_path is not None:
            return cls._load_config_file(config_path)

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
        try:
            with open(path, "rb") as f:
                return tomllib.load(f)
        except (OSError, tomllib.TOMLDecodeError):
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
