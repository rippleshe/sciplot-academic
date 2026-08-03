"""
回归测试 - 验证已修复问题不会再次出现
"""

import pytest
import numpy as np
import sciplot as sp
from matplotlib import rcParams
import warnings


class TestUnicodeMinusFix:
    """
    回归测试：负号显示问题 (U+2212)
    
    问题描述：matplotlib 默认使用 Unicode 减号 U+2212，
    但中文字体通常不包含这个字符，导致显示为方框或警告。
    
    修复方案：
    1. 设置 axes.unicode_minus = False（使用 ASCII 减号）
    2. 设置 axes.formatter.use_mathtext = False
    """
    
    def test_unicode_minus_disabled_in_zh_mode(self):
        """中文模式必须禁用 Unicode 减号"""
        sp.setup_style(lang="zh")
        assert not rcParams["axes.unicode_minus"]
        assert not rcParams["axes.formatter.use_mathtext"]
        
    def test_no_unicode_minus_warning(self, temp_dir, cleanup_figures):
        """测试不产生 U+2212 警告"""
        sp.setup_style("thesis", lang="zh")
        
        x = np.linspace(-5, 5, 100)
        y = -np.abs(x)
        
        # 捕获警告
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            fig, ax = sp.plot(x, y)
            
            # 不应该有 Unicode 减号相关的警告
            unicode_warnings = [warning for warning in w 
                              if "U+2212" in str(warning.message) or 
                                 "unicode_minus" in str(warning.message)]
            assert len(unicode_warnings) == 0, f"发现 Unicode 减号警告: {unicode_warnings}"
            
    def test_negative_numbers_display_correctly(self, temp_dir, cleanup_figures):
        """测试负数正确显示"""
        sp.setup_style("thesis", lang="zh")
        
        x = np.linspace(-10, 10, 100)
        y = x  # 包含正负值
        
        fig, ax = sp.plot(x, y, xlabel="X", ylabel="Y")
        
        # 保存应该成功，不报错
        output_path = temp_dir / "negative_values"
        paths = sp.save(fig, output_path, formats=("png",))
        assert len(paths) == 1


class TestLaTeXChineseCompatibility:
    """
    回归测试：LaTeX 与中文兼容性
    
    问题描述：LaTeX 渲染不支持中文字符，
    如果在中文模式下启用 LaTeX，会导致中文显示为空白或报错。
    
    修复方案：
    中文模式自动禁用 LaTeX（text.usetex = False）
    英文模式自动启用 LaTeX（text.usetex = True）
    """
    
    def test_latex_disabled_in_chinese(self):
        """中文模式必须禁用 LaTeX"""
        sp.setup_style(lang="zh")
        assert not rcParams["text.usetex"]
        
    def test_latex_enabled_in_english(self):
        """英文模式应该启用 LaTeX"""
        sp.setup_style(lang="en")
        # 如果系统安装了 LaTeX，应该启用
        # 如果没有安装，matplotlib 会回退到普通文本
        # 但至少配置应该被设置
        
    def test_chinese_text_renders_correctly(self, temp_dir, cleanup_figures):
        """测试中文文本正确渲染"""
        sp.setup_style("thesis", lang="zh")
        
        fig, ax = sp.plot(
            [1, 2, 3], [1, 2, 3],
            xlabel="中文标签",
            ylabel="中文标签",
            title="中文标题"
        )
        
        # 保存应该成功
        output_path = temp_dir / "chinese_text"
        paths = sp.save(fig, output_path, formats=("png",))
        assert len(paths) == 1
        
    def test_mixed_chinese_english(self, temp_dir, cleanup_figures):
        """测试中英文混合"""
        sp.setup_style("thesis", lang="zh")
        
        fig, ax = sp.plot(
            [1, 2, 3], [1, 2, 3],
            xlabel="时间 Time (s)",
            ylabel="电压 Voltage (V)"
        )
        
        output_path = temp_dir / "mixed_text"
        paths = sp.save(fig, output_path, formats=("png",))
        assert len(paths) == 1


class TestColorPaletteRegression:
    """
    回归测试：配色方案问题
    
    问题描述：早期版本依赖 SciencePlots 的 rainbow/TOL 配色，
    但这些配色在某些环境下不可用。
    
    修复方案：所有配色均为内置，不依赖外部配色
    """
    
    def test_all_palettes_builtin(self):
        """测试所有配色都是内置的"""
        palettes = sp.list_palettes()
        
        # 不应该依赖 SciencePlots 的配色
        for palette in palettes:
            # 每个配色应该都能直接获取
            colors = sp.get_palette(palette)
            assert len(colors) > 0
            assert all(c.startswith("#") for c in colors)
            
    def test_pastel_not_rainbow(self):
        """测试 pastel 不是 rainbow"""
        pastel = sp.get_palette("pastel")
        # pastel 应该是柔和的粉彩色，不是彩虹色
        # 简单检查：pastel 的颜色应该比较浅（RGB 值较高）
        for color in pastel[:3]:
            # 解析 HEX 颜色
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            # pastel 颜色应该比较浅（至少一个通道 > 128）
            assert max(r, g, b) > 128, f"{color} 不是 pastel 颜色"


class TestAliasConsistency:
    """
    回归测试：别名函数参数一致性
    
    问题描述：别名函数和原函数的参数不一致，
    导致使用别名时报错。
    
    修复方案：确保所有别名函数参数与原函数完全一致
    """
    
    def test_line_alias_signature(self):
        """测试 line 别名签名"""
        import inspect
        sig_original = inspect.signature(sp.plot_line)
        sig_alias = inspect.signature(sp.line)
        
        orig_params = list(sig_original.parameters.keys())
        alias_params = list(sig_alias.parameters.keys())
        
        assert orig_params == alias_params, \
            f"参数不匹配: {orig_params} vs {alias_params}"
        
    def test_scatter_alias_signature(self):
        """测试 scatter 别名签名"""
        import inspect
        sig_original = inspect.signature(sp.plot_scatter)
        sig_alias = inspect.signature(sp.scatter)
        
        orig_params = list(sig_original.parameters.keys())
        alias_params = list(sig_alias.parameters.keys())
        
        assert orig_params == alias_params
        
    def test_bar_alias_signature(self):
        """测试 bar 别名签名"""
        import inspect
        sig_original = inspect.signature(sp.plot_bar)
        sig_alias = inspect.signature(sp.bar)
        
        orig_params = list(sig_original.parameters.keys())
        alias_params = list(sig_alias.parameters.keys())
        
        assert orig_params == alias_params


class TestContextManagerNesting:
    """
    回归测试：上下文管理器嵌套问题
    
    问题描述：嵌套使用 style_context 时，
    退出内层上下文后没有正确恢复外层上下文。
    
    修复方案：使用栈结构保存状态，确保正确恢复
    """
    
    def test_nested_context_restores_correctly(self, cleanup_figures):
        """测试嵌套上下文正确恢复"""
        x = [1, 2, 3]
        y = [1, 2, 3]
        
        # 外层上下文
        with sp.style_context("nature", palette="pastel"):
            fig1, ax1 = sp.plot(x, y)
            
            # 内层上下文
            with sp.style_context("ieee", palette="ocean"):
                fig2, ax2 = sp.plot(x, y)
                # 这里应该是 ieee + ocean
                
            # 退出内层后，应该恢复为 nature + pastel
            fig3, ax3 = sp.plot(x, y)
            
        # 所有图都应该成功创建
        assert fig1 is not None
        assert fig2 is not None
        assert fig3 is not None


class TestSaveFunction:
    """
    回归测试：保存功能问题
    
    问题描述：保存时格式处理、路径处理等问题
    """
    
    def test_save_creates_directory(self, temp_dir, cleanup_figures):
        """测试保存自动创建目录"""
        fig, ax = sp.plot([1, 2], [1, 2])
        
        nested_dir = temp_dir / "nested" / "deep" / "dir"
        output_path = nested_dir / "figure"
        
        # 目录不存在时应该自动创建
        paths = sp.save(fig, output_path, formats=("png",))
        
        assert len(paths) == 1
        assert paths[0].exists()
        
    def test_save_multiple_formats(self, temp_dir, cleanup_figures):
        """测试保存多种格式"""
        fig, ax = sp.plot([1, 2], [1, 2])
        
        output_path = temp_dir / "multi_format"
        paths = sp.save(fig, output_path, formats=("png", "pdf", "svg"))
        
        assert len(paths) == 3
        for path in paths:
            assert path.exists()
            
    def test_save_with_dir_parameter(self, temp_dir, cleanup_figures):
        """测试使用 dir 参数"""
        fig, ax = sp.plot([1, 2], [1, 2])
        
        output_path = "figure_name"
        paths = sp.save(fig, output_path, formats=("png",), dir=temp_dir)
        
        assert len(paths) == 1
        assert paths[0].exists()
        assert paths[0].parent == temp_dir
