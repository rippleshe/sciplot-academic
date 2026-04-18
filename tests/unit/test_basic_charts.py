"""
基础图表单元测试 - 测试所有基础绘图函数
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
import sciplot as sp
from matplotlib.figure import Figure
from matplotlib.axes import Axes


class TestPlotLine:
    """测试折线图"""
    
    def test_plot_basic(self, test_data, cleanup_figures):
        """测试基础折线图"""
        fig, ax = sp.plot(test_data["x"], test_data["y"])
        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)
        
    def test_plot_with_labels(self, test_data, cleanup_figures):
        """测试带标签的折线图"""
        fig, ax = sp.plot(
            test_data["x"], 
            test_data["y"],
            xlabel="X 轴",
            ylabel="Y 轴",
            title="测试标题"
        )
        assert ax.get_xlabel() == "X 轴"
        assert ax.get_ylabel() == "Y 轴"
        assert ax.get_title() == "测试标题"
        
    def test_plot_line_alias(self, test_data, cleanup_figures):
        """测试 line 别名"""
        fig1, ax1 = sp.plot_line(test_data["x"], test_data["y"])
        fig2, ax2 = sp.line(test_data["x"], test_data["y"])
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)


class TestPlotMulti:
    """测试多线图"""
    
    def test_plot_multi_basic(self, test_data, cleanup_figures):
        """测试基础多线图"""
        fig, ax = sp.plot_multi(
            test_data["x"],
            [test_data["y"], test_data["y2"]],
            labels=["线1", "线2"]
        )
        assert isinstance(fig, Figure)
        # 检查图例
        assert ax.get_legend() is not None
        
    def test_plot_multi_auto_colors(self, test_data, cleanup_figures):
        """测试多线图自动配色"""
        x = test_data["x"]
        lines = [np.sin(x), np.cos(x), np.sin(x) + np.cos(x)]
        fig, ax = sp.plot_multi(x, lines)
        # 应该自动选择3色
        assert len(ax.lines) == 3


class TestScatter:
    """测试散点图"""
    
    def test_scatter_basic(self, test_data, cleanup_figures):
        """测试基础散点图"""
        fig, ax = sp.plot_scatter(
            test_data["x"],
            test_data["y"],
            s=30,
            alpha=0.7
        )
        assert isinstance(fig, Figure)
        # 检查是散点图（collections）而不是线图
        assert len(ax.collections) > 0
        
    def test_scatter_alias(self, test_data, cleanup_figures):
        """测试 scatter 别名"""
        fig1, ax1 = sp.plot_scatter(test_data["x"], test_data["y"])
        fig2, ax2 = sp.scatter(test_data["x"], test_data["y"])
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)


class TestBarCharts:
    """测试柱状图"""
    
    def test_bar_basic(self, test_data, cleanup_figures):
        """测试基础柱状图"""
        fig, ax = sp.plot_bar(
            test_data["categories"],
            test_data["values"]
        )
        assert isinstance(fig, Figure)
        # 检查有柱状图元素
        assert len(ax.patches) == len(test_data["categories"])
        
    def test_bar_alias(self, test_data, cleanup_figures):
        """测试 bar 别名"""
        fig1, ax1 = sp.plot_bar(test_data["categories"], test_data["values"])
        fig2, ax2 = sp.bar(test_data["categories"], test_data["values"])
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)
        
    def test_grouped_bar(self, test_data, cleanup_figures):
        """测试分组柱状图"""
        groups = ["组1", "组2", "组3"]
        data = {
            "A": [10, 20, 30],
            "B": [15, 25, 35],
            "C": [20, 30, 40]
        }
        fig, ax = sp.plot_grouped_bar(groups, data)
        assert isinstance(fig, Figure)
        
    def test_stacked_bar(self, test_data, cleanup_figures):
        """测试堆叠柱状图"""
        categories = ["Q1", "Q2", "Q3", "Q4"]
        data = {
            "产品A": [30, 40, 35, 50],
            "产品B": [20, 30, 25, 40],
        }
        fig, ax = sp.plot_stacked_bar(categories, data)
        assert isinstance(fig, Figure)
        
    def test_horizontal_bar(self, test_data, cleanup_figures):
        """测试水平柱状图"""
        fig, ax = sp.plot_horizontal_bar(
            test_data["categories"],
            test_data["values"],
            sort=True
        )
        assert isinstance(fig, Figure)
        
    def test_hbar_alias(self, test_data, cleanup_figures):
        """测试 hbar 别名"""
        fig1, ax1 = sp.plot_horizontal_bar(test_data["categories"], test_data["values"])
        fig2, ax2 = sp.hbar(test_data["categories"], test_data["values"])
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)


class TestAreaCharts:
    """测试面积图"""
    
    def test_area_basic(self, test_data, cleanup_figures):
        """测试基础面积图"""
        fig, ax = sp.plot_area(test_data["x"], test_data["y"], alpha=0.3)
        assert isinstance(fig, Figure)
        
    def test_area_alias(self, test_data, cleanup_figures):
        """测试 area 别名"""
        fig1, ax1 = sp.plot_area(test_data["x"], test_data["y"])
        fig2, ax2 = sp.area(test_data["x"], test_data["y"])
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)
        
    def test_multi_area(self, test_data, cleanup_figures):
        """测试多组面积图"""
        fig, ax = sp.plot_multi_area(
            test_data["x"],
            [test_data["y"], test_data["y2"]],
            stacked=False
        )
        assert isinstance(fig, Figure)
        
    def test_multi_area_stacked(self, test_data, cleanup_figures):
        """测试堆叠面积图"""
        fig, ax = sp.plot_multi_area(
            test_data["x"],
            [test_data["y"], test_data["y2"]],
            stacked=True
        )
        assert isinstance(fig, Figure)


class TestStepChart:
    """测试阶梯图"""
    
    def test_step_basic(self, test_data, cleanup_figures):
        """测试基础阶梯图"""
        fig, ax = sp.plot_step(test_data["x"], test_data["y"], where="mid")
        assert isinstance(fig, Figure)
        
    def test_step_alias(self, test_data, cleanup_figures):
        """测试 step 别名"""
        fig1, ax1 = sp.plot_step(test_data["x"], test_data["y"])
        fig2, ax2 = sp.step(test_data["x"], test_data["y"])
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)


class TestErrorBar:
    """测试误差条图"""
    
    def test_errorbar_basic(self, test_data, cleanup_figures):
        """测试基础误差条图"""
        x = np.linspace(0, 10, 10)
        y = np.sin(x)
        yerr = np.random.uniform(0.1, 0.3, len(x))
        
        fig, ax = sp.plot_errorbar(x, y, yerr, fmt="o", capsize=4)
        assert isinstance(fig, Figure)
        # 检查有误差条
        assert len(ax.lines) > 0 or len(ax.collections) > 0
        
    def test_errorbar_alias(self, test_data, cleanup_figures):
        """测试 errorbar 别名"""
        x = np.linspace(0, 10, 10)
        y = np.sin(x)
        yerr = np.random.uniform(0.1, 0.3, len(x))
        
        fig1, ax1 = sp.plot_errorbar(x, y, yerr)
        fig2, ax2 = sp.errorbar(x, y, yerr)
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)


class TestConfidenceInterval:
    """测试置信区间"""
    
    def test_confidence_basic(self, test_data, cleanup_figures):
        """测试基础置信区间"""
        x = np.linspace(0, 10, 50)
        mean = np.sin(x)
        std = np.random.uniform(0.1, 0.3, len(x))
        
        fig, ax = sp.plot_confidence(x, mean, std, alpha=0.25)
        assert isinstance(fig, Figure)


class TestComboChart:
    """测试组合图"""
    
    def test_combo_basic(self):
        """测试基础组合图（柱状+折线）"""
        x = ["Q1", "Q2", "Q3", "Q4"]
        bar_data = {"销售额": [100, 120, 140, 160]}
        line_data = {"增长率": [5, 8, 12, 15]}
        
        result = sp.plot_combo(x, bar_data, line_data)
        assert isinstance(result, sp.PlotResult)
        fig, axes = result
        assert isinstance(fig, Figure)
        ax_bar, ax_line = result.ax_array
        assert ax_line is not None


class TestEdgeCases:
    """测试边界情况"""
    
    def test_empty_data(self, cleanup_figures):
        """测试空数据 - 某些情况下可能不报错，只验证不崩溃"""
        try:
            fig, ax = sp.plot([], [])
            # 如果能运行到这里，说明实现允许空数据
            assert fig is not None
        except (ValueError, IndexError):
            # 如果报错也是合理的
            pass
            
    def test_mismatched_lengths(self):
        """测试长度不匹配的数据"""
        # matplotlib 可能会警告但不报错，我们验证行为合理即可
        try:
            fig, ax = sp.plot([1, 2, 3], [1, 2])
        except ValueError:
            pass  # 报错是预期的
            
    def test_single_point(self, cleanup_figures):
        """测试单点数据"""
        fig, ax = sp.plot([1], [1])
        assert isinstance(fig, Figure)
        
    def test_large_data(self, cleanup_figures):
        """测试大数据量"""
        x = np.linspace(0, 100, 10000)
        y = np.sin(x)
        fig, ax = sp.plot(x, y)
        assert isinstance(fig, Figure)
