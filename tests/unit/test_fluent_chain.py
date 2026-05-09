"""链式调用 API 测试 — PlotChain, FigureWrapper"""
import pytest
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sciplot as sp
from pathlib import Path


@pytest.fixture(autouse=True)
def cleanup():
    yield
    plt.close("all")
    sp.reset_style()


@pytest.fixture
def xy_data():
    x = np.linspace(0, 10, 100)
    return x, np.sin(x), np.cos(x)


class TestPlotChainEntry:
    def test_style_entry(self, xy_data):
        x, y, _ = xy_data
        result = sp.style("nature")
        assert isinstance(result, sp.PlotChain)

    def test_palette_entry(self, xy_data):
        x, y, _ = xy_data
        result = sp.palette("ocean")
        assert isinstance(result, sp.PlotChain)

    def test_chain_entry(self, xy_data):
        x, y, _ = xy_data
        result = sp.chain("ieee", "earth")
        assert isinstance(result, sp.PlotChain)


class TestPlotChainStyleMethods:
    def test_style_method(self, xy_data):
        x, y, _ = xy_data
        result = sp.chain().style("nature")
        assert isinstance(result, sp.PlotChain)

    def test_palette_method(self, xy_data):
        x, y, _ = xy_data
        result = sp.chain().palette("ocean")
        assert isinstance(result, sp.PlotChain)

    def test_lang_method(self, xy_data):
        x, y, _ = xy_data
        result = sp.chain().lang("en")
        assert isinstance(result, sp.PlotChain)

    def test_figsize_method(self, xy_data):
        x, y, _ = xy_data
        result = sp.chain().figsize(8, 6)
        assert isinstance(result, sp.PlotChain)


class TestPlotChainPlotMethods:
    def test_plot(self, xy_data):
        x, y, _ = xy_data
        result = sp.style("nature").plot(x, y)
        assert isinstance(result, sp.FigureWrapper)
        assert result.fig is not None
        assert result.ax is not None

    def test_scatter(self, xy_data):
        x, y, _ = xy_data
        result = sp.style("nature").scatter(x, y)
        assert isinstance(result, sp.FigureWrapper)

    def test_bar(self):
        result = sp.style("nature").bar(["A", "B", "C"], [1, 2, 3])
        assert isinstance(result, sp.FigureWrapper)

    def test_hist(self):
        data = np.random.randn(100)
        result = sp.style("nature").hist(data)
        assert isinstance(result, sp.FigureWrapper)

    def test_boxplot(self):
        data = [np.random.randn(100) for _ in range(3)]
        result = sp.style("nature").boxplot(data)
        assert isinstance(result, sp.FigureWrapper)

    def test_fill_between(self, xy_data):
        x, y, _ = xy_data
        result = sp.style("nature").fill_between(x, y, -y)
        assert isinstance(result, sp.FigureWrapper)

    def test_errorbar(self, xy_data):
        x, y, _ = xy_data
        yerr = np.abs(np.random.randn(len(y)) * 0.1)
        result = sp.style("nature").errorbar(x, y, yerr=yerr)
        assert isinstance(result, sp.FigureWrapper)

    def test_area(self, xy_data):
        x, y, _ = xy_data
        result = sp.style("nature").area(x, y)
        assert isinstance(result, sp.FigureWrapper)


class TestFigureWrapper:
    def test_get_figure(self, xy_data):
        x, y, _ = xy_data
        wrapper = sp.style("nature").plot(x, y)
        assert wrapper.get_figure() is wrapper.fig

    def test_get_axes(self, xy_data):
        x, y, _ = xy_data
        wrapper = sp.style("nature").plot(x, y)
        assert wrapper.get_axes() is wrapper.ax

    def test_unwrap(self, xy_data):
        x, y, _ = xy_data
        wrapper = sp.style("nature").plot(x, y)
        fig, ax = wrapper.unwrap()
        assert fig is wrapper.fig
        assert ax is wrapper.ax

    def test_chain_plot_then_save(self, xy_data, tmp_path):
        x, y, _ = xy_data
        output = tmp_path / "chain_test"
        result = sp.style("nature").plot(x, y)
        paths = result.save(str(output), formats=("png",))
        assert len(paths) == 1
        assert paths[0].exists()

    def test_metadata(self, xy_data):
        x, y, _ = xy_data
        wrapper = sp.style("nature").palette("pastel").plot(x, y)
        meta = wrapper.metadata
        assert "venue" in meta
        assert "palette" in meta


class TestPlotChainFigsizeBeforePlot:
    def test_figsize_before_plot(self, xy_data):
        x, y, _ = xy_data
        result = sp.style("nature").figsize(10, 6).plot(x, y)
        assert isinstance(result, sp.FigureWrapper)
        w, h = result.fig.get_size_inches()
        assert abs(w - 10) < 0.1
        assert abs(h - 6) < 0.1


class TestPlotChainStyleAfterPlotError:
    def test_style_after_plot_raises(self, xy_data):
        x, y, _ = xy_data
        chain = sp.style("nature").plot(x, y)
        with pytest.raises(RuntimeError):
            chain._chain.style("ieee")

    def test_palette_after_plot_raises(self, xy_data):
        x, y, _ = xy_data
        chain = sp.style("nature").plot(x, y)
        with pytest.raises(RuntimeError):
            chain._chain.palette("earth")

    def test_lang_after_plot_raises(self, xy_data):
        x, y, _ = xy_data
        chain = sp.style("nature").plot(x, y)
        with pytest.raises(RuntimeError):
            chain._chain.lang("en")

    def test_figsize_after_plot_raises(self, xy_data):
        x, y, _ = xy_data
        chain = sp.style("nature").plot(x, y)
        with pytest.raises(RuntimeError):
            chain._chain.figsize(10, 6)
