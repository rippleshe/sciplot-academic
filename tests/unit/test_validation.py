"""
输入验证测试 — 边界情况和异常路径
"""

import pytest
import numpy as np
import sciplot as sp


class TestValidateArrayLike:
    """测试 validate_array_like 函数"""

    def test_validate_list(self):
        """测试列表输入"""
        result = sp.validate_array_like([1, 2, 3], "test")
        assert result == [1, 2, 3]

    def test_validate_tuple(self):
        """测试元组输入"""
        result = sp.validate_array_like((1, 2, 3), "test")
        assert result == [1, 2, 3]

    def test_validate_numpy_array(self):
        """测试 numpy 数组输入"""
        arr = np.array([1, 2, 3])
        result = sp.validate_array_like(arr, "test")
        assert result == [1, 2, 3]

    def test_validate_none_raises(self):
        """测试 None 输入抛出异常"""
        with pytest.raises(TypeError, match="不能为 None"):
            sp.validate_array_like(None, "test")

    def test_validate_empty_raises(self):
        """测试空数组抛出异常"""
        with pytest.raises(ValueError, match="不能为空数组"):
            sp.validate_array_like([], "test")

    def test_validate_empty_allowed(self):
        """测试允许空数组"""
        result = sp.validate_array_like([], "test", allow_empty=True)
        assert result == []

    def test_validate_min_length(self):
        """测试最小长度要求"""
        sp.validate_array_like([1, 2, 3], "test", min_length=3)
        with pytest.raises(ValueError, match="长度不能小于"):
            sp.validate_array_like([1, 2], "test", min_length=3)

    def test_validate_invalid_type(self):
        """测试无效类型"""
        with pytest.raises(TypeError, match="必须是数组类型"):
            sp.validate_array_like(123, "test")


class TestValidateLabelsMatchData:
    """测试 validate_labels_match_data 函数"""

    def test_auto_generate_labels(self):
        """测试自动生成标签"""
        result = sp.validate_labels_match_data(None, [1, 2, 3])
        assert result == ["Series 1", "Series 2", "Series 3"]

    def test_valid_labels(self):
        """测试有效标签"""
        result = sp.validate_labels_match_data(["A", "B"], [1, 2])
        assert result == ["A", "B"]

    def test_mismatch_length_raises(self):
        """测试长度不匹配抛出异常"""
        with pytest.raises(ValueError, match="长度.*不一致"):
            sp.validate_labels_match_data(["A"], [1, 2])


class TestValidatePositiveNumber:
    """测试 validate_positive_number 函数"""

    def test_positive_number(self):
        """测试正数"""
        result = sp.validate_positive_number(5, "test")
        assert result == 5.0

    def test_zero_not_allowed(self):
        """测试零不允许"""
        with pytest.raises(ValueError, match="必须为正数"):
            sp.validate_positive_number(0, "test")

    def test_zero_allowed(self):
        """测试零允许"""
        result = sp.validate_positive_number(0, "test", allow_zero=True)
        assert result == 0.0

    def test_negative_raises(self):
        """测试负数抛出异常"""
        with pytest.raises(ValueError, match="必须为正数"):
            sp.validate_positive_number(-1, "test")

    def test_string_number(self):
        """测试字符串数字"""
        result = sp.validate_positive_number("5", "test")
        assert result == 5.0

    def test_invalid_string_raises(self):
        """测试无效字符串抛出异常"""
        with pytest.raises(ValueError, match="必须是数值类型"):
            sp.validate_positive_number("abc", "test")


class TestValidateChoice:
    """测试 validate_choice 函数"""

    def test_valid_choice(self):
        """测试有效选择"""
        result = sp.validate_choice("a", ["a", "b", "c"], "test")
        assert result == "a"

    def test_case_insensitive(self):
        """测试大小写不敏感"""
        result = sp.validate_choice("A", ["a", "b", "c"], "test")
        assert result == "a"

    def test_case_sensitive(self):
        """测试大小写敏感"""
        result = sp.validate_choice("a", ["a", "b", "c"], "test", case_sensitive=True)
        assert result == "a"

    def test_invalid_choice_raises(self):
        """测试无效选择抛出异常"""
        with pytest.raises(ValueError, match="无效"):
            sp.validate_choice("d", ["a", "b", "c"], "test")

    def test_none_raises(self):
        """测试 None 抛出异常"""
        with pytest.raises(TypeError, match="不能为 None"):
            sp.validate_choice(None, ["a", "b"], "test")


class TestValidateDictNotEmpty:
    """测试 validate_dict_not_empty 函数"""

    def test_valid_dict(self):
        """测试有效字典"""
        result = sp.validate_dict_not_empty({"a": 1}, "test")
        assert result == {"a": 1}

    def test_empty_dict_raises(self):
        """测试空字典抛出异常"""
        with pytest.raises(ValueError, match="不能为空字典"):
            sp.validate_dict_not_empty({}, "test")

    def test_non_dict_raises(self):
        """测试非字典抛出异常"""
        with pytest.raises(TypeError, match="必须是字典类型"):
            sp.validate_dict_not_empty([1, 2], "test")


class TestPlotBarValidation:
    """测试 plot_bar 输入验证"""

    def test_empty_categories_raises(self, cleanup_figures):
        """测试空分类抛出异常"""
        with pytest.raises(ValueError, match="不能为空列表"):
            sp.plot_bar([], np.array([1, 2, 3]))

    def test_length_mismatch_raises(self, cleanup_figures):
        """测试长度不匹配抛出异常"""
        with pytest.raises(ValueError, match="长度.*不一致"):
            sp.plot_bar(["A", "B"], np.array([1, 2, 3]))

    def test_invalid_width_raises(self, cleanup_figures):
        """测试无效宽度抛出异常"""
        with pytest.raises(ValueError, match="必须为正数"):
            sp.plot_bar(["A", "B"], np.array([1, 2]), width=0)


class TestPlotGroupedBarValidation:
    """测试 plot_grouped_bar 输入验证"""

    def test_empty_groups_raises(self, cleanup_figures):
        """测试空分组抛出异常"""
        with pytest.raises(ValueError, match="不能为空列表"):
            sp.plot_grouped_bar([], {"A": [1, 2]})

    def test_empty_data_raises(self, cleanup_figures):
        """测试空数据抛出异常"""
        with pytest.raises(ValueError, match="不能为空字典"):
            sp.plot_grouped_bar(["A", "B"], {})

    def test_data_length_mismatch_raises(self, cleanup_figures):
        """测试数据长度不匹配抛出异常"""
        with pytest.raises(ValueError, match="数据系列.*长度.*不一致"):
            sp.plot_grouped_bar(["A", "B"], {"Series": [1]})

    def test_invalid_width_raises(self, cleanup_figures):
        """测试无效宽度抛出异常"""
        with pytest.raises(ValueError, match="必须为正数"):
            sp.plot_grouped_bar(["A", "B"], {"S": [1, 2]}, width=0)


class TestPlotMultiLineValidation:
    """测试 plot_multi_line 输入验证"""

    def test_labels_mismatch_raises(self, cleanup_figures):
        """测试标签长度不匹配抛出异常"""
        x = np.linspace(0, 10, 100)
        y_list = [np.sin(x), np.cos(x)]
        with pytest.raises(ValueError, match="labels 长度.*不一致"):
            sp.plot_multi_line(x, y_list, labels=["A"])

    def test_auto_labels(self, cleanup_figures):
        """测试自动生成标签"""
        x = np.linspace(0, 10, 100)
        y_list = [np.sin(x), np.cos(x)]
        fig, ax = sp.plot_multi_line(x, y_list)
        assert fig is not None
        assert ax is not None
