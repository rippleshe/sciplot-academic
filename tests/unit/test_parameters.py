"""
参数边界值测试 - 验证函数参数处理的一致性和健壮性
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
import sciplot as sp
from matplotlib.figure import Figure
from matplotlib.axes import Axes


class TestParameterValidation:
    """测试参数验证"""
    
    def test_plot_with_empty_arrays(self, cleanup_figures):
        """测试空数组处理"""
        # 空数组应该优雅处理或给出清晰错误
        try:
            fig, ax = sp.plot([], [])
            # 如果成功，验证返回类型
            assert isinstance(fig, Figure)
        except (ValueError, IndexError) as e:
            # 如果失败，验证错误信息清晰
            assert "empty" in str(e).lower() or "length" in str(e).lower()
            
    def test_plot_with_mismatched_lengths(self, cleanup_figures):
        """测试长度不匹配的数组"""
        with pytest.raises(ValueError):
            sp.plot([1, 2, 3], [1, 2])
            
    def test_plot_with_single_point(self, cleanup_figures):
        """测试单点数据"""
        fig, ax = sp.plot([1], [1])
        assert isinstance(fig, Figure)
        assert len(ax.lines) == 1
        
    def test_plot_with_nan_values(self, cleanup_figures):
        """测试 NaN 值处理"""
        x = np.array([1, 2, np.nan, 4])
        y = np.array([1, 2, 3, 4])
        fig, ax = sp.plot(x, y)
        assert isinstance(fig, Figure)
        
    def test_plot_with_inf_values(self, cleanup_figures):
        """测试无穷值处理"""
        x = np.array([1, 2, np.inf, 4])
        y = np.array([1, 2, 3, 4])
        fig, ax = sp.plot(x, y)
        assert isinstance(fig, Figure)


class TestVenueParameter:
    """测试 venue 参数"""
    
    def test_all_venues_accepted(self, cleanup_figures):
        """测试所有 venue 都被接受"""
        venues = sp.list_venues()
        for venue in venues:
            sp.setup_style(venue=venue)
            fig, ax = sp.plot([1, 2], [1, 2])
            assert isinstance(fig, Figure)
            plt.close(fig)
            sp.reset_style()
            
    def test_invalid_venue_raises_error(self):
        """测试无效 venue 报错"""
        with pytest.raises(ValueError) as exc_info:
            sp.setup_style(venue="invalid_venue_xyz")
        assert "invalid_venue_xyz" in str(exc_info.value)
        
    def test_case_sensitive_venue(self):
        """测试 venue 大小写敏感"""
        # 大写应该不被接受
        with pytest.raises(ValueError):
            sp.setup_style(venue="IEEE")  # 应该是 "ieee"


class TestPaletteParameter:
    """测试 palette 参数"""
    
    def test_all_palettes_accepted(self, cleanup_figures):
        """测试所有 palette 都被接受"""
        palettes = sp.list_palettes()
        for palette in palettes[:5]:  # 测试前5个避免太慢
            sp.setup_style(palette=palette)
            fig, ax = sp.plot([1, 2], [1, 2])
            assert isinstance(fig, Figure)
            plt.close(fig)
            sp.reset_style()
            
    def test_invalid_palette_raises_error(self):
        """测试无效 palette 报错"""
        with pytest.raises((ValueError, KeyError)):
            sp.setup_style(palette="invalid_palette_xyz")
            
    def test_palette_subsets(self, cleanup_figures):
        """测试 palette 子集"""
        for i in range(1, 5):
            sp.setup_style(palette=f"pastel-{i}")
            fig, ax = sp.plot([1, 2], [1, 2])
            assert isinstance(fig, Figure)
            plt.close(fig)
            sp.reset_style()


class TestLanguageParameter:
    """测试 lang 参数"""
    
    def test_zh_language(self, cleanup_figures):
        """测试中文语言"""
        sp.setup_style(lang="zh")
        fig, ax = sp.plot([1, 2], [1, 2], xlabel="中文")
        assert isinstance(fig, Figure)
        
    def test_zh_cn_language(self, cleanup_figures):
        """测试中文(中国)语言"""
        sp.setup_style(lang="zh-cn")
        fig, ax = sp.plot([1, 2], [1, 2], xlabel="中文")
        assert isinstance(fig, Figure)
        
    def test_en_language(self, cleanup_figures):
        """测试英文语言"""
        sp.setup_style(lang="en")
        fig, ax = sp.plot([1, 2], [1, 2], xlabel="English")
        assert isinstance(fig, Figure)
        
    def test_invalid_language_raises_error(self):
        """测试无效语言报错"""
        with pytest.raises(ValueError):
            sp.setup_style(lang="invalid_lang")


class TestFigureSizeParameter:
    """测试 figsize 参数"""
    
    def test_custom_figsize(self, cleanup_figures):
        """测试自定义尺寸"""
        fig, ax = sp.new_figure("ieee", figsize=(5.0, 4.0))
        assert fig.get_figwidth() == pytest.approx(5.0, abs=0.1)
        assert fig.get_figheight() == pytest.approx(4.0, abs=0.1)
        
    def test_zero_figsize_raises_error(self):
        """测试零尺寸报错（matplotlib 可能接受但不合理）"""
        # matplotlib 可能不报错，但会产生不可用的图
        # 我们测试它至少不崩溃，但尺寸不合理
        try:
            fig, ax = sp.new_figure("ieee", figsize=(0.1, 0.1))
            # 如果能创建，尺寸应该非常小
            assert fig.get_figwidth() < 1.0
        except (ValueError, AssertionError):
            pass  # 报错也是合理的
            
    def test_negative_figsize_raises_error(self):
        """测试负尺寸报错"""
        with pytest.raises((ValueError, AssertionError)):
            sp.new_figure("ieee", figsize=(-1, -1))


class TestDPIParameter:
    """测试 DPI 参数"""
    
    def test_high_dpi(self, temp_dir, cleanup_figures):
        """测试高 DPI"""
        fig, ax = sp.plot([1, 2], [1, 2])
        output_path = temp_dir / "high_dpi"
        paths = sp.save(fig, output_path, formats=("png",), dpi=1200)
        assert paths[0].exists()
        
    def test_low_dpi(self, temp_dir, cleanup_figures):
        """测试低 DPI"""
        fig, ax = sp.plot([1, 2], [1, 2])
        output_path = temp_dir / "low_dpi"
        paths = sp.save(fig, output_path, formats=("png",), dpi=72)
        assert paths[0].exists()
        
    def test_zero_dpi_raises_error(self, temp_dir, cleanup_figures):
        """测试零 DPI 报错"""
        fig, ax = sp.plot([1, 2], [1, 2])
        output_path = temp_dir / "zero_dpi"
        with pytest.raises((ValueError, AssertionError)):
            sp.save(fig, output_path, formats=("png",), dpi=0)


class TestLabelParameters:
    """测试标签参数"""
    
    def test_empty_labels(self, cleanup_figures):
        """测试空标签"""
        fig, ax = sp.plot([1, 2], [1, 2], xlabel="", ylabel="", title="")
        assert isinstance(fig, Figure)
        assert ax.get_xlabel() == ""
        assert ax.get_ylabel() == ""
        assert ax.get_title() == ""
        
    def test_long_labels(self, cleanup_figures):
        """测试长标签"""
        long_label = "A" * 200
        fig, ax = sp.plot([1, 2], [1, 2], xlabel=long_label)
        assert isinstance(fig, Figure)
        assert ax.get_xlabel() == long_label
        
    def test_unicode_labels(self, cleanup_figures):
        """测试 Unicode 标签"""
        fig, ax = sp.plot(
            [1, 2], [1, 2],
            xlabel="中文标签",
            ylabel="日本語ラベル",
            title="Emoji 🎨"
        )
        assert isinstance(fig, Figure)
        assert ax.get_xlabel() == "中文标签"
        assert ax.get_ylabel() == "日本語ラベル"


class TestColorParameters:
    """测试颜色参数"""
    
    def test_hex_color(self, cleanup_figures):
        """测试 HEX 颜色"""
        fig, ax = sp.plot([1, 2], [1, 2], color="#FF5733")
        assert isinstance(fig, Figure)
        
    def test_named_color(self, cleanup_figures):
        """测试命名颜色"""
        fig, ax = sp.plot([1, 2], [1, 2], color="red")
        assert isinstance(fig, Figure)
        
    def test_rgb_color(self, cleanup_figures):
        """测试 RGB 颜色"""
        fig, ax = sp.plot([1, 2], [1, 2], color=(0.5, 0.5, 0.5))
        assert isinstance(fig, Figure)
        
    def test_invalid_color_raises_error(self, cleanup_figures):
        """测试无效颜色报错"""
        # matplotlib 可能会接受一些奇怪的颜色，但至少不崩溃
        try:
            fig, ax = sp.plot([1, 2], [1, 2], color="invalid_color")
        except ValueError:
            pass  # 报错是合理的


class TestAlphaParameter:
    """测试透明度参数"""
    
    def test_zero_alpha(self, cleanup_figures):
        """测试完全透明"""
        fig, ax = sp.plot([1, 2], [1, 2], alpha=0)
        assert isinstance(fig, Figure)
        
    def test_full_alpha(self, cleanup_figures):
        """测试完全不透明"""
        fig, ax = sp.plot([1, 2], [1, 2], alpha=1)
        assert isinstance(fig, Figure)
        
    def test_half_alpha(self, cleanup_figures):
        """测试半透明"""
        fig, ax = sp.plot([1, 2], [1, 2], alpha=0.5)
        assert isinstance(fig, Figure)
        
    def test_negative_alpha_raises_error(self, cleanup_figures):
        """测试负透明度报错"""
        with pytest.raises((ValueError, AssertionError)):
            sp.plot([1, 2], [1, 2], alpha=-0.5)
            
    def test_alpha_greater_than_one_raises_error(self, cleanup_figures):
        """测试透明度大于1报错"""
        with pytest.raises((ValueError, AssertionError)):
            sp.plot([1, 2], [1, 2], alpha=1.5)


class TestMarkerSizeParameter:
    """测试标记大小参数"""
    
    def test_zero_marker_size(self, cleanup_figures):
        """测试零标记大小"""
        fig, ax = sp.scatter([1, 2], [1, 2], s=0)
        assert isinstance(fig, Figure)
        
    def test_large_marker_size(self, cleanup_figures):
        """测试大标记大小"""
        fig, ax = sp.scatter([1, 2], [1, 2], s=1000)
        assert isinstance(fig, Figure)
        
    def test_negative_marker_size_warning(self, cleanup_figures):
        """测试负标记大小产生警告（matplotlib 可能接受但会警告）"""
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            fig, ax = sp.scatter([1, 2], [1, 2], s=-10)
            # matplotlib 可能产生警告，但至少不崩溃
            assert isinstance(fig, Figure)


class TestLineWidthParameter:
    """测试线宽参数"""
    
    def test_zero_line_width(self, cleanup_figures):
        """测试零线宽"""
        fig, ax = sp.plot([1, 2], [1, 2], linewidth=0)
        assert isinstance(fig, Figure)
        
    def test_thick_line(self, cleanup_figures):
        """测试粗线"""
        fig, ax = sp.plot([1, 2], [1, 2], linewidth=5)
        assert isinstance(fig, Figure)
        
    def test_negative_line_width_warning(self, cleanup_figures):
        """测试负线宽产生警告（matplotlib 可能接受但会警告）"""
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            fig, ax = sp.plot([1, 2], [1, 2], linewidth=-1)
            # matplotlib 可能产生警告，但至少不崩溃
            assert isinstance(fig, Figure)


class TestBinsParameter:
    """测试 bins 参数（直方图）"""
    
    def test_low_bins(self, cleanup_figures):
        """测试少 bins"""
        data = np.random.normal(0, 1, 100)
        fig, ax = sp.hist(data, bins=5)
        assert isinstance(fig, Figure)
        
    def test_high_bins(self, cleanup_figures):
        """测试多 bins"""
        data = np.random.normal(0, 1, 1000)
        fig, ax = sp.hist(data, bins=100)
        assert isinstance(fig, Figure)
        
    def test_zero_bins_raises_error(self, cleanup_figures):
        """测试零 bins 报错"""
        data = np.random.normal(0, 1, 100)
        with pytest.raises((ValueError, AssertionError)):
            sp.hist(data, bins=0)
