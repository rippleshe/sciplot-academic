"""
Round-47 tests for hero_layout (不对称主面板 + 卫星布局).
"""

from __future__ import annotations

import numpy as np
import pytest
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import sciplot as sp


def test_hero_right_basic(cleanup_figures):
    """hero_right：左侧主面板 + 右侧 2×1 卫星。"""
    result = sp.hero_layout("hero_right", venue="thesis")
    fig = result.fig
    assert isinstance(fig, Figure)
    assert isinstance(result.ax_hero, Axes)
    assert len(result.satellites) == 2
    # 解包兼容
    fig2, gs = result
    assert fig2 is fig


def test_hero_top_basic(cleanup_figures):
    """hero_top：顶部通栏 + 底部 3 列。"""
    result = sp.hero_layout("hero_top", venue="nature")
    assert len(result.satellites) == 3
    # 主面板位置应横跨 3 列
    spec = result.ax_hero.get_subplotspec()
    assert spec.num2 - spec.num1 + 1 == 3


def test_hub_spoke_basic(cleanup_figures):
    """hub_spoke：中心 + 四向卫星。"""
    result = sp.hero_layout("hub_spoke")
    assert len(result.satellites) == 4


def test_hero_invalid_template(cleanup_figures):
    with pytest.raises(ValueError, match="未知 hero template"):
        sp.hero_layout("nonexistent")


def test_hero_satellite_index(cleanup_figures):
    """ax_satellite 索引访问与越界检查。"""
    result = sp.hero_layout("hero_right")
    ax0 = result.ax_satellite(0)
    assert isinstance(ax0, Axes)
    with pytest.raises(IndexError):
        result.ax_satellite(5)


def test_hero_plain_gridspec_no_hero(cleanup_figures):
    """普通 create_gridspec 结果无主面板属性（防误用）。"""
    result = sp.create_gridspec(2, 2)
    with pytest.raises(AttributeError, match="hero_layout"):
        result.ax_hero


def test_hero_panel_labels(cleanup_figures):
    """面板标签默认 8pt 加粗，(a) 是主面板。"""
    result = sp.hero_layout("hero_right")
    hero_texts = [t.get_text() for t in result.ax_hero.texts]
    assert "(a)" in hero_texts
    # 卫星标签 (b) (c)
    sat_texts = [t.get_text() for s in result.satellites for t in s.texts]
    assert "(b)" in sat_texts and "(c)" in sat_texts


def test_hero_no_labels(cleanup_figures):
    result = sp.hero_layout("hero_right", panel_labels=False)
    texts = [t.get_text() for s in result.satellites for t in s.texts]
    texts += [t.get_text() for t in result.ax_hero.texts]
    assert all(not t.startswith("(a)") for t in texts)


def test_hero_list_templates(cleanup_figures):
    templates = sp.list_hero_templates()
    assert "hero_right" in templates
    assert "hero_top" in templates
    assert "hub_spoke" in templates
    assert "description" in templates["hero_right"]
    assert callable(sp.hero_layout)
    assert "hero_layout" in sp.__all__


def test_hero_with_plots(tmp_path, cleanup_figures):
    """Hero 布局实际画图并保存。"""
    result = sp.hero_layout("hero_right", venue="thesis")
    rng = np.random.default_rng(7)
    x = np.linspace(0, 10, 80)
    result.ax_hero.plot(x, np.sin(x), color="#2E6DA4")
    result.ax_satellite(0).hist(rng.normal(0, 1, 200), bins=20)
    result.ax_satellite(1).scatter(rng.normal(0, 1, 40), rng.normal(0, 1, 40), s=12)
    paths = sp.save(result.fig, tmp_path / "hero", formats=("png",))
    assert paths[0].exists()
