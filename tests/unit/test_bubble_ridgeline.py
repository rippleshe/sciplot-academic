"""
Round-19 tests for plot_bubble (二维气泡图) and plot_ridgeline (山脊图).
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pytest

import sciplot as sp


# ═══════════════════════════════════════════════════════════════
# plot_bubble
# ═══════════════════════════════════════════════════════════════

@pytest.fixture()
def bubble_data():
    rng = np.random.default_rng(7)
    return rng.random(12), rng.random(12), np.abs(rng.random(12)) * 10


def _bubble_scatter(result):
    from matplotlib.collections import PathCollection

    for coll in result.ax.collections:
        if isinstance(coll, PathCollection):
            return coll
    raise AssertionError("未找到气泡 scatter")


def test_bubble_basic(bubble_data, cleanup_figures):
    x, y, s = bubble_data
    result = sp.plot_bubble(x, y, size=s)
    coll = _bubble_scatter(result)
    assert len(coll.get_sizes()) == 12
    assert len(result.fig.axes) == 1  # 无 colorbar


def test_bubble_size_linear_scaling(bubble_data, cleanup_figures):
    """气泡面积与 size 线性成正比。"""
    x, y, _ = bubble_data
    result = sp.plot_bubble(x, y, size=np.array([1.0, 4.0] + [1.0] * 10))
    sizes = _bubble_scatter(result).get_sizes()
    assert sizes[1] == pytest.approx(4 * sizes[0], rel=0.05)


def test_bubble_zero_size_invisible(bubble_data, cleanup_figures):
    x, y, _ = bubble_data
    result = sp.plot_bubble(x, y, size=np.array([0.0, 3.0] + [1.0] * 10))
    sizes = _bubble_scatter(result).get_sizes()
    assert sizes[0] == 0.0
    assert sizes[1] > 0.0


def test_bubble_color_channel_creates_colorbar(bubble_data, cleanup_figures):
    x, y, s = bubble_data
    result = sp.plot_bubble(x, y, size=s, color=np.linspace(0, 1, 12))
    assert len(result.fig.axes) == 2  # 主图 + colorbar


def test_bubble_colorbar_label(bubble_data, cleanup_figures):
    x, y, s = bubble_data
    result = sp.plot_bubble(x, y, size=s, color=np.linspace(0, 1, 12),
                            colorbar_label="增长率")
    assert result.fig.axes[-1].get_ylabel() == "增长率"


def test_bubble_labels_legend(bubble_data, cleanup_figures):
    x, y, s = bubble_data
    labels = ["A"] * 6 + ["B"] * 6
    result = sp.plot_bubble(x, y, size=s, labels=labels)
    legend = result.ax.get_legend()
    assert legend is not None
    texts = [t.get_text() for t in legend.get_texts()]
    assert texts == ["A", "B"]


def test_bubble_show_values(bubble_data, cleanup_figures):
    x, y, s = bubble_data
    result = sp.plot_bubble(x, y, size=s, show_values=True, fmt=".1f")
    texts = [t.get_text() for t in result.ax.texts]
    assert len(texts) == 12
    assert all(float(t) >= 0 for t in texts)


def test_bubble_length_mismatch_raises(bubble_data, cleanup_figures):
    x, y, s = bubble_data
    with pytest.raises(ValueError, match="不一致"):
        sp.plot_bubble(x, y, size=s[:-1])
    with pytest.raises(ValueError, match="不一致"):
        sp.plot_bubble(x, y[:-2], size=s)


def test_bubble_color_length_mismatch_raises(bubble_data, cleanup_figures):
    x, y, s = bubble_data
    with pytest.raises(ValueError, match="color"):
        sp.plot_bubble(x, y, size=s, color=np.linspace(0, 1, 5))


def test_bubble_labels_length_mismatch_raises(bubble_data, cleanup_figures):
    x, y, s = bubble_data
    with pytest.raises(ValueError, match="labels"):
        sp.plot_bubble(x, y, size=s, labels=["A"] * 3)


def test_bubble_nan_raises(cleanup_figures):
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_bubble([1.0, np.nan], [1.0, 2.0], size=[1.0, 1.0])


def test_bubble_all_nan_color_raises(bubble_data, cleanup_figures):
    x, y, s = bubble_data
    with pytest.raises(ValueError, match="颜色映射"):
        sp.plot_bubble(x, y, size=s, color=np.full(12, np.nan))


def test_bubble_bad_size_scale_raises(bubble_data, cleanup_figures):
    x, y, s = bubble_data
    with pytest.raises(ValueError, match="size_scale"):
        sp.plot_bubble(x, y, size=s, size_scale=0)


def test_bubble_alias_and_export(bubble_data, cleanup_figures):
    x, y, s = bubble_data
    assert callable(sp.plot_bubble)
    assert callable(sp.bubble)
    assert "plot_bubble" in sp.__all__ and "bubble" in sp.__all__
    result = sp.bubble(x, y, size=s)
    assert result.fig is not None


def test_bubble_save_png(tmp_path, bubble_data, cleanup_figures):
    x, y, s = bubble_data
    result = sp.plot_bubble(x, y, size=s, color=np.linspace(0, 1, 12))
    paths = result.save(str(tmp_path / "bubble2d"), formats=("png",), dpi=100)
    assert paths[0].exists() and paths[0].stat().st_size > 0


# ═══════════════════════════════════════════════════════════════
# plot_ridgeline
# ═══════════════════════════════════════════════════════════════

@pytest.fixture()
def ridge_data():
    rng = np.random.default_rng(11)
    return [
        rng.normal(0, 1.0, 300),
        rng.normal(1.5, 1.2, 300),
        rng.normal(-1.0, 0.6, 300),
    ]


def test_ridgeline_basic(ridge_data, cleanup_figures):
    result = sp.plot_ridgeline(ridge_data, labels=["G1", "G2", "G3"])
    assert result.fig is not None
    # 3 条山脊线 + 图例
    assert len(result.ax.lines) == 3
    yt = [t.get_text() for t in result.ax.get_yticklabels()]
    assert yt == ["G1", "G2", "G3"]


def test_ridgeline_auto_labels(ridge_data, cleanup_figures):
    result = sp.plot_ridgeline(ridge_data)
    handles, labels = result.ax.get_legend_handles_labels()
    assert labels == ["Series 1", "Series 2", "Series 3"]


def test_ridgeline_no_fill(ridge_data, cleanup_figures):
    result = sp.plot_ridgeline(ridge_data, fill=False)
    assert len(result.ax.collections) == 0


def test_ridgeline_median_markers(ridge_data, cleanup_figures):
    result = sp.plot_ridgeline(ridge_data, show_median=True)
    # 中位数刻度线是 xdata 相同的垂直线
    vlines = [
        ln for ln in result.ax.lines
        if len(ln.get_xdata()) == 2 and ln.get_xdata()[0] == ln.get_xdata()[1]
    ]
    assert len(vlines) == 3


def test_ridgeline_overlap_validation(ridge_data, cleanup_figures):
    with pytest.raises(ValueError, match="overlap"):
        sp.plot_ridgeline(ridge_data, overlap=1.0)
    with pytest.raises(ValueError, match="overlap"):
        sp.plot_ridgeline(ridge_data, overlap=-0.1)


def test_ridgeline_empty_raises(cleanup_figures):
    with pytest.raises(ValueError, match="data_list"):
        sp.plot_ridgeline([])


def test_ridgeline_too_few_points_raises(cleanup_figures):
    with pytest.raises(ValueError, match="至少需要 2 个"):
        sp.plot_ridgeline([np.array([1.0])])


def test_ridgeline_label_mismatch_raises(ridge_data, cleanup_figures):
    with pytest.raises(ValueError, match="labels"):
        sp.plot_ridgeline(ridge_data, labels=["a"])


def test_ridgeline_constant_group(cleanup_figures):
    """常数序列组应绘制垂直线而不是崩溃。"""
    groups = [np.random.default_rng(0).normal(0, 1, 100), np.full(50, 2.0)]
    result = sp.plot_ridgeline(groups)
    assert result.fig is not None
    assert len(result.ax.lines) == 2


def test_ridgeline_alias_and_export(ridge_data, cleanup_figures):
    assert callable(sp.plot_ridgeline)
    assert callable(sp.ridgeline)
    assert "plot_ridgeline" in sp.__all__ and "ridgeline" in sp.__all__
    result = sp.ridgeline(ridge_data)
    assert result.fig is not None


def test_ridgeline_save_png(tmp_path, ridge_data, cleanup_figures):
    result = sp.plot_ridgeline(ridge_data, labels=["对照", "处理A", "处理B"],
                               xlabel="响应", show_median=True)
    paths = result.save(str(tmp_path / "ridgeline"), formats=("png",), dpi=100)
    assert paths[0].exists() and paths[0].stat().st_size > 0
