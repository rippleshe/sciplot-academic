"""
Round-22 tests for plot_network upgrades: top-N labels, seed, ranges, legend, colorbar.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import pytest

import sciplot as sp


def _node_coll(result):
    """节点 PathCollection（边 LineCollection 在前）。"""
    from matplotlib.collections import PathCollection

    for coll in result.ax.collections:
        if isinstance(coll, PathCollection):
            return coll
    raise AssertionError("未找到节点集合")


def _node_offsets(result):
    return np.asarray(_node_coll(result).get_offsets())


@pytest.fixture()
def karate():
    return nx.karate_club_graph()


def test_network_top_n_labels(karate, cleanup_figures):
    """labels=整数 时只标注度最大的前 N 个节点。"""
    result = sp.plot_network(karate, labels=5)
    # 5 个 label text（draw_networkx_labels 产生 text 对象）
    n_texts = len([t for t in result.ax.texts if t.get_text()])
    assert n_texts == 5


def test_network_no_labels(karate, cleanup_figures):
    result = sp.plot_network(karate, labels=False)
    assert len(result.ax.texts) == 0


def test_network_labels_all(karate, cleanup_figures):
    result = sp.plot_network(karate, labels=True)
    assert len(result.ax.texts) == karate.number_of_nodes()


def test_network_seed_reproducible(karate, cleanup_figures):
    """相同 seed 必须产生相同布局。"""
    r1 = sp.plot_network(karate, layout="spring", seed=42)
    pos1 = _node_offsets(r1)
    r2 = sp.plot_network(karate, layout="spring", seed=42)
    pos2 = _node_offsets(r2)
    assert np.allclose(pos1, pos2)


def test_network_different_seed_different_layout(karate, cleanup_figures):
    r1 = sp.plot_network(karate, layout="spring", seed=1)
    pos1 = _node_offsets(r1)
    r2 = sp.plot_network(karate, layout="spring", seed=999)
    pos2 = _node_offsets(r2)
    assert not np.allclose(pos1, pos2)


def test_network_node_size_range(karate, cleanup_figures):
    """node_size_range 控制属性→尺寸映射的上下界。"""
    nx.set_node_attributes(karate, {n: float(n) for n in karate.nodes()}, "val")
    result = sp.plot_network(
        karate, node_size_by="val", node_size_range=(50, 500)
    )
    sizes = np.asarray(_node_coll(result).get_sizes())
    assert sizes.min() == pytest.approx(50, rel=0.05)
    assert sizes.max() == pytest.approx(500, rel=0.05)


def test_network_edge_width_range(karate, cleanup_figures):
    """edge_width_range 控制权重→边宽映射的上下界。"""
    nx.set_edge_attributes(karate, {e: 1.0 for e in karate.edges()}, "w")
    # 给边赋不同权重
    for i, e in enumerate(karate.edges()):
        karate[e[0]][e[1]]["w"] = i + 1
    result = sp.plot_network(
        karate, edge_weight_by="w", edge_width_range=(0.2, 5.0)
    )
    widths = np.asarray(result.ax.collections[0].get_linewidths())
    assert widths.min() == pytest.approx(0.2, rel=0.05)
    assert widths.max() == pytest.approx(5.0, rel=0.05)


def test_network_categorical_legend(karate, cleanup_figures):
    """分类着色应生成图例。"""
    nx.set_node_attributes(
        karate, {n: ("club1" if karate.nodes[n]["club"] == "Mr. Hi" else "club2")
                 for n in karate.nodes()}, "grp"
    )
    result = sp.plot_network(karate, node_color_by="grp")
    legend = result.ax.get_legend()
    assert legend is not None
    texts = [t.get_text() for t in legend.get_texts()]
    assert texts == ["club1", "club2"]


def test_network_categorical_no_legend_when_disabled(karate, cleanup_figures):
    nx.set_node_attributes(karate, {n: "x" for n in karate.nodes()}, "grp")
    result = sp.plot_network(karate, node_color_by="grp", show_legend=False)
    assert result.ax.get_legend() is None


def test_network_colorbar(karate, cleanup_figures):
    """连续着色 + show_colorbar 应产生颜色条。"""
    nx.set_node_attributes(karate, {n: float(n) * 1.5 for n in karate.nodes()}, "val")
    result = sp.plot_network(karate, node_color_by="val", show_colorbar=True)
    assert len(result.fig.axes) == 2


def test_network_colorbar_disabled_by_default(karate, cleanup_figures):
    nx.set_node_attributes(karate, {n: float(n) for n in karate.nodes()}, "val")
    result = sp.plot_network(karate, node_color_by="val")
    assert len(result.fig.axes) == 1


def test_network_layout_kwargs(karate, cleanup_figures):
    """layout_kwargs 透传（iterations 影响布局结果）。"""
    r1 = sp.plot_network(karate, layout="spring", seed=42, layout_kwargs={"iterations": 1})
    pos1 = _node_offsets(r1)
    r2 = sp.plot_network(karate, layout="spring", seed=42, layout_kwargs={"iterations": 200})
    pos2 = _node_offsets(r2)
    assert not np.allclose(pos1, pos2)


def test_network_categorical_color_stable_across_calls(karate, cleanup_figures):
    """分类配色跨调用稳定（sorted 迭代而非 set 迭代）。"""
    nx.set_node_attributes(
        karate, {n: f"grp{n % 5}" for n in karate.nodes()}, "grp"
    )
    r1 = sp.plot_network(karate, node_color_by="grp")
    colors1 = np.asarray(r1.ax.collections[0].get_facecolors())
    r2 = sp.plot_network(karate, node_color_by="grp")
    colors2 = np.asarray(r2.ax.collections[0].get_facecolors())
    assert np.array_equal(colors1, colors2)


def test_network_communities_still_works(karate, cleanup_figures):
    """plot_network_communities 不受影响。"""
    from networkx.algorithms.community import greedy_modularity_communities

    communities = list(greedy_modularity_communities(karate))
    result = sp.plot_network_communities(karate, communities)
    assert result.fig is not None


def test_network_from_matrix_kwargs_forward(karate, cleanup_figures):
    """plot_network_from_matrix 透传新参数（seed/node_color_by）。"""
    adj = nx.to_numpy_array(karate)
    result = sp.plot_network_from_matrix(adj, seed=42, node_color_by="degree")
    assert result.fig is not None
    assert len(result.fig.axes) == 1
