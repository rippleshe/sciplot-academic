"""v1.15.0 新增图表函数、别名导出及视觉增强选项单元测试。"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

import sciplot as sp


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    plt.close("all")
    sp.reset_style()


class TestExportsAndAliases:
    """确认所有新增图表函数及简洁别名导出完整且转发一致。"""

    @pytest.mark.parametrize(
        "full_name,alias_name",
        [
            ("plot_pareto", "pareto"),
            ("plot_paired", "paired"),
            ("plot_fan", "fan"),
            ("plot_roc", "roc"),
            ("plot_calibration", "calibration"),
        ],
    )
    def test_exported_in_all_and_wrapped(self, full_name, alias_name):
        assert full_name in sp.__all__
        assert alias_name in sp.__all__
        full_fn = getattr(sp, full_name)
        alias_fn = getattr(sp, alias_name)
        assert callable(full_fn) and callable(alias_fn)
        assert getattr(alias_fn, "__wrapped__", None) is full_fn


class TestNewChartsV115:
    """针对 5 个新增图表的功能与边界校验测试。"""

    def test_plot_pareto_descending_and_save(self, tmp_path):
        cats = ["缺陷A", "缺陷B", "缺陷C", "缺陷D", "缺陷E"]
        vals = [15, 62, 8, 35, 4]
        res = sp.plot_pareto(
            cats, vals, xlabel="类型", ylabel="频数", title="Pareto", threshold=80.0,
            palette="blue-sky",
        )
        xt = [t.get_text() for t in res.ax.get_xticklabels()]
        assert xt[0] == "缺陷B" and xt[-1] == "缺陷E"
        saved = res.save(str(tmp_path / "pareto"), formats=("png",), dpi=90)
        assert saved[0].exists() and saved[0].stat().st_size > 0

        res_no_thr = sp.pareto(cats, vals, threshold=None, show_values=False)
        assert res_no_thr.fig is not None

    @pytest.mark.parametrize(
        "cats,vals,thr",
        [
            ([], [], 80.0),
            (["A"], [1.0, 2.0], 80.0),
            (["A", "B"], [-1.0, 5.0], 80.0),
            (["A", "B"], [0.0, 0.0], 80.0),
            (["A", "B"], [1.0, 2.0], 120.0),
        ],
    )
    def test_plot_pareto_validation_errors(self, cats, vals, thr):
        with pytest.raises(ValueError):
            sp.plot_pareto(cats, vals, threshold=thr)

    def test_plot_paired_basic_and_toggles(self):
        rng = np.random.default_rng(11)
        before = rng.normal(50, 6, 24)
        after = before + rng.normal(4.5, 2.0, 24)
        res = sp.plot_paired(
            before, after, labels=("基线", "随访"), ylabel="评分", title="配对对照",
            palette="coral-teal",
        )
        assert [t.get_text() for t in res.ax.get_xticklabels()] == ["基线", "随访"]
        assert any("Δ =" in t.get_text() for t in res.ax.texts)

        res_minimal = sp.paired(before, after, show_box=False, show_mean=False, show_stats=False)
        assert res_minimal.fig is not None

    def test_plot_paired_validation_errors(self):
        with pytest.raises(ValueError):
            sp.plot_paired([], [])
        with pytest.raises(ValueError):
            sp.plot_paired([1.0, 2.0], [1.0])
        with pytest.raises(ValueError):
            sp.plot_paired([1.0, np.nan], [2.0, 3.0])

    def test_plot_fan_samples_and_explicit_bands(self):
        rng = np.random.default_rng(7)
        t_hist = np.arange(0, 10)
        y_hist = 10 + 0.5 * t_hist + rng.normal(0, 0.3, size=10)
        t_future = np.arange(10, 22)
        noise = np.cumsum(rng.normal(0.3, 0.6, size=(80, len(t_future))), axis=1)
        samples = y_hist[-1] + noise

        res = sp.plot_fan(
            t_future, samples=samples, intervals=(50, 80, 95),
            history_x=t_hist, history_y=y_hist,
            xlabel="步长", ylabel="温度", palette="coral-teal",
        )
        assert len(res.ax.collections) >= 3  # 3 层嵌套置信区间

        center = np.median(samples, axis=0)
        bands = {80: (np.percentile(samples, 10, axis=0), np.percentile(samples, 90, axis=0))}
        res2 = sp.fan(t_future, center=center, bands=bands)
        assert res2.fig is not None

    def test_plot_fan_validation_errors(self):
        with pytest.raises(ValueError):
            sp.plot_fan([1], center=[1.0])
        with pytest.raises(ValueError):
            sp.plot_fan([1, 2, 3], samples=np.ones((1, 3)))
        with pytest.raises(ValueError):
            sp.plot_fan([1, 2, 3])

    def test_plot_roc_both_modes_and_multi_model(self):
        rng = np.random.default_rng(19)
        y_true = np.r_[np.zeros(80, dtype=int), np.ones(80, dtype=int)]
        scores = {
            "XGBoost": np.r_[rng.uniform(0.05, 0.55, 80), rng.uniform(0.45, 0.98, 80)],
            "Logistic": np.r_[rng.uniform(0.10, 0.65, 80), rng.uniform(0.35, 0.90, 80)],
        }
        res_roc = sp.plot_roc(y_true, scores, mode="roc", palette="blue-sky")
        leg_texts = [t.get_text() for t in res_roc.ax.get_legend().get_texts()]
        assert any("AUC =" in txt for txt in leg_texts)

        res_pr = sp.roc(y_true, scores, mode="pr", show_threshold=False)
        leg_pr = [t.get_text() for t in res_pr.ax.get_legend().get_texts()]
        assert any("AP =" in txt for txt in leg_pr)

    def test_plot_roc_validation_errors(self):
        with pytest.raises(ValueError):
            sp.plot_roc([0, 0, 0], [0.1, 0.2, 0.3])
        with pytest.raises(ValueError):
            sp.plot_roc([0, 1], [0.1, 0.9], mode="invalid")
        with pytest.raises(ValueError):
            sp.plot_roc([0, 1, 2], [0.1, 0.5, 0.9])

    def test_plot_calibration(self):
        rng = np.random.default_rng(31)
        p = rng.uniform(0.02, 0.98, 240)
        y = (rng.random(240) < p).astype(int)
        res = sp.plot_calibration(
            y, {"Calibrated": p, "Shifted": np.clip(p * 0.75 + 0.1, 0, 1)},
            n_bins=8, show_hist=True, palette="coral-teal",
        )
        leg = [t.get_text() for t in res.ax.get_legend().get_texts()]
        assert any("ECE=" in txt and "Brier=" in txt for txt in leg)

        res2 = sp.calibration(y, p, show_hist=False)
        assert res2.fig is not None

        with pytest.raises(ValueError):
            sp.plot_calibration(y, p * 1.5)


class TestExistingChartUpgrades:
    """验证已有核心图表新增视觉下限增强参数可正常运行。"""

    def test_scatter_fit_line_and_stats(self):
        rng = np.random.default_rng(5)
        x = np.linspace(0, 10, 45)
        y = 2.1 * x + 1.0 + rng.normal(0, 1.5, 45)
        res = sp.plot_scatter(x, y, fit_line=True, ci=True, show_stats=True, palette="coral-teal")
        assert any("R^2" in t.get_text() for t in res.ax.texts)
        assert len(res.ax.lines) >= 1

    def test_distribution_enhanced_options(self):
        rng = np.random.default_rng(8)
        groups = [rng.normal(0, 1, 40), rng.normal(1.2, 0.8, 40), rng.normal(2.1, 1.1, 40)]

        res_bar = sp.plot_bar(["A", "B", "C"], [10, 18, 14], yerr=[1.0, 1.5, 1.2], show_values=True)
        assert len(res_bar.ax.texts) >= 3

        res_gb = sp.plot_grouped_bar(
            ["T1", "T2"], {"M1": [10, 12], "M2": [14, 16]}, errors={"M1": [1, 1], "M2": [1.5, 1.2]}
        )
        assert res_gb.fig is not None

        res_box = sp.plot_box(groups, labels=["G1", "G2", "G3"], show_points=True, show_means=True)
        assert len(res_box.ax.collections) >= 3

        res_vio = sp.plot_violin(groups, labels=["G1", "G2", "G3"], show_box=True, show_points=True)
        assert len(res_vio.ax.collections) >= 3

        res_hist = sp.plot_histogram(groups[0], show_kde=True, show_median=True)
        assert len(res_hist.ax.lines) >= 2

    def test_heatmap_triangle_and_pvalues(self):
        mat = np.corrcoef(np.random.default_rng(12).normal(size=(4, 50)))
        pvals = np.full((4, 4), 0.2)
        pvals[1, 0] = 0.0005
        res = sp.plot_heatmap(
            mat, row_labels=["A", "B", "C", "D"], col_labels=["A", "B", "C", "D"],
            triangle="lower", show_values=True, p_values=pvals,
        )
        assert any("***" in t.get_text() for t in res.ax.texts)
        assert not res.ax.spines["top"].get_visible()
        assert not res.ax.spines["right"].get_visible()

    def test_scatter_matrix_upper_corr_and_pca_ellipse(self):
        rng = np.random.default_rng(15)
        X = rng.normal(size=(60, 4))
        labels = np.repeat([0, 1, 2], 20)

        res_sm = sp.plot_scatter_matrix(X[:, :3], columns=["F1", "F2", "F3"], upper="corr")
        assert len(res_sm.fig.axes) >= 9

        res_pca = sp.plot_pca(X, labels=labels, show_ellipse=True, palette="coral-teal")
        assert len(res_pca.ax.patches) >= 3  # 至少 3 个置信椭圆
