"""
Round-6 hardening tests for critical runtime behaviors.
"""

from __future__ import annotations

import numpy as np
import pytest
import matplotlib.pyplot as plt

import sciplot as sp
from sciplot._core.style import get_current_lang


class TestCriticalHardeningRound6:
    def test_context_partial_palette_override_keeps_context_venue_and_lang(
        self, cleanup_figures, reset_style
    ):
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([1.0, 2.0, 3.0])

        with sp.style_context("ieee", palette="earth", lang="en"):
            before_size = tuple(plt.rcParams["figure.figsize"])
            assert get_current_lang() == "en"

            sp.plot(x, y, palette="ocean")

            after_size = tuple(plt.rcParams["figure.figsize"])
            assert after_size == pytest.approx(before_size)
            assert get_current_lang() == "en"

            cycle_colors = [item["color"] for item in plt.rcParams["axes.prop_cycle"]]
            assert cycle_colors[:3] == sp.get_palette("ocean")[:3]

    def test_plot_area_fill_false_does_not_apply_fill_alpha_to_line(
        self, cleanup_figures
    ):
        x = np.array([0.0, 1.0, 2.0, 3.0])
        y = np.array([1.0, 2.5, 1.5, 3.0])

        result = sp.plot_area(x, y, fill=False, alpha=0.2, color="#ff0000")
        line = result.ax.lines[0]
        assert line.get_alpha() in (None, 1.0)

    def test_plot_area_fill_true_applies_alpha_to_fill_only(self, cleanup_figures):
        x = np.array([0.0, 1.0, 2.0, 3.0])
        y = np.array([1.0, 2.5, 1.5, 3.0])

        result = sp.plot_area(x, y, fill=True, alpha=0.2, color="#ff0000")
        line = result.ax.lines[0]
        assert line.get_alpha() in (None, 1.0)
        assert len(result.ax.collections) >= 1
        assert result.ax.collections[0].get_alpha() == pytest.approx(0.2)

    def test_plot_radar_respects_venue_dependent_size(self, cleanup_figures):
        categories = ["A", "B", "C", "D"]
        values = [[0.8, 0.7, 0.9, 0.6]]

        ieee = sp.plot_radar(categories, values, venue="ieee")
        nature = sp.plot_radar(categories, values, venue="nature")

        w_ieee, h_ieee = ieee.fig.get_size_inches()
        w_nat, h_nat = nature.fig.get_size_inches()

        assert w_ieee == pytest.approx(h_ieee)
        assert w_nat == pytest.approx(h_nat)
        assert w_nat > w_ieee

    def test_plot_timeseries_event_annotation_uses_axes_fraction(self, cleanup_figures):
        t = np.arange(10)
        y = np.array([0, 1, 2, 3, 4, 5, 10, 7, 8, 9], dtype=float)

        result = sp.plot_timeseries(
            t,
            y,
            rolling_mean=3,
            events=[{"time": 5, "label": "milestone", "color": "red"}],
        )

        annotations = result.ax.texts
        assert len(annotations) >= 1
        ann = annotations[0]
        assert ann.xycoords == ("data", "axes fraction")
        assert ann.xy[1] == pytest.approx(0.95)

    def test_plot_violin_requires_labels_match_data_length(self, cleanup_figures):
        data = [np.array([1.0, 1.2, 1.4]), np.array([2.0, 2.2, 2.4])]
        with pytest.raises(ValueError, match="labels 长度"):
            sp.plot_violin(data, labels=["only-one-label"])

    def test_lazy_extension_names_not_in_all(self):
        lazy_names = {
            "plot_network",
            "plot_network_from_matrix",
            "plot_network_communities",
            "plot_dendrogram",
            "plot_clustermap",
            "plot_venn2",
            "plot_venn3",
        }
        assert lazy_names.isdisjoint(set(sp.__all__))
