# 配色重构与规范修复 Spec

## Why

综合代码审阅发现的中低优先级问题需要修复，同时用户要求：移除人民币配色、移除 scienceplots 配色、新增用户提供的4组渐变配色作为内置配色系列。

## What Changes

- **移除** RMB_PALETTES 人民币配色系列
- **移除** 所有对 scienceplots 配色的引用
- **新增** 4组用户提供的渐变配色系列（pastel/ocean/forest/sunset），每组拆分为 -1 到 -N 子集
- **修复** 函数命名不一致问题（同类函数统一命名）
- **修复** 文档字符串缺失问题
- **修复** 参数默认值不一致问题

## Impact

- Affected specs: 配色管理、API 一致性
- Affected code: `_core/palette.py`（主要），`_plots/*.py`，`_ext/*.py`

## MODIFIED Requirements

### Requirement: 内置配色体系

**BREAKING** 移除 RMB 配色系列。内置配色仅保留用户提供的系列：

| 配色名 | 颜色（按顺序） | 颜色数量 |
|--------|---------------|---------|
| `pastel` | `#845EC2, #D65DB1, #FF6F91, #FF9671, #FFC75F, #F9F871` | 6 |
| `ocean` | `#5E98C2, #26B3D1, #00CCCB, #56E2B0, #A6F18C, #F9F871` | 6 |
| `forest` | `#5EC299, #00B3A2, #00A2AD, #0090B8, #007DBD, #0067B9` | 6 |
| `sunset` | `#D44132, #F45E4A, #FF7A62, #FF967C, #FFB296` | 5 |

每个配色系列自动注册子集（如 `pastel-1`, `pastel-2`, ..., `pastel-6`），命名规则与现有 `pastel-N` 一致。

### Requirement: 函数命名规范

同类函数使用统一命名约定：

| 类别 | 命名模式 | 示例 |
|------|---------|------|
| 绘图函数 | `plot_<type>` | `plot_line`, `plot_bar`, `plot_heatmap` |
| 样式设置 | `setup_<target>` | `setup_style`, `setup_palette` |
| 获取信息 | `get_<info>` | `get_palette`, `get_venue_info` |
| 列出项目 | `list_<items>` | `list_palettes`, `list_venues` |
| 验证输入 | `validate_<condition>` | `validate_array_like`, `validate_choice` |
| 应用样式 | `apply_<target>` | `apply_palette`, `apply_resolved_style` |

### Requirement: 参数默认值一致性

| 参数 | 统一默认值 |
|------|-----------|
| `alpha`（散点/填充） | `0.7`（散点）、`0.3`（填充） |
| `venue` | `None`（从配置获取） |
| `palette` | `None`（从配置获取） |
| `xlabel`/`ylabel`/`title` | `""`（空字符串） |

## REMOVED Requirements

### Requirement: RMB 配色系列

**Reason**: 用户要求移除，配色来源不明确且不实用。

### Requirement: scienceplots 配色

**Reason**: 依赖第三方库，且配色风格与 SciPlot 学术定位不符。

### Requirement: 发散型/序列型/主题配色

**Reason**: 这些配色系使用场景有限，用户未提供替代方案，暂时移除。后续可通过 `set_custom_palette` 和 `register_color_scheme` 扩展。
