"""
Round-7 hardening tests for high-priority consistency fixes.
"""

from __future__ import annotations

import threading

import matplotlib.pyplot as plt
import pytest

import sciplot as sp
from sciplot._core.style import get_current_lang, set_current_lang


class TestHighPriorityHardeningRound7:
    def test_create_subplots_respects_config_default_palette(self, cleanup_figures):
        try:
            sp.reset_config()
            sp.set_defaults(palette="earth")

            sp.create_subplots(1, 1, venue="nature")
            colors = [item["color"] for item in plt.rcParams["axes.prop_cycle"]]
            assert colors[:5] == sp.get_palette("earth")[:5]
        finally:
            sp.reset_config()

    def test_paper_subplots_respects_config_default_palette(self, cleanup_figures):
        try:
            sp.reset_config()
            sp.set_defaults(palette="ocean")

            sp.paper_subplots(1, 1, venue="nature")
            colors = [item["color"] for item in plt.rcParams["axes.prop_cycle"]]
            assert colors[:6] == sp.get_palette("ocean")[:6]
        finally:
            sp.reset_config()

    def test_chain_without_lang_preserves_current_global_lang(self, cleanup_figures):
        try:
            sp.setup_style(lang="en")
            assert get_current_lang() == "en"

            sp.chain(venue="nature", palette="pastel").plot([1, 2, 3], [1, 3, 2])
            assert get_current_lang() == "en"
        finally:
            sp.setup_style(lang="zh")

    def test_chain_without_lang_falls_back_to_zh_when_global_invalid(
        self, cleanup_figures
    ):
        try:
            set_current_lang(None)
            sp.chain(venue="nature", palette="pastel").plot([1, 2], [2, 1])
            assert get_current_lang() == "zh"
        finally:
            sp.setup_style(lang="zh")

    def test_lang_state_is_thread_isolated(self):
        set_current_lang("en")
        assert get_current_lang() == "en"

        observed = {}

        def worker() -> None:
            observed["before"] = get_current_lang()
            set_current_lang("zh")
            observed["after"] = get_current_lang()

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()

        assert observed["before"] is None
        assert observed["after"] == "zh"
        assert get_current_lang() == "en"
