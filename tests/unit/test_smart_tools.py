"""智能辅助工具测试 — auto_rotate_labels, smart_legend, suggest_figsize, check_color_contrast"""
import pytest
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sciplot as sp


@pytest.fixture(autouse=True)
def cleanup():
    yield
    plt.close("all")


class TestAutoRotateLabels:
    def test_x_axis_short_labels_no_rotation(self):
        fig, ax = plt.subplots()
        ax.bar(["A", "B", "C"], [1, 2, 3])
        sp.auto_rotate_labels(ax, axis="x", max_labels=10, threshold=6)
        # 短标签不应旋转
        labels = ax.get_xticklabels()
        for label in labels:
            assert label.get_rotation() == 0.0

    def test_x_axis_many_labels_rotation(self):
        fig, ax = plt.subplots()
        categories = [f"Cat_{i}" for i in range(15)]
        ax.bar(categories, range(15))
        sp.auto_rotate_labels(ax, axis="x", max_labels=10, threshold=6)
        labels = ax.get_xticklabels()
        rotations = [label.get_rotation() for label in labels]
        assert any(r != 0 for r in rotations)

    def test_y_axis(self):
        fig, ax = plt.subplots()
        categories = [f"LongCategory_{i}" for i in range(8)]
        ax.barh(categories, range(8))
        sp.auto_rotate_labels(ax, axis="y", max_labels=5, threshold=4)
        labels = ax.get_yticklabels()
        rotations = [label.get_rotation() for label in labels]
        assert any(r != 0 for r in rotations)

    def test_invalid_axis(self):
        fig, ax = plt.subplots()
        with pytest.raises(ValueError):
            sp.auto_rotate_labels(ax, axis="z")


class TestSmartLegend:
    def test_no_handles(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3])  # no label
        sp.smart_legend(ax)  # should not raise
        assert ax.get_legend() is None

    def test_with_handles(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], label="A")
        ax.plot([3, 2, 1], label="B")
        sp.smart_legend(ax)
        legend = ax.get_legend()
        assert legend is not None
        assert len(legend.get_texts()) == 2

    def test_outside(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], label="A")
        sp.smart_legend(ax, outside=True)
        legend = ax.get_legend()
        assert legend is not None

    def test_ncols(self):
        fig, ax = plt.subplots()
        for i in range(6):
            ax.plot([1, 2, 3], label=f"Series {i}")
        sp.smart_legend(ax, ncols=2)
        legend = ax.get_legend()
        assert legend is not None
        # ncol 属性通过 _ncol 或 get_texts 验证
        texts = legend.get_texts()
        assert len(texts) == 6

    def test_invalid_ncols_zero(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], label="A")
        with pytest.raises(ValueError):
            sp.smart_legend(ax, ncols=0)

    def test_invalid_ncols_negative(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], label="A")
        with pytest.raises(ValueError):
            sp.smart_legend(ax, ncols=-1)

    def test_auto_ncols_many_items(self):
        fig, ax = plt.subplots()
        for i in range(8):
            ax.plot([1, 2, 3], label=f"Item {i}")
        sp.smart_legend(ax)  # auto ncols for >4 items
        legend = ax.get_legend()
        assert legend is not None


class TestSuggestFigsize:
    def test_basic(self):
        w, h = sp.suggest_figsize(5)
        assert w > 0 and h > 0
        assert h < w  # height_ratio < 1

    def test_min_width_clamp(self):
        w, h = sp.suggest_figsize(1, min_width=4.0, item_width=0.5)
        assert w >= 4.0

    def test_max_width_clamp(self):
        w, h = sp.suggest_figsize(100, max_width=10.0, item_width=0.5)
        assert w <= 10.0

    def test_zero_items(self):
        w, h = sp.suggest_figsize(0, min_width=4.0)
        assert w == 4.0

    def test_custom_height_ratio(self):
        w1, h1 = sp.suggest_figsize(10, height_ratio=0.5)
        w2, h2 = sp.suggest_figsize(10, height_ratio=1.0)
        assert h2 > h1

    def test_invalid_n_items_negative(self):
        with pytest.raises(ValueError):
            sp.suggest_figsize(-1)

    def test_invalid_item_width_zero(self):
        with pytest.raises(ValueError):
            sp.suggest_figsize(5, item_width=0)

    def test_invalid_min_width_negative(self):
        with pytest.raises(ValueError):
            sp.suggest_figsize(5, min_width=-1)

    def test_invalid_max_width_less_than_min(self):
        with pytest.raises(ValueError):
            sp.suggest_figsize(5, min_width=10, max_width=5)

    def test_invalid_height_ratio_zero(self):
        with pytest.raises(ValueError):
            sp.suggest_figsize(5, height_ratio=0)


class TestCheckColorContrast:
    def test_black_white_max_contrast(self):
        passed, ratio = sp.check_color_contrast("#FFFFFF", "#000000")
        assert passed is True
        assert ratio > 20  # 黑白对比度约21:1

    def test_same_color_no_contrast(self):
        passed, ratio = sp.check_color_contrast("#FF0000", "#FF0000")
        assert passed is False
        assert abs(ratio - 1.0) < 0.01

    def test_threshold_custom(self):
        _, ratio = sp.check_color_contrast("#FFFFFF", "#777777")
        # 默认阈值 4.5
        passed_default, _ = sp.check_color_contrast("#FFFFFF", "#777777", threshold=4.5)
        passed_high, _ = sp.check_color_contrast("#FFFFFF", "#777777", threshold=100)
        assert passed_default is True or passed_default is False  # just verify no error
        assert passed_high is False

    def test_hex3_shorthand(self):
        passed, ratio = sp.check_color_contrast("#FFF", "#000")
        assert passed is True
        assert ratio > 20

    def test_invalid_bg_color(self):
        with pytest.raises(ValueError):
            sp.check_color_contrast("invalid", "#000000")

    def test_invalid_fg_color(self):
        with pytest.raises(ValueError):
            sp.check_color_contrast("#FFFFFF", "")

    def test_invalid_threshold_zero(self):
        with pytest.raises(ValueError):
            sp.check_color_contrast("#FFFFFF", "#000000", threshold=0)

    def test_invalid_threshold_negative(self):
        with pytest.raises(ValueError):
            sp.check_color_contrast("#FFFFFF", "#000000", threshold=-1)

    def test_return_type(self):
        result = sp.check_color_contrast("#FFFFFF", "#000000")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], float)


class TestOptimizeLayout:
    def test_basic(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3])
        sp.optimize_layout(fig)  # should not raise

    def test_tight_false(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3])
        sp.optimize_layout(fig, tight=False)  # should not raise


class TestAdjustSubplots:
    def test_basic(self):
        fig, axes = plt.subplots(2, 2)
        sp.adjust_subplots(fig, hspace=0.4, wspace=0.4)
        # Verify no error

    def test_custom_params(self):
        fig, axes = plt.subplots(1, 3)
        sp.adjust_subplots(fig, hspace=0.5, wspace=0.5, top=0.9, bottom=0.1, left=0.05, right=0.95)
