"""
Round-26 tests for plot_beeswarm (蜂群图).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp
from sciplot._plots.distribution import _swarm_offsets


@pytest.fixture()
def beeswarm_data():
    rng = np.random.default_rng(13)
    return [
        rng.normal(0, 1, 80),
        rng.normal(1, 1.2, 60),
        rng.normal(-0.5, 0.8, 100),
    ]


def test_beeswarm_basic_vertical(beeswarm_data, cleanup_figures):
    result = sp.plot_beeswarm(beeswarm_data, labels=["A", "B", "C"])
    assert result.fig is not None
    # 3 个组 → 3 个 scatter 集合（每组合并为一个 PathCollection）
    from matplotlib.collections import PathCollection

    scatters = [c for c in result.ax.collections if isinstance(c, PathCollection)]
    assert len(scatters) == 3
    assert len(scatters[0].get_offsets()) == 80


def test_beeswarm_horizontal(beeswarm_data, cleanup_figures):
    result = sp.plot_beeswarm(beeswarm_data, orient="h")
    assert result.fig is not None
    yt = [t.get_text() for t in result.ax.get_yticklabels()]
    assert len(yt) == 3


def test_beeswarm_jitter_method(beeswarm_data, cleanup_figures):
    result = sp.plot_beeswarm(beeswarm_data, method="jitter")
    assert result.fig is not None


def test_beeswarm_show_box(beeswarm_data, cleanup_figures):
    result = sp.plot_beeswarm(beeswarm_data, show_box=True)
    # 箱线产生 patches
    assert len(result.ax.patches) >= 3


def test_beeswarm_auto_labels(beeswarm_data, cleanup_figures):
    result = sp.plot_beeswarm(beeswarm_data)
    xt = [t.get_text() for t in result.ax.get_xticklabels()]
    assert xt == ["Series 1", "Series 2", "Series 3"]


def test_swarm_offsets_deterministic():
    rng = np.random.default_rng(1)
    values = rng.normal(0, 1, 50)
    o1 = _swarm_offsets(values)
    o2 = _swarm_offsets(values)
    assert np.allclose(o1, o2)


def test_swarm_offsets_centered():
    """蜂群偏移应近似关于 0 对称（无整体偏移）。"""
    rng = np.random.default_rng(2)
    values = rng.normal(0, 1, 100)
    offsets = _swarm_offsets(values)
    assert abs(offsets.mean()) < 0.05
    assert offsets.max() <= 0.41  # width=0.8 的一半 + 步长余量


def test_swarm_offsets_single_point():
    assert _swarm_offsets(np.array([3.0]))[0] == 0.0


def test_swarm_offsets_empty():
    assert len(_swarm_offsets(np.empty(0))) == 0


def test_beeswarm_empty_raises(cleanup_figures):
    with pytest.raises(ValueError, match="data_list"):
        sp.plot_beeswarm([])


def test_beeswarm_nan_only_raises(cleanup_figures):
    with pytest.raises(ValueError, match="有效数据点"):
        sp.plot_beeswarm([np.array([np.nan, np.nan])])


def test_beeswarm_bad_method_raises(beeswarm_data, cleanup_figures):
    with pytest.raises(ValueError, match="method"):
        sp.plot_beeswarm(beeswarm_data, method="strip")


def test_beeswarm_bad_orient_raises(beeswarm_data, cleanup_figures):
    with pytest.raises(ValueError, match="orient"):
        sp.plot_beeswarm(beeswarm_data, orient="diag")


def test_beeswarm_label_mismatch_raises(beeswarm_data, cleanup_figures):
    with pytest.raises(ValueError, match="labels"):
        sp.plot_beeswarm(beeswarm_data, labels=["a"])


def test_beeswarm_alias_and_export(beeswarm_data, cleanup_figures):
    assert callable(sp.plot_beeswarm)
    assert callable(sp.beeswarm)
    assert "plot_beeswarm" in sp.__all__ and "beeswarm" in sp.__all__
    result = sp.beeswarm(beeswarm_data)
    assert result.fig is not None


def test_beeswarm_save_png(tmp_path, beeswarm_data, cleanup_figures):
    result = sp.plot_beeswarm(beeswarm_data, labels=["对照", "处理A", "处理B"], show_box=True)
    paths = result.save(str(tmp_path / "beeswarm"), formats=("png",), dpi=100)
    assert paths[0].exists() and paths[0].stat().st_size > 0
