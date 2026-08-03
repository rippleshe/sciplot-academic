"""
Round-21 hardening tests: 无标题默认、3D 面板标签、StyleContext 深拷贝隔离、网络图属性鲁棒性。
"""

from __future__ import annotations

import warnings

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pytest

import sciplot as sp


# ═══════════════════════════════════════════════════════════════
# 无标题默认（论文图惯例）
# ═══════════════════════════════════════════════════════════════

@pytest.mark.parametrize("plot_fn,args", [
    (sp.plot_feature_importance, (["a", "b"], [0.6, 0.4])),
    (sp.plot_residuals, (np.array([1.0, 2.0]), np.array([1.1, 1.9]))),
    (sp.plot_qq, (np.random.default_rng(0).normal(0, 1, 50),)),
    (sp.plot_bland_altman, (np.array([1.0, 2.0, 3.0]), np.array([1.1, 2.2, 2.9]))),
])
def test_default_title_empty(cleanup_figures, plot_fn, args):
    """默认 title 必须为空字符串（图默认无标题）。"""
    result = plot_fn(*args)
    assert result.ax.get_title() == ""


def test_radar_show_labels_single_group_only(cleanup_figures):
    """多组时 show_labels 不产生标注（单组时产生）。"""
    r_multi = sp.plot_radar(["a", "b"], [[1, 2], [3, 4]], show_labels=True)
    assert len(r_multi.ax.texts) == 0
    r_single = sp.plot_radar(["a", "b"], [[1, 2]], show_labels=True)
    assert len(r_single.ax.texts) == 2


# ═══════════════════════════════════════════════════════════════
# 3D 子图面板标签
# ═══════════════════════════════════════════════════════════════

def test_add_panel_labels_on_3d_axes(cleanup_figures):
    """add_panel_labels 对 3D 子图不得崩溃，且产生面板标签文本。"""
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    fig = plt.figure()
    ax3d = fig.add_subplot(111, projection="3d")
    sp.add_panel_labels([ax3d])
    assert len(ax3d.texts) == 1
    assert ax3d.texts[0].get_text() == "(a)"


def test_add_panel_labels_mixed_2d_3d(cleanup_figures):
    """2D 与 3D 子图混合时全部正常标注。"""
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    fig = plt.figure(figsize=(8, 4))
    ax2d = fig.add_subplot(1, 2, 1)
    ax3d = fig.add_subplot(1, 2, 2, projection="3d")
    sp.add_panel_labels([ax2d, ax3d])
    assert ax2d.texts[0].get_text() == "(a)"
    assert ax3d.texts[0].get_text() == "(b)"


# ═══════════════════════════════════════════════════════════════
# StyleContext 深拷贝隔离
# ═══════════════════════════════════════════════════════════════

def test_style_context_nested_list_pollution_fixed(cleanup_figures):
    """上下文内修改 rcParams 列表不得污染退出后的状态。"""
    sp.setup_style("ieee")
    before = list(matplotlib.rcParams["font.serif"])
    with sp.style_context():
        matplotlib.rcParams["font.serif"].append("FAKE FONT")
    assert matplotlib.rcParams["font.serif"] == before
    assert "FAKE FONT" not in matplotlib.rcParams["font.serif"]


def test_style_context_removed_key_restored_on_exit(cleanup_figures):
    """上下文内删除的 rcParams 键在退出时必须被恢复。"""
    sp.setup_style("ieee")
    key = "font.serif"
    assert key in matplotlib.rcParams
def test_style_context_dict_value_isolated(cleanup_figures):
    """上下文内修改 dict 型 rcParams 不污染外部。"""
    sp.setup_style("ieee")
    with sp.style_context():
        matplotlib.rcParams["font.serif"] = ["ONLY FAKE"]
    assert "ONLY FAKE" not in matplotlib.rcParams["font.serif"]


# ═══════════════════════════════════════════════════════════════
# 网络图属性鲁棒性
# ═══════════════════════════════════════════════════════════════

def test_network_size_by_string_attr_warns_and_falls_back(cleanup_figures):
    """node_size_by 指向字符串属性应警告并回退默认大小，不得崩溃。"""
    G = nx.karate_club_graph()
    nx.set_node_attributes(G, {n: f"cat{n % 3}" for n in G.nodes}, "cat")
    with pytest.warns(UserWarning, match="非数值"):
        result = sp.plot_network(G, node_size_by="cat")
    assert result.fig is not None


def test_network_color_by_string_attr_many_categories(cleanup_figures):
    """node_color_by 字符串属性且类别 >10 时按分类着色，不得崩溃。"""
    G = nx.complete_graph(12)
    nx.set_node_attributes(G, {n: f"cat{n}" for n in G.nodes}, "cat")
    result = sp.plot_network(G, node_color_by="cat")
    assert result.fig is not None


def test_network_edge_weight_by_string_attr_warns(cleanup_figures):
    """edge_weight_by 指向字符串属性应警告并回退默认边宽。"""
    G = nx.complete_graph(5)
    nx.set_edge_attributes(G, {e: "heavy" for e in G.edges}, "w")
    with pytest.warns(UserWarning, match="非数值"):
        result = sp.plot_network(G, edge_weight_by="w")
    assert result.fig is not None


def test_network_numeric_attrs_still_work(cleanup_figures):
    """数值属性映射功能不回归。"""
    G = nx.karate_club_graph()
    nx.set_node_attributes(G, {n: n * 1.0 for n in G.nodes}, "val")
    nx.set_edge_attributes(G, {e: 1.0 for e in G.edges}, "w")
    result = sp.plot_network(
        G, node_color_by="val", node_size_by="val", edge_weight_by="w"
    )
    assert result.fig is not None


# ═══════════════════════════════════════════════════════════════
# LaTeX 默认关闭（混排中文安全）
# ═══════════════════════════════════════════════════════════════

def test_usetex_disabled_by_default_in_en_mode(cleanup_figures):
    """干净状态下 lang='en' 的 usetex 必须为 False（避免中文标签触发 latex 崩溃）。"""
    sp.reset_style()
    sp.setup_style("ieee", lang="en")
    assert matplotlib.rcParams["text.usetex"] is False


def test_usetex_persists_after_later_setup(cleanup_figures):
    """显式开启 usetex 后，后续 setup_style 不得悄悄关闭它。"""
    import shutil

    if not (shutil.which("latex") or shutil.which("pdflatex")):
        pytest.skip("系统未安装 LaTeX")
    sp.reset_style()
    sp.setup_style("ieee", lang="en", usetex=True)
    assert matplotlib.rcParams["text.usetex"] is True
    sp.setup_style("nature", lang="en")
    assert matplotlib.rcParams["text.usetex"] is True  # 不被默认调用覆盖
    sp.setup_style("ieee", lang="en", usetex=False)
    assert matplotlib.rcParams["text.usetex"] is False  # 显式关闭生效


def test_usetex_forced_off_in_zh_mode(cleanup_figures):
    """中文模式下显式 usetex=True 必须警告并强制关闭。"""
    sp.reset_style()
    with pytest.warns(UserWarning, match="中文模式"):
        sp.setup_style("thesis", lang="zh", usetex=True)
    assert matplotlib.rcParams["text.usetex"] is False


def test_en_mode_chinese_label_save_no_crash(tmp_path, cleanup_figures):
    """lang='en' 后混排中文标签保存不得触发 latex 崩溃。"""
    sp.setup_style("ieee", lang="en")
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    ax.set_xlabel("响应值")
    ax.set_ylabel("强度")
    paths = sp.save(fig, str(tmp_path / "en_zh_mix"), formats=("png",), dpi=100)
    assert paths[0].exists()


def test_usetex_explicit_true_works(cleanup_figures):
    """显式 usetex=True 时启用 LaTeX（无 LaTeX 环境则警告回退）。"""
    import shutil

    has_latex = bool(shutil.which("latex") or shutil.which("pdflatex"))
    try:
        if has_latex:
            sp.setup_style("ieee", lang="en", usetex=True)
            assert matplotlib.rcParams["text.usetex"] is True
        else:
            with pytest.warns(UserWarning, match="LaTeX"):
                sp.setup_style("ieee", lang="en", usetex=True)
            assert matplotlib.rcParams["text.usetex"] is False
    finally:
        sp.reset_style()
