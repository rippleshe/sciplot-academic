"""
Round-31 tests for plot_volcano (火山图).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp


@pytest.fixture()
def volcano_data():
    rng = np.random.default_rng(21)
    n = 300
    fc = rng.normal(0, 1.2, n)
    p = 10 ** (-rng.uniform(0, 4, n))
    # 掺入显著差异
    fc[:30] = rng.uniform(1.5, 3.0, 30)
    p[:30] = 10 ** (-rng.uniform(2, 8, 30))
    labels = [f"gene_{i}" for i in range(n)]
    return fc, p, labels


def test_volcano_basic(volcano_data, cleanup_figures):
    fc, p, labels = volcano_data
    result = sp.plot_volcano(fc, p, labels=labels)
    assert result.fig is not None
    # 图例三项
    legend = result.ax.get_legend()
    assert legend is not None
    assert len(legend.get_texts()) == 3


def test_volcano_three_color_classes(volcano_data, cleanup_figures):
    """上调/下调/不显著三类颜色互不相同。"""
    fc, p, labels = volcano_data
    result = sp.plot_volcano(fc, p, labels=labels)
    scatter = result.ax.collections[0]
    facecolors = np.asarray(scatter.get_facecolors())
    unique = {tuple(c[:3].round(2)) for c in facecolors}
    assert len(unique) == 3


def test_volcano_annotation_count(volcano_data, cleanup_figures):
    fc, p, labels = volcano_data
    result = sp.plot_volcano(fc, p, labels=labels, top_n=5)
    n_annot = len([t for t in result.ax.texts if t.get_text()])
    assert n_annot == 5


def test_volcano_no_annotation(volcano_data, cleanup_figures):
    fc, p, labels = volcano_data
    result = sp.plot_volcano(fc, p, labels=labels, annotate_top=False)
    assert len(result.ax.texts) == 0


def test_volcano_no_labels_no_annotation(volcano_data, cleanup_figures):
    fc, p, _ = volcano_data
    result = sp.plot_volcano(fc, p)
    assert len(result.ax.texts) == 0


def test_volcano_zero_p_values(volcano_data, cleanup_figures):
    """p=0 时必须正常处理（不产生 inf）。"""
    fc, p, labels = volcano_data
    p2 = p.copy()
    p2[0] = 0.0
    result = sp.plot_volcano(fc, p2, labels=labels)
    assert result.fig is not None
    ys = np.asarray(result.ax.collections[0].get_offsets())[:, 1]
    assert np.all(np.isfinite(ys))


def test_volcano_thresholds_lines(volcano_data, cleanup_figures):
    fc, p, _ = volcano_data
    result = sp.plot_volcano(fc, p)
    # 3 条阈值线
    lines = [ln for ln in result.ax.lines if ln.get_linestyle() != "-"]
    assert len(lines) == 3


def test_volcano_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="不一致"):
        sp.plot_volcano([1.0, 2.0], [0.1, 0.2, 0.3])


def test_volcano_invalid_p_raises(cleanup_figures):
    with pytest.raises(ValueError, match="p_values"):
        sp.plot_volcano([1.0, 2.0], [0.1, -0.1])
    with pytest.raises(ValueError, match="p_values"):
        sp.plot_volcano([1.0, 2.0], [0.1, 1.5])


def test_volcano_nan_fc_raises(cleanup_figures):
    with pytest.raises(ValueError, match="log2fc"):
        sp.plot_volcano([1.0, np.nan], [0.1, 0.2])


def test_volcano_bad_thresholds_raise(volcano_data, cleanup_figures):
    fc, p, _ = volcano_data
    with pytest.raises(ValueError, match="p_threshold"):
        sp.plot_volcano(fc, p, p_threshold=0.0)
    with pytest.raises(ValueError, match="fc_threshold"):
        sp.plot_volcano(fc, p, fc_threshold=-1.0)


def test_volcano_label_mismatch_raises(volcano_data, cleanup_figures):
    fc, p, _ = volcano_data
    with pytest.raises(ValueError, match="labels"):
        sp.plot_volcano(fc, p, labels=["x"])


def test_volcano_alias_and_export(volcano_data, cleanup_figures):
    fc, p, labels = volcano_data
    assert callable(sp.plot_volcano)
    assert callable(sp.volcano)
    assert "plot_volcano" in sp.__all__ and "volcano" in sp.__all__
    result = sp.volcano(fc, p, labels=labels)
    assert result.fig is not None


def test_volcano_save_png(tmp_path, volcano_data, cleanup_figures):
    fc, p, labels = volcano_data
    result = sp.plot_volcano(fc, p, labels=labels)
    paths = result.save(str(tmp_path / "volcano"), formats=("png",), dpi=100)
    assert paths[0].exists() and paths[0].stat().st_size > 0


def test_volcano_annotation_stagger(cleanup_figures):
    """近邻 top 基因标注应纵向错开避免重叠。"""
    rng = np.random.default_rng(7)
    fc = np.r_[rng.normal(0, 1, 300), 2.9, 3.0]
    p = np.r_[rng.random(300) ** 3, 1e-7, 1e-7]
    labels = [f"G{i}" for i in range(300)] + ["TOP_A", "TOP_B"]
    result = sp.plot_volcano(fc, p, labels=labels, annotate_top=True, top_n=8)
    texts = [t for t in result.ax.texts if t.get_text() in ("TOP_A", "TOP_B")]
    assert len(texts) == 2
    ys = [t.get_position()[1] for t in texts]
    assert abs(ys[0] - ys[1]) > 0.5, "近邻标签未错开"
