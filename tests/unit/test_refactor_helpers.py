"""
第4轮迭代重构产出的公共 helper 单测：
new_styled_figure / _is_constant / _try_import_optional / _require_optional
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp
from sciplot._core.utils import (
    _require_optional,
    _try_import_optional,
    new_styled_figure,
)
from sciplot._plots.statistical import _is_constant


# ── new_styled_figure ────────────────────────────────────────────────────────


def test_new_styled_figure_returns_fig_ax(cleanup_figures):
    fig, ax = new_styled_figure()
    assert fig is not None
    assert ax is not None


def test_new_styled_figure_venue_size(cleanup_figures):
    fig, ax = new_styled_figure("ieee")
    assert fig is not None


def test_new_styled_figure_equivalent_to_manual_pair(cleanup_figures):
    """new_styled_figure 与手写 apply_resolved_style + new_figure 行为等价。"""
    from sciplot._core.layout import new_figure
    from sciplot._core.utils import apply_resolved_style

    fig1, ax1 = new_styled_figure("nature", "pastel")
    eff = apply_resolved_style("nature", "pastel", None)
    fig2, ax2 = new_figure(eff)
    assert fig1.get_size_inches().tolist() == fig2.get_size_inches().tolist()
    assert isinstance(ax1, type(ax2))


# ── _is_constant ─────────────────────────────────────────────────────────────


def test_is_constant_true():
    assert _is_constant(np.array([5.0, 5.0, 5.0]))
    assert _is_constant(np.array([1, 1]))


def test_is_constant_false():
    assert not _is_constant(np.array([1.0, 2.0]))
    assert not _is_constant(np.array([0.1, 0.2, 0.15]))


def test_is_constant_single_value():
    assert _is_constant(np.array([7.0]))


# ── _try_import_optional / _require_optional ─────────────────────────────────


def test_try_import_optional_present():
    mod = _try_import_optional("numpy")
    assert mod is not None
    assert mod.__name__ == "numpy"


def test_try_import_optional_missing_returns_none():
    assert _try_import_optional("no_such_module_sciplot_xyz") is None


def test_require_optional_present():
    mod = _require_optional("numpy", "测试功能")
    assert mod.__name__ == "numpy"


def test_require_optional_missing_raises_with_hint():
    with pytest.raises(ImportError, match="测试功能需要安装"):
        _require_optional("no_such_module_sciplot_xyz", "测试功能")


# ── 端到端：重构后公共入口仍可用 ─────────────────────────────────────────────


def test_plot_line_still_works_after_refactor(cleanup_figures):
    result = sp.plot([1, 2, 3], [1, 4, 9])
    assert result.fig is not None
