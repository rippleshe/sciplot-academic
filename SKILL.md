# SciPlot Academic — 包使用 Skill (v1.7)

---
name: sciplot
description: >
  科研绘图技能（sciplot-academic 包版 v1.7）。凡涉及学术图表、论文插图、数据可视化、
  matplotlib 绘图、期刊格式配图、毕设/竞赛图片等需求，必须调用本技能。
  本技能针对已安装 sciplot-academic 包的环境，直接 `import sciplot as sp` 使用，
  无需复制任何文件到项目目录。
  默认中文 + Nature 期刊样式 + pastel 配色，支持 IEEE/APS/Springer/Thesis 学位论文，
  提供折线、散点、柱状、分组柱状、堆叠柱状、水平柱状、面积图、箱线、小提琴、热力图、
  阶梯图、误差条、置信区间、组合图、多子图、显著性标注等全类型图表。
  支持自定义配色方案（单/双/三/四/五色自动选择）、3D可视化扩展、智能辅助功能。
  **本版本彻底移除 rainbow/TOL 等 SciencePlots 依赖配色，所有配色均为内置。**
---

## 0. 安装方式

```bash
# pip
pip install sciplot-academic

# uv（推荐）
uv pip install sciplot-academic

# ML 扩展（可选）
uv pip install sciplot-academic[ml]
```

---

## 1. 快速上手

```python
import sciplot as sp
import numpy as np

x = np.linspace(0, 10, 200)

# 单线图
fig, ax = sp.plot(x, np.sin(x), xlabel="时间 (s)", ylabel="电压 (V)")
sp.save(fig, "结果图")

# 多线对比（≤4 自动选 pastel/earth/ocean 子集）
fig, ax = sp.plot_multi(x, [np.sin(x), np.cos(x)],
                       labels=["方法 A", "方法 B"],
                       xlabel="迭代次数", ylabel="准确率 (%)")
sp.save(fig, "对比")
```

---

## 2. 核心函数

### `sp.setup_style(venue, palette, lang)`

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `venue` | `"nature"` | 期刊/场合预设 |
| `palette` | `"pastel"` | 配色方案 |
| `lang` | `"zh"` | `"zh"`/`"zh-cn"` 中文，`"en"` 英文 |

```python
sp.setup_style()                  # 默认：nature + pastel + 中文
sp.setup_style(lang="en")         # 英文模式
sp.setup_style("ieee", "pastel-2")  # IEEE + 前2色
sp.setup_style("thesis", "earth-3") # 学位论文 + 大地色
```

### `sp.new_figure(venue, figsize, **kwargs)`

```python
fig, ax = sp.new_figure("ieee")
fig, axes = sp.new_figure("thesis", nrows=1, ncols=2)
```

### `sp.save(fig, name, dpi, formats, dir)`

```python
sp.save(fig, "fig1")                       # PDF + PNG 1200 DPI
sp.save(fig, "word稿", formats=("png",), dpi=1200)
sp.save(fig, "投稿", formats=("pdf",))
sp.save(fig, "fig", dir="outputs")
```

---

## 3. 期刊样式与尺寸

| venue | 尺寸（英寸） | 适用场景 |
|-------|-------------|----------|
| `nature` | 7.0 × 5.0 | Nature/Science 双栏全图 |
| `ieee` | 3.5 × 3.0 | IEEE 单栏 |
| `aps` | 3.4 × 2.8 | APS Physical Review |
| `springer` | 6.0 × 4.5 | Springer 期刊 |
| `thesis` | 6.1 × 4.3 | 学位论文（A4 版心） |
| `presentation` | 8.0 × 5.5 | 幻灯片 |

---

## 4. 配色方案

### 三大常驻色系（推荐，首选 pastel）

| 系列 | 风格 | 子集 |
|------|------|------|
| `pastel` | 柔和粉彩 | pastel-1/2/3/4 |
| `earth` | 大地色系 | earth-1/2/3/4 |
| `ocean` | 海洋蓝绿 | ocean-1/2/3/4 |

### 人民币系列（各 5 色）

`100yuan`(红) / `50yuan`(绿) / `20yuan`(棕) / `10yuan`(蓝) / `5yuan`(紫) / `1yuan`(橄榄)

### 自定义配色

```python
# 简单自定义配色
sp.set_custom_palette(["#E74C3C", "#3498DB"], name="brand")
sp.setup_style(palette="brand")     # 2 色
sp.setup_style(palette="brand-1")   # 只取第1色

# 注册完整配色方案（支持自动选择）
my_scheme = {
    "single":    ["#264653"],
    "double":    ["#264653", "#2a9d8f"],
    "triple":    ["#264653", "#2a9d8f", "#e9c46a"],
    "quadruple": ["#264653", "#2a9d8f", "#e9c46a", "#f4a261"],
    "quintuple": ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"],
}
sp.register_color_scheme("mytheme", my_scheme)
sp.setup_style(palette="mytheme-triple")  # 明确使用3色
sp.plot_multi(x, [y1, y2, y3], palette="mytheme")  # 自动选择3色
```

---

## 5. 图表函数速查

### 基础图表

```python
sp.plot(x, y)                    # 折线图（简化入口）
sp.plot_line(x, y, ...)          # 折线图（完整参数）
sp.plot_multi(x, [y1, y2])       # 多线图（自动配色子集）
sp.plot_multi_line(x, y_list, use_linestyles=False, ...)
sp.plot_scatter(x, y, s=20, alpha=0.7, ...)
sp.plot_step(x, y, where="mid")  # 阶梯图（CDF/直方风格）

# 面积图
sp.plot_area(x, y, alpha=0.3)    # 单组面积图
sp.plot_multi_area(x, [y1, y2], stacked=True)  # 堆叠面积图
```

### 分布图表

```python
sp.plot_bar(categories, values)              # 单组柱状图
sp.plot_grouped_bar(groups, data)           # 分组柱状图（论文最常见）
sp.plot_stacked_bar(categories, data)       # 堆叠柱状图
sp.plot_horizontal_bar(categories, values, sort=True)  # 水平柱状图
sp.plot_box(data_list, labels=..., showfliers=True)   # 箱线图
sp.plot_violin(data_list, labels=..., showmedians=True)  # 小提琴图
sp.plot_histogram(data, bins=30, density=False)  # 直方图
sp.plot_errorbar(x, y, yerr, fmt="o", capsize=4)  # 误差条
sp.plot_confidence(x, mean, std, alpha=0.25)  # 置信区间
sp.plot_heatmap(data, cmap="Blues", show_values=False)  # 热力图

# 组合图（柱状 + 折线，双 Y 轴）
sp.plot_combo(
    x=["Q1", "Q2", "Q3", "Q4"],
    bar_data={"销售额": [100, 120, 140, 160]},
    line_data={"增长率": [5, 8, 12, 15]},
)
```

### 显著性标注

```python
# 在箱线图/小提琴图上标注显著性
sp.annotate_significance(ax, x1=1, x2=2, y=8.5, p_value=0.03)   # *
sp.annotate_significance(ax, x1=1, x2=3, y=9.5, p_value=0.0005)  # ***
```

---

## 6. 机器学习可视化（扩展）

需要安装：`pip install sciplot-academic[ml]`

```python
from sciplot._ext.ml import plot_pca, plot_confusion_matrix

# PCA 可视化
fig, ax = plot_pca(data, labels=labels, venue="nature")

# 混淆矩阵
fig, ax = plot_confusion_matrix(y_true, y_pred, labels=["A", "B", "C"])

# 特征重要性
fig, ax = plot_feature_importance(features, importance, top_n=15)

# 学习曲线
fig, ax = plot_learning_curve(train_scores, val_scores, sizes)
```

### 3D 可视化（扩展）

```python
from sciplot._ext.plot3d import plot_surface, plot_contour, plot_3d_scatter

# 3D 曲面
fig, ax = plot_surface(X, Y, Z, xlabel="X", ylabel="Y", zlabel="Z")

# 等高线图
fig, ax = plot_contour(X, Y, Z, levels=15, filled=True)

# 3D 散点
fig, ax = plot_3d_scatter(x, y, z, c=colors, cmap="plasma")
```

---

## 7. 高级布局

### 规则子图

```python
fig, axes = sp.create_subplots(2, 2, venue="ieee", sharex=True)
axes[0,0].plot(x, y)
sp.save(fig, "multi")
```

### 论文子图布局（推荐）

```python
# 精确匹配论文版心
fig, axes = sp.paper_subplots(1, 2, venue="thesis")
axes[0].plot(x, y1); axes[0].set_title("(a)")
axes[1].plot(x, y2); axes[1].set_title("(b)")
sp.save(fig, "1x2_thesis", formats=("png",), dpi=1200)
```

### 面板标签

```python
fig, axes = sp.paper_subplots(1, 3, venue="thesis")
# ... 绘图 ...
sp.add_panel_labels(axes)              # (a) (b) (c)
sp.add_panel_labels(axes, style="A")  # (A) (B) (C)
sp.add_panel_labels(axes, labels=["实验", "对照", "基准"])  # 自定义
```

### GridSpec 不规则布局

```python
fig, gs = sp.create_gridspec(2, 3, venue="nature")
ax_top = fig.add_subplot(gs[0, :])   # 顶部通栏
ax_l = fig.add_subplot(gs[1, 0])
ax_m = fig.add_subplot(gs[1, 1])
ax_r = fig.add_subplot(gs[1, 2])
```

---

## 8. 工具函数

```python
sp.list_venues()                # 所有 venue
sp.list_palettes()              # 所有配色
sp.list_resident_palettes()     # 三大常驻色系
sp.list_pastel_subsets()        # pastel 子集
sp.list_rmb_palettes()          # 人民币配色
sp.list_paper_layouts()         # 论文子图尺寸
sp.get_venue_info("ieee")       # venue 详情
sp.get_palette("pastel")        # 获取 HEX 列表
sp.set_custom_palette(colors)   # 自定义配色
sp.reset_style()                # 重置 matplotlib

# 颜色工具
from sciplot.utils import hex_to_rgb, rgb_to_hex, lighten_color, darken_color, generate_gradient
sp.generate_gradient("#cdb4db", "#264653", 5)  # 渐变色

# 智能辅助
sp.auto_rotate_labels(ax)           # 自动旋转标签避免重叠
sp.smart_legend(ax, outside=True)   # 智能图例位置
sp.optimize_layout(fig)             # 自动优化布局
sp.suggest_figsize(n_items=20)      # 根据数据量建议尺寸
sp.check_color_contrast("#FFF", "#000")  # 检查颜色对比度
```

---

## 9. AI 脚本规范

**必须创建独立可运行的 Python 脚本**，通过 `import sciplot as sp` 使用本库。

### 标准模板

```python
"""
科研绘图脚本
依赖: pip install sciplot-academic
运行: python plot_result.py
"""
import numpy as np
import sciplot as sp

# 数据
x = np.linspace(0, 10, 200)
y1, y2 = np.sin(x), np.cos(x)

# Word 中文论文（PNG）
sp.setup_style("thesis", "pastel-2", lang="zh")
fig, ax = sp.plot(x, y1, xlabel="时间 (s)", ylabel="幅度")
sp.save(fig, "word_single", formats=("png",), dpi=1200)

# Word 双子图
sp.setup_style("thesis", "pastel-2", lang="zh")
fig, axes = sp.paper_subplots(1, 2, venue="thesis")
axes[0].plot(x, y1); axes[0].set_title("(a)")
axes[1].plot(x, y2); axes[1].set_title("(b)")
sp.add_panel_labels(axes)
sp.save(fig, "word_double", formats=("png",), dpi=1200)

# IEEE LaTeX（PDF）
sp.setup_style("ieee", "pastel-2", lang="en")
fig, ax = sp.new_figure("ieee")
ax.plot(x, y1, label="Method A")
ax.plot(x, y2, label="Method B")
sp.save(fig, "ieee_pdf", formats=("pdf",))

print("✓ 已保存")
```

### 场景速查

| 场景 | venue | formats | dpi | lang |
|------|-------|---------|-----|------|
| Word 单图 | thesis | png | 1200 | zh |
| Word 双图 | thesis | png | 1200 | zh |
| IEEE 投稿 | ieee | pdf | — | en |
| Nature 投稿 | nature | pdf | — | en |

---

## 10. 最佳实践

- **Word 用 PNG 1200 DPI，LaTeX 用 PDF**
- **多子图总宽锁定**：用 `paper_subplots()` 或手动 `figsize=(6.1, h)`
- **刻度向内**：所有函数已自动 `tick_params(direction='in')`
- **无网格**：默认 `axes.grid=False`，保持简洁
- **色盲友好**：≥4 条线用 `use_linestyles=True`

---

## 11. 能力边界

**不支持的图表类型**：

| 类型 | 推荐替代 |
|------|---------|
| 决策树 | `sklearn.tree.plot_tree` |
| 神经网络结构 | `PlotNeuralNet` |
| 流程图 | `graphviz` / `Mermaid` |
| 3D 图 | `plotly` |
| 地图 | `cartopy` |

---

## 12. 版本信息

- 包名：`sciplot-academic`（PyPI）
- 版本：**1.7.0**
- 默认：Nature + pastel + 中文

### v1.7 更新

- 🆕 **配色方案系统** `register_color_scheme()`，支持单/双/三/四/五色自动选择
- 🆕 **面积图** `plot_area()` / `plot_multi_area()`，支持堆叠模式
- 🆕 **堆叠柱状图** `plot_stacked_bar()`，展示比例构成
- 🆕 **水平柱状图** `plot_horizontal_bar()`，适合类别较多场景
- 🆕 **组合图** `plot_combo()`，柱状+折线双Y轴
- 🆕 **3D可视化扩展** `_ext/plot3d.py`，曲面/等高线/3D散点
- 🆕 **智能辅助工具** `utils/smart.py`，自动标签旋转/智能图例/布局优化

### v1.6 更新

- 🆕 **分组柱状图** `plot_grouped_bar()`，论文最常用
- 🆕 **显著性标注** `annotate_significance()`，自动显示 */**/***
- 🆕 **面板标签** `add_panel_labels()`，自动 (a)(b)(c)
- 🆕 **阶梯图** `plot_step()`，CDF/直方风格
- 🆕 **颜色工具** `utils` 模块
- 🆕 **论文子图尺寸表** `PAPER_LAYOUTS` 扩充
- 🆕 **彻底移除 rainbow/TOL 依赖**，所有配色均为内置
