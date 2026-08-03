"""
Round-25 tests for plot_raincloud (雨云图).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp


@pytest.fixture()
def raincloud_data():
    rng = np.random.default_rng(9)
    return [
        rng.normal(0, 1.0, 200),
        rng.normal(0.8, 1.3, 200),
        rng.normal(1.5, 0.9, 200),
    ]


def test_raincloud_basic_horizontal(raincloud_data, cleanup_figures):
    result = sp.plot_raincloud(raincloud_data, labels=["G1", "G2", "G3"])
    assert result.fig is not None
    # 3 组 × (点散点 + 箱线 patch + 小提琴填充)
    yt = [t.get_text() for t in result.ax.get_yticklabels()]
    assert yt == ["G1", "G2", "G3"]
    # 每组至少一个 violin 填充（PolyCollection）
    from matplotlib.collections import PolyCollection
    polys = [c for c in result.ax.collections if isinstance(c, PolyCollection)]
    assert len(polys) == 3


def test_raincloud_vertical(raincloud_data, cleanup_figures):
    result = sp.plot_raincloud(raincloud_data, orientation="v")
    assert result.fig is not None
    xt = [t.get_text() for t in result.ax.get_xticklabels()]
    assert len(xt) == 3


def test_raincloud_parts_toggle(raincloud_data, cleanup_figures):
    """show_points/show_box/show_violin 均可独立关闭。"""
    result = sp.plot_raincloud(
        raincloud_data, show_points=False, show_box=False, show_violin=False,
        show_median=False,
    )
    assert result.fig is not None
    assert len(result.ax.collections) == 0
    assert len(result.ax.patches) == 0


def test_raincloud_median_markers(raincloud_data, cleanup_figures):
    result = sp.plot_raincloud(raincloud_data, show_median=True)
    # 中位数刻度为 #333333 的短竖线
    vlines = [
        ln for ln in result.ax.lines
        if ln.get_color() == "#333333"
        and len(ln.get_xdata()) == 2
        and ln.get_xdata()[0] == ln.get_xdata()[1]
    ]
    assert len(vlines) == 3


def test_raincloud_constant_group(cleanup_figures):
    groups = [np.random.default_rng(0).normal(0, 1, 100), np.full(50, 2.0)]
    result = sp.plot_raincloud(groups)
    assert result.fig is not None


def test_raincloud_auto_labels(raincloud_data, cleanup_figures):
    result = sp.plot_raincloud(raincloud_data)
    yt = [t.get_text() for t in result.ax.get_yticklabels()]
    assert yt == ["Series 1", "Series 2", "Series 3"]


def test_raincloud_label_mismatch_raises(raincloud_data, cleanup_figures):
    with pytest.raises(ValueError, match="labels"):
        sp.plot_raincloud(raincloud_data, labels=["a"])


def test_raincloud_empty_raises(cleanup_figures):
    with pytest.raises(ValueError, match="data_list"):
        sp.plot_raincloud([])


def test_raincloud_too_few_points_raises(cleanup_figures):
    with pytest.raises(ValueError, match="至少需要 2 个"):
        sp.plot_raincloud([np.array([1.0])])


def test_raincloud_bad_orientation_raises(raincloud_data, cleanup_figures):
    with pytest.raises(ValueError, match="orientation"):
        sp.plot_raincloud(raincloud_data, orientation="diagonal")


def test_raincloud_alias_and_export(raincloud_data, cleanup_figures):
    assert callable(sp.plot_raincloud)
    assert callable(sp.raincloud)
    assert "plot_raincloud" in sp.__all__ and "raincloud" in sp.__all__
    result = sp.raincloud(raincloud_data)
    assert result.fig is not None


def test_raincloud_save_png(tmp_path, raincloud_data, cleanup_figures):
    result = sp.plot_raincloud(
        raincloud_data, labels=["对照", "处理A", "处理B"], xlabel="响应值"
    )
    paths = result.save(str(tmp_path / "raincloud"), formats=("png",), dpi=100)
    assert paths[0].exists() and paths[0].stat().st_size > 0


def test_raincloud_dark_theme(raincloud_data, cleanup_figures):
    sp.setup_style("presentation", theme="dark")
    result = sp.plot_raincloud(raincloud_data)
    assert result.fig is not None
