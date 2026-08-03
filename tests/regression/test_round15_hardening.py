"""
Round-15 hardening tests for ext-layer validation and API-layer behavior.
"""

from __future__ import annotations

import io
import warnings
from contextlib import redirect_stdout

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pytest

import sciplot as sp


# ═══════════════════════════════════════════════════════════════
# 扩展层校验护栏
# ═══════════════════════════════════════════════════════════════

def test_network_from_matrix_non_square_raises(cleanup_figures):
    with pytest.raises(ValueError, match="方阵"):
        sp.plot_network_from_matrix(np.ones((3, 4)))


def test_network_from_matrix_nan_inf_tolerated(cleanup_figures):
    """含 NaN/Inf 的邻接矩阵不应崩溃（NaN 边被跳过，Inf 边被过滤前由阈值控制）。"""
    adj = np.array([[0.0, np.nan], [np.inf, 0.0]])
    result = sp.plot_network_from_matrix(adj)
    assert result.fig is not None


def test_network_empty_graph_ok(cleanup_figures):
    result = sp.plot_network(nx.Graph())
    assert result.fig is not None


def test_network_zero_matrix_ok(cleanup_figures):
    result = sp.plot_network_from_matrix(np.zeros((4, 4)))
    assert result.fig is not None


def test_dendrogram_bad_orientation_raises(cleanup_figures):
    with pytest.raises(ValueError):
        sp.plot_dendrogram(np.random.randn(10, 5), orientation="sideways")


def test_dendrogram_label_mismatch_raises(cleanup_figures):
    with pytest.raises(ValueError):
        sp.plot_dendrogram(np.random.randn(10, 5), labels=["a", "b"])


def test_venn2_all_zero_no_crash(cleanup_figures):
    """全零集合可绘制（matplotlib-venn 仅警告零面积）。"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = sp.plot_venn2((0, 0, 0))
    assert result.fig is not None


# ═══════════════════════════════════════════════════════════════
# save 校验护栏
# ═══════════════════════════════════════════════════════════════

def test_save_unsupported_format_raises(tmp_path, cleanup_figures):
    fig, ax = plt.subplots()
    with pytest.raises(ValueError, match="不支持的输出格式"):
        sp.save(fig, str(tmp_path / "x"), formats=("gif",))


def test_save_empty_formats_raises(tmp_path, cleanup_figures):
    fig, ax = plt.subplots()
    with pytest.raises(ValueError, match="formats 不能为空"):
        sp.save(fig, str(tmp_path / "x"), formats=())


def test_save_path_escape_blocked(tmp_path, cleanup_figures):
    """name 不能通过 ../ 跳出 dir 指定目录。"""
    fig, ax = plt.subplots()
    with pytest.raises(ValueError, match="回退跳出"):
        sp.save(fig, "../../escape", dir=str(tmp_path), formats=("png",))


def test_save_absolute_name_with_dir_raises(tmp_path, cleanup_figures):
    fig, ax = plt.subplots()
    with pytest.raises(ValueError, match="绝对路径"):
        sp.save(fig, str(tmp_path / "abs"), dir=str(tmp_path), formats=("png",))


def test_save_windows_reserved_name_raises(tmp_path, cleanup_figures):
    """Windows 保留设备名（CON/PRN/NUL/COM1 等）必须被拒绝。"""
    fig, ax = plt.subplots()
    for bad_name in ["CON", "con.png", "PRN", "NUL", "COM1", "LPT3.pdf"]:
        with pytest.raises(ValueError, match="保留设备名"):
            sp.save(fig, str(tmp_path / bad_name), formats=("png",))


# ═══════════════════════════════════════════════════════════════
# 链式调用护栏
# ═══════════════════════════════════════════════════════════════

def test_chain_style_after_plot_raises(cleanup_figures):
    chain = sp.style("ieee")
    chain.plot([1, 2], [1, 2])
    with pytest.raises(RuntimeError, match="style"):
        chain.style("nature")


def test_chain_negative_figsize_raises(cleanup_figures):
    with pytest.raises(ValueError):
        sp.style("ieee").figsize(-5, 4).plot([1, 2], [1, 2])


def test_chain_lang_before_plot(cleanup_figures):
    """lang() 在绘图前设置应生效。"""
    result = sp.style("nature").lang("en").plot([1, 2], [1, 2])
    assert result.fig is not None


# ═══════════════════════════════════════════════════════════════
# 延迟加载与自省
# ═══════════════════════════════════════════════════════════════

def test_lazy_ext_names_in_dir():
    dir_names = dir(sp)
    for name in ["plot_network", "plot_dendrogram", "plot_venn2", "plot_clustermap"]:
        assert name in dir_names


def test_lazy_ext_access_returns_callable():
    for name in ["plot_network", "plot_venn2", "plot_venn3"]:
        assert callable(getattr(sp, name))


def test_lazy_unknown_name_raises():
    with pytest.raises(AttributeError):
        sp.not_a_real_function_xyz  # noqa: B018


def test_inspect_runs_without_error():
    buf = io.StringIO()
    with redirect_stdout(buf):
        sp.inspect()
    assert "SciPlot Academic" in buf.getvalue()


# ═══════════════════════════════════════════════════════════════
# 上下文管理器补充
# ═══════════════════════════════════════════════════════════════

def test_palette_only_context_keeps_venue(cleanup_figures):
    """上下文内仅覆盖 palette 时不得重置 venue。"""
    sp.setup_style("ieee", "ocean", lang="en")
    figsize_before = list(matplotlib.rcParams["figure.figsize"])
    with sp.style_context(palette="sunset"):
        # figsize 与 venue 状态均不应被 palette 覆盖改变
        assert matplotlib.rcParams["figure.figsize"] == figsize_before
        from sciplot._core.style import get_current_venue
        assert get_current_venue() == "ieee"
    assert matplotlib.rcParams["figure.figsize"] == figsize_before


def test_ieee_context_defaults(cleanup_figures):
    from sciplot._core.style import get_current_venue
    venue_before = get_current_venue()
    with sp.ieee_context():
        assert get_current_venue() == "ieee"
    # 退出后恢复到进入前的 venue 状态
    assert get_current_venue() == venue_before


def test_context_with_rc_params(cleanup_figures):
    """自定义 rcParams 上下文在退出后恢复。"""
    sp.setup_style("ieee")
    before = matplotlib.rcParams["lines.linewidth"]
    with sp.style_context(**{"lines.linewidth": 5}):
        assert matplotlib.rcParams["lines.linewidth"] == 5
    assert matplotlib.rcParams["lines.linewidth"] == before
