"""颜色工具函数测试 — hex_to_rgb, rgb_to_hex, lighten/darken_color, generate_gradient"""
import pytest
import math
import sciplot as sp


class TestHexToRgb:
    def test_basic_hex6(self):
        assert sp.hex_to_rgb("#FF0000") == (1.0, 0.0, 0.0)
        assert sp.hex_to_rgb("#00FF00") == (0.0, 1.0, 0.0)
        assert sp.hex_to_rgb("#0000FF") == (0.0, 0.0, 1.0)

    def test_hex3_shorthand(self):
        r, g, b = sp.hex_to_rgb("#F00")
        assert abs(r - 1.0) < 1e-9
        assert abs(g - 0.0) < 1e-9
        assert abs(b - 0.0) < 1e-9

    def test_hex_without_hash(self):
        r, g, b = sp.hex_to_rgb("FF8800")
        assert abs(r - 1.0) < 1e-9
        assert abs(g - 0.533) < 0.001
        assert abs(b - 0.0) < 1e-9

    def test_lowercase(self):
        assert sp.hex_to_rgb("#ff0000") == (1.0, 0.0, 0.0)
        assert sp.hex_to_rgb("abc") == (sp.hex_to_rgb("AABBCC")[0], sp.hex_to_rgb("AABBCC")[1], sp.hex_to_rgb("AABBCC")[2])

    def test_mixed_case(self):
        r, g, b = sp.hex_to_rgb("#aAbBcC")
        assert 0.0 <= r <= 1.0
        assert 0.0 <= g <= 1.0
        assert 0.0 <= b <= 1.0

    def test_black_white(self):
        assert sp.hex_to_rgb("#000000") == (0.0, 0.0, 0.0)
        assert sp.hex_to_rgb("#FFFFFF") == (1.0, 1.0, 1.0)

    def test_invalid_empty(self):
        with pytest.raises(ValueError):
            sp.hex_to_rgb("")

    def test_invalid_none(self):
        with pytest.raises(ValueError):
            sp.hex_to_rgb(None)

    def test_invalid_format(self):
        with pytest.raises(ValueError):
            sp.hex_to_rgb("#GGGGGG")
        with pytest.raises(ValueError):
            sp.hex_to_rgb("#12")  # too short
        with pytest.raises(ValueError):
            sp.hex_to_rgb("#12345")  # wrong length

    def test_whitespace_stripped(self):
        assert sp.hex_to_rgb("  #FF0000  ") == (1.0, 0.0, 0.0)


class TestRgbToHex:
    def test_primary_colors(self):
        assert sp.rgb_to_hex(1.0, 0.0, 0.0) == "#ff0000"
        assert sp.rgb_to_hex(0.0, 1.0, 0.0) == "#00ff00"
        assert sp.rgb_to_hex(0.0, 0.0, 1.0) == "#0000ff"

    def test_black_white(self):
        assert sp.rgb_to_hex(0.0, 0.0, 0.0) == "#000000"
        assert sp.rgb_to_hex(1.0, 1.0, 1.0) == "#ffffff"

    def test_mid_values(self):
        result = sp.rgb_to_hex(0.5, 0.5, 0.5)
        # int(0.5 * 255) = int(127.5) = 127 = 0x7f
        assert result == "#7f7f7f"

    def test_boundary_zero(self):
        assert sp.rgb_to_hex(0.0, 0.0, 0.0) == "#000000"

    def test_boundary_one(self):
        assert sp.rgb_to_hex(1.0, 1.0, 1.0) == "#ffffff"

    def test_out_of_range_low(self):
        with pytest.raises(ValueError):
            sp.rgb_to_hex(-0.1, 0.5, 0.5)

    def test_out_of_range_high(self):
        with pytest.raises(ValueError):
            sp.rgb_to_hex(0.5, 1.1, 0.5)

    def test_non_numeric(self):
        with pytest.raises(ValueError):
            sp.rgb_to_hex("a", 0.5, 0.5)

    def test_roundtrip(self):
        original = "#c0ffee"
        r, g, b = sp.hex_to_rgb(original)
        result = sp.rgb_to_hex(r, g, b)
        assert result == original


class TestLightenColor:
    def test_lighten_zero(self):
        """amount=0 应返回原色"""
        color = "#264653"
        assert sp.lighten_color(color, 0.0) == color

    def test_lighten_one(self):
        """amount=1 应返回白色"""
        result = sp.lighten_color("#264653", 1.0)
        assert result == "#ffffff"

    def test_lighten_partial(self):
        result = sp.lighten_color("#000000", 0.5)
        r, g, b = sp.hex_to_rgb(result)
        assert abs(r - 0.5) < 0.01
        assert abs(g - 0.5) < 0.01
        assert abs(b - 0.5) < 0.01

    def test_invalid_amount_negative(self):
        with pytest.raises(ValueError):
            sp.lighten_color("#FF0000", -0.1)

    def test_invalid_amount_over_one(self):
        with pytest.raises(ValueError):
            sp.lighten_color("#FF0000", 1.1)


class TestDarkenColor:
    def test_darken_zero(self):
        """amount=0 应返回原色"""
        color = "#cdb4db"
        assert sp.darken_color(color, 0.0) == color

    def test_darken_one(self):
        """amount=1 应返回黑色"""
        result = sp.darken_color("#cdb4db", 1.0)
        assert result == "#000000"

    def test_darken_partial(self):
        result = sp.darken_color("#FFFFFF", 0.5)
        r, g, b = sp.hex_to_rgb(result)
        assert abs(r - 0.5) < 0.01
        assert abs(g - 0.5) < 0.01
        assert abs(b - 0.5) < 0.01

    def test_invalid_amount(self):
        with pytest.raises(ValueError):
            sp.darken_color("#FF0000", -0.1)


class TestGenerateGradient:
    def test_basic_gradient(self):
        colors = sp.generate_gradient("#000000", "#FFFFFF", 3)
        assert len(colors) == 3
        assert colors[0] == "#000000"
        assert colors[-1] == "#ffffff"

    def test_two_colors(self):
        colors = sp.generate_gradient("#FF0000", "#0000FF", 2)
        assert len(colors) == 2
        assert colors[0] == "#ff0000"
        assert colors[1] == "#0000ff"

    def test_many_steps(self):
        colors = sp.generate_gradient("#000000", "#FFFFFF", 10)
        assert len(colors) == 10
        # 渐变应单调递增亮度
        for i in range(len(colors) - 1):
            r1, g1, b1 = sp.hex_to_rgb(colors[i])
            r2, g2, b2 = sp.hex_to_rgb(colors[i + 1])
            assert (r2 + g2 + b2) >= (r1 + g1 + b1)

    def test_same_color(self):
        colors = sp.generate_gradient("#FF0000", "#FF0000", 5)
        assert all(c == "#ff0000" for c in colors)

    def test_n_less_than_2(self):
        with pytest.raises(ValueError):
            sp.generate_gradient("#000000", "#FFFFFF", 1)

    def test_n_not_int(self):
        with pytest.raises(ValueError):
            sp.generate_gradient("#000000", "#FFFFFF", 2.5)

    def test_invalid_start_color(self):
        with pytest.raises(ValueError):
            sp.generate_gradient("invalid", "#FFFFFF", 3)

    def test_invalid_end_color(self):
        with pytest.raises(ValueError):
            sp.generate_gradient("#000000", "invalid", 3)
