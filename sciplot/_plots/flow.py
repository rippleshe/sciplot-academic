"""
Flow 家族图表 — 桑基图
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np

from sciplot._core.utils import cycle_color, get_cycle_colors, new_styled_figure, relative_fontsize
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
    min_node_height: float = 0.012,
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
        min_node_height: 节点最小可见高度（归一化，默认 0.012）。
                       极小流量节点提升到此高度，避免条高被间隙吞掉只剩标签

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

    # 节点高度：极小节点提升到 min_node_height（避免条高不可见）。
    # 提升后各层高度相应扩张，保证 ∑节点高 + 间隙 ≈ 层高。
    min_node_h = float(min_node_height)
    node_h_eff: Dict[Any, float] = {}
    for n in node_list:
        raw_h = node_value[n] / total_value
        node_h_eff[n] = max(raw_h, min_node_h)

    x_stride = node_width * 2.5
    node_pos: Dict[Any, Tuple[float, float]] = {}
    node_h_display: Dict[Any, float] = {}  # 实际绘制高度（含最小提升与收缩）
    for lv, nodes in layers.items():
        x = lv * x_stride
        # 层内节点高之和（含最小提升）+ 间隙
        raw_layer_h = sum(node_value[n] for n in nodes) / total_value
        eff_layer_h = sum(node_h_eff[n] for n in nodes)
        n_gaps = len(nodes) - 1
        # 若提升导致溢出，按比例收缩（保持相对大小）；
        # 但保证提升后的最小节点不被收缩回阈值以下
        avail = max(raw_layer_h, eff_layer_h + n_gaps * 0.02)
        scale = raw_layer_h / avail if avail > 0 else 1.0
        y_cursor = (max_layer_h - raw_layer_h) / 2
        for n in nodes:
            h = max(node_h_eff[n] * scale, min_node_h * 0.9)
            node_pos[n] = (x, y_cursor)
            node_h_display[n] = h
            y_cursor += h + 0.02

    # 流出/流入偏移游标（用于流量带锚点）
    out_cursor: Dict[Any, float] = {n: 0.0 for n in node_list}
    in_cursor: Dict[Any, float] = {n: 0.0 for n in node_list}

    fig, ax = new_styled_figure(venue, palette, lang)

    # ── 流量带（先画，zorder 低于节点） ──
    # 流带高度在源/目标侧分别按该节点自身流量归一化，
    # 保证 ∑流带高度 == 节点条高度（视觉严格对齐，无溢出残留）
    for s, t, v in zip(src_arr, tgt_arr, val_arr):
        x_s, y_s = node_pos[s]
        x_t, y_t = node_pos[t]
        h_s = node_h_display[s]
        h_t = node_h_display[t]
        # 节点内流量占比（避免流入≠流出时流带溢出节点条）
        out_total = max(outflow[s], 1e-12)
        in_total = max(inflow[t], 1e-12)
        frac_s = float(v) / out_total * h_s
        frac_t = float(v) / in_total * h_t
        y_s0 = y_s + h_s - (out_cursor[s] + frac_s)
        y_t0 = y_t + h_t - (in_cursor[t] + frac_t)
        out_cursor[s] += frac_s
        in_cursor[t] += frac_t
        # 半带宽：取两侧的平均（带在两端宽度一致，中间平滑过渡）
        b_s = frac_s / 2
        b_t = frac_t / 2
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
        h = node_h_display[n]
        ax.add_patch(Rectangle(
            (x, y), node_width, h,
            facecolor=color_of[n], alpha=node_alpha,
            edgecolor="white", linewidth=0.8, zorder=3,
        ))

    # ── 节点标签（末层在左，其余在右） ──
    fs = max(7, plt.rcParams.get("font.size", 9) - 1)

    # 标签避让：同层标签按 y 排序后累积推挤，保证最小文字间距
    min_label_gap = 0.045
    label_y: Dict[Any, float] = {}
    for lv in sorted(set(level.values())):
        layer_nodes = sorted(
            (n for n in node_list if level[n] == lv),
            key=lambda n: node_pos[n][1],
        )
        for i, n in enumerate(layer_nodes):
            y0 = node_pos[n][1] + node_h_display[n] / 2
            if i > 0:
                prev = layer_nodes[i - 1]
                y0 = max(y0, label_y[prev] + min_label_gap)
            label_y[n] = y0

    for n in node_list:
        x, y = node_pos[n]
        h = node_h_display[n]
        if level[n] == max_level:
            ax.text(x - 0.005, label_y[n], label_of[n],
                    ha="right", va="center", fontsize=fs, zorder=4)
        else:
            ax.text(x + node_width + 0.005, label_y[n], label_of[n],
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


# ============================================================================
# 瀑布图（Waterfall，增量分解）
# ============================================================================

def plot_waterfall(
    categories: List[str],
    values: np.ndarray,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    start_value: float = 0.0,
    show_connectors: bool = True,
    show_values: bool = True,
    fmt: str = ".1f",
    increase_color: str = "#2E8B57",
    decrease_color: str = "#D64541",
    total_color: str = "#4A4A4A",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制瀑布图（Waterfall Chart，增量分解）。

    财务/预算/误差分析的经典图表：从起始值出发，每个增量（绿）与
    减量（红）依次堆叠，末位显示最终总计条（深灰），
    累计值用虚线连接。Plotly 单列一类的经典图表。

    参数:
        categories    : 各增量/减量的名称（最后自动追加“总计”条）
        values        : 各步增量（正数=增加，负数=减少）
        start_value   : 起始值（如初始库存/预算）
        show_connectors: 是否显示累计虚线连接线
        show_values   : 是否在条形上显示数值
        increase_color/ decrease_color/ total_color: 增/减/总计三色

    示例:
        >>> fig, ax = sp.plot_waterfall(
        ...     ["期初", "销售", "采购", "损耗"], [100, 30, -15, -5],
        ...     start_value=80,
        ... )
    """
    cat_arr = list(categories)
    val_arr = np.asarray(values, dtype=float).ravel()
    if len(cat_arr) != len(val_arr):
        raise ValueError(
            f"categories 长度 ({len(cat_arr)}) 与 values 长度 ({len(val_arr)}) 不一致"
        )
    if len(cat_arr) == 0:
        raise ValueError("categories/values 不能为空")
    if not np.all(np.isfinite(val_arr)):
        raise ValueError("values 不能包含 NaN 或 Inf")
    if not np.isfinite(start_value):
        raise ValueError("start_value 必须是有限数值")

    # 累计轨迹
    cum = float(start_value)
    bottoms: List[float] = []
    for v in val_arr:
        bottoms.append(cum)
        cum += float(v)
    total = cum

    # 条形颜色与高度（增加/减少/总计）
    bar_colors = [increase_color if v >= 0 else decrease_color for v in val_arr]
    bar_colors.append(total_color)
    bar_heights = [abs(v) for v in val_arr] + [abs(total)]
    bar_bottoms = bottoms + [0.0]
    bar_cats = cat_arr + ["总计"]

    # 是否显示起始条（标准瀑布图结构：起始值也画一条浅色基准条）
    show_start = start_value != 0.0
    if show_start:
        bar_colors = ["#C8CDD3"] + bar_colors
        bar_heights = [abs(start_value)] + bar_heights
        bar_bottoms = [0.0] + bar_bottoms
        bar_cats = ["期初"] + bar_cats

    fig, ax = new_styled_figure(venue, palette, lang)

    x_pos = np.arange(len(bar_cats))
    bars = ax.bar(x_pos, bar_heights, bottom=bar_bottoms, color=bar_colors,
                  edgecolor="white", linewidth=0.8, width=0.62, **kwargs)
    for b in bars:
        b.set_zorder(2)

    # 累计连接线：从每个条顶端连到下一个条的基准（标准瀑布连接）
    if show_connectors and len(bottoms) > 1:
        offset = 1 if show_start else 0
        cum_pts = [float(start_value)] + [b + h for b, h in zip(bottoms, [abs(v) for v in val_arr])]
        for i in range(len(cum_pts) - 1):
            # 水平段：当前条顶端 → 下一条 x 位置（同高度）
            ax.plot([x_pos[i] + offset, x_pos[i + 1] + offset], [cum_pts[i], cum_pts[i]],
                    color="#999999", linestyle="--", linewidth=0.9, zorder=1)

    # 数值标注（正值在条顶上方，负值在条底下方，避免重叠）
    if show_values:
        fs = relative_fontsize(-1, floor=6)
        span = max(bar_heights) if bar_heights else 1.0
        if show_start:
            value_labels = [float(start_value)] + [float(x) for x in val_arr] + [total]
        else:
            value_labels = [float(x) for x in val_arr] + [total]
        for xi, (h, btm, v) in enumerate(zip(bar_heights, bar_bottoms, value_labels)):
            if v >= 0:
                label_y = btm + h + 0.03 * span
                va = "bottom"
            else:
                label_y = btm - 0.03 * span
                va = "top"
            ax.text(xi, label_y, f"{v:{fmt}}", ha="center",
                    fontsize=fs, va=va, color="#333333", zorder=3)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(bar_cats, rotation=25, ha="right")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_alluvial(
    stages: Sequence[Sequence[str]],
    flows: Sequence[Sequence[Tuple[int, int, float]]],
    title: str = "",
    node_colors: Optional[Sequence[str]] = None,
    flow_alpha: float = 0.55,
    node_width: float = 0.06,
    label_size: Optional[int] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制冲积图（Alluvial Diagram，多阶段类别流动）

    各阶段为竖直列，列内类别堆叠为水平条；相邻阶段的类别
    之间用贝塞尔流带连接，流带宽度正比于流量。
    适合展示人群/样本在多分类间的迁移（如 分组→响应→结局）。

    参数:
        stages : 各阶段的类别名列表，如 [["A", "B"], ["X", "Y", "Z"]]
        flows  : 相邻阶段间流量，每阶段对一组 (源索引, 目标索引, 流量)：
                 flows[0] 描述 stages[0]→stages[1]，依此类推
        node_colors: 各阶段类别颜色（扁平列表，按阶段顺序拼接）；
                     None 用当前配色循环
        flow_alpha: 流带不透明度
        node_width: 节点条宽度（归一化坐标）
        label_size: 类别标签字号；None 继承 rcParams

    示例:
        >>> # 队列研究：基线分组 → 干预 → 结局 的三阶段迁移
        >>> fig, ax = sp.plot_alluvial(
        ...     stages=[["对照", "治疗"], ["完成", "脱落", "继续"], ["改善", "无变化"]],
        ...     flows=[
        ...         [(0, 0, 60), (0, 1, 10), (1, 0, 40), (1, 2, 60)],
        ...         [(0, 0, 70), (1, 1, 10), (2, 1, 20), (2, 0, 40)],
        ...     ],
        ... )
        >>> sp.save(fig, "alluvial")
    """
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path

    stage_list = [list(s) for s in stages]
    n_stages = len(stage_list)
    if n_stages < 2:
        raise ValueError("stages 至少需要两个阶段")
    if any(len(s) == 0 for s in stage_list):
        raise ValueError("每个阶段至少需要一个类别")
    if not 0.0 <= flow_alpha <= 1.0:
        raise ValueError(f"flow_alpha 必须在 [0, 1] 范围内，实际值: {flow_alpha!r}")
    if not 0.0 < node_width < 0.5:
        raise ValueError(f"node_width 必须在 (0, 0.5) 范围内，实际值: {node_width!r}")

    # flows 容错：允许扁平三元组列表（两阶段时的便捷写法）
    if flows and isinstance(flows[0], tuple) and len(flows[0]) == 3:
        flow_groups: List[List[Tuple[int, int, float]]] = [list(flows)]  # type: ignore[arg-type]
    else:
        flow_groups = [list(g) for g in flows]

    if len(flow_groups) != n_stages - 1:
        raise ValueError(
            f"flows 长度 ({len(flow_groups)}) 必须为阶段数减一 ({n_stages - 1})"
        )
    for si, flow_group in enumerate(flow_groups):
        n_src = len(stage_list[si])
        n_dst = len(stage_list[si + 1])
        for src_idx, dst_idx, val in flow_group:
            if not (0 <= src_idx < n_src):
                raise ValueError(f"flows[{si}] 源索引 {src_idx} 超出阶段 {si} 范围")
            if not (0 <= dst_idx < n_dst):
                raise ValueError(f"flows[{si}] 目标索引 {dst_idx} 超出阶段 {si + 1} 范围")
            if not np.isfinite(val) or val < 0:
                raise ValueError(f"flows[{si}] 流量必须为非负有限值，实际: {val!r}")

    # 先应用 venue/palette，再读取颜色循环；否则显式 palette 参数会被上一张
    # 图遗留的 rcParams 颜色吞掉，造成“参数传了但颜色没变”的隐蔽 bug。
    fig, ax = new_styled_figure(venue, palette, lang)
    colors = get_cycle_colors()
    if node_colors is None:
        flat_colors: List[str] = []
        for s in stage_list:
            for j in range(len(s)):
                flat_colors.append(cycle_color(colors, len(flat_colors)))
    else:
        flat_colors = list(node_colors)
        expected = sum(len(s) for s in stage_list)
        if len(flat_colors) != expected:
            raise ValueError(
                f"node_colors 长度 ({len(flat_colors)}) 与类别总数 ({expected}) 不一致"
            )

    # 每阶段类别颜色
    stage_colors: List[List[str]] = []
    idx = 0
    for s in stage_list:
        stage_colors.append(flat_colors[idx:idx + len(s)])
        idx += len(s)

    # 每阶段：先算类别总流入/流出，确定节点条高度
    x_positions = np.linspace(0.0, 1.0, n_stages)
    node_totals: List[List[float]] = []
    for si in range(n_stages):
        totals = [0.0] * len(stage_list[si])
        if si > 0:
            for src_idx, dst_idx, val in flow_groups[si - 1]:
                totals[dst_idx] += float(val)
        if si < n_stages - 1:
            for src_idx, dst_idx, val in flow_groups[si]:
                totals[src_idx] += float(val)
        node_totals.append(totals)

    # 节点条 y 区间（自顶向下堆叠，归一化）
    node_y: List[List[Tuple[float, float]]] = []
    for si in range(n_stages):
        total = sum(node_totals[si])
        if total <= 0:
            total = 1.0
        intervals: List[Tuple[float, float]] = []
        cursor = 1.0
        for t in node_totals[si]:
            h = t / total
            intervals.append((cursor - h, cursor))
            cursor -= h
        node_y.append(intervals)

    fs = label_size if label_size is not None \
        else relative_fontsize(-1, floor=7)

    # 绘制流带（先画，垫底）
    for si in range(n_stages - 1):
        x0, x1 = x_positions[si], x_positions[si + 1]
        gap = x1 - x0
        # 流带在节点条内部的 y 区间：按流量细分
        src_y = node_y[si]
        dst_y = node_y[si + 1]
        # 记录每个类别已用偏移量（从区间顶部开始分配）
        src_cursor = [y_hi for (_, y_hi) in src_y]
        dst_cursor = [y_hi for (_, y_hi) in dst_y]
        for src_idx, dst_idx, val in flow_groups[si]:
            v = float(val)
            # 源侧：按类别内流量比例分配流带（从上往下连续分配）
            src_lo, src_hi = src_y[src_idx]
            src_span = src_hi - src_lo
            src_total = max(sum(x[2] for x in flow_groups[si] if x[0] == src_idx), 1e-12)
            src_frac = v / src_total
            band_h = src_span * src_frac
            yA0 = src_cursor[src_idx] - band_h
            yA1 = src_cursor[src_idx]
            src_cursor[src_idx] = yA0

            dst_span = dst_y[dst_idx][1] - dst_y[dst_idx][0]
            dst_total = max(sum(x[2] for x in flow_groups[si] if x[1] == dst_idx), 1e-12)
            dst_frac = v / dst_total
            band_h2 = dst_span * dst_frac
            yB0 = dst_cursor[dst_idx] - band_h2
            yB1 = dst_cursor[dst_idx]
            dst_cursor[dst_idx] = yB0

            # 贝塞尔曲线流带
            c = stage_colors[si][src_idx]
            # 一个完整的闭合 ribbon：上下边界各由一段三次贝塞尔连接。
            # CURVE4 必须以 3 个顶点为一组（控制点1、控制点2、终点）。
            # 旧实现下边界少了终点且没有 CLOSEPOLY，虽然能渲染，但会出现
            # 斜切/漏口等不稳定形状，尤其在多流带密集时明显。
            x_left = x0 + node_width / 2
            x_right = x1 - node_width / 2
            c1 = x0 + gap * 0.38
            c2 = x1 - gap * 0.38
            verts = [
                (x_left, yA0),
                (x_left, yA1),
                (c1, yA1),
                (c2, yB1),
                (x_right, yB1),
                (x_right, yB0),
                (c2, yB0),
                (c1, yA0),
                (x_left, yA0),
                (x_left, yA0),
            ]
            codes = [
                Path.MOVETO,
                Path.LINETO,
                Path.CURVE4, Path.CURVE4, Path.CURVE4,
                Path.LINETO,
                Path.CURVE4, Path.CURVE4, Path.CURVE4,
                Path.CLOSEPOLY,
            ]
            path = Path(verts, codes)
            patch = PathPatch(path, facecolor=c, edgecolor="none",
                              alpha=flow_alpha, zorder=1)
            ax.add_patch(patch)

    # 节点条（覆盖流带边缘）
    for si in range(n_stages):
        x0 = x_positions[si]
        for j, (ylo, yhi) in enumerate(node_y[si]):
            ax.add_patch(PathPatch(
                Path([(x0 - node_width / 2, ylo),
                      (x0 + node_width / 2, ylo),
                      (x0 + node_width / 2, yhi),
                      (x0 - node_width / 2, yhi),
                      (x0 - node_width / 2, ylo)]),
                facecolor=stage_colors[si][j], edgecolor="white",
                linewidth=0.8, zorder=2,
            ))
            # 类别标签
            ax.text(x0 - node_width / 2 - 0.012, (ylo + yhi) / 2,
                    stage_list[si][j], va="center", ha="right",
                    fontsize=fs, color="#333333", clip_on=False)

    ax.set_xlim(-0.02 - node_width, 1.02 + node_width)
    ax.set_ylim(-0.02, 1.02)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    if title:
        ax.set_title(title)
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})
