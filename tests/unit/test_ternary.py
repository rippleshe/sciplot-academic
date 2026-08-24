"""
Round-35 tests for plot_ternary (三角相图).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp


@pytest.fixture()
def ternary_data():
    rng = np.random.default_rng(41)
    n = 60
    a = rng.uniform(0, 1, n)
    b = rng.uniform(0, 1, n)
    c = 1.0 - a - b
    c = np.clip(c, 0, None)
    # 重新归一化保证每行和 > 0
    s = a + b + c
    return a / s, b / s, c / s


def test_ternary_basic(ternary_data, cleanup_figures):
    a, b, c = ternary_data
    result = sp.plot_ternary(a, b, c, labels=["组分A", "组分B", "组分C"])
    assert result.fig is not None
    scatter = result.ax.collections[0]
    assert len(scatter.get_offsets()) == 60


def test_ternary_corner_projection(cleanup_figures):
    """纯组分点必须落在对应顶点。"""
    a = np.array([1.0, 0.0, 0.0])
    b = np.array([0.0, 1.0, 0.0])
    c = np.array([0.0, 0.0, 1.0])
    result = sp.plot_ternary(a, b, c)
    offs = np.asarray(result.ax.collections[0].get_offsets())
    # 纯 A → (0, 0)；纯 B → (1, 0)；纯 C → (0.5, √3/2)
    assert np.allclose(offs[0], [0.0, 0.0])
    assert np.allclose(offs[1], [1.0, 0.0])
    assert np.allclose(offs[2], [0.5, np.sqrt(3) / 2])


def test_ternary_normalization(cleanup_figures):
    """行和不为 1 的输入自动归一化。"""
    a = np.array([1.0, 2.0, 1.0])
    b = np.array([1.0, 2.0, 1.0])
    c = np.array([0.0, 0.0, 2.0])
    r1 = sp.plot_ternary(a, b, c)
    offs1 = np.asarray(r1.ax.collections[0].get_offsets())
    # 等比例缩放不改变投影位置
    r2 = sp.plot_ternary(a / 3, b / 3, c / 3)
    offs2 = np.asarray(r2.ax.collections[0].get_offsets())
    assert np.allclose(offs1, offs2)


def test_ternary_color_by(ternary_data, cleanup_figures):
    a, b, c = ternary_data
    result = sp.plot_ternary(a, b, c, color_by=np.linspace(0, 1, len(a)))
    assert len(result.fig.axes) == 2  # 主图 + colorbar


def test_ternary_color_by_disabled(ternary_data, cleanup_figures):
    a, b, c = ternary_data
    result = sp.plot_ternary(a, b, c, color_by=np.linspace(0, 1, len(a)),
                             show_colorbar=False)
    assert len(result.fig.axes) == 1


def test_ternary_grid_off(ternary_data, cleanup_figures):
    a, b, c = ternary_data
    result = sp.plot_ternary(a, b, c, grid=False)
    assert result.fig is not None


def test_ternary_grid_segments_stay_inside_simplex(ternary_data, cleanup_figures):
    """三族辅助线的全部端点都必须落在三角形内部/边界，不能穿出 simplex。"""
    a, b, c = ternary_data
    levels = 4
    result = sp.plot_ternary(a, b, c, grid=True, grid_levels=levels)
    # 第一条 Line2D 是三角形边框，后续每级有 c/b/a 三条网格线。
    grid_lines = result.ax.lines[1:]
    assert len(grid_lines) == levels * 3

    h = np.sqrt(3) / 2
    for line in grid_lines:
        xs = np.asarray(line.get_xdata(), dtype=float)
        ys = np.asarray(line.get_ydata(), dtype=float)
        c_coord = ys / h
        b_coord = xs - 0.5 * c_coord
        a_coord = 1.0 - b_coord - c_coord
        assert np.all(a_coord >= -1e-12)
        assert np.all(b_coord >= -1e-12)
        assert np.all(c_coord >= -1e-12)
        assert np.all(a_coord <= 1.0 + 1e-12)
        assert np.all(b_coord <= 1.0 + 1e-12)
        assert np.all(c_coord <= 1.0 + 1e-12)


def test_ternary_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="长度必须一致"):
        sp.plot_ternary([1.0, 2.0], [1.0], [1.0])


def test_ternary_negative_raises(cleanup_figures):
    with pytest.raises(ValueError, match="负值"):
        sp.plot_ternary([-0.1], [1.0], [0.1])


def test_ternary_zero_row_raises(cleanup_figures):
    with pytest.raises(ValueError, match="之和必须大于 0"):
        sp.plot_ternary([0.0], [0.0], [0.0])


def test_ternary_nan_raises(cleanup_figures):
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_ternary([np.nan], [1.0], [0.1])


def test_ternary_bad_labels_raises(ternary_data, cleanup_figures):
    a, b, c = ternary_data
    with pytest.raises(ValueError, match="labels"):
        sp.plot_ternary(a, b, c, labels=["A", "B"])


def test_ternary_bad_grid_raises(ternary_data, cleanup_figures):
    a, b, c = ternary_data
    with pytest.raises(ValueError, match="grid_levels"):
        sp.plot_ternary(a, b, c, grid_levels=0)


def test_ternary_color_mismatch_raises(ternary_data, cleanup_figures):
    a, b, c = ternary_data
    with pytest.raises(ValueError, match="color_by"):
        sp.plot_ternary(a, b, c, color_by=[1.0])


def test_ternary_alias_and_export(ternary_data, cleanup_figures):
    a, b, c = ternary_data
    assert callable(sp.plot_ternary)
    assert callable(sp.ternary)
    assert "plot_ternary" in sp.__all__ and "ternary" in sp.__all__
    result = sp.ternary(a, b, c)
    assert result.fig is not None


def test_ternary_save_png(tmp_path, ternary_data, cleanup_figures):
    a, b, c = ternary_data
    result = sp.plot_ternary(a, b, c, labels=["砂", "粉", "黏"], color_by=a + b,
                             colorbar_label="有机质")
    paths = result.save(str(tmp_path / "ternary"), formats=("png",), dpi=100)
    assert paths[0].exists() and paths[0].stat().st_size > 0


def test_ternary_colorbar_label(cleanup_figures):
    """colorbar_label 参数生效（此前缺失导致 kwargs 透传崩溃）。"""
    a = np.array([0.5, 0.3])
    b = np.array([0.3, 0.4])
    c = np.array([0.2, 0.3])
    result = sp.plot_ternary(a, b, c, color_by=a + b, colorbar_label="有机质")
    assert result.fig.axes[-1].get_ylabel() == "有机质"


def test_volcano_legend_language(cleanup_figures):
    """图例语言跟随 lang：en 模式必须为英文。"""
    fc = np.array([1.5, -1.5, 0.1])
    p = np.array([0.01, 0.02, 0.5])
    sp.reset_style()
    try:
        result = sp.plot_volcano(fc, p, lang="en")
        texts = [t.get_text() for t in result.ax.get_legend().get_texts()]
        assert texts == ["Up-regulated", "Down-regulated", "Not significant"]
        result_zh = sp.plot_volcano(fc, p, lang="zh")
        texts_zh = [t.get_text() for t in result_zh.ax.get_legend().get_texts()]
        assert texts_zh == ["显著上调", "显著下调", "不显著"]
    finally:
        sp.reset_style()
