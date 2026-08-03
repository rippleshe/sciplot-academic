"""
Round-18 tests for plot_waterfall3d (3D 瀑布图).
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pytest

import sciplot as sp


@pytest.fixture()
def waterfall_data():
    x = np.linspace(0, 10, 50)
    y_list = [
        np.sin(x) * 2,
        np.cos(x) * 1.5,
        np.sin(x + 1) * 1.0,
    ]
    return x, y_list


def test_waterfall3d_basic(waterfall_data, cleanup_figures):
    x, y_list = waterfall_data
    result = sp.plot_waterfall3d(x, y_list, labels=["A", "B", "C"])
    assert result.fig is not None
    # 3 条曲线 + 3 个填充带（Poly3DCollection）
    assert len(result.ax.lines) == 3
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    polys = [c for c in result.ax.collections if isinstance(c, Poly3DCollection)]
    assert len(polys) == 3


def test_waterfall3d_no_fill(waterfall_data, cleanup_figures):
    x, y_list = waterfall_data
    result = sp.plot_waterfall3d(x, y_list, fill=False)
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    polys = [c for c in result.ax.collections if isinstance(c, Poly3DCollection)]
    assert polys == []


def test_waterfall3d_single_group(cleanup_figures):
    x = np.linspace(0, 5, 30)
    result = sp.plot_waterfall3d(x, [np.sin(x)])
    assert len(result.ax.lines) == 1


def test_waterfall3d_spacing(waterfall_data, cleanup_figures):
    x, y_list = waterfall_data
    result = sp.plot_waterfall3d(x, y_list, spacing=2.5)
    # 第三条线应位于 y = 5.0
    y_vals = result.ax.lines[2].get_data_3d()[1]
    assert np.allclose(y_vals, 5.0)


def test_waterfall3d_auto_labels(waterfall_data, cleanup_figures):
    x, y_list = waterfall_data
    result = sp.plot_waterfall3d(x, y_list)
    handles, labels = result.ax.get_legend_handles_labels()
    assert labels == ["Series 1", "Series 2", "Series 3"]


def test_waterfall3d_label_mismatch_raises(waterfall_data, cleanup_figures):
    x, y_list = waterfall_data
    with pytest.raises(ValueError, match="labels"):
        sp.plot_waterfall3d(x, y_list, labels=["only-one"])


def test_waterfall3d_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="长度"):
        sp.plot_waterfall3d(np.linspace(0, 1, 10), [np.zeros(5)])


def test_waterfall3d_empty_y_list_raises(cleanup_figures):
    with pytest.raises(ValueError, match="y_list"):
        sp.plot_waterfall3d(np.linspace(0, 1, 10), [])


def test_waterfall3d_nan_raises(cleanup_figures):
    x = np.linspace(0, 1, 10)
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_waterfall3d(x, [np.array([1.0, np.nan] + [1.0] * 8)])


def test_waterfall3d_nan_x_raises(cleanup_figures):
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_waterfall3d(np.array([1.0, np.nan, 3.0]), [np.zeros(3)])


def test_waterfall3d_bad_spacing_raises(waterfall_data, cleanup_figures):
    x, y_list = waterfall_data
    with pytest.raises(ValueError, match="spacing"):
        sp.plot_waterfall3d(x, y_list, spacing=0)
    with pytest.raises(ValueError, match="spacing"):
        sp.plot_waterfall3d(x, y_list, spacing=-1)


def test_waterfall3d_2d_x_raises(cleanup_figures):
    with pytest.raises(ValueError, match="一维"):
        sp.plot_waterfall3d(np.zeros((2, 2)), [np.zeros(4)])


def test_waterfall3d_baseline_shift(waterfall_data, cleanup_figures, monkeypatch):
    """baseline 偏移后填充带底面应落在对应高度。"""
    x, y_list = waterfall_data
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    captured: list = []
    orig_init = Poly3DCollection.__init__

    def spy_init(self, *args, **kwargs):
        captured.append(args[0] if args else None)
        orig_init(self, *args, **kwargs)

    monkeypatch.setattr(Poly3DCollection, "__init__", spy_init)
    result = sp.plot_waterfall3d(x, y_list, baseline=-1.0, fill=True)
    assert len(captured) == 3
    for verts_pair in captured:
        # verts 为两个多边形：曲线带 + 底面带
        assert len(verts_pair) == 2
        bottom = np.asarray(verts_pair[1])
        assert np.allclose(bottom[:, 2], -1.0)


def test_waterfall3d_alias(waterfall_data, cleanup_figures):
    x, y_list = waterfall_data
    result = sp.waterfall3d(x, y_list)
    assert result.fig is not None


def test_waterfall3d_exported():
    assert callable(sp.plot_waterfall3d)
    assert callable(sp.waterfall3d)
    assert "plot_waterfall3d" in sp.__all__
    assert "waterfall3d" in sp.__all__


def test_waterfall3d_view_init(waterfall_data, cleanup_figures):
    x, y_list = waterfall_data
    result = sp.plot_waterfall3d(x, y_list, elev=45, azim=30)
    assert result.ax.elev == 45
    assert result.ax.azim == 30


def test_waterfall3d_save_png(tmp_path, waterfall_data, cleanup_figures):
    x, y_list = waterfall_data
    result = sp.plot_waterfall3d(
        x, y_list, labels=["A", "B", "C"],
        xlabel="波数", ylabel="样品", zlabel="强度",
    )
    paths = result.save(str(tmp_path / "waterfall"), formats=("png",), dpi=100)
    assert paths[0].exists()
    assert paths[0].stat().st_size > 0
