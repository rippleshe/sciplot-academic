"""
Round-42 tests for plot_streamgraph (流图).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp


@pytest.fixture()
def stream_data():
    years = np.arange(2000, 2025)
    web = 10 + 3 * (years - 2000) + 2 * np.sin(years) + 4 * np.cos(years * 0.4)
    mobile = 2 + 8 * np.tanh((years - 2008) / 2.5)
    pc = 40 - 0.8 * (years - 2000)
    web = np.maximum(web, 0)
    mobile = np.maximum(mobile, 0)
    pc = np.maximum(pc, 0)
    return years, [web, mobile, pc], ["Web", "移动端", "PC"]


def test_streamgraph_basic(stream_data, cleanup_figures):
    years, series, labels = stream_data
    result = sp.plot_streamgraph(years, series, labels=labels)
    assert result.fig is not None
    assert result.ax is not None


def test_streamgraph_alias_and_export(stream_data, cleanup_figures):
    years, series, labels = stream_data
    assert callable(sp.plot_streamgraph)
    assert callable(sp.streamgraph)
    assert "plot_streamgraph" in sp.__all__ and "streamgraph" in sp.__all__
    result = sp.streamgraph(years, series, labels=labels)
    assert result.fig is not None


def test_streamgraph_baseline_modes(stream_data, cleanup_figures):
    years, series, labels = stream_data
    for mode in ["wiggle", "center", "zero"]:
        result = sp.plot_streamgraph(years, series, labels=labels, baseline=mode)
        assert result.fig is not None


def test_streamgraph_invalid_baseline_raises(stream_data, cleanup_figures):
    years, series, labels = stream_data
    with pytest.raises(ValueError, match="baseline"):
        sp.plot_streamgraph(years, series, labels=labels, baseline="nope")


def test_streamgraph_length_mismatch_raises(stream_data, cleanup_figures):
    years, series, labels = stream_data
    with pytest.raises(ValueError, match="长度"):
        sp.plot_streamgraph(years, series[:-1] + [series[0][:-1]], labels=labels)


def test_streamgraph_negative_raises(stream_data, cleanup_figures):
    years, series, labels = stream_data
    bad = series[0].copy()
    bad[0] = -1.0
    with pytest.raises(ValueError, match="不能包含负值"):
        sp.plot_streamgraph(years, [bad] + series[1:], labels=labels)


def test_streamgraph_nan_raises(stream_data, cleanup_figures):
    years, series, labels = stream_data
    bad = series[0].copy()
    bad[0] = np.nan
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_streamgraph(years, [bad] + series[1:], labels=labels)


def test_streamgraph_single_series(stream_data, cleanup_figures):
    years, series, labels = stream_data
    result = sp.plot_streamgraph(years, [series[0]], labels=[labels[0]])
    assert result.fig is not None


def test_streamgraph_save_png(tmp_path, stream_data, cleanup_figures):
    years, series, labels = stream_data
    result = sp.plot_streamgraph(years, series, labels=labels)
    paths = sp.save(result.fig, tmp_path / "streamgraph", formats=("png",))
    assert paths[0].exists()
