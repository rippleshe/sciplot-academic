# 语法糖功能

SciPlot 提供四种语法糖，让绘图代码更简洁、更流畅。

---

## 1. Fluent Interface 链式调用

通过链式 API 实现流畅的绘图流程，支持多图层叠加。

### 基础用法

```python
import sciplot as sp
import numpy as np

x = np.linspace(0, 10, 100)

# 最简链式调用
fig = sp.style("nature").palette("pastel").plot(x, np.sin(x)).save("output")

# 使用 chain() 入口
fig = sp.chain(venue="thesis", palette="ocean", lang="zh").plot(x, y).save("fig")
```

### 多图层叠加

```python
fig = (sp.style("ieee")
         .palette("forest")
         .plot(x, np.sin(x), label="sin")
         .scatter(x, np.cos(x), label="cos")
         .legend()
         .xlabel("时间 (s)")
         .ylabel("幅度")
         .title("三角函数")
         .save("multi_layer"))
```

### 链式方法速查

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `sp.style(venue)` | 设置期刊样式 | PlotChain |
| `sp.palette(name)` | 设置配色方案 | PlotChain |
| `sp.chain(venue, palette, lang)` | 完整链式入口 | PlotChain |
| `.plot(x, y, **kwargs)` | 添加折线 | FigureWrapper |
| `.scatter(x, y, **kwargs)` | 添加散点 | FigureWrapper |
| `.bar(x, y, **kwargs)` | 添加柱状图 | FigureWrapper |
| `.xlabel(label)` | 设置 X 轴标签 | FigureWrapper |
| `.ylabel(label)` | 设置 Y 轴标签 | FigureWrapper |
| `.title(title)` | 设置标题 | FigureWrapper |
| `.legend(**kwargs)` | 显示图例 | FigureWrapper |
| `.save(name, **kwargs)` | 保存图片 | list[Path] |
| `.show()` | 显示图形 | None |

---

## 2. Context Manager 上下文管理器

临时切换样式，不影响全局设置，支持嵌套使用。

### 基础用法

```python
import sciplot as sp
import numpy as np

x = np.linspace(0, 10, 100)

# 临时切换样式
with sp.style_context("ieee", palette="forest"):
    fig, ax = sp.plot(x, np.sin(x))
    sp.save(fig, "ieee_style")

# 恢复默认样式继续绘图
fig, ax = sp.plot(x, np.cos(x))  # 使用默认 nature + pastel
```

### 嵌套上下文

```python
with sp.style_context("nature", palette="pastel"):
    fig1, ax1 = sp.plot(x, y1)  # nature + pastel
    
    with sp.style_context("ieee", palette="ocean"):
        fig2, ax2 = sp.plot(x, y2)  # ieee + ocean
    
    # 恢复为 nature + pastel
    fig3, ax3 = sp.plot(x, y3)
```

### 自定义 rcParams

```python
with sp.style_context("thesis", lang="zh", figure.dpi=200, font.size=14):
    fig, ax = sp.plot(x, y)
```

---

## 3. 简洁函数别名

更短更直观的函数名，适合快速绘图。

| 别名 | 完整名称 | 说明 |
|------|----------|------|
| `sp.line()` | `sp.plot_line()` | 折线图 |
| `sp.scatter()` | `sp.plot_scatter()` | 散点图 |
| `sp.bar()` | `sp.plot_bar()` | 柱状图 |
| `sp.hbar()` | `sp.plot_horizontal_bar()` | 水平柱状图 |
| `sp.hist()` | `sp.plot_histogram()` | 直方图 |
| `sp.box()` | `sp.plot_box()` | 箱线图 |
| `sp.violin()` | `sp.plot_violin()` | 小提琴图 |
| `sp.heatmap()` | `sp.plot_heatmap()` | 热力图 |
| `sp.area()` | `sp.plot_area()` | 面积图 |
| `sp.step()` | `sp.plot_step()` | 阶梯图 |
| `sp.errorbar()` | `sp.plot_errorbar()` | 误差条图 |

### 使用示例

```python
import sciplot as sp
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

# 简洁别名
fig, ax = sp.line(x, y)
fig, ax = sp.scatter(x, y)
fig, ax = sp.bar(["A", "B"], [1, 2])
fig, ax = sp.hbar(["A", "B"], [1, 2])
fig, ax = sp.hist(data, bins=30)
fig, ax = sp.box([data1, data2])
fig, ax = sp.violin([data1, data2])
fig, ax = sp.heatmap(matrix)
fig, ax = sp.area(x, y)
fig, ax = sp.step(x, y)
fig, ax = sp.errorbar(x, y, yerr)
```

---

## 4. PlotResult 增强返回类型（v1.7.4 新增）

统一封装绘图结果，支持元组解包、属性访问和链式调用。

### 基础用法

```python
import sciplot as sp
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

# 包装为 PlotResult
fig, ax = sp.plot(x, y)
result = sp.PlotResult(fig, ax)

# 链式调用设置标签
result.xlabel("时间 (s)").ylabel("电压 (V)").title("正弦波").save("output")
```

### 多子图统一设置

```python
# 创建多子图
fig, axes = sp.paper_subplots(1, 2, venue="thesis")
result = sp.PlotResult(fig, axes)

# 统一设置所有子图的标签
result.xlabel("共同X标签").ylabel("共同Y标签")

# 添加面板标签 (a) (b)
result.add_panel_labels()

# 保存
result.save("subplots", formats=("png",), dpi=1200)
```

### 属性访问

```python
fig, ax = sp.plot(x, y)
result = sp.PlotResult(fig, ax)

# 访问属性
result.fig        # Figure 对象
result.figure     # Figure 对象（别名）
result.ax         # Axes 对象（单个子图）
result.axes       # Axes 对象或数组
result.ax_array   # Axes 数组（多子图时）
```

### 元组解包

```python
result = sp.PlotResult(fig, ax)

# 支持解包
f, a = result           # f 是 fig, a 是 ax
fig = result[0]         # 通过索引访问
ax = result[1]
```

### 链式方法速查

| 方法 | 说明 | 适用场景 |
|------|------|----------|
| `xlabel(label)` | 设置 X 轴标签 | 单图/多图 |
| `ylabel(label)` | 设置 Y 轴标签 | 单图/多图 |
| `title(title)` | 设置标题 | 单图 |
| `suptitle(title)` | 设置总标题 | 多图 |
| `xlim(left, right)` | 设置 X 轴范围 | 单图/多图 |
| `ylim(bottom, top)` | 设置 Y 轴范围 | 单图/多图 |
| `legend()` | 显示图例 | 单图/多图 |
| `grid(visible)` | 设置网格 | 单图/多图 |
| `tight_layout()` | 自动调整布局 | 单图/多图 |
| `plot(x, y)` | 添加折线 | 单图 |
| `scatter(x, y)` | 添加散点 | 单图 |
| `axhline(y)` | 添加水平线 | 单图/多图 |
| `axvline(x)` | 添加垂直线 | 单图/多图 |
| `annotate(text, xy)` | 添加标注 | 单图 |
| `save(name, **kwargs)` | 保存图形 | 单图/多图 |
| `show()` | 显示图形 | 单图/多图 |
| `close()` | 关闭图形 | 单图/多图 |
| `set_labels(**kwargs)` | 一次性设置标签 | 单图/多图 |
| `add_panel_labels()` | 添加 (a) (b) 标签 | 多图 |

---

## 四种风格对比

```python
import sciplot as sp
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

# 风格 1: 传统 API
sp.setup_style("nature", "pastel")
fig, ax = sp.plot_line(x, y, xlabel="X", ylabel="Y")
sp.save(fig, "output")

# 风格 2: 链式调用
sp.style("nature").palette("pastel").plot(x, y).xlabel("X").ylabel("Y").save("output")

# 风格 3: 简洁别名
sp.setup_style("nature", "pastel")
fig, ax = sp.line(x, y, xlabel="X", ylabel="Y")
sp.save(fig, "output")

# 风格 4: PlotResult 增强返回类型
fig, ax = sp.plot(x, y)
sp.PlotResult(fig, ax).xlabel("X").ylabel("Y").save("output")
```

选择最适合你代码风格的写法！
