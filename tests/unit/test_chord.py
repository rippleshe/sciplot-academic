"""
Round-34 tests for plot_chord (弦图).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp


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
    # 4 段弧 → 4 个 fill patch
    from matplotlib.patches import Polygon

    n_polys = sum(1 for p in result.ax.patches if isinstance(p, Polygon))
    assert n_polys == 4


def test_chord_labels(chord_matrix, cleanup_figures):
    result = sp.plot_chord(chord_matrix, labels=["北京", "上海", "广州", "深圳"])
    texts = [t.get_text() for t in result.ax.texts]
    assert "北京" in texts and "深圳" in texts


def test_chord_show_values(chord_matrix, cleanup_figures):
    result = sp.plot_chord(chord_matrix, labels=["A", "B", "C", "D"], show_values=True)
    texts = [t.get_text() for t in result.ax.texts]
    # 节点 A 双向总量 = (12+5+3) * 2 = 40
    assert "40" in texts


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
