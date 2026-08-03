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
    axes[0].plot([1, 2, 3]); axes[0].set_xlabel("x"); axes[0].set_ylabel("y")
    axes[1].plot([1, 2, 3]); axes[1].set_xlabel("x"); axes[1].set_ylabel("y")
    report = sp.audit_figure(fig, verbose=False)
    assert any("面板标签" in i for i in report["issues"])


def test_audit_panel_labels_present(cleanup_figures):
    """figure_panels 生成的面板标签可通过审计。"""
    fig, axes = sp.figure_panels(1, 2)
    axes[0].plot([1, 2, 3]); axes[0].set_xlabel("x"); axes[0].set_ylabel("y")
    axes[1].plot([1, 2, 3]); axes[1].set_xlabel("x"); axes[1].set_ylabel("y")
    report = sp.audit_figure(fig, verbose=False)
    assert not any("面板标签" in i for i in report["issues"])


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
