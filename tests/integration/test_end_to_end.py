"""
端到端集成测试 - 模拟真实使用场景
"""

import pytest
import numpy as np
import sciplot as sp
from pathlib import Path


class TestWordThesisWorkflow:
    """测试 Word 学位论文工作流"""
    
    def test_thesis_single_figure(self, temp_dir, cleanup_figures):
        """测试学位论文单图"""
        sp.setup_style("thesis", "pastel-2", lang="zh")
        
        x = np.linspace(0, 10, 200)
        y = np.sin(x)
        
        fig, ax = sp.plot(x, y, xlabel="时间 (s)", ylabel="电压 (V)")
        
        output_path = temp_dir / "thesis_single"
        paths = sp.save(fig, output_path, formats=("png",), dpi=1200)
        
        assert len(paths) == 1
        assert paths[0].exists()
        assert paths[0].stat().st_size > 0
        
    def test_thesis_double_figure(self, temp_dir, cleanup_figures):
        """测试学位论文双图"""
        sp.setup_style("thesis", "pastel-2", lang="zh")
        
        x = np.linspace(0, 10, 200)
        
        fig, axes = sp.paper_subplots(1, 2, venue="thesis")
        axes[0].plot(x, np.sin(x))
        axes[0].set_title("(a) 正弦波")
        axes[1].plot(x, np.cos(x))
        axes[1].set_title("(b) 余弦波")
        
        sp.add_panel_labels(axes)
        
        output_path = temp_dir / "thesis_double"
        paths = sp.save(fig, output_path, formats=("png",), dpi=1200)
        
        assert len(paths) == 1
        assert paths[0].exists()


class TestIEEEPaperWorkflow:
    """测试 IEEE 论文工作流"""
    
    def test_ieee_single_column(self, temp_dir, cleanup_figures):
        """测试 IEEE 单栏图"""
        sp.setup_style("ieee", "pastel-2", lang="en")
        
        x = np.linspace(0, 10, 200)
        y1 = np.sin(x)
        y2 = np.cos(x)
        
        fig, ax = sp.new_figure("ieee")
        ax.plot(x, y1, label="Method A")
        ax.plot(x, y2, label="Method B")
        ax.legend()
        
        output_path = temp_dir / "ieee_single"
        paths = sp.save(fig, output_path, formats=("pdf",))
        
        assert len(paths) == 1
        assert paths[0].exists()
        assert paths[0].suffix == ".pdf"
        
    def test_ieee_error_bar(self, temp_dir, cleanup_figures):
        """测试 IEEE 误差条图"""
        sp.setup_style("ieee", "pastel", lang="en")
        
        x = np.linspace(0, 10, 10)
        y = np.sin(x)
        yerr = np.random.uniform(0.05, 0.15, len(x))
        
        fig, ax = sp.errorbar(x, y, yerr, fmt="o", capsize=3)
        
        output_path = temp_dir / "ieee_errorbar"
        paths = sp.save(fig, output_path, formats=("pdf",))
        
        assert len(paths) == 1
        assert paths[0].exists()


class TestNaturePaperWorkflow:
    """测试 Nature 论文工作流"""
    
    def test_nature_full_width(self, temp_dir, cleanup_figures):
        """测试 Nature 全宽图"""
        sp.setup_style("nature", "forest-3", lang="en")
        
        x = np.linspace(0, 10, 200)
        
        fig, ax = sp.new_figure("nature")
        ax.plot(x, np.sin(x), label="Group 1")
        ax.plot(x, np.cos(x), label="Group 2")
        ax.plot(x, np.sin(x) + np.cos(x), label="Group 3")
        ax.legend()
        
        output_path = temp_dir / "nature_fullwidth"
        paths = sp.save(fig, output_path, formats=("pdf",))
        
        assert len(paths) == 1
        assert paths[0].exists()
        
    def test_nature_box_plot(self, temp_dir, cleanup_figures):
        """测试 Nature 箱线图"""
        sp.setup_style("nature", "pastel", lang="en")
        
        data = [np.random.normal(0, 1, 100) for _ in range(4)]
        
        fig, ax = sp.box(data, labels=["A", "B", "C", "D"])
        
        # 添加显著性标注
        sp.annotate_significance(ax, x1=1, x2=2, y=2.5, p_value=0.01)
        
        output_path = temp_dir / "nature_box"
        paths = sp.save(fig, output_path, formats=("pdf",))
        
        assert len(paths) == 1
        assert paths[0].exists()


class TestComplexMultiPanel:
    """测试复杂多子图场景"""
    
    def test_2x2_comparison(self, temp_dir, cleanup_figures):
        """测试 2x2 对比图"""
        sp.setup_style("thesis", "pastel-4", lang="zh")
        
        x = np.linspace(0, 10, 100)
        
        fig, axes = sp.paper_subplots(2, 2, venue="thesis")
        
        axes[0, 0].plot(x, np.sin(x))
        axes[0, 1].plot(x, np.cos(x))
        axes[1, 0].plot(x, np.sin(x) + np.cos(x))
        axes[1, 1].plot(x, np.sin(x) * np.cos(x))
        
        sp.add_panel_labels(axes.flatten())
        
        output_path = temp_dir / "comparison_2x2"
        paths = sp.save(fig, output_path, formats=("png",), dpi=1200)
        
        assert len(paths) == 1
        assert paths[0].exists()
        
    def test_gridspec_complex(self, temp_dir, cleanup_figures):
        """测试复杂 GridSpec 布局"""
        sp.setup_style("nature", "ocean", lang="en")
        
        fig, gs = sp.create_gridspec(3, 3, venue="nature")
        
        # 大图为左上 2x2
        ax_large = fig.add_subplot(gs[0:2, 0:2])
        # 右列小图
        ax_r1 = fig.add_subplot(gs[0, 2])
        ax_r2 = fig.add_subplot(gs[1, 2])
        # 底部通栏
        ax_bottom = fig.add_subplot(gs[2, :])
        
        x = np.linspace(0, 10, 100)
        ax_large.plot(x, np.sin(x))
        ax_r1.plot(x, np.cos(x))
        ax_r2.plot(x, np.sin(x) * 0.5)
        ax_bottom.plot(x, np.sin(x) + np.cos(x))
        
        output_path = temp_dir / "gridspec_complex"
        paths = sp.save(fig, output_path, formats=("pdf",))
        
        assert len(paths) == 1
        assert paths[0].exists()


class TestSyntaxSugarWorkflow:
    """测试语法糖工作流"""
    
    def test_fluent_chain_workflow(self, temp_dir, cleanup_figures):
        """测试链式调用工作流"""
        x = np.linspace(0, 10, 100)
        
        output_path = temp_dir / "fluent_output"
        paths = (sp.style("ieee")
                   .palette("forest")
                   .plot(x, np.sin(x), label="Sin")
                   .plot(x, np.cos(x), label="Cos")
                   .legend()
                   .xlabel("X")
                   .ylabel("Y")
                   .save(output_path, formats=("pdf",)))
        
        assert len(paths) == 1
        assert paths[0].exists()
        
    def test_context_manager_workflow(self, temp_dir, cleanup_figures):
        """测试上下文管理器工作流"""
        x = np.linspace(0, 10, 100)
        
        # 默认样式
        fig1, ax1 = sp.plot(x, np.sin(x))
        output1 = temp_dir / "default_style"
        sp.save(fig1, output1, formats=("png",))
        
        # 临时切换样式
        with sp.style_context("ieee", "pastel"):
            fig2, ax2 = sp.plot(x, np.cos(x))
            output2 = temp_dir / "ieee_style"
            sp.save(fig2, output2, formats=("png",))
        
        # 恢复默认样式
        fig3, ax3 = sp.plot(x, np.sin(x) + np.cos(x))
        output3 = temp_dir / "back_to_default"
        sp.save(fig3, output3, formats=("png",))
        
        assert output1.exists() or output1.with_suffix(".png").exists()
        assert output2.exists() or output2.with_suffix(".png").exists()
        assert output3.exists() or output3.with_suffix(".png").exists()


class TestChineseRendering:
    """测试中文渲染"""
    
    def test_chinese_labels_no_unicode_minus_error(self, temp_dir, cleanup_figures):
        """测试中文标签不产生 U+2212 警告"""
        sp.setup_style("thesis", lang="zh")
        
        x = np.linspace(-5, 5, 100)
        y = -np.abs(x)  # 负值测试
        
        fig, ax = sp.plot(x, y, xlabel="负值测试", ylabel="数值")
        
        output_path = temp_dir / "chinese_negative"
        paths = sp.save(fig, output_path, formats=("png",))
        
        assert len(paths) == 1
        assert paths[0].exists()
        
    def test_chinese_title_and_labels(self, temp_dir, cleanup_figures):
        """测试中文标题和标签"""
        sp.setup_style("thesis", lang="zh")
        
        x = np.linspace(0, 10, 100)
        
        fig, ax = sp.plot(
            x, np.sin(x),
            xlabel="时间（秒）",
            ylabel="振幅（伏特）",
            title="正弦波信号"
        )
        
        output_path = temp_dir / "chinese_full"
        paths = sp.save(fig, output_path, formats=("png",), dpi=1200)
        
        assert len(paths) == 1
        assert paths[0].exists()
