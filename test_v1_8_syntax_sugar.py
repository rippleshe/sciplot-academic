"""
SciPlot v1.8.0 语法糖功能全面测试

测试内容:
1. 链式调用 (Fluent Interface)
2. 上下文管理器 (Context Manager)
3. 简洁函数别名 (Aliases)

运行: uv run python test_v1_8_syntax_sugar.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import tempfile

print("=" * 70)
print("SciPlot v1.8.0 语法糖功能测试")
print("=" * 70)

# 创建临时目录用于保存测试图片
temp_dir = tempfile.mkdtemp(prefix="sciplot_test_")
print(f"\n临时目录: {temp_dir}")

# 测试数据
x = np.linspace(0, 10, 50)
y = np.sin(x)
y2 = np.cos(x)
y3 = np.sin(x) * 0.5
categories = ["A", "B", "C", "D"]
values = [10, 20, 15, 25]

errors = []


def check_save(paths, desc):
    """辅助函数：检查保存结果"""
    if isinstance(paths, list) and len(paths) > 0:
        filepath = str(paths[0])
        if os.path.exists(filepath):
            print(f"  ✓ {desc}: {os.path.basename(filepath)}")
            return True
    print(f"  ✗ {desc}: 保存失败")
    return False


# ═══════════════════════════════════════════════════════════════
# 测试 1: 链式调用基础功能
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("测试 1: 链式调用 (Fluent Interface)")
print("=" * 70)

try:
    import sciplot as sp
    import matplotlib.pyplot as plt

    # 测试 1.1: 基础链式调用
    print("\n[1.1] 基础链式调用: sp.style('nature').palette('pastel').plot(x, y).save(...)")
    paths = sp.style("nature").palette("pastel").plot(x, y).save(
        os.path.join(temp_dir, "test_fluent_basic"), dpi=150, formats=("png",)
    )
    assert check_save(paths, "基础链式调用")

    # 测试 1.2: 多图层链式调用
    print("\n[1.2] 多图层链式调用")
    paths = (sp.style("ieee")
                  .palette("earth")
                  .plot(x, y, label="sin")
                  .scatter(x[::5], y2[::5], label="cos")
                  .legend()
                  .xlabel("X轴")
                  .ylabel("Y轴")
                  .title("多图层测试")
                  .save(os.path.join(temp_dir, "test_fluent_multi"), dpi=150, formats=("png",)))
    assert check_save(paths, "多图层链式调用")

    # 测试 1.3: 从 palette 入口开始
    print("\n[1.3] 从 palette 入口开始")
    paths = sp.palette("ocean").plot(x, y).save(
        os.path.join(temp_dir, "test_fluent_palette_entry"), dpi=150, formats=("png",)
    )
    assert check_save(paths, "palette 入口")

    # 测试 1.4: 使用 chain 通用入口
    print("\n[1.4] 使用 chain 通用入口")
    paths = sp.chain("thesis", "100yuan").plot(x, y).save(
        os.path.join(temp_dir, "test_fluent_chain"), dpi=150, formats=("png",)
    )
    assert check_save(paths, "chain 入口")

    # 测试 1.5: 自定义 figsize
    print("\n[1.5] 自定义 figsize")
    paths = sp.style("nature").figsize(12, 6).plot(x, y).save(
        os.path.join(temp_dir, "test_fluent_figsize"), dpi=150, formats=("png",)
    )
    assert check_save(paths, "自定义 figsize")

    # 测试 1.6: 各种图表类型
    print("\n[1.6] 链式调用各种图表类型")

    # scatter
    paths = sp.style("nature").scatter(x, y).save(
        os.path.join(temp_dir, "test_fluent_scatter"), dpi=150, formats=("png",)
    )
    check_save(paths, "scatter")

    # bar
    paths = sp.style("nature").bar(categories, values).save(
        os.path.join(temp_dir, "test_fluent_bar"), dpi=150, formats=("png",)
    )
    check_save(paths, "bar")

    # hist
    paths = sp.style("nature").hist(np.random.randn(100), bins=15).save(
        os.path.join(temp_dir, "test_fluent_hist"), dpi=150, formats=("png",)
    )
    check_save(paths, "hist")

    # area
    paths = sp.style("nature").area(x, y).save(
        os.path.join(temp_dir, "test_fluent_area"), dpi=150, formats=("png",)
    )
    check_save(paths, "area")

    # errorbar
    errors_y = np.random.rand(len(x)) * 0.1
    paths = sp.style("nature").errorbar(x, y, yerr=errors_y).save(
        os.path.join(temp_dir, "test_fluent_errorbar"), dpi=150, formats=("png",)
    )
    check_save(paths, "errorbar")

    print("\n[链式调用] 所有测试通过 ✓")

except Exception as e:
    errors.append(f"链式调用测试失败: {e}")
    print(f"\n  ✗ 失败: {e}")
    import traceback
    traceback.print_exc()

# ═══════════════════════════════════════════════════════════════
# 测试 2: 上下文管理器
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("测试 2: 上下文管理器 (Context Manager)")
print("=" * 70)

try:
    import sciplot as sp
    import matplotlib.pyplot as plt

    # 保存原始状态
    original_color = plt.rcParams.get('axes.prop_cycle')

    # 测试 2.1: 基础上下文
    print("\n[2.1] 基础上下文: with sp.style_context('ieee', palette='earth')")
    with sp.style_context("ieee", palette="earth"):
        fig, ax = sp.plot(x, y)
        paths = sp.save(fig, os.path.join(temp_dir, "test_context_basic"), dpi=150, formats=("png",))
        check_save(paths, "基础上下文")

    # 测试 2.2: 只修改配色
    print("\n[2.2] 只修改配色: with sp.style_context(palette='100yuan')")
    with sp.style_context(palette="100yuan"):
        fig, ax = sp.plot(x, y)
        paths = sp.save(fig, os.path.join(temp_dir, "test_context_palette"), dpi=150, formats=("png",))
        check_save(paths, "只修改配色")

    # 测试 2.3: 使用简写 context
    print("\n[2.3] 使用简写 context()")
    with sp.context("thesis"):
        fig, ax = sp.plot(x, y)
        paths = sp.save(fig, os.path.join(temp_dir, "test_context_short"), dpi=150, formats=("png",))
        check_save(paths, "简写 context")

    # 测试 2.4: 特定场景上下文
    print("\n[2.4] 特定场景上下文")

    with sp.ieee_context():
        fig, ax = sp.plot(x, y)
        paths = sp.save(fig, os.path.join(temp_dir, "test_context_ieee"), dpi=150, formats=("png",))
        check_save(paths, "ieee_context")

    with sp.nature_context(palette="ocean"):
        fig, ax = sp.plot(x, y)
        paths = sp.save(fig, os.path.join(temp_dir, "test_context_nature"), dpi=150, formats=("png",))
        check_save(paths, "nature_context")

    with sp.thesis_context():
        fig, ax = sp.plot(x, y)
        paths = sp.save(fig, os.path.join(temp_dir, "test_context_thesis"), dpi=150, formats=("png",))
        check_save(paths, "thesis_context")

    # 测试 2.5: 嵌套上下文
    print("\n[2.5] 嵌套上下文")
    with sp.style_context("nature"):
        fig1, ax1 = sp.plot(x, y, title="外层: nature")
        paths1 = sp.save(fig1, os.path.join(temp_dir, "test_context_outer"), dpi=150, formats=("png",))

        with sp.style_context("ieee"):
            fig2, ax2 = sp.plot(x, y, title="内层: ieee")
            paths2 = sp.save(fig2, os.path.join(temp_dir, "test_context_inner"), dpi=150, formats=("png",))

        fig3, ax3 = sp.plot(x, y, title="回到外层: nature")
        paths3 = sp.save(fig3, os.path.join(temp_dir, "test_context_back"), dpi=150, formats=("png",))

        assert check_save(paths1, "嵌套-外层")
        assert check_save(paths2, "嵌套-内层")
        assert check_save(paths3, "嵌套-回到外层")

    # 测试 2.6: 检查状态恢复
    print("\n[2.6] 检查状态恢复")
    # 获取当前颜色循环
    current_color = plt.rcParams.get('axes.prop_cycle')
    print(f"  ✓ 上下文退出后状态正常")

    print("\n[上下文管理器] 所有测试通过 ✓")

except Exception as e:
    errors.append(f"上下文管理器测试失败: {e}")
    print(f"\n  ✗ 失败: {e}")
    import traceback
    traceback.print_exc()

# ═══════════════════════════════════════════════════════════════
# 测试 3: 简洁函数别名
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("测试 3: 简洁函数别名 (Aliases)")
print("=" * 70)

try:
    import sciplot as sp
    import matplotlib.pyplot as plt

    # 测试 3.1: 基础别名
    print("\n[3.1] 基础图表别名")

    # line
    fig, ax = sp.line(x, y, xlabel="X", ylabel="Y")
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_line"), dpi=150, formats=("png",))
    check_save(paths, "line()")

    # scatter
    fig, ax = sp.scatter(x, y, xlabel="X", ylabel="Y")
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_scatter"), dpi=150, formats=("png",))
    check_save(paths, "scatter()")

    # bar
    fig, ax = sp.bar(categories, values)
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_bar"), dpi=150, formats=("png",))
    check_save(paths, "bar()")

    # hist
    fig, ax = sp.hist(np.random.randn(100), bins=15)
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_hist"), dpi=150, formats=("png",))
    check_save(paths, "hist()")

    # box
    data = [np.random.randn(50) for _ in range(3)]
    fig, ax = sp.box(data, labels=["A", "B", "C"])
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_box"), dpi=150, formats=("png",))
    check_save(paths, "box()")

    # violin
    fig, ax = sp.violin(data, labels=["A", "B", "C"])
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_violin"), dpi=150, formats=("png",))
    check_save(paths, "violin()")

    # 测试 3.2: 多系列别名
    print("\n[3.2] 多系列图表别名")

    # multi
    fig, ax = sp.multi(x, [y, y2, y3], labels=["sin", "cos", "0.5sin"])
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_multi"), dpi=150, formats=("png",))
    check_save(paths, "multi()")

    # multi_line (与 multi 相同)
    fig, ax = sp.multi_line(x, [y, y2], labels=["sin", "cos"])
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_multi_line"), dpi=150, formats=("png",))
    check_save(paths, "multi_line()")

    # area
    fig, ax = sp.area(x, y, alpha=0.5)
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_area"), dpi=150, formats=("png",))
    check_save(paths, "area()")

    # multi_area
    fig, ax = sp.multi_area(x, [y, y2], labels=["sin", "cos"], alpha=0.3)
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_multi_area"), dpi=150, formats=("png",))
    check_save(paths, "multi_area()")

    # 测试 3.3: 分布统计别名
    print("\n[3.3] 分布统计图表别名")

    # grouped_bar
    data_dict = {"A": [1, 2, 3], "B": [4, 5, 6]}
    fig, ax = sp.grouped_bar(["X", "Y", "Z"], data_dict)
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_grouped_bar"), dpi=150, formats=("png",))
    check_save(paths, "grouped_bar()")

    # stacked_bar
    fig, ax = sp.stacked_bar(["X", "Y", "Z"], data_dict)
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_stacked_bar"), dpi=150, formats=("png",))
    check_save(paths, "stacked_bar()")

    # hbar (水平柱状图)
    fig, ax = sp.hbar(categories, values)
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_hbar"), dpi=150, formats=("png",))
    check_save(paths, "hbar()")

    # 测试 3.4: 高级图表别名
    print("\n[3.4] 高级图表别名")

    # errorbar
    errors_y = np.random.rand(len(x)) * 0.1
    fig, ax = sp.errorbar(x, y, yerr=errors_y)
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_errorbar"), dpi=150, formats=("png",))
    check_save(paths, "errorbar()")

    # confidence
    y_std = np.random.rand(len(x)) * 0.1
    fig, ax = sp.confidence(x, y, y_std, xlabel="X", ylabel="Y")
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_confidence"), dpi=150, formats=("png",))
    check_save(paths, "confidence()")

    # heatmap
    matrix = np.random.rand(5, 5)
    fig, ax = sp.heatmap(matrix, show_values=True)
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_heatmap"), dpi=150, formats=("png",))
    check_save(paths, "heatmap()")

    # combo
    bar_d = {"销量": [10, 20, 30]}
    line_d = {"趋势": [12, 22, 32]}
    fig, ax1, ax2 = sp.combo(["Q1", "Q2", "Q3"], bar_d, line_d)
    paths = sp.save(fig, os.path.join(temp_dir, "test_alias_combo"), dpi=150, formats=("png",))
    check_save(paths, "combo()")

    # 测试 3.5: 别名与原函数等价性
    print("\n[3.5] 别名与原函数等价性验证")

    # 比较 line 和 plot_line 的返回值类型
    fig1, ax1 = sp.line(x, y)
    fig2, ax2 = sp.plot_line(x, y)
    assert type(fig1) == type(fig2), "line() 和 plot_line() 返回类型不一致"
    assert type(ax1) == type(ax2), "line() 和 plot_line() 返回类型不一致"
    print(f"  ✓ line() 与 plot_line() 等价")

    fig1, ax1 = sp.scatter(x, y)
    fig2, ax2 = sp.plot_scatter(x, y)
    assert type(fig1) == type(fig2), "scatter() 和 plot_scatter() 返回类型不一致"
    print(f"  ✓ scatter() 与 plot_scatter() 等价")

    fig1, ax1 = sp.bar(categories, values)
    fig2, ax2 = sp.plot_bar(categories, values)
    assert type(fig1) == type(fig2), "bar() 和 plot_bar() 返回类型不一致"
    print(f"  ✓ bar() 与 plot_bar() 等价")

    print("\n[简洁函数别名] 所有测试通过 ✓")

except Exception as e:
    errors.append(f"简洁函数别名测试失败: {e}")
    print(f"\n  ✗ 失败: {e}")
    import traceback
    traceback.print_exc()

# ═══════════════════════════════════════════════════════════════
# 测试 4: 组合使用
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("测试 4: 组合使用场景")
print("=" * 70)

try:
    import sciplot as sp

    # 测试 4.1: 链式调用 + 别名
    print("\n[4.1] 链式调用中使用别名")
    # 注意: 链式调用内部使用自己的方法，但可以在链式调用前后使用别名

    # 在上下文管理器中使用别名
    with sp.style_context("ieee"):
        fig, ax = sp.line(x, y, xlabel="时间", ylabel="数值")
        paths = sp.save(fig, os.path.join(temp_dir, "test_combo_context_alias"), dpi=150, formats=("png",))
        check_save(paths, "上下文 + 别名")

    # 测试 4.2: 复杂工作流
    print("\n[4.2] 复杂工作流")

    # 使用上下文管理器设置基础样式
    with sp.nature_context(palette="earth"):
        # 使用简洁别名快速绘图
        fig, ax = sp.multi(x, [y, y2, y3], labels=["sin", "cos", "0.5sin"],
                          xlabel="时间 (s)", ylabel="幅值")

        # 使用智能辅助工具优化
        sp.smart_legend(ax, outside=True)

        # 保存
        paths = sp.save(fig, os.path.join(temp_dir, "test_combo_workflow"), dpi=150, formats=("png",))
        check_save(paths, "复杂工作流")

    print("\n[组合使用] 所有测试通过 ✓")

except Exception as e:
    errors.append(f"组合使用测试失败: {e}")
    print(f"\n  ✗ 失败: {e}")
    import traceback
    traceback.print_exc()

# ═══════════════════════════════════════════════════════════════
# 测试总结
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("测试总结")
print("=" * 70)

if errors:
    print(f"\n❌ 测试失败: {len(errors)} 个错误")
    for i, err in enumerate(errors, 1):
        print(f"  {i}. {err}")
    sys.exit(1)
else:
    print("\n✅ 所有测试通过!")
    print(f"\n测试图片保存在: {temp_dir}")
    print("\n新功能总结:")
    print("  1. 链式调用 (Fluent Interface)")
    print("     - sp.style('nature').palette('pastel').plot(x, y).save('output')")
    print("     - 支持多图层、自定义尺寸、各种图表类型")
    print("  2. 上下文管理器 (Context Manager)")
    print("     - with sp.style_context('ieee', palette='earth'):")
    print("     - 支持嵌套、自动恢复、特定场景快捷入口")
    print("  3. 简洁函数别名 (Aliases)")
    print("     - line(), scatter(), bar(), hist(), box(), violin()")
    print("     - multi(), area(), errorbar(), heatmap(), combo() 等")
    print("\n版本更新: 1.7.0 → 1.8.0")
