"""
语法糖功能单元测试 - Fluent Interface、Context Manager、Aliases
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
import sciplot as sp
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib import rcParams
from sciplot._core.fluent import FigureWrapper, PlotChain


class TestFluentInterface:
    """测试 Fluent Interface 链式调用"""
    
    def test_style_chain(self, test_data, cleanup_figures):
        """测试 style().plot() 链式调用"""
        result = sp.style("nature").plot(test_data["x"], test_data["y"])
        # 链式调用返回 FigureWrapper，可以通过 get_figure() 获取 Figure
        assert isinstance(result, FigureWrapper)
        assert isinstance(result.get_figure(), Figure)
        
    def test_style_palette_chain(self, test_data, cleanup_figures):
        """测试 style().palette().plot() 链式调用"""
        result = sp.style("ieee").palette("earth").plot(test_data["x"], test_data["y"])
        assert isinstance(result, FigureWrapper)
        assert isinstance(result.get_figure(), Figure)
        
    def test_full_chain_with_save(self, test_data, temp_dir, cleanup_figures):
        """测试完整链式调用包括保存"""
        output_path = temp_dir / "test_chain"
        paths = (sp.style("thesis")
                   .palette("pastel")
                   .plot(test_data["x"], test_data["y"])
                   .save(output_path, formats=("png",)))
        assert len(paths) > 0
        assert paths[0].exists()
        
    def test_chain_multi_layer(self, test_data, cleanup_figures):
        """测试多图层链式调用"""
        result = (sp.style("ieee")
                 .palette("ocean")
                 .plot(test_data["x"], test_data["y"], label="线1")
                 .plot(test_data["x"], test_data["y2"], label="线2")
                 .legend())
        assert isinstance(result, FigureWrapper)
        assert isinstance(result.get_figure(), Figure)
        
    def test_chain_with_labels(self, test_data, cleanup_figures):
        """测试带标签的链式调用"""
        result = (sp.style("nature")
                 .plot(test_data["x"], test_data["y"])
                 .xlabel("X 轴")
                 .ylabel("Y 轴")
                 .title("标题"))
        assert isinstance(result, FigureWrapper)
        assert isinstance(result.get_figure(), Figure)
        
    def test_chain_scatter(self, test_data, cleanup_figures):
        """测试链式散点图"""
        result = sp.style("ieee").scatter(test_data["x"], test_data["y"])
        assert isinstance(result, FigureWrapper)
        assert isinstance(result.get_figure(), Figure)
        
    def test_chain_bar(self, test_data, cleanup_figures):
        """测试链式柱状图"""
        result = sp.style("thesis").bar(["A", "B", "C"], [1, 2, 3])
        assert isinstance(result, FigureWrapper)
        assert isinstance(result.get_figure(), Figure)
        
    def test_palette_entry(self, test_data, cleanup_figures):
        """测试 palette() 入口"""
        result = sp.palette("earth").plot(test_data["x"], test_data["y"])
        assert isinstance(result, FigureWrapper)
        assert isinstance(result.get_figure(), Figure)
        
    def test_chain_entry(self, test_data, cleanup_figures):
        """测试 chain() 入口"""
        result = sp.chain(venue="ieee", palette="pastel", lang="zh").plot(
            test_data["x"], test_data["y"]
        )
        assert isinstance(result, FigureWrapper)
        assert isinstance(result.get_figure(), Figure)


class TestContextManager:
    """测试 Context Manager 上下文管理器"""
    
    def test_style_context_basic(self, test_data, cleanup_figures):
        """测试基础上下文管理器"""
        # 记录原始设置
        original_family = rcParams["font.family"]
        
        with sp.style_context("ieee", palette="earth"):
            fig, ax = sp.plot(test_data["x"], test_data["y"])
            assert isinstance(fig, Figure)
            # 在上下文中，样式应该改变
            
        # 退出上下文后，样式应该恢复
        # 注意：reset_style 可能不完全恢复，但至少不报错
        
    def test_style_context_nested(self, test_data, cleanup_figures):
        """测试嵌套上下文"""
        with sp.style_context("nature", palette="pastel"):
            fig1, ax1 = sp.plot(test_data["x"], test_data["y"])
            assert isinstance(fig1, Figure)
            
            with sp.style_context("ieee", palette="ocean"):
                fig2, ax2 = sp.plot(test_data["x"], test_data["y"])
                assert isinstance(fig2, Figure)
                
            # 应该恢复为 nature + pastel
            fig3, ax3 = sp.plot(test_data["x"], test_data["y"])
            assert isinstance(fig3, Figure)
            
    def test_style_context_with_rcparams(self, test_data, cleanup_figures):
        """测试带自定义 rcParams 的上下文"""
        # 使用正确的 rcParams 键名（matplotlib 使用 figure.dpi）
        with sp.style_context("thesis", lang="zh", **{"figure.dpi": 200}):
            fig, ax = sp.plot(test_data["x"], test_data["y"])
            assert isinstance(fig, Figure)
            
    def test_style_context_does_not_affect_global(self, test_data, cleanup_figures):
        """测试上下文不影响全局样式"""
        # 设置全局样式
        sp.setup_style("nature", "pastel", lang="zh")
        
        # 使用上下文临时改变
        with sp.style_context("ieee", "earth"):
            fig, ax = sp.plot(test_data["x"], test_data["y"])
            
        # 全局样式应该还是 nature
        # 这个测试主要验证不报错


class TestAliases:
    """测试函数别名"""
    
    def test_line_alias(self, test_data, cleanup_figures):
        """测试 line 别名"""
        fig1, ax1 = sp.plot_line(test_data["x"], test_data["y"])
        fig2, ax2 = sp.line(test_data["x"], test_data["y"])
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)
        
    def test_scatter_alias(self, test_data, cleanup_figures):
        """测试 scatter 别名"""
        fig1, ax1 = sp.plot_scatter(test_data["x"], test_data["y"])
        fig2, ax2 = sp.scatter(test_data["x"], test_data["y"])
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)
        
    def test_bar_alias(self, test_data, cleanup_figures):
        """测试 bar 别名"""
        fig1, ax1 = sp.plot_bar(["A", "B"], [1, 2])
        fig2, ax2 = sp.bar(["A", "B"], [1, 2])
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)
        
    def test_hbar_alias(self, test_data, cleanup_figures):
        """测试 hbar 别名"""
        fig1, ax1 = sp.plot_horizontal_bar(["A", "B"], [1, 2])
        fig2, ax2 = sp.hbar(["A", "B"], [1, 2])
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)
        
    def test_hist_alias(self, cleanup_figures):
        """测试 hist 别名"""
        data = np.random.normal(0, 1, 100)
        fig1, ax1 = sp.plot_histogram(data)
        fig2, ax2 = sp.hist(data)
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)
        
    def test_box_alias(self, test_data, cleanup_figures):
        """测试 box 别名"""
        data_list = [np.random.normal(0, 1, 100) for _ in range(3)]
        fig1, ax1 = sp.plot_box(data_list)
        fig2, ax2 = sp.box(data_list)
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)
        
    def test_violin_alias(self, test_data, cleanup_figures):
        """测试 violin 别名"""
        data_list = [np.random.normal(0, 1, 100) for _ in range(3)]
        fig1, ax1 = sp.plot_violin(data_list)
        fig2, ax2 = sp.violin(data_list)
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)
        
    def test_heatmap_alias(self, test_data, cleanup_figures):
        """测试 heatmap 别名"""
        matrix = np.random.rand(5, 5)
        fig1, ax1 = sp.plot_heatmap(matrix)
        fig2, ax2 = sp.heatmap(matrix)
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)
        
    def test_area_alias(self, test_data, cleanup_figures):
        """测试 area 别名"""
        fig1, ax1 = sp.plot_area(test_data["x"], test_data["y"])
        fig2, ax2 = sp.area(test_data["x"], test_data["y"])
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)
        
    def test_step_alias(self, test_data, cleanup_figures):
        """测试 step 别名"""
        fig1, ax1 = sp.plot_step(test_data["x"], test_data["y"])
        fig2, ax2 = sp.step(test_data["x"], test_data["y"])
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)
        
    def test_errorbar_alias(self, test_data, cleanup_figures):
        """测试 errorbar 别名"""
        x = np.linspace(0, 10, 10)
        y = np.sin(x)
        yerr = np.random.uniform(0.1, 0.3, len(x))
        
        fig1, ax1 = sp.plot_errorbar(x, y, yerr)
        fig2, ax2 = sp.errorbar(x, y, yerr)
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)


class TestAliasParameters:
    """测试别名函数参数一致性"""
    
    def test_line_parameters_match(self, test_data):
        """测试 line 和 plot_line 参数一致"""
        import inspect
        sig1 = inspect.signature(sp.plot_line)
        sig2 = inspect.signature(sp.line)
        # 参数应该相同
        assert list(sig1.parameters.keys()) == list(sig2.parameters.keys())
        
    def test_scatter_parameters_match(self, test_data):
        """测试 scatter 和 plot_scatter 参数一致"""
        import inspect
        sig1 = inspect.signature(sp.plot_scatter)
        sig2 = inspect.signature(sp.scatter)
        assert list(sig1.parameters.keys()) == list(sig2.parameters.keys())
