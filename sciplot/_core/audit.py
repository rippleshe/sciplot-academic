"""
图表质量审计 — 审稿七宗罪防线

Nature 审稿人高频指出的图表问题（2024-2026 编辑规范）：
1. 字号低于 5pt（Nature 最小字号规范）
2. 多面板图缺少字母标签 (a) (b) (c)
3. 轴未标注（unlabeled axes）
4. 面板顺序漂移（panel-order drift）
5. 色盲不安全配色（由 colorblind.py 处理）
6. 填充式留白（filler whitespace）

本模块在 save() 时自动审计，把"审稿人会打回的问题"
变成保存时的可见警告，将质量防线前置到绘图流程。
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import numpy as np

# Nature 规范：正文最小 5pt，面板标签 8pt 加粗
MIN_FONT_SIZE = 5.0
MIN_LABEL_SIZE = 6.0
PANEL_LABEL_SIZE = 8.0

_PANEL_LABEL_RE = re.compile(r"^\(?[a-zA-Z0-9ivxIVX]{1,3}\)?$")


def _collect_texts(fig: Figure) -> List[Tuple[Axes, Any, str, float]]:
    """收集图中所有文本元素: (ax, text_obj, content, fontsize)。"""
    out: List[Tuple[Axes, Any, str, float]] = []
    for ax in fig.axes:
        if not isinstance(ax, Axes):
            continue
        for t in ax.texts:
            content = t.get_text()
            if content:
                fs = t.get_fontsize()
                out.append((ax, t, content, fs))
        # 轴刻度标签
        for tick in ax.get_xticklabels() + ax.get_yticklabels():
            content = tick.get_text()
            if content:
                out.append((ax, tick, str(content), tick.get_fontsize()))
    # 图例文本
    for ax in fig.axes:
        if not isinstance(ax, Axes):
            continue
        leg = ax.get_legend()
        if leg is not None:
            for t in leg.get_texts():
                content = t.get_text()
                if content:
                    out.append((ax, t, content, t.get_fontsize()))
    return out


def _has_panel_labels(fig: Figure) -> bool:
    """检查图中是否存在 (a)/(b) 样式的面板标签。"""
    for ax in fig.axes:
        if not isinstance(ax, Axes):
            continue
        for t in ax.texts:
            content = t.get_text().strip()
            if content and _PANEL_LABEL_RE.match(content):
                return True
    return False


def audit_figure(
    fig: Figure,
    check_font_size: bool = True,
    check_panel_labels: bool = True,
    check_axis_labels: bool = True,
    min_font_size: float = MIN_FONT_SIZE,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    审计图表的投稿质量风险（审稿七宗罪防线）。

    检查项:
        - font_size   : 是否存在小于 min_font_size 的文本（Nature 最小 5pt）
        - panel_labels: 多面板图是否缺少 (a) (b) 面板标签
        - axis_labels : 含数据的坐标轴是否未标注 x/y 轴

    参数:
        fig             : matplotlib Figure
        check_font_size : 是否检查字号下限
        check_panel_labels: 是否检查面板标签
        check_axis_labels: 是否检查轴标签
        min_font_size   : 字号下限（默认 5pt，Nature 规范）
        verbose         : 是否将问题输出为警告

    返回:
        {"issues": [...], "warnings": [...], "safe": bool}

    示例:
        >>> report = sp.audit_figure(fig)
        >>> report["safe"]
        True
    """
    issues: List[str] = []
    warnings_list: List[str] = []

    # ── 字号下限 ──
    if check_font_size:
        small: List[Tuple[float, str]] = []
        for _ax, _t, content, fs in _collect_texts(fig):
            if fs < min_font_size:
                small.append((fs, content[:20]))
        if small:
            details = ", ".join(f"{fs:.1f}pt '{txt}'" for fs, txt in small[:5])
            msg = f"存在 {len(small)} 处字号小于 {min_font_size:.0f}pt 的文本: {details}"
            issues.append(msg)
            warnings_list.append(msg)

    # ── 面板标签 ──
    if check_panel_labels:
        n_axes = sum(1 for ax in fig.axes if isinstance(ax, Axes))
        if n_axes > 1 and not _has_panel_labels(fig):
            msg = (
                f"多面板图（{n_axes} 个子图）缺少面板标签 (a) (b)…，"
                f"请使用 sp.add_panel_labels(axes) 或 figure_panels()"
            )
            issues.append(msg)
            warnings_list.append(msg)

    # ── 轴标签 ──
    if check_axis_labels:
        unlabeled: List[str] = []
        for ax in fig.axes:
            if not isinstance(ax, Axes):
                continue
            # 跳过隐藏轴（如纯示意图面板）
            if not ax.get_visible():
                continue
            has_data = bool(ax.lines or ax.collections or ax.patches
                            or ax.images or ax.barcontainers)
            if not has_data:
                continue
            xlbl = ax.get_xlabel().strip()
            ylbl = ax.get_ylabel().strip()
            if not xlbl:
                unlabeled.append("x")
            if not ylbl:
                unlabeled.append("y")
        if unlabeled:
            msg = f"存在未标注的坐标轴: {', '.join(sorted(set(unlabeled)))} 轴"
            issues.append(msg)
            warnings_list.append(msg)

    safe = len(issues) == 0

    if verbose:
        for msg in warnings_list:
            import warnings as _w

            _w.warn(f"[sciplot 审计] {msg}", UserWarning, stacklevel=3)

    return {"issues": issues, "warnings": warnings_list, "safe": safe}


def _audit_and_warn(fig: Figure, enabled: bool) -> None:
    """save() 内部钩子：按配置执行审计并输出警告（不中断保存）。"""
    if not enabled:
        return
    try:
        audit_figure(fig, verbose=True)
    except Exception:
        # 审计失败不影响保存
        pass
