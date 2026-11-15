"""数据画像分析与智能图表推荐引擎单元测试。"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import numpy as np
import pytest

import sciplot as sp

pandas = pytest.importorskip("pandas")


class TestDataProfilingAndRecommendation:
    """验证多种科研数据结构的精准画像与反单调多样化图表推荐。"""

    def test_exports_present(self):
        for name in (
            "ColumnProfile",
            "DataProfile",
            "ChartRecommendation",
            "ChartRecommendationReport",
            "profile_data",
            "recommend_charts",
        ):
            assert name in sp.__all__
            assert hasattr(sp, name)

    def test_grouped_samples_prefers_raincloud_or_violin(self):
        rng = np.random.default_rng(21)
        groups = [rng.normal(0, 1, 40), rng.normal(1.5, 1.2, 40), rng.normal(0.5, 0.7, 40)]
        report = sp.recommend_charts(groups, columns=["Control", "Low", "High"])
        assert report.profile.shape_pattern == "grouped_samples"
        funcs = [r.sciplot_func for r in report.recommendations]
        assert funcs[0] == "plot_raincloud"
        assert "plot_violin" in funcs
        md = report.summary()
        assert "数据结构画像" in md and "plot_raincloud" in md

    def test_correlation_matrix_prefers_lower_heatmap_and_clustermap(self):
        rng = np.random.default_rng(3)
        corr = np.corrcoef(rng.normal(size=(5, 40)))
        report = sp.recommend_charts(corr, columns=[f"Var{i}" for i in range(5)])
        assert report.profile.shape_pattern == "square_corr"
        assert "correlation_matrix" in report.profile.special_hints
        funcs = [r.sciplot_func for r in report.recommendations]
        assert funcs[0] == "plot_heatmap"
        assert "plot_clustermap" in funcs

    def test_bivariate_small_vs_large_sample_anti_overplotting(self):
        rng = np.random.default_rng(99)
        small = pandas.DataFrame({"dose": rng.uniform(0, 10, 60), "response": rng.normal(5, 1, 60)})
        rep_small = sp.recommend_charts(small)
        assert rep_small.profile.shape_pattern == "bivariate"
        assert rep_small.recommendations[0].sciplot_func == "plot_marginal"

        large = pandas.DataFrame({"x": rng.normal(size=1200), "y": rng.normal(size=1200)})
        rep_large = sp.recommend_charts(large)
        assert rep_large.recommendations[0].sciplot_func == "plot_hexbin"

    def test_many_timeseries_warns_against_spaghetti(self):
        t = np.arange(30)
        df = pandas.DataFrame({"time": t, **{f"S{i}": np.sin(t * 0.2 + i) for i in range(6)}})
        rep = sp.recommend_charts(df, time_col="time")
        assert rep.profile.shape_pattern == "timeseries"
        assert rep.recommendations[0].sciplot_func in {"plot_bump", "plot_streamgraph"}
        assert rep.composite_plan and "paper_subplots" in rep.composite_plan

    def test_domain_specific_detection_volcano_paired_roc_flow_forest(self):
        rng = np.random.default_rng(1)
        volcano_df = pandas.DataFrame({"gene": ["G1", "G2", "G3"], "log2FC": [-2.1, 0.2, 3.0], "pvalue": [1e-4, 0.5, 1e-6]})
        assert sp.recommend_charts(volcano_df).recommendations[0].sciplot_func == "plot_volcano"

        paired_df = pandas.DataFrame({"before": rng.normal(10, 1, 20), "after": rng.normal(12, 1, 20)})
        assert sp.recommend_charts(paired_df).recommendations[0].sciplot_func == "plot_paired"

        roc_df = pandas.DataFrame({"y_true": [0, 1, 0, 1, 1, 0], "prob_a": [0.1, 0.9, 0.3, 0.8, 0.7, 0.2]})
        assert sp.recommend_charts(roc_df).recommendations[0].sciplot_func == "plot_roc"

        flow_df = pandas.DataFrame({"source": ["A", "B"], "target": ["X", "Y"], "value": [30, 50]})
        assert sp.recommend_charts(flow_df).recommendations[0].sciplot_func == "plot_sankey"

        forest_df = pandas.DataFrame({"effect": [0.8, 1.3], "ci_low": [0.5, 1.0], "ci_high": [1.1, 1.7]})
        assert sp.recommend_charts(forest_df).recommendations[0].sciplot_func == "plot_forest"

    def test_multivariate_and_category_scalar_and_csv_loading(self, tmp_path):
        rng = np.random.default_rng(42)
        multi_df = pandas.DataFrame({f"F{i}": rng.normal(size=50) for i in range(5)})
        rep_multi = sp.recommend_charts(multi_df)
        assert rep_multi.profile.shape_pattern == "multivariate"
        assert "plot_scatter_matrix" in [r.sciplot_func for r in rep_multi.recommendations]
        assert rep_multi.composite_plan and "hero_layout" in rep_multi.composite_plan

        cat_df = pandas.DataFrame({"category": [f"Item{i}" for i in range(6)], "delta": [-4.2, -1.5, 0.8, 2.3, 5.1, -0.4]})
        rep_cat = sp.recommend_charts(cat_df)
        assert rep_cat.profile.shape_pattern == "category_scalar"
        assert rep_cat.recommendations[0].sciplot_func == "plot_diverging_bar"

        csv_path = tmp_path / "sample.csv"
        cat_df.to_csv(csv_path, index=False)
        rep_csv = sp.recommend_charts(csv_path, goal="ranking")
        assert rep_csv.profile.n_rows == 6
        assert isinstance(rep_csv.to_dict(), dict)

    def test_univariate_skew_warning_and_invalid_goal(self):
        rng = np.random.default_rng(7)
        skewed = np.exp(rng.normal(0, 1.4, 80))
        rep = sp.recommend_charts(skewed)
        assert rep.profile.shape_pattern == "univariate"
        assert any("偏态" in w for w in rep.profile.warnings)
        assert rep.recommendations[0].sciplot_func == "plot_histogram"

        with pytest.raises(ValueError, match="goal"):
            sp.recommend_charts(skewed, goal="unknown_goal")

    def test_dict_input_disambiguates_bivariate_timeseries_multivariate_vs_grouped(self):
        rng = np.random.default_rng(11)
        x = rng.normal(size=1000)
        bivar_dict = {"x": x, "y": 0.7 * x + rng.normal(0, 0.5, 1000)}
        rep_bivar = sp.recommend_charts(bivar_dict)
        assert rep_bivar.profile.shape_pattern == "bivariate"
        assert rep_bivar.recommendations[0].sciplot_func == "plot_hexbin"

        t = np.arange(30)
        ts_dict = {
            "time": t,
            "Sensor_A": np.sin(t * 0.2),
            "Sensor_B": np.cos(t * 0.2),
            "Sensor_C": 0.1 * t,
        }
        rep_ts = sp.recommend_charts(ts_dict)
        assert rep_ts.profile.shape_pattern == "timeseries"
        assert rep_ts.recommendations[0].sciplot_func == "plot_multi_timeseries"

        multi_dict = {f"Feature_{i}": rng.normal(size=40) for i in range(4)}
        rep_multi = sp.recommend_charts(multi_dict)
        assert rep_multi.profile.shape_pattern == "multivariate"
        assert rep_multi.recommendations[0].sciplot_func == "plot_scatter_matrix"

        grouped_dict = {
            "Control": rng.normal(5.0, 0.8, 30),
            "Treatment_A": rng.normal(6.5, 0.9, 30),
            "Treatment_B": rng.normal(7.2, 0.7, 30),
        }
        rep_grp = sp.recommend_charts(grouped_dict)
        assert rep_grp.profile.shape_pattern == "grouped_samples"
        assert rep_grp.recommendations[0].sciplot_func == "plot_raincloud"
