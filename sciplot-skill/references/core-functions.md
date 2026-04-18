# 核心函数

## setup_style — 样式设置

```python
sp.setup_style(venue="nature", palette="pastel", lang="zh")
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `venue` | `"nature"` | 期刊/场合预设 |
| `palette` | `"pastel"` | 配色方案 |
| `lang` | `"zh"` | `"zh"`/`"zh-cn"` 中文，`"en"` 英文 |

### 示例

```python
sp.setup_style()                       # 默认：nature + pastel + 中文
sp.setup_style(lang="en")              # 英文模式
sp.setup_style("ieee", "pastel-2")     # IEEE + 前2色
sp.setup_style("thesis", "forest-3")   # 学位论文 + 森林色
```

### 语言与 LaTeX 渲染

- **`lang="zh"`（中文模式）**：自动**禁用 LaTeX**，确保中文正常渲染，负号使用 ASCII 减号（避免 U+2212 警告）
- **`lang="en"`（英文模式）**：自动**启用 LaTeX**（如果系统已安装），数学公式渲染更美观

```python
# 中文论文 - 禁用 LaTeX，中文显示正常
sp.setup_style("thesis", "pastel", lang="zh")
fig, ax = sp.plot(x, y, xlabel="时间 (s)", ylabel="电压 (V)")

# 英文论文 - 启用 LaTeX，数学公式更美观
sp.setup_style("ieee", "pastel", lang="en")
fig, ax = sp.plot(x, y, xlabel="Time $t$ (s)", ylabel="Voltage $V$ (V)")
```

---

## new_figure — 创建图形

```python
fig, ax = sp.new_figure(venue="nature", figsize=None, **kwargs)
```

### 示例

```python
fig, ax = sp.new_figure("ieee")
fig, axes = sp.new_figure("thesis", nrows=1, ncols=2)
```

---

## save — 保存图片

```python
sp.save(fig, name, dpi=1200, formats=("pdf", "png"), dir=None)
```

### 示例

```python
sp.save(fig, "fig1")                          # PDF + PNG 1200 DPI
sp.save(fig, "word稿", formats=("png",), dpi=1200)
sp.save(fig, "投稿", formats=("pdf",))
sp.save(fig, "fig", dir="outputs")
sp.save(fig, "nested/dir/fig")                # 自动创建嵌套目录
```

---

## PlotResult — 增强返回类型

```python
result = sp.PlotResult(fig, ax)
```

### 特性

- **元组解包**: `fig, ax = result`
- **属性访问**: `result.fig`, `result.ax`, `result.axes`
- **链式调用**: `result.xlabel("X").ylabel("Y").save("fig")`
- **多子图支持**: `result.ax_array` 访问子图数组

### 示例

```python
# 基础用法
fig, ax = sp.plot(x, y)
result = sp.PlotResult(fig, ax)
result.xlabel("时间 (s)").ylabel("电压 (V)").save("结果图")

# 多子图统一设置
fig, axes = sp.paper_subplots(1, 2)
result = sp.PlotResult(fig, axes)
result.xlabel("共同X标签").ylabel("共同Y标签").add_panel_labels().save("subplots")

# 属性访问
print(result.fig)      # Figure 对象
print(result.ax)       # Axes 对象（单个子图）
print(result.ax_array) # Axes 数组（多子图）
```

### 链式方法

| 方法 | 说明 |
|------|------|
| `xlabel(label)` | 设置 X 轴标签 |
| `ylabel(label)` | 设置 Y 轴标签 |
| `title(title)` | 设置标题 |
| `suptitle(title)` | 设置图形总标题 |
| `xlim(left, right)` | 设置 X 轴范围 |
| `ylim(bottom, top)` | 设置 Y 轴范围 |
| `legend()` | 添加图例 |
| `grid(visible)` | 设置网格 |
| `tight_layout()` | 自动调整布局 |
| `plot(x, y)` | 添加折线（单图）|
| `scatter(x, y)` | 添加散点（单图）|
| `axhline(y)` | 添加水平线 |
| `axvline(x)` | 添加垂直线 |
| `annotate(text, xy)` | 添加标注 |
| `save(name, **kwargs)` | 保存图形 |
| `show()` | 显示图形 |
| `close()` | 关闭图形 |
| `set_labels(**kwargs)` | 一次性设置标签 |
| `add_panel_labels()` | 添加 (a) (b) 面板标签 |

---

## 工具函数

```python
sp.list_venues()                # 所有 venue
sp.list_palettes()              # 所有配色
sp.list_resident_palettes()     # 四大内置色系
sp.list_pastel_subsets()        # pastel 子集
sp.list_ocean_subsets()         # ocean 子集
sp.list_forest_subsets()        # forest 子集
sp.list_sunset_subsets()        # sunset 子集
sp.list_paper_layouts()         # 论文子图尺寸
sp.get_venue_info("ieee")       # venue 详情
sp.get_palette("pastel")        # 获取 HEX 列表
sp.set_custom_palette(colors)   # 自定义配色
sp.reset_style()                # 重置 matplotlib
```

---

## 颜色工具

```python
from sciplot.utils import hex_to_rgb, rgb_to_hex, lighten_color, darken_color, generate_gradient

# 生成渐变色
sp.generate_gradient("#cdb4db", "#264653", 5)
```

---

## 智能辅助

```python
sp.auto_rotate_labels(ax)           # 自动旋转标签避免重叠
sp.smart_legend(ax, outside=True)   # 智能图例位置
sp.optimize_layout(fig)             # 自动优化布局
sp.suggest_figsize(n_items=20)      # 根据数据量建议尺寸
sp.check_color_contrast("#FFF", "#000")  # 检查颜色对比度
```

---

## 配置系统（v1.7.4 新增）

```python
# 设置全局默认值
sp.set_defaults(venue="nature", lang="zh", palette="pastel")

# 获取当前配置
config = sp.get_config()
print(config.venue)   # "nature"
print(config.lang)    # "zh"

# 从文件加载配置
sp.load_config("sciplot_config.json")

# 重置为出厂默认
sp.reset_config()
```

---

## 验证工具

```python
from sciplot.utils import (
    validate_array_like,
    validate_labels_match_data,
    validate_positive_number,
    validate_choice,
    validate_dict_not_empty,
)

# 验证数组类数据
data = validate_array_like([1, 2, 3])

# 验证标签匹配
validate_labels_match_data([1, 2, 3], ["A", "B", "C"])

# 验证正数
validate_positive_number(value, name="value")

# 验证选项
validate_choice(value, choices=["A", "B", "C"])

# 验证字典非空
validate_dict_not_empty(my_dict, name="my_dict")
```
