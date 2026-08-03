"""
Round-29 tests for plot_packed_bubble (打包气泡图).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp
from sciplot._plots.advanced import _pack_bubbles


def _bubble_circles(result):
    """气泡圆（排除黑色阴影）。"""
    from matplotlib.patches import Circle

    return [
        p for p in result.ax.patches
        if isinstance(p, Circle) and np.asarray(p.get_facecolor())[:3].sum() > 0.01
    ]


def test_packed_bubble_basic(cleanup_figures):
    result = sp.plot_packed_bubble(
        ["计算", "存储", "网络", "人力", "运维"],
        np.array([40, 25, 15, 12, 8]),
    )
    assert result.fig is not None
    # 5 个气泡 Circle（不含阴影）
    assert len(_bubble_circles(result)) == 5


def test_packed_bubble_area_proportional(cleanup_figures):
    """气泡面积与 sizes 成正比（半径与 sqrt(size) 成正比）。"""
    result = sp.plot_packed_bubble(["A", "B"], np.array([1.0, 4.0]))
    circles = sorted(_bubble_circles(result), key=lambda c: c.radius)
    # r_B / r_A == sqrt(4) == 2
    assert circles[1].radius == pytest.approx(2 * circles[0].radius, rel=0.05)


def test_packed_bubble_no_overlap(cleanup_figures):
    """打包后气泡之间不应重叠（中心距 >= 半径和 ×0.98）。"""
    sizes = np.array([30, 20, 15, 10, 8, 5, 3, 2])
    pos, radii = _pack_bubbles(sizes)
    for i in range(len(sizes)):
        for j in range(i + 1, len(sizes)):
            dist = np.hypot(pos[i][0] - pos[j][0], pos[i][1] - pos[j][1])
            assert dist >= (radii[i] + radii[j]) * 0.95 - 1e-6


def test_packed_bubble_single(cleanup_figures):
    result = sp.plot_packed_bubble(["A"], np.array([5.0]))
    assert result.fig is not None


def test_packed_bubble_custom_colors(cleanup_figures):
    result = sp.plot_packed_bubble(
        ["A", "B"], np.array([3.0, 2.0]),
        colors=["#E74C3C", "#3498DB"],
    )
    facecolors = {np.asarray(p.get_facecolor())[:3].round(3).tobytes()
                  for p in _bubble_circles(result)}
    assert len(facecolors) == 2


def test_packed_bubble_show_values(cleanup_figures):
    result = sp.plot_packed_bubble(["A"], np.array([5.0]), show_values=True, fmt=".1f")
    texts = [t.get_text() for t in result.ax.texts]
    assert "5.0" in texts


def test_packed_bubble_empty_raises(cleanup_figures):
    with pytest.raises(ValueError, match="labels"):
        sp.plot_packed_bubble([], [])


def test_packed_bubble_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="不一致"):
        sp.plot_packed_bubble(["A", "B"], np.array([1.0]))


def test_packed_bubble_nonpositive_raises(cleanup_figures):
    with pytest.raises(ValueError, match="正数"):
        sp.plot_packed_bubble(["A"], np.array([0.0]))
    with pytest.raises(ValueError, match="正数"):
        sp.plot_packed_bubble(["A"], np.array([-1.0]))


def test_packed_bubble_nan_raises(cleanup_figures):
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_packed_bubble(["A"], np.array([np.nan]))


def test_packed_bubble_color_by_legend(cleanup_figures):
    """color_by 类别分组生成图例。"""
    result = sp.plot_packed_bubble(
        ["A", "B", "C"], np.array([5.0, 3.0, 2.0]),
        color_by=["核心", "核心", "支撑"],
    )
    legend = result.ax.get_legend()
    assert legend is not None
    texts = [t.get_text() for t in legend.get_texts()]
    assert texts == ["核心", "支撑"]


def test_packed_bubble_min_size_frac(cleanup_figures):
    """min_size_frac 保证小气泡可见。"""
    result = sp.plot_packed_bubble(
        ["A", "B"], np.array([100.0, 1.0]), min_size_frac=0.4
    )
    circles = sorted(_bubble_circles(result), key=lambda c: c.radius)
    # 小气泡半径 >= 大气泡的 40%
    assert circles[0].radius >= 0.4 * circles[1].radius - 1e-9


def test_packed_bubble_bad_min_size_frac_raises(cleanup_figures):
    with pytest.raises(ValueError, match="min_size_frac"):
        sp.plot_packed_bubble(["A"], np.array([1.0]), min_size_frac=0.0)


def test_packed_bubble_color_by_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="color_by"):
        sp.plot_packed_bubble(["A", "B"], np.array([1.0, 2.0]), color_by=["x"])


def test_packed_bubble_alias_and_export(cleanup_figures):
    assert callable(sp.plot_packed_bubble)
    assert callable(sp.packed_bubble)
    assert "plot_packed_bubble" in sp.__all__ and "packed_bubble" in sp.__all__
    result = sp.packed_bubble(["A"], np.array([2.0]))
    assert result.fig is not None


def test_packed_bubble_save_png(tmp_path, cleanup_figures):
    result = sp.plot_packed_bubble(
        ["计算", "存储", "网络", "人力"], np.array([40, 25, 15, 12])
    )
    paths = result.save(str(tmp_path / "packed"), formats=("png",), dpi=100)
    assert paths[0].exists() and paths[0].stat().st_size > 0
