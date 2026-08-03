"""
Round-24 tests for plot_marginal (边际分布图).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp


@pytest.fixture()
def marginal_data():
    rng = np.random.default_rng(5)
    x = rng.normal(0, 1, 300)
    y = 0.6 * x + rng.normal(0, 0.8, 300)
    return x, y


def test_marginal_hist_basic(marginal_data, cleanup_figures):
    x, y = marginal_data
    result = sp.plot_marginal(x, y, marginal="hist")
    assert result.fig is not None
    assert len(result.fig.axes) == 3  # 主图 + 顶 + 右


def test_marginal_box(marginal_data, cleanup_figures):
    x, y = marginal_data
    result = sp.plot_marginal(x, y, marginal="box")
    assert result.fig is not None


def test_marginal_kde(marginal_data, cleanup_figures):
    x, y = marginal_data
    result = sp.plot_marginal(x, y, marginal="kde")
    assert result.fig is not None


def test_marginal_show_corr(marginal_data, cleanup_figures):
    x, y = marginal_data
    result = sp.plot_marginal(x, y, show_corr=True)
    texts = [t.get_text() for t in result.ax.texts]
    assert any(t.startswith("r = ") for t in texts)
    r_expected = np.corrcoef(x, y)[0, 1]
    r_drawn = float(texts[0].split("= ")[1])
    assert r_drawn == pytest.approx(r_expected, abs=0.001)


def test_marginal_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="不一致"):
        sp.plot_marginal([1.0, 2.0], [1.0, 2.0, 3.0])


def test_marginal_nan_raises(cleanup_figures):
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_marginal([1.0, np.nan], [1.0, 2.0])


def test_marginal_invalid_type_raises(marginal_data, cleanup_figures):
    x, y = marginal_data
    with pytest.raises(ValueError, match="marginal"):
        sp.plot_marginal(x, y, marginal="scatter")


def test_marginal_invalid_bins_raises(marginal_data, cleanup_figures):
    x, y = marginal_data
    with pytest.raises(ValueError, match="bins"):
        sp.plot_marginal(x, y, bins=0)


def test_marginal_invalid_ratio_raises(marginal_data, cleanup_figures):
    x, y = marginal_data
    with pytest.raises(ValueError, match="size_ratio"):
        sp.plot_marginal(x, y, size_ratio=1.5)


def test_marginal_alias_and_export(marginal_data, cleanup_figures):
    x, y = marginal_data
    assert callable(sp.plot_marginal)
    assert callable(sp.marginal)
    assert "plot_marginal" in sp.__all__ and "marginal" in sp.__all__
    result = sp.marginal(x, y)
    assert result.fig is not None


def test_marginal_shared_axes(marginal_data, cleanup_figures):
    """边缘轴与主图共享坐标轴。"""
    x, y = marginal_data
    result = sp.plot_marginal(x, y)
    ax_main, ax_x, ax_y = result.fig.axes
    assert ax_x.get_shared_x_axes().joined(ax_main, ax_x)
    assert ax_y.get_shared_y_axes().joined(ax_main, ax_y)


def test_marginal_custom_color(marginal_data, cleanup_figures):
    x, y = marginal_data
    result = sp.plot_marginal(x, y, color="#E74C3C")
    scatter = result.ax.collections[0]
    assert np.allclose(np.asarray(scatter.get_facecolors())[0][:3], [0.906, 0.298, 0.235], atol=0.01)


def test_marginal_save_png(tmp_path, marginal_data, cleanup_figures):
    x, y = marginal_data
    result = sp.plot_marginal(x, y, marginal="hist", show_corr=True)
    paths = result.save(str(tmp_path / "marginal"), formats=("png",), dpi=100)
    assert paths[0].exists() and paths[0].stat().st_size > 0
