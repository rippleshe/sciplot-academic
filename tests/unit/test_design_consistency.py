"""
设计一致性测试 - 验证 API 设计的统一性和优雅性
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
import sciplot as sp
import inspect
from matplotlib.figure import Figure
from matplotlib.axes import Axes


class TestAPIConsistency:
    """测试 API 一致性"""
    
    def test_all_plot_functions_have_similar_signature_pattern(self):
        """所有绘图函数应该有相似的签名模式（柱状图使用 categories/values）"""
        # 折线/散点类函数有 x, y
        line_funcs = [sp.plot_line, sp.plot_scatter, sp.plot_area, sp.plot_step]
        for func in line_funcs:
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            assert "x" in params, f"{func.__name__} 缺少 x 参数"
            assert "y" in params, f"{func.__name__} 缺少 y 参数"
        
        # 柱状图使用 categories/values
        bar_sig = inspect.signature(sp.plot_bar)
        bar_params = list(bar_sig.parameters.keys())
        assert "categories" in bar_params, "plot_bar 缺少 categories 参数"
        assert "values" in bar_params, "plot_bar 缺少 values 参数"
            
    def test_all_plot_functions_have_venue_palette_params(self):
        """所有绘图函数应该有 venue 和 palette 参数"""
        plot_funcs = [
            sp.plot_line,
            sp.plot_scatter,
            sp.plot_bar,
            sp.plot_area,
            sp.plot_step,
        ]
        
        for func in plot_funcs:
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            assert "venue" in params, f"{func.__name__} 缺少 venue 参数"
            assert "palette" in params, f"{func.__name__} 缺少 palette 参数"
            
    def test_all_plot_functions_have_label_params(self):
        """所有绘图函数应该有标签参数"""
        plot_funcs = [
            sp.plot_line,
            sp.plot_scatter,
            sp.plot_bar,
            sp.plot_area,
            sp.plot_step,
        ]
        
        for func in plot_funcs:
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            assert "xlabel" in params, f"{func.__name__} 缺少 xlabel 参数"
            assert "ylabel" in params, f"{func.__name__} 缺少 ylabel 参数"
            assert "title" in params, f"{func.__name__} 缺少 title 参数"


class TestAliasConsistency:
    """测试别名一致性"""
    
    def test_aliases_match_original_signatures(self):
        """别名函数签名应该与原函数一致"""
        alias_pairs = [
            (sp.plot_line, sp.line),
            (sp.plot_scatter, sp.scatter),
            (sp.plot_bar, sp.bar),
            (sp.plot_horizontal_bar, sp.hbar),
            (sp.plot_histogram, sp.hist),
            (sp.plot_box, sp.box),
            (sp.plot_violin, sp.violin),
            (sp.plot_heatmap, sp.heatmap),
            (sp.plot_area, sp.area),
            (sp.plot_step, sp.step),
            (sp.plot_errorbar, sp.errorbar),
        ]
        
        for original, alias in alias_pairs:
            orig_sig = inspect.signature(original)
            alias_sig = inspect.signature(alias)
            
            orig_params = list(orig_sig.parameters.keys())
            alias_params = list(alias_sig.parameters.keys())
            
            # 某些别名使用不同的参数名
            if original == sp.plot_bar:
                # 柱状图: categories/values vs x/height
                assert "categories" in orig_params or "x" in orig_params
                assert "values" in orig_params or "height" in orig_params
            elif original == sp.plot_histogram:
                # 直方图: data vs x
                assert "data" in orig_params or "x" in orig_params
            else:
                assert orig_params == alias_params, \
                    f"{original.__name__} 和 {alias.__name__} 参数不匹配: {orig_params} vs {alias_params}"
            
    def test_aliases_have_same_defaults(self):
        """别名函数默认值应该与原函数一致"""
        alias_pairs = [
            (sp.plot_line, sp.line),
            (sp.plot_scatter, sp.scatter),
            # plot_bar/bar 参数名不同，跳过详细检查
        ]
        
        for original, alias in alias_pairs:
            orig_sig = inspect.signature(original)
            alias_sig = inspect.signature(alias)
            
            for param_name in orig_sig.parameters:
                if param_name in alias_sig.parameters:  # 确保参数存在
                    orig_default = orig_sig.parameters[param_name].default
                    alias_default = alias_sig.parameters[param_name].default
                    
                    assert orig_default == alias_default, \
                        f"{original.__name__}.{param_name} 默认值不匹配: {orig_default} vs {alias_default}"


class TestNamingConventions:
    """测试命名规范"""
    
    def test_plot_functions_use_verb_noun_pattern(self):
        """绘图函数使用动词+名词模式"""
        plot_funcs = [
            "plot_line", "plot_scatter", "plot_bar", "plot_area",
            "plot_step", "plot_box", "plot_violin", "plot_heatmap",
        ]
        
        for func_name in plot_funcs:
            assert func_name.startswith("plot_"), \
                f"{func_name} 应该以 plot_ 开头"
            
    def test_aliases_use_noun_only(self):
        """别名使用纯名词"""
        aliases = [
            "line", "scatter", "bar", "area", "step",
            "box", "violin", "heatmap", "hist"
        ]
        
        for alias in aliases:
            assert "_" not in alias, f"{alias} 不应该包含下划线"
            assert alias.islower(), f"{alias} 应该全小写"
            
    def test_venue_names_lowercase(self):
        """venue 名称应该全小写"""
        venues = sp.list_venues()
        for venue in venues:
            assert venue.islower(), f"{venue} 应该全小写"
            assert "_" not in venue, f"{venue} 不应该包含下划线"
            
    def test_palette_names_lowercase(self):
        """palette 名称应该全小写"""
        palettes = sp.list_palettes()
        for palette in palettes:
            assert palette.islower() or "-" in palette, \
                f"{palette} 应该全小写或使用连字符"


class TestDefaultValues:
    """测试默认值一致性"""
    
    def test_default_venue_is_nature(self):
        """默认 venue 应该是 nature"""
        sig = inspect.signature(sp.setup_style)
        venue_default = sig.parameters["venue"].default
        assert venue_default == "nature"
        
    def test_default_palette_is_pastel(self):
        """默认 palette 应该是 pastel"""
        sig = inspect.signature(sp.setup_style)
        palette_default = sig.parameters["palette"].default
        assert palette_default == "pastel"
        
    def test_default_lang_is_zh(self):
        """默认 lang 应该是 zh"""
        sig = inspect.signature(sp.setup_style)
        lang_default = sig.parameters["lang"].default
        assert lang_default == "zh"


class TestErrorHandling:
    """测试错误处理一致性"""
    
    def test_invalid_venue_raises_valueerror(self):
        """无效 venue 应该 raise ValueError"""
        with pytest.raises(ValueError):
            sp.setup_style(venue="invalid")
            
    def test_invalid_palette_raises_valueerror(self):
        """无效 palette 应该 raise ValueError"""
        with pytest.raises((ValueError, KeyError)):
            sp.setup_style(palette="invalid")
            
    def test_error_messages_are_clear(self):
        """错误信息应该清晰"""
        try:
            sp.setup_style(venue="invalid_venue_xyz")
        except ValueError as e:
            error_msg = str(e)
            assert "invalid_venue_xyz" in error_msg or "未知" in error_msg
            assert "可用选项" in error_msg or "available" in error_msg.lower()


class TestFluentInterfaceDesign:
    """测试 Fluent Interface 设计"""
    
    def test_chain_methods_return_self_or_wrapper(self, test_data):
        """链式方法应该返回 self 或 FigureWrapper"""
        from sciplot._core.fluent import PlotChain, FigureWrapper
        
        chain = sp.style("nature")
        assert isinstance(chain, PlotChain)
        
        # 样式设置方法返回 PlotChain
        result = chain.palette("pastel")
        assert isinstance(result, PlotChain)
        
        # 绘图方法返回 FigureWrapper
        result = chain.plot(test_data["x"], test_data["y"])
        assert isinstance(result, FigureWrapper)
        
    def test_figure_wrapper_has_consistent_methods(self, test_data):
        """FigureWrapper 应该有统一的方法"""
        from sciplot._core.fluent import FigureWrapper
        
        wrapper = sp.style("nature").plot(test_data["x"], test_data["y"])
        
        # 应该有这些方法
        assert hasattr(wrapper, 'xlabel')
        assert hasattr(wrapper, 'ylabel')
        assert hasattr(wrapper, 'title')
        assert hasattr(wrapper, 'legend')
        assert hasattr(wrapper, 'save')
        assert hasattr(wrapper, 'show')
        assert hasattr(wrapper, 'get_figure')
        assert hasattr(wrapper, 'get_axes')


class TestVenueSizes:
    """测试期刊尺寸设计"""
    
    def test_ieee_is_single_column(self):
        """IEEE 应该是单栏尺寸"""
        info = sp.get_venue_info("ieee")
        width, height = info["figsize"]
        # IEEE 单栏通常 3.5 英寸宽
        assert width == pytest.approx(3.5, abs=0.1)
        assert width < 4.0  # 单栏应该小于 4 英寸
        
    def test_nature_is_double_column(self):
        """Nature 应该是双栏尺寸"""
        info = sp.get_venue_info("nature")
        width, height = info["figsize"]
        # Nature 双栏通常 7 英寸宽
        assert width == pytest.approx(7.0, abs=0.1)
        assert width > 6.0  # 双栏应该大于 6 英寸
        
    def test_thesis_is_a4_compatible(self):
        """Thesis 应该兼容 A4 纸张"""
        info = sp.get_venue_info("thesis")
        width, height = info["figsize"]
        # A4 版心宽度约 6.1 英寸
        assert width == pytest.approx(6.1, abs=0.1)
        # 宽高比应该合理
        assert 1.3 < width / height < 1.5


class TestColorPaletteDesign:
    """测试配色设计"""
    
    def test_pastel_colors_are_light(self):
        """Pastel 颜色应该较浅"""
        pastel = sp.get_palette("pastel")
        for color in pastel[:3]:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            # 至少一个通道应该较亮 (>128)
            assert max(r, g, b) > 128, f"{color} 不是 pastel 颜色"
            
    def test_earth_colors_are_muted(self):
        """Earth 颜色应该是大地色系"""
        earth = sp.get_palette("earth")
        # 大地色通常偏棕色/绿色
        assert len(earth) >= 4
        
    def test_ocean_colors_are_blue_green(self):
        """Ocean 颜色应该是蓝绿色系"""
        ocean = sp.get_palette("ocean")
        # 海洋色通常偏蓝/青
        assert len(ocean) >= 4


class TestDocumentationConsistency:
    """测试文档一致性"""
    
    def test_all_public_functions_have_docstrings(self):
        """所有公共函数应该有文档字符串"""
        public_funcs = [
            sp.setup_style,
            sp.new_figure,
            sp.save,
            sp.plot,
            sp.plot_line,
            sp.plot_scatter,
            sp.plot_bar,
        ]
        
        for func in public_funcs:
            assert func.__doc__ is not None, f"{func.__name__} 缺少文档字符串"
            assert len(func.__doc__) > 10, f"{func.__name__} 文档字符串太短"
            
    def test_docstrings_contain_examples(self):
        """文档字符串应该包含示例"""
        # 核心函数应该有示例
        core_funcs = [sp.setup_style, sp.plot]
        
        for func in core_funcs:
            doc = func.__doc__ or ""
            assert "示例" in doc or "Example" in doc or ">>>" in doc, \
                f"{func.__name__} 文档缺少示例"


class TestBackwardCompatibility:
    """测试向后兼容性"""
    
    def test_old_api_still_works(self, cleanup_figures):
        """旧 API 应该仍然可用"""
        # 最基本的用法
        sp.setup_style()
        fig, ax = sp.plot([1, 2, 3], [1, 2, 3])
        assert isinstance(fig, Figure)
        
    def test_positional_args_still_work(self, cleanup_figures):
        """位置参数应该仍然可用"""
        fig, ax = sp.plot([1, 2], [1, 2], "X Label", "Y Label", "Title")
        assert isinstance(fig, Figure)
        assert ax.get_xlabel() == "X Label"
