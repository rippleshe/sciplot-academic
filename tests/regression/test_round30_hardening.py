"""
Round-30 hardening tests: plot_confidence list 输入、plot_bar color 覆盖、
boxplot 弃用参数、plot_parallel DataFrame 分类列。
"""

from __future__ import annotations

import warnings

import matplotlib.pyplot as plt
import numpy as np
import pytest

import sciplot as sp
from sciplot._core.utils import boxplot_with_orientation

pd = pytest.importorskip("pandas")


# ═══════════════════════════════════════════════════════════════
# plot_confidence 输入鲁棒性
# ═══════════════════════════════════════════════════════════════

def test_confidence_list_input(cleanup_figures):
    """plot_confidence 接受纯 list 输入（此前 list-float 运算崩溃）。"""
    result = sp.plot_confidence(
        [1, 2, 3], [1.0, 2.0, 3.0], [0.1, 0.2, 0.3],
    )
    assert result.fig is not None


def test_confidence_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="长度必须一致"):
        sp.plot_confidence([1, 2], [1.0, 2.0, 3.0], [0.1, 0.1])


def test_confidence_negative_std_raises(cleanup_figures):
    with pytest.raises(ValueError, match="y_std"):
        sp.plot_confidence([1, 2], [1.0, 2.0], [0.1, -0.1])


def test_confidence_nan_std_raises(cleanup_figures):
    with pytest.raises(ValueError, match="y_std"):
        sp.plot_confidence([1, 2], [1.0, 2.0], [0.1, np.nan])


# ═══════════════════════════════════════════════════════════════
# plot_bar color 覆盖
# ═══════════════════════════════════════════════════════════════

def test_bar_explicit_color_override(cleanup_figures):
    """显式 color 参数覆盖自动配色，且不与其他参数冲突。"""
    result = sp.plot_bar(["A", "B", "C"], [1.0, 2.0, 3.0], color="#333333")
    colors = {p.get_facecolor() for p in result.ax.patches}
    assert len(colors) == 1
    assert np.allclose(list(colors)[0][:3], [0.2, 0.2, 0.2])


def test_bar_auto_colors_still_work(cleanup_figures):
    """未传 color 时保持逐柱自动配色。"""
    result = sp.plot_bar(["A", "B", "C"], [1.0, 2.0, 3.0])
    colors = {p.get_facecolor() for p in result.ax.patches}
    assert len(colors) == 3


# ═══════════════════════════════════════════════════════════════
# boxplot 方向参数兼容
# ═══════════════════════════════════════════════════════════════

def test_boxplot_with_orientation_horizontal(cleanup_figures):
    fig, ax = plt.subplots()
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # 任何弃用/未来警告都视为失败
        bp = boxplot_with_orientation(ax, [np.random.randn(50)], orientation="horizontal")
    assert len(bp["boxes"]) == 1


def test_boxplot_with_orientation_vertical(cleanup_figures):
    fig, ax = plt.subplots()
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        bp = boxplot_with_orientation(ax, [np.random.randn(50)], orientation="vertical")
    assert len(bp["boxes"]) == 1


def test_raincloud_no_deprecation_warning(cleanup_figures):
    """raincloud/beeswarm/marginal 的箱线调用不得触发弃用警告。"""
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        r1 = sp.plot_raincloud([np.random.randn(50)])
        r2 = sp.plot_beeswarm([np.random.randn(50)], show_box=True)
        r3 = sp.plot_marginal(
            np.random.randn(50), np.random.randn(50), marginal="box"
        )
    assert r1.fig is not None and r2.fig is not None and r3.fig is not None


# ═══════════════════════════════════════════════════════════════
# plot_parallel DataFrame 支持
# ═══════════════════════════════════════════════════════════════

def test_parallel_dataframe_categorical_color(cleanup_figures):
    """DataFrame 分类列 + color_by 列名：分类着色 + 图例。"""
    df = pd.DataFrame({
        "cat": ["a", "b", "a", "c"],
        "f1": [1.0, 2.0, 3.0, 4.0],
        "f2": [4.0, 3.0, 2.0, 1.0],
    })
    result = sp.plot_parallel(df, color_by="cat")
    legend = result.ax.get_legend()
    assert legend is not None
    texts = [t.get_text() for t in legend.get_texts()]
    assert texts == ["a", "b", "c"]


def test_parallel_dataframe_mixed_columns(cleanup_figures):
    """混合类型 DataFrame 自动提取数值列，文本列不参与绘图。"""
    df = pd.DataFrame({
        "txt": ["x", "y", "z"],
        "v1": [1.0, 2.0, 3.0],
        "v2": [3.0, 2.0, 1.0],
    })
    result = sp.plot_parallel(df)
    xt = [t.get_text() for t in result.ax.get_xticklabels()]
    assert xt == ["v1", "v2"]


def test_parallel_dataframe_explicit_columns_filtered(cleanup_figures):
    """显式 columns 中混入非数值列时应自动剔除。"""
    df = pd.DataFrame({
        "txt": ["x", "y", "z"],
        "v1": [1.0, 2.0, 3.0],
        "v2": [3.0, 2.0, 1.0],
    })
    result = sp.plot_parallel(df, columns=["txt", "v1", "v2"])
    xt = [t.get_text() for t in result.ax.get_xticklabels()]
    assert xt == ["v1", "v2"]


def test_parallel_dataframe_no_numeric_raises(cleanup_figures):
    df = pd.DataFrame({"txt": ["x", "y", "z"]})
    with pytest.raises(ValueError, match="不包含数值列"):
        sp.plot_parallel(df)


def test_parallel_dataframe_numeric_color_by_index(cleanup_figures):
    """数值 DataFrame 按列索引着色不回归。"""
    df = pd.DataFrame({"f1": [1.0, 2.0, 3.0], "f2": [3.0, 2.0, 1.0]})
    result = sp.plot_parallel(df, color_by=0)
    assert result.fig is not None
