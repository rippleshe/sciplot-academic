"""
Round-11 hardening tests for audit findings in 2026-04-20 report.
"""

from __future__ import annotations

import importlib

from cycler import cycler
import matplotlib.pyplot as plt
import numpy as np
import pytest

import sciplot as sp
from sciplot._core.context import StyleContext
from sciplot._core.style import (
    get_current_lang,
    get_current_palette,
    get_current_venue,
)


def test_setup_style_invalid_palette_does_not_pollute_thread_local_state(cleanup_figures):
    sp.setup_style("nature", "pastel", "zh")
    before = (get_current_venue(), get_current_palette(), get_current_lang())

    with pytest.raises(ValueError):
        sp.setup_style(palette="invalid_palette_xyz")

    after = (get_current_venue(), get_current_palette(), get_current_lang())
    assert after == before


def test_plot_uses_config_defaults_for_venue_palette_lang(cleanup_figures):
    try:
        sp.reset_config()
        sp.reset_style()

        sp.set_defaults(venue="ieee", palette="earth", lang="en")
        sp.plot([1, 2, 3], [1, 3, 2])

        assert get_current_venue() == "ieee"
        assert get_current_palette() == "earth"
        assert get_current_lang() == "en"

        colors = [item["color"] for item in plt.rcParams["axes.prop_cycle"]]
        assert colors[:5] == sp.get_palette("earth")[:5]
    finally:
        sp.reset_config()
        sp.reset_style()


def test_plot_partial_override_keeps_unspecified_layers_outside_context(cleanup_figures):
    try:
        sp.setup_style("ieee", "earth", "en")

        sp.plot([1, 2], [1, 2], palette="ocean")
        assert get_current_venue() == "ieee"
        assert get_current_palette() == "ocean"
        assert get_current_lang() == "en"

        sp.plot([1, 2], [2, 1], lang="zh")
        assert get_current_venue() == "ieee"
        assert get_current_palette() == "ocean"
        assert get_current_lang() == "zh"
    finally:
        sp.reset_style()


def test_result_save_and_layout_save_respect_config_defaults(temp_dir, cleanup_figures):
    try:
        sp.reset_config()
        sp.set_defaults(dpi=300, formats=("svg",))

        result = sp.plot([1, 2], [1, 2])
        result_paths = result.save("result_cfg", dir=temp_dir)
        assert [p.suffix for p in result_paths] == [".svg"]

        gs_result = sp.create_gridspec(1, 1)
        gs_result.add_subplot(gs_result.gs[0, 0]).plot([1, 2], [2, 3])
        gs_paths = gs_result.save("gridspec_cfg", dir=temp_dir)
        assert [p.suffix for p in gs_paths] == [".svg"]

        fig, ax = sp.plot([1, 2], [3, 4])
        save_paths = sp.save(fig, "save_cfg", dir=temp_dir)
        assert [p.suffix for p in save_paths] == [".svg"]
    finally:
        sp.reset_config()


def test_style_context_get_current_context_returns_active_instance(cleanup_figures):
    assert StyleContext.get_current_context() is None

    with sp.style_context("ieee") as outer:
        assert StyleContext.get_current_context() is outer

        with sp.style_context(palette="earth") as inner:
            assert StyleContext.get_current_context() is inner

        assert StyleContext.get_current_context() is outer

    assert StyleContext.get_current_context() is None


def test_statistical_plots_do_not_crash_on_empty_color_cycle(cleanup_figures):
    y_true = np.array([1.0, 2.0, 3.0, 4.0])
    y_pred = np.array([1.1, 1.9, 3.2, 3.8])

    with sp.style_context(**{"axes.prop_cycle": cycler(color=[])}):
        residuals = sp.plot_residuals(y_true, y_pred)
        qq = sp.plot_qq(np.array([1.0, 1.5, 2.0, 2.5, 3.0]))
        bland = sp.plot_bland_altman(y_true, y_pred)

    assert len(residuals.ax.collections) >= 1
    assert len(qq.ax.collections) >= 1
    assert len(bland.ax.collections) >= 1


def test_scatter_matrix_figsize_follows_venue_semantics(cleanup_figures):
    data = np.random.rand(30, 4)

    ieee_result = sp.plot_scatter_matrix(data, venue="ieee")
    nature_result = sp.plot_scatter_matrix(data, venue="nature")

    w_ieee, h_ieee = ieee_result.fig.get_size_inches()
    w_nature, h_nature = nature_result.fig.get_size_inches()

    assert w_nature > w_ieee
    assert h_nature > h_ieee


def test_registry_module_removed_to_avoid_dead_unwired_surface():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("sciplot._core.registry")
