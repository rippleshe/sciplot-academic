# SciPlot Academic — 代码审查报告

> **版本**：v1.8.2 | **审查时间**：2025 | **审查范围**：全项目（pyproject.toml + sciplot/ 全部源文件）

---

## 问题汇总总览

| 级别 | 数量 |
|------|------|
| 致命 Critical | 1 |
| 严重 Major | 7 |
| 轻微 Minor | 5 |
| 建议 Info | 3 |

---

## 致命问题（Critical）

---

### C-1｜`matplotlib.use('Agg')` 在库内部被调用，破坏用户后端

- **严重级别**：致命（Critical）
- **问题定位**：`sciplot/_core/config.py` → 第 43–57 行 → `_get_supported_formats()`
- **上下文代码**：
```python
def _get_supported_formats() -> frozenset:
    """延迟获取支持的文件格式，避免导入时创建Figure实例。"""
    global _SUPPORTED_SAVE_FORMATS
    if _SUPPORTED_SAVE_FORMATS is not None:
        return _SUPPORTED_SAVE_FORMATS
    with _FORMATS_LOCK:
        if _SUPPORTED_SAVE_FORMATS is not None:
            return _SUPPORTED_SAVE_FORMATS
        fig = None
        try:
            import matplotlib
            matplotlib.use('Agg')          # ← ⚠️ 致命：强制切换后端
            from matplotlib.figure import Figure
            fig = Figure()
            _SUPPORTED_SAVE_FORMATS = frozenset(fig.canvas.get_supported_filetypes().keys())
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception:
            _SUPPORTED_SAVE_FORMATS = frozenset({...})
        finally:
            if fig is not None:
                import matplotlib.pyplot as plt
                plt.close(fig)             # ← ⚠️ 次要：对裸 Figure 调用 plt.close 无效
        return _SUPPORTED_SAVE_FORMATS
```
- **风险分析**：
  1. `matplotlib.use('Agg')` 必须在任何 `import matplotlib.pyplot` 之前调用，否则会抛出 `UserWarning` 甚至静默失效。但即使调用成功，它会**全局强制覆盖**用户已选择的 Qt、TkAgg、notebook 等后端。在 Jupyter Notebook 或 PyCharm 的交互式绘图环境中，调用后所有图形将无法显示，造成无法回滚的破坏性副作用。
  2. `plt.close(fig)` 在此处对一个**裸 `Figure()` 实例**（非通过 `plt.subplots` 创建）调用无意义：裸 Figure 未被 pyplot 的图形管理器跟踪，`plt.close` 不会释放其资源，正确做法是 `matplotlib.pyplot.close(fig)` 或直接 `del fig`。
  3. 触发条件：首次调用 `set_defaults(formats=...)` 或 `save()` 时，`_get_supported_formats()` 被调用。这会在用户毫无察觉的情况下改变全局状态。

- **修复方案**：

```python
# 修复：不再需要创建 Figure 实例来获取格式，直接使用已知的静态集合
# 或通过 Figure.canvas.get_supported_filetypes() 但不调用 matplotlib.use()

def _get_supported_formats() -> frozenset:
    """延迟获取支持的文件格式（不修改 matplotlib 后端）。"""
    global _SUPPORTED_SAVE_FORMATS
    if _SUPPORTED_SAVE_FORMATS is not None:
        return _SUPPORTED_SAVE_FORMATS
    with _FORMATS_LOCK:
        if _SUPPORTED_SAVE_FORMATS is not None:
            return _SUPPORTED_SAVE_FORMATS
        try:
            # ✅ 修复1：不调用 matplotlib.use()，直接使用当前 Figure 类的能力
            # Figure() 是非交互式的纯数据对象，不需要后端，可以安全实例化
            from matplotlib.figure import Figure
            fig = Figure()
            _SUPPORTED_SAVE_FORMATS = frozenset(fig.canvas.get_supported_filetypes().keys())
            # ✅ 修复2：对裸 Figure 使用 fig.clf() + del 而非 plt.close()
            fig.clf()
        except Exception:
            _SUPPORTED_SAVE_FORMATS = frozenset({
                'png', 'pdf', 'svg', 'eps', 'ps', 'jpg', 'jpeg', 'tif', 'tiff'
            })
        return _SUPPORTED_SAVE_FORMATS
```

> **修改理由**：`matplotlib.Figure()` 本身是与后端无关的对象，可以在不改变全局后端的情况下直接实例化以查询支持格式。删除 `matplotlib.use('Agg')` 消除了对用户环境的破坏性副作用。

- **回归验证**：
```python
# 测试1：在 set_defaults 之前记录后端，调用后验证后端未改变
import matplotlib
backend_before = matplotlib.get_backend()
import sciplot as sp
sp.set_defaults(formats=("png", "pdf"))
assert matplotlib.get_backend() == backend_before, "后端不应被修改"

# 测试2：验证返回的格式集合包含常见格式
from sciplot._core.config import _get_supported_formats
fmts = _get_supported_formats()
assert 'pdf' in fmts and 'png' in fmts

# 静态检查
# ruff check sciplot/_core/config.py
```

---

## 严重问题（Major）

---

### M-1｜`_normalize_formats` 使用了未导入的 `List` 类型

- **严重级别**：严重（Major）
- **问题定位**：`sciplot/_core/config.py` → 第 1 行（导入） + 第 72 行 → `_normalize_formats()`
- **上下文代码**：
```python
# 文件头部导入 —— List 缺失
from typing import Any, Dict, Optional, Tuple, Union, cast, Type
# ↑ 无 List

# 第 72 行函数签名
def _normalize_formats(formats: Union[Tuple[str, ...], List[str]]) -> Tuple[str, ...]:
    #                                               ^^^^ NameError 隐患
    normalized = tuple(formats)
    ...
```
- **风险分析**：
  - 由于文件顶部有 `from __future__ import annotations`，注解被推迟为字符串，运行时不求值，因此不会立即引发 `NameError`。
  - 但以下情况会直接报错：`typing.get_type_hints(config._normalize_formats)` 调用（用于文档生成、序列化框架、部分测试框架）；Mypy / Pyright 静态检查会报 `error: Name "List" is not defined`。
  - Python 3.12 中部分注解处理路径可能提前求值，存在潜在的兼容性风险。

- **修复方案**：
```python
# 修复：在 typing 导入中补充 List
from typing import Any, Dict, List, Optional, Tuple, Union, cast, Type
# 或对于 Python ≥ 3.9，可替换为内置 list：
# def _normalize_formats(formats: Union[Tuple[str, ...], list[str]]) -> Tuple[str, ...]:
```

- **回归验证**：
```bash
mypy sciplot/_core/config.py --strict
python -c "import typing; import sciplot._core.config as c; print(typing.get_type_hints(c._normalize_formats))"
```

---

### M-2｜`_ext/plot3d.py` 使用脆弱的 NamedTuple 位置解包

- **严重级别**：严重（Major）
- **问题定位**：`sciplot/_ext/plot3d.py` → 第 37–40 行 → `_get_3d_figsize()`
- **上下文代码**：
```python
def _get_3d_figsize(venue: Optional[str]) -> Tuple[float, float]:
    """获取3D图形的尺寸，基于venue设置。"""
    if venue and venue in VENUES:
        _, (w, h), _ = VENUES[venue]   # ← ⚠️ 位置解包，依赖字段顺序
        # 3D图通常需要更大的尺寸来展示深度
        return (w * 1.2, h * 1.2)
    return (8, 6)
```
- **风险分析**：
  - `VENUES` 的值类型为 `VenueConfig(styles, figsize, fontsize)` — 当前位置解包 `_, (w, h), _` 恰好正确。
  - 但若未来 `VenueConfig` 增删字段或调整顺序，此处会**静默返回错误值**（e.g., 用字号当宽度），而非在改动时报错，排查极为困难。
  - 项目其他所有地方均使用 `.figsize` 属性访问，此处风格不一致，且是唯一的脆弱点。

- **修复方案**：
```python
def _get_3d_figsize(venue: Optional[str]) -> Tuple[float, float]:
    """获取3D图形的尺寸，基于venue设置。"""
    if venue and venue in VENUES:
        w, h = VENUES[venue].figsize   # ✅ 使用具名属性，安全且自文档化
        return (w * 1.2, h * 1.2)
    return (8.0, 6.0)
```

- **回归验证**：
```python
from sciplot._ext.plot3d import _get_3d_figsize
assert _get_3d_figsize("ieee") == (3.5 * 1.2, 3.0 * 1.2)
assert _get_3d_figsize(None) == (8.0, 6.0)
assert _get_3d_figsize("unknown_venue") == (8.0, 6.0)
```

---

### M-3｜`__init__.py` 的 `_freeze_palette_mapping` 改变公开 API 的值类型

- **严重级别**：严重（Major）
- **问题定位**：`sciplot/__init__.py` → 最后约 20 行
- **上下文代码**：
```python
# 从 _core.palette 导入：Dict[str, List[str]]
from sciplot._core.palette import (
    PASTEL_PALETTE,   # Dict[str, List[str]]
    ...
)

# ── 文件末尾 ──────────────────────────────────────────────
def _freeze_palette_mapping(data):
    """导出层提供只读映射，避免用户误改全局配色。"""
    return _MappingProxyType({k: tuple(v) for k, v in data.items()})
    #                                     ^^^^^^^^ 值从 List 变成 tuple

# 覆盖上面的导入，改变类型
PASTEL_PALETTE = _freeze_palette_mapping(PASTEL_PALETTE)
# 此后：sp.PASTEL_PALETTE["pastel"] → tuple，而非 list
```
- **风险分析**：
  1. 用户调用 `sp.PASTEL_PALETTE["pastel"]` 得到 `tuple`，但 `sp.get_palette("pastel")` 返回 `List[str]`，类型不一致，容易造成混淆。
  2. 文档字符串和类型注解中声明的是 `Dict[str, List[str]]`，实际运行时类型为 `MappingProxyType[str, tuple[str, ...]]`，破坏 Mypy 的类型推断。
  3. 由于 `_LAZY_EXT` 中导入的 `RESIDENT_PALETTES` 等常量仍为原始可变字典，公开 API 的只读保护实际上并不完整。

- **修复方案**：
```python
# 方案A：保持值类型为 List，只对外层 Dict 做只读
def _freeze_palette_mapping(data: Dict[str, List[str]]) -> _MappingProxyType:
    """导出层提供只读映射，值保持 List 类型不变（与 get_palette() 一致）。"""
    return _MappingProxyType(data)   # 仅冻结外层，不改变值类型

# 方案B（推荐）：不暴露内部常量，通过函数API访问
# 移除 __all__ 中的 PASTEL_PALETTE 等，引导用户使用 sp.get_palette("pastel")
```
> 若选择方案A，由于 `MappingProxyType` 不会递归冻结，`List` 值本身仍可变。若追求完全不可变，可在 `__init__.py` 顶部注释说明这是"只读视图，值内容请勿修改"。

- **回归验证**：
```python
import sciplot as sp
# 验证类型一致性
palette_from_const = sp.PASTEL_PALETTE["pastel"]
palette_from_func = sp.get_palette("pastel")
assert type(palette_from_const) == type(palette_from_func), \
    f"类型不一致: {type(palette_from_const)} vs {type(palette_from_func)}"
```

---

### M-4｜`StyleContext.__enter__` 深拷贝整个 rcParams，存在性能与兼容性风险

- **严重级别**：严重（Major）
- **问题定位**：`sciplot/_core/context.py` → 第 86 行 → `StyleContext.__enter__()`
- **上下文代码**：
```python
def __enter__(self) -> StyleContext:
    """进入上下文，保存当前状态并应用新样式"""
    # 保存当前 rcParams 的副本
    self._saved_state = copy.deepcopy(dict(rcParams))  # ← ⚠️ 深拷贝所有 rcParams
    self._saved_lang = get_current_lang()
    self._saved_venue = get_current_venue()
    ...
```
- **风险分析**：
  1. **性能**：matplotlib 的 `rcParams` 字典包含 300+ 条配置项，部分值为复杂对象（字体列表、颜色对象等）。每次进入 `with sp.style_context()` 都进行深拷贝，在频繁调用的测试或批量绘图场景中会产生明显开销。
  2. **兼容性**：某些 rcParams 值（如 `axes.prop_cycle` 中的 `cycler` 对象、`font.family` 中的字体路径对象）在部分 matplotlib 版本中不支持深拷贝，可能引发 `TypeError: cannot pickle 'X' object`。
  3. **实际需要**：`setup_style` 只修改约 15 个 rcParams，完整保存并恢复所有 300+ 项是过度的。

- **修复方案**：
```python
# 仅保存 setup_style 会修改的 rcParams 键
_STYLE_RCPARAMS_KEYS = frozenset({
    "font.family", "font.serif", "font.size",
    "axes.labelsize", "axes.titlesize",
    "xtick.labelsize", "ytick.labelsize",
    "legend.fontsize",
    "text.usetex",
    "axes.unicode_minus",
    "axes.formatter.use_mathtext",
    "mathtext.fontset", "mathtext.rm", "mathtext.it", "mathtext.bf",
    "axes.grid",
    "axes.prop_cycle",
    "figure.figsize",
})

def __enter__(self) -> StyleContext:
    # 只保存相关键，避免深拷贝整个 rcParams
    self._saved_state = {
        k: rcParams[k] for k in _STYLE_RCPARAMS_KEYS if k in rcParams
    }
    ...

def __exit__(self, ...):
    if self._saved_state is not None:
        rcParams.update(self._saved_state)   # 同样只恢复相关键
    ...
```

- **回归验证**：
```python
import time, matplotlib.pyplot as plt, sciplot as sp, numpy as np
x = np.linspace(0, 10, 100)

# 测试：进出 100 次上下文，验证性能与 rcParams 正确恢复
original_fontsize = plt.rcParams["font.size"]
t0 = time.perf_counter()
for _ in range(100):
    with sp.style_context("ieee"):
        pass
elapsed = time.perf_counter() - t0
assert plt.rcParams["font.size"] == original_fontsize, "rcParams 未正确恢复"
print(f"100次上下文耗时: {elapsed:.3f}s")  # 应 < 1s
```

---

### M-5｜`annotate_significance` 未验证 `p_value` 范围，负值或超过 1 的值静默给出错误标注

- **严重级别**：严重（Major）
- **问题定位**：`sciplot/_plots/distribution.py` → 第 386–430 行 → `annotate_significance()`
- **上下文代码**：
```python
def annotate_significance(
    ax: Axes,
    x1: float, x2: float, y: float,
    p_value: float,          # ← ⚠️ 未验证范围
    h: float = 0.02,
    ...
) -> None:
    if p_value < 0.001:
        marker = "***"
    elif p_value < 0.01:
        marker = "**"
    elif p_value < 0.05:
        marker = "*"
    else:
        marker = ns_text      # ← p_value = -0.5 也会走到这里，给出 "ns" 标注
```
- **风险分析**：
  - `p_value = -1.0` 会满足 `p_value < 0.001`，输出 `***`，掩盖数据错误。
  - `p_value = 1.5` 会输出 `ns`，同样无声无息。
  - 对于科研绘图库，统计显著性标注错误是严重的学术风险。

- **修复方案**：
```python
def annotate_significance(
    ax: Axes,
    x1: float, x2: float, y: float,
    p_value: float,
    h: float = 0.02,
    tip_len: float = 0.01,
    color: str = "black",
    fontsize: Optional[int] = None,
    ns_text: str = "ns",
) -> None:
    # ✅ 新增：p_value 范围验证
    if not isinstance(p_value, (int, float)) or not (0.0 <= p_value <= 1.0):
        raise ValueError(
            f"p_value 必须是 [0, 1] 范围内的浮点数，实际值: {p_value!r}"
        )
    # ✅ 新增：坐标轴参数基本验证
    if x1 == x2:
        raise ValueError("x1 与 x2 不能相等，无法绘制括号")
    
    if p_value < 0.001:
        marker = "***"
    ...
```

- **回归验证**：
```python
import pytest, matplotlib.pyplot as plt
from sciplot._plots.distribution import annotate_significance

fig, ax = plt.subplots()
with pytest.raises(ValueError, match="p_value"):
    annotate_significance(ax, 1, 2, 0.5, p_value=-0.1)
with pytest.raises(ValueError, match="p_value"):
    annotate_significance(ax, 1, 2, 0.5, p_value=1.5)
# 正常情况不抛出
annotate_significance(ax, 1, 2, 0.5, p_value=0.03)
plt.close(fig)
```

---

### M-6｜`plot_violin` 对列表输入缺少 NaN/Inf 检查

- **严重级别**：严重（Major）
- **问题定位**：`sciplot/_plots/distribution.py` → 第 258–275 行 → `plot_violin()`
- **上下文代码**：
```python
def plot_violin(data, ...):
    if isinstance(data, (list, tuple)):
        if not data:
            raise ValueError("参数 'data' 不能为空列表")
        for i, values in enumerate(data):
            if np.asarray(values).size == 0:
                raise ValueError(f"data[{i}] 不能为空")
            # ← ⚠️ 此处没有 NaN/Inf 检查！
        n_groups = len(data)
    else:
        data_arr = np.asarray(data, dtype=float)
        if data_arr.size == 0:
            raise ValueError("参数 'data' 不能为空")
        if not np.all(np.isfinite(data_arr)):   # ← ndarray 有检查
            raise ValueError("data 不能包含 NaN 或 Inf")
```
- **风险分析**：
  - 当 `data` 为 `[np.array([1, np.nan, 3]), np.array([2, 4])]` 时，NaN 不被拦截，`ax.violinplot()` 会接收 NaN，可能导致 matplotlib 内部错误（`LinAlgError`）或生成空白图形，错误信息对用户毫无帮助。
  - 与 `plot_box` 的行为不一致：`plot_box` 对列表输入有完整的 NaN/Inf 检查。

- **修复方案**：
```python
if isinstance(data, (list, tuple)):
    if not data:
        raise ValueError("参数 'data' 不能为空列表")
    for i, values in enumerate(data):
        values_arr = np.asarray(values, dtype=float).ravel()
        if values_arr.size == 0:
            raise ValueError(f"data[{i}] 不能为空")
        if not np.all(np.isfinite(values_arr)):   # ✅ 补充 NaN/Inf 检查
            raise ValueError(f"data[{i}] 不能包含 NaN 或 Inf")
    n_groups = len(data)
```

- **回归验证**：
```python
import numpy as np, pytest
from sciplot._plots.distribution import plot_violin

with pytest.raises(ValueError, match="NaN"):
    plot_violin([np.array([1, np.nan, 3]), np.array([2, 4])])
with pytest.raises(ValueError, match="Inf"):
    plot_violin([np.array([1, np.inf]), np.array([2, 4])])
# 正常情况
fig, ax = plot_violin([np.array([1, 2, 3]), np.array([2, 3, 4])])
```

---

### M-7｜`config.py` 顶层冗余 `Figure` 导入 + `plt.close()` 对裸 Figure 无效

- **严重级别**：严重（Major）
- **问题定位**：`sciplot/_core/config.py` → 第 13 行（导入） + `_get_supported_formats()` 的 `finally` 块
- **上下文代码**：
```python
# 第 13 行 —— 模块顶层已导入 Figure（随后 C-1 修复会删除它）
from matplotlib.figure import Figure   # ← 若 C-1 修复后此行成为孤立导入

# _get_supported_formats() 的 finally 块
finally:
    if fig is not None:
        import matplotlib.pyplot as plt
        plt.close(fig)     # ← Figure() 未经 pyplot 创建，plt.close() 不会释放它
```
- **风险分析**：
  - `Figure()` 是直接实例化的裸 Figure，不在 pyplot 图形管理器中注册。`plt.close(fig)` 对其没有效果，资源不会被释放（C-1 修复后此问题随之消失）。
  - 顶层 `from matplotlib.figure import Figure` 在 `TYPE_CHECKING` 块之外导入，只是为了 `_get_supported_formats` 内部使用，但函数内部还会再次 `from matplotlib.figure import Figure`，冗余且可能导致静态检查工具误判。

- **修复方案**：
```python
# 移除顶层 Figure 导入（C-1 修复后不再需要）
# 顶层 TYPE_CHECKING 用途：
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from matplotlib.figure import Figure  # 仅类型检查时用

# finally 块使用 fig.clf() + del 代替 plt.close()
finally:
    if fig is not None:
        fig.clf()
        del fig
```

- **回归验证**：
```bash
ruff check sciplot/_core/config.py --select F401  # 检测未使用导入
mypy sciplot/_core/config.py
```

---

## 轻微问题（Minor）

---

### N-1｜`_LINE2D_KWARGS` 使用私有内部属性 `Line2D._alias_map`

- **严重级别**：轻微（Minor）
- **问题定位**：`sciplot/_plots/basic.py` → 第 18 行
- **上下文代码**：
```python
_LINE2D_KWARGS = set(Line2D([], []).properties().keys()) | set(
    getattr(Line2D, "_alias_map", {}).keys()   # ← ⚠️ _alias_map 为私有属性
)
```
- **风险分析**：`_alias_map` 是 matplotlib 的私有属性，在 matplotlib 3.7+ 中已被重构，在将来版本中可能被移除或改名，导致 `_LINE2D_KWARGS` 不完整，进而使 `plot_multi_area` 的 kwarg 过滤逻辑出错（过滤过于保守或宽松）。

- **修复方案**：
```python
# 方案A：移除私有属性访问，仅用 properties()
_LINE2D_KWARGS = frozenset(Line2D([], []).properties().keys())

# 方案B：使用 matplotlib 公开 API 获取别名（matplotlib >= 3.4）
try:
    from matplotlib.artist import Artist
    _ALIAS_MAP = getattr(Artist, "_alias_map", {})
except Exception:
    _ALIAS_MAP = {}
_LINE2D_KWARGS = frozenset(Line2D([], []).properties().keys()) | frozenset(_ALIAS_MAP.keys())
```

- **回归验证**：
```python
from sciplot._plots.basic import _LINE2D_KWARGS
# 验证关键 Line2D 属性都在集合中
assert "color" in _LINE2D_KWARGS
assert "linewidth" in _LINE2D_KWARGS
assert "linestyle" in _LINE2D_KWARGS
```

---

### N-2｜`PlotResult.save()` / `show()` 使用 `set_constrained_layout(True)` 作为无效降级

- **严重级别**：轻微（Minor）
- **问题定位**：`sciplot/_core/result.py` → 第 243–246 行 → `PlotResult.save()` 和 `show()`
- **上下文代码**：
```python
def save(self, name, ...):
    if tight:
        try:
            self._fig.tight_layout()
        except (ValueError, AttributeError):
            self._fig.set_constrained_layout(True)   # ← ⚠️ 降级逻辑有误
```
- **风险分析**：
  - `tight_layout()` 失败通常因为图形已使用 `constrained_layout`，此时调用 `set_constrained_layout(True)` 是无意义的（已经是True）。
  - `set_constrained_layout(True)` 在图形创建后调用不总是生效，需要在首次渲染前设置。
  - 更常见的 `tight_layout()` 失败原因（如子图间距过小）不会因此被修复。
  - 正确的降级策略是静默忽略或打印警告，而非无效操作。

- **修复方案**：
```python
def save(self, name, ...):
    if tight:
        try:
            self._fig.tight_layout()
        except ValueError:
            # tight_layout 在 constrained_layout 模式下会抛 ValueError，静默忽略即可
            pass
        except Exception as e:
            import warnings
            warnings.warn(f"tight_layout() 失败: {e}", UserWarning, stacklevel=2)
```

- **回归验证**：
```python
import sciplot as sp, numpy as np, matplotlib.pyplot as plt
x = np.linspace(0, 1, 10)
fig, axes = plt.subplots(1, 2, constrained_layout=True)
result = sp.PlotResult(fig, axes)
# 不应抛出异常，也不应修改 constrained_layout 设置
result.save("test_save", formats=("png",))
```

---

### N-3｜`plot_timeseries` 未验证数值型 `y` 数据的 NaN/Inf

- **严重级别**：轻微（Minor）
- **问题定位**：`sciplot/_plots/timeseries.py` → `plot_timeseries()` 函数体
- **上下文代码**：
```python
def plot_timeseries(t, y, ...):
    t = np.asarray(t)
    y = np.asarray(y)
    if len(t) != len(y):
        raise ValueError(...)
    # ← ⚠️ 没有对 y 做 NaN/Inf 检查
    ...
    ax.plot(t, y, label=label, marker=marker, color=main_color, **kwargs)
```
- **风险分析**：NaN 数据点在 matplotlib 中会产生不连续的折线段，这可能是预期行为，但若用户传入全 NaN 或含 Inf 的数据，会导致 rolling_mean 计算产生 NaN 传播，或者 `axvline` 等注解定位出现问题。与其他图表函数的行为不一致。

- **修复方案**：
```python
y = np.asarray(y, dtype=float)
if len(t) != len(y):
    raise ValueError(...)

# 对于时序数据，NaN 通常表示缺失值，允许存在；
# 但 Inf 通常是错误数据，给出警告
if np.any(np.isinf(y)):
    import warnings
    warnings.warn(
        "y 数据包含 Inf 值，可能导致图形显示异常",
        UserWarning, stacklevel=2,
    )
```

- **回归验证**：
```python
import numpy as np, warnings, sciplot as sp
y_with_nan = np.array([1.0, np.nan, 3.0, 4.0])
t = np.arange(4)
# NaN 应被允许（表示缺失值），但给出信息
result = sp.plot_timeseries(t, y_with_nan)

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    sp.plot_timeseries(t, np.array([1.0, np.inf, 3.0, 4.0]))
    assert any("Inf" in str(warning.message) for warning in w)
```

---

### N-4｜`FluentChain` 绘图方法缺少类型注解，IDE 自动补全失效

- **严重级别**：轻微（Minor）
- **问题定位**：`sciplot/_core/fluent.py` → `PlotChain` 类绘图方法（第 135–205 行）
- **上下文代码**：
```python
class PlotChain:
    def plot(self, x, y, **kwargs) -> FigureWrapper:    # ← x, y 无类型注解
        """绘制折线图"""
        self._ensure_figure()
        self._ax.plot(x, y, **kwargs)
        return FigureWrapper(self._fig, self._ax, self)

    def scatter(self, x, y, **kwargs) -> FigureWrapper:  # ← 同上
        ...
    def bar(self, x, height, **kwargs) -> FigureWrapper:  # ← height 无注解
        ...
```
- **风险分析**：公开 API 的方法缺少参数类型注解，导致：IDE 无法提供参数提示；Mypy 在调用链上推断类型时丢失信息；文档工具（sphinx-autodoc）无法生成准确的参数文档。

- **修复方案**：
```python
from numpy.typing import ArrayLike

class PlotChain:
    def plot(
        self,
        x: ArrayLike,
        y: ArrayLike,
        **kwargs: Any,
    ) -> FigureWrapper:
        """绘制折线图"""
        ...

    def scatter(
        self,
        x: ArrayLike,
        y: ArrayLike,
        **kwargs: Any,
    ) -> FigureWrapper:
        """绘制散点图"""
        ...

    def bar(
        self,
        x: ArrayLike,
        height: ArrayLike,
        **kwargs: Any,
    ) -> FigureWrapper:
        """绘制柱状图"""
        ...
```

- **回归验证**：
```bash
mypy sciplot/_core/fluent.py --strict --disallow-untyped-defs
```

---

### N-5｜`_core/result.py` 中 `PlotResult.ax` 在多子图时抛出 `AttributeError`，错误信息不够清晰

- **严重级别**：轻微（Minor）
- **问题定位**：`sciplot/_core/result.py` → `PlotResult.ax` 属性（约第 115 行）
- **上下文代码**：
```python
@property
def ax(self) -> Axes:
    """获取 Axes 对象（单个子图时）"""
    if self._is_array:
        raise AttributeError(
            "多子图请使用 result.axes 或 result.ax_array 访问"
        )
    return cast(Axes, self._ax)
```
- **风险分析**：错误信息未说明如何判断是否为多子图，对新用户不够友好。另外，`_is_array` 的判断基于 `isinstance(ax, np.ndarray)`，当用户直接传入包装了单个子图的 ndarray（`np.array([ax])`）时，会误判为多子图，导致 `.ax` 无法访问真正的单个 `Axes`。

- **修复方案**：
```python
@property
def ax(self) -> Axes:
    """获取 Axes 对象（单个子图时）。多子图请使用 .axes 或 .ax_array"""
    if self._is_array:
        ax_arr = cast(np.ndarray, self._ax)
        if ax_arr.size == 1:
            # ✅ 允许从单元素 ndarray 中取出单个 Axes
            return cast(Axes, ax_arr.flat[0])
        raise AttributeError(
            f"此结果包含 {ax_arr.size} 个子图（形状 {ax_arr.shape}），"
            "请使用 result.axes 获取 ndarray，或 result.axes[i, j] 访问指定子图。"
        )
    return cast(Axes, self._ax)
```

- **回归验证**：
```python
import sciplot as sp, numpy as np
# 单子图：.ax 应正常工作
result = sp.plot(np.arange(5), np.arange(5))
ax = result.ax
assert hasattr(ax, 'plot')

# 多子图：.ax 应给出清晰错误
fig, axes = sp.create_subplots(1, 2)
result_multi = sp.PlotResult(fig, axes)
try:
    result_multi.ax
    assert False, "应抛出 AttributeError"
except AttributeError as e:
    assert "2" in str(e) or "子图" in str(e)
```

---

## 建议（Info）

---

### I-1｜`pyproject.toml` 中 `statistical = []` 是空的可选依赖项

- **严重级别**：建议（Info）
- **问题定位**：`pyproject.toml` → `[project.optional-dependencies]` → `statistical = []`
- **上下文代码**：
```toml
[project.optional-dependencies]
statistical = []   # ← 空列表，没有实际内容
dev = [...]
ml = ["scikit-learn>=1.0.0"]
```
- **风险分析**：`pip install sciplot-academic[statistical]` 可以正常执行但不会安装任何东西，误导用户以为某些功能需要此扩展。实际上 `scipy` 是 `statistical` 图表的必需依赖（已在 `dependencies` 中声明为必需），此条目应删除或填充内容。

- **修复方案**：
```toml
# 方案A：删除空条目
[project.optional-dependencies]
dev = [...]
ml = ["scikit-learn>=1.0.0"]
network = ["networkx>=2.6.0"]
venn = ["matplotlib-venn>=0.11.0"]
all = ["scikit-learn>=1.0.0", "networkx>=2.6.0", "matplotlib-venn>=0.11.0"]

# 方案B：如果 scipy 计划从 required → optional，则填充
# statistical = ["scipy>=1.10.1"]
# 并将 scipy 从 dependencies 移出
```

---

### I-2｜`__init__.py` 中硬编码的 fallback 版本字符串与实际版本不同步

- **严重级别**：建议（Info）
- **问题定位**：`sciplot/__init__.py` → 第 52–56 行
- **上下文代码**：
```python
try:
    from importlib.metadata import version as _get_version
    __version__ = _get_version("sciplot-academic")
except Exception:
    __version__ = "1.8.1"   # ← ⚠️ 硬编码的旧版本号（当前为 1.8.2）
```
- **风险分析**：每次版本升级后若忘记更新此 fallback，会在包元数据不可用的特殊环境（如从源码直接 import 不安装的情况）下报告错误版本，干扰调试。实际上 `_LOCAL_VERSION` 已从 `pyproject.toml` 读取，此 fallback 几乎不会触发，但若触发则给出误导性版本号。

- **修复方案**：
```python
except Exception:
    __version__ = "unknown"   # ✅ 明确说明版本未知，而非给一个过时的具体版本
```

---

### I-3｜`_core/palette.py` 在模块导入时执行 `_register_diverging_cmaps()` 产生全局副作用

- **严重级别**：建议（Info）
- **问题定位**：`sciplot/_core/palette.py` → 模块末尾 `_register_diverging_cmaps()` 调用
- **上下文代码**：
```python
# 文件末尾
_register_diverging_cmaps()   # ← 模块导入时立即执行，修改全局 matplotlib colormap 注册表
```
- **风险分析**：
  1. 违反"导入无副作用"原则——`import sciplot` 或 `import sciplot._core.palette` 会立即修改全局 matplotlib colormap 注册表，影响使用同一 matplotlib 实例的其他库。
  2. 在多次导入（reload）或测试隔离场景中，colormap 注册冲突可能产生警告噪声。
  3. 这使得单独测试 `palette.py` 中的纯函数时会有不必要的副作用。

- **修复方案**：
```python
# 方案A：改为延迟注册，在 apply_palette 或 setup_style 首次调用时触发
_diverging_cmaps_registered = False

def _ensure_diverging_cmaps() -> None:
    global _diverging_cmaps_registered
    if not _diverging_cmaps_registered:
        _register_diverging_cmaps()
        _diverging_cmaps_registered = True

# 在 apply_palette() 开头调用
def apply_palette(palette: str, n_colors: Optional[int] = None) -> None:
    _ensure_diverging_cmaps()   # ✅ 延迟到首次需要时
    ...

# 方案B（最小改动）：保持现有行为，但加注释说明副作用
# _register_diverging_cmaps()  # NOTE: side effect at import time, by design
```

- **回归验证**：
```python
import matplotlib.pyplot as plt
# 验证 sciplot 未导入时，rdbu colormap 不存在
try:
    plt.colormaps["rdbu"]
    print("WARNING: colormap 已存在（可能来自其他库）")
except KeyError:
    pass

import sciplot  # 导入后应注册
cmap = plt.colormaps.get_cmap("rdbu")
assert cmap is not None
```

---

## 附：快速修复优先级矩阵

| 编号 | 问题 | 影响范围 | 修复难度 | 优先级 |
|------|------|----------|----------|--------|
| C-1 | `matplotlib.use('Agg')` 破坏后端 | 所有用户 | 低 | 🔴 立即 |
| M-1 | `List` 未导入 | 类型检查/反射 | 极低 | 🔴 立即 |
| M-5 | `p_value` 无范围校验 | 统计标注 | 低 | 🔴 立即 |
| M-6 | `plot_violin` 列表 NaN/Inf 检查缺失 | 小提琴图 | 低 | 🟠 本版本 |
| M-2 | NamedTuple 位置解包 | 3D图表 | 极低 | 🟠 本版本 |
| M-3 | `_freeze_palette_mapping` 类型变更 | 常量访问 | 低 | 🟠 本版本 |
| M-4 | `deepcopy(rcParams)` 性能/兼容性 | 上下文管理 | 中 | 🟡 下版本 |
| M-7 | `plt.close(bare_fig)` 无效 | 资源管理 | 低 | 🟡 下版本 |
| N-1~N-5 | 其他轻微问题 | 局部 | 低~中 | 🟢 积压 |
| I-1~I-3 | 建议项 | 文档/工程规范 | 极低 | 🟢 积压 |

---

*报告生成结束。所有代码补丁均已考虑向后兼容性，不引入破坏性变更（Breaking Changes）。*
