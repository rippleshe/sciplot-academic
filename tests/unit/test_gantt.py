"""
Round-28 tests for plot_gantt (甘特图).
"""

from __future__ import annotations

import datetime

import numpy as np
import pytest

import sciplot as sp


def test_gantt_basic_numeric(cleanup_figures):
    result = sp.plot_gantt(
        ["任务A", "任务B", "任务C"],
        start=[0, 10, 30], duration=[10, 20, 20],
        xlabel="天数",
    )
    assert result.fig is not None
    # 3 个条形 patch
    assert len(result.ax.patches) == 3
    yt = [t.get_text() for t in result.ax.get_yticklabels()]
    assert yt == ["任务A", "任务B", "任务C"]


def test_gantt_with_end(cleanup_figures):
    """提供 end 时自动推导 duration。"""
    result = sp.plot_gantt(
        ["A", "B"], start=[1.0, 5.0], end=[4.0, 9.0]
    )
    assert result.fig is not None
    widths = [p.get_width() for p in result.ax.patches]
    assert widths == pytest.approx([3.0, 4.0])


def test_gantt_datetime_axis(cleanup_figures):
    starts = [datetime.date(2024, 1, 1), datetime.date(2024, 1, 15)]
    result = sp.plot_gantt(
        ["阶段1", "阶段2"], start=starts, duration=[14, 21]
    )
    assert result.fig is not None


def test_gantt_datetime_with_end(cleanup_figures):
    starts = [datetime.datetime(2024, 1, 1), datetime.datetime(2024, 1, 10)]
    ends = [datetime.datetime(2024, 1, 8), datetime.datetime(2024, 1, 20)]
    result = sp.plot_gantt(["A", "B"], start=starts, end=ends)
    assert result.fig is not None


def test_gantt_color_by_categories(cleanup_figures):
    result = sp.plot_gantt(
        ["A", "B", "C"], start=[0, 1, 2], duration=[1, 1, 1],
        color_by=["开发", "开发", "测试"],
    )
    legend = result.ax.get_legend()
    assert legend is not None
    texts = [t.get_text() for t in legend.get_texts()]
    assert texts == ["开发", "测试"]


def test_gantt_no_labels(cleanup_figures):
    result = sp.plot_gantt(["A"], start=[0.0], duration=[1.0], show_labels=False)
    assert len(result.ax.get_yticklabels()) == 0


def test_gantt_empty_tasks_raises(cleanup_figures):
    with pytest.raises(ValueError, match="tasks"):
        sp.plot_gantt([], [], [])


def test_gantt_length_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="不一致"):
        sp.plot_gantt(["A", "B"], start=[0.0], duration=[1.0, 2.0])


def test_gantt_bad_duration_raises(cleanup_figures):
    with pytest.raises(ValueError, match="duration"):
        sp.plot_gantt(["A"], start=[0.0], duration=[0.0])
    with pytest.raises(ValueError, match="duration"):
        sp.plot_gantt(["A"], start=[0.0], duration=[-1.0])


def test_gantt_end_before_start_raises(cleanup_figures):
    with pytest.raises(ValueError, match="end 必须全部大于 start"):
        sp.plot_gantt(["A"], start=[5.0], end=[3.0])


def test_gantt_both_duration_and_end_raises(cleanup_figures):
    with pytest.raises(ValueError, match="二选一"):
        sp.plot_gantt(["A"], start=[0.0], duration=[1.0], end=[2.0])


def test_gantt_neither_duration_nor_end_raises(cleanup_figures):
    with pytest.raises(ValueError, match="duration 或 end"):
        sp.plot_gantt(["A"], start=[0.0])


def test_gantt_color_by_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="color_by"):
        sp.plot_gantt(["A", "B"], start=[0.0, 1.0], duration=[1.0, 1.0],
                      color_by=["x"])


def test_gantt_alias_and_export(cleanup_figures):
    assert callable(sp.plot_gantt)
    assert callable(sp.gantt)
    assert "plot_gantt" in sp.__all__ and "gantt" in sp.__all__
    result = sp.gantt(["A"], start=[0.0], duration=[1.0])
    assert result.fig is not None


def test_gantt_milestones_dependencies_now(cleanup_figures):
    """里程碑/依赖/当前线组合绘制。"""
    result = sp.plot_gantt(
        ["A", "B", "C"], start=[0.0, 1.0, 2.0], duration=[1.0, 1.0, 1.0],
        milestones={"检查点": 2.5}, dependencies=[(0, 1)], now=1.5,
    )
    assert result.fig is not None


def test_gantt_bad_dependencies_raises(cleanup_figures):
    with pytest.raises(ValueError, match="dependencies"):
        sp.plot_gantt(
            ["A", "B"], start=[0.0, 1.0], duration=[1.0, 1.0],
            dependencies=[(0, 5)],
        )


def test_gantt_groups_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError, match="groups"):
        sp.plot_gantt(
            ["A", "B"], start=[0.0, 1.0], duration=[1.0, 1.0],
            groups=["x"],
        )


def test_gantt_groups_legend(cleanup_figures):
    """groups 阶段色带与图例。"""
    result = sp.plot_gantt(
        ["A", "B", "C"], start=[0.0, 1.0, 2.0], duration=[1.0, 1.0, 1.0],
        groups=["前期", "中期", "后期"],
    )
    legend = result.ax.get_legend()
    assert legend is not None
    texts = [t.get_text() for t in legend.get_texts()]
    assert "前期" in texts and "后期" in texts


def test_gantt_save_png(tmp_path, cleanup_figures):
    result = sp.plot_gantt(
        ["数据采集", "模型训练", "论文撰写"],
        start=[0, 10, 30], duration=[10, 20, 20],
        xlabel="天数",
    )
    paths = result.save(str(tmp_path / "gantt"), formats=("png",), dpi=100)
    assert paths[0].exists() and paths[0].stat().st_size > 0


def test_gantt_legend_dedup_colorby_groups(cleanup_figures):
    """color_by 与 groups 同标签时，图例只出现一次且保持首次出现顺序。"""
    tasks = [f"T{i}" for i in range(6)]
    result = sp.plot_gantt(
        tasks, [0, 1, 2, 3, 4, 5], [1, 1, 1, 1, 1, 1],
        color_by=["前期", "前期", "中期", "中期", "后期", "后期"],
        groups=["前期", "前期", "中期", "中期", "后期", "后期"],
    )
    leg = result.ax.get_legend()
    assert leg is not None
    labels = [t.get_text() for t in leg.get_texts()]
    assert labels == ["前期", "中期", "后期"], f"图例应去重且有序: {labels}"
