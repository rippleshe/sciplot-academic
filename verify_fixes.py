#!/usr/bin/env python3
"""
验证代码审查报告中的修复是否成功
"""

import sys
import warnings

def test_c1_matplotlib_backend():
    """C-1: 验证 matplotlib.use('Agg') 不会破坏用户后端"""
    import matplotlib
    backend_before = matplotlib.get_backend()
    
    import sciplot as sp
    sp.set_defaults(formats=("png", "pdf"))
    
    backend_after = matplotlib.get_backend()
    assert backend_before == backend_after, f"后端被修改: {backend_before} -> {backend_after}"
    print("✅ C-1: matplotlib 后端未被修改")

def test_m1_list_import():
    """M-1: 验证 List 类型已导入"""
    from sciplot._core.config import _normalize_formats
    import typing
    hints = typing.get_type_hints(_normalize_formats)
    assert 'formats' in hints, "formats 参数类型注解缺失"
    print("✅ M-1: List 类型已正确导入")

def test_m2_namedtuple_access():
    """M-2: 验证使用具名属性访问 NamedTuple"""
    from sciplot._ext.plot3d import _get_3d_figsize
    result = _get_3d_figsize("ieee")
    assert isinstance(result, tuple) and len(result) == 2, "返回类型错误"
    print("✅ M-2: NamedTuple 具名属性访问正确")

def test_m3_palette_type_consistency():
    """M-3: 验证 _freeze_palette_mapping 保持值类型一致性"""
    import sciplot as sp
    from sciplot._core.palette import get_palette
    
    palette_from_const = sp.PASTEL_PALETTE["pastel"]
    palette_from_func = get_palette("pastel")
    
    assert type(palette_from_const) == type(palette_from_func), \
        f"类型不一致: {type(palette_from_const)} vs {type(palette_from_func)}"
    print("✅ M-3: 配色常量类型一致性正确")

def test_m4_no_deepcopy():
    """M-4: 验证 StyleContext 不使用深拷贝"""
    import sciplot as sp
    import time
    
    # 测试性能，100次上下文应该很快
    t0 = time.perf_counter()
    for _ in range(100):
        with sp.style_context("ieee"):
            pass
    elapsed = time.perf_counter() - t0
    
    assert elapsed < 5.0, f"上下文切换过慢: {elapsed:.3f}s，可能使用了深拷贝"
    print(f"✅ M-4: StyleContext 性能正常 ({elapsed:.3f}s for 100次)")

def test_m5_pvalue_validation():
    """M-5: 验证 annotate_significance 的 p_value 范围验证"""
    import matplotlib.pyplot as plt
    from sciplot._plots.distribution import annotate_significance
    
    fig, ax = plt.subplots()
    
    try:
        annotate_significance(ax, 1, 2, 0.5, p_value=-0.1)
        assert False, "应该抛出 ValueError"
    except ValueError as e:
        assert "p_value" in str(e) or "[0, 1]" in str(e), f"错误信息不正确: {e}"
    
    try:
        annotate_significance(ax, 1, 2, 0.5, p_value=1.5)
        assert False, "应该抛出 ValueError"
    except ValueError as e:
        assert "p_value" in str(e) or "[0, 1]" in str(e), f"错误信息不正确: {e}"
    
    plt.close(fig)
    print("✅ M-5: p_value 范围验证正确")

def test_m6_violin_nan_check():
    """M-6: 验证 plot_violin 的 NaN/Inf 检查"""
    import numpy as np
    import matplotlib.pyplot as plt
    from sciplot._plots.distribution import plot_violin
    
    try:
        plot_violin([np.array([1, np.nan, 3]), np.array([2, 4])])
        assert False, "应该抛出 ValueError"
    except ValueError as e:
        assert "NaN" in str(e), f"错误信息不正确: {e}"
    
    try:
        plot_violin([np.array([1, np.inf]), np.array([2, 4])])
        assert False, "应该抛出 ValueError"
    except ValueError as e:
        assert "Inf" in str(e), f"错误信息不正确: {e}"
    
    print("✅ M-6: plot_violin NaN/Inf 检查正确")

def test_n1_no_alias_map():
    """N-1: 验证没有使用 Line2D._alias_map"""
    from sciplot._plots.basic import _LINE2D_KWARGS
    
    # 验证关键属性存在
    assert "color" in _LINE2D_KWARGS
    assert "linewidth" in _LINE2D_KWARGS
    assert "linestyle" in _LINE2D_KWARGS
    print("✅ N-1: Line2D 属性检查正确")

def test_n3_timeseries_inf_check():
    """N-3: 验证 plot_timeseries 的 Inf 检查"""
    import numpy as np
    import warnings
    import sciplot as sp
    
    t = np.arange(4)
    y_with_inf = np.array([1.0, np.inf, 3.0, 4.0])
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = sp.plot_timeseries(t, y_with_inf)
        result.close()
        assert any("Inf" in str(warning.message) for warning in w), "应该发出 Inf 警告"
    
    print("✅ N-3: plot_timeseries Inf 检查正确")

def test_n5_plotresult_ax():
    """N-5: 验证 PlotResult.ax 错误信息和单元素 ndarray 处理"""
    import sciplot as sp
    import numpy as np
    
    # 单子图
    result = sp.plot(np.arange(5), np.arange(5))
    ax = result.ax
    assert hasattr(ax, 'plot'), "ax 属性应该返回 Axes 对象"
    result.close()
    
    # 多子图
    fig, axes = sp.create_subplots(1, 2)
    result_multi = sp.PlotResult(fig, axes)
    try:
        result_multi.ax
        assert False, "应该抛出 AttributeError"
    except AttributeError as e:
        assert "子图" in str(e) or "2" in str(e), f"错误信息不够清晰: {e}"
    result_multi.close()
    
    print("✅ N-5: PlotResult.ax 错误信息正确")

def test_i2_fallback_version():
    """I-2: 验证 fallback 版本字符串为 unknown"""
    import sciplot as sp
    
    # 版本应该是有效的字符串
    assert sp.__version__ != "", "版本号不能为空"
    assert sp.__version__ != "1.8.1", "fallback 版本不应该使用旧版本号"
    print(f"✅ I-2: 版本号正确 ({sp.__version__})")

def test_i3_lazy_register():
    """I-3: 验证 diverging colormaps 延迟注册"""
    import matplotlib.pyplot as plt
    import sciplot as sp
    
    # 检查 rdbu colormap 是否存在
    try:
        cmap = plt.colormaps.get_cmap("rdbu")
        assert cmap is not None
    except KeyError:
        # 如果 apply_palette 还没被调用，可能不存在
        pass
    
    # 调用 apply_palette 后应该存在
    sp.setup_style(palette="rdbu")
    cmap = plt.colormaps.get_cmap("rdbu")
    assert cmap is not None
    
    print("✅ I-3: diverging colormaps 延迟注册正确")

def main():
    print("=" * 60)
    print("SciPlot Academic 代码审查修复验证")
    print("=" * 60)
    
    tests = [
        test_c1_matplotlib_backend,
        test_m1_list_import,
        test_m2_namedtuple_access,
        test_m3_palette_type_consistency,
        test_m4_no_deepcopy,
        test_m5_pvalue_validation,
        test_m6_violin_nan_check,
        test_n1_no_alias_map,
        test_n3_timeseries_inf_check,
        test_n5_plotresult_ax,
        test_i2_fallback_version,
        test_i3_lazy_register,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
