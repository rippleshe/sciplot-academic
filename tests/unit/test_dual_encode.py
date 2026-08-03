"""
Round-45 tests for dual_encode_colors (双编码配色).
"""

from __future__ import annotations

import matplotlib.colors as mcolors
import pytest

import sciplot as sp


def test_dual_encode_shape():
    colors = sp.dual_encode_colors(["#E07B54", "#5B7DB1"], 3)
    assert len(colors) == 2
    assert len(colors[0]) == 3
    assert all(c.startswith("#") for c in colors[0] + colors[1])


def test_dual_encode_monotonic_lightness():
    """同一色相内明度应单调递减（浅 → 深）。"""
    colors = sp.dual_encode_colors(["#E07B54"], 4)
    lightness = []
    for c in colors[0]:
        h, l, s = mcolors.rgb_to_hls(*mcolors.to_rgb(c))
        lightness.append(l)
    for i in range(len(lightness) - 1):
        assert lightness[i] > lightness[i + 1]


def test_dual_encode_hue_preserved():
    """明度变化不应改变色相。"""
    colors = sp.dual_encode_colors(["#5B7DB1"], 3)
    hues = set()
    for c in colors[0]:
        h, l, s = mcolors.rgb_to_hls(*mcolors.to_rgb(c))
        hues.add(round(h, 3))
    assert len(hues) == 1


def test_dual_encode_single_level():
    colors = sp.dual_encode_colors(["#D62728", "#1F77B4"], 1)
    assert colors[0] == ["#D62728"]


def test_dual_encode_empty_hues_raises():
    with pytest.raises(ValueError, match="hue_colors"):
        sp.dual_encode_colors([], 2)


def test_dual_encode_bad_levels_raises():
    with pytest.raises(ValueError, match="levels"):
        sp.dual_encode_colors(["#D62728"], 0)


def test_dual_encode_inverted_lightness_raises():
    with pytest.raises(ValueError, match="min_lightness"):
        sp.dual_encode_colors(["#D62728"], 3, min_lightness=0.3, max_lightness=0.7)


def test_dual_encode_export():
    assert callable(sp.dual_encode_colors)
    assert "dual_encode_colors" in sp.__all__


def test_dual_encode_usable_as_colors():
    """生成的矩阵可直接用于绘图颜色参数。"""
    colors = sp.dual_encode_colors(["#E07B54", "#5B7DB1"], 3)
    flat = [c for row in colors for c in row]
    # 全部可被 matplotlib 解析
    for c in flat:
        mcolors.to_rgba(c)
