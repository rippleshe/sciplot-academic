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


def test_volcano_annotations_avoid_each_other_legend_and_axes(cleanup_figures):
    """自动标注必须按真实像素边界避让，而不是只修改抽象 offset。"""
    rng = np.random.default_rng(7)
    fc = np.r_[rng.normal(0, 0.9, 260), -2.95, -2.82, -2.68, -2.53, 2.70, 2.84]
    p = np.r_[rng.random(260) ** 2, [1e-8, 1.1e-8, 1.3e-8, 1.6e-8, 1.2e-8, 1.5e-8]]
    labels = [f"G{i}" for i in range(260)] + [
        "TOP_LEFT_A", "TOP_LEFT_B", "TOP_LEFT_C", "TOP_LEFT_D",
        "TOP_RIGHT_A", "TOP_RIGHT_B",
    ]
    result = sp.plot_volcano(fc, p, labels=labels, annotate_top=True, top_n=6)
    result.fig.canvas.draw()
    renderer = result.fig.canvas.get_renderer()
    annotations = [t for t in result.ax.texts if t.get_text().startswith("TOP_")]
    assert len(annotations) >= 4

    boxes = [t.get_window_extent(renderer=renderer).expanded(1.02, 1.05) for t in annotations]
    for i, box_a in enumerate(boxes):
        for box_b in boxes[i + 1:]:
            assert not box_a.overlaps(box_b), "Volcano top 标签仍发生像素级重叠"

    legend = result.ax.get_legend()
    assert legend is not None
    legend_box = legend.get_window_extent(renderer=renderer)
    axes_box = result.ax.get_window_extent(renderer=renderer)
    for box in boxes:
        assert not box.overlaps(legend_box), "Volcano 标签与图例重叠"
        assert box.x0 >= axes_box.x0 - 1.0 and box.x1 <= axes_box.x1 + 1.0
        assert box.y0 >= axes_box.y0 - 1.0 and box.y1 <= axes_box.y1 + 1.0


def test_volcano_scatter_kwargs_do_not_duplicate_semantic_keys(volcano_data, cleanup_figures):
    fc, p, labels = volcano_data
    result = sp.plot_volcano(
        fc,
        p,
        labels=labels,
        annotate_top=False,
        s=31,
        alpha=0.42,
        c="#000000",
    )
    scatter = result.ax.collections[0]
    assert scatter.get_sizes()[0] == pytest.approx(31)
    assert scatter.get_alpha() == pytest.approx(0.42)
    # c=... 不得覆盖 Volcano 上调/下调/不显著三分类的语义色。
    unique = {tuple(c[:3].round(2)) for c in scatter.get_facecolors()}
    assert len(unique) == 3
