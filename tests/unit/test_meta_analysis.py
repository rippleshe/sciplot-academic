"""
Round-43 tests for plot_forest & plot_funnel (Meta 分析标配图表).
"""

from __future__ import annotations

import numpy as np
import pytest
from matplotlib.axes import Axes

import sciplot as sp


# ── plot_forest ────────────────────────────────────────────────

def test_forest_basic(cleanup_figures):
    """基础森林图：返回 PlotResult，可解包。"""
    result = sp.plot_forest(
        effect=[0.8, 0.5, 1.1],
        ci_low=[0.3, 0.1, 0.7],
        ci_high=[1.3, 0.9, 1.5],
        labels=["研究 1", "研究 2", "研究 3"],
    )
    fig, ax = result
    assert isinstance(ax, Axes)
    # 三个散点（效应量标记）
    assert len(ax.collections) >= 1


def test_forest_validation_length_mismatch(cleanup_figures):
    with pytest.raises(ValueError, match="不一致"):
        sp.plot_forest(effect=[1, 2], ci_low=[0, 0], ci_high=[2, 2, 3])


def test_forest_validation_ci_order(cleanup_figures):
    with pytest.raises(ValueError, match="ci_low"):
        sp.plot_forest(effect=[1], ci_low=[2], ci_high=[0])


def test_forest_empty_raises(cleanup_figures):
    with pytest.raises(ValueError, match="不能为空"):
        sp.plot_forest(effect=[], ci_low=[], ci_high=[])


def test_forest_summary_diamond(cleanup_figures):
    """summary 参数绘制合并菱形。"""
    fig, ax = sp.plot_forest(
        effect=[0.8, 0.5],
        ci_low=[0.3, 0.1],
        ci_high=[1.3, 0.9],
        summary=(0.65, 0.45, 0.85),
    )
    # 菱形 = 一个 Polygon patch
    from matplotlib.patches import Polygon

    polys = [p for p in ax.patches if isinstance(p, Polygon)]
    assert len(polys) == 1
    # 元数据记录 summary
    assert fig is not None


def test_forest_reference_line(cleanup_figures):
    """参考线默认 0，可自定义。"""
    fig, ax = sp.plot_forest(effect=[0.5], ci_low=[0.2], ci_high=[0.8], reference=1.0)
    lines = [l for l in ax.lines if l.get_linestyle() == "--"]
    assert len(lines) >= 1


def test_forest_labels_mismatch(cleanup_figures):
    with pytest.raises(ValueError, match="labels"):
        sp.plot_forest(effect=[1, 2], ci_low=[0, 0], ci_high=[2, 2], labels=["a"])


# ── plot_funnel ────────────────────────────────────────────────

def test_funnel_basic(cleanup_figures):
    """基础漏斗图：y 轴倒置（SE 大在下）。"""
    fig, ax = sp.plot_funnel(
        effect=[0.8, 0.5, 1.1, 0.6, 0.9],
        se=[0.25, 0.30, 0.20, 0.28, 0.22],
    )
    assert isinstance(ax, Axes)
    ylim = ax.get_ylim()
    # invert_yaxis：ylim[0] > ylim[1]
    assert ylim[0] > ylim[1]


def test_funnel_validation_se_positive(cleanup_figures):
    with pytest.raises(ValueError, match="正数"):
        sp.plot_funnel(effect=[1, 2], se=[0.1, -0.2])


def test_funnel_validation_ci_pair(cleanup_figures):
    with pytest.raises(ValueError, match="同时提供"):
        sp.plot_funnel(effect=[1], se=[0.1], ci_low=[0.5])


def test_funnel_reference_weighted_mean(cleanup_figures):
    """未指定 reference 时使用逆方差加权均值。"""
    effect = np.array([1.0, 2.0])
    se = np.array([1.0, 3.0])
    w = 1.0 / se**2
    expected = float(np.sum(w * effect) / np.sum(w))
    fig, ax = sp.plot_funnel(effect=effect, se=se, show_ci_triangle=False,
                             show_legend=False)
    lines = [l for l in ax.lines if l.get_linestyle() == "--"]
    assert len(lines) == 1
    xdata = lines[0].get_xdata()
    assert abs(xdata[0] - expected) < 1e-9


def test_funnel_empty_raises(cleanup_figures):
    with pytest.raises(ValueError, match="不能为空"):
        sp.plot_funnel(effect=[], se=[])


# ── 别名与导出 ────────────────────────────────────────────────

def test_aliases_exported(cleanup_figures):
    """森林图/漏斗图有完整名称与简洁别名，且已列入 __all__。"""
    assert callable(sp.plot_forest)
    assert callable(sp.plot_funnel)
    assert callable(sp.forest)
    assert callable(sp.funnel)
    assert "plot_forest" in sp.__all__
    assert "plot_funnel" in sp.__all__
    assert "forest" in sp.__all__
    assert "funnel" in sp.__all__


def test_forest_save_png(tmp_path, cleanup_figures):
    """森林图可正常保存。"""
    fig, ax = sp.plot_forest(
        effect=[0.8, 0.5, 1.1], ci_low=[0.3, 0.1, 0.7], ci_high=[1.3, 0.9, 1.5],
        labels=["A", "B", "C"], summary=(0.75, 0.55, 0.95),
    )
    paths = sp.save(fig, tmp_path / "forest", formats=("png",))
    assert paths[0].exists()
