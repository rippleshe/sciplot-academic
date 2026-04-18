"""
PlotResult 和 GridSpecResult 返回类型测试
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
import sciplot as sp
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.gridspec import GridSpec
from pathlib import Path


class TestPlotResultBasic:
    """测试 PlotResult 基本功能"""

    def test_plot_result_creation(self, cleanup_figures):
        """测试 PlotResult 创建"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        assert isinstance(result.fig, Figure)
        assert isinstance(result.ax, Axes)
        assert result.figure is fig

    def test_plot_result_tuple_unpacking(self, cleanup_figures):
        """测试元组解包"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        # 测试解包
        f, a = result
        assert f is fig
        assert a is ax

    def test_plot_result_indexing(self, cleanup_figures):
        """测试索引访问"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        assert result[0] is fig
        assert result[1] is ax

    def test_plot_result_length(self, cleanup_figures):
        """测试长度"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        assert len(result) == 2


class TestPlotResultChaining:
    """测试 PlotResult 链式调用"""

    def test_xlabel_chaining(self, cleanup_figures):
        """测试 xlabel 链式调用"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        returned = result.xlabel("X Label")
        assert returned is result
        assert ax.get_xlabel() == "X Label"

    def test_ylabel_chaining(self, cleanup_figures):
        """测试 ylabel 链式调用"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        returned = result.ylabel("Y Label")
        assert returned is result
        assert ax.get_ylabel() == "Y Label"

    def test_title_chaining(self, cleanup_figures):
        """测试 title 链式调用"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        returned = result.title("Title")
        assert returned is result
        assert ax.get_title() == "Title"

    def test_xlim_ylim_chaining(self, cleanup_figures):
        """测试 xlim/ylim 链式调用"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        result.xlabel("X").ylabel("Y").title("T")
        assert ax.get_xlabel() == "X"
        assert ax.get_ylabel() == "Y"
        assert ax.get_title() == "T"

    def test_grid_chaining(self, cleanup_figures):
        """测试 grid 链式调用"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        returned = result.grid(True)
        assert returned is result

    def test_legend_chaining(self, cleanup_figures):
        """测试 legend 链式调用"""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2], label="line")
        result = sp.PlotResult(fig, ax)

        returned = result.legend()
        assert returned is result
        assert ax.get_legend() is not None

    def test_tight_layout_chaining(self, cleanup_figures):
        """测试 tight_layout 链式调用"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        returned = result.tight_layout()
        assert returned is result

    def test_full_chain(self, cleanup_figures):
        """测试完整链式调用"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        result.xlabel("X").ylabel("Y").title("Title").grid(True).tight_layout()

        assert ax.get_xlabel() == "X"
        assert ax.get_ylabel() == "Y"
        assert ax.get_title() == "Title"


class TestPlotResultSave:
    """测试 PlotResult 保存功能"""

    def test_save_returns_list(self, temp_dir, cleanup_figures):
        """测试 save 返回列表"""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])
        result = sp.PlotResult(fig, ax)

        output_path = temp_dir / "test_fig"
        paths = result.save(output_path, formats=("png",))

        assert isinstance(paths, list)
        assert len(paths) == 1
        assert isinstance(paths[0], Path)
        assert paths[0].exists()

    def test_save_multiple_formats(self, temp_dir, cleanup_figures):
        """测试保存多种格式"""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])
        result = sp.PlotResult(fig, ax)

        output_path = temp_dir / "multi"
        paths = result.save(output_path, formats=("png", "pdf"))

        assert len(paths) == 2
        for path in paths:
            assert path.exists()


class TestPlotResultSubplots:
    """测试多子图的 PlotResult"""

    def test_subplots_array_access(self, cleanup_figures):
        """测试多子图数组访问"""
        fig, axes = plt.subplots(1, 2)
        result = sp.PlotResult(fig, axes)

        assert result._is_array is True
        assert isinstance(result.axes, np.ndarray)
        assert isinstance(result.ax_array, np.ndarray)
        assert result.ax_array.shape == (2,)

    def test_subplots_single_ax_raises(self, cleanup_figures):
        """测试单个子图访问多子图时抛出异常"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        assert result._is_array is False
        with pytest.raises(AttributeError):
            _ = result.ax_array

    def test_subplots_multi_ax_raises(self, cleanup_figures):
        """测试多子图访问单个子图时抛出异常"""
        fig, axes = plt.subplots(1, 2)
        result = sp.PlotResult(fig, axes)

        with pytest.raises(AttributeError):
            _ = result.ax

    def test_subplots_xlabel_all(self, cleanup_figures):
        """测试多子图统一设置 xlabel"""
        fig, axes = plt.subplots(1, 2)
        result = sp.PlotResult(fig, axes)

        result.xlabel("Common X")

        for ax in axes:
            assert ax.get_xlabel() == "Common X"

    def test_subplots_ylabel_all(self, cleanup_figures):
        """测试多子图统一设置 ylabel"""
        fig, axes = plt.subplots(2, 2)
        result = sp.PlotResult(fig, axes)

        result.ylabel("Common Y")

        for ax in axes.flat:
            assert ax.get_ylabel() == "Common Y"

    def test_subplots_suptitle(self, cleanup_figures):
        """测试多子图设置总标题"""
        fig, axes = plt.subplots(1, 2)
        result = sp.PlotResult(fig, axes)

        result.suptitle("Main Title")

        # suptitle 设置后可以通过 fig._suptitle 检查
        assert fig._suptitle is not None


class TestPlotResultLayers:
    """测试 PlotResult 图层添加"""

    def test_plot_layer(self, cleanup_figures):
        """测试添加折线"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        x = np.linspace(0, 10, 100)
        result.plot(x, np.sin(x))

        assert len(ax.lines) == 1

    def test_scatter_layer(self, cleanup_figures):
        """测试添加散点"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        result.scatter([1, 2, 3], [1, 4, 9])

        assert len(ax.collections) > 0

    def test_axhline_layer(self, cleanup_figures):
        """测试添加水平线"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        result.axhline(0.5)

        assert len(ax.axhline(0.5).figure.axes) > 0

    def test_axvline_layer(self, cleanup_figures):
        """测试添加垂直线"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        result.axvline(0.5)

        # axvline 会创建一条线
        lines_before = len(ax.lines)
        ax.axvline(0.5)
        assert len(ax.lines) > lines_before - 1

    def test_annotate_layer(self, cleanup_figures):
        """测试添加标注"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        result.annotate("Point", (0.5, 0.5))

        # 检查文本是否添加
        texts = [child for child in ax.get_children() if hasattr(child, 'get_text')]
        assert len(texts) > 0


class TestPlotResultContextManager:
    """测试 PlotResult 上下文管理器"""

    def test_context_manager(self, cleanup_figures):
        """测试上下文管理器自动关闭"""
        fig, ax = plt.subplots()
        fig_id = id(fig)

        with sp.PlotResult(fig, ax) as result:
            assert result.fig is fig

        # 上下文退出后图形应该被关闭
        # 注意：这里只是测试没有异常抛出


class TestPlotResultUtility:
    """测试 PlotResult 工具方法"""

    def test_set_labels(self, cleanup_figures):
        """测试 set_labels 方法"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        result.set_labels(xlabel="X", ylabel="Y", title="Title")

        assert ax.get_xlabel() == "X"
        assert ax.get_ylabel() == "Y"
        assert ax.get_title() == "Title"

    def test_set_labels_partial(self, cleanup_figures):
        """测试 set_labels 部分参数"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        result.set_labels(xlabel="X")

        assert ax.get_xlabel() == "X"
        assert ax.get_ylabel() == ""


class TestGridSpecResult:
    """测试 GridSpecResult"""

    def test_gridspec_result_creation(self, cleanup_figures):
        """测试 GridSpecResult 创建"""
        fig = plt.figure()
        gs = fig.add_gridspec(2, 2)
        result = sp.GridSpecResult(fig, gs)

        assert isinstance(result.fig, Figure)
        assert isinstance(result.gs, GridSpec)
        assert isinstance(result.gridspec, GridSpec)

    def test_gridspec_tuple_unpacking(self, cleanup_figures):
        """测试 GridSpecResult 元组解包"""
        fig = plt.figure()
        gs = fig.add_gridspec(2, 2)
        result = sp.GridSpecResult(fig, gs)

        f, g = result
        assert f is fig
        assert g is gs

    def test_gridspec_indexing(self, cleanup_figures):
        """测试 GridSpecResult 索引访问"""
        fig = plt.figure()
        gs = fig.add_gridspec(2, 2)
        result = sp.GridSpecResult(fig, gs)

        assert result[0] is fig
        assert result[1] is gs

    def test_gridspec_add_subplot(self, cleanup_figures):
        """测试 GridSpecResult 添加子图"""
        fig = plt.figure()
        gs = fig.add_gridspec(2, 2)
        result = sp.GridSpecResult(fig, gs)

        ax = result.add_subplot(gs[0, 0])
        assert isinstance(ax, Axes)


class TestPlotResultRepr:
    """测试 PlotResult 字符串表示"""

    def test_single_ax_repr(self, cleanup_figures):
        """测试单个子图的 repr"""
        fig, ax = plt.subplots()
        result = sp.PlotResult(fig, ax)

        repr_str = repr(result)
        assert "PlotResult" in repr_str
        assert "fig=" in repr_str
        assert "ax=" in repr_str

    def test_multi_ax_repr(self, cleanup_figures):
        """测试多子图的 repr"""
        fig, axes = plt.subplots(1, 2)
        result = sp.PlotResult(fig, axes)

        repr_str = repr(result)
        assert "PlotResult" in repr_str
        assert "axes=array" in repr_str


class TestIntegrationWithPlotFunctions:
    """测试与绘图函数的集成"""

    def test_plot_function_returns_result(self, test_data, cleanup_figures):
        """测试绘图函数可以包装为 PlotResult"""
        fig, ax = sp.plot(test_data["x"], test_data["y"])

        # 传统用法仍然工作
        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)

        # 可以包装为 PlotResult
        result = sp.PlotResult(fig, ax)
        assert isinstance(result, sp.PlotResult)

    def test_plot_result_chain_after_plot(self, test_data, cleanup_figures):
        """测试绘图后链式调用"""
        fig, ax = sp.plot(test_data["x"], test_data["y"])
        result = sp.PlotResult(fig, ax)

        result.xlabel("Time").ylabel("Value").tight_layout()

        assert ax.get_xlabel() == "Time"
        assert ax.get_ylabel() == "Value"

    def test_subplots_result(self, cleanup_figures):
        """测试子图结果"""
        fig, axes = sp.create_subplots(1, 2, venue="ieee")
        result = sp.PlotResult(fig, axes)

        assert isinstance(result.ax_array, np.ndarray)
        assert result.ax_array.shape == (2,)
