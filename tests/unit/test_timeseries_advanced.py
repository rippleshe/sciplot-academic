"""时序图表高级功能测试 — events, shade_regions, rolling_mean, datetime, slope"""
import pytest
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from datetime import date, datetime
import sciplot as sp


@pytest.fixture(autouse=True)
def cleanup():
    yield
    plt.close("all")
    sp.reset_style()


@pytest.fixture
def numeric_timeseries():
    np.random.seed(42)
    t = np.arange(100)
    y = np.cumsum(np.random.randn(100))
    return t, y


@pytest.fixture
def datetime_timeseries():
    dates = [date(2024, 1, i + 1) for i in range(30)]
    values = np.random.randn(30).cumsum()
    return dates, values


class TestPlotTimeseriesEvents:
    def test_single_event(self, numeric_timeseries):
        t, y = numeric_timeseries
        result = sp.plot_timeseries(
            t, y,
            events=[{"time": 50, "label": "Event A", "color": "red"}],
        )
        assert result.fig is not None

    def test_multiple_events(self, numeric_timeseries):
        t, y = numeric_timeseries
        result = sp.plot_timeseries(
            t, y,
            events=[
                {"time": 20, "label": "Start"},
                {"time": 50, "label": "Mid"},
                {"time": 80, "label": "End"},
            ],
        )
        assert result.fig is not None

    def test_event_missing_time_raises(self):
        t = np.arange(10)
        y = np.random.randn(10)
        with pytest.raises(ValueError):
            sp.plot_timeseries(t, y, events=[{"label": "no time"}])

    def test_event_invalid_type_raises(self):
        t = np.arange(10)
        y = np.random.randn(10)
        with pytest.raises(TypeError):
            sp.plot_timeseries(t, y, events="not a list")


class TestPlotTimeseriesShadeRegions:
    def test_single_region(self, numeric_timeseries):
        t, y = numeric_timeseries
        result = sp.plot_timeseries(
            t, y,
            shade_regions=[{"start": 20, "end": 40, "color": "#CCCCCC", "alpha": 0.3}],
        )
        assert result.fig is not None

    def test_multiple_regions(self, numeric_timeseries):
        t, y = numeric_timeseries
        result = sp.plot_timeseries(
            t, y,
            shade_regions=[
                {"start": 10, "end": 20},
                {"start": 50, "end": 60},
            ],
        )
        assert result.fig is not None

    def test_region_missing_start_raises(self):
        t = np.arange(10)
        y = np.random.randn(10)
        with pytest.raises(ValueError):
            sp.plot_timeseries(t, y, shade_regions=[{"end": 5}])


class TestPlotTimeseriesRollingMean:
    def test_rolling_mean(self, numeric_timeseries):
        t, y = numeric_timeseries
        result = sp.plot_timeseries(t, y, rolling_mean=7)
        assert result.fig is not None

    def test_rolling_mean_too_large(self, numeric_timeseries):
        t, y = numeric_timeseries
        # rolling_mean > len(y), should not draw rolling line
        result = sp.plot_timeseries(t, y, rolling_mean=200)
        assert result.fig is not None

    def test_rolling_mean_zero_raises(self, numeric_timeseries):
        t, y = numeric_timeseries
        with pytest.raises(ValueError):
            sp.plot_timeseries(t, y, rolling_mean=0)

    def test_rolling_mean_negative_raises(self, numeric_timeseries):
        t, y = numeric_timeseries
        with pytest.raises(ValueError):
            sp.plot_timeseries(t, y, rolling_mean=-1)

    def test_rolling_mean_float_raises(self, numeric_timeseries):
        t, y = numeric_timeseries
        with pytest.raises(TypeError):
            sp.plot_timeseries(t, y, rolling_mean=3.5)


class TestPlotTimeseriesDatetime:
    def test_datetime_dates(self, datetime_timeseries):
        dates, values = datetime_timeseries
        result = sp.plot_timeseries(dates, values, xlabel="Date")
        assert result.fig is not None

    def test_datetime_with_events(self, datetime_timeseries):
        dates, values = datetime_timeseries
        result = sp.plot_timeseries(
            dates, values,
            events=[{"time": date(2024, 1, 15), "label": "Mid-month"}],
        )
        assert result.fig is not None

    def test_numeric_event_on_datetime_axis_raises(self, datetime_timeseries):
        dates, values = datetime_timeseries
        with pytest.raises(TypeError):
            sp.plot_timeseries(
                dates, values,
                events=[{"time": 15, "label": "numeric on datetime"}],
            )


class TestPlotTimeseriesBasic:
    def test_length_mismatch(self):
        with pytest.raises(ValueError):
            sp.plot_timeseries([1, 2, 3], [1, 2])

    def test_inf_warning(self):
        t = np.arange(10)
        y = np.array([1, 2, np.inf, 4, 5, 6, 7, 8, 9, 10])
        with pytest.warns(UserWarning):
            sp.plot_timeseries(t, y)

    def test_with_label(self, numeric_timeseries):
        t, y = numeric_timeseries
        result = sp.plot_timeseries(t, y, label="Series A")
        legend = result.ax.get_legend()
        assert legend is not None

    def test_with_marker(self, numeric_timeseries):
        t, y = numeric_timeseries
        result = sp.plot_timeseries(t[:20], y[:20], marker="o")
        assert result.fig is not None


class TestPlotMultiTimeseries:
    def test_basic(self):
        t = np.arange(50)
        y1 = np.sin(t * 0.1)
        y2 = np.cos(t * 0.1)
        result = sp.plot_multi_timeseries(t, [y1, y2], labels=["sin", "cos"])
        assert isinstance(result, sp.PlotResult)

    def test_empty_y_list(self):
        with pytest.raises(ValueError):
            sp.plot_multi_timeseries(np.arange(10), [])

    def test_label_length_mismatch(self):
        t = np.arange(10)
        y1 = np.random.randn(10)
        with pytest.raises(ValueError):
            sp.plot_multi_timeseries(t, [y1], labels=["A", "B"])

    def test_y_length_mismatch(self):
        t = np.arange(10)
        y1 = np.random.randn(5)
        with pytest.raises(ValueError):
            sp.plot_multi_timeseries(t, [y1])

    def test_with_events_and_regions(self):
        t = np.arange(100)
        y1 = np.sin(t * 0.1)
        y2 = np.cos(t * 0.1)
        result = sp.plot_multi_timeseries(
            t, [y1, y2],
            labels=["A", "B"],
            events=[{"time": 50, "label": "Event"}],
            shade_regions=[{"start": 20, "end": 40}],
        )
        assert result.fig is not None


class TestPlotSlope:
    def test_basic(self):
        result = sp.plot_slope(
            ["A", "B", "C"],
            [10, 20, 30],
            [15, 25, 20],
        )
        assert isinstance(result, sp.PlotResult)

    def test_with_diff(self):
        result = sp.plot_slope(
            ["A", "B"],
            [10, 20],
            [15, 25],
            show_diff=True,
        )
        assert result.fig is not None

    def test_without_diff(self):
        result = sp.plot_slope(
            ["A", "B"],
            [10, 20],
            [15, 25],
            show_diff=False,
        )
        assert result.fig is not None

    def test_with_grid(self):
        result = sp.plot_slope(
            ["A", "B"],
            [10, 20],
            [15, 25],
            show_grid=True,
        )
        assert result.fig is not None

    def test_empty_labels(self):
        with pytest.raises(ValueError):
            sp.plot_slope([], [], [])

    def test_length_mismatch(self):
        with pytest.raises(ValueError):
            sp.plot_slope(["A", "B"], [1, 2, 3], [4, 5])

    def test_nan_raises(self):
        with pytest.raises(ValueError):
            sp.plot_slope(["A", "B"], [1, np.nan], [3, 4])

    def test_inf_raises(self):
        with pytest.raises(ValueError):
            sp.plot_slope(["A", "B"], [1, np.inf], [3, 4])
