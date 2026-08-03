"""
Flow 家族图表 — 桑基图
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np

from sciplot._core.utils import cycle_color, get_cycle_colors, new_styled_figure
from sciplot._core.result import PlotResult

# ============================================================================
# 桑基图（Sankey，Flow 家族）
# ============================================================================

def plot_sankey(
    sources: Sequence[Any],
    targets: Sequence[Any],
    values: Sequence[float],
    labels: Optional[Sequence[str]] = None,
    node_colors: Optional[Sequence[str]] = None,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    node_width: float = 0.1,
    node_alpha: float = 0.9,
    flow_alpha: float = 0.55,
    min_flow: float = 0.0,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制桑基图（Sankey Diagram，能量/物质/流量流向）。

    纯 matplotlib 实现，无额外依赖。节点按最长路径分层，
    节点高度与流量带宽度均正比于流量值。

    参数:
        sources    : 每条流的源节点（名称或任意可哈希值）
        targets    : 每条流的目标节点
        values     : 每条流的流量（非负）
        labels     : 节点显示名（与节点集合等长或为 dict）；默认用节点本身
        node_colors: 节点颜色列表（按节点出现顺序）；默认取当前配色循环
        node_width : 节点矩形宽度（归一化坐标）
        node_alpha : 节点不透明度
        flow_alpha : 流量带不透明度
        min_flow   : 小于该值的流被过滤（避免视觉噪音）

    示例:
        >>> fig, ax = sp.plot_sankey(
        ...     ["A", "A", "B"], ["B", "C", "C"], [40, 30, 20],
        ...     labels=["能源", "转化", "终端"],
        ... )
    """
    from matplotlib.patches import PathPatch, Rectangle
    from matplotlib.path import Path

    src_arr = list(sources)
    tgt_arr = list(targets)
    val_arr = np.asarray(values, dtype=float)
    if len(src_arr) != len(tgt_arr) or len(src_arr) != len(val_arr):
        raise ValueError(
            f"sources/targets/values 长度必须一致: "
            f"{len(src_arr)}/{len(tgt_arr)}/{len(val_arr)}"
        )
    if val_arr.size == 0:
        raise ValueError("sources/targets/values 不能为空")
    if not np.all(np.isfinite(val_arr)):
        raise ValueError("values 不能包含 NaN 或 Inf")
    if np.any(val_arr < 0):
        raise ValueError("values 不能包含负值（流量必须非负）")
    if not (0.0 < node_width < 1.0):
        raise ValueError(f"node_width 必须在 (0, 1) 范围内，实际值: {node_width!r}")
    if min_flow < 0:
        raise ValueError(f"min_flow 必须非负，实际值: {min_flow!r}")

    # 过滤小流量
    keep = val_arr >= min_flow
    if not np.any(keep):
        raise ValueError("过滤 min_flow 后没有剩余流量，请调低 min_flow")
    src_arr = [s for s, k in zip(src_arr, keep) if k]
    tgt_arr = [t for t, k in zip(tgt_arr, keep) if k]
    val_arr = val_arr[keep]

    # 节点集合（按出现顺序）
    node_list: List[Any] = []
    for s, t in zip(src_arr, tgt_arr):
        if s not in node_list:
            node_list.append(s)
        if t not in node_list:
            node_list.append(t)
    n_nodes = len(node_list)
    node_index = {n: i for i, n in enumerate(node_list)}

    if labels is not None:
        if isinstance(labels, dict):
            label_of = {n: str(labels[n]) for n in node_list}
        elif len(labels) != n_nodes:
            raise ValueError(
                f"labels 长度 ({len(labels)}) 与节点数 ({n_nodes}) 不一致"
            )
        else:
            label_of = {n: str(labels[i]) for i, n in enumerate(node_list)}
    else:
        label_of = {n: str(n) for n in node_list}

    if node_colors is not None:
        if len(node_colors) < n_nodes:
            raise ValueError(
                f"node_colors 长度 ({len(node_colors)}) 小于节点数 ({n_nodes})"
            )
        color_of = {n: node_colors[i] for i, n in enumerate(node_list)}
    else:
        cycle = get_cycle_colors()
        color_of = {n: cycle_color(cycle, i) for i, n in enumerate(node_list)}

    # 层级分配：最长路径（源 → 目标）
    preds: Dict[Any, List[Any]] = {n: [] for n in node_list}
    for s, t in zip(src_arr, tgt_arr):
        if t not in preds[s]:
            preds[s].append(t)
    level: Dict[Any, int] = {n: 0 for n in node_list}
    changed = True
    while changed:
        changed = False
        for s, t in zip(src_arr, tgt_arr):
            if s != t and level[t] <= level[s]:  # 自环跳过，避免死循环
                level[t] = level[s] + 1
                changed = True
    max_level = max(level.values())

    # 节点流量（流入/流出取大者作为高度基准）
    inflow: Dict[Any, float] = {n: 0.0 for n in node_list}
    outflow: Dict[Any, float] = {n: 0.0 for n in node_list}
    for s, t, v in zip(src_arr, tgt_arr, val_arr):
        outflow[s] += float(v)
        inflow[t] += float(v)
    node_value = {n: max(inflow[n], outflow[n]) for n in node_list}

    # 逐层布局：层内按流量降序，节点高度 ∝ 流量
    total_value = float(max(sum(outflow.values()), sum(inflow.values()), 1e-9))
    layers: Dict[int, List[Any]] = {}
    for n in node_list:
        layers.setdefault(level[n], []).append(n)
    for lv in layers:
        layers[lv].sort(key=lambda n: -node_value[n])

    max_layer_h = 0.0
    layer_heights: Dict[int, float] = {}
    for lv, nodes in layers.items():
        h = sum(node_value[n] for n in nodes) / total_value
        layer_heights[lv] = h
        max_layer_h = max(max_layer_h, h)

    x_stride = node_width * 2.5
    node_pos: Dict[Any, Tuple[float, float]] = {}
    for lv, nodes in layers.items():
        x = lv * x_stride
        y_cursor = (max_layer_h - layer_heights[lv]) / 2
        for n in nodes:
            h = node_value[n] / total_value
            node_pos[n] = (x, y_cursor)
            y_cursor += h + 0.02

    # 流出/流入偏移游标（用于流量带锚点）
    out_cursor: Dict[Any, float] = {n: 0.0 for n in node_list}
    in_cursor: Dict[Any, float] = {n: 0.0 for n in node_list}

    fig, ax = new_styled_figure(venue, palette, lang)

    # ── 流量带（先画，zorder 低于节点） ──
    for s, t, v in zip(src_arr, tgt_arr, val_arr):
        x_s, y_s = node_pos[s]
        x_t, y_t = node_pos[t]
        h_s = node_value[s] / total_value
        h_t = node_value[t] / total_value
        y_s0 = y_s + h_s - (out_cursor[s] + v / total_value)
        y_t0 = y_t + h_t - (in_cursor[t] + v / total_value)
        out_cursor[s] += v / total_value
        in_cursor[t] += v / total_value
        w = v / total_value
        # 垂直居中于带，半带宽
        b_s = w / 2
        b_t = w / 2
        xm = (x_s + node_width + x_t) / 2
        verts = [
            (x_s + node_width, y_s0 + b_s),
            (xm, y_s0 + b_s),
            (xm, y_t0 + b_t),
            (x_t, y_t0 + b_t),
            (x_t, y_t0 - b_t),
            (xm, y_t0 - b_t),
            (xm, y_s0 - b_s),
            (x_s + node_width, y_s0 - b_s),
        ]
        codes = [
            Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
            Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
        ]
        ax.add_patch(PathPatch(
            Path(verts, codes),
            facecolor=color_of[s], alpha=flow_alpha,
            edgecolor="none", zorder=1,
        ))

    # ── 节点矩形 ──
    for n in node_list:
        x, y = node_pos[n]
        h = node_value[n] / total_value
        ax.add_patch(Rectangle(
            (x, y), node_width, h,
            facecolor=color_of[n], alpha=node_alpha,
            edgecolor="white", linewidth=0.8, zorder=3,
        ))

    # ── 节点标签（末层在左，其余在右） ──
    fs = max(7, plt.rcParams.get("font.size", 9) - 1)
    for n in node_list:
        x, y = node_pos[n]
        h = node_value[n] / total_value
        if level[n] == max_level:
            ax.text(x - 0.005, y + h / 2, label_of[n],
                    ha="right", va="center", fontsize=fs, zorder=4)
        else:
            ax.text(x + node_width + 0.005, y + h / 2, label_of[n],
                    ha="left", va="center", fontsize=fs, zorder=4)

    ax.set_xlim(-0.3, max_level * x_stride + node_width + 0.3)
    ax.set_ylim(-0.05, max_layer_h + 0.08)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})
