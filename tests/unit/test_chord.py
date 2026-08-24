"""
Round-34 tests for plot_chord (弦图).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp
from sciplot._plots.advanced import _compute_chord_geometry


@pytest.fixture()
def chord_matrix():
    """4 节点对称流量矩阵。"""
    return np.array([
        [0, 12, 5, 3],
        [12, 0, 8, 2],
        [5, 8, 0, 6],
        [3, 2, 6, 0],
    ], dtype=float)


def test_chord_basic(chord_matrix, cleanup_figures):
    result = sp.plot_chord(chord_matrix, labels=["A", "B", "C", "D"])
    assert result.fig is not None
    # 4 个节点标签（弧段 + 弦均为 Polygon，以标签文本验证节点数）
    texts = [t.get_text() for t in result.ax.texts]
    assert "A" in texts and "D" in texts
    # 存在弧段填充（面积大）与弦填充
    from matplotlib.patches import Polygon

    n_polys = sum(1 for p in result.ax.patches if isinstance(p, Polygon))
    assert n_polys >= 4


def test_chord_labels(chord_matrix, cleanup_figures):
    result = sp.plot_chord(chord_matrix, labels=["北京", "上海", "广州", "深圳"])
    texts = [t.get_text() for t in result.ax.texts]
    assert "北京" in texts and "深圳" in texts


def test_chord_show_values(chord_matrix, cleanup_figures):
    result = sp.plot_chord(chord_matrix, labels=["A", "B", "C", "D"], show_values=True)
    texts = [t.get_text() for t in result.ax.texts]
    # 节点 A 双向总量 = (12+5+3) * 2 = 40；数值与标签组成稳定双行块。
    assert "A\n40" in texts


def test_chord_auto_labels(chord_matrix, cleanup_figures):
    result = sp.plot_chord(chord_matrix)
    texts = [t.get_text() for t in result.ax.texts]
    assert texts[:4] == ["1", "2", "3", "4"]


def test_chord_non_square_raises(cleanup_figures):
    with pytest.raises(ValueError, match="方阵"):
        sp.plot_chord(np.ones((3, 4)))


def test_chord_negative_raises(cleanup_figures):
    with pytest.raises(ValueError, match="负值"):
        sp.plot_chord(np.array([[0, -1], [1, 0]]))


def test_chord_zero_flow_raises(cleanup_figures):
    with pytest.raises(ValueError, match="总流量为零"):
        sp.plot_chord(np.zeros((3, 3)))


def test_chord_label_mismatch_raises(chord_matrix, cleanup_figures):
    with pytest.raises(ValueError, match="labels"):
        sp.plot_chord(chord_matrix, labels=["A", "B"])


def test_chord_bad_width_raises(chord_matrix, cleanup_figures):
    with pytest.raises(ValueError, match="width"):
        sp.plot_chord(chord_matrix, width=1.5)


def test_chord_single_node_raises(cleanup_figures):
    with pytest.raises(ValueError, match="至少需要 2 个"):
        sp.plot_chord(np.array([[5.0]]))


def test_chord_color_by_legend(chord_matrix, cleanup_figures):
    """color_by 分组应生成类别图例。"""
    result = sp.plot_chord(
        chord_matrix, labels=["A", "B", "C", "D"],
        color_by=["组1", "组1", "组2", "组2"],
    )
    legend = result.ax.get_legend()
    assert legend is not None
    texts = [t.get_text() for t in legend.get_texts()]
    assert texts == ["组1", "组2"]


def test_chord_min_flow_filter(chord_matrix, cleanup_figures):
    """min_flow 过滤小流量弦。"""
    result = sp.plot_chord(chord_matrix, labels=["A", "B", "C", "D"], min_flow=10.0)
    assert result.fig is not None


def test_chord_bad_min_flow_raises(chord_matrix, cleanup_figures):
    with pytest.raises(ValueError, match="min_flow"):
        sp.plot_chord(chord_matrix, min_flow=-1.0)
    with pytest.raises(ValueError, match="min_flow"):
        sp.plot_chord(chord_matrix, min_flow=np.nan)


def test_chord_bad_gap_raises(chord_matrix, cleanup_figures):
    with pytest.raises(ValueError, match="gap"):
        sp.plot_chord(chord_matrix, gap=-0.1)
    with pytest.raises(ValueError, match="gap"):
        sp.plot_chord(chord_matrix, gap=np.inf)
    with pytest.raises(ValueError, match="gap 过大"):
        sp.plot_chord(chord_matrix, gap=np.pi)


def test_chord_geometry_closes_exactly_one_circle(chord_matrix):
    """节点弧段 + 全部 gap 必须恰好占一圈，不能越过 2π 再重叠。"""
    gap = 0.03
    _, _, starts, ends, _, _ = _compute_chord_geometry(
        chord_matrix, min_flow=0.0, gap=gap
    )
    arc_total = float(np.sum(ends - starts))
    assert arc_total + len(starts) * gap == pytest.approx(2 * np.pi)
    assert ends[-1] + gap == pytest.approx(starts[0] + 2 * np.pi)


def test_chord_flow_slots_conserve_visible_flow(chord_matrix):
    """过滤后的每条流在源/目标两端都必须占用与其数值成比例的真实槽位。"""
    visible, totals, starts, ends, source_slots, target_slots = _compute_chord_geometry(
        chord_matrix, min_flow=6.0, gap=0.02
    )
    spans = ends - starts

    for node in range(len(totals)):
        if totals[node] <= 0:
            continue
        scale = spans[node] / totals[node]
        source_width = sum(
            b - a for (i, _), (a, b) in source_slots.items() if i == node
        )
        target_width = sum(
            b - a for (_, j), (a, b) in target_slots.items() if j == node
        )
        assert source_width + target_width == pytest.approx(spans[node])

        for (i, j), (a, b) in source_slots.items():
            if i == node:
                assert b - a == pytest.approx(float(visible[i, j]) * scale)
        for (i, j), (a, b) in target_slots.items():
            if j == node:
                assert b - a == pytest.approx(float(visible[i, j]) * scale)


def test_chord_min_flow_updates_visible_totals(chord_matrix, cleanup_figures):
    """show_values 应与实际绘制的过滤后流量一致，而不是继续显示被过滤流。"""
    result = sp.plot_chord(
        chord_matrix,
        labels=["A", "B", "C", "D"],
        min_flow=10.0,
        show_values=True,
    )
    texts = [t.get_text() for t in result.ax.texts]
    # 仅 0↔1 的 12 保留，因此 A/B 可见双向总量均为 24，C/D 为 0。
    assert "A\n24" in texts and "B\n24" in texts
    assert "C\n0" in texts and "D\n0" in texts


def test_chord_color_by_mismatch_raises(chord_matrix, cleanup_figures):
    with pytest.raises(ValueError, match="color_by"):
        sp.plot_chord(chord_matrix, labels=["A", "B", "C", "D"],
                      color_by=["x", "y"])


def test_chord_alias_and_export(chord_matrix, cleanup_figures):
    assert callable(sp.plot_chord)
    assert callable(sp.chord)
    assert "plot_chord" in sp.__all__ and "chord" in sp.__all__
    result = sp.chord(chord_matrix)
    assert result.fig is not None


def test_chord_save_png(tmp_path, chord_matrix, cleanup_figures):
    result = sp.plot_chord(chord_matrix, labels=["A", "B", "C", "D"])
    paths = result.save(str(tmp_path / "chord"), formats=("png",), dpi=100)
    assert paths[0].exists() and paths[0].stat().st_size > 0
