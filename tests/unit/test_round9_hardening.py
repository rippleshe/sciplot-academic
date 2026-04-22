"""
Round-9 hardening tests for API consistency and usability fixes.
"""

from __future__ import annotations

import numpy as np
import pytest
import matplotlib.pyplot as plt

import sciplot as sp
from sciplot._core.style import get_current_lang


def test_plot_lollipop_accepts_lang(cleanup_figures, reset_style):
    result = sp.plot_lollipop(["A", "B"], np.array([1.0, 2.0]), lang="en")
    assert isinstance(result, sp.PlotResult)
    assert get_current_lang() == "en"


def test_plot_multi_area_non_stacked_draws_boundary_lines(cleanup_figures):
    x = np.arange(5)
    y_list = [
        np.array([1.0, 2.0, 3.0, 2.5, 2.0]),
        np.array([0.8, 1.3, 2.2, 1.8, 1.5]),
    ]

    result = sp.plot_multi_area(x, y_list, labels=["A", "B"], stacked=False)

    assert len(result.ax.collections) == 2
    assert len(result.ax.lines) == 2


def test_plot_confidence_fill_kwargs_applied_to_fill(cleanup_figures):
    x = np.linspace(0, 10, 40)
    y_mean = np.sin(x)
    y_std = np.full_like(x, 0.2)

    result = sp.plot_confidence(
        x,
        y_mean,
        y_std,
        fill_kwargs={"hatch": "//", "edgecolor": "black"},
    )

    assert len(result.ax.lines) == 1
    assert len(result.ax.collections) >= 1
    assert result.ax.collections[0].get_hatch() == "//"


def test_plot_result_multi_axes_targeted_layers(cleanup_figures):
    fig, axes = plt.subplots(1, 2)
    result = sp.PlotResult(fig, axes)

    result.plot([0, 1], [0, 1], ax_index=1)
    result.scatter([0, 1], [1, 0], ax_index=0)
    result.annotate("pt", (0.5, 0.5), ax_index=1)

    assert len(axes[0].lines) == 0
    assert len(axes[1].lines) == 1
    assert len(axes[0].collections) == 1
    assert any(text.get_text() == "pt" for text in axes[1].texts)


def test_plot_result_tick_params_default_inward(cleanup_figures):
    fig, axes = plt.subplots(1, 2)
    result = sp.PlotResult(fig, axes)

    result.tick_params()

    assert axes[0].xaxis.majorTicks[0]._tickdir == "in"
    assert axes[1].xaxis.majorTicks[0]._tickdir == "in"


def test_combo_result_ylabels_side_helpers(cleanup_figures):
    result = sp.plot_combo(
        x=["Q1", "Q2"],
        bar_data={"销量": [10.0, 12.0]},
        line_data={"增长率": [0.1, 0.2]},
    )

    result.ylabel_left("左轴").ylabel_right("右轴")

    assert result.ax_bar.get_ylabel() == "左轴"
    assert result.ax_line is not None
    assert result.ax_line.get_ylabel() == "右轴"


def test_gridspec_result_add_panel_labels(cleanup_figures):
    result = sp.create_gridspec(1, 2)
    result.add_subplot(result.gs[0, 0])
    result.add_subplot(result.gs[0, 1])

    result.add_panel_labels()

    labels = [text.get_text() for ax in result.fig.axes for text in ax.texts]
    assert "(a)" in labels
    assert "(b)" in labels


def test_plot_result_save_accepts_single_string_format(cleanup_figures, tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    result = sp.PlotResult(fig, ax)

    output = tmp_path / "single_format"
    saved_paths = result.save(str(output), formats="png")

    assert len(saved_paths) == 1
    assert saved_paths[0].suffix.lower() == ".png"
    assert saved_paths[0].exists()


def test_plot_result_ax_index_out_of_range_raises(cleanup_figures):
    fig, axes = plt.subplots(1, 2)
    result = sp.PlotResult(fig, axes)

    with pytest.raises(IndexError, match="ax_index"):
        result.plot([0, 1], [1, 2], ax_index=2)


def test_context_partial_lang_override_keeps_venue_and_palette(
    cleanup_figures, reset_style
):
    x = np.array([0.0, 1.0, 2.0])
    y = np.array([1.0, 2.0, 3.0])

    with sp.style_context("ieee", palette="earth", lang="en"):
        before_size = tuple(plt.rcParams["figure.figsize"])
        before_colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

        sp.plot(x, y, lang="zh")

        after_size = tuple(plt.rcParams["figure.figsize"])
        after_colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]

        assert after_size == pytest.approx(before_size)
        assert after_colors[:5] == before_colors[:5]
        assert get_current_lang() == "zh"


def test_exported_palette_constants_are_read_only():
    """验证配色常量外层只读保护有效，且类型与 get_palette() 一致。"""
    # 外层 Dict 应该是只读的
    with pytest.raises(TypeError):
        sp.PASTEL_PALETTE["new"] = ("#000000",)

    # 值类型应该与 get_palette() 返回类型一致（List）
    from sciplot import get_palette
    palette_from_const = sp.PASTEL_PALETTE["pastel"]
    palette_from_func = get_palette("pastel")
    assert type(palette_from_const) == type(palette_from_func), \
        f"类型不一致: {type(palette_from_const)} vs {type(palette_from_func)}"
