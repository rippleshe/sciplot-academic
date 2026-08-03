"""
Round-20 tests for plot_hexbin (六边形密度图).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp


@pytest.fixture()
def hexbin_data():
    rng = np.random.default_rng(3)
    x = rng.normal(0, 1, 5000)
    y = rng.normal(0, 1, 5000) * 0.7 + x * 0.3
    return x, y


def test_hexbin_basic(hexbin_data, cleanup_figures):
    x, y = hexbin_data
    result = sp.plot_hexbin(x, y)
    assert result.fig is not None
    assert len(result.fig.axes) == 2  # 主图 + colorbar


def test_hexbin_log_bins(hexbin_data, cleanup_figures):
    x, y = hexbin_data
    result = sp.plot_hexbin(x, y, bins="log")
    assert result.fig is not None


def test_hexbin_gridsize_options(hexbin_data, cleanup_figures):
    x, y = hexbin_data
    result = sp.plot_hexbin(x, y, gridsize=15)
    hb = result.ax.collections[0]
    assert hb is not None


def test_hexbin_colorbar_label(hexbin_data, cleanup_figures):
    x, y = hexbin_data
    result = sp.plot_hexbin(x, y, colorbar_label="密度")
    assert result.fig.axes[-1].get_ylabel() == "密度"


def test_hexbin_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="不一致"):
        sp.plot_hexbin([1.0, 2.0, 3.0], [1.0, 2.0])


def test_hexbin_empty_raises(cleanup_figures):
    with pytest.raises(ValueError, match="不能为空"):
        sp.plot_hexbin([], [])


def test_hexbin_nan_raises(cleanup_figures):
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_hexbin([1.0, np.nan], [1.0, 2.0])


def test_hexbin_bad_gridsize_raises(hexbin_data, cleanup_figures):
    x, y = hexbin_data
    with pytest.raises(ValueError, match="gridsize"):
        sp.plot_hexbin(x, y, gridsize=0)
    with pytest.raises(ValueError, match="gridsize"):
        sp.plot_hexbin(x, y, gridsize=2.5)


def test_hexbin_bad_mincnt_raises(hexbin_data, cleanup_figures):
    x, y = hexbin_data
    with pytest.raises(ValueError, match="mincnt"):
        sp.plot_hexbin(x, y, mincnt=-1)


def test_hexbin_alias_and_export(hexbin_data, cleanup_figures):
    x, y = hexbin_data
    assert callable(sp.plot_hexbin)
    assert callable(sp.hexbin)
    assert "plot_hexbin" in sp.__all__ and "hexbin" in sp.__all__
    result = sp.hexbin(x, y)
    assert result.fig is not None


def test_hexbin_save_png(tmp_path, hexbin_data, cleanup_figures):
    x, y = hexbin_data
    result = sp.plot_hexbin(x, y, gridsize=25, bins="log")
    paths = result.save(str(tmp_path / "hexbin"), formats=("png",), dpi=100)
    assert paths[0].exists() and paths[0].stat().st_size > 0


def test_new_advanced_charts_dark_theme(hexbin_data, cleanup_figures):
    """新图表在暗色主题下均应正常工作。"""
    x, y = hexbin_data
    sp.setup_style("presentation", theme="dark")
    r1 = sp.plot_hexbin(x, y, gridsize=20)
    r2 = sp.plot_bubble(np.random.rand(20), np.random.rand(20),
                        size=np.random.rand(20) * 5)
    r3 = sp.plot_bubble_heatmap(np.random.rand(3, 4))
    assert r1.fig is not None and r2.fig is not None and r3.fig is not None
