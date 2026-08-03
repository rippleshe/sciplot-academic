"""
Round-32 tests for plot_calendar_heatmap (日历热图).
"""

from __future__ import annotations

import datetime

import numpy as np
import pytest

import sciplot as sp
from sciplot._plots.timeseries import _coerce_to_date


@pytest.fixture()
def calendar_data():
    rng = np.random.default_rng(8)
    dates = [datetime.date(2024, 1, 1) + datetime.timedelta(days=i) for i in range(366)]
    values = rng.poisson(3, 366).astype(float)
    return dates, values


def test_calendar_basic(calendar_data, cleanup_figures):
    dates, values = calendar_data
    result = sp.plot_calendar_heatmap(dates, values)
    assert result.fig is not None
    assert len(result.fig.axes) == 2  # 主图 + colorbar
    scatter = result.ax.collections[0]
    assert len(scatter.get_offsets()) == 366


def test_calendar_weekday_labels(calendar_data, cleanup_figures):
    """默认周一起始，标签为一~日。"""
    dates, values = calendar_data
    result = sp.plot_calendar_heatmap(dates, values)
    yt = [t.get_text() for t in result.ax.get_yticklabels()]
    assert yt == ["一", "二", "三", "四", "五", "六", "日"]


def test_calendar_sunday_start(calendar_data, cleanup_figures):
    """weekday_start=6 时周日排首行。"""
    dates, values = calendar_data
    result = sp.plot_calendar_heatmap(dates, values, weekday_start=6)
    yt = [t.get_text() for t in result.ax.get_yticklabels()]
    assert yt[0] == "日"


def test_calendar_string_dates(calendar_data, cleanup_figures):
    """字符串日期 YYYY-MM-DD 可解析。"""
    dates, values = calendar_data
    str_dates = [d.strftime("%Y-%m-%d") for d in dates]
    result = sp.plot_calendar_heatmap(str_dates, values)
    assert result.fig is not None


def test_calendar_np_datetime64(calendar_data, cleanup_figures):
    dates, values = calendar_data
    np_dates = np.array([np.datetime64(d) for d in dates])
    result = sp.plot_calendar_heatmap(np_dates, values)
    assert result.fig is not None


def test_calendar_cross_year(cleanup_figures):
    """跨年数据正常绘制（年间隔）。"""
    dates = [
        datetime.date(2023, 12, 25) + datetime.timedelta(days=i)
        for i in range(20)
    ]
    values = np.ones(20)
    result = sp.plot_calendar_heatmap(dates, values)
    assert result.fig is not None


def test_calendar_month_lines(calendar_data, cleanup_figures):
    dates, values = calendar_data
    result = sp.plot_calendar_heatmap(dates, values, show_month_lines=True)
    assert len(result.ax.get_xticklabels()) >= 12


def test_calendar_no_month_lines(calendar_data, cleanup_figures):
    dates, values = calendar_data
    result = sp.plot_calendar_heatmap(dates, values, show_month_lines=False)
    assert len(result.ax.get_xticklabels()) == 0


def test_calendar_colorbar_label(calendar_data, cleanup_figures):
    dates, values = calendar_data
    result = sp.plot_calendar_heatmap(dates, values, colorbar_label="事件数")
    assert result.fig.axes[-1].get_ylabel() == "事件数"


def test_calendar_length_mismatch_raises(cleanup_figures):
    dates = [datetime.date(2024, 1, 1), datetime.date(2024, 1, 2)]
    with pytest.raises(ValueError, match="不一致"):
        sp.plot_calendar_heatmap(dates, [1.0])


def test_calendar_bad_date_string_raises(cleanup_figures):
    with pytest.raises(ValueError, match="无法解析"):
        sp.plot_calendar_heatmap(["2024/01/01"], [1.0])


def test_calendar_bad_weekday_start_raises(calendar_data, cleanup_figures):
    dates, values = calendar_data
    with pytest.raises(ValueError, match="weekday_start"):
        sp.plot_calendar_heatmap(dates, values, weekday_start=3)


def test_calendar_nan_values_raises(calendar_data, cleanup_figures):
    dates, values = calendar_data
    values[0] = np.nan
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_calendar_heatmap(dates, values)


def test_calendar_alias_and_export(calendar_data, cleanup_figures):
    dates, values = calendar_data
    assert callable(sp.plot_calendar_heatmap)
    assert callable(sp.calendar_heatmap)


def test_coerce_to_date_conversion(cleanup_figures):
    """_coerce_to_date 支持 datetime/date/np.datetime64/str 四类输入。"""
    d = datetime.date(2024, 5, 6)
    assert _coerce_to_date(datetime.datetime(2024, 5, 6, 12, 30)) == d
    assert _coerce_to_date(d) == d
    assert _coerce_to_date(np.datetime64("2024-05-06")) == d
    assert _coerce_to_date("2024-05-06") == d


def test_coerce_to_date_invalid(cleanup_figures):
    """非法输入分别抛 ValueError（字符串格式错）与 TypeError（类型错）。"""
    with pytest.raises(ValueError, match="无法解析日期字符串"):
        _coerce_to_date("2024/05/06")
    with pytest.raises(TypeError, match="元素必须是 datetime/date/字符串"):
        _coerce_to_date(12345)


def test_coerce_to_date_truncates_time(cleanup_figures):
    """np.datetime64 带时间部分时截断为日期。"""
    assert _coerce_to_date(np.datetime64("2024-05-06T23:59:59")) == datetime.date(2024, 5, 6)


def test_calendar_save_png(tmp_path, calendar_data, cleanup_figures):
    dates, values = calendar_data
    result = sp.plot_calendar_heatmap(dates, values, colorbar_label="事件数")
    paths = result.save(str(tmp_path / "calendar"), formats=("png",), dpi=100)
    assert paths[0].exists() and paths[0].stat().st_size > 0
