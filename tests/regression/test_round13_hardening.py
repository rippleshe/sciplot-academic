"""
Round-13 hardening tests for theme-state fixes and plot3d/heatmap robustness.
"""

from __future__ import annotations

import warnings

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest

import sciplot as sp
from sciplot._core.style import (
    get_current_theme,
    set_current_theme,
)


# ═══════════════════════════════════════════════════════════════
# theme 状态保持与配置
# ═══════════════════════════════════════════════════════════════

def test_set_defaults_theme_dark_affects_setup_style(cleanup_figures):
    """set_defaults(theme=...) 必须被 setup_style() 读取（此前被忽略）。"""
    sp.reset_config()
    sp.reset_style()  # 清空线程局部主题状态，确保读取配置默认值
    try:
        sp.set_defaults(theme="dark")
        sp.setup_style("presentation")
        assert matplotlib.rcParams["figure.facecolor"] == "#1a1a2e"
        assert get_current_theme() == "dark"
    finally:
        sp.reset_config()
        sp.reset_style()


def test_dark_theme_preserved_across_venue_change(cleanup_figures):
    """显式 dark 主题后切换 venue，不得回退到 light。"""
    sp.setup_style("presentation", theme="dark")
    sp.plot(np.linspace(0, 1, 10), np.linspace(0, 1, 10), venue="ieee")
    assert matplotlib.rcParams["figure.facecolor"] == "#1a1a2e"
    assert get_current_theme() == "dark"


def test_explicit_light_theme_resets_dark(cleanup_figures):
    """显式 theme="light" 必须真正复位暗色参数（此前 light 是空操作）。"""
    sp.setup_style("presentation", theme="dark")
    sp.setup_style("ieee", theme="light")
    assert matplotlib.rcParams["figure.facecolor"] == "white"
    assert matplotlib.rcParams["text.color"] == "black"
    assert get_current_theme() == "light"


def test_style_context_inherits_outer_dark_theme(cleanup_figures):
    """style_context(venue=...) 在暗色外部状态下应继承暗色。"""
    sp.setup_style("presentation", theme="dark")
    with sp.style_context("ieee"):
        assert matplotlib.rcParams["figure.facecolor"] == "#1a1a2e"
        assert get_current_theme() == "dark"
    # 退出后恢复外部状态
    assert matplotlib.rcParams["figure.facecolor"] == "#1a1a2e"
    assert get_current_theme() == "dark"


def test_style_context_theme_override_restores_after_exit(cleanup_figures):
    """style_context(theme="light") 在暗色外部状态下临时切换，退出必须恢复。"""
    sp.setup_style("presentation", theme="dark")
    with sp.style_context("ieee", theme="light"):
        assert matplotlib.rcParams["figure.facecolor"] == "white"
        assert get_current_theme() == "light"
    assert matplotlib.rcParams["figure.facecolor"] == "#1a1a2e"
    assert get_current_theme() == "dark"


def test_reset_style_clears_theme_state(cleanup_figures):
    """reset_style() 必须清空 theme 状态。"""
    sp.setup_style("presentation", theme="dark")
    sp.reset_style()
    assert get_current_theme() is None


def test_plotchain_preserves_dark_theme(cleanup_figures):
    """链式调用在暗色状态下绘图应保持暗色。"""
    sp.setup_style("presentation", theme="dark")
    sp.style("ieee").plot(np.linspace(0, 1, 10), np.linspace(0, 1, 10))
    assert matplotlib.rcParams["figure.facecolor"] == "#1a1a2e"


def test_failed_context_enter_rolls_back_state(cleanup_figures):
    """style_context 进入失败（非法 venue）必须完整回滚并清空上下文栈。"""
    sp.setup_style("ieee", "ocean", lang="en")
    before = dict(matplotlib.rcParams)
    with pytest.raises(ValueError):
        with sp.style_context("not-a-venue"):
            pass
    assert not sp.StyleContext.is_in_context()
    assert matplotlib.rcParams["figure.facecolor"] == before["figure.facecolor"]
    assert matplotlib.rcParams["font.family"] == before["font.family"]


# ═══════════════════════════════════════════════════════════════
# plot_3d_scatter 颜色参数鲁棒性
# ═══════════════════════════════════════════════════════════════

@pytest.fixture()
def _scatter3d_data():
    rng = np.random.default_rng(42)
    return rng.random(20), rng.random(20), rng.random(20)


def test_plot3d_scatter_scalar_c_no_crash(_scatter3d_data, cleanup_figures):
    """c=数值标量不得崩溃（此前 3D scatter 拒绝标量 c）。"""
    x, y, z = _scatter3d_data
    result = sp.plot_3d_scatter(x, y, z, c=5.0, s=30)
    assert result.fig is not None
    # 标量 c 是单一颜色，不应创建 colorbar
    assert len(result.fig.axes) == 1


def test_plot3d_scatter_string_c_no_crash(_scatter3d_data, cleanup_figures):
    """c=颜色字符串应正常渲染且不创建 colorbar。"""
    x, y, z = _scatter3d_data
    result = sp.plot_3d_scatter(x, y, z, c="red", s=30)
    assert result.fig is not None
    assert len(result.fig.axes) == 1


def test_plot3d_scatter_single_element_c_no_crash(_scatter3d_data, cleanup_figures):
    """c=单元素数组应广播为统一颜色且不崩溃。"""
    x, y, z = _scatter3d_data
    result = sp.plot_3d_scatter(x, y, z, c=np.array([3.0]), s=30)
    assert result.fig is not None
    assert len(result.fig.axes) == 1


def test_plot3d_scatter_array_c_creates_colorbar(_scatter3d_data, cleanup_figures):
    """c=等长数组应创建颜色条。"""
    x, y, z = _scatter3d_data
    cvals = np.linspace(0, 1, len(x))
    result = sp.plot_3d_scatter(x, y, z, c=cvals, s=30)
    assert result.fig is not None
    # 3D 子图 + colorbar 轴
    assert len(result.fig.axes) >= 2


def test_plot3d_scatter_none_c_no_colormapping_warning(_scatter3d_data, cleanup_figures):
    """c=None 时不得发出 'No data for colormapping' 警告。"""
    x, y, z = _scatter3d_data
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        sp.plot_3d_scatter(x, y, z, s=30)
    colormapping_warns = [wi for wi in w if "colormapping" in str(wi.message)]
    assert colormapping_warns == []


def test_plot3d_scatter_invalid_c_type_raises(_scatter3d_data, cleanup_figures):
    """c=无法解释的类型应抛出 ValueError 而非静默失败。"""
    x, y, z = _scatter3d_data
    with pytest.raises(ValueError, match="'c'"):
        sp.plot_3d_scatter(x, y, z, c={"bad": 1}, s=30)


def test_plot3d_scatter_mismatched_c_length_raises(_scatter3d_data, cleanup_figures):
    """c 长度与数据点不匹配必须报错。"""
    x, y, z = _scatter3d_data
    with pytest.raises(ValueError, match="长度"):
        sp.plot_3d_scatter(x, y, z, c=np.linspace(0, 1, 5), s=30)


# ═══════════════════════════════════════════════════════════════
# plot_heatmap 标注对比度
# ═══════════════════════════════════════════════════════════════

def _cell_text_colors(ax):
    """收集热力图中所有 text 标注及其颜色。"""
    return {
        (round(t.get_position()[0]), round(t.get_position()[1])): t.get_color()
        for t in ax.texts
    }


def test_heatmap_annotate_auto_contrast(cleanup_figures):
    """深色格子应自动使用白字，浅色格子使用黑字。"""
    data = np.array([
        [0.0, 0.1],   # 浅色格子 → 黑字
        [0.9, 1.0],   # 深色格子 → 白字
    ])
    result = sp.plot_heatmap(data, cmap="Blues", show_values=True, fmt=".1f")
    colors = _cell_text_colors(result.ax)
    # text 位置为 (j, i) = (列, 行)，对应 data[i][j]
    assert colors[(0, 0)] == "black"   # data[0][0]=0.0 浅色 → 黑字
    assert colors[(1, 0)] == "black"   # data[0][1]=0.1 浅色 → 黑字
    assert colors[(0, 1)] == "white"   # data[1][0]=0.9 深色 → 白字
    assert colors[(1, 1)] == "white"   # data[1][1]=1.0 深色 → 白字


def test_heatmap_annotate_explicit_color(cleanup_figures):
    """显式 annot_color 应覆盖自动对比度选择。"""
    data = np.array([[0.9, 0.2], [0.1, 0.8]])
    result = sp.plot_heatmap(
        data, cmap="Blues", show_values=True, fmt=".1f",
        annot_color="red",
    )
    colors = _cell_text_colors(result.ax)
    assert set(colors.values()) == {"red"}


def test_heatmap_annotate_vmin_vmax_contrast(cleanup_figures):
    """vmin/vmax 影响映射时，对比度判断应基于实际渲染颜色。"""
    data = np.array([[0.0], [1.0]])
    # vmin=0.9：0.0 被裁剪到 viridis 最暗端 → 白字；1.0 映射到最亮端 → 黑字
    result = sp.plot_heatmap(
        data, cmap="viridis", show_values=True, fmt=".1f",
        vmin=0.9, vmax=1.0,
    )
    colors = _cell_text_colors(result.ax)
    assert colors[(0, 0)] == "white"
    assert colors[(0, 1)] == "black"
