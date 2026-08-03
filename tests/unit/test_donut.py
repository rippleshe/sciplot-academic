"""
Round-40 tests for plot_donut (环形图).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp


def test_donut_basic(cleanup_figures):
    result = sp.plot_donut(["A", "B", "C"], [55, 30, 15])
    assert result.fig is not None
    assert result.ax is not None


def test_donut_alias_and_export(cleanup_figures):
    assert callable(sp.plot_donut)
    assert callable(sp.donut)
    assert "plot_donut" in sp.__all__ and "donut" in sp.__all__
    result = sp.donut(["A", "B"], [60, 40])
    assert result.fig is not None


def test_donut_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="长度"):
        sp.plot_donut(["A", "B"], [1.0, 2.0, 3.0])


def test_donut_negative_raises(cleanup_figures):
    with pytest.raises(ValueError, match="不能包含负值"):
        sp.plot_donut(["A", "B"], [-1.0, 5.0])


def test_donut_nan_raises(cleanup_figures):
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_donut(["A", "B"], [np.nan, 5.0])


def test_donut_zero_sum_raises(cleanup_figures):
    with pytest.raises(ValueError, match="之和必须大于 0"):
        sp.plot_donut(["A", "B"], [0.0, 0.0])


def test_donut_hole_ratio_invalid_raises(cleanup_figures):
    with pytest.raises(ValueError, match="hole_ratio"):
        sp.plot_donut(["A", "B"], [5.0, 5.0], hole_ratio=1.2)


def test_donut_single_category(cleanup_figures):
    result = sp.plot_donut(["A"], [100.0], center_text="100")
    assert result.fig is not None


def test_donut_extreme_split(cleanup_figures):
    """5%/95% 极端占比（小扇区不写数值）不崩溃。"""
    result = sp.plot_donut(["A", "B"], [5.0, 95.0])
    assert result.fig is not None


def test_donut_custom_options(cleanup_figures):
    result = sp.plot_donut(
        ["A", "B", "C", "D"], [40, 30, 20, 10],
        colors=["#D62728", "#1F77B4", "#2CA02C", "#FF7F0E"],
        hole_ratio=0.5,
        show_values=True,
        show_percent=False,
        start_angle=0.0,
    )
    assert result.fig is not None


def test_donut_save_png(tmp_path, cleanup_figures):
    result = sp.plot_donut(["A", "B"], [70, 30])
    paths = sp.save(result.fig, tmp_path / "donut", formats=("png",))
    assert paths[0].exists()
