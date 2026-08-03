"""
Round-44 tests for plot_bump & plot_alluvial (排名变化 + 冲积图).
"""

from __future__ import annotations

import numpy as np
import pytest
from matplotlib.axes import Axes

import sciplot as sp


# ── plot_bump ──────────────────────────────────────────────────

def test_bump_basic(cleanup_figures):
    """基础排名变化图：y 轴倒置（排名 1 在顶部）。"""
    fig, ax = sp.plot_bump(
        labels=["A", "B", "C"],
        values=[[85, 88, 90], [90, 85, 82], [78, 92, 95]],
        time_points=["T1", "T2", "T3"],
    )
    assert isinstance(ax, Axes)
    ylim = ax.get_ylim()
    assert ylim[0] > ylim[1]  # invert_yaxis


def test_bump_line_count(cleanup_figures):
    """每个对象一条曲线。"""
    fig, ax = sp.plot_bump(
        labels=["A", "B", "C", "D"],
        values=np.random.default_rng(0).uniform(50, 100, (4, 6)),
    )
    assert len(ax.lines) == 4


def test_bump_highlight(cleanup_figures):
    """高亮对象：其余曲线置灰。"""
    fig, ax = sp.plot_bump(
        labels=["A", "B", "C"],
        values=[[85, 88, 90], [90, 85, 82], [78, 92, 95]],
        highlight="C",
    )
    colors = [l.get_color() for l in ax.lines]
    assert "#C0392B" in colors  # 高亮色
    assert "#9AA5B1" in colors  # 置灰色


def test_bump_highlight_invalid(cleanup_figures):
    with pytest.raises(ValueError, match="highlight"):
        sp.plot_bump(labels=["A"], values=[[1, 2]], highlight="X")


def test_bump_validation(cleanup_figures):
    """labels 长度与 values 行数不一致时报错。"""
    with pytest.raises(ValueError, match="labels"):
        sp.plot_bump(labels=["A", "B"], values=[[1, 2, 3]])


def test_bump_1d_values_raises(cleanup_figures):
    with pytest.raises(ValueError, match="二维"):
        sp.plot_bump(labels=["A"], values=[1, 2, 3])


def test_bump_save_png(tmp_path, cleanup_figures):
    fig, ax = sp.plot_bump(
        labels=["A", "B"], values=[[10, 8, 9], [9, 10, 8]],
        time_points=["P1", "P2", "P3"], show_end_labels=True,
    )
    paths = sp.save(fig, tmp_path / "bump", formats=("png",))
    assert paths[0].exists()


# ── plot_alluvial ──────────────────────────────────────────────

def test_alluvial_basic(cleanup_figures):
    """三阶段冲积图：返回 PlotResult。"""
    result = sp.plot_alluvial(
        stages=[["A", "B"], ["X", "Y", "Z"], ["P", "Q"]],
        flows=[
            [(0, 0, 60), (0, 1, 10), (1, 0, 40), (1, 2, 60)],
            [(0, 0, 70), (1, 1, 10), (2, 1, 20), (2, 0, 40)],
        ],
    )
    fig, ax = result
    assert isinstance(ax, Axes)


def test_alluvial_two_stages(cleanup_figures):
    """两阶段冲积图。"""
    fig, ax = sp.plot_alluvial(
        stages=[["对照", "治疗"], ["改善", "无变化"]],
        flows=[(0, 0, 30), (0, 1, 10), (1, 0, 45), (1, 1, 15)],
    )
    # 流带 patch 数量 = 4
    from matplotlib.patches import PathPatch

    patches = [p for p in ax.patches if isinstance(p, PathPatch)]
    assert len(patches) >= 4


def test_alluvial_validation_stages(cleanup_figures):
    """少于两个阶段报错。"""
    with pytest.raises(ValueError, match="至少需要两个阶段"):
        sp.plot_alluvial(stages=[["A"]], flows=[])


def test_alluvial_validation_flows_count(cleanup_figures):
    """flows 组数必须为阶段数减一（嵌套列表形式下）。"""
    with pytest.raises(ValueError, match="阶段数减一"):
        sp.plot_alluvial(
            stages=[["A", "B"], ["X", "Y"], ["P"]],
            flows=[[(0, 0, 10), (1, 0, 5)]],  # 三阶段应有两组
        )


def test_alluvial_validation_index(cleanup_figures):
    """源索引越界报错。"""
    with pytest.raises(ValueError, match="源索引"):
        sp.plot_alluvial(
            stages=[["A", "B"], ["X", "Y"]],
            flows=[(2, 0, 10)],
        )


def test_alluvial_validation_negative_flow(cleanup_figures):
    with pytest.raises(ValueError, match="非负"):
        sp.plot_alluvial(
            stages=[["A"], ["X"]],
            flows=[(0, 0, -1)],
        )


def test_alluvial_node_colors_mismatch(cleanup_figures):
    with pytest.raises(ValueError, match="node_colors"):
        sp.plot_alluvial(
            stages=[["A", "B"], ["X"]],
            flows=[(0, 0, 1), (1, 0, 2)],
            node_colors=["#111111"],
        )


def test_alluvial_save_png(tmp_path, cleanup_figures):
    fig, ax = sp.plot_alluvial(
        stages=[["A", "B"], ["X", "Y"]],
        flows=[(0, 0, 30), (0, 1, 10), (1, 0, 20), (1, 1, 40)],
    )
    paths = sp.save(fig, tmp_path / "alluvial", formats=("png",))
    assert paths[0].exists()


# ── 别名与导出 ────────────────────────────────────────────────

def test_aliases_exported(cleanup_figures):
    assert callable(sp.plot_bump)
    assert callable(sp.plot_alluvial)
    assert callable(sp.bump)
    assert callable(sp.alluvial)
    assert "plot_bump" in sp.__all__
    assert "plot_alluvial" in sp.__all__
    assert "bump" in sp.__all__
    assert "alluvial" in sp.__all__
