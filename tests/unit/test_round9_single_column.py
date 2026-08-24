"""Round-9: dense multi-series and IEEE single-column publication floor."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

import sciplot as sp


def _many_labels(n: int) -> list[str]:
    return [f"Experimental Method {i + 1}" for i in range(n)]


def test_plot_multi_line_explicit_linestyle_wins(cleanup_figures):
    x = np.linspace(0, 1, 20)
    ys = [x + i for i in range(8)]
    result = sp.plot_multi_line(x, ys, labels=_many_labels(8), linestyle=":")
    assert all(line.get_linestyle() == ":" for line in result.ax.lines)


def test_plot_multi_line_single_explicit_color_gets_redundant_linestyles(cleanup_figures):
    x = np.linspace(0, 1, 20)
    ys = [x + i for i in range(4)]
    result = sp.plot_multi_line(x, ys, labels=_many_labels(4), color="black")
    styles = [line.get_linestyle() for line in result.ax.lines]
    assert len(set(styles)) == 4
    assert all(line.get_color() == "black" for line in result.ax.lines)


def test_multi_timeseries_repeated_palette_colors_gain_linestyle(cleanup_figures):
    t = np.arange(20)
    ys = [np.sin(t / 4 + i * 0.2) for i in range(8)]
    result = sp.plot_multi_timeseries(t, ys, labels=_many_labels(8), palette="pastel")
    assert result.ax.lines[0].get_color() == result.ax.lines[6].get_color()
    assert result.ax.lines[0].get_linestyle() != result.ax.lines[6].get_linestyle()


def test_multi_timeseries_explicit_single_color_uses_line_redundancy(cleanup_figures):
    t = np.arange(20)
    ys = [np.sin(t / 4 + i * 0.2) for i in range(4)]
    result = sp.plot_multi_timeseries(t, ys, labels=_many_labels(4), color="black")
    assert all(line.get_color() == "black" for line in result.ax.lines)
    assert len({line.get_linestyle() for line in result.ax.lines}) == 4


def test_multi_density_repeated_palette_colors_gain_linestyle(cleanup_figures):
    rng = np.random.default_rng(9)
    data = [rng.normal(i * 0.15, 1.0, 100) for i in range(8)]
    result = sp.plot_multi_density(data, labels=_many_labels(8), palette="pastel")
    assert result.ax.lines[0].get_color() == result.ax.lines[6].get_color()
    assert result.ax.lines[0].get_linestyle() != result.ax.lines[6].get_linestyle()


def test_ridgeline_repeated_palette_colors_gain_linestyle(cleanup_figures):
    rng = np.random.default_rng(10)
    data = [rng.normal(i * 0.2, 1.0, 100) for i in range(8)]
    result = sp.plot_ridgeline(data, labels=_many_labels(8), palette="pastel")
    assert result.ax.lines[0].get_color() == result.ax.lines[6].get_color()
    assert result.ax.lines[0].get_linestyle() != result.ax.lines[6].get_linestyle()


def test_ridgeline_explicit_color_does_not_conflict_with_palette(cleanup_figures):
    rng = np.random.default_rng(11)
    data = [rng.normal(i * 0.2, 1.0, 80) for i in range(4)]
    result = sp.plot_ridgeline(data, labels=_many_labels(4), color="black")
    assert all(line.get_color() == "black" for line in result.ax.lines)
    assert len({line.get_linestyle() for line in result.ax.lines}) == 4


def test_smart_legend_moves_dense_narrow_legend_below(cleanup_figures):
    fig, ax = plt.subplots(figsize=(3.5, 3.0))
    x = np.linspace(0, 1, 20)
    for i, label in enumerate(_many_labels(12)):
        ax.plot(x, x + i * 0.02, label=label)
    sp.smart_legend(ax)
    legend = ax.get_legend()
    assert legend is not None
    # "upper center" = 9; bbox anchor 在 axes 下方。
    assert getattr(legend, "_loc", None) == 9
    anchor = legend.get_bbox_to_anchor().transformed(ax.transAxes.inverted())
    assert anchor.y0 < 0
    assert getattr(legend, "_ncols", None) <= 2


def test_smart_legend_explicit_loc_is_respected_on_narrow_figure(cleanup_figures):
    fig, ax = plt.subplots(figsize=(3.5, 3.0))
    x = np.linspace(0, 1, 20)
    for i, label in enumerate(_many_labels(12)):
        ax.plot(x, x + i * 0.02, label=label)
    sp.smart_legend(ax, loc="upper left")
    legend = ax.get_legend()
    assert legend is not None
    assert getattr(legend, "_loc", None) == 2
