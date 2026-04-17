"""
论文尺寸验证测试 - 验证 Word 和 LaTeX 论文的图表尺寸标准
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
import sciplot as sp
from matplotlib.figure import Figure


class TestWordThesisSizes:
    """测试 Word 学位论文尺寸标准"""
    
    def test_thesis_figsize_width(self):
        """Thesis 宽度应该适合 A4 版心"""
        info = sp.get_venue_info("thesis")
        width, height = info["figsize"]
        
        # A4 纸张宽度 210mm ≈ 8.27 英寸
        # 版心宽度约 155mm ≈ 6.1 英寸
        assert width == pytest.approx(6.1, abs=0.1), \
            f"Thesis 宽度 {width} 不符合 A4 版心标准 (6.1英寸)"
        
    def test_thesis_figsize_height(self):
        """Thesis 高度应该合理"""
        info = sp.get_venue_info("thesis")
        width, height = info["figsize"]
        
        # 高度约 4.3 英寸，宽高比约 1.4:1
        assert height == pytest.approx(4.3, abs=0.1), \
            f"Thesis 高度 {height} 不符合标准 (4.3英寸)"
        
    def test_thesis_aspect_ratio(self):
        """Thesis 宽高比应该合理"""
        info = sp.get_venue_info("thesis")
        width, height = info["figsize"]
        ratio = width / height
        
        # 黄金比例约 1.618，常用比例 1.4-1.5
        assert 1.3 <= ratio <= 1.5, \
            f"Thesis 宽高比 {ratio:.2f} 不在合理范围 (1.3-1.5)"
        
    def test_thesis_fontsize(self):
        """Thesis 字号应该适合 Word 文档"""
        info = sp.get_venue_info("thesis")
        fontsize = info["fontsize"]
        
        # Word 论文字号通常 8-10pt
        assert 6 <= fontsize <= 10, \
            f"Thesis 字号 {fontsize}pt 不在合理范围 (6-10pt)"
        
    def test_thesis_single_column(self, cleanup_figures):
        """Thesis 单栏图尺寸"""
        sp.setup_style("thesis")
        fig, ax = sp.new_figure("thesis")
        
        assert fig.get_figwidth() == pytest.approx(6.1, abs=0.1)
        assert fig.get_figheight() == pytest.approx(4.3, abs=0.1)
        
    def test_thesis_double_column(self, cleanup_figures):
        """Thesis 双栏图尺寸（每个子图）"""
        sp.setup_style("thesis")
        fig, axes = sp.paper_subplots(1, 2, venue="thesis")
        
        # 总宽度应该还是 6.1 英寸
        assert fig.get_figwidth() == pytest.approx(6.1, abs=0.1)
        # 双栏图高度可能调整以适应布局
        assert fig.get_figheight() > 2.0  # 至少合理高度


class TestLaTeXPaperSizes:
    """测试 LaTeX 论文字尺寸标准"""
    
    def test_ieee_single_column_width(self):
        """IEEE 单栏宽度"""
        info = sp.get_venue_info("ieee")
        width, height = info["figsize"]
        
        # IEEE 单栏 3.5 英寸
        assert width == pytest.approx(3.5, abs=0.1), \
            f"IEEE 宽度 {width} 不符合标准 (3.5英寸)"
        
    def test_ieee_single_column_height(self):
        """IEEE 单栏高度"""
        info = sp.get_venue_info("ieee")
        width, height = info["figsize"]
        
        # IEEE 单栏高度 3.0 英寸
        assert height == pytest.approx(3.0, abs=0.1), \
            f"IEEE 高度 {height} 不符合标准 (3.0英寸)"
        
    def test_ieee_aspect_ratio(self):
        """IEEE 宽高比"""
        info = sp.get_venue_info("ieee")
        width, height = info["figsize"]
        ratio = width / height
        
        # IEEE 约 1.17:1
        assert 1.1 <= ratio <= 1.3, \
            f"IEEE 宽高比 {ratio:.2f} 不在合理范围"
        
    def test_ieee_fontsize(self):
        """IEEE 字号"""
        info = sp.get_venue_info("ieee")
        fontsize = info["fontsize"]
        
        # IEEE 字号通常 8pt
        assert 6 <= fontsize <= 10, \
            f"IEEE 字号 {fontsize}pt 不在合理范围"
        
    def test_nature_full_width(self):
        """Nature 全宽图尺寸"""
        info = sp.get_venue_info("nature")
        width, height = info["figsize"]
        
        # Nature 双栏全宽 7.0 英寸
        assert width == pytest.approx(7.0, abs=0.1), \
            f"Nature 宽度 {width} 不符合标准 (7.0英寸)"
        assert height == pytest.approx(5.0, abs=0.1), \
            f"Nature 高度 {height} 不符合标准 (5.0英寸)"
        
    def test_nature_aspect_ratio(self):
        """Nature 宽高比"""
        info = sp.get_venue_info("nature")
        width, height = info["figsize"]
        ratio = width / height
        
        # Nature 约 1.4:1
        assert 1.3 <= ratio <= 1.5, \
            f"Nature 宽高比 {ratio:.2f} 不在合理范围"
        
    def test_aps_single_column(self):
        """APS 单栏尺寸"""
        info = sp.get_venue_info("aps")
        width, height = info["figsize"]
        
        # APS Physical Review 单栏 3.4 英寸
        assert width == pytest.approx(3.4, abs=0.1), \
            f"APS 宽度 {width} 不符合标准 (3.4英寸)"
        assert height == pytest.approx(2.8, abs=0.1), \
            f"APS 高度 {height} 不符合标准 (2.8英寸)"
        
    def test_springer_sizes(self):
        """Springer 尺寸"""
        info = sp.get_venue_info("springer")
        width, height = info["figsize"]
        
        # Springer 通常 6.0 x 4.5 英寸
        assert width == pytest.approx(6.0, abs=0.1)
        assert height == pytest.approx(4.5, abs=0.1)


class TestFontSizeStandards:
    """测试字号标准"""
    
    def test_fontsize_reduced_by_2pt(self):
        """验证字号已减小 2pt"""
        # 原始字号: nature=10, ieee=8, thesis=10
        # 新字号: nature=8, ieee=6, thesis=8
        
        nature_info = sp.get_venue_info("nature")
        ieee_info = sp.get_venue_info("ieee")
        thesis_info = sp.get_venue_info("thesis")
        
        assert nature_info["fontsize"] == 8, "Nature 字号应该为 8pt"
        assert ieee_info["fontsize"] == 6, "IEEE 字号应该为 6pt"
        assert thesis_info["fontsize"] == 8, "Thesis 字号应该为 8pt"
        
    def test_minimum_fontsize(self):
        """最小字号不应该太小"""
        venues = sp.list_venues()
        
        for venue in venues:
            info = sp.get_venue_info(venue)
            fontsize = info["fontsize"]
            
            # 字号不应该小于 6pt（可读性考虑）
            assert fontsize >= 6, \
                f"{venue} 字号 {fontsize}pt 太小，最小应为 6pt"
            
    def test_maximum_fontsize(self):
        """最大字号不应该太大"""
        venues = sp.list_venues()
        
        for venue in venues:
            info = sp.get_venue_info(venue)
            fontsize = info["fontsize"]
            
            # 字号不应该大于 14pt
            assert fontsize <= 14, \
                f"{venue} 字号 {fontsize}pt 太大，最大应为 14pt"


class TestDPIStandards:
    """测试 DPI 标准"""
    
    def test_word_dpi_1200(self, temp_dir, cleanup_figures):
        """Word 论文应该使用 1200 DPI"""
        sp.setup_style("thesis")
        fig, ax = sp.plot([1, 2], [1, 2])
        
        output_path = temp_dir / "word_1200dpi"
        paths = sp.save(fig, output_path, formats=("png",), dpi=1200)
        
        assert paths[0].exists()
        
    def test_latex_dpi_default(self, temp_dir, cleanup_figures):
        """LaTeX 论文使用默认 DPI"""
        sp.setup_style("ieee")
        fig, ax = sp.plot([1, 2], [1, 2])
        
        # PDF 不需要指定 DPI
        output_path = temp_dir / "latex_pdf"
        paths = sp.save(fig, output_path, formats=("pdf",))
        
        assert paths[0].exists()


class TestFormatStandards:
    """测试格式标准"""
    
    def test_word_png_format(self, temp_dir, cleanup_figures):
        """Word 论文应该使用 PNG 格式"""
        sp.setup_style("thesis")
        fig, ax = sp.plot([1, 2], [1, 2])
        
        output_path = temp_dir / "word_figure"
        paths = sp.save(fig, output_path, formats=("png",), dpi=1200)
        
        assert paths[0].suffix == ".png"
        
    def test_latex_pdf_format(self, temp_dir, cleanup_figures):
        """LaTeX 论文应该使用 PDF 格式"""
        sp.setup_style("ieee")
        fig, ax = sp.plot([1, 2], [1, 2])
        
        output_path = temp_dir / "latex_figure"
        paths = sp.save(fig, output_path, formats=("pdf",))
        
        assert paths[0].suffix == ".pdf"
        
    def test_multi_format_output(self, temp_dir, cleanup_figures):
        """多格式输出"""
        sp.setup_style("nature")
        fig, ax = sp.plot([1, 2], [1, 2])
        
        output_path = temp_dir / "multi_format"
        paths = sp.save(fig, output_path, formats=("png", "pdf", "svg"))
        
        assert len(paths) == 3
        extensions = [p.suffix for p in paths]
        assert ".png" in extensions
        assert ".pdf" in extensions
        assert ".svg" in extensions


class TestPaperCompatibility:
    """测试论文兼容性"""
    
    def test_all_sizes_reasonable(self):
        """所有尺寸应该在合理范围内"""
        venues = sp.list_venues()
        
        for venue in venues:
            info = sp.get_venue_info(venue)
            width, height = info["figsize"]
            
            # 宽度应该在 2-10 英寸之间
            assert 2.0 <= width <= 10.0, \
                f"{venue} 宽度 {width} 不在合理范围"
            
            # 高度应该在 2-8 英寸之间
            assert 2.0 <= height <= 8.0, \
                f"{venue} 高度 {height} 不在合理范围"
            
            # 宽高比应该在 0.5-2.0 之间
            ratio = width / height
            assert 0.5 <= ratio <= 2.0, \
                f"{venue} 宽高比 {ratio:.2f} 不在合理范围"
                
    def test_no_extreme_sizes(self):
        """不应该有极端尺寸"""
        venues = sp.list_venues()
        
        for venue in venues:
            info = sp.get_venue_info(venue)
            width, height = info["figsize"]
            
            # 不应该有正方形（太特殊）
            ratio = width / height
            assert not (0.95 <= ratio <= 1.05), \
                f"{venue} 接近正方形，可能不是标准尺寸"
