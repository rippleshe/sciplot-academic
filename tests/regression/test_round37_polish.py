"""
Round-37 polish tests: 新图暗色主题兼容 + 边界场景 + 互通性。
"""

from __future__ import annotations

import datetime

import matplotlib
import numpy as np
import pytest

import sciplot as sp


# ═══════════════════════════════════════════════════════════════
# 新图 × 暗色主题
# ═══════════════════════════════════════════════════════════════

def test_new_charts_dark_theme(cleanup_figures):
    """volcano/calendar/taylor/chord/ternary/waffle 在暗色主题下全部可绘。"""
    sp.setup_style("presentation", theme="dark")
    rng = np.random.default_rng(1)

    r1 = sp.plot_volcano(rng.normal(0, 1, 100), 10 ** (-rng.uniform(0, 3, 100)))
    dates = [datetime.date(2024, 1, 1) + datetime.timedelta(days=i) for i in range(60)]
    r2 = sp.plot_calendar_heatmap(dates, rng.poisson(2, 60))
    obs = rng.normal(0, 1, 100)
    r3 = sp.plot_taylor(obs, {"m1": 0.8 * obs + rng.normal(0, 0.5, 100)})
    mat = np.array([[0, 5, 2], [5, 0, 3], [2, 3, 0]], dtype=float)
    r4 = sp.plot_chord(mat)
    a, b, c = rng.random(30), rng.random(30), rng.random(30)
    s = a + b + c
    r5 = sp.plot_ternary(a / s, b / s, c / s)
    r6 = sp.plot_waffle(["A", "B"], np.array([60, 40]))

    assert all(r.fig is not None for r in [r1, r2, r3, r4, r5, r6])
    assert matplotlib.rcParams["figure.facecolor"] == "#1a1a2e"


# ═══════════════════════════════════════════════════════════════
# 边界场景
# ═══════════════════════════════════════════════════════════════

def test_volcano_all_insignificant(cleanup_figures):
    """全不显著数据：全部灰色，不崩溃。"""
    rng = np.random.default_rng(2)
    result = sp.plot_volcano(rng.normal(0, 0.5, 50), rng.uniform(0.1, 0.9, 50))
    scatter = result.ax.collections[0]
    facecolors = np.asarray(scatter.get_facecolors())
    unique = {tuple(c[:3].round(2)) for c in facecolors}
    assert len(unique) == 1  # 全部同色


def test_taylor_negative_correlation(cleanup_figures):
    """负相关模型可绘制（角度 > 90° 裁剪到图内）。"""
    rng = np.random.default_rng(3)
    obs = rng.normal(0, 1, 200)
    anti = -obs + rng.normal(0, 0.5, 200)
    result = sp.plot_taylor(obs, {"反相关": anti})
    assert result.fig is not None


def test_chord_asymmetric_matrix(cleanup_figures):
    """非对称流量矩阵可绘制。"""
    mat = np.array([[0, 8, 2], [3, 0, 1], [5, 4, 0]], dtype=float)
    result = sp.plot_chord(mat, labels=["A", "B", "C"])
    assert result.fig is not None


def test_waffle_single_category(cleanup_figures):
    result = sp.plot_waffle(["A"], np.array([100.0]))
    assert result.fig is not None


def test_calendar_single_day(cleanup_figures):
    result = sp.plot_calendar_heatmap([datetime.date(2024, 6, 15)], [1.0])
    assert result.fig is not None


# ═══════════════════════════════════════════════════════════════
# 互通性：新图与既有 API
# ═══════════════════════════════════════════════════════════════

def test_new_charts_in_style_context(cleanup_figures):
    """新图在 style_context 内绘制并使用上下文样式。"""
    with sp.style_context("ieee", palette="ocean"):
        result = sp.plot_volcano(
            np.array([1.0, -1.5, 0.2]), np.array([0.01, 0.02, 0.5]),
        )
        assert result.fig is not None
    # 退出后样式恢复
    assert matplotlib.rcParams["figure.figsize"] != [3.3, 2.5]


def test_new_charts_save_all_formats(tmp_path, cleanup_figures):
    """新图与 sp.save 多格式输出互通。"""
    rng = np.random.default_rng(4)
    r = sp.plot_volcano(rng.normal(0, 1, 80), 10 ** (-rng.uniform(0, 3, 80)))
    paths = r.save(str(tmp_path / "volcano_multi"), formats=("pdf", "png"), dpi=100)
    assert len(paths) == 2
    assert all(p.exists() for p in paths)


def test_chord_legend_not_required(cleanup_figures):
    """chord 不产生图例但文本标签齐全。"""
    mat = np.array([[0, 4, 1], [4, 0, 2], [1, 2, 0]], dtype=float)
    result = sp.plot_chord(mat, labels=["X", "Y", "Z"])
    texts = [t.get_text() for t in result.ax.texts]
    assert "X" in texts and "Y" in texts and "Z" in texts
