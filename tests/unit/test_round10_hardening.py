"""
Round-10 hardening tests for context-state rollback and timeseries type safety.
"""

from __future__ import annotations

from datetime import date

import matplotlib.pyplot as plt
import numpy as np
import pytest

import sciplot as sp
from sciplot._core.style import get_current_lang


def _cycle_colors():
    return [item["color"] for item in plt.rcParams["axes.prop_cycle"]]


def test_style_context_restores_lang_on_exit(cleanup_figures):
    try:
        sp.setup_style(lang="en")
        assert get_current_lang() == "en"

        with sp.style_context(lang="zh"):
            assert get_current_lang() == "zh"

        assert get_current_lang() == "en"
    finally:
        sp.setup_style(lang="zh")


def test_style_context_lang_only_preserves_venue_and_palette(cleanup_figures):
    try:
        sp.setup_style("ieee", "earth", lang="en")
        before_size = tuple(plt.rcParams["figure.figsize"])
        before_colors = _cycle_colors()

        with sp.style_context(lang="zh"):
            inside_size = tuple(plt.rcParams["figure.figsize"])
            inside_colors = _cycle_colors()
            assert inside_size == pytest.approx(before_size)
            assert inside_colors[:5] == before_colors[:5]
            assert get_current_lang() == "zh"

        assert get_current_lang() == "en"
    finally:
        sp.setup_style(lang="zh")


def test_style_context_venue_only_preserves_palette_and_lang(cleanup_figures):
    try:
        sp.setup_style("nature", "ocean", lang="en")
        before_colors = _cycle_colors()
        before_fontsize = float(plt.rcParams["font.size"])

        with sp.style_context(venue="ieee"):
            inside_colors = _cycle_colors()
            assert inside_colors[:6] == before_colors[:6]
            assert get_current_lang() == "en"
            assert float(plt.rcParams["font.size"]) < before_fontsize

        assert get_current_lang() == "en"
    finally:
        sp.setup_style(lang="zh")


def test_plot_timeseries_rejects_string_event_time_for_numeric_axis(cleanup_figures):
    t = np.arange(5)
    y = np.linspace(0.0, 1.0, 5)

    with pytest.raises(TypeError, match=r"events\[0\]\['time'\]"):
        sp.plot_timeseries(t, y, events=[{"time": "2026-01-01", "label": "bad"}])


def test_plot_timeseries_rejects_numeric_region_for_datetime_axis(cleanup_figures):
    t = [date(2026, 1, d) for d in range(1, 6)]
    y = np.linspace(0.0, 1.0, 5)

    with pytest.raises(TypeError, match=r"shade_regions\[0\]\['start'\]"):
        sp.plot_timeseries(
            t,
            y,
            shade_regions=[{"start": 1, "end": 3, "color": "#cccccc"}],
        )


def test_plot_multi_timeseries_rejects_datetime_event_for_numeric_axis(cleanup_figures):
    t = np.arange(5)
    y_list = [np.arange(5), np.arange(5) + 1]

    with pytest.raises(TypeError, match=r"events\[0\]\['time'\]"):
        sp.plot_multi_timeseries(
            t,
            y_list,
            events=[{"time": date(2026, 1, 1), "label": "bad"}],
        )
