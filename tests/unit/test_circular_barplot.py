"""
Round-43 tests for plot_circular_barplot (环形条形图).
"""

from __future__ import annotations

import numpy as np
import pytest
from matplotlib.colors import to_hex

import sciplot as sp


def test_circular_barplot_basic(cleanup_figures):
    result = sp.plot_circular_barplot(["A", "B", "C", "D"], [4.0, 9.0, 7.0, 3.0])
    assert result.fig is not None
    assert result.ax is not None


def test_circular_barplot_alias_and_export(cleanup_figures):
    assert callable(sp.plot_circular_barplot)
    assert callable(sp.circular_barplot)
    assert "plot_circular_barplot" in sp.__all__
    assert "circular_barplot" in sp.__all__
    result = sp.circular_barplot(["A", "B"], [5.0, 3.0])
    assert result.fig is not None


def test_circular_barplot_sort_default_descending(cleanup_figures):
    """默认按值降序：第一个条形是最长值。"""
    result = sp.plot_circular_barplot(["A", "B"], [3.0, 9.0])
    bars = result.ax.patches[:2]
    # 排序后 B(9) 在前；A(3) 在后
    assert bars[0].get_height() >= bars[1].get_height()


def test_circular_barplot_no_sort(cleanup_figures):
    result = sp.plot_circular_barplot(["A", "B"], [3.0, 9.0], sort=False)
    bars = result.ax.patches[:2]
    assert bars[0].get_height() < bars[1].get_height()


def test_circular_barplot_palette_argument_is_applied_before_color_cycle(cleanup_figures):
    """显式 palette 必须决定当前图颜色，不能沿用上一张图的 rcParams。"""
    sp.setup_style("nature", "pastel")
    result = sp.plot_circular_barplot(
        ["A", "B", "C"], [3.0, 2.0, 1.0], palette="ocean", sort=False,
    )
    expected = sp.get_palette("ocean")[0]
    actual = to_hex(result.ax.patches[0].get_facecolor(), keep_alpha=False)
    assert actual.lower() == expected.lower()


def test_circular_barplot_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="长度"):
        sp.plot_circular_barplot(["A", "B"], [1.0, 2.0, 3.0])


def test_circular_barplot_negative_raises(cleanup_figures):
    with pytest.raises(ValueError, match="不能包含负值"):
        sp.plot_circular_barplot(["A", "B"], [-1.0, 5.0])


def test_circular_barplot_nan_raises(cleanup_figures):
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_circular_barplot(["A", "B"], [np.nan, 5.0])


def test_circular_barplot_colors_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="colors 长度"):
        sp.plot_circular_barplot(["A", "B", "C"], [1, 2, 3], colors=["#D62728"])


def test_circular_barplot_show_values(cleanup_figures):
    result = sp.plot_circular_barplot(
        ["A", "B", "C"], [4.0, 9.0, 7.0], show_values=True, fmt=".1f"
    )
    assert result.fig is not None


def test_circular_barplot_save_png(tmp_path, cleanup_figures):
    result = sp.plot_circular_barplot(["A", "B", "C", "D", "E"], [3, 5, 8, 6, 4])
    paths = sp.save(result.fig, tmp_path / "circular_bar", formats=("png",))
    assert paths[0].exists()
