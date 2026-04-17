"""
布局系统单元测试 - 子图、GridSpec、面板标签
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
import sciplot as sp
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.gridspec as gridspec


class TestNewFigure:
    """测试创建图形"""
    
    def test_new_figure_nature(self, cleanup_figures):
        """测试 Nature 尺寸"""
        fig, ax = sp.new_figure("nature")
        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)
        assert fig.get_figwidth() == pytest.approx(7.0, abs=0.1)
        assert fig.get_figheight() == pytest.approx(5.0, abs=0.1)
        
    def test_new_figure_ieee(self, cleanup_figures):
        """测试 IEEE 尺寸"""
        fig, ax = sp.new_figure("ieee")
        assert fig.get_figwidth() == pytest.approx(3.5, abs=0.1)
        assert fig.get_figheight() == pytest.approx(3.0, abs=0.1)
        
    def test_new_figure_thesis(self, cleanup_figures):
        """测试 Thesis 尺寸"""
        fig, ax = sp.new_figure("thesis")
        assert fig.get_figwidth() == pytest.approx(6.1, abs=0.1)
        assert fig.get_figheight() == pytest.approx(4.3, abs=0.1)


class TestSubplots:
    """测试子图创建"""
    
    def test_create_subplots_2x2(self, cleanup_figures):
        """测试 2x2 子图"""
        fig, axes = sp.create_subplots(2, 2, venue="ieee")
        assert isinstance(fig, Figure)
        assert axes.shape == (2, 2)
        
    def test_create_subplots_1x3(self, cleanup_figures):
        """测试 1x3 子图"""
        fig, axes = sp.create_subplots(1, 3, venue="nature")
        assert isinstance(fig, Figure)
        # 1x3 子图可能返回一维数组
        assert axes.shape == (1, 3) or axes.shape == (3,)
        
    def test_create_subplots_sharex(self, cleanup_figures):
        """测试共享 X 轴"""
        fig, axes = sp.create_subplots(2, 2, venue="ieee", sharex=True)
        # 检查共享轴
        assert axes[0, 0].get_shared_x_axes().joined(axes[0, 0], axes[1, 0])


class TestPaperSubplots:
    """测试论文子图布局"""
    
    def test_paper_subplots_1x2(self, cleanup_figures):
        """测试 1x2 论文子图"""
        fig, axes = sp.paper_subplots(1, 2, venue="thesis")
        assert isinstance(fig, Figure)
        assert len(axes) == 2
        # 检查总宽度符合论文版心
        assert fig.get_figwidth() == pytest.approx(6.1, abs=0.1)
        
    def test_paper_subplots_2x2(self, cleanup_figures):
        """测试 2x2 论文子图"""
        fig, axes = sp.paper_subplots(2, 2, venue="nature")
        assert isinstance(fig, Figure)
        assert axes.shape == (2, 2)
        
    def test_paper_subplots_plotting(self, cleanup_figures):
        """测试在论文子图中绘图"""
        fig, axes = sp.paper_subplots(1, 2, venue="thesis")
        x = np.linspace(0, 10, 100)
        axes[0].plot(x, np.sin(x))
        axes[1].plot(x, np.cos(x))
        assert len(axes[0].lines) == 1
        assert len(axes[1].lines) == 1


class TestPanelLabels:
    """测试面板标签"""
    
    def test_add_panel_labels_default(self, cleanup_figures):
        """测试默认面板标签 (a) (b) (c)"""
        fig, axes = sp.paper_subplots(1, 3, venue="thesis")
        sp.add_panel_labels(axes)
        
        # 检查有文本标签
        texts = []
        for ax in axes:
            for child in ax.get_children():
                if hasattr(child, 'get_text') and child.get_text():
                    texts.append(child.get_text())
        
        # 应该包含 (a), (b), (c)
        assert any('(a)' in t for t in texts)
        assert any('(b)' in t for t in texts)
        assert any('(c)' in t for t in texts)
        
    def test_add_panel_labels_style_A(self, cleanup_figures):
        """测试大写字母面板标签 (A) (B) (C)"""
        fig, axes = sp.paper_subplots(1, 3, venue="thesis")
        # 使用正确的 style 参数
        sp.add_panel_labels(axes, style="LETTER")
        
        texts = []
        for ax in axes:
            for child in ax.get_children():
                if hasattr(child, 'get_text') and child.get_text():
                    texts.append(child.get_text())
        
        assert any('(A)' in t for t in texts)
        assert any('(B)' in t for t in texts)
        
    def test_add_panel_labels_custom(self, cleanup_figures):
        """测试自定义面板标签"""
        fig, axes = sp.paper_subplots(1, 3, venue="thesis")
        labels = ["实验", "对照", "基准"]
        sp.add_panel_labels(axes, labels=labels)
        
        texts = []
        for ax in axes:
            for child in ax.get_children():
                if hasattr(child, 'get_text') and child.get_text():
                    texts.append(child.get_text())
        
        # 应该包含自定义标签
        all_text = ' '.join(texts)
        assert any(label in all_text for label in labels)


class TestGridSpec:
    """测试 GridSpec 不规则布局"""
    
    def test_create_gridspec(self, cleanup_figures):
        """测试创建 GridSpec"""
        fig, gs = sp.create_gridspec(2, 3, venue="nature")
        assert isinstance(fig, Figure)
        assert isinstance(gs, gridspec.GridSpec)
        
    def test_gridspec_irregular_layout(self, cleanup_figures):
        """测试不规则布局"""
        fig, gs = sp.create_gridspec(2, 3, venue="nature")
        
        # 顶部通栏
        ax_top = fig.add_subplot(gs[0, :])
        # 底部三个小图
        ax_l = fig.add_subplot(gs[1, 0])
        ax_m = fig.add_subplot(gs[1, 1])
        ax_r = fig.add_subplot(gs[1, 2])
        
        assert ax_top is not None
        assert ax_l is not None
        assert ax_m is not None
        assert ax_r is not None


class TestVenueLayouts:
    """测试期刊布局尺寸"""
    
    def test_all_venues_have_layouts(self):
        """测试所有 venue 都有布局定义"""
        venues = sp.list_venues()
        layouts = sp.list_paper_layouts()
        
        for venue in venues:
            info = sp.get_venue_info(venue)
            assert info is not None
            assert "figsize" in info or hasattr(info, 'figsize')
            
    def test_layout_dimensions_reasonable(self):
        """测试布局尺寸合理"""
        layouts = sp.list_paper_layouts()
        
        for venue in layouts:
            info = sp.get_venue_info(venue)
            width, height = info["figsize"]
            
            # 宽度应该在 2-10 英寸之间
            assert 2.0 <= width <= 10.0
            # 高度应该在 2-8 英寸之间
            assert 2.0 <= height <= 8.0
            # 宽高比应该合理
            assert 0.5 <= height / width <= 2.0
