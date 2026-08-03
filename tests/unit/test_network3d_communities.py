"""
Round-23 tests for plot_network3d and plot_network_communities upgrades.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import pytest

import sciplot as sp


@pytest.fixture()
def karate():
    return nx.karate_club_graph()


# ═══════════════════════════════════════════════════════════════
# plot_network3d
# ═══════════════════════════════════════════════════════════════

def test_network3d_basic(karate, cleanup_figures):
    result = sp.plot_network3d(karate)
    assert result.fig is not None
    # 3D 轴 + 34 个节点 scatter
    assert len(result.ax.collections) == 1
    assert len(result.ax.collections[0].get_offsets()) == 34


def test_network3d_exported():
    assert callable(sp.plot_network3d)
    assert "plot_network3d" in sp.__all__


def test_network3d_z_by_degree(karate, cleanup_figures):
    """z_by='degree' 默认归一化保持单调；normalize_z=False 用原始度值。"""
    result = sp.plot_network3d(karate, z_by="degree")
    zs = np.asarray(result.ax.collections[0]._offsets3d)[2]
    degrees = [d for _, d in karate.degree()]
    assert len(zs) == len(degrees)
    # 归一化后：排序一致、存在深度差异
    assert np.all(np.diff(np.sort(zs)) >= 0)
    assert float(np.max(zs)) > float(np.min(zs))

    # 显式关闭归一化：Z 与原始度一致
    result_raw = sp.plot_network3d(karate, z_by="degree", normalize_z=False)
    zs_raw = np.asarray(result_raw.ax.collections[0]._offsets3d)[2]
    assert np.allclose(np.sort(zs_raw), np.sort(degrees))


def test_network3d_z_by_attr(karate, cleanup_figures):
    """z_by 指向数值属性时归一化保持单调。"""
    nx.set_node_attributes(karate, {n: n * 2.0 for n in karate.nodes()}, "zval")
    result = sp.plot_network3d(karate, z_by="zval")
    zs = np.asarray(result.ax.collections[0]._offsets3d)[2]
    expected = np.sort([n * 2.0 for n in karate.nodes()])
    z_sorted = np.sort(zs)
    assert len(z_sorted) == len(expected)
    assert z_sorted[-1] > z_sorted[0]
    assert np.all(np.diff(z_sorted) >= 0)

    # normalize_z=False 保留原始属性值
    result_raw = sp.plot_network3d(karate, z_by="zval", normalize_z=False)
    zs_raw = np.asarray(result_raw.ax.collections[0]._offsets3d)[2]
    assert np.allclose(np.sort(zs_raw), expected)


def test_network3d_z_by_string_attr_warns(karate, cleanup_figures):
    """z_by 指向字符串属性应警告并回退 0。"""
    nx.set_node_attributes(karate, {n: "x" for n in karate.nodes()}, "zval")
    with pytest.warns(UserWarning, match="Z 坐标"):
        result = sp.plot_network3d(karate, z_by="zval")
    zs = np.asarray(result.ax.collections[0]._offsets3d)[2]
    assert np.all(zs == 0.0)


def test_network3d_top_n_labels(karate, cleanup_figures):
    result = sp.plot_network3d(karate, labels=3)
    texts = [t for t in result.ax.texts if t.get_text()]
    assert len(texts) == 3


def test_network3d_no_labels(karate, cleanup_figures):
    result = sp.plot_network3d(karate, labels=False)
    assert len(result.ax.texts) == 0


def test_network3d_categorical_legend(karate, cleanup_figures):
    nx.set_node_attributes(
        karate, {n: f"g{n % 3}" for n in karate.nodes()}, "grp"
    )
    result = sp.plot_network3d(karate, node_color_by="grp")
    legend = result.ax.get_legend()
    assert legend is not None
    assert [t.get_text() for t in legend.get_texts()] == ["g0", "g1", "g2"]


def test_network3d_colorbar(karate, cleanup_figures):
    nx.set_node_attributes(karate, {n: float(n) for n in karate.nodes()}, "val")
    result = sp.plot_network3d(karate, node_color_by="val", show_colorbar=True)
    assert len(result.fig.axes) >= 2


def test_network3d_save_png(tmp_path, karate, cleanup_figures):
    result = sp.plot_network3d(karate, labels=10)
    paths = result.save(str(tmp_path / "net3d"), formats=("png",), dpi=100)
    assert paths[0].exists() and paths[0].stat().st_size > 0


# ═══════════════════════════════════════════════════════════════
# plot_network_communities 升级
# ═══════════════════════════════════════════════════════════════

def test_communities_auto_detect(karate, cleanup_figures):
    """communities=None 时自动检测。"""
    result = sp.plot_network_communities(karate)
    assert result.fig is not None
    legend = result.ax.get_legend()
    assert legend is not None
    # 空手道俱乐部通常检测出 2-4 个社区
    n_communities = len(legend.get_texts())
    assert 2 <= n_communities <= 4


def test_communities_manual(karate, cleanup_figures):
    communities = [[0, 1, 2], [3, 4, 5]]
    result = sp.plot_network_communities(karate, communities)
    legend = result.ax.get_legend()
    assert legend is not None
    assert len(legend.get_texts()) == 2


def test_communities_labels_top_n(karate, cleanup_figures):
    result = sp.plot_network_communities(karate, labels=4)
    texts = [t for t in result.ax.texts if t.get_text()]
    assert len(texts) == 4


def test_communities_labels_none(karate, cleanup_figures):
    result = sp.plot_network_communities(karate, labels=False)
    assert len(result.ax.texts) == 0


def test_communities_seed_reproducible(karate, cleanup_figures):
    r1 = sp.plot_network_communities(karate, seed=42)
    off1 = np.asarray(r1.ax.collections[1].get_offsets())
    r2 = sp.plot_network_communities(karate, seed=42)
    off2 = np.asarray(r2.ax.collections[1].get_offsets())
    assert np.allclose(off1, off2)


def test_communities_node_size(karate, cleanup_figures):
    result = sp.plot_network_communities(karate, node_size=500)
    sizes = np.asarray(result.ax.collections[1].get_sizes())
    assert np.all(sizes == 500)
