"""
Round-46 tests: plot_grouped_bar colors 参数 + plot_heatmap NaN 掩膜.
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp


def test_grouped_bar_custom_colors(cleanup_figures):
    data = {"A": [1.0, 2.0], "B": [3.0, 4.0], "C": [5.0, 6.0]}
    result = sp.plot_grouped_bar(
        ["g1", "g2"], data,
        colors=["#D62728", "#1F77B4", "#2CA02C"],
    )
    assert result.fig is not None


def test_grouped_bar_colors_mismatch_raises(cleanup_figures):
    data = {"A": [1.0, 2.0], "B": [3.0, 4.0]}
    with pytest.raises(ValueError, match="colors 长度"):
        sp.plot_grouped_bar(["g1", "g2"], data, colors=["#D62728"])


def test_grouped_bar_default_colors_still_work(cleanup_figures):
    """不传 colors 时行为不变（默认循环配色）。"""
    data = {"A": [1.0, 2.0], "B": [3.0, 4.0]}
    result = sp.plot_grouped_bar(["g1", "g2"], data)
    assert result.fig is not None


def test_heatmap_nan_mask_ok(cleanup_figures):
    """NaN 掩膜格（上三角）不写文字、不崩溃。"""
    m = np.array([[1.0, np.nan, np.nan],
                  [0.5, 1.0, np.nan],
                  [-0.2, 0.3, 1.0]])
    result = sp.plot_heatmap(m, show_values=True, fmt=".1f", cmap="RdBu_r",
                             vmin=-1, vmax=1)
    assert result.fig is not None
    # 应只有 6 个非 NaN 格的文字
    texts = [t.get_text() for t in result.ax.texts]
    assert len(texts) == 6
    assert "nan" not in [t.lower() for t in texts]
