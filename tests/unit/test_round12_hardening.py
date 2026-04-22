"""
Round-12 hardening tests for critical/major fixes from final audit.
"""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest

import sciplot as sp
from sciplot._core import config as _config
from sciplot._ext.plot3d import _get_3d_figsize
from sciplot._plots.basic import _LINE2D_KWARGS


def test_get_supported_formats_does_not_change_backend(cleanup_figures):
    backend_before = matplotlib.get_backend()

    # Force refresh cache to exercise initialization path.
    _config._SUPPORTED_SAVE_FORMATS = None
    formats = _config._get_supported_formats()

    assert "png" in formats
    assert "pdf" in formats
    assert matplotlib.get_backend() == backend_before


def test_plot3d_figsize_uses_named_venue_fields():
    w, h = _get_3d_figsize("ieee")
    assert w == pytest.approx(3.5 * 1.2)
    assert h == pytest.approx(3.0 * 1.2)


def test_annotate_significance_validates_p_value_and_x(cleanup_figures):
    fig, ax = plt.subplots()

    with pytest.raises(ValueError, match="p_value"):
        sp.annotate_significance(ax, x1=1, x2=2, y=1.0, p_value=-0.1)

    with pytest.raises(ValueError, match="p_value"):
        sp.annotate_significance(ax, x1=1, x2=2, y=1.0, p_value=1.1)

    with pytest.raises(ValueError, match="x1 与 x2"):
        sp.annotate_significance(ax, x1=1, x2=1, y=1.0, p_value=0.05)


def test_plot_violin_list_rejects_nan_inf(cleanup_figures):
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_violin([np.array([1.0, np.nan, 2.0]), np.array([3.0, 4.0])])

    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_violin([np.array([1.0, np.inf, 2.0]), np.array([3.0, 4.0])])


def test_plot_result_ax_allows_single_element_array(cleanup_figures):
    fig, ax = plt.subplots()
    wrapped = np.array([ax], dtype=object)
    result = sp.PlotResult(fig, wrapped)

    assert result.ax is ax


def test_plot_result_save_ignores_tight_layout_value_error(tmp_path, cleanup_figures, monkeypatch):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    result = sp.PlotResult(fig, ax)

    def _raise_value_error(*args, **kwargs):
        raise ValueError("tight layout conflict")

    monkeypatch.setattr(fig, "tight_layout", _raise_value_error)

    output = tmp_path / "tight_layout_value_error_ok"
    paths = result.save(str(output), formats=("png",))
    assert len(paths) == 1
    assert paths[0].exists()


def test_plot_timeseries_warns_on_inf(cleanup_figures):
    t = np.arange(4)
    y = np.array([1.0, np.inf, 3.0, 4.0])

    with pytest.warns(UserWarning, match="Inf"):
        result = sp.plot_timeseries(t, y)

    assert result.fig is not None


def test_line2d_kwargs_uses_public_properties_only():
    assert "color" in _LINE2D_KWARGS
    assert "linewidth" in _LINE2D_KWARGS
    assert "linestyle" in _LINE2D_KWARGS