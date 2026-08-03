"""
Round-41 tests for figure_panels (Nature 级复合图布局).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp


def test_figure_panels_basic(cleanup_figures):
    fig, axes = sp.figure_panels(2, 2)
    assert fig is not None
    assert axes.shape == (2, 2)


def test_figure_panels_single_row_squeeze(cleanup_figures):
    fig, axes = sp.figure_panels(1, 3)
    assert axes.shape == (3,)


def test_figure_panels_width_ratios(cleanup_figures):
    fig, axes = sp.figure_panels(1, 2, widths=[2, 1])
    # 主面板宽度应约为注释面板的 2 倍
    gs = axes[0].get_subplotspec().get_gridspec()
    ratios = gs.get_width_ratios()
    assert abs(ratios[0] / ratios[1] - 2.0) < 1e-9


def test_figure_panels_height_ratios(cleanup_figures):
    fig, axes = sp.figure_panels(2, 1, heights=[3, 1])
    gs = axes[0].get_subplotspec().get_gridspec()
    ratios = gs.get_height_ratios()
    assert abs(ratios[0] / ratios[1] - 3.0) < 1e-9


def test_figure_panels_no_labels(cleanup_figures):
    fig, axes = sp.figure_panels(1, 2, panel_labels=False)
    texts = [t.get_text() for a in axes for t in a.texts]
    assert all(not t.startswith("(a)") for t in texts)


def test_figure_panels_labels_added(cleanup_figures):
    fig, axes = sp.figure_panels(1, 2, panel_labels=True)
    texts = [t.get_text() for a in axes for t in a.texts]
    assert "(a)" in texts and "(b)" in texts


def test_figure_panels_invalid_dims_raises(cleanup_figures):
    with pytest.raises(ValueError, match="正整数"):
        sp.figure_panels(0, 2)


def test_figure_panels_widths_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="widths 长度"):
        sp.figure_panels(1, 3, widths=[1, 2])


def test_figure_panels_heights_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="heights 长度"):
        sp.figure_panels(3, 1, heights=[1, 2])


def test_figure_panels_export(cleanup_figures):
    assert callable(sp.figure_panels)
    assert "figure_panels" in sp.__all__


def test_figure_panels_sharex(cleanup_figures):
    fig, axes = sp.figure_panels(2, 1, sharex=True)
    assert axes[0].get_shared_x_axes().joined(axes[0], axes[1])


def test_figure_panels_works_with_plots(tmp_path, cleanup_figures):
    """模板落地：2x2 布局中每个面板用 matplotlib 原生 API 画不同类型的图。"""
    fig, axes = sp.figure_panels(2, 2, venue="thesis")
    rng = np.random.default_rng(5)
    x = np.linspace(0, 10, 60)
    axes[0].plot(x, np.sin(x))
    axes[0].plot(x, np.cos(x))
    axes[1].hist(rng.normal(0, 1, 300), bins=30)
    axes[2].scatter(rng.normal(0, 1, 50), rng.normal(0, 1, 50), s=20, alpha=0.7)
    axes[3].bar(["A", "B", "C"], [3, 1, 2])
    paths = sp.save(fig, tmp_path / "panels", formats=("png",))
    assert paths[0].exists()
