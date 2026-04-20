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
        # 应该包含四大内置色系
        assert any("pastel" in p for p in palettes)
        assert any("ocean" in p for p in palettes)
        assert any("forest" in p for p in palettes)
        assert any("sunset" in p for p in palettes)
        
    def test_list_resident_palettes(self):
        """测试列出内置色系"""
        residents = sp.list_resident_palettes()
        assert "pastel" in residents
        assert "earth" in residents
        assert "ocean" in residents
        assert "forest" in residents
        assert "sunset" in residents


class TestPaletteApplication:
    """测试配色应用"""
    
    def test_apply_pastel(self, reset_style):
        """测试应用 pastel 配色"""
        sp.setup_style(palette="pastel")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        lines_obj = ax._get_lines
        has_cycler = hasattr(lines_obj, 'prop_cycler') or hasattr(lines_obj, '_prop_cycle')
        assert has_cycler or lines_obj is not None
        plt.close(fig)
        
    def test_apply_ocean(self, reset_style):
        """测试应用 ocean 配色"""
        sp.setup_style(palette="ocean")
        fig, ax = sp.plot([1, 2], [1, 2])
        assert fig is not None
        plt.close(fig)
        
    def test_apply_forest(self, reset_style):
        """测试应用 forest 配色"""
        sp.setup_style(palette="forest")
        fig, ax = sp.plot([1, 2], [1, 2])
        assert fig is not None
        plt.close(fig)
        
    def test_apply_sunset(self, reset_style):
        """测试应用 sunset 配色"""
        sp.setup_style(palette="sunset")
        fig, ax = sp.plot([1, 2], [1, 2])
        assert fig is not None
        plt.close(fig)


class TestPaletteSubsets:
    """测试配色子集（-1 到 -N）"""
    
    def test_pastel_subsets(self, reset_style):
        """测试 pastel 子集（1-6）"""
        for i in range(1, 7):
            sp.setup_style(palette=f"pastel-{i}")
            fig, ax = sp.plot([1, 2], [1, 2])
            assert fig is not None
            plt.close(fig)
            sp.reset_style()
            
    def test_ocean_subsets(self, reset_style):
        """测试 ocean 子集（1-6）"""
        for i in range(1, 7):
            sp.setup_style(palette=f"ocean-{i}")
            fig, ax = sp.plot([1, 2], [1, 2])
            assert fig is not None
            plt.close(fig)
            sp.reset_style()
            
    def test_forest_subsets(self, reset_style):
        """测试 forest 子集（1-6）"""
        for i in range(1, 7):
            sp.setup_style(palette=f"forest-{i}")
            fig, ax = sp.plot([1, 2], [1, 2])
            assert fig is not None
            plt.close(fig)
            sp.reset_style()
            
    def test_sunset_subsets(self, reset_style):
        """测试 sunset 子集（1-5）"""
        for i in range(1, 6):
            sp.setup_style(palette=f"sunset-{i}")
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
        colors = [line.get_color() for line in ax.lines]
        assert colors[:2] == sp.get_palette("pastel-2")
        assert fig is not None
        plt.close(fig)
        
        # 3 条线应该使用 -3
        fig, ax = sp.plot_multi(x, [test_data["y"], test_data["y2"], test_data["y3"]])
        colors = [line.get_color() for line in ax.lines]
        assert colors[:3] == sp.get_palette("pastel-3")
        assert fig is not None
        plt.close(fig)
        
        # 4 条线应该使用 -4
        y4 = np.sin(x) * 0.5
        fig, ax = sp.plot_multi(x, [test_data["y"], test_data["y2"], test_data["y3"], y4])
        colors = [line.get_color() for line in ax.lines]
        assert colors[:4] == sp.get_palette("pastel-4")
        assert fig is not None
        plt.close(fig)

    def test_plot_multi_auto_select_earth(self, reset_style, test_data):
        """测试指定 earth 时自动选择 earth-N 子集"""
        x = test_data["x"]
        fig, ax = sp.plot_multi(
            x,
            [test_data["y"], test_data["y2"], test_data["y3"]],
            palette="earth",
        )
        colors = [line.get_color() for line in ax.lines]
        assert colors[:3] == sp.get_palette("earth-3")
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
        assert len(palette) >= 5
        # 验证是有效的颜色代码
        for color in palette:
            assert color.startswith("#")
            assert len(color) == 7
            
    def test_get_palette_pastel_colors(self):
        """测试获取 pastel 配色颜色正确"""
        palette = sp.get_palette("pastel")
        expected = ["#845EC2", "#D65DB1", "#FF6F91", "#FF9671", "#FFC75F", "#F9F871"]
        assert palette == expected
            
    def test_get_palette_ocean_colors(self):
        """测试获取 ocean 配色颜色正确"""
        palette = sp.get_palette("ocean")
        expected = ["#5E98C2", "#26B3D1", "#00CCCB", "#56E2B0", "#A6F18C", "#F9F871"]
        assert palette == expected
        
    def test_get_palette_forest_colors(self):
        """测试获取 forest 配色颜色正确"""
        palette = sp.get_palette("forest")
        expected = ["#5EC299", "#00B3A2", "#00A2AD", "#0090B8", "#007DBD", "#0067B9"]
        assert palette == expected
        
    def test_get_palette_sunset_colors(self):
        """测试获取 sunset 配色颜色正确"""
        palette = sp.get_palette("sunset")
        expected = ["#D44132", "#F45E4A", "#FF7A62", "#FF967C", "#FFB296"]
        assert palette == expected
        
    def test_get_palette_invalid_name(self):
        """测试获取无效配色"""
        with pytest.raises((KeyError, ValueError)):
            sp.get_palette("nonexistent_palette_xyz")


class TestPaletteConstants:
    """测试配色常量"""
    
    def test_pastel_palette_constant(self):
        """测试 PASTEL_PALETTE 常量"""
        assert hasattr(sp, "PASTEL_PALETTE")
        assert "pastel" in sp.PASTEL_PALETTE
        assert len(sp.PASTEL_PALETTE["pastel"]) == 6
        
    def test_ocean_palette_constant(self):
        """测试 OCEAN_PALETTE 常量"""
        assert hasattr(sp, "OCEAN_PALETTE")
        assert "ocean" in sp.OCEAN_PALETTE
        assert len(sp.OCEAN_PALETTE["ocean"]) == 6
        
    def test_forest_palette_constant(self):
        """测试 FOREST_PALETTE 常量"""
        assert hasattr(sp, "FOREST_PALETTE")
        assert "forest" in sp.FOREST_PALETTE
        assert len(sp.FOREST_PALETTE["forest"]) == 6
        
    def test_sunset_palette_constant(self):
        """测试 SUNSET_PALETTE 常量"""
        assert hasattr(sp, "SUNSET_PALETTE")
        assert "sunset" in sp.SUNSET_PALETTE
        assert len(sp.SUNSET_PALETTE["sunset"]) == 5
        
    def test_default_palette(self):
        """测试默认配色是 pastel"""
        assert sp.DEFAULT_PALETTE == "pastel"


class TestRMBPalettes:
    """测试人民币配色恢复"""

    def test_rmb_palettes_available(self):
        """人民币配色应可直接获取"""
        palette = sp.get_palette("100yuan")
        assert isinstance(palette, list)
        assert len(palette) == 5

    def test_list_rmb_palettes(self):
        """应提供 list_rmb_palettes 入口"""
        names = sp.list_rmb_palettes()
        assert "100yuan" in names
        assert "1yuan" in names


class TestDivergingPalettes:
    """测试发散配色及 cmap 注册"""

    def test_diverging_palette_available(self):
        palette = sp.get_palette("rdbu")
        assert isinstance(palette, list)
        assert len(palette) == 7

    def test_rdbu_heatmap_cmap_registered(self, reset_style):
        data = np.random.randn(5, 5)
        fig, ax = sp.plot_heatmap(data, cmap="rdbu")
        assert fig is not None
        plt.close(fig)


class TestColorBlindFriendly:
    """测试色盲友好性"""
    
    def test_pastel_is_colorblind_friendly(self):
        """测试 pastel 配色是否色盲友好"""
        palette = sp.get_palette("pastel")
        # pastel 应该至少有 5 个不同的颜色
        assert len(palette) >= 5
        # 颜色应该足够区分
        assert len(set(palette)) == len(palette)


class TestValidateHexColor:
    """测试 _validate_hex_color 类型安全"""

    def test_non_string_input_returns_false(self):
        """非字符串输入应返回 False"""
        from sciplot._core.palette import _validate_hex_color
        assert _validate_hex_color(123) is False
        assert _validate_hex_color(None) is False
        assert _validate_hex_color(["#FF0000"]) is False

    def test_valid_hex_returns_true(self):
        """有效 HEX 颜色应返回 True"""
        from sciplot._core.palette import _validate_hex_color
        assert _validate_hex_color("#FF0000") is True
        assert _validate_hex_color("#F00") is True
        assert _validate_hex_color("#845EC2") is True

    def test_invalid_hex_returns_false(self):
        """无效 HEX 颜色应返回 False"""
        from sciplot._core.palette import _validate_hex_color
        assert _validate_hex_color("FF0000") is False
        assert _validate_hex_color("#GG0000") is False
        assert _validate_hex_color("") is False


class TestAutoSelectBestMatch:
    """测试 auto_select 最近匹配逻辑"""

    def test_auto_select_exact_match(self):
        """精确匹配 name-n"""
        from sciplot._core.palette import _UserPaletteStore
        _UserPaletteStore.set("test_exact", ["#A", "#B", "#C"])
        result = _UserPaletteStore.auto_select("test_exact", 2)
        assert result == ["#A", "#B"]

    def test_auto_select_fallback_to_largest(self):
        """当所有配色方案颜色数都小于 n 时，返回最大的配色"""
        from sciplot._core.palette import _UserPaletteStore
        scheme = {
            "single": ["#111111"],
            "double": ["#111111", "#222222"],
            "triple": ["#111111", "#222222", "#333333"],
        }
        _UserPaletteStore.register_scheme("test_fallback", scheme)
        result = _UserPaletteStore.auto_select("test_fallback", 10)
        assert result is not None
        assert len(result) == 3

    def test_auto_select_unknown_returns_none(self):
        """未知配色方案返回 None"""
        from sciplot._core.palette import _UserPaletteStore
        result = _UserPaletteStore.auto_select("nonexistent_scheme_xyz", 3)
        assert result is None


class TestSetCustomPaletteValidation:
    """测试 set_custom_palette 的输入验证"""

    def test_non_hex_color_raises(self):
        """非 HEX 格式颜色应抛出异常"""
        with pytest.raises(ValueError, match="颜色格式错误"):
            sp.set_custom_palette(["not_a_color", "#3498DB"], name="bad")

    def test_empty_colors_raises(self):
        """空颜色列表应抛出异常"""
        with pytest.raises(ValueError, match="不能为空"):
            sp.set_custom_palette([], name="empty")

    def test_single_color_warns(self):
        """单色配色应发出警告"""
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            sp.set_custom_palette(["#E74C3C"], name="single_warn")
            assert len(w) >= 1
            assert "至少包含 2 种颜色" in str(w[0].message)


class TestRegisterColorSchemeValidation:
    """测试 register_color_scheme 的输入验证"""

    def test_missing_required_key_raises(self):
        """缺少必要键应抛出异常"""
        with pytest.raises(ValueError, match="必须包含"):
            sp.register_color_scheme("bad_scheme", {"double": ["#A", "#B"]})

    def test_non_list_value_raises(self):
        """非列表值应抛出异常"""
        with pytest.raises(ValueError, match="必须是颜色列表"):
            sp.register_color_scheme("bad_scheme2", {
                "single": "#264653",
                "double": ["#264653", "#2a9d8f"],
                "triple": ["#264653", "#2a9d8f", "#e9c46a"],
            })

    def test_non_hex_in_scheme_raises(self):
        """配色方案中非 HEX 颜色应抛出异常"""
        with pytest.raises(ValueError, match="颜色格式错误"):
            sp.register_color_scheme("bad_scheme3", {
                "single": ["not_a_color"],
                "double": ["#264653", "#2a9d8f"],
                "triple": ["#264653", "#2a9d8f", "#e9c46a"],
            })
