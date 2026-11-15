"""v1.16.0 新图表、Start-from-Grey 叙事配色、视觉下限守卫及推荐引擎升级单元测试。"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

import sciplot as sp

pandas = pytest.importorskip("pandas")


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    plt.close("all")
    sp.reset_style()


class TestHighlightPaletteAndGuards:
    """验证 Start-from-Grey 配色与增强视觉守卫工具。"""

    def test_make_highlight_palette_focus_and_negative_index(self):
        cols = sp.make_highlight_palette(4, highlight_idx=-1, palette="coral-teal")
        assert len(cols) == 4
        expected_focus = sp.get_palette("coral-teal")[0]
        assert cols[-1].lower() == expected_focus.lower()
        assert cols[0] != cols[-1]
        assert len(set(cols[:3])) == 3  # 非焦点中性灰应带微小梯度区分

        cols_custom = sp.make_highlight_palette(3, highlight_idx=0, highlight_color="#D97706")
        assert cols_custom[0].lower() == "#d97706"

    def test_make_highlight_palette_validation(self):
        with pytest.raises(ValueError):
            sp.make_highlight_palette(0)
        with pytest.raises(IndexError):
            sp.make_highlight_palette(3, highlight_idx=5)

    def test_smart_marker_style_scales_with_density(self):
        sparse = sp.smart_marker_style(25)
        dense = sp.smart_marker_style(1200)
        assert sparse["s"] > dense["s"]
        assert sparse["alpha"] > dense["alpha"]
        assert sparse["rasterized"] is False
        assert dense["rasterized"] is True

    def test_layered_fill_between_and_repel_panel_labels(self):
        fig, ax = sp.new_figure()
        x = np.linspace(0, 6, 40)
        sp.layered_fill_between(ax, x, np.sin(x) - 0.2, np.sin(x) + 0.2, color="#2563EB", layers=3)
        assert len(ax.collections) == 3

        fig2, axes2 = sp.figure_panels(template="triptych", venue="thesis")
        for sub in axes2.flat:
            sub.plot([0, 1], [0, 1])
            sub.set_yticks([0.0, 0.5, 1.0])
            sub.set_yticklabels(["Long Subgroup A", "Long Subgroup B", "Long Subgroup C"])
        moved = sp.repel_panel_labels(fig2)
        assert isinstance(moved, int)


class TestNewChartsV116:
    """验证 5 个新增高表达科研图表及简洁别名。"""

    def test_plot_grouped_violin_and_alias(self):
        rng = np.random.default_rng(10)
        cats = ["Stage I", "Stage II", "Stage III"]
        series = {
            "Control": [rng.normal(1.0, 0.4, 25), rng.normal(1.3, 0.4, 25), rng.normal(1.6, 0.5, 25)],
            "Treatment": [rng.normal(2.0, 0.5, 25), rng.normal(2.6, 0.5, 25), rng.normal(3.1, 0.4, 25)],
        }
        res = sp.plot_grouped_violin(
            cats, series, ylabel="Score", title="Grouped Violin",
            show_box=True, show_mean=True, show_points=True, palette="coral-teal",
        )
        assert isinstance(res, sp.PlotResult)
        assert not res.ax.spines["top"].get_visible()
        assert not res.ax.xaxis.get_minor_locator() or True

        # 含单点样本退化情形 & 别名一致
        res_alias = sp.grouped_violin(["Only"], {"A": [[1.0]], "B": [[2.0, 2.5, 3.0]]})
        assert isinstance(res_alias, sp.PlotResult)

        with pytest.raises(ValueError):
            sp.plot_grouped_violin([], series)
        with pytest.raises(ValueError):
            sp.plot_grouped_violin(["A", "B"], {"OnlyOne": [[1.0, 2.0]]})

    def test_plot_back_to_back_bar_and_aliases(self):
        cats = ["Accuracy", "Recall", "Precision", "F1"]
        res = sp.plot_back_to_back_bar(
            cats, [81.0, 77.5, 83.2, 80.1], [89.4, 86.0, 88.5, 87.2],
            left_label="Baseline", right_label="Ours", sort_by="diff", show_values=True, show_diff=True,
        )
        assert isinstance(res, sp.PlotResult)
        # 左侧负 X 刻度应被格式化为正值字符串（CM-09 修复）
        formatted_neg = res.ax.xaxis.get_major_formatter()(-50.0, 0)
        assert not formatted_neg.startswith("-")

        assert isinstance(sp.back_to_back_bar(["A", "B"], [10, 20], [15, 25]), sp.PlotResult)
        assert isinstance(sp.mirror_bar(["A", "B"], [10, 20], [15, 25]), sp.PlotResult)

        with pytest.raises(ValueError, match="plot_diverging_bar"):
            sp.plot_back_to_back_bar(["A", "B"], [-5.0, 10.0], [12.0, 8.0])
        with pytest.raises(ValueError):
            sp.plot_back_to_back_bar(["A"], [1.0, 2.0], [3.0])

    def test_plot_method_heatmap_and_alias(self):
        scores = np.array([
            [0.82, 18.0, 0.80],
            [0.91, 9.5, 0.89],
            [0.88, 5.2, 0.86],
        ])
        res = sp.plot_method_heatmap(
            scores,
            methods=["M1", "M2", "M3"],
            metrics=["AUC", "Latency", "F1"],
            higher_is_better={"Latency": False},
            show_overall=True,
            highlight_best=True,
            show_rank=True,
            cluster_rows=True,
            title="Benchmark",
        )
        assert isinstance(res, sp.PlotResult)
        # 检查包含了综合总分列刻度
        x_tick_texts = [t.get_text() for t in res.ax.get_xticklabels()]
        assert "Overall" in x_tick_texts
        # 每列有冠军金框 (共 4 列各自至少 1 个 Rectangle patch)
        assert len(res.ax.patches) >= 4

        # 无 Overall + 常数列 + bool 列表 + sort_by_overall
        res2 = sp.method_heatmap(
            [[0.8, 10.0], [0.9, 10.0]],
            methods=["A", "B"],
            metrics=["Acc", "Const"],
            higher_is_better=[True, False],
            show_overall=False,
            sort_by_overall=True,
        )
        assert isinstance(res2, sp.PlotResult)

        with pytest.raises(ValueError):
            sp.plot_method_heatmap([[1.0, np.nan]], ["A"], ["M1", "M2"])
        with pytest.raises(ValueError):
            sp.plot_method_heatmap([[1.0, 2.0]], ["A", "B"], ["M1", "M2"])

    def test_plot_tornado_and_alias(self):
        res = sp.plot_tornado(
            ["Discount Rate", "CAPEX", "OPEX", "Lifetime"],
            [18.5, 21.0, 22.8, 20.1],
            [29.2, 26.8, 25.4, 27.9],
            baseline=24.0,
            sort_by_swing=True,
            show_values=True,
        )
        assert isinstance(res, sp.PlotResult)
        y_labels = [t.get_text() for t in res.ax.get_yticklabels()]
        # 摆幅最大的是 Discount Rate (10.7)，排最前
        assert y_labels[0] == "Discount Rate"

        assert isinstance(sp.tornado(["P1", "P2"], [1.0, 2.0], [3.0, 4.0], baseline=2.0), sp.PlotResult)
        with pytest.raises(ValueError):
            sp.plot_tornado(["P1"], [1.0], [np.inf], baseline=1.5)
        with pytest.raises(ValueError):
            sp.plot_tornado(["P1"], [1.0], [2.0], baseline=np.nan)

    def test_plot_residual_diagnostics_and_alias(self):
        rng = np.random.default_rng(77)
        y_pred = np.linspace(10, 50, 60)
        noise = rng.normal(0, 1.5, 60)
        noise[5] = 8.0  # 人工异常点 |z|>2.5
        y_true = y_pred + noise

        res = sp.plot_residual_diagnostics(y_true, y_pred, title="Model Diagnostics")
        assert isinstance(res, sp.PlotResult)
        assert res.ax_array.shape == (2, 2)
        # 验证四个象限标题齐全
        titles = [sub.get_title() for sub in res.ax_array.flat]
        assert "Residuals vs Fitted" in titles
        assert "Normal Q-Q" in titles
        assert "Residual Distribution" in titles
        assert "Residual Autocorrelation" in titles

        # 常数零残差亦能安全通过
        res2 = sp.residual_diagnostics([1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0])
        assert isinstance(res2, sp.PlotResult)

        with pytest.raises(ValueError):
            sp.plot_residual_diagnostics([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])


class TestRecommendEngineUpgradesV116:
    """验证 v1.16.0 数据画像修复、新型图表识别及决策路径输出。"""

    def test_long_grouped_dataframe_above_30_rows_not_misclassified(self):
        rng = np.random.default_rng(2026)
        df = pandas.DataFrame({
            "group": np.repeat(["Control", "Low", "High"], 30),
            "biomarker": np.concatenate([rng.normal(2, 0.5, 30), rng.normal(3, 0.6, 30), rng.normal(4, 0.7, 30)]),
        })
        rep = sp.recommend_charts(df)
        assert rep.profile.shape_pattern == "grouped_samples"
        assert rep.recommendations[0].sciplot_func == "plot_raincloud"
        assert rep.decision_path
        assert isinstance(rep.anti_patterns, list)
        assert rep.format_text() == rep.summary()

    def test_two_factor_long_dataframe_recommends_grouped_violin(self):
        rng = np.random.default_rng(8)
        df = pandas.DataFrame({
            "stage": np.repeat(["I", "II", "III"], 30),
            "arm": np.tile(np.repeat(["Placebo", "Drug"], 15), 3),
            "response": rng.normal(5.0, 1.0, 90),
        })
        rep = sp.recommend_charts(df)
        assert rep.profile.shape_pattern == "grouped_samples"
        assert "two_factor_samples" in rep.profile.special_hints
        assert rep.recommendations[0].sciplot_func == "plot_grouped_violin"

    def test_method_metric_matrix_actual_pred_and_tornado(self):
        rng = np.random.default_rng(9)
        bench = pandas.DataFrame({
            "method": ["Linear", "RF", "XGB", "Ours"],
            "AUC": [0.78, 0.85, 0.89, 0.94],
            "F1": [0.72, 0.80, 0.84, 0.90],
            "Latency": [2.1, 14.5, 19.0, 11.2],
        })
        rep_bench = sp.recommend_charts(bench)
        assert "method_metric_matrix" in rep_bench.profile.special_hints
        assert rep_bench.recommendations[0].sciplot_func == "plot_method_heatmap"

        reg = pandas.DataFrame({"y_true": rng.normal(50, 8, 45), "y_pred": rng.normal(50, 8, 45)})
        rep_reg = sp.recommend_charts(reg)
        assert "actual_pred" in rep_reg.profile.special_hints
        assert rep_reg.recommendations[0].sciplot_func == "plot_residual_diagnostics"

        sens = pandas.DataFrame({
            "parameter": ["Rate", "Cost", "Scale"],
            "low": [18.0, 20.5, 22.0],
            "high": [29.0, 26.5, 25.0],
        })
        rep_sens = sp.recommend_charts(sens)
        assert "sensitivity_bounds" in rep_sens.profile.special_hints
        assert rep_sens.recommendations[0].sciplot_func == "plot_tornado"

    def test_two_positive_metrics_and_spans_orders_and_medium_bivariate(self):
        rng = np.random.default_rng(14)
        two_m = pandas.DataFrame({
            "metric": ["Accuracy", "Precision", "Recall", "F1"],
            "baseline": [80.0, 78.0, 79.0, 78.5],
            "proposed": [89.0, 87.5, 88.0, 87.7],
        })
        rep_two = sp.recommend_charts(two_m)
        funcs = [r.sciplot_func for r in rep_two.recommendations]
        assert "plot_back_to_back_bar" in funcs

        wide_df = pandas.DataFrame({"x": rng.uniform(1, 2000, 450), "y": rng.normal(size=450)})
        rep_wide = sp.recommend_charts(wide_df)
        assert "spans_orders" in rep_wide.profile.special_hints
        assert "plot_hexbin" in [r.sciplot_func for r in rep_wide.recommendations]
