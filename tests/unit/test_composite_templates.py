"""
Round-42 tests for composite figure templates (figure_panels template=).

验证 Nature 级复合图模板系统：
- 模板名解析与错误处理
- 模板网格结构（nrows/ncols/widths/heights/sharex/sharey）
- 8pt 面板标签规范
- 手动参数覆盖模板值
- 向后兼容（template=None 行为不变）
"""

from __future__ import annotations

import numpy as np
import pytest
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import sciplot as sp


def test_list_composite_templates_exported(cleanup_figures):
    """模板注册表可通过包入口查询。"""
    templates = sp.list_composite_templates()
    assert callable(sp.list_composite_templates)
    assert "list_composite_templates" in sp.__all__
    for name in ("condition_matrix", "time_march", "comparative",
                 "pipeline", "triptych"):
        assert name in templates
        assert "description" in templates[name]
        assert "nrows" in templates[name]
        assert "ncols" in templates[name]


def test_template_condition_matrix_shape(cleanup_figures):
    """条件矩阵模板：2×3，共享 y 轴。"""
    fig, axes = sp.figure_panels(template="condition_matrix")
    assert isinstance(fig, Figure)
    assert axes.shape == (2, 3)
    # 共享 y 轴
    assert axes[0, 0].get_shared_y_axes().joined(axes[0, 0], axes[1, 0])


def test_template_comparative_shape(cleanup_figures):
    """对照双列模板：1×2，共享 y 轴。"""
    fig, axes = sp.figure_panels(template="comparative", venue="thesis")
    assert axes.shape == (2,)
    assert axes[0].get_shared_y_axes().joined(axes[0], axes[1])


def test_template_pipeline_shape(cleanup_figures):
    """流水线模板：1×5。"""
    fig, axes = sp.figure_panels(template="pipeline")
    assert axes.shape == (5,)


def test_template_triptych_heights(cleanup_figures):
    """临床三联画模板：3×2，行高比 [1, 0.9, 0.7]。"""
    fig, axes = sp.figure_panels(template="triptych")
    assert axes.shape == (3, 2)
    gs = axes[0, 0].get_subplotspec().get_gridspec()
    heights = gs.get_height_ratios()
    assert len(heights) == 3
    assert abs(heights[0] / heights[2] - 1.0 / 0.7) < 1e-9


def test_template_panel_labels_8pt(cleanup_figures):
    """模板自动加 (a) (b)… 标签，且字号为 8pt（Nature 规范）。"""
    fig, axes = sp.figure_panels(template="time_march")
    texts = [t for a in axes.flat for t in a.texts]
    labels = [t.get_text() for t in texts]
    assert "(a)" in labels and "(b)" in labels and "(d)" in labels
    # 标签加粗且 8pt
    label_texts = [t for t in texts if t.get_text() in {"(a)", "(b)", "(c)", "(d)"}]
    assert len(label_texts) == 4
    for t in label_texts:
        assert t.get_fontsize() == 8
        assert t.get_fontweight() == "bold"


def test_template_manual_override(cleanup_figures):
    """显式参数覆盖模板值（如自定义 figsize 与 wspace）。"""
    fig, axes = sp.figure_panels(template="comparative", wspace=0.5)
    gs = axes[0].get_subplotspec().get_gridspec()
    assert gs.wspace == pytest.approx(0.5)


def test_template_invalid_raises(cleanup_figures):
    """未知模板名报错并列出可用选项。"""
    with pytest.raises(ValueError, match="未知 template"):
        sp.figure_panels(template="nonexistent")
    with pytest.raises(ValueError, match="condition_matrix"):
        sp.figure_panels(template="nonexistent")


def test_template_none_backward_compatible(cleanup_figures):
    """template=None 保持原有手动网格行为（含默认标签字号继承）。"""
    fig, axes = sp.figure_panels(2, 2, venue="thesis")
    assert axes.shape == (2, 2)
    texts = [t.get_text() for a in axes.flat for t in a.texts]
    assert "(a)" in texts and "(d)" in texts


def test_template_with_plots(tmp_path, cleanup_figures):
    """模板布局可直接作图画图并保存。"""
    fig, axes = sp.figure_panels(template="condition_matrix", venue="thesis")
    rng = np.random.default_rng(3)
    x = np.linspace(0, 10, 40)
    for ax in axes.flat:
        ax.plot(x, np.sin(x) + rng.normal(0, 0.05, 40))
    paths = sp.save(fig, tmp_path / "tmpl_matrix", formats=("png",))
    assert paths[0].exists()


def test_template_label_size_override(cleanup_figures):
    """label_size 显式参数覆盖模板默认 8pt。"""
    fig, axes = sp.figure_panels(template="comparative", label_size=10)
    texts = [t for a in axes for t in a.texts if t.get_text() in {"(a)", "(b)"}]
    assert all(t.get_fontsize() == 10 for t in texts)


def test_template_panel_labels_disabled(cleanup_figures):
    """panel_labels=False 时模板不加标签。"""
    fig, axes = sp.figure_panels(template="comparative", panel_labels=False)
    texts = [t.get_text() for a in axes for t in a.texts]
    assert all(not t.startswith("(a)") for t in texts)
