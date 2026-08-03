"""
Round-44 tests for plot_waterfall (瀑布图，增量分解).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp


def test_waterfall_basic(cleanup_figures):
    result = sp.plot_waterfall(["销售", "采购", "损耗"], [30.0, -15.0, -5.0],
                               start_value=80.0)
    assert result.fig is not None
    assert result.ax is not None


def test_waterfall_alias_and_export(cleanup_figures):
    assert callable(sp.plot_waterfall)
    assert callable(sp.waterfall)
    assert "plot_waterfall" in sp.__all__ and "waterfall" in sp.__all__
    result = sp.waterfall(["A", "B"], [10.0, -4.0])
    assert result.fig is not None


def test_waterfall_total_bar_present(cleanup_figures):
    """末位应存在“总计”条，且高度为累计值。"""
    result = sp.plot_waterfall(["A", "B"], [10.0, -4.0], start_value=5.0)
    labels = [t.get_text() for t in result.ax.get_xticklabels()]
    assert "总计" in labels
    # 累计 = 5 + 10 - 4 = 11
    bars = result.ax.patches
    last = bars[-1]
    assert abs(last.get_height() - 11.0) < 1e-9


def test_waterfall_bottoms_accumulate(cleanup_figures):
    """增量条底部应从起始值开始累计。"""
    result = sp.plot_waterfall(["A", "B"], [10.0, -4.0], start_value=5.0)
    bars = result.ax.patches
    assert abs(bars[0].get_y() - 5.0) < 1e-9       # 第一根从 start 起
    assert abs(bars[1].get_y() - 15.0) < 1e-9      # 第二根从 5+10 起
    assert abs(bars[2].get_y() - 0.0) < 1e-9       # 总计条从 0 起


def test_waterfall_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="长度"):
        sp.plot_waterfall(["A", "B"], [1.0, 2.0, 3.0])


def test_waterfall_nan_raises(cleanup_figures):
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_waterfall(["A", "B"], [np.nan, 2.0])


def test_waterfall_bad_start_raises(cleanup_figures):
    with pytest.raises(ValueError, match="start_value"):
        sp.plot_waterfall(["A"], [1.0], start_value=np.inf)


def test_waterfall_all_decrease(cleanup_figures):
    """全减量场景（如亏损分解）。"""
    result = sp.plot_waterfall(["A", "B", "C"], [-5.0, -3.0, -2.0], start_value=20.0)
    bars = result.ax.patches
    assert abs(bars[-1].get_height() - 10.0) < 1e-9  # 20-5-3-2=10


def test_waterfall_no_connectors(cleanup_figures):
    result = sp.plot_waterfall(["A", "B"], [5.0, 3.0], show_connectors=False)
    assert result.fig is not None


def test_waterfall_custom_colors(cleanup_figures):
    result = sp.plot_waterfall(
        ["A", "B"], [5.0, -2.0],
        increase_color="#1F77B4", decrease_color="#D62728", total_color="#333333",
    )
    assert result.fig is not None


def test_waterfall_save_png(tmp_path, cleanup_figures):
    result = sp.plot_waterfall(["A", "B", "C"], [10.0, 5.0, -3.0], start_value=20.0)
    paths = sp.save(result.fig, tmp_path / "waterfall", formats=("png",))
    assert paths[0].exists()
