"""
分布图表单元测试 - 箱线图、小提琴图、直方图、热力图
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
import sciplot as sp
from matplotlib.figure import Figure
from matplotlib.axes import Axes


class TestBoxPlot:
    """测试箱线图"""
    
    def test_box_basic(self, test_data, cleanup_figures):
        """测试基础箱线图"""
        fig, ax = sp.plot_box(
            test_data["data_list"],
            labels=["A", "B", "C"]
        )
        assert isinstance(fig, Figure)
        # 检查有箱线图元素
        assert len(ax.patches) > 0 or len(ax.lines) > 0
        
    def test_box_with_outliers(self, test_data, cleanup_figures):
        """测试带异常值的箱线图"""
        fig, ax = sp.plot_box(
            test_data["data_list"],
            labels=["A", "B", "C"],
            showfliers=True
        )
        assert isinstance(fig, Figure)
        
    def test_box_alias(self, test_data, cleanup_figures):
        """测试 box 别名"""
        fig1, ax1 = sp.plot_box(test_data["data_list"])
        fig2, ax2 = sp.box(test_data["data_list"])
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)


class TestViolinPlot:
    """测试小提琴图"""
    
    def test_violin_basic(self, test_data, cleanup_figures):
        """测试基础小提琴图"""
        fig, ax = sp.plot_violin(
            test_data["data_list"],
            labels=["A", "B", "C"]
        )
        assert isinstance(fig, Figure)
        # 检查有小提琴图元素
        assert len(ax.collections) > 0
        
    def test_violin_with_medians(self, test_data, cleanup_figures):
        """测试显示中位数的小提琴图"""
        fig, ax = sp.plot_violin(
            test_data["data_list"],
            labels=["A", "B", "C"],
            showmedians=True
        )
        assert isinstance(fig, Figure)
        
    def test_violin_alias(self, test_data, cleanup_figures):
        """测试 violin 别名"""
        fig1, ax1 = sp.plot_violin(test_data["data_list"])
        fig2, ax2 = sp.violin(test_data["data_list"])
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)


class TestHistogram:
    """测试直方图"""
    
    def test_hist_basic(self, test_data, cleanup_figures):
        """测试基础直方图"""
        data = np.random.normal(0, 1, 1000)
        fig, ax = sp.plot_histogram(data, bins=30)
        assert isinstance(fig, Figure)
        # 检查有直方图元素
        assert len(ax.patches) > 0
        
    def test_hist_density(self, test_data, cleanup_figures):
        """测试密度直方图"""
        data = np.random.normal(0, 1, 1000)
        fig, ax = sp.plot_histogram(data, bins=30, density=True)
        assert isinstance(fig, Figure)
        
    def test_hist_alias(self, test_data, cleanup_figures):
        """测试 hist 别名"""
        data = np.random.normal(0, 1, 100)
        fig1, ax1 = sp.plot_histogram(data)
        fig2, ax2 = sp.hist(data)
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)


class TestHeatmap:
    """测试热力图"""
    
    def test_heatmap_basic(self, test_data, cleanup_figures):
        """测试基础热力图"""
        fig, ax = sp.plot_heatmap(test_data["matrix"], cmap="Blues")
        assert isinstance(fig, Figure)
        # 检查有热力图元素
        assert len(ax.images) > 0 or len(ax.collections) > 0
        
    def test_heatmap_with_values(self, test_data, cleanup_figures):
        """测试显示数值的热力图"""
        fig, ax = sp.plot_heatmap(
            test_data["matrix"],
            cmap="Blues",
            show_values=True
        )
        assert isinstance(fig, Figure)
        # 检查有文本标注
        texts = [child for child in ax.get_children() 
                 if hasattr(child, 'get_text') and child.get_text()]
        assert len(texts) > 0
        
    def test_heatmap_alias(self, test_data, cleanup_figures):
        """测试 heatmap 别名"""
        fig1, ax1 = sp.plot_heatmap(test_data["matrix"])
        fig2, ax2 = sp.heatmap(test_data["matrix"])
        assert isinstance(fig1, Figure)
        assert isinstance(fig2, Figure)


class TestSignificanceAnnotation:
    """测试显著性标注"""
    
    def test_significance_star(self, test_data, cleanup_figures):
        """测试单星显著性标注"""
        fig, ax = sp.plot_box(test_data["data_list"])
        sp.annotate_significance(ax, x1=1, x2=2, y=2.5, p_value=0.03)
        # 检查有标注线
        lines = [line for line in ax.lines if line.get_visible()]
        assert len(lines) > 0
        
    def test_significance_triple_star(self, test_data, cleanup_figures):
        """测试三星显著性标注"""
        fig, ax = sp.plot_box(test_data["data_list"])
        sp.annotate_significance(ax, x1=1, x2=3, y=3.0, p_value=0.0005)
        # 检查有标注线
        lines = [line for line in ax.lines if line.get_visible()]
        assert len(lines) > 0
        
    def test_significance_ns(self, test_data, cleanup_figures):
        """测试不显著标注"""
        fig, ax = sp.plot_box(test_data["data_list"])
        sp.annotate_significance(ax, x1=1, x2=2, y=2.5, p_value=0.5)
        # 应该显示 "ns"
        texts = [child for child in ax.get_children() 
                 if hasattr(child, 'get_text')]
        assert len(texts) > 0
