"""
Round 5 回归测试

覆盖 v1.8.1 新增修复项与核心新增功能。
"""

import numpy as np
import matplotlib.pyplot as plt
import pytest

import sciplot as sp


def test_plot_multi_default_auto_subset_works(reset_style, test_data, cleanup_figures):
    """palette=None 时应自动按 DEFAULT_PALETTE 选择子集。"""
    fig, ax = sp.plot_multi(test_data["x"], [test_data["y"], test_data["y2"]])
    colors = [line.get_color() for line in ax.lines]
    assert colors[:2] == sp.get_palette("pastel-2")
    plt.close(fig)


def test_earth_palette_is_resident(reset_style, cleanup_figures):
    """EARTH_PALETTE 应可直接应用。"""
    sp.setup_style(palette="earth")
    fig, ax = sp.plot([1, 2, 3], [1, 3, 2])
    assert fig is not None
    plt.close(fig)


def test_combo_returns_combo_plot_result(cleanup_figures):
    """plot_combo 应返回 ComboPlotResult 并支持三元解包。"""
    x = ["Q1", "Q2", "Q3"]
    result = sp.plot_combo(
        x,
        bar_data={"销量": [10, 15, 20]},
        line_data={"增长率": [0.1, 0.2, 0.3]},
    )
    assert isinstance(result, sp.ComboPlotResult)

    fig, ax_bar, ax_line = result
    assert fig is not None
    assert ax_bar is not None
    assert ax_line is not None


def test_distribution_aliases_accept_lang(cleanup_figures):
    """grouped_bar/stacked_bar/combo 别名应支持 lang 参数。"""
    grouped = sp.grouped_bar(
        groups=["A", "B"],
        data={"M1": [1.0, 2.0], "M2": [1.5, 2.2]},
        lang="en",
    )
    assert isinstance(grouped, sp.PlotResult)

    stacked = sp.stacked_bar(
        categories=["A", "B"],
        data={"M1": [1.0, 2.0], "M2": [0.5, 0.8]},
        lang="en",
    )
    assert isinstance(stacked, sp.PlotResult)

    combo = sp.combo(
        x=["Q1", "Q2"],
        bar_data={"销量": [10, 12]},
        line_data={"增长率": [0.1, 0.2]},
        lang="en",
    )
    assert isinstance(combo, sp.ComboPlotResult)


def test_plot_parallel_show_colorbar_false(cleanup_figures):
    """连续着色下可关闭 colorbar 以保持版心尺寸。"""
    data = np.random.randn(30, 4)
    result = sp.plot_parallel(data, color_by=0, show_colorbar=False)
    assert isinstance(result, sp.PlotResult)
    assert len(result.fig.axes) == 1


def test_plot_radar_no_overlap_labels_for_multi(cleanup_figures):
    """多组雷达图在 show_labels=True 时不应叠加数值标签。"""
    categories = ["A", "B", "C", "D", "E"]
    values = [
        [0.7, 0.8, 0.75, 0.65, 0.9],
        [0.6, 0.7, 0.8, 0.7, 0.85],
    ]
    result = sp.plot_radar(categories, values, labels=["方法1", "方法2"], show_labels=True)
    assert len(result.ax.texts) == 0


def test_auto_rotate_labels_draw_before_read(cleanup_figures):
    """auto_rotate_labels 在未显式 draw 前也应能判断并旋转。"""
    fig, ax = plt.subplots()
    labels = [f"very_long_label_{i}" for i in range(8)]
    ax.bar(labels, np.arange(8))

    sp.auto_rotate_labels(ax)

    rotations = [tick.get_rotation() for tick in ax.get_xticklabels()]
    assert any(abs(rot) > 0 for rot in rotations)


def test_plot_lollipop_basic(cleanup_figures):
    """棒棒糖图应可正常返回 PlotResult。"""
    result = sp.plot_lollipop(["A", "B", "C"], np.array([2.0, 3.5, 1.2]))
    assert isinstance(result, sp.PlotResult)


def test_plot_multi_area_applies_kwargs_in_non_stacked_mode(cleanup_figures):
    """multi_area 非堆叠模式应透传 fill_between kwargs。"""
    x = np.arange(5)
    ys = [np.array([1, 2, 3, 2, 1]), np.array([2, 3, 4, 3, 2])]
    result = sp.plot_multi_area(x, ys, stacked=False, linewidth=2.5, edgecolor="black")

    assert len(result.ax.collections) == 2
    line_widths = [coll.get_linewidths()[0] for coll in result.ax.collections]
    assert all(lw == pytest.approx(2.5, rel=1e-3, abs=1e-3) for lw in line_widths)


def test_plot_density_and_multi_density(cleanup_figures):
    """KDE 图函数应可正常工作。"""
    pytest.importorskip("scipy")

    data = np.random.normal(0, 1, 200)
    result = sp.plot_density(data, fill=True)
    assert isinstance(result, sp.PlotResult)

    data2 = np.random.normal(0.8, 1.2, 200)
    result2 = sp.plot_multi_density([data, data2], labels=["A", "B"], fill=False)
    assert isinstance(result2, sp.PlotResult)


def test_plot_slope_basic(cleanup_figures):
    """斜率图应返回 PlotResult。"""
    result = sp.plot_slope(
        labels=["模型A", "模型B", "模型C"],
        before=[81.2, 83.4, 85.1],
        after=[84.0, 85.2, 89.6],
        left_label="Before",
        right_label="After",
        show_diff=True,
    )
    assert isinstance(result, sp.PlotResult)


def test_plot_scatter_matrix_basic(cleanup_figures):
    """散点矩阵应返回多子图 PlotResult。"""
    data = np.random.randn(60, 4)
    result = sp.plot_scatter_matrix(data, columns=["A", "B", "C", "D"], diag="hist")
    assert isinstance(result, sp.PlotResult)
    assert result.ax_array.shape == (4, 4)


def test_diverging_palette_heatmap(reset_style, cleanup_figures):
    """rdbu 发散配色应可作为 heatmap cmap 使用。"""
    data = np.random.randn(5, 5)
    result = sp.plot_heatmap(data, cmap="rdbu")
    assert isinstance(result, sp.PlotResult)


def test_clustermap_respects_venue_size(cleanup_figures):
    """clustermap 尺寸应随 venue 改变，不再硬编码。"""
    pytest.importorskip("scipy")

    data = np.random.randn(6, 4)
    result = sp.plot_clustermap(data, venue="ieee")
    width, height = result.fig.get_size_inches()
    assert width == pytest.approx(3.5, abs=0.6)
    assert height == pytest.approx(3.5, abs=0.6)


def test_inspect_outputs_summary(capsys):
    """sp.inspect() 应输出诊断摘要而不是抛错。"""
    sp.inspect()
    out = capsys.readouterr().out
    assert "SciPlot Academic" in out
    assert "环境诊断" in out
