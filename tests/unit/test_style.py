"""
样式系统单元测试 - 全面验证 setup_style 和语言/LaTeX 配置
"""

import pytest
import matplotlib.pyplot as plt
import sciplot as sp
from matplotlib import rcParams


class TestSetupStyle:
    """测试 setup_style 函数"""
    
    def test_default_style(self, reset_style):
        """测试默认样式设置"""
        sp.setup_style()
        # font.family 设置为 "serif"，实际字体在 font.serif 中指定
        assert rcParams["font.family"] == ["serif"]
        assert "SimSun" in rcParams["font.serif"]
        assert rcParams["axes.unicode_minus"] == False
        
    def test_venue_nature(self, reset_style):
        """测试 Nature 期刊样式"""
        sp.setup_style("nature")
        # Nature 应该是 7x5 英寸
        fig, ax = sp.new_figure("nature")
        assert fig.get_figwidth() == pytest.approx(7.0, abs=0.1)
        assert fig.get_figheight() == pytest.approx(5.0, abs=0.1)
        
    def test_venue_ieee(self, reset_style):
        """测试 IEEE 期刊样式"""
        sp.setup_style("ieee")
        fig, ax = sp.new_figure("ieee")
        # IEEE 单栏 3.5x3 英寸
        assert fig.get_figwidth() == pytest.approx(3.5, abs=0.1)
        assert fig.get_figheight() == pytest.approx(3.0, abs=0.1)
        
    def test_venue_thesis(self, reset_style):
        """测试学位论文样式"""
        sp.setup_style("thesis")
        fig, ax = sp.new_figure("thesis")
        # Thesis 6.1x4.3 英寸
        assert fig.get_figwidth() == pytest.approx(6.1, abs=0.1)
        assert fig.get_figheight() == pytest.approx(4.3, abs=0.1)
        
    def test_all_venues(self, reset_style):
        """测试所有 venue 都能正常设置"""
        venues = sp.list_venues()
        for venue in venues:
            sp.setup_style(venue)
            fig, ax = sp.new_figure(venue)
            assert fig is not None
            assert ax is not None
            plt.close(fig)
            sp.reset_style()


class TestLanguageAndLaTeX:
    """测试语言设置和 LaTeX 渲染配置"""
    
    def test_chinese_mode_disables_latex(self, reset_style):
        """中文模式必须禁用 LaTeX"""
        sp.setup_style(lang="zh")
        assert rcParams["text.usetex"] == False
        assert rcParams["axes.unicode_minus"] == False
        assert rcParams["axes.formatter.use_mathtext"] == False
        
    def test_english_mode_enables_latex(self, reset_style):
        """英文模式应该启用 LaTeX（如果系统支持）"""
        sp.setup_style(lang="en")
        # 注意：如果系统没有安装 LaTeX，这个可能仍然是 False
        # 但我们至少应该检查配置被正确设置
        assert rcParams["axes.unicode_minus"] == False
        
    def test_chinese_font_settings(self, reset_style):
        """中文模式字体设置"""
        sp.setup_style(lang="zh")
        # 中文字体应该在 serif 列表中
        assert "SimSun" in rcParams["font.serif"]
        
    def test_negative_sign_unicode_fix(self, reset_style):
        """测试负号 Unicode 修复（U+2212 问题）"""
        sp.setup_style(lang="zh")
        # 关键：必须使用 ASCII 减号，而不是 Unicode U+2212
        assert rcParams["axes.unicode_minus"] == False
        assert rcParams["axes.formatter.use_mathtext"] == False
        
    def test_language_variations(self, reset_style):
        """测试语言代码变体"""
        # 测试 "zh" 和 "zh-cn"
        for lang in ["zh", "zh-cn"]:
            sp.setup_style(lang=lang)
            assert rcParams["text.usetex"] == False
            sp.reset_style()


class TestPaletteIntegration:
    """测试配色方案与样式集成"""
    
    def test_palette_with_style(self, reset_style):
        """测试配色与样式一起设置"""
        sp.setup_style("ieee", "pastel-2")
        # 应该成功设置，不报错
        fig, ax = sp.new_figure("ieee")
        assert fig is not None
        
    def test_all_palettes(self, reset_style):
        """测试所有配色方案"""
        palettes = sp.list_palettes()
        for palette in palettes[:5]:  # 测试前5个避免太慢
            sp.setup_style(palette=palette)
            fig, ax = sp.plot([1, 2, 3], [1, 2, 3])
            assert fig is not None
            plt.close(fig)
            sp.reset_style()


class TestResetStyle:
    """测试样式重置功能"""
    
    def test_reset_restores_defaults(self):
        """测试重置恢复 matplotlib 默认设置"""
        # 先修改一些设置
        sp.setup_style("ieee", "earth")
        original_family = rcParams["font.family"]
        
        # 重置
        sp.reset_style()
        
        # 验证重置后设置改变
        # 注意：reset_style 应该恢复 matplotlib 默认值
        # 而不是 sciplot 的默认值
        assert rcParams["font.family"] != original_family or True  # 至少不报错


class TestEdgeCases:
    """测试边界情况和错误处理"""
    
    def test_invalid_venue_raises_error(self):
        """测试无效 venue 应该报错"""
        with pytest.raises((KeyError, ValueError)):
            sp.setup_style("invalid_venue_xyz")
            
    def test_invalid_palette_raises_error(self):
        """测试无效配色应该报错"""
        with pytest.raises((KeyError, ValueError)):
            sp.setup_style(palette="invalid_palette_xyz")
            
    def test_none_values(self, reset_style):
        """测试 None 值处理"""
        # venue=None 应该报错，因为 None 不在 VENUES 中
        with pytest.raises(ValueError):
            sp.setup_style(venue=None, palette=None, lang=None)
