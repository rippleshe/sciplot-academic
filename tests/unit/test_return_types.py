"""
函数返回值类型测试 - 验证所有函数的返回类型一致性
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
import sciplot as sp
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.collections import PathCollection, PolyCollection
from typing import Tuple, List, Dict, Any
import pathlib
from sciplot._core.result import PlotResult


class TestCoreFunctionsReturnTypes:
    """测试核心函数返回类型"""
    
    def test_setup_style_returns_none(self, reset_style):
        """setup_style 应该返回 None"""
        result = sp.setup_style()
        assert result is None
        
    def test_new_figure_returns_tuple(self, reset_style, cleanup_figures):
        """new_figure 应该返回 (Figure, Axes) 元组"""
        result = sp.new_figure("nature")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], Figure)
        assert isinstance(result[1], Axes)
        
    def test_save_returns_list(self, temp_dir, reset_style, cleanup_figures):
        """save 应该返回 Path 列表"""
        fig, ax = sp.plot([1, 2], [1, 2])
        output_path = temp_dir / "test"
        result = sp.save(fig, output_path, formats=("png",))
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], pathlib.Path)
        
    def test_save_multiple_formats_returns_multiple_paths(self, temp_dir, reset_style, cleanup_figures):
        """save 多格式应该返回多个 Path"""
        fig, ax = sp.plot([1, 2], [1, 2])
        output_path = temp_dir / "test"
        result = sp.save(fig, output_path, formats=("png", "pdf"))
        
        assert isinstance(result, list)
        assert len(result) == 2
        for path in result:
            assert isinstance(path, pathlib.Path)


class TestBasicChartsReturnTypes:
    """测试基础图表函数返回类型"""
    
    def test_plot_returns_plotresult(self, test_data, reset_style, cleanup_figures):
        """plot 应该返回 PlotResult（支持元组解包）"""
        result = sp.plot(test_data["x"], test_data["y"])
        assert isinstance(result, PlotResult)
        fig, ax = result
        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)
        
    def test_plot_line_returns_plotresult(self, test_data, reset_style, cleanup_figures):
        """plot_line 应该返回 PlotResult"""
        result = sp.plot_line(test_data["x"], test_data["y"])
        assert isinstance(result, PlotResult)
        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)
        
    def test_plot_multi_returns_plotresult(self, test_data, reset_style, cleanup_figures):
        """plot_multi 应该返回 PlotResult"""
        result = sp.plot_multi(test_data["x"], [test_data["y"], test_data["y2"]])
        assert isinstance(result, PlotResult)
        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)
        
    def test_plot_scatter_returns_plotresult(self, test_data, reset_style, cleanup_figures):
        """plot_scatter 应该返回 PlotResult"""
        result = sp.plot_scatter(test_data["x"], test_data["y"])
        assert isinstance(result, PlotResult)
        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)
        
    def test_plot_bar_returns_plotresult(self, test_data, reset_style, cleanup_figures):
        """plot_bar 应该返回 PlotResult"""
        result = sp.plot_bar(test_data["categories"], test_data["values"])
        assert isinstance(result, PlotResult)
        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)
        
    def test_plot_grouped_bar_returns_plotresult(self, reset_style, cleanup_figures):
        """plot_grouped_bar 应该返回 PlotResult"""
        result = sp.plot_grouped_bar(
            ["A", "B"],
            {"组1": [1, 2], "组2": [3, 4]}
        )
        assert isinstance(result, PlotResult)
        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)
        
    def test_plot_stacked_bar_returns_plotresult(self, reset_style, cleanup_figures):
        """plot_stacked_bar 应该返回 PlotResult"""
        result = sp.plot_stacked_bar(
            ["A", "B"],
            {"组1": [1, 2], "组2": [3, 4]}
        )
        assert isinstance(result, PlotResult)
        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)
        
    def test_plot_horizontal_bar_returns_plotresult(self, test_data, reset_style, cleanup_figures):
        """plot_horizontal_bar 应该返回 PlotResult"""
        result = sp.plot_horizontal_bar(test_data["categories"], test_data["values"])
        assert isinstance(result, PlotResult)
        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)
        
    def test_plot_area_returns_plotresult(self, test_data, reset_style, cleanup_figures):
        """plot_area 应该返回 PlotResult"""
        result = sp.plot_area(test_data["x"], test_data["y"])
        assert isinstance(result, PlotResult)
        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)
        
    def test_plot_multi_area_returns_plotresult(self, test_data, reset_style, cleanup_figures):
        """plot_multi_area 应该返回 PlotResult"""
        result = sp.plot_multi_area(test_data["x"], [test_data["y"], test_data["y2"]])
        assert isinstance(result, PlotResult)
        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)
        
    def test_plot_step_returns_plotresult(self, test_data, reset_style, cleanup_figures):
        """plot_step 应该返回 PlotResult"""
        result = sp.plot_step(test_data["x"], test_data["y"])
        assert isinstance(result, PlotResult)
        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)
        
    def test_plot_errorbar_returns_plotresult(self, reset_style, cleanup_figures):
        """plot_errorbar 应该返回 PlotResult"""
        x = np.linspace(0, 10, 10)
        y = np.sin(x)
        yerr = np.random.uniform(0.1, 0.3, len(x))
        result = sp.plot_errorbar(x, y, yerr)
        assert isinstance(result, PlotResult)
        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)
        
    def test_plot_confidence_returns_plotresult(self, reset_style, cleanup_figures):
        """plot_confidence 应该返回 PlotResult"""
        x = np.linspace(0, 10, 50)
        mean = np.sin(x)
        std = np.random.uniform(0.1, 0.3, len(x))
        result = sp.plot_confidence(x, mean, std)
        assert isinstance(result, PlotResult)
        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)


class TestDistributionChartsReturnTypes:
    """测试分布图表函数返回类型"""
    
    def test_plot_box_returns_plotresult(self, test_data, reset_style, cleanup_figures):
        """plot_box 应该返回 PlotResult"""
        result = sp.plot_box(test_data["data_list"])
        assert isinstance(result, PlotResult)
        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)
        
    def test_plot_violin_returns_plotresult(self, test_data, reset_style, cleanup_figures):
        """plot_violin 应该返回 PlotResult"""
        result = sp.plot_violin(test_data["data_list"])
        assert isinstance(result, PlotResult)
        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)
        
    def test_plot_histogram_returns_plotresult(self, reset_style, cleanup_figures):
        """plot_histogram 应该返回 PlotResult"""
        data = np.random.normal(0, 1, 100)
        result = sp.plot_histogram(data)
        assert isinstance(result, PlotResult)
        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)
        
    def test_plot_heatmap_returns_plotresult(self, test_data, reset_style, cleanup_figures):
        """plot_heatmap 应该返回 PlotResult"""
        result = sp.plot_heatmap(test_data["matrix"])
        assert isinstance(result, PlotResult)
        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)


class TestLayoutFunctionsReturnTypes:
    """测试布局函数返回类型"""
    
    def test_create_subplots_returns_tuple(self, reset_style, cleanup_figures):
        """create_subplots 应该返回 (Figure, ndarray)"""
        result = sp.create_subplots(2, 2, venue="ieee")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], Figure)
        assert isinstance(result[1], np.ndarray)
        
    def test_paper_subplots_returns_tuple(self, reset_style, cleanup_figures):
        """paper_subplots 应该返回 (Figure, ndarray)"""
        result = sp.paper_subplots(1, 2, venue="thesis")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], Figure)
        assert isinstance(result[1], np.ndarray)
        
    def test_create_gridspec_returns_tuple(self, reset_style, cleanup_figures):
        """create_gridspec 应该返回 (Figure, GridSpec)"""
        result = sp.create_gridspec(2, 3, venue="nature")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], Figure)
        # GridSpec 类型检查
        from matplotlib.gridspec import GridSpec
        assert isinstance(result[1], GridSpec)


class TestUtilityFunctionsReturnTypes:
    """测试工具函数返回类型"""
    
    def test_list_venues_returns_list(self):
        """list_venues 应该返回字符串列表"""
        result = sp.list_venues()
        assert isinstance(result, list)
        assert all(isinstance(v, str) for v in result)
        
    def test_list_palettes_returns_list(self):
        """list_palettes 应该返回字符串列表"""
        result = sp.list_palettes()
        assert isinstance(result, list)
        assert all(isinstance(p, str) for p in result)
        
    def test_get_palette_returns_list(self):
        """get_palette 应该返回颜色字符串列表"""
        result = sp.get_palette("pastel")
        assert isinstance(result, list)
        assert all(isinstance(c, str) and c.startswith("#") for c in result)
        
    def test_get_venue_info_returns_dict(self):
        """get_venue_info 应该返回字典"""
        result = sp.get_venue_info("ieee")
        assert isinstance(result, dict)
        assert "name" in result
        assert "figsize" in result
        assert "fontsize" in result


class TestFluentInterfaceReturnTypes:
    """测试 Fluent Interface 返回类型"""
    
    def test_style_returns_plot_chain(self):
        """style() 应该返回 PlotChain"""
        from sciplot._core.fluent import PlotChain
        result = sp.style("nature")
        assert isinstance(result, PlotChain)
        
    def test_palette_returns_plot_chain(self):
        """palette() 应该返回 PlotChain"""
        from sciplot._core.fluent import PlotChain
        result = sp.palette("pastel")
        assert isinstance(result, PlotChain)
        
    def test_chain_returns_plot_chain(self):
        """chain() 应该返回 PlotChain"""
        from sciplot._core.fluent import PlotChain
        result = sp.chain(venue="ieee")
        assert isinstance(result, PlotChain)
        
    def test_plot_chain_methods_return_figure_wrapper(self, test_data):
        """PlotChain 绘图方法应该返回 FigureWrapper"""
        from sciplot._core.fluent import FigureWrapper
        chain = sp.style("nature")
        result = chain.plot(test_data["x"], test_data["y"])
        assert isinstance(result, FigureWrapper)
        
    def test_figure_wrapper_save_returns_list(self, test_data, temp_dir):
        """FigureWrapper.save() 应该返回 Path 列表"""
        wrapper = sp.style("nature").plot(test_data["x"], test_data["y"])
        output_path = temp_dir / "test"
        result = wrapper.save(output_path, formats=("png",))
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], pathlib.Path)


class TestReturnValueConsistency:
    """测试返回值一致性"""
    
    def test_all_plot_functions_return_plotresult(self, test_data, reset_style, cleanup_figures):
        """所有绘图函数应该返回 PlotResult"""
        functions = [
            lambda: sp.plot(test_data["x"], test_data["y"]),
            lambda: sp.plot_line(test_data["x"], test_data["y"]),
            lambda: sp.plot_scatter(test_data["x"], test_data["y"]),
            lambda: sp.plot_bar(test_data["categories"], test_data["values"]),
            lambda: sp.plot_area(test_data["x"], test_data["y"]),
            lambda: sp.plot_step(test_data["x"], test_data["y"]),
        ]
        
        for func in functions:
            result = func()
            assert isinstance(result, PlotResult), f"{func.__name__} 应该返回 PlotResult"
            assert isinstance(result.fig, Figure), f"{func.__name__} .fig 应该是 Figure"
            assert isinstance(result.ax, Axes), f"{func.__name__} .ax 应该是 Axes"
            # 验证元组解包
            fig, ax = result
            assert isinstance(fig, Figure)
            assert isinstance(ax, Axes)
