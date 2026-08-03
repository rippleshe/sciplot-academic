"""
Round-49 tests: plot_taylor / plot_combo 数组输入兼容（修复 ambiguous truth value bug）。
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp


# ── plot_taylor 数组输入兼容 ───────────────────────────────────

def test_taylor_array_input(cleanup_figures):
    """单个数组输入自动命名，不抛 ambiguous 异常。"""
    rng = np.random.default_rng(0)
    obs = rng.normal(0, 1, 50)
    pred = obs + rng.normal(0, 0.3, 50)
    result = sp.plot_taylor(obs, pred)
    assert result.fig is not None
    assert result.ax is not None


def test_taylor_dict_input(cleanup_figures):
    """字典输入仍正常。"""
    rng = np.random.default_rng(1)
    obs = rng.normal(0, 1, 50)
    result = sp.plot_taylor(
        obs,
        {"A": obs + rng.normal(0, 0.2, 50),
         "B": obs + rng.normal(0, 0.5, 50)},
    )
    assert result.fig is not None


def test_taylor_empty_dict_raises(cleanup_figures):
    with pytest.raises(ValueError, match="models"):
        sp.plot_taylor(np.random.randn(10), {})


def test_taylor_invalid_type_raises(cleanup_figures):
    with pytest.raises(ValueError, match="models"):
        sp.plot_taylor(np.random.randn(10), 42)


# ── plot_combo 数组输入兼容 ────────────────────────────────────

def test_combo_array_input(cleanup_figures):
    """bar_data/line_data 传数组时自动包装为单系列。"""
    result = sp.plot_combo(
        np.arange(5), np.arange(5), np.arange(5) * 2,
    )
    assert result.fig is not None


def test_combo_dict_input(cleanup_figures):
    """字典输入仍正常（多系列）。"""
    result = sp.plot_combo(
        ["a", "b", "c"],
        {"柱1": [1, 2, 3], "柱2": [3, 2, 1]},
        {"线1": [2, 3, 4]},
    )
    assert result.fig is not None


def test_combo_no_line_data(cleanup_figures):
    """仅柱状图（line_data=None）。"""
    result = sp.plot_combo(["a", "b"], {"柱": [1, 2]})
    assert result.fig is not None


def test_combo_empty_raises(cleanup_figures):
    with pytest.raises(ValueError):
        sp.plot_combo(np.arange(3), {})


def test_combo_save_png(tmp_path, cleanup_figures):
    """数组输入可正常保存。"""
    result = sp.plot_combo(np.arange(4), np.arange(4), np.arange(4) * 3)
    paths = result.save(str(tmp_path / "combo_arr"), formats=("png",), dpi=80)
    assert paths[0].exists()
