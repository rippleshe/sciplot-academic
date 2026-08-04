"""
集合关系图表 — UpSet Plot（集合交集可视化）

UpSet 图（Lex et al., 2014）是韦恩图在高维集合下的替代方案：
- 左侧：每个集合的大小（水平柱）
- 顶部：每个交集的规模（垂直柱）
- 中部：点阵图表示交集包含哪些集合

当集合数量 > 3 时，韦恩图无法清晰表达交集结构，UpSet 图
成为顶刊中的标准选择（组学、行为学、分类学等）。
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np

from sciplot._core.utils import cycle_color, get_cycle_colors, new_styled_figure, relative_fontsize
from sciplot._core.result import PlotResult

# 集合输入类型：Dict[集合名, 元素序列]
SetDict = Dict[str, Sequence[Any]]


def plot_upset(
    sets: Union[SetDict, Sequence[Sequence[Any]]],
    set_names: Optional[List[str]] = None,
    min_degree: int = 2,
    max_intersections: int = 15,
    title: str = "",
    set_color: Optional[str] = None,
    intersection_color: Optional[str] = None,
    show_counts: bool = True,
    show_degree_labels: bool = True,
    sort_by: str = "size",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    绘制 UpSet 图（集合交集可视化，韦恩图的替代方案）

    支持任意数量集合（3 个以上时优势明显）。布局遵循 UpSet
    经典结构：左侧集合大小柱 + 顶部交集大小柱 + 中部点阵。

    参数:
        sets      : 集合数据。两种形式：
                    - Dict[集合名, 元素列表]
                    - 元素列表的列表（需配合 set_names）
        set_names : 集合名列表（sets 为列表形式时必填）
        min_degree: 只展示至少包含该数量集合的交集（默认 2，排除单一集合）
        max_intersections: 最多展示多少个交集（按大小排序后截断）
        sort_by   : 交集排序方式：'size'（交集大小，默认）| 'degree'（集合数）
        set_color : 左侧集合柱颜色；None 用配色循环
        intersection_color: 顶部交集柱颜色；None 用深蓝灰

    示例:
        >>> # 三个数据源的基因交集
        >>> fig, ax = sp.plot_upset({
        ...     "RNA-seq":  {"G1", "G2", "G3", "G4", "G5"},
        ...     "Proteomics": {"G3", "G4", "G5", "G6"},
        ...     "ChIP-seq": {"G1", "G3", "G5", "G7"},
        ... })
        >>> sp.save(fig, "upset")

        >>> # 列表形式（自动取元素）
        >>> fig, ax = sp.plot_upset(
        ...     [["G1", "G2", "G3"], ["G2", "G3", "G4"], ["G3", "G4", "G5"]],
        ...     set_names=["数据集 A", "数据集 B", "数据集 C"],
        ... )
    """
    # ── 输入规范化 ──
    if isinstance(sets, dict):
        if not sets:
            raise ValueError("sets 不能为空")
        names = list(sets.keys())
        element_lists = [list(v) for v in sets.values()]
    else:
        seq = list(sets)
        if not seq:
            raise ValueError("sets 不能为空")
        if set_names is None:
            raise ValueError("sets 为列表形式时必须提供 set_names")
        if len(set_names) != len(seq):
            raise ValueError(
                f"set_names 长度 ({len(set_names)}) 与 sets 组数 ({len(seq)}) 不一致"
            )
        names = list(set_names)
        element_lists = [list(s) for s in seq]

    n_sets = len(names)
    if n_sets < 2:
        raise ValueError("至少需要两个集合")
    if min_degree < 1:
        raise ValueError(f"min_degree 必须为正整数，实际值: {min_degree!r}")
    if max_intersections < 1:
        raise ValueError(f"max_intersections 必须为正整数，实际值: {max_intersections!r}")
    if sort_by not in {"size", "degree"}:
        raise ValueError(f"sort_by 必须是 'size' 或 'degree'，实际值: {sort_by!r}")

    # ── 计算各集合与所有交集 ──
    sets_of_elements: Dict[Any, List[int]] = {}
    for si, elems in enumerate(element_lists):
        for e in elems:
            sets_of_elements.setdefault(e, []).append(si)

    set_sizes = [len(s) for s in element_lists]

    # 枚举所有交集组合（从 degree 高到低，或按大小）
    all_combos: List[Tuple[Tuple[int, ...], int]] = []
    for degree in range(n_sets, 0, -1):
        for combo in combinations(range(n_sets), degree):
            members = [
                e for e, member_sets in sets_of_elements.items()
                if all(i in member_sets for i in combo)
                and not any(i in member_sets for i in range(n_sets) if i not in combo)
            ]
            if members:
                all_combos.append((combo, len(members)))

    # 过滤最小集合数
    all_combos = [c for c in all_combos if len(c[0]) >= min_degree]
    if not all_combos:
        raise ValueError("没有满足 min_degree 的交集，请降低 min_degree")

    # 排序与截断
    if sort_by == "degree":
        all_combos.sort(key=lambda c: (len(c[0]), c[1]), reverse=True)
    else:
        all_combos.sort(key=lambda c: (c[1], len(c[0])), reverse=True)
    combos = all_combos[:max_intersections]

    # ── 布局：左侧集合柱 + 右侧主区 ──
    n_inters = len(combos)
    fig = plt.figure(figsize=(6.0 + n_inters * 0.55, 5.4))
    # 左列宽 22%，主区 78%；上行 58%（交集柱），下行 42%（点阵）
    gs = fig.add_gridspec(2, 2, width_ratios=[0.22, 0.78],
                          height_ratios=[0.58, 0.42],
                          hspace=0.08, wspace=0.06)
    ax_set = fig.add_subplot(gs[0, 0])
    ax_main = fig.add_subplot(gs[1, 1])
    ax_bar = fig.add_subplot(gs[0, 1], sharex=ax_main)

    cycle = get_cycle_colors()
    if set_color is not None:
        set_colors = [set_color] * n_sets
    else:
        set_colors = [cycle_color(cycle, i) for i in range(n_sets)]
    inter_color = intersection_color or "#4A6B8A"

    fs_small = relative_fontsize(-2, floor=6)
    fs_tiny = relative_fontsize(-3, floor=5)

    # ── 左：集合大小（水平柱，从上到下，柱尾数值标签） ──
    y_set = np.arange(n_sets)
    ax_set.barh(y_set, set_sizes, color=set_colors,
                edgecolor="white", linewidth=0.8, height=0.62, zorder=2)
    ax_set.set_yticks(y_set)
    ax_set.set_yticklabels(names, fontsize=fs_small)
    ax_set.invert_yaxis()
    ax_set.set_xlabel("集合大小", fontsize=relative_fontsize(-1))
    ax_set.tick_params(axis="x", labelsize=fs_tiny)
    ax_set.tick_params(direction="in")
    ax_set.set_xlim(0, max(set_sizes) * 1.22)
    for spine in ["top", "right"]:
        ax_set.spines[spine].set_visible(False)
    # 柱尾数值
    if show_counts:
        for yi, s in enumerate(set_sizes):
            ax_set.text(s + max(set_sizes) * 0.015, yi, str(int(s)),
                        va="center", ha="left", fontsize=fs_tiny,
                        color="#555555")

    # ── 主区 x 轴：每个交集一个槽位 ──
    x_pos = np.arange(n_inters)
    # 与左侧柱相同的 y 顺序
    ax_main.set_ylim(-0.6, n_sets - 0.4)
    ax_main.invert_yaxis()
    ax_main.set_xlim(-0.5, n_inters - 0.5)

    # 点阵：先画连线（垫底），再画圆点
    for ci, (combo, size) in enumerate(combos):
        combo_sorted = sorted(combo)
        for a, b in zip(combo_sorted[:-1], combo_sorted[1:]):
            # 相邻集合才连线（经典 UpSet 约定：连续成员连成线段）
            if b == a + 1:
                ax_main.plot([ci, ci], [a, b], color="#2C3E50",
                             linewidth=2.6, zorder=1, solid_capstyle="round")
    for ci, (combo, size) in enumerate(combos):
        for si in range(n_sets):
            if si in combo:
                ax_main.scatter(ci, si, s=120, color="#2C3E50",
                                edgecolors="white", linewidths=1.2,
                                zorder=3)
            else:
                ax_main.scatter(ci, si, s=120, facecolors="none",
                                edgecolors="#C8CDD3", linewidths=1.0,
                                zorder=2)

    ax_main.set_xticks(x_pos)
    ax_main.set_xticklabels([])
    ax_main.set_yticks([])
    ax_main.tick_params(direction="in")

    # ── 顶：交集大小柱（默认渐变蓝，显式 intersection_color 时用单色） ──
    sizes = [c[1] for c in combos]
    if intersection_color is None:
        cmap_sizes = plt.cm.get_cmap("Blues")
        bar_colors = [cmap_sizes(0.45 + 0.5 * s / max(sizes)) for s in sizes]
    else:
        bar_colors = [inter_color] * n_inters
    ax_bar.bar(x_pos, sizes, color=bar_colors,
               edgecolor="white", linewidth=0.8, width=0.66, zorder=2)
    ax_bar.set_ylim(0, max(sizes) * 1.25)
    ax_bar.set_ylabel("交集大小", fontsize=relative_fontsize(-1))
    ax_bar.tick_params(axis="x", labelbottom=False)
    ax_bar.tick_params(axis="y", labelsize=fs_tiny)
    ax_bar.tick_params(direction="in")
    for spine in ["top", "right"]:
        ax_bar.spines[spine].set_visible(False)
    ax_bar.set_xticks(x_pos)

    # 柱顶数值（加粗）
    if show_counts:
        for xi, s in enumerate(sizes):
            ax_bar.text(xi, s + max(sizes) * 0.03, str(int(s)),
                        ha="center", va="bottom", fontsize=fs_small,
                        color="#2C3E50", fontweight="bold")

    # 底部分组标签（集合成员的并集名，如 "A&B"；过长按显示宽度截断）
    if show_degree_labels:
        fs_bottom = fs_tiny
        max_chars = max(10, int(18 / max(1.0, n_inters / 4.0)))

        def _disp_w(s: str) -> int:
            """近似显示宽度：中文/全角按 2 计，其余按 1。"""
            return sum(2 if ord(c) > 0x2E80 else 1 for c in s)

        for ci, (combo, size) in enumerate(combos):
            label = "&".join(names[i] for i in combo)
            if _disp_w(label) > max_chars:
                # 按显示宽度预算从头部截断，省略号计入预算
                out = ""
                for c in label:
                    if _disp_w(out + c) + 1 > max_chars:
                        break
                    out += c
                label = out + "…"
            ax_main.text(ci, n_sets + 0.42, label,
                         ha="center", va="top", fontsize=fs_bottom,
                         color="#555555")

    # 隐藏边框
    for ax in (ax_main,):
        for spine in ax.spines.values():
            spine.set_visible(False)

    if title:
        fig.suptitle(title, fontsize=relative_fontsize(1), y=0.99)

    return PlotResult(fig, ax_main, metadata={
        "venue": venue, "palette": palette,
        "axes": {"set": ax_set, "bar": ax_bar, "main": ax_main},
        "intersections": [(names[i] for i in combo) for combo, _ in combos],
        "sizes": sizes,
    })
