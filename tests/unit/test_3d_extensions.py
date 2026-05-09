"""3D 扩展测试 — plot_surface, plot_contour, plot_3d_scatter, plot_wireframe"""
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
def grid_data():
    x = np.linspace(-5, 5, 20)
    y = np.linspace(-5, 5, 20)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(np.sqrt(X**2 + Y**2))
    return X, Y, Z


class TestPlotSurface:
    def test_basic(self, grid_data):
        X, Y, Z = grid_data
        result = sp.plot_surface(X, Y, Z)
        assert result.fig is not None
        assert result.ax is not None

    def test_with_labels(self, grid_data):
        X, Y, Z = grid_data
        result = sp.plot_surface(X, Y, Z, xlabel="X", ylabel="Y", zlabel="Z", title="Surface")
        assert result.fig is not None

    def test_custom_cmap(self, grid_data):
        X, Y, Z = grid_data
        result = sp.plot_surface(X, Y, Z, cmap="plasma")
        assert result.fig is not None

    def test_custom_view(self, grid_data):
        X, Y, Z = grid_data
        result = sp.plot_surface(X, Y, Z, elev=45, azim=90)
        assert result.fig is not None

    def test_shape_mismatch(self):
        X = np.ones((10, 10))
        Y = np.ones((10, 10))
        Z = np.ones((5, 5))
        with pytest.raises(ValueError):
            sp.plot_surface(X, Y, Z)

    def test_1d_array_raises(self):
        x = np.linspace(0, 1, 10)
        with pytest.raises(ValueError):
            sp.plot_surface(x, x, x)

    def test_returns_plot_result(self, grid_data):
        X, Y, Z = grid_data
        result = sp.plot_surface(X, Y, Z)
        assert isinstance(result, sp.PlotResult)
        fig, ax = result
        assert fig is result.fig


class TestPlotContour:
    def test_basic(self, grid_data):
        X, Y, Z = grid_data
        result = sp.plot_contour(X, Y, Z)
        assert result.fig is not None

    def test_filled(self, grid_data):
        X, Y, Z = grid_data
        result = sp.plot_contour(X, Y, Z, filled=True)
        assert result.fig is not None

    def test_show_labels(self, grid_data):
        X, Y, Z = grid_data
        result = sp.plot_contour(X, Y, Z, show_labels=True)
        assert result.fig is not None

    def test_hide_labels(self, grid_data):
        X, Y, Z = grid_data
        result = sp.plot_contour(X, Y, Z, show_labels=False)
        assert result.fig is not None

    def test_custom_levels_int(self, grid_data):
        X, Y, Z = grid_data
        result = sp.plot_contour(X, Y, Z, levels=20)
        assert result.fig is not None

    def test_custom_levels_list(self, grid_data):
        X, Y, Z = grid_data
        result = sp.plot_contour(X, Y, Z, levels=[-0.5, 0, 0.5])
        assert result.fig is not None

    def test_levels_zero_raises(self, grid_data):
        X, Y, Z = grid_data
        with pytest.raises(ValueError):
            sp.plot_contour(X, Y, Z, levels=0)

    def test_levels_empty_list_raises(self, grid_data):
        X, Y, Z = grid_data
        with pytest.raises(ValueError):
            sp.plot_contour(X, Y, Z, levels=[])

    def test_levels_nan_raises(self, grid_data):
        X, Y, Z = grid_data
        with pytest.raises(ValueError):
            sp.plot_contour(X, Y, Z, levels=[1, np.nan, 3])


class TestPlot3dScatter:
    def test_basic(self):
        np.random.seed(42)
        x, y, z = np.random.randn(3, 50)
        result = sp.plot_3d_scatter(x, y, z)
        assert result.fig is not None

    def test_with_color(self):
        np.random.seed(42)
        x, y, z = np.random.randn(3, 50)
        c = np.random.rand(50)
        result = sp.plot_3d_scatter(x, y, z, c=c, cmap="viridis")
        assert result.fig is not None

    def test_custom_size_scalar(self):
        x, y, z = np.random.randn(3, 20)
        result = sp.plot_3d_scatter(x, y, z, s=50)
        assert result.fig is not None

    def test_custom_size_array(self):
        x, y, z = np.random.randn(3, 20)
        s = np.random.rand(20) * 100
        result = sp.plot_3d_scatter(x, y, z, s=s)
        assert result.fig is not None

    def test_length_mismatch(self):
        x = np.array([1, 2, 3])
        y = np.array([1, 2])
        z = np.array([1, 2, 3])
        with pytest.raises(ValueError):
            sp.plot_3d_scatter(x, y, z)

    def test_color_array_length_mismatch(self):
        x, y, z = np.random.randn(3, 10)
        c = np.random.rand(5)
        with pytest.raises(ValueError):
            sp.plot_3d_scatter(x, y, z, c=c)

    def test_with_labels(self):
        x, y, z = np.random.randn(3, 20)
        result = sp.plot_3d_scatter(x, y, z, xlabel="X", ylabel="Y", zlabel="Z", title="3D Scatter")
        assert result.fig is not None


class TestPlotWireframe:
    def test_basic(self, grid_data):
        X, Y, Z = grid_data
        result = sp.plot_wireframe(X, Y, Z)
        assert result.fig is not None

    def test_custom_stride(self, grid_data):
        X, Y, Z = grid_data
        result = sp.plot_wireframe(X, Y, Z, rstride=2, cstride=2)
        assert result.fig is not None

    def test_invalid_rstride(self, grid_data):
        X, Y, Z = grid_data
        with pytest.raises(ValueError):
            sp.plot_wireframe(X, Y, Z, rstride=0)

    def test_invalid_cstride(self, grid_data):
        X, Y, Z = grid_data
        with pytest.raises(ValueError):
            sp.plot_wireframe(X, Y, Z, cstride=-1)

    def test_custom_color(self, grid_data):
        X, Y, Z = grid_data
        result = sp.plot_wireframe(X, Y, Z, color="#FF0000")
        assert result.fig is not None
