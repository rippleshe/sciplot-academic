"""负索引支持测试 — PlotResult, ComboPlotResult, GridSpecResult"""
import pytest
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sciplot as sp


@pytest.fixture(autouse=True)
def cleanup():
    yield
    plt.close("all")
    sp.reset_style()


class TestPlotResultNegativeIndexing:
    def test_negative_index_minus1(self):
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)
        assert result[-1] is ax

    def test_negative_index_minus2(self):
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)
        assert result[-2] is fig

    def test_negative_index_out_of_range(self):
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)
        with pytest.raises(IndexError):
            result[-3]

    def test_positive_index_out_of_range(self):
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)
        with pytest.raises(IndexError):
            result[2]

    def test_invalid_type_index(self):
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)
        with pytest.raises(TypeError):
            result["invalid"]

    def test_slice_works(self):
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)
        sliced = result[:]
        assert len(sliced) == 2
        assert sliced[0] is fig
        assert sliced[1] is ax

    def test_tuple_unpack_still_works(self):
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)
        f, a = result
        assert f is fig
        assert a is ax

    def test_len_still_2(self):
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)
        assert len(result) == 2


class TestComboPlotResultNegativeIndexing:
    def test_negative_index_minus1(self):
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        result = sp.ComboPlotResult(fig, ax1, ax2)
        assert result[-1] is ax2

    def test_negative_index_minus2(self):
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        result = sp.ComboPlotResult(fig, ax1, ax2)
        assert result[-2] is ax1

    def test_negative_index_minus3(self):
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        result = sp.ComboPlotResult(fig, ax1, ax2)
        assert result[-3] is fig

    def test_negative_index_out_of_range(self):
        fig, ax1 = plt.subplots()
        result = sp.ComboPlotResult(fig, ax1)
        with pytest.raises(IndexError):
            result[-4]

    def test_positive_index_out_of_range(self):
        fig, ax1 = plt.subplots()
        result = sp.ComboPlotResult(fig, ax1)
        with pytest.raises(IndexError):
            result[3]

    def test_none_ax_line_negative_index(self):
        fig, ax1 = plt.subplots()
        result = sp.ComboPlotResult(fig, ax1, ax_line=None)
        assert result[-1] is None
        assert result[-2] is ax1
        assert result[-3] is fig


class TestGridSpecResultNegativeIndexing:
    def test_negative_index_minus1(self):
        fig = plt.figure()
        gs = fig.add_gridspec(2, 2)
        result = sp.GridSpecResult(fig, gs)
        assert result[-1] is gs

    def test_negative_index_minus2(self):
        fig = plt.figure()
        gs = fig.add_gridspec(2, 2)
        result = sp.GridSpecResult(fig, gs)
        assert result[-2] is fig

    def test_negative_index_out_of_range(self):
        fig = plt.figure()
        gs = fig.add_gridspec(2, 2)
        result = sp.GridSpecResult(fig, gs)
        with pytest.raises(IndexError):
            result[-3]

    def test_positive_index_out_of_range(self):
        fig = plt.figure()
        gs = fig.add_gridspec(2, 2)
        result = sp.GridSpecResult(fig, gs)
        with pytest.raises(IndexError):
            result[2]
