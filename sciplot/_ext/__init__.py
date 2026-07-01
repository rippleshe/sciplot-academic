"""
SciPlot 扩展模块
包含机器学习可视化、3D 可视化等高级功能
"""

from __future__ import annotations

import importlib
from typing import Any

__all__ = ["ml", "plot3d", "network", "hierarchical", "venn"]


def __getattr__(name: str) -> Any:
    """延迟导入扩展模块"""
    if name in {"ml", "plot3d", "network", "hierarchical", "venn"}:
        try:
            return importlib.import_module(f"{__name__}.{name}")
        except ImportError as exc:
            raise AttributeError(f"扩展模块 '{name}' 需要额外依赖") from exc
    raise AttributeError(f"模块 'sciplot._ext' 没有属性 '{name}'")
