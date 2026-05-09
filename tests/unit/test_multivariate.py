"""多维图表测试 — plot_parallel, plot_scatter_matrix"""
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


@pytest.fixture
def multivariate_data():
    np.random.seed(42)
    return np.random.randn(50, 5)


@pytest.fixture
def labeled_data():
    np.random.seed(42)
    data = np.random.randn(30, 4)
    columns = ["Feature A", "Feature B", "Feature C", "Feature D"]
    return data, columns


class TestPlotParallel:
    def test_basic(self, multivariate_data):
        result = sp.plot_parallel(multivariate_data)
        assert isinstance(result, sp.PlotResult)
        assert result.fig is not None

    def test_with_columns(self, labeled_data):
        data, columns = labeled_data
        result = sp.plot_parallel(data, columns=columns)
        assert result.fig is not None

    def test_normalize_minmax(self, multivariate_data):
        result = sp.plot_parallel(multivariate_data, normalize="minmax")
        assert result.fig is not None

    def test_normalize_zscore(self, multivariate_data):
        result = sp.plot_parallel(multivariate_data, normalize="zscore")
        assert result.fig is not None

    def test_normalize_none(self, multivariate_data):
        result = sp.plot_parallel(multivariate_data, normalize="none")
        assert result.fig is not None

    def test_normalize_invalid(self, multivariate_data):
        with pytest.raises(ValueError):
            sp.plot_parallel(multivariate_data, normalize="invalid")

    def test_color_by_int(self, labeled_data):
        data, columns = labeled_data
        result = sp.plot_parallel(data, columns=columns, color_by=0)
        assert result.fig is not None

    def test_color_by_str(self, labeled_data):
        data, columns = labeled_data
        result = sp.plot_parallel(data, columns=columns, color_by="Feature A")
        assert result.fig is not None

    def test_color_by_str_not_in_columns(self, labeled_data):
        data, columns = labeled_data
        with pytest.raises(ValueError):
            sp.plot_parallel(data, columns=columns, color_by="Nonexistent")

    def test_color_by_out_of_range(self, labeled_data):
        data, columns = labeled_data
        with pytest.raises(ValueError):
            sp.plot_parallel(data, columns=columns, color_by=100)

    def test_color_by_negative_index(self, labeled_data):
        data, columns = labeled_data
        result = sp.plot_parallel(data, columns=columns, color_by=-1)
        assert result.fig is not None

    def test_1d_data_raises(self):
        with pytest.raises(ValueError):
            sp.plot_parallel(np.array([1, 2, 3]))

    def test_non_numeric_data_raises(self):
        with pytest.raises(ValueError):
            sp.plot_parallel(np.array([["a", "b"], ["c", "d"]]))

    def test_columns_length_mismatch(self, multivariate_data):
        with pytest.raises(ValueError):
            sp.plot_parallel(multivariate_data, columns=["A", "B"])

    def test_with_labels(self, labeled_data):
        data, columns = labeled_data
        labels = [f"Sample {i}" for i in range(len(data))]
        result = sp.plot_parallel(data, columns=columns, labels=labels)
        assert result.fig is not None

    def test_dataframe_like(self, labeled_data):
        """Test with object that has .iloc and .columns (simulated DataFrame)"""
        data, columns = labeled_data

        class FakeDF:
            def __init__(self, data, columns):
                self._data = data
                self.columns = columns
                self.index = range(len(data))

            @property
            def iloc(self):
                return self

            @property
            def values(self):
                return self._data

        df = FakeDF(data, columns)
        result = sp.plot_parallel(df)
        assert result.fig is not None

    def test_show_colorbar_false(self, labeled_data):
        data, columns = labeled_data
        result = sp.plot_parallel(data, columns=columns, color_by=0, show_colorbar=False)
        assert result.fig is not None


class TestPlotScatterMatrix:
    def test_basic(self, multivariate_data):
        result = sp.plot_scatter_matrix(multivariate_data)
        assert isinstance(result, sp.PlotResult)
        assert result.fig is not None

    def test_with_columns(self, labeled_data):
        data, columns = labeled_data
        result = sp.plot_scatter_matrix(data, columns=columns)
        assert result.fig is not None

    def test_diag_hist(self, multivariate_data):
        result = sp.plot_scatter_matrix(multivariate_data, diag="hist")
        assert result.fig is not None

    def test_diag_none(self, multivariate_data):
        result = sp.plot_scatter_matrix(multivariate_data, diag="none")
        assert result.fig is not None

    def test_diag_invalid(self, multivariate_data):
        with pytest.raises(ValueError):
            sp.plot_scatter_matrix(multivariate_data, diag="invalid")

    def test_1d_data_raises(self):
        with pytest.raises(ValueError):
            sp.plot_scatter_matrix(np.array([1, 2, 3]))

    def test_single_feature_raises(self):
        with pytest.raises(ValueError):
            sp.plot_scatter_matrix(np.array([[1], [2], [3]]))

    def test_columns_length_mismatch(self, multivariate_data):
        with pytest.raises(ValueError):
            sp.plot_scatter_matrix(multivariate_data, columns=["A"])

    def test_color_by_array(self, multivariate_data):
        color_values = np.array([0] * 25 + [1] * 25)
        result = sp.plot_scatter_matrix(multivariate_data, color_by=color_values)
        assert result.fig is not None

    def test_color_by_length_mismatch(self, multivariate_data):
        color_values = np.array([0] * 10)
        with pytest.raises(ValueError):
            sp.plot_scatter_matrix(multivariate_data, color_by=color_values)

    def test_custom_alpha_s(self, multivariate_data):
        result = sp.plot_scatter_matrix(multivariate_data, alpha=0.3, s=20)
        assert result.fig is not None
