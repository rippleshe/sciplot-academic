"""
Round-48 tests for audit_figure & save(audit=) (投稿质量防线).
"""

from __future__ import annotations

import warnings

import numpy as np
import pytest
from matplotlib.figure import Figure

import sciplot as sp


# ── audit_figure ───────────────────────────────────────────────

def test_audit_single_clean(cleanup_figures):
    """规范单图：无问题。"""
    fig, ax = sp.plot_line(np.arange(10), np.random.rand(10),
                           xlabel="X", ylabel="Y")
    report = sp.audit_figure(fig, verbose=False)
    assert report["safe"] is True
    assert report["issues"] == []


def test_audit_missing_axis_labels(cleanup_figures):
    """无轴标签应被检出。"""
    fig, ax = sp.plot_line(np.arange(10), np.random.rand(10))
    report = sp.audit_figure(fig, verbose=False)
    assert report["safe"] is False
    assert any("未标注" in i for i in report["issues"])


def test_audit_missing_panel_labels(cleanup_figures):
    """多面板无标签应被检出。"""
    fig, axes = sp.paper_subplots(1, 2, venue="thesis")
    axes[0].plot([1, 2, 3])
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("y")
    axes[1].plot([1, 2, 3])
    axes[1].set_xlabel("x")
    axes[1].set_ylabel("y")
    report = sp.audit_figure(fig, verbose=False)
    assert any("面板标签" in i for i in report["issues"])


def test_audit_panel_labels_present(cleanup_figures):
    """figure_panels 生成的面板标签可通过审计。"""
    fig, axes = sp.figure_panels(1, 2)
    axes[0].plot([1, 2, 3])
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("y")
    axes[1].plot([1, 2, 3])
    axes[1].set_xlabel("x")
    axes[1].set_ylabel("y")
    report = sp.audit_figure(fig, verbose=False)
    assert not any("面板标签" in i for i in report["issues"])


def test_audit_colorbar_is_not_a_panel(cleanup_figures):
    """色条轴不应被误判为第二个论文面板。"""
    fig, ax = sp.plot_hexbin(
        np.linspace(0, 1, 60),
        np.linspace(0, 1, 60) ** 2,
        xlabel="X",
        ylabel="Y",
        colorbar_label="Count",
    )
    report = sp.audit_figure(fig, verbose=False)
    assert not any("面板标签" in issue for issue in report["issues"])


def test_audit_twin_axis_is_not_a_panel(cleanup_figures):
    """共享同一绘图区的第二坐标轴不应触发多面板警告。"""
    fig, ax = sp.new_figure("nature")
    ax.plot([0, 1], [0, 1])
    ax.set_xlabel("X")
    ax.set_ylabel("Left")
    ax2 = ax.twinx()
    ax2.plot([0, 1], [1, 2])
    ax2.set_ylabel("Right")
    report = sp.audit_figure(fig, verbose=False)
    assert not any("面板标签" in issue for issue in report["issues"])


def test_audit_marginal_axes_are_auxiliary(cleanup_figures):
    """边际分布轴属于一个组合统计图，而不是三个独立面板。"""
    x = np.linspace(-2, 2, 80)
    y = 0.7 * x + np.sin(x)
    fig, ax = sp.plot_marginal(x, y, xlabel="X", ylabel="Y")
    report = sp.audit_figure(fig, verbose=False)
    assert not any("面板标签" in issue for issue in report["issues"])


def test_audit_small_font(cleanup_figures):
    """小于 5pt 的文本应被检出。"""
    fig, ax = sp.plot_line(np.arange(10), np.random.rand(10),
                           xlabel="X", ylabel="Y")
    ax.text(0.5, 0.5, "tiny", fontsize=4)
    report = sp.audit_figure(fig, verbose=False)
    assert any("字号" in i for i in report["issues"])


def test_audit_disabled_checks(cleanup_figures):
    """可关闭单项检查。"""
    fig, ax = sp.plot_line(np.arange(10), np.random.rand(10))
    report = sp.audit_figure(fig, verbose=False,
                             check_axis_labels=False)
    assert report["safe"] is True


def test_audit_3d_z_axis(cleanup_figures):
    """3D 图审计应检查 z 轴标签。"""
    import numpy as np

    # 带 z 标签：clean
    rng = np.random.default_rng(0)
    fig, ax = sp.plot_3d_scatter(
        rng.random(20), rng.random(20), rng.random(20),
        xlabel="X", ylabel="Y", zlabel="Z",
    )
    report = sp.audit_figure(fig, verbose=False, check_axis_labels=True)
    assert report["safe"] is True

    # 缺 z 标签：检出
    fig2, ax2 = sp.plot_3d_scatter(
        rng.random(20), rng.random(20), rng.random(20),
        xlabel="X", ylabel="Y",
    )
    report2 = sp.audit_figure(fig2, verbose=False, check_axis_labels=True)
    assert not report2["safe"]
    assert any("z 轴" in i for i in report2["issues"])


def test_audit_exported(cleanup_figures):
    assert callable(sp.audit_figure)
    assert "audit_figure" in sp.__all__


# ── save(audit=) 集成 ──────────────────────────────────────────

def test_save_audit_warns(tmp_path, cleanup_figures):
    """save() 默认审计：多面板无标签的图保存时发出警告。"""
    fig, axes = sp.paper_subplots(1, 2, venue="thesis")
    for ax in axes:
        ax.plot([1, 2, 3])
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        sp.save(fig, tmp_path / "bad", formats=("png",))
    assert any("sciplot 审计" in str(x.message) for x in w)


def test_save_audit_disabled(tmp_path, cleanup_figures):
    """audit=False 关闭保存时审计。"""
    fig, ax = sp.plot_line(np.arange(10), np.random.rand(10))
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        sp.save(fig, tmp_path / "ok", formats=("png",), audit=False)
    assert not any("sciplot 审计" in str(x.message) for x in w)


def test_save_clean_figure_no_audit_warning(tmp_path, cleanup_figures):
    """规范图保存不产生审计警告。"""
    fig, ax = sp.plot_line(np.arange(10), np.random.rand(10),
                           xlabel="X", ylabel="Y")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        sp.save(fig, tmp_path / "clean", formats=("png",))
    assert not any("sciplot 审计" in str(x.message) for x in w)


def test_audit_config_toggle(tmp_path, cleanup_figures):
    """配置项 audit=False 时保存不审计。"""
    sp.set_defaults(audit=False)
    try:
        fig, ax = sp.plot_line(np.arange(10), np.random.rand(10))
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            sp.save(fig, tmp_path / "cfg", formats=("png",))
        assert not any("sciplot 审计" in str(x.message) for x in w)
    finally:
        sp.set_defaults(audit=True)
