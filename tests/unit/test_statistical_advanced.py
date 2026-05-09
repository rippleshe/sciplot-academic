"""统计图表高级功能测试 — plot_bland_altman, plot_multi_density, plot_qq各种分布, plot_residuals LOESS"""
import pytest
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sciplot as sp

try:
    import scipy
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

pytestmark_scipy = pytest.mark.skipif(not HAS_SCIPY, reason="scipy not installed")


@pytest.fixture(autouse=True)
def cleanup():
    yield
    plt.close("all")
    sp.reset_style()


class TestPlotResiduals:
    def test_basic(self):
        y_true = np.array([1, 2, 3, 4, 5], dtype=float)
        y_pred = np.array([1.1, 2.2, 2.9, 4.1, 4.8], dtype=float)
        result = sp.plot_residuals(y_true, y_pred)
        assert isinstance(result, sp.PlotResult)

    def test_with_zero_line(self):
        y_true = np.arange(10, dtype=float)
        y_pred = y_true + np.random.randn(10) * 0.1
        result = sp.plot_residuals(y_true, y_pred, show_zero_line=True)
        assert result.fig is not None

    def test_without_zero_line(self):
        y_true = np.arange(10, dtype=float)
        y_pred = y_true + np.random.randn(10) * 0.1
        result = sp.plot_residuals(y_true, y_pred, show_zero_line=False)
        assert result.fig is not None

    def test_length_mismatch(self):
        with pytest.raises(ValueError):
            sp.plot_residuals(np.array([1, 2, 3]), np.array([1, 2]))

    def test_custom_labels(self):
        y_true = np.arange(10, dtype=float)
        y_pred = y_true + np.random.randn(10) * 0.1
        result = sp.plot_residuals(y_true, y_pred, xlabel="Predicted", ylabel="Residual", title="Test")
        assert result.ax.get_xlabel() == "Predicted"


@pytestmark_scipy
class TestPlotQqDistributions:
    def test_norm(self):
        data = np.random.normal(0, 1, 100)
        result = sp.plot_qq(data, distribution="norm")
        assert result.fig is not None

    def test_expon(self):
        data = np.random.exponential(1, 100)
        result = sp.plot_qq(data, distribution="expon")
        assert result.fig is not None

    def test_uniform(self):
        data = np.random.uniform(0, 1, 100)
        result = sp.plot_qq(data, distribution="uniform")
        assert result.fig is not None

    def test_t(self):
        data = np.random.standard_t(10, 100)
        result = sp.plot_qq(data, distribution="t")
        assert result.fig is not None

    def test_unknown_distribution(self):
        data = np.random.normal(0, 1, 100)
        with pytest.raises(ValueError):
            sp.plot_qq(data, distribution="unknown")

    def test_too_few_points(self):
        with pytest.raises(ValueError):
            sp.plot_qq(np.array([1.0, 2.0]), distribution="norm")

    def test_show_line_false(self):
        data = np.random.normal(0, 1, 100)
        result = sp.plot_qq(data, show_line=False)
        assert result.fig is not None

    def test_filters_nan(self):
        data = np.array([1, 2, np.nan, 4, 5, 6, 7, 8, 9, 10], dtype=float)
        result = sp.plot_qq(data)
        assert result.fig is not None


@pytestmark_scipy
class TestPlotBlandAltman:
    def test_basic(self):
        np.random.seed(42)
        y1 = np.random.normal(10, 2, 50)
        y2 = y1 + np.random.normal(0, 0.5, 50)
        result = sp.plot_bland_altman(y1, y2)
        assert isinstance(result, sp.PlotResult)

    def test_without_ci(self):
        np.random.seed(42)
        y1 = np.random.normal(10, 2, 50)
        y2 = y1 + np.random.normal(0, 0.5, 50)
        result = sp.plot_bland_altman(y1, y2, show_ci=False)
        assert result.fig is not None

    def test_custom_ci(self):
        np.random.seed(42)
        y1 = np.random.normal(10, 2, 50)
        y2 = y1 + np.random.normal(0, 0.5, 50)
        result = sp.plot_bland_altman(y1, y2, ci=0.99)
        assert result.fig is not None

    def test_length_mismatch(self):
        with pytest.raises(ValueError):
            sp.plot_bland_altman(np.array([1, 2, 3]), np.array([1, 2]))

    def test_custom_labels(self):
        y1 = np.array([1, 2, 3, 4, 5], dtype=float)
        y2 = np.array([1.1, 2.1, 2.9, 4.0, 5.1], dtype=float)
        result = sp.plot_bland_altman(y1, y2, xlabel="Mean", ylabel="Diff", title="BA Plot")
        assert result.ax.get_xlabel() == "Mean"


@pytestmark_scipy
class TestPlotDensity:
    def test_basic(self):
        data = np.random.normal(0, 1, 100)
        result = sp.plot_density(data)
        assert isinstance(result, sp.PlotResult)

    def test_with_fill(self):
        data = np.random.normal(0, 1, 100)
        result = sp.plot_density(data, fill=True, alpha=0.5)
        assert result.fig is not None

    def test_without_fill(self):
        data = np.random.normal(0, 1, 100)
        result = sp.plot_density(data, fill=False)
        assert result.fig is not None

    def test_too_few_points(self):
        with pytest.raises(ValueError):
            sp.plot_density(np.array([1.0]))

    def test_filters_nan(self):
        data = np.array([1, 2, 3, np.nan, 5, 6, 7, 8, 9, 10], dtype=float)
        result = sp.plot_density(data)
        assert result.fig is not None


@pytestmark_scipy
class TestPlotMultiDensity:
    def test_basic(self):
        data1 = np.random.normal(0, 1, 100)
        data2 = np.random.normal(2, 1.5, 100)
        result = sp.plot_multi_density([data1, data2], labels=["A", "B"])
        assert isinstance(result, sp.PlotResult)

    def test_with_fill(self):
        data1 = np.random.normal(0, 1, 100)
        data2 = np.random.normal(2, 1, 100)
        result = sp.plot_multi_density([data1, data2], fill=True, alpha=0.3)
        assert result.fig is not None

    def test_empty_list(self):
        with pytest.raises(ValueError):
            sp.plot_multi_density([])

    def test_too_few_points(self):
        with pytest.raises(ValueError):
            sp.plot_multi_density([np.array([1.0])])

    def test_label_length_mismatch(self):
        data = np.random.normal(0, 1, 100)
        with pytest.raises(ValueError):
            sp.plot_multi_density([data], labels=["A", "B"])

    def test_auto_labels(self):
        data1 = np.random.normal(0, 1, 100)
        data2 = np.random.normal(2, 1, 100)
        result = sp.plot_multi_density([data1, data2])
        legend = result.ax.get_legend()
        assert legend is not None
