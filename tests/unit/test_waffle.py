"""
Round-36 tests for plot_waffle (华夫图).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp


def test_waffle_basic(cleanup_figures):
    result = sp.plot_waffle(["训练", "验证", "测试"], np.array([70, 15, 15]))
    assert result.fig is not None
    # 100 个格子
    from matplotlib.patches import Rectangle

    rects = [p for p in result.ax.patches if isinstance(p, Rectangle)]
    assert len(rects) == 100


def test_waffle_cell_counts(cleanup_figures):
    """70/15/15 → 70/15/15 格。"""
    result = sp.plot_waffle(["A", "B", "C"], np.array([70, 15, 15]))
    from matplotlib.patches import Rectangle

    rects = [p for p in result.ax.patches if isinstance(p, Rectangle)]
    colors = [p.get_facecolor() for p in rects]
    # 按颜色分桶计数
    uniq = {}
    for c in colors:
        key = tuple(np.asarray(c)[:3].round(3))
        uniq[key] = uniq.get(key, 0) + 1
    counts = sorted(uniq.values())
    assert counts == [15, 15, 70]


def test_waffle_custom_grid(cleanup_figures):
    result = sp.plot_waffle(["A", "B"], np.array([50, 50]), rows=8, cols=8)
    from matplotlib.patches import Rectangle

    rects = [p for p in result.ax.patches if isinstance(p, Rectangle)]
    assert len(rects) == 64


def test_waffle_percent_labels(cleanup_figures):
    result = sp.plot_waffle(["A", "B"], np.array([25, 75]))
    legend = result.ax.get_legend()
    assert legend is not None
    texts = [t.get_text() for t in legend.get_texts()]
    assert texts[0].startswith("A") and "25%" in texts[0]
    assert texts[1].startswith("B") and "75%" in texts[1]


def test_waffle_no_percent(cleanup_figures):
    result = sp.plot_waffle(["A", "B"], np.array([50, 50]), show_percent=False)
    texts = [t.get_text() for t in result.ax.get_legend().get_texts()]
    assert texts == ["A", "B"]


def test_waffle_custom_colors(cleanup_figures):
    result = sp.plot_waffle(
        ["A", "B"], np.array([50, 50]), colors=["#E74C3C", "#3498DB"]
    )
    from matplotlib.patches import Rectangle

    rects = [p for p in result.ax.patches if isinstance(p, Rectangle)]
    colors = {tuple(np.asarray(p.get_facecolor())[:3].round(2)) for p in rects}
    assert len(colors) == 2


def test_waffle_rounding_exact(cleanup_figures):
    """比例不能整除时格数总和必须恰好为 rows*cols。"""
    result = sp.plot_waffle(["A", "B", "C"], np.array([33.3, 33.3, 33.4]))
    from matplotlib.patches import Rectangle

    rects = [p for p in result.ax.patches if isinstance(p, Rectangle)]
    assert len(rects) == 100


def test_waffle_empty_raises(cleanup_figures):
    with pytest.raises(ValueError, match="categories"):
        sp.plot_waffle([], [])


def test_waffle_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="不一致"):
        sp.plot_waffle(["A", "B"], np.array([1.0]))


def test_waffle_negative_raises(cleanup_figures):
    with pytest.raises(ValueError, match="负值"):
        sp.plot_waffle(["A"], np.array([-1.0]))


def test_waffle_zero_sum_raises(cleanup_figures):
    with pytest.raises(ValueError, match="总和必须大于 0"):
        sp.plot_waffle(["A"], np.array([0.0]))


def test_waffle_bad_grid_raises(cleanup_figures):
    with pytest.raises(ValueError, match="rows/cols"):
        sp.plot_waffle(["A"], np.array([1.0]), rows=0)


def test_waffle_alias_and_export(cleanup_figures):
    assert callable(sp.plot_waffle)
    assert callable(sp.waffle)
    assert "plot_waffle" in sp.__all__ and "waffle" in sp.__all__
    result = sp.waffle(["A", "B"], np.array([60, 40]))
    assert result.fig is not None


def test_waffle_save_png(tmp_path, cleanup_figures):
    result = sp.plot_waffle(["训练", "验证", "测试"], np.array([70, 15, 15]))
    paths = result.save(str(tmp_path / "waffle"), formats=("png",), dpi=100)
    assert paths[0].exists() and paths[0].stat().st_size > 0
