"""视觉下限守卫工具与 vivid-illustration 精选配色测试。"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from matplotlib.ticker import NullLocator
import numpy as np
import pytest

import sciplot as sp


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    plt.close("all")
    sp.reset_style()


class TestVividPalettes:
    """验证 vivid-illustration 精选配色方案与连续色阶派生函数。"""

    def test_vivid_palettes_exported_and_subsets(self):
        names = sp.list_vivid_palettes()
        assert len(names) >= 7
        for name in ("olive-apricot", "coral-teal", "blue-pink", "blue-sky", "soft-forest", "pastel-girl", "ocean-breeze"):
            assert name in names
            colors = sp.get_palette(name)
            assert len(colors) >= 4
            assert sp.get_palette(f"{name}-2") == colors[:2]
            assert name in sp.VIVID_PALETTES

    def test_make_palette_cmap_sequential_and_diverging(self):
        seq = sp.make_palette_cmap("coral-teal", kind="sequential")
        div = sp.make_palette_cmap("coral-teal", kind="diverging")
        assert isinstance(seq, LinearSegmentedColormap)
        assert isinstance(div, LinearSegmentedColormap)
        # 发散色阶中点接近白色
        mid_r, mid_g, mid_b, _ = div(0.5)
        assert mid_r > 0.9 and mid_g > 0.9 and mid_b > 0.9

    def test_make_palette_cmap_invalid_kind_raises(self):
        with pytest.raises(ValueError, match="kind"):
            sp.make_palette_cmap("coral-teal", kind="categorical")


class TestVisualGuards:
    """验证坐标轴净化、柔和轮廓、标签排斥与视觉异常巡检。"""

    def test_polish_axis_removes_categorical_minor_ticks_and_spines(self):
        fig, ax = plt.subplots()
        ax.bar(["A", "B", "C"], [3.0, 5.0, 2.0])
        sp.polish_axis(ax, categorical_axis="x", clean_spines=True, grid="y", max_num_ticks=5)
        assert isinstance(ax.xaxis.get_minor_locator(), NullLocator)
        assert not ax.spines["top"].get_visible()
        assert not ax.spines["right"].get_visible()
        assert ax.spines["left"].get_visible()
        assert ax.spines["bottom"].get_visible()

    def test_polish_axis_dark_theme_adaptive_spine(self):
        sp.setup_style("nature", theme="dark")
        fig, ax = plt.subplots()
        ax.plot([0, 1, 2], [1, 3, 2])
        sp.polish_axis(ax, clean_spines=True, grid="both")
        r, g, b, _ = ax.spines["left"].get_edgecolor()
        assert (r + g + b) / 3 > 0.5  # 深底自动选用浅色轴框

    def test_style_patch_edges_darkens_outline(self):
        fig, ax = plt.subplots()
        bars = ax.bar([0, 1], [4.0, 7.0])
        colors = ["#6283B2", "#E39B7E"]
        sp.style_patch_edges(bars, colors, fill_alpha=0.85, darken_amount=0.30)
        for patch, orig in zip(bars, colors):
            fc = patch.get_facecolor()[:3]
            ec = patch.get_edgecolor()[:3]
            assert sum(ec) < sum(to_rgb(orig))
            assert np.allclose(fc, to_rgb(orig), atol=0.02)

    def test_truncate_tick_labels(self):
        fig, ax = plt.subplots()
        ax.barh([0, 1], [1.0, 2.0])
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["Short", "VeryLongCategoryIdentifierNameExceedingLimit"])
        sp.truncate_tick_labels(ax, axis="y", max_len=14)
        out = [t.get_text() for t in ax.get_yticklabels()]
        assert out[0] == "Short"
        assert len(out[1]) <= 14 and out[1].endswith("...")

    def test_pick_best_corner_avoids_dense_cluster(self):
        fig, ax = plt.subplots()
        # 所有点集中于右上角
        x = np.linspace(7.0, 9.8, 30)
        y = np.linspace(7.0, 9.8, 30)
        ax.scatter(x, y)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        loc = sp.pick_best_corner(ax, x, y, prefer=("upper right", "lower left", "upper left", "lower right"))
        assert loc != "upper right"

    def test_smart_labels_separates_overlapping_texts(self):
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        points = [(5.0, 5.0), (5.05, 5.02), (4.98, 4.97), (5.02, 5.05)]
        texts = [ax.text(x, y, f"Label_{i}", fontsize=8) for i, (x, y) in enumerate(points)]
        sp.smart_labels(ax, texts, anchor_xy=points, add_connectors=True, pad_px=4.0)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        boxes = [t.get_window_extent(renderer) for t in texts]
        overlaps = sum(
            1 for i in range(len(boxes)) for j in range(i + 1, len(boxes))
            if boxes[i].overlaps(boxes[j])
        )
        assert overlaps == 0

    def test_inspect_figure_guards_and_audit_integration(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [2, 4, 6])
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.text(-0.5, 1.4, "OutOfBoundsText", transform=ax.transAxes)
        warnings_list = sp.inspect_figure_guards(fig)
        assert any("越界" in w for w in warnings_list)

        # 默认 check_visual_guards=False 保持原有 issues 契约；显式开启则拦截
        rep_soft = sp.audit_figure(fig, verbose=False)
        assert rep_soft["guard_warnings"]
        assert rep_soft["safe"] is True

        rep_strict = sp.audit_figure(fig, check_visual_guards=True, verbose=False)
        assert rep_strict["safe"] is False
        assert any("越界" in issue for issue in rep_strict["issues"])
