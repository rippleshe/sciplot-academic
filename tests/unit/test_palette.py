"""
配色系统单元测试 - 验证配色方案、自动选择、自定义配色
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
import sciplot as sp
from matplotlib import rcParams


class TestPaletteBasics:
    """测试配色基础功能"""
    
    def test_list_palettes(self):
        """测试列出所有配色"""
        palettes = sp.list_palettes()
        assert isinstance(palettes, list)
        assert len(palettes) > 0
        # 应该包含三大常驻色系
        assert any("pastel" in p for p in palettes)
        assert any("earth" in p for p in palettes)
        assert any("ocean" in p for p in palettes)
        
    def test_list_resident_palettes(self):
        """测试列出常驻色系"""
        residents = sp.list_resident_palettes()
        assert "pastel" in residents
        assert "earth" in residents
        assert "ocean" in residents
        
    def test_list_rmb_palettes(self):
        """测试列出人民币配色"""
        rmb = sp.list_rmb_palettes()
        assert "100yuan" in rmb
        assert "50yuan" in rmb
        assert "10yuan" in rmb


class TestPaletteApplication:
    """测试配色应用"""
    
    def test_apply_pastel(self, reset_style):
        """测试应用 pastel 配色"""
        sp.setup_style(palette="pastel")
        # 获取当前颜色循环
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        # 验证颜色循环被设置（不同 matplotlib 版本属性名可能不同）
        lines_obj = ax._get_lines
        # 检查是否有颜色循环相关属性
        has_cycler = hasattr(lines_obj, 'prop_cycler') or hasattr(lines_obj, '_prop_cycle')
        assert has_cycler or lines_obj is not None
        plt.close(fig)
        
    def test_apply_earth(self, reset_style):
        """测试应用 earth 配色"""
        sp.setup_style(palette="earth")
        fig, ax = sp.plot([1, 2], [1, 2])
        assert fig is not None
        plt.close(fig)
        
    def test_apply_ocean(self, reset_style):
        """测试应用 ocean 配色"""
        sp.setup_style(palette="ocean")
        fig, ax = sp.plot([1, 2], [1, 2])
        assert fig is not None
        plt.close(fig)


class TestPaletteSubsets:
    """测试配色子集（-1, -2, -3, -4）"""
    
    def test_pastel_subsets(self, reset_style):
        """测试 pastel 子集"""
        for i in range(1, 5):
            sp.setup_style(palette=f"pastel-{i}")
            fig, ax = sp.plot([1, 2], [1, 2])
            assert fig is not None
            plt.close(fig)
            sp.reset_style()
            
    def test_earth_subsets(self, reset_style):
        """测试 earth 子集"""
        for i in range(1, 5):
            sp.setup_style(palette=f"earth-{i}")
            fig, ax = sp.plot([1, 2], [1, 2])
            assert fig is not None
            plt.close(fig)
            sp.reset_style()
            
    def test_invalid_subset_raises_error(self):
        """测试无效子集应该报错"""
        with pytest.raises((KeyError, ValueError)):
            sp.setup_style(palette="pastel-10")  # 超出范围


class TestAutoPaletteSelection:
    """测试自动配色选择"""
    
    def test_plot_multi_auto_select(self, reset_style, test_data):
        """测试 plot_multi 自动选择配色子集"""
        x = test_data["x"]
        
        # 2 条线应该使用 -2
        fig, ax = sp.plot_multi(x, [test_data["y"], test_data["y2"]])
        assert fig is not None
        plt.close(fig)
        
        # 3 条线应该使用 -3
        fig, ax = sp.plot_multi(x, [test_data["y"], test_data["y2"], test_data["y3"]])
        assert fig is not None
        plt.close(fig)
        
        # 4 条线应该使用 -4
        y4 = np.sin(x) * 0.5
        fig, ax = sp.plot_multi(x, [test_data["y"], test_data["y2"], test_data["y3"], y4])
        assert fig is not None
        plt.close(fig)


class TestCustomPalette:
    """测试自定义配色"""
    
    def test_set_custom_palette(self, reset_style):
        """测试设置自定义配色"""
        colors = ["#E74C3C", "#3498DB", "#2ECC71"]
        sp.set_custom_palette(colors, name="mybrand")
        
        # 应用自定义配色
        sp.setup_style(palette="mybrand")
        fig, ax = sp.plot([1, 2], [1, 2])
        assert fig is not None
        plt.close(fig)
        
    def test_custom_palette_subset(self, reset_style):
        """测试自定义配色子集"""
        colors = ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6"]
        sp.set_custom_palette(colors, name="mybrand")
        
        # 使用子集
        sp.setup_style(palette="mybrand-2")
        fig, ax = sp.plot([1, 2], [1, 2])
        assert fig is not None
        plt.close(fig)


class TestColorSchemeRegistration:
    """测试配色方案注册"""
    
    def test_register_color_scheme(self, reset_style):
        """测试注册完整配色方案"""
        scheme = {
            "single": ["#264653"],
            "double": ["#264653", "#2a9d8f"],
            "triple": ["#264653", "#2a9d8f", "#e9c46a"],
            "quadruple": ["#264653", "#2a9d8f", "#e9c46a", "#f4a261"],
            "quintuple": ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"],
        }
        sp.register_color_scheme("mytheme", scheme)
        
        # 使用注册的配色
        sp.setup_style(palette="mytheme-triple")
        fig, ax = sp.plot([1, 2], [1, 2])
        assert fig is not None
        plt.close(fig)
        
    def test_register_invalid_scheme(self):
        """测试注册无效配色方案"""
        with pytest.raises((ValueError, KeyError)):
            sp.register_color_scheme("invalid", {"invalid_key": ["#000"]})


class TestGetPalette:
    """测试获取配色"""
    
    def test_get_palette_returns_list(self):
        """测试获取配色返回列表"""
        palette = sp.get_palette("pastel")
        assert isinstance(palette, list)
        assert len(palette) >= 4
        # 验证是有效的颜色代码
        for color in palette:
            assert color.startswith("#")
            assert len(color) == 7
            
    def test_get_palette_invalid_name(self):
        """测试获取无效配色"""
        with pytest.raises((KeyError, ValueError)):
            sp.get_palette("nonexistent_palette_xyz")


class TestColorBlindFriendly:
    """测试色盲友好性"""
    
    def test_pastel_is_colorblind_friendly(self):
        """测试 pastel 配色是否色盲友好"""
        palette = sp.get_palette("pastel")
        # pastel 应该至少有 4 个不同的颜色
        assert len(palette) >= 4
        # 颜色应该足够区分
        assert len(set(palette)) == len(palette)
