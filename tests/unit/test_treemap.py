"""
Round-39 tests for plot_treemap (矩形树图).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp
from sciplot._plots.proportions import _treemap_layout


def test_treemap_basic(cleanup_figures):
    result = sp.plot_treemap(["A", "B", "C", "D"], [40, 30, 20, 10])
    assert result.fig is not None
    assert result.ax is not None


def test_treemap_alias_and_export(cleanup_figures):
    assert callable(sp.plot_treemap)
    assert callable(sp.treemap)
    assert "plot_treemap" in sp.__all__ and "treemap" in sp.__all__
    result = sp.treemap(["A", "B"], [60, 40])
    assert result.fig is not None


def test_treemap_layout_areas():
    """squarify 布局面积总和应等于容器面积。"""
    rects = _treemap_layout([40.0, 30.0, 20.0, 10.0], 0, 0, 1, 1)
    assert len(rects) == 4
    total_area = sum(w * h for _, _, w, h in rects)
    assert abs(total_area - 1.0) < 1e-9
    # 顺序对应
    assert abs(rects[0][2] * rects[0][3] - 0.4) < 1e-9
    assert abs(rects[3][2] * rects[3][3] - 0.1) < 1e-9


def test_treemap_layout_inside_container():
    rects = _treemap_layout([5.0, 3.0, 2.0], 0, 0, 1, 1)
    for x, y, w, h in rects:
        assert x >= -1e-9 and y >= -1e-9
        assert x + w <= 1 + 1e-9 and y + h <= 1 + 1e-9


def test_treemap_layout_empty():
    assert _treemap_layout([], 0, 0, 1, 1) == []


def test_treemap_layout_zero_total_raises():
    with pytest.raises(ValueError, match="之和必须大于 0"):
        _treemap_layout([0.0, 0.0], 0, 0, 1, 1)


def test_treemap_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="长度"):
        sp.plot_treemap(["A", "B"], [1.0, 2.0, 3.0])


def test_treemap_negative_raises(cleanup_figures):
    with pytest.raises(ValueError, match="不能包含负值"):
        sp.plot_treemap(["A", "B"], [-1.0, 5.0])


def test_treemap_nan_raises(cleanup_figures):
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_treemap(["A", "B"], [np.nan, 5.0])


def test_treemap_zero_sum_raises(cleanup_figures):
    with pytest.raises(ValueError, match="之和必须大于 0"):
        sp.plot_treemap(["A", "B"], [0.0, 0.0])


def test_treemap_custom_colors(cleanup_figures):
    result = sp.plot_treemap(
        ["A", "B"], [60, 40],
        colors=["#D62728", "#1F77B4"],
        show_values=True, fmt=".1f",
    )
    assert result.fig is not None


def test_treemap_colors_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="colors 长度"):
        sp.plot_treemap(["A", "B", "C"], [1, 2, 3], colors=["#D62728"])


def test_treemap_save_png(tmp_path, cleanup_figures):
    result = sp.plot_treemap(["A", "B", "C"], [50, 30, 20])
    paths = sp.save(result.fig, tmp_path / "treemap", formats=("png",))
    assert paths[0].exists()


def test_treemap_many_categories(cleanup_figures):
    """多类别（>10）布局稳定。"""
    rng = np.random.default_rng(3)
    vals = rng.uniform(1, 100, 20)
    cats = [f"类{i}" for i in range(20)]
    result = sp.plot_treemap(cats, vals)
    assert result.fig is not None


def test_treemap_single_category(cleanup_figures):
    result = sp.plot_treemap(["A"], [100.0])
    assert result.fig is not None


def test_treemap_extreme_skew(cleanup_figures):
    """1 个大值 + 30 个小值的极端分布（布局稳定）。"""
    rng = np.random.default_rng(1)
    vals = np.r_[500.0, rng.uniform(1, 5, 30)]
    cats = [f"C{i}" for i in range(31)]
    result = sp.plot_treemap(cats, vals)
    assert result.fig is not None
