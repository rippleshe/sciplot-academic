"""配置系统测试 — SciPlotConfig, set_defaults, get_config, load_config, reset_config"""
import pytest
import tempfile
import os
from pathlib import Path
import sciplot as sp
from sciplot._core.config import SciPlotConfig, _normalize_formats, _normalize_config_value


@pytest.fixture(autouse=True)
def reset():
    yield
    sp.reset_config()
    sp.reset_style()


class TestSetDefaults:
    def test_set_venue(self):
        sp.set_defaults(venue="ieee")
        assert sp.get_config("venue") == "ieee"

    def test_set_palette(self):
        sp.set_defaults(palette="earth")
        assert sp.get_config("palette") == "earth"

    def test_set_lang(self):
        sp.set_defaults(lang="en")
        assert sp.get_config("lang") == "en"

    def test_set_dpi(self):
        sp.set_defaults(dpi=600)
        assert sp.get_config("dpi") == 600

    def test_set_formats(self):
        sp.set_defaults(formats=("png",))
        assert sp.get_config("formats") == ("png",)

    def test_set_multiple(self):
        sp.set_defaults(venue="ieee", palette="earth", dpi=600)
        assert sp.get_config("venue") == "ieee"
        assert sp.get_config("palette") == "earth"
        assert sp.get_config("dpi") == 600

    def test_invalid_venue(self):
        with pytest.raises(ValueError):
            sp.set_defaults(venue="invalid_venue")

    def test_invalid_palette(self):
        with pytest.raises(ValueError):
            sp.set_defaults(palette="invalid_palette")

    def test_invalid_lang(self):
        with pytest.raises(ValueError):
            sp.set_defaults(lang="invalid_lang")

    def test_invalid_key(self):
        with pytest.raises(ValueError):
            sp.set_defaults(invalid_key="value")

    def test_invalid_dpi_type(self):
        with pytest.raises(ValueError):
            sp.set_defaults(dpi="not_a_number")

    def test_invalid_dpi_zero(self):
        with pytest.raises(ValueError):
            sp.set_defaults(dpi=0)

    def test_invalid_dpi_negative(self):
        with pytest.raises(ValueError):
            sp.set_defaults(dpi=-100)

    def test_set_formats_with_dot_prefix(self):
        sp.set_defaults(formats=(".png",))
        assert sp.get_config("formats") == ("png",)


class TestGetConfig:
    def test_get_venue_default(self):
        assert sp.get_config("venue") == "nature"

    def test_get_palette_default(self):
        assert sp.get_config("palette") == "pastel"

    def test_get_lang_default(self):
        assert sp.get_config("lang") == "zh"

    def test_get_dpi_default(self):
        assert sp.get_config("dpi") == 1200

    def test_get_formats_default(self):
        assert sp.get_config("formats") == ("pdf", "png")

    def test_get_none_returns_all(self):
        config = sp.get_config()
        assert isinstance(config, dict)
        assert "venue" in config
        assert "palette" in config
        assert "lang" in config

    def test_get_unknown_key(self):
        assert sp.get_config("nonexistent") is None

    def test_get_unknown_key_with_default(self):
        assert sp.get_config("nonexistent") is None


class TestResetConfig:
    def test_reset_clears_user_settings(self):
        sp.set_defaults(venue="ieee")
        sp.reset_config()
        assert sp.get_config("venue") == "nature"

    def test_reset_clears_file_settings(self):
        SciPlotConfig._file_settings["venue"] = "ieee"
        sp.reset_config()
        assert sp.get_config("venue") == "nature"


class TestNormalizeFormats:
    def test_basic(self):
        result = _normalize_formats(("png",))
        assert result == ("png",)

    def test_multiple(self):
        result = _normalize_formats(("png", "pdf"))
        assert result == ("png", "pdf")

    def test_with_dot(self):
        result = _normalize_formats((".png",))
        assert result == ("png",)

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            _normalize_formats(())

    def test_non_string_raises(self):
        with pytest.raises(ValueError):
            _normalize_formats((123,))


class TestNormalizeConfigValue:
    def test_dpi_from_float(self):
        result = _normalize_config_value("dpi", 300.0)
        assert result == 300
        assert isinstance(result, int)

    def test_dpi_from_string(self):
        result = _normalize_config_value("dpi", "600")
        assert result == 600

    def test_dpi_invalid_string(self):
        with pytest.raises(ValueError):
            _normalize_config_value("dpi", "abc")

    def test_dpi_zero(self):
        with pytest.raises(ValueError):
            _normalize_config_value("dpi", 0)


class TestLoadConfig:
    def test_load_from_file(self, tmp_path):
        config_file = tmp_path / ".sciplot.toml"
        config_file.write_text('venue = "ieee"\npalette = "earth"\n')
        result = sp.load_config(str(config_file))
        assert result is True
        assert sp.get_config("venue") == "ieee"
        assert sp.get_config("palette") == "earth"

    def test_load_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            sp.load_config("/nonexistent/path/config.toml")

    def test_load_auto_find_no_config(self):
        result = sp.load_config()
        # No config file in current dir hierarchy
        assert result is False

    def test_is_loaded(self):
        assert SciPlotConfig.is_loaded() is False


class TestSciPlotConfigGetAll:
    def test_get_all_returns_dict(self):
        result = SciPlotConfig.get_all()
        assert isinstance(result, dict)
        assert "venue" in result
        assert "palette" in result

    def test_user_settings_override_defaults(self):
        sp.set_defaults(venue="ieee")
        result = SciPlotConfig.get_all()
        assert result["venue"] == "ieee"

    def test_nested_key(self):
        SciPlotConfig._file_settings["section"] = {"key": "value"}
        result = SciPlotConfig.get("section.key")
        assert result == "value"

    def test_nested_key_missing(self):
        result = SciPlotConfig.get("section.key", default="fallback")
        assert result == "fallback"
