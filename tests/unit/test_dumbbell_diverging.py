"""
Round-27 tests for plot_dumbbell (哑铃图) and plot_diverging_bar (发散条形图).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp


# ═══════════════════════════════════════════════════════════════
# plot_dumbbell
# ═══════════════════════════════════════════════════════════════

def test_dumbbell_basic(cleanup_figures):
    result = sp.plot_dumbbell(
        ["A", "B", "C"], [10.0, 20.0, 30.0], [15.0, 18.0, 35.0]
    )
    assert result.fig is not None
    # 起点散点 + 终点散点
    from matplotlib.collections import PathCollection

    scatters = [c for c in result.ax.collections if isinstance(c, PathCollection)]
    assert len(scatters) == 2
    assert len(scatters[0].get_offsets()) == 3
    # 图例
    legend = result.ax.get_legend()
    assert legend is not None


def test_dumbbell_sort_by_delta(cleanup_figures):
    """sort_by='delta' 时变化量最大的类别在顶部。"""
    result = sp.plot_dumbbell(
        ["A", "B", "C"], [10.0, 20.0, 30.0], [11.0, 25.0, 31.0],
        sort_by="delta",
    )
    yt = [t.get_text() for t in result.ax.get_yticklabels()]
    # B 的 delta=5 最大 → 顶部
    assert yt[-1] == "B"
    assert yt[0] == "A"


def test_dumbbell_show_values(cleanup_figures):
    result = sp.plot_dumbbell(
        ["A", "B"], [1.0, 2.0], [3.0, 4.0], show_values=True
    )
    texts = [t.get_text() for t in result.ax.texts]
    assert len(texts) == 2
    assert all("+" in t for t in texts)


def test_dumbbell_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="长度必须一致"):
        sp.plot_dumbbell(["A", "B"], [1.0], [2.0, 3.0])


def test_dumbbell_nan_raises(cleanup_figures):
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_dumbbell(["A"], [np.nan], [1.0])


def test_dumbbell_bad_sort_raises(cleanup_figures):
    with pytest.raises(ValueError, match="sort_by"):
        sp.plot_dumbbell(["A"], [1.0], [2.0], sort_by="sideways")


def test_dumbbell_empty_categories_raises(cleanup_figures):
    with pytest.raises(ValueError, match="categories"):
        sp.plot_dumbbell([], [], [])


def test_dumbbell_alias_and_export(cleanup_figures):
    assert callable(sp.plot_dumbbell)
    assert callable(sp.dumbbell)
    assert "plot_dumbbell" in sp.__all__ and "dumbbell" in sp.__all__
    result = sp.dumbbell(["A"], [1.0], [2.0])
    assert result.fig is not None


# ═══════════════════════════════════════════════════════════════
# plot_diverging_bar
# ═══════════════════════════════════════════════════════════════

def test_diverging_bar_basic(cleanup_figures):
    result = sp.plot_diverging_bar(
        ["A", "B", "C"], np.array([42.0, -18.0, 35.0])
    )
    assert result.fig is not None
    # 3 个条形 patch
    assert len(result.ax.patches) >= 3
    # 分界线
    vlines = [ln for ln in result.ax.lines if len(ln.get_xdata()) == 2]
    assert len(vlines) == 1


def test_diverging_bar_two_colors(cleanup_figures):
    """正负条形颜色不同。"""
    result = sp.plot_diverging_bar(
        ["A", "B"], np.array([5.0, -5.0]), positive_color="#E74C3C", negative_color="#3498DB"
    )
    patch_colors = {
        np.asarray(p.get_facecolor())[:3].round(3).tobytes()
        for p in result.ax.patches
    }
    assert len(patch_colors) == 2


def test_diverging_bar_threshold(cleanup_figures):
    """threshold 偏移分界。"""
    result = sp.plot_diverging_bar(
        ["A", "B"], np.array([1.0, -1.0]), threshold=0.5
    )
    # A(1.0) >= 0.5 正色，B(-1.0) < 0.5 负色
    assert result.fig is not None


def test_diverging_bar_show_values(cleanup_figures):
    result = sp.plot_diverging_bar(
        ["A", "B"], np.array([42.0, -18.0]), show_values=True, fmt=".0f", sort=False
    )
    texts = [t.get_text() for t in result.ax.texts]
    assert texts == ["42", "-18"]


def test_diverging_bar_no_sort(cleanup_figures):
    result = sp.plot_diverging_bar(
        ["A", "B", "C"], np.array([3.0, 1.0, 2.0]), sort=False
    )
    yt = [t.get_text() for t in result.ax.get_yticklabels()]
    assert yt == ["A", "B", "C"]


def test_diverging_bar_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="不一致"):
        sp.plot_diverging_bar(["A", "B"], np.array([1.0]))


def test_diverging_bar_nan_raises(cleanup_figures):
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_diverging_bar(["A"], np.array([np.nan]))


def test_diverging_bar_alias_and_export(cleanup_figures):
    assert callable(sp.plot_diverging_bar)
    assert callable(sp.diverging_bar)
    assert "plot_diverging_bar" in sp.__all__ and "diverging_bar" in sp.__all__
    result = sp.diverging_bar(["A"], np.array([1.0]))
    assert result.fig is not None


def test_dumbbell_diverging_save(tmp_path, cleanup_figures):
    r1 = sp.plot_dumbbell(["A", "B"], [1.0, 2.0], [3.0, 2.5], show_values=True)
    p1 = r1.save(str(tmp_path / "dumbbell"), formats=("png",), dpi=100)
    r2 = sp.plot_diverging_bar(["X", "Y"], np.array([10.0, -8.0]), show_values=True)
    p2 = r2.save(str(tmp_path / "diverging"), formats=("png",), dpi=100)
    assert p1[0].exists() and p2[0].exists()
