"""
Round-17 tests for plot_bubble_heatmap (气泡热力图).
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pytest

import sciplot as sp


def _bubble_collection(result):
    """返回气泡 scatter collection。"""
    for coll in result.ax.collections:
        if hasattr(coll, "get_sizes") and len(coll.get_sizes()) > 0:
            if isinstance(coll, plt.matplotlib.collections.PathCollection):
                return coll
    raise AssertionError("未找到气泡 PathCollection")


def test_bubble_heatmap_basic(cleanup_figures):
    data = np.array([[1.0, 4.0, 9.0], [0.5, 2.0, 16.0]])
    result = sp.plot_bubble_heatmap(data)
    assert result.fig is not None
    coll = _bubble_collection(result)
    assert len(coll.get_sizes()) == data.size
    assert len(result.fig.axes) == 2  # 主图 + colorbar


def test_bubble_heatmap_size_proportional_to_sqrt_abs(cleanup_figures):
    """气泡面积与 |值| 成正比：值 4 的气泡面积 = 值 1 的 4 倍。"""
    data = np.array([[1.0, 4.0]])
    result = sp.plot_bubble_heatmap(data)
    sizes = _bubble_collection(result).get_sizes()
    assert sizes[1] == pytest.approx(4 * sizes[0], rel=0.05)


def test_bubble_heatmap_negative_values_ok(cleanup_figures):
    data = np.array([[-1.0, -4.0], [2.0, 8.0]])
    result = sp.plot_bubble_heatmap(data, cmap="RdBu_r")
    sizes = _bubble_collection(result).get_sizes()
    # |−1| 与 |2| 对应 sqrt 比例：sqrt(2/4)=0.707，面积比 2
    assert sizes[0] > 0
    assert sizes[1] == pytest.approx(4 * sizes[0], rel=0.05)


def test_bubble_heatmap_zero_values_invisible(cleanup_figures):
    data = np.array([[0.0, 3.0]])
    result = sp.plot_bubble_heatmap(data)
    sizes = _bubble_collection(result).get_sizes()
    assert sizes[0] == 0.0
    assert sizes[1] > 0.0


def test_bubble_heatmap_labels(cleanup_figures):
    data = np.random.rand(3, 4)
    result = sp.plot_bubble_heatmap(
        data,
        row_labels=["r1", "r2", "r3"],
        col_labels=["c1", "c2", "c3", "c4"],
    )
    xt = [t.get_text() for t in result.ax.get_xticklabels()]
    yt = [t.get_text() for t in result.ax.get_yticklabels()]
    assert xt == ["c1", "c2", "c3", "c4"]
    assert yt == ["r1", "r2", "r3"]


def test_bubble_heatmap_label_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="row_labels"):
        sp.plot_bubble_heatmap(np.zeros((2, 2)), row_labels=["only-one"])


def test_bubble_heatmap_1d_raises(cleanup_figures):
    with pytest.raises(ValueError, match="二维"):
        sp.plot_bubble_heatmap(np.array([1.0, 2.0, 3.0]))


def test_bubble_heatmap_invalid_scale_raises(cleanup_figures):
    with pytest.raises(ValueError, match="bubble_scale"):
        sp.plot_bubble_heatmap(np.zeros((2, 2)), bubble_scale=1.5)
    with pytest.raises(ValueError, match="bubble_scale"):
        sp.plot_bubble_heatmap(np.zeros((2, 2)), bubble_scale=0.0)


def test_bubble_heatmap_no_background(cleanup_figures):
    data = np.random.rand(3, 3)
    result = sp.plot_bubble_heatmap(data, background=False)
    # 无 imshow 层；仍有 colorbar 轴
    assert len(result.fig.axes) == 2
    assert not any(isinstance(c, plt.matplotlib.image.AxesImage) for c in result.ax.images)


def test_bubble_heatmap_show_values(cleanup_figures):
    data = np.array([[0.2, 0.8]])
    result = sp.plot_bubble_heatmap(data, show_values=True, fmt=".1f", annot_color="red")
    texts = [t.get_text() for t in result.ax.texts]
    assert texts == ["0.2", "0.8"]
    assert all(t.get_color() == "red" for t in result.ax.texts)


def test_bubble_heatmap_auto_contrast_annotation(cleanup_figures):
    """深色气泡自动使用白字。"""
    data = np.array([[0.05, 0.95]])
    result = sp.plot_bubble_heatmap(data, cmap="viridis", show_values=True, fmt=".2f")
    colors = [t.get_color() for t in result.ax.texts]
    # 0.05 → viridis 暗端 → 白字；0.95 → viridis 亮端 → 黑字
    assert colors[0] == "white"
    assert colors[1] == "black"


def test_bubble_heatmap_vmin_vmax(cleanup_figures):
    data = np.array([[0.0, 1.0]])
    result = sp.plot_bubble_heatmap(data, vmin=0.9, vmax=1.0, cmap="viridis")
    coll = _bubble_collection(result)
    facecolors = np.asarray(coll.get_facecolors())
    cmap = plt.matplotlib.colormaps["viridis"]
    # 0.0 低于 vmin → 裁剪到色标最暗端；1.0 → 最亮端
    assert np.allclose(facecolors[0], cmap(0.0), atol=1e-6)
    assert np.allclose(facecolors[1], cmap(1.0), atol=1e-6)
    assert not np.allclose(facecolors[0], facecolors[1])


def test_bubble_heatmap_constant_data(cleanup_figures):
    data = np.full((2, 2), 5.0)
    result = sp.plot_bubble_heatmap(data)
    sizes = _bubble_collection(result).get_sizes()
    assert np.all(sizes > 0)


def test_bubble_heatmap_all_nan_raises(cleanup_figures):
    with pytest.raises(ValueError, match="有限数值"):
        sp.plot_bubble_heatmap(np.full((2, 2), np.nan))


def test_bubble_heatmap_nan_cells_skipped(cleanup_figures):
    """含 NaN 的格子跳过气泡但不影响其他格子。"""
    data = np.array([[1.0, np.nan], [3.0, 4.0]])
    result = sp.plot_bubble_heatmap(data)
    sizes = _bubble_collection(result).get_sizes()
    assert len(sizes) == 3


def test_bubble_heatmap_alias(cleanup_figures):
    data = np.random.rand(2, 3)
    result = sp.bubble_heatmap(data)
    assert result.fig is not None


def test_bubble_heatmap_exported():
    assert callable(sp.plot_bubble_heatmap)
    assert callable(sp.bubble_heatmap)
    assert "plot_bubble_heatmap" in sp.__all__
    assert "bubble_heatmap" in sp.__all__


def test_bubble_heatmap_save_png(tmp_path, cleanup_figures):
    data = np.random.rand(4, 5)
    result = sp.plot_bubble_heatmap(
        data, row_labels=[f"r{i}" for i in range(4)],
        col_labels=[f"c{i}" for i in range(5)],
        show_values=True,
    )
    paths = result.save(str(tmp_path / "bubble_hm"), formats=("png",), dpi=100)
    assert paths[0].exists()
    assert paths[0].stat().st_size > 0


def test_bubble_heatmap_colorbar_label(cleanup_figures):
    result = sp.plot_bubble_heatmap(np.random.rand(2, 2), colorbar_label="表达水平")
    cbar_label = result.fig.axes[-1].get_ylabel()
    assert cbar_label == "表达水平"


def test_bubble_heatmap_edgecolor_linewidth(cleanup_figures):
    result = sp.plot_bubble_heatmap(np.random.rand(2, 2), edgecolor="black", linewidth=2.0)
    coll = _bubble_collection(result)
    assert np.allclose(np.asarray(coll.get_edgecolors())[0], [0, 0, 0, 1])
