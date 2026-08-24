"""Round-8: publication-floor defaults for colorbars, category labels and legends."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pytest

import sciplot as sp
from sciplot._core.layout import add_colorbar


def test_add_colorbar_rejects_invalid_geometry(cleanup_figures):
    fig, ax = plt.subplots()
    im = ax.imshow(np.arange(4).reshape(2, 2))
    with pytest.raises(ValueError, match="fraction"):
        add_colorbar(fig, im, ax=ax, fraction=0)
    with pytest.raises(ValueError, match="pad"):
        add_colorbar(fig, im, ax=ax, pad=-0.01)


def test_add_colorbar_uses_subordinate_visual_weight(cleanup_figures):
    sp.setup_style(venue="nature")
    fig, ax = plt.subplots()
    im = ax.imshow(np.arange(4).reshape(2, 2))
    cbar = add_colorbar(fig, im, ax=ax, label="Value")
    assert cbar.outline.get_linewidth() < plt.rcParams["axes.linewidth"]
    assert cbar.ax.yaxis.get_ticklabels()
    assert cbar.ax.yaxis.get_ticklabels()[0].get_fontsize() <= plt.rcParams["font.size"]


def test_heatmap_short_labels_stay_horizontal(cleanup_figures):
    result = sp.plot_heatmap(
        np.arange(9).reshape(3, 3),
        col_labels=["A", "B", "C"],
        row_labels=["R1", "R2", "R3"],
    )
    assert all(label.get_rotation() == 0 for label in result.ax.get_xticklabels())


def test_heatmap_long_colliding_labels_rotate(cleanup_figures):
    labels = [f"VeryLongExperimentalCondition_{i}" for i in range(6)]
    result = sp.plot_heatmap(
        np.arange(36).reshape(6, 6),
        col_labels=labels,
        row_labels=[f"R{i}" for i in range(6)],
    )
    assert any(label.get_rotation() != 0 for label in result.ax.get_xticklabels())


def test_lollipop_short_categories_stay_horizontal(cleanup_figures):
    result = sp.plot_lollipop(["A", "B", "C"], np.array([1, 2, 3]))
    assert all(label.get_rotation() == 0 for label in result.ax.get_xticklabels())


def test_parallel_short_columns_stay_horizontal(cleanup_figures):
    data = np.array([[1.0, 2.0, 3.0], [2.0, 1.0, 2.5]])
    result = sp.plot_parallel(data, columns=["A", "B", "C"])
    assert all(label.get_rotation() == 0 for label in result.ax.get_xticklabels())


def test_multi_timeseries_many_series_uses_multicolumn_legend(cleanup_figures):
    t = np.arange(20)
    y_list = [np.sin(t / 4 + i / 3) for i in range(8)]
    result = sp.plot_multi_timeseries(t, y_list, labels=[f"S{i}" for i in range(8)])
    assert getattr(result.ax.get_legend(), "_ncols", None) == 2


def test_multi_density_many_series_uses_multicolumn_legend(cleanup_figures):
    rng = np.random.default_rng(7)
    data = [rng.normal(i * 0.2, 1.0, 80) for i in range(8)]
    result = sp.plot_multi_density(data, labels=[f"D{i}" for i in range(8)])
    assert getattr(result.ax.get_legend(), "_ncols", None) == 2
