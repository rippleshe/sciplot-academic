"""
Hardening tests for hidden edge cases in core modules.
"""

from __future__ import annotations

import pytest

import sciplot as sp


@pytest.fixture(autouse=True)
def reset_config_state():
    """Keep config state isolated across tests."""
    sp.reset_config()
    yield
    sp.reset_config()


class TestConfigHardening:
    """Configuration normalization and validation edge cases."""

    def test_set_defaults_normalizes_formats_list(self):
        sp.set_defaults(formats=["PDF", " png "])
        assert sp.get_config("formats") == ("pdf", "png")

    def test_load_config_normalizes_formats(self, temp_dir):
        config_file = temp_dir / ".sciplot.toml"
        config_file.write_text(
            'venue = "thesis"\nlang = "zh"\ndpi = 600\nformats = ["PNG"]\n',
            encoding="utf-8",
        )

        loaded = sp.load_config(config_file)
        assert loaded is True
        assert sp.get_config("venue") == "thesis"
        assert sp.get_config("formats") == ("png",)

    def test_load_config_rejects_all_invalid_entries(self, temp_dir):
        config_file = temp_dir / ".sciplot.toml"
        config_file.write_text(
            'venue = "not-a-real-venue"\nformats = []\ndpi = 0\nlang = "xx"\n',
            encoding="utf-8",
        )

        loaded = sp.load_config(config_file)
        assert loaded is False
        assert sp.get_config("venue") == "nature"
        assert sp.get_config("formats") == ("pdf", "png")


class TestSaveHardening:
    """Save-path and format normalization edge cases."""

    def test_save_accepts_single_string_format(self, temp_dir, cleanup_figures):
        fig, ax = sp.plot([1, 2], [1, 2])
        paths = sp.save(fig, temp_dir / "single_format", formats="png")

        assert len(paths) == 1
        assert paths[0].suffix == ".png"
        assert paths[0].exists()

    def test_save_blocks_parent_escape_when_dir_set(self, temp_dir, cleanup_figures):
        fig, ax = sp.plot([1, 2], [1, 2])
        safe_dir = temp_dir / "safe"
        safe_dir.mkdir()

        with pytest.raises(ValueError):
            sp.save(fig, "../escape", formats="png", dir=safe_dir)

    def test_save_blocks_absolute_name_when_dir_set(self, temp_dir, cleanup_figures):
        fig, ax = sp.plot([1, 2], [1, 2])
        safe_dir = temp_dir / "safe"
        safe_dir.mkdir()

        with pytest.raises(ValueError):
            sp.save(fig, str(temp_dir / "escape"), formats="png", dir=safe_dir)


class TestPaletteDefensiveCopies:
    """Global palette state should not be mutable via returned lists."""

    def test_builtin_palette_get_returns_copy(self):
        palette = sp.get_palette("pastel")
        palette[0] = "#000000"

        fresh = sp.get_palette("pastel")
        assert fresh[0] != "#000000"

    def test_custom_palette_get_returns_copy(self):
        sp.set_custom_palette(["#111111", "#222222"], name="copy_test_palette")
        palette = sp.get_palette("copy_test_palette")
        palette.append("#333333")

        fresh = sp.get_palette("copy_test_palette")
        assert fresh == ["#111111", "#222222"]
