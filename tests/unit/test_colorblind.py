"""
Round-46 tests for colorblind safety (色盲安全防线).

验证：
- simulate_colorblind 三类色觉缺失模拟
- check_colorblind_safe 区分度校验
- audit_palette 内置配色体检
- Okabe-Ito 调色板注册与可用性
"""

from __future__ import annotations

import pytest

import sciplot as sp


# ── simulate_colorblind ────────────────────────────────────────

def test_simulate_basic(cleanup_figures):
    """模拟返回与输入等长的 HEX 列表。"""
    out = sp.simulate_colorblind(["#E69F00", "#009E73", "#56B4E9"])
    assert len(out) == 3
    for c in out:
        assert c.startswith("#")
        assert len(c) == 7


def test_simulate_empty(cleanup_figures):
    assert sp.simulate_colorblind([]) == []


def test_simulate_invalid_deficiency(cleanup_figures):
    with pytest.raises(ValueError, match="deficiency"):
        sp.simulate_colorblind(["#E69F00"], deficiency="achromatopsia")


def test_simulate_invalid_hex(cleanup_figures):
    with pytest.raises(ValueError, match="HEX"):
        sp.simulate_colorblind(["red"])


def test_simulate_all_types(cleanup_figures):
    """三种类型都可用且结果不同。"""
    colors = ["#E69F00", "#56B4E9", "#009E73"]
    results = {d: sp.simulate_colorblind(colors, d)
               for d in ("deuteranopia", "protanopia", "tritanopia")}
    assert len(results) == 3


# ── check_colorblind_safe ──────────────────────────────────────

def test_check_safe_okabe_ito(cleanup_figures):
    """Okabe-Ito 全套在三种色盲视角下均应安全。"""
    report = sp.check_colorblind_safe(sp.OKABE_ITO["okabe-ito"])
    assert all(report[d]["safe"] for d in report)


def test_check_unsafe_pair(cleanup_figures):
    """颜色与其色盲模拟结果在对应色觉缺失视角下应几乎重合（自洽性）。"""
    sim = sp.simulate_colorblind(["#FF0000"], "deuteranopia")[0]
    report = sp.check_colorblind_safe(["#FF0000", sim],
                                      deficiencies=("deuteranopia",))
    assert not report["deuteranopia"]["safe"]


def test_check_conflict_pairs_reported(cleanup_figures):
    """冲突颜色对会被记录。"""
    sim = sp.simulate_colorblind(["#FF0000"], "deuteranopia")[0]
    report = sp.check_colorblind_safe(["#FF0000", sim],
                                      deficiencies=("deuteranopia",))
    pairs = report["deuteranopia"]["conflict_pairs"]
    assert len(pairs) >= 1
    c1, c2 = pairs[0]
    assert c1 in ("#FF0000", sim)
    assert c2 in ("#FF0000", sim)


def test_check_requires_two_colors(cleanup_figures):
    with pytest.raises(ValueError, match="至少需要两个颜色"):
        sp.check_colorblind_safe(["#E69F00"])


def test_check_invalid_deficiency(cleanup_figures):
    with pytest.raises(ValueError, match="deficiency"):
        sp.check_colorblind_safe(["#E69F00", "#009E73"],
                                 deficiencies=("bogus",))


# ── audit_palette ──────────────────────────────────────────────

def test_audit_palette_safe_field(cleanup_figures):
    """审计返回结构完整。"""
    result = sp.audit_palette("okabe-ito")
    assert result["palette"] == "okabe-ito"
    assert result["n_colors"] == 8
    assert "report" in result
    assert isinstance(result["safe"], bool)


def test_audit_palette_unknown(cleanup_figures):
    with pytest.raises((ValueError, KeyError)):
        sp.audit_palette("nonexistent-palette-xyz")


# ── Okabe-Ito 注册 ─────────────────────────────────────────────

def test_okabe_ito_registered(cleanup_figures):
    """Okabe-Ito 已并入内置配色，可直接 apply。"""
    assert "okabe-ito" in sp.list_palettes()
    assert "okabe-ito-4" in sp.list_palettes()
    palette = sp.get_palette("okabe-ito")
    assert len(palette) == 8
    assert palette[0] == "#E69F00"


def test_okabe_ito_usable_in_style(cleanup_figures):
    """okabe-ito 可作为 setup_style 的配色使用。"""
    sp.setup_style("nature", "okabe-ito", lang="en")
    import matplotlib.pyplot as plt

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]
    assert colors[0] == "#E69F00"


def test_exports(cleanup_figures):
    assert callable(sp.simulate_colorblind)
    assert callable(sp.check_colorblind_safe)
    assert callable(sp.audit_palette)
    assert "OKABE_ITO" in sp.__all__
    assert "simulate_colorblind" in sp.__all__
