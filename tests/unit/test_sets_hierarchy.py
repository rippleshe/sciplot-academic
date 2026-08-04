"""
Round-45 tests for plot_sunburst & plot_upset (分层占比 + 集合交集).
"""

from __future__ import annotations

import numpy as np
import pytest
from matplotlib.axes import Axes

import sciplot as sp


# ── plot_sunburst ──────────────────────────────────────────────

def test_sunburst_basic(cleanup_figures):
    """两层旭日图：返回 PlotResult，可解包。"""
    result = sp.plot_sunburst(
        labels=["", "门A", "门B", "属A1", "属A2", "属B1"],
        parents=[None, "", "", "门A", "门A", "门B"],
        values=[100, 60, 40, 35, 25, 40],
    )
    fig, ax = result
    assert isinstance(ax, Axes)


def test_sunburst_three_levels(cleanup_figures):
    """三层旭日图。"""
    fig, ax = sp.plot_sunburst(
        labels=["", "A", "B", "A1", "A2", "B1", "B2", "A1x", "A1y"],
        parents=[None, "", "", "A", "A", "B", "B", "A1", "A1"],
        values=[100, 60, 40, 40, 20, 25, 15, 22, 18],
    )
    assert isinstance(ax, Axes)


def test_sunburst_validation_lengths(cleanup_figures):
    with pytest.raises(ValueError, match="长度必须一致"):
        sp.plot_sunburst(labels=["A"], parents=[None], values=[1, 2])


def test_sunburst_validation_parent(cleanup_figures):
    with pytest.raises(ValueError, match="不在 labels"):
        sp.plot_sunburst(labels=["A"], parents=["不存在"], values=[1])


def test_sunburst_no_root_raises(cleanup_figures):
    with pytest.raises(ValueError, match="根节点"):
        sp.plot_sunburst(labels=["A", "B"], parents=["B", "A"], values=[1, 1])


def test_sunburst_negative_raises(cleanup_figures):
    with pytest.raises(ValueError, match="负值"):
        sp.plot_sunburst(labels=["A"], parents=[None], values=[-1])


def test_sunburst_zero_root_raises(cleanup_figures):
    with pytest.raises(ValueError, match="大于 0"):
        sp.plot_sunburst(labels=["A"], parents=[None], values=[0])


def test_sunburst_colors_mismatch(cleanup_figures):
    with pytest.raises(ValueError, match="colors"):
        sp.plot_sunburst(
            labels=["A", "B"], parents=[None, None], values=[1, 2],
            colors=["#111111"],
        )


def test_sunburst_save_png(tmp_path, cleanup_figures):
    fig, ax = sp.plot_sunburst(
        labels=["", "X", "Y", "X1", "Y1"],
        parents=[None, "", "", "X", "Y"],
        values=[100, 55, 45, 55, 45],
    )
    paths = sp.save(fig, tmp_path / "sunburst", formats=("png",))
    assert paths[0].exists()


# ── plot_upset ─────────────────────────────────────────────────

def test_upset_basic_dict(cleanup_figures):
    """字典输入：三集合 Upset 图。"""
    result = sp.plot_upset({
        "RNA": {"G1", "G2", "G3", "G4"},
        "Prot": {"G3", "G4", "G5"},
        "ChIP": {"G1", "G3", "G5"},
    })
    fig, ax = result
    assert isinstance(ax, Axes)
    # 元数据含交集信息
    assert "intersections" in result.metadata


def test_upset_basic_list(cleanup_figures):
    """列表输入：需 set_names。"""
    fig, ax = sp.plot_upset(
        [["G1", "G2"], ["G2", "G3"], ["G1", "G3"]],
        set_names=["A", "B", "C"],
    )
    assert isinstance(ax, Axes)


def test_upset_list_requires_names(cleanup_figures):
    with pytest.raises(ValueError, match="set_names"):
        sp.plot_upset([["G1"], ["G2"]])


def test_upset_names_mismatch(cleanup_figures):
    with pytest.raises(ValueError, match="set_names 长度"):
        sp.plot_upset([["G1"], ["G2"]], set_names=["A"])


def test_upset_less_than_two_sets(cleanup_figures):
    with pytest.raises(ValueError, match="至少需要两个集合"):
        sp.plot_upset({"A": {"G1"}})


def test_upset_empty_raises(cleanup_figures):
    with pytest.raises(ValueError, match="不能为空"):
        sp.plot_upset({})


def test_upset_no_intersections(cleanup_figures):
    """无交集时（min_degree=2）报错提示。"""
    with pytest.raises(ValueError, match="min_degree"):
        sp.plot_upset({"A": {"G1"}, "B": {"G2"}})


def test_upset_min_degree_validation(cleanup_figures):
    with pytest.raises(ValueError, match="min_degree"):
        sp.plot_upset({"A": {"G1"}, "B": {"G1"}}, min_degree=0)


def test_upset_sort_by_validation(cleanup_figures):
    with pytest.raises(ValueError, match="sort_by"):
        sp.plot_upset({"A": {"G1"}, "B": {"G1"}}, sort_by="bogus")


def test_upset_save_png(tmp_path, cleanup_figures):
    fig, ax = sp.plot_upset({
        "A": {"G1", "G2", "G3"},
        "B": {"G2", "G3", "G4"},
        "C": {"G3", "G4", "G5"},
    })
    paths = sp.save(fig, tmp_path / "upset", formats=("png",))
    assert paths[0].exists()


# ── 别名与导出 ────────────────────────────────────────────────

def test_aliases_exported(cleanup_figures):
    assert callable(sp.plot_sunburst)
    assert callable(sp.plot_upset)
    assert callable(sp.sunburst)
    assert callable(sp.upset)
    assert "plot_sunburst" in sp.__all__
    assert "plot_upset" in sp.__all__
    assert "sunburst" in sp.__all__
    assert "upset" in sp.__all__


def test_upset_label_truncation_display_width(cleanup_figures):
    """底部分组标签按显示宽度截断（中文按 2 计），且省略号计入预算。"""
    result = sp.plot_upset({
        "RNA-seq": {1, 2, 3, 4, 5},
        "蛋白质组": {3, 4, 5, 6},
        "ChIP-seq": {1, 3, 5, 7},
    })
    bottom = [t.get_text() for t in result.ax.texts if "&" in t.get_text()]

    def disp_w(s):
        return sum(2 if ord(c) > 0x2E80 else 1 for c in s)

    # 预算：max(10, int(18 / (3 / 4))) = 24（3 个交集）
    for label in bottom:
        assert disp_w(label) <= 24, f"标签 {label!r} 显示宽度超预算: {disp_w(label)}"
    # 截断后必须带省略号，且保留完整集合名单元
    full = "RNA-seq&蛋白质组&ChIP-seq"
    truncated = [t for t in bottom if t.endswith("…")]
    assert truncated, "超宽标签应被截断"
    assert any(t.startswith("RNA-seq&蛋白质组&") for t in truncated), "应保留头部信息"
