"""
Round-2 hardening tests for plots and extension edge cases.
"""

from __future__ import annotations

from datetime import date

import matplotlib.dates as mdates
import numpy as np
import pytest

import sciplot as sp


class TestStatisticalHardening:
    def test_plot_qq_supports_t_distribution(self, cleanup_figures):
        data = np.random.randn(200)
        result = sp.plot_qq(data, distribution="t")
        assert result.fig is not None


class TestHierarchicalHardening:
    def test_clustermap_single_row_does_not_fail(self, cleanup_figures):
        data = np.random.rand(1, 5)
        result = sp.plot_clustermap(data, row_cluster=True, col_cluster=True)
        assert result.fig is not None

    def test_clustermap_single_column_does_not_fail(self, cleanup_figures):
        data = np.random.rand(5, 1)
        result = sp.plot_clustermap(data, row_cluster=True, col_cluster=True)
        assert result.fig is not None


class TestMultivariateHardening:
    def test_plot_parallel_color_by_index_out_of_range(self, cleanup_figures):
        data = np.random.rand(10, 3)
        with pytest.raises(ValueError):
            sp.plot_parallel(data, color_by=5)

    def test_plot_parallel_rejects_non_numeric_data(self, cleanup_figures):
        data = np.array([["a", "b"], ["c", "d"]], dtype=object)
        with pytest.raises(ValueError):
            sp.plot_parallel(data)


class TestDistributionHardening:
    def test_plot_combo_validates_bar_lengths(self, cleanup_figures):
        with pytest.raises(ValueError):
            sp.plot_combo(["A", "B"], bar_data={"series": [1]})

    def test_plot_combo_validates_line_lengths(self, cleanup_figures):
        with pytest.raises(ValueError):
            sp.plot_combo(
                ["A", "B"],
                bar_data={"bar": [1, 2]},
                line_data={"line": [1]},
            )

    def test_plot_violin_rejects_empty_group(self, cleanup_figures):
        with pytest.raises(ValueError):
            sp.plot_violin([np.array([]), np.array([1.0, 2.0, 3.0])])


class TestAdvancedHardening:
    def test_plot_heatmap_requires_2d_input(self, cleanup_figures):
        with pytest.raises(ValueError):
            sp.plot_heatmap(np.array([1, 2, 3]))

    def test_plot_heatmap_validates_label_lengths(self, cleanup_figures):
        matrix = np.random.rand(3, 4)
        with pytest.raises(ValueError):
            sp.plot_heatmap(matrix, row_labels=["r1"])
        with pytest.raises(ValueError):
            sp.plot_heatmap(matrix, col_labels=["c1"])


class TestTimeseriesHardening:
    def test_plot_timeseries_recognizes_date_objects(self, cleanup_figures):
        t = [date(2024, 1, d) for d in range(1, 8)]
        y = np.arange(7)

        result = sp.plot_timeseries(t, y)
        formatter = result.ax.xaxis.get_major_formatter()
        assert isinstance(formatter, mdates.DateFormatter)
