"""
Round-8 hardening tests for high-priority API cleanup and VENUES structure migration.
"""

from __future__ import annotations

import pytest

import sciplot as sp
import sciplot._core as core
from sciplot._core.style import VENUES


class TestHighPriorityHardeningRound8:
    def test_validate_params_not_exposed_in_public_api(self):
        assert "validate_params" not in sp.__all__
        assert not hasattr(sp, "validate_params")

    def test_registry_dead_api_not_exposed_from_core_namespace(self):
        dead_api = {
            "PlotterMetadata",
            "PLOTTER_REGISTRY",
            "register_plotter",
            "get_plotter",
            "list_plotters",
        }
        assert dead_api.isdisjoint(set(getattr(core, "__all__", [])))
        for name in dead_api:
            assert not hasattr(core, name)

    def test_venues_use_named_fields_with_tuple_compatibility(self):
        nature = VENUES["nature"]

        assert hasattr(nature, "styles")
        assert hasattr(nature, "figsize")
        assert hasattr(nature, "fontsize")

        assert nature.styles[0] == "science"
        assert nature.figsize == (7.0, 5.0)
        assert nature.fontsize == 8

        # 向后兼容：仍可按元组下标访问
        assert nature[0] == nature.styles
        assert nature[1] == nature.figsize
        assert nature[2] == nature.fontsize

    def test_venue_consumers_work_after_named_config_migration(self, cleanup_figures):
        fig, _ = sp.new_figure("ieee")
        info = sp.get_venue_info("ieee")

        width, height = fig.get_size_inches()
        exp_w, exp_h = info["figsize"]

        assert width == pytest.approx(exp_w, abs=0.1)
        assert height == pytest.approx(exp_h, abs=0.1)
