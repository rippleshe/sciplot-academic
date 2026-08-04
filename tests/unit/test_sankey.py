"""
Round-38 tests for plot_sankey (桑基图).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp


@pytest.fixture()
def flow_data():
    sources = ["能源", "能源", "材料", "转化", "转化", "人工"]
    targets = ["转化", "终端", "转化", "终端", "损耗", "终端"]
    values = [40.0, 10.0, 20.0, 15.0, 5.0, 8.0]
    return sources, targets, values


def test_sankey_basic(flow_data, cleanup_figures):
    sources, targets, values = flow_data
    result = sp.plot_sankey(sources, targets, values)
    assert result.fig is not None
    assert result.ax is not None


def test_sankey_alias_and_export(flow_data, cleanup_figures):
    sources, targets, values = flow_data
    assert callable(sp.plot_sankey)
    assert callable(sp.sankey)
    assert "plot_sankey" in sp.__all__ and "sankey" in sp.__all__
    result = sp.sankey(sources, targets, values)
    assert result.fig is not None


def test_sankey_labels_dict_and_colors(flow_data, cleanup_figures):
    sources, targets, values = flow_data
    labels = {"能源": "E", "转化": "T", "终端": "C", "材料": "M", "损耗": "W", "人工": "L"}
    result = sp.plot_sankey(
        sources, targets, values,
        labels=labels,
        node_colors=["#D62728", "#1F77B4", "#2CA02C", "#FF7F0E", "#9467BD", "#8C564B"],
    )
    assert result.fig is not None


def test_sankey_length_mismatch_raises(flow_data, cleanup_figures):
    sources, targets, values = flow_data
    with pytest.raises(ValueError, match="长度必须一致"):
        sp.plot_sankey(sources, targets[:-1], values)


def test_sankey_negative_values_raises(flow_data, cleanup_figures):
    sources, targets, values = flow_data
    values[0] = -1.0
    with pytest.raises(ValueError, match="不能包含负值"):
        sp.plot_sankey(sources, targets, values)


def test_sankey_nan_values_raises(flow_data, cleanup_figures):
    sources, targets, values = flow_data
    values[0] = np.nan
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_sankey(sources, targets, values)


def test_sankey_min_flow_filters(flow_data, cleanup_figures):
    sources, targets, values = flow_data
    result = sp.plot_sankey(sources, targets, values, min_flow=10.0)
    assert result.fig is not None


def test_sankey_min_flow_too_high_raises(flow_data, cleanup_figures):
    sources, targets, values = flow_data
    with pytest.raises(ValueError, match="min_flow"):
        sp.plot_sankey(sources, targets, values, min_flow=999.0)


def test_sankey_labels_length_mismatch_raises(flow_data, cleanup_figures):
    sources, targets, values = flow_data
    with pytest.raises(ValueError, match="labels 长度"):
        sp.plot_sankey(sources, targets, values, labels=["A", "B"])


def test_sankey_node_width_invalid_raises(flow_data, cleanup_figures):
    sources, targets, values = flow_data
    with pytest.raises(ValueError, match="node_width"):
        sp.plot_sankey(sources, targets, values, node_width=1.5)


def test_sankey_save_png(tmp_path, flow_data, cleanup_figures):
    sources, targets, values = flow_data
    result = sp.plot_sankey(sources, targets, values)
    paths = sp.save(result.fig, tmp_path / "sankey", formats=("png",))
    assert paths[0].exists()


def test_sankey_two_layer_chain(cleanup_figures):
    """单链结构（A→B→C）也能正确分层。"""
    result = sp.plot_sankey(
        ["A", "B"], ["B", "C"], [30.0, 30.0],
        labels=["源", "中转", "汇"],
    )
    assert result.fig is not None


def test_sankey_zero_values_ok(cleanup_figures):
    """零流量流被允许（不参与布局但对齐校验）。"""
    result = sp.plot_sankey(["A", "B"], ["B", "C"], [10.0, 0.0])
    assert result.fig is not None


def test_sankey_self_loop_no_hang(cleanup_figures):
    """自环（源==目标）不得导致层级分配死循环。"""
    result = sp.plot_sankey(["A", "A"], ["A", "B"], [5.0, 3.0])
    assert result.fig is not None
    result2 = sp.plot_sankey(["A"], ["A"], [10.0])
    assert result2.fig is not None


def test_sankey_min_node_height(cleanup_figures):
    """极小流量节点应提升到最小可见高度（不被间隙吞掉）。"""
    from matplotlib.patches import Rectangle

    src = ["A", "B", "C", "A", "B"]
    tgt = ["X", "Y", "X", "Y", "X"]
    val = [100.0, 1.0, 1.0, 60.0, 42.0]
    result = sp.plot_sankey(src, tgt, val)
    rects = [p for p in result.ax.patches if isinstance(p, Rectangle)]
    assert len(rects) == 5
    hs = sorted(r.get_height() for r in rects)
    assert hs[0] >= 0.010, f"最小节点条高 {hs[0]:.4f} 不可见"


def test_sankey_min_node_height_zero_disables(cleanup_figures):
    """min_node_height=0 时不做最小高度提升（保持原始比例）。"""
    from matplotlib.patches import Rectangle

    src = ["A", "B"]
    tgt = ["X", "Y"]
    val = [100.0, 1.0]
    result = sp.plot_sankey(src, tgt, val, min_node_height=0.0)
    rects = [p for p in result.ax.patches if isinstance(p, Rectangle)]
    hs = sorted(r.get_height() for r in rects)
    assert hs[0] < 0.01  # 原始比例下小节点仍很小


def test_sankey_label_collision_avoidance(cleanup_figures):
    """同层节点标签按 y 累积推挤，最小间距 0.045 不重叠。"""
    src = (["煤炭", "石油", "天然气", "水电", "风电", "核电", "太阳能", "生物质"]
           + ["电力转化"] * 4)
    tgt = ["电力转化"] * 8 + ["工业用电", "商业用电", "居民用电", "农业"]
    val = [180.0, 60.0, 30.0, 25.0, 15.0, 10.0, 8.0, 5.0, 150.0, 40.0, 30.0, 10.0]
    result = sp.plot_sankey(src, tgt, val)

    cols = {}
    for t in result.ax.texts:
        x, y = t.get_position()
        cols.setdefault(round(x, 2), []).append(y)
    for x, ys in cols.items():
        ys.sort()
        for i in range(len(ys) - 1):
            assert ys[i + 1] - ys[i] >= 0.044, f"x={x} 列标签重叠: {ys[i]:.3f}→{ys[i+1]:.3f}"
