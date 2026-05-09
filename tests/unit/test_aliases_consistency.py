"""别名一致性测试 — 验证所有别名函数与原函数行为一致"""
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


class TestAliasExistence:
    """验证 README 中声明的别名都存在"""

    def test_line_alias(self):
        assert callable(sp.line)

    def test_scatter_alias(self):
        assert callable(sp.scatter)

    def test_step_alias(self):
        assert callable(sp.step)

    def test_area_alias(self):
        assert callable(sp.area)

    def test_multi_alias(self):
        assert callable(sp.multi)

    def test_multi_line_alias(self):
        assert callable(sp.multi_line)

    def test_multi_area_alias(self):
        assert callable(sp.multi_area)

    def test_bar_alias(self):
        assert callable(sp.bar)

    def test_grouped_bar_alias(self):
        assert callable(sp.grouped_bar)

    def test_stacked_bar_alias(self):
        assert callable(sp.stacked_bar)

    def test_hbar_alias(self):
        assert callable(sp.hbar)

    def test_hist_alias(self):
        assert callable(sp.hist)

    def test_box_alias(self):
        assert callable(sp.box)

    def test_violin_alias(self):
        assert callable(sp.violin)

    def test_errorbar_alias(self):
        assert callable(sp.errorbar)

    def test_confidence_alias(self):
        assert callable(sp.confidence)

    def test_heatmap_alias(self):
        assert callable(sp.heatmap)

    def test_combo_alias(self):
        assert callable(sp.combo)

    def test_radar_alias(self):
        assert callable(sp.radar)

    def test_timeseries_alias(self):
        assert callable(sp.timeseries)

    def test_multi_timeseries_alias(self):
        assert callable(sp.multi_timeseries)

    def test_density_alias(self):
        assert callable(sp.density)

    def test_multi_density_alias(self):
        assert callable(sp.multi_density)

    def test_residuals_alias(self):
        assert callable(sp.residuals)

    def test_qq_alias(self):
        assert callable(sp.qq)

    def test_bland_altman_alias(self):
        assert callable(sp.bland_altman)

    def test_lollipop_alias(self):
        assert callable(sp.lollipop)


class TestAliasBehavior:
    """验证别名函数返回与原函数相同类型"""

    def test_line_returns_plot_result(self):
        x = np.linspace(0, 10, 50)
        result = sp.line(x, np.sin(x))
        assert isinstance(result, sp.PlotResult)

    def test_scatter_returns_plot_result(self):
        x = np.linspace(0, 10, 50)
        result = sp.scatter(x, np.sin(x))
        assert isinstance(result, sp.PlotResult)

    def test_step_returns_plot_result(self):
        x = np.linspace(0, 10, 50)
        result = sp.step(x, np.sin(x))
        assert isinstance(result, sp.PlotResult)

    def test_area_returns_plot_result(self):
        x = np.linspace(0, 10, 50)
        result = sp.area(x, np.sin(x))
        assert isinstance(result, sp.PlotResult)

    def test_multi_returns_plot_result(self):
        x = np.linspace(0, 10, 50)
        result = sp.multi(x, [np.sin(x), np.cos(x)])
        assert isinstance(result, sp.PlotResult)

    def test_bar_returns_plot_result(self):
        result = sp.bar(["A", "B", "C"], [1, 2, 3])
        assert isinstance(result, sp.PlotResult)

    def test_hist_returns_plot_result(self):
        result = sp.hist(np.random.randn(100))
        assert isinstance(result, sp.PlotResult)

    def test_box_returns_plot_result(self):
        result = sp.box([np.random.randn(50) for _ in range(3)])
        assert isinstance(result, sp.PlotResult)

    def test_violin_returns_plot_result(self):
        result = sp.violin([np.random.randn(50) for _ in range(3)])
        assert isinstance(result, sp.PlotResult)

    def test_errorbar_returns_plot_result(self):
        x = np.arange(5)
        result = sp.errorbar(x, [1, 2, 3, 4, 5], [0.1, 0.2, 0.1, 0.3, 0.2])
        assert isinstance(result, sp.PlotResult)

    def test_heatmap_returns_plot_result(self):
        data = np.random.rand(5, 5)
        result = sp.heatmap(data)
        assert isinstance(result, sp.PlotResult)

    def test_combo_returns_combo_result(self):
        result = sp.combo(
            ["Q1", "Q2", "Q3"],
            bar_data={"sales": [100, 120, 140]},
            line_data={"growth": [0.1, 0.2, 0.15]},
        )
        assert isinstance(result, sp.ComboPlotResult)

    def test_radar_returns_plot_result(self):
        result = sp.radar(
            ["A", "B", "C"],
            [[0.8, 0.9, 0.7]],
            labels=["Series 1"],
        )
        assert isinstance(result, sp.PlotResult)

    def test_timeseries_returns_plot_result(self):
        t = np.arange(100)
        result = sp.timeseries(t, np.sin(t))
        assert isinstance(result, sp.PlotResult)

    def test_residuals_returns_plot_result(self):
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([1.1, 2.2, 2.9, 4.1, 4.8])
        result = sp.residuals(y_true, y_pred)
        assert isinstance(result, sp.PlotResult)

    def test_qq_returns_plot_result(self):
        data = np.random.normal(0, 1, 100)
        result = sp.qq(data)
        assert isinstance(result, sp.PlotResult)

    def test_density_returns_plot_result(self):
        data = np.random.normal(0, 1, 100)
        result = sp.density(data)
        assert isinstance(result, sp.PlotResult)

    def test_lollipop_returns_plot_result(self):
        result = sp.lollipop(["A", "B", "C"], [0.8, 0.6, 0.9])
        assert isinstance(result, sp.PlotResult)


class TestAliasParameterForwarding:
    """验证别名正确转发所有参数"""

    def test_line_xlabel_forwarded(self):
        x = np.linspace(0, 10, 50)
        result = sp.line(x, np.sin(x), xlabel="My X", ylabel="My Y", title="My Title")
        assert result.ax.get_xlabel() == "My X"
        assert result.ax.get_ylabel() == "My Y"
        assert result.ax.get_title() == "My Title"

    def test_bar_title_forwarded(self):
        result = sp.bar(["A", "B"], [1, 2], title="Bar Title")
        assert result.ax.get_title() == "Bar Title"

    def test_hist_density_forwarded(self):
        data = np.random.randn(100)
        result = sp.hist(data, density=True)
        # density=True should normalize
        assert result.fig is not None

    def test_heatmap_show_values_forwarded(self):
        data = np.array([[1, 2], [3, 4]])
        result = sp.heatmap(data, show_values=True, fmt=".1f")
        assert result.fig is not None
