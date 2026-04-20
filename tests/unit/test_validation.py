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

    def test_non_finite_values_raise(self, cleanup_figures):
        with pytest.raises(ValueError, match="NaN 或 Inf"):
            sp.plot_bar(["A", "B"], np.array([1.0, np.nan]))


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

    def test_width_gap_relation_raises(self, cleanup_figures):
        """测试 width 与 gap 组合导致柱宽非正时报错"""
        with pytest.raises(ValueError, match="宽度将小于等于 0"):
            sp.plot_grouped_bar(
                ["A", "B"],
                {"S1": [1, 2], "S2": [2, 3], "S3": [3, 4]},
                width=0.1,
                gap=0.1,
            )

    def test_non_finite_series_raises(self, cleanup_figures):
        with pytest.raises(ValueError, match="NaN 或 Inf"):
            sp.plot_grouped_bar(["A", "B"], {"S1": [1.0, np.nan]})


class TestPlotStackedBarValidation:
    """测试 plot_stacked_bar 输入验证"""

    def test_empty_categories_raises(self, cleanup_figures):
        with pytest.raises(ValueError, match="不能为空列表"):
            sp.plot_stacked_bar([], {"A": [1, 2]})

    def test_empty_data_raises(self, cleanup_figures):
        with pytest.raises(ValueError, match="不能为空字典"):
            sp.plot_stacked_bar(["A", "B"], {})

    def test_data_length_mismatch_raises(self, cleanup_figures):
        with pytest.raises(ValueError, match="长度.*不一致"):
            sp.plot_stacked_bar(["A", "B"], {"Series": [1]})

    def test_non_finite_series_raises(self, cleanup_figures):
        with pytest.raises(ValueError, match="NaN 或 Inf"):
            sp.plot_stacked_bar(["A", "B"], {"Series": [1.0, np.nan]})


class TestPlotHorizontalBarValidation:
    """测试 plot_horizontal_bar 输入验证"""

    def test_empty_categories_raises(self, cleanup_figures):
        with pytest.raises(ValueError, match="不能为空列表"):
            sp.plot_horizontal_bar([], [])

    def test_length_mismatch_raises(self, cleanup_figures):
        with pytest.raises(ValueError, match="长度.*不一致"):
            sp.plot_horizontal_bar(["A", "B"], [1.0])


class TestPlotHistogramValidation:
    """测试 plot_histogram 输入验证"""

    def test_empty_data_raises(self, cleanup_figures):
        with pytest.raises(ValueError, match="至少需要 1 个有限数值"):
            sp.plot_histogram(np.array([]))

    def test_all_nan_data_raises(self, cleanup_figures):
        with pytest.raises(ValueError, match="至少需要 1 个有限数值"):
            sp.plot_histogram(np.array([np.nan, np.nan]))


class TestPlotComboValidation:
    """测试 plot_combo 输入验证"""

    def test_invalid_bar_width_raises(self, cleanup_figures):
        with pytest.raises(ValueError, match="bar_width"):
            sp.plot_combo(["A", "B"], bar_data={"S1": [1, 2]}, bar_width=0)

    def test_bar_data_non_finite_raises(self, cleanup_figures):
        with pytest.raises(ValueError, match="NaN 或 Inf"):
            sp.plot_combo(["A", "B"], bar_data={"S1": [1.0, np.nan]})

    def test_line_data_non_finite_raises(self, cleanup_figures):
        with pytest.raises(ValueError, match="NaN 或 Inf"):
            sp.plot_combo(
                ["A", "B"],
                bar_data={"S1": [1.0, 2.0]},
                line_data={"L1": [np.nan, 1.0]},
            )


class TestPlotBoxValidation:
    def test_empty_data_raises(self, cleanup_figures):
        with pytest.raises(ValueError, match="不能为空列表"):
            sp.plot_box([])


class TestPlotLollipopValidation:
    def test_non_finite_values_raise(self, cleanup_figures):
        with pytest.raises(ValueError, match="NaN 或 Inf"):
            sp.plot_lollipop(["A", "B"], np.array([1.0, np.nan]))


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

    def test_empty_y_list_raises(self, cleanup_figures):
        x = np.linspace(0, 10, 100)
        with pytest.raises(ValueError, match="y_list"):
            sp.plot_multi_line(x, [])


class TestPlotMultiValidation:
    def test_empty_y_list_raises(self, cleanup_figures):
        x = np.linspace(0, 10, 100)
        with pytest.raises(ValueError, match="y_list"):
            sp.plot_multi(x, [])


class TestPlotMultiAreaValidation:
    def test_empty_y_list_raises(self, cleanup_figures):
        x = np.linspace(0, 10, 100)
        with pytest.raises(ValueError, match="y_list"):
            sp.plot_multi_area(x, [])


class TestPlotMultiTimeseriesValidation:
    def test_empty_y_list_raises(self, cleanup_figures):
        t = np.arange(10)
        with pytest.raises(ValueError, match="y_list"):
            sp.plot_multi_timeseries(t, [])


class TestValidatePositiveNumberBool:
    """测试 validate_positive_number 对布尔值的处理"""

    def test_bool_true_raises(self):
        """布尔值 True 应该抛出 ValueError"""
        with pytest.raises(ValueError, match="必须是数值类型"):
            sp.validate_positive_number(True, "test")

    def test_bool_false_raises(self):
        """布尔值 False 应该抛出 ValueError"""
        with pytest.raises(ValueError, match="必须是数值类型"):
            sp.validate_positive_number(False, "test")

    def test_int_one_passes(self):
        """整数 1 应该通过验证"""
        result = sp.validate_positive_number(1, "test")
        assert result == 1.0

    def test_int_zero_allow_zero(self):
        """整数 0 在 allow_zero=True 时应该通过"""
        result = sp.validate_positive_number(0, "test", allow_zero=True)
        assert result == 0.0


class TestValidateParamsEqualLength:
    """测试 validate_params 装饰器的 equal_length 对 numpy 数组的处理"""

    def test_numpy_1d_equal_length(self):
        """一维 numpy 数组等长验证"""
        from sciplot._core.utils import validate_params

        @validate_params(equal_length=[("x", "y")])
        def dummy_func(x, y):
            return True

        assert dummy_func(np.array([1, 2, 3]), np.array([4, 5, 6]))

    def test_numpy_1d_unequal_length_raises(self):
        """一维 numpy 数组不等长应抛出异常"""
        from sciplot._core.utils import validate_params

        @validate_params(equal_length=[("x", "y")])
        def dummy_func(x, y):
            return True

        with pytest.raises(ValueError, match="长度.*不一致"):
            dummy_func(np.array([1, 2, 3]), np.array([4, 5]))

    def test_list_vs_numpy_equal_length(self):
        """列表与 numpy 数组等长验证"""
        from sciplot._core.utils import validate_params

        @validate_params(equal_length=[("x", "y")])
        def dummy_func(x, y):
            return True

        assert dummy_func([1, 2, 3], np.array([4, 5, 6]))

    def test_none_values_skip_validation(self):
        """None 值应跳过等长验证"""
        from sciplot._core.utils import validate_params

        @validate_params(equal_length=[("x", "y")])
        def dummy_func(x, y):
            return True

        assert dummy_func(None, np.array([1, 2, 3]))


class TestValidateArrayLikeEdgeCases:
    """测试 validate_array_like 边界情况"""

    def test_generator_input(self):
        """生成器输入应该被转换为列表"""
        result = sp.validate_array_like(range(5), "test")
        assert result == [0, 1, 2, 3, 4]

    def test_min_length_negative_raises(self):
        """负数 min_length 应该抛出异常"""
        with pytest.raises(ValueError, match="min_length 必须为非负整数"):
            sp.validate_array_like([1, 2], "test", min_length=-1)

    def test_min_length_zero_passes(self):
        """min_length=0 应该通过"""
        result = sp.validate_array_like([1], "test", min_length=0)
        assert result == [1]

    def test_numpy_2d_array(self):
        """二维 numpy 数组应该被转换为嵌套列表"""
        arr = np.array([[1, 2], [3, 4]])
        result = sp.validate_array_like(arr, "test")
        assert result == [[1, 2], [3, 4]]
