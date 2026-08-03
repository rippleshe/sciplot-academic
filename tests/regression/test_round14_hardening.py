"""
Round-14 hardening tests for plots-layer robustness (radar/density/bland-altman).
"""

from __future__ import annotations

import warnings

import matplotlib.pyplot as plt
import numpy as np
import pytest

import sciplot as sp


# ═══════════════════════════════════════════════════════════════
# plot_radar 输入鲁棒性
# ═══════════════════════════════════════════════════════════════

def test_radar_accepts_2d_ndarray(cleanup_figures):
    """values_list 传 2D ndarray 不得崩溃（此前抛出歧义真值错误）。"""
    values = np.array([[0.5, 0.6, 0.7], [0.4, 0.5, 0.6]])
    result = sp.plot_radar(
        ["准确率", "召回率", "F1"], values,
        labels=["A", "B"],
    )
    assert result.fig is not None
    assert len(result.ax.lines) == 2


def test_radar_accepts_list_of_ndarrays(cleanup_figures):
    """values_list 为 ndarray 列表时正常绘制。"""
    result = sp.plot_radar(
        ["a", "b", "c"],
        [np.array([0.5, 0.6, 0.7]), np.array([0.4, 0.5, 0.6])],
    )
    assert len(result.ax.lines) == 2


def test_radar_rejects_2d_row(cleanup_figures):
    """values_list 中某个系列是二维数据必须报清晰错误。"""
    with pytest.raises(ValueError, match="一维"):
        sp.plot_radar(["a", "b"], [np.ones((2, 2))])


def test_radar_rejects_nan(cleanup_figures):
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_radar(["a", "b"], [[0.5, np.nan]])


# ═══════════════════════════════════════════════════════════════
# plot_density / plot_multi_density 常数序列
# ═══════════════════════════════════════════════════════════════

def test_density_constant_series_no_crash(cleanup_figures):
    """常数序列的 KDE 应退化为垂直线而不是抛 LinAlgError。"""
    result = sp.plot_density(np.full(50, 3.0))
    assert result.fig is not None
    # axvline 会产生 Line2D 图元
    assert len(result.ax.lines) == 1


def test_density_constant_series_fill_ok(cleanup_figures):
    """常数序列 + fill=True 也不得崩溃。"""
    result = sp.plot_density(np.full(20, 1.5), fill=True)
    assert result.fig is not None


def test_multi_density_with_constant_group(cleanup_figures):
    """多密度图中某一组为常数序列不得拖垮整张图。"""
    groups = [
        np.random.default_rng(0).normal(0, 1, 100),
        np.full(50, 2.0),
    ]
    result = sp.plot_multi_density(groups, labels=["随机", "常数"])
    assert result.fig is not None
    # 常数组绘制为一条垂直线
    assert len(result.ax.lines) == 2


def test_density_too_few_points_raises(cleanup_figures):
    with pytest.raises(ValueError, match="至少需要 2 个"):
        sp.plot_density(np.array([1.0]))


# ═══════════════════════════════════════════════════════════════
# plot_bland_altman 最小样本量
# ═══════════════════════════════════════════════════════════════

def test_bland_altman_single_point_raises(cleanup_figures):
    """单点数据必须报错而不是产生 numpy 运行时警告。"""
    with pytest.raises(ValueError, match="至少需要 2 个"):
        sp.plot_bland_altman(np.array([1.0]), np.array([1.1]))


def test_bland_altman_two_points_no_warning(cleanup_figures):
    """2 个数据点可正常绘制且不产生警告。"""
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # 任何警告都视为失败
        result = sp.plot_bland_altman(np.array([1.0, 2.0]), np.array([1.1, 2.2]))
    assert result.fig is not None


# ═══════════════════════════════════════════════════════════════
# 既有校验行为回归护栏
# ═══════════════════════════════════════════════════════════════

def test_step_invalid_where_raises(cleanup_figures):
    with pytest.raises(ValueError):
        sp.plot_step([1, 2], [1, 2], where="sideways")


def test_qq_all_inf_raises(cleanup_figures):
    with pytest.raises(ValueError, match="数据点太少"):
        sp.plot_qq(np.array([np.inf, np.inf, np.inf]))


def test_histogram_all_inf_raises(cleanup_figures):
    with pytest.raises(ValueError, match="至少需要 1 个有限数值"):
        sp.plot_histogram(np.array([np.inf, np.inf]))


def test_grouped_bar_gap_too_large_raises(cleanup_figures):
    with pytest.raises(ValueError, match="width"):
        sp.plot_grouped_bar(
            ["A", "B"], {"m1": [1, 2], "m2": [3, 4]},
            width=0.2, gap=0.5,
        )


def test_combo_empty_x_raises(cleanup_figures):
    with pytest.raises(ValueError, match="x 不能为空"):
        sp.plot_combo([], {"a": [1]})


def test_scatter_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="不一致"):
        sp.plot_scatter([1, 2], [1, 2, 3])
