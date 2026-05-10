# SciPlot 完整 API 参考 (v1.9.1)

## 安装

```bash
pip install sciplot-academic          # 基础
pip install sciplot-academic[ml]      # + scikit-learn
pip install sciplot-academic[stats]   # + scipy（统计图表）
pip install sciplot-academic[all]     # 全部
```

---

## 核心函数

### setup_style

```python
sp.setup_style(venue="nature", palette="pastel", lang="zh", theme="light")
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| venue | 从 Config 读取，回退 "nature" | 期刊预设 |
| palette | 从 Config 读取，回退 "pastel" | 配色方案 |
| lang | 从 Config 读取，回退 "zh" | 语言 |
| theme | "light" | "light" 或 "dark" |

v1.9.0+: `set_defaults(venue="ieee")` 后 `setup_style()` 自动读取。

### save

```python
sp.save(fig, name, dpi=None, formats=None, dir=None, close=False)
```
- `dpi`: None 读取 Config（默认 1200）
- `formats`: None 读取 Config（默认 ("pdf", "png")）
- `close`: True 保存后关闭图形释放内存

### new_figure / paper_subplots / create_subplots

```python
fig, ax = sp.new_figure(venue="nature")
fig, axes = sp.paper_subplots(1, 2, venue="thesis")   # 精确版心
fig, axes = sp.create_subplots(2, 2, venue="ieee")     # 比例缩放
fig, gs = sp.create_gridspec(2, 3, venue="nature")     # 不规则布局
```

---

## 图表函数

### 基础

| 函数 | 别名 | 说明 |
|------|------|------|
| `plot(x, y)` / `plot_line(x, y)` | `line()` | 折线图 |
| `plot_multi(x, [y1,y2])` | `multi()` | 多线（自动配色） |
| `plot_multi_line(x, y_list, use_linestyles=True)` | `multi_line()` | 多线（完整参数） |
| `plot_scatter(x, y)` | `scatter()` | 散点图 |
| `plot_step(x, y)` | `step()` | 阶梯图 |
| `plot_area(x, y)` | `area()` | 面积图 |
| `plot_multi_area(x, [y1,y2], stacked=True)` | `multi_area()` | 堆叠面积 |

### 柱状图

| 函数 | 别名 | 说明 |
|------|------|------|
| `plot_bar(cats, vals)` | `bar()` | 单组柱状 |
| `plot_grouped_bar(groups, data)` | `grouped_bar()` | 分组柱状（论文最常用） |
| `plot_stacked_bar(cats, data)` | `stacked_bar()` | 堆叠柱状 |
| `plot_horizontal_bar(cats, vals)` | `hbar()` | 水平柱状 |
| `plot_lollipop(cats, vals)` | `lollipop()` | 棒棒糖图 |
| `plot_combo(x, bar_data, line_data)` | `combo()` | 柱+线双轴组合 |

### 分布

| 函数 | 别名 | 说明 |
|------|------|------|
| `plot_box(data)` | `box()` | 箱线图 |
| `plot_violin(data)` | `violin()` | 小提琴图 |
| `plot_histogram(data)` | `hist()` | 直方图 |
| `plot_density(data)` | `density()` | 核密度估计 |
| `plot_multi_density(data_list)` | `multi_density()` | 多组密度对比 |
| `plot_heatmap(data)` | `heatmap()` | 热力图 |

### 误差与置信

| 函数 | 别名 | 说明 |
|------|------|------|
| `plot_errorbar(x, y, yerr)` | `errorbar()` | 误差条 |
| `plot_confidence(x, mean, std)` | `confidence()` | 置信区间带 |

### 时间序列

| 函数 | 别名 | 说明 |
|------|------|------|
| `plot_timeseries(t, y)` | `timeseries()` | 时间序列（支持事件标注、背景区域、滚动均值） |
| `plot_multi_timeseries(t, [y1,y2])` | `multi_timeseries()` | 多时间序列 |
| `plot_slope(labels, before, after)` | — | 斜率图 |

### 统计诊断

| 函数 | 别名 | 说明 |
|------|------|------|
| `plot_residuals(y_true, y_pred)` | `residuals()` | 残差图 |
| `plot_qq(data)` | `qq()` | Q-Q 图（norm/expon/uniform/t） |
| `plot_bland_altman(y1, y2)` | `bland_altman()` | Bland-Altman 一致性 |

### 多维/进阶

| 函数 | 别名 | 说明 |
|------|------|------|
| `plot_radar(categories, values_list)` | `radar()` | 雷达图 |
| `plot_parallel(data)` | — | 平行坐标图 |
| `plot_scatter_matrix(data)` | — | 散点矩阵 |

### 标注

| 函数 | 说明 |
|------|------|
| `annotate_significance(ax, x1, x2, y, p_value)` | 显著性标注（*/**/***） |
| `add_panel_labels(axes)` | 面板标签 (a)(b)(c) |

---

## 扩展模块

### ML 扩展（`pip install sciplot-academic[ml]`）

```python
sp.plot_pca(data, labels=y, venue="nature")
sp.plot_confusion_matrix(y_true, y_pred, labels=["A","B","C"])
sp.plot_feature_importance(features, importance, top_n=15)
sp.plot_learning_curve(train_scores, val_scores, train_sizes)
```

### 3D 扩展（内置）

```python
sp.plot_surface(X, Y, Z, xlabel="X", ylabel="Y", zlabel="Z")
sp.plot_contour(X, Y, Z, levels=15, filled=True)
sp.plot_3d_scatter(x, y, z, c=values, cmap="plasma")
sp.plot_wireframe(X, Y, Z, rstride=2, cstride=2)
```

### 网络图（`pip install networkx`）

```python
sp.plot_network(nodes, edges)
sp.plot_network_from_matrix(adj_matrix, labels=["A","B","C"])
sp.plot_network_communities(nodes, edges, method="louvain")
```

### 层次聚类（scipy 已内置）

```python
sp.plot_dendrogram(data, method="ward")
sp.plot_clustermap(data, row_cluster=True, col_cluster=True)
```

### 维恩图（`pip install matplotlib-venn`）

```python
sp.plot_venn2((10, 8, 5), set_labels=("A", "B"))
sp.plot_venn3((10, 8, 5, 7, 4, 3, 2), set_labels=("A", "B", "C"))
```

---

## PlotResult 链式方法

所有绘图函数返回 `PlotResult`，支持：

```python
result = sp.plot(x, y)
result.xlabel("X").ylabel("Y").title("标题").save("fig")

# 多子图统一设置
result = sp.PlotResult(fig, axes)
result.xlabel("共同X").add_panel_labels().save("fig")
```

| 方法 | 说明 |
|------|------|
| `xlabel/ylabel(label)` | 设置轴标签 |
| `title(title)` / `suptitle(title)` | 设置标题 |
| `xlim/ylim(...)` | 设置范围 |
| `legend()` | 显示图例 |
| `grid(visible)` | 设置网格 |
| `tight_layout()` | 优化布局 |
| `plot/scatter(x, y)` | 添加图层 |
| `axhline/axvline(v)` | 参考线 |
| `annotate(text, xy)` | 标注 |
| `add_panel_labels()` | 面板标签 |
| `save(name)` / `show()` / `close()` | 输出 |

---

## 工具函数

```python
# 颜色工具
sp.hex_to_rgb("#FF0000")            # → (1.0, 0.0, 0.0)
sp.rgb_to_hex(1.0, 0.0, 0.0)       # → "#ff0000"
sp.lighten_color("#264653", 0.3)    # 变亮
sp.darken_color("#cdb4db", 0.3)     # 变暗
sp.generate_gradient("#000", "#FFF", 5)  # 渐变

# 智能辅助
sp.auto_rotate_labels(ax)
sp.smart_legend(ax, outside=True)
sp.optimize_layout(fig)
sp.adjust_subplots(fig, hspace=0.4)
sp.suggest_figsize(n_items=20)
sp.check_color_contrast("#FFF", "#000")

# 配置
sp.set_defaults(venue="ieee", palette="earth", dpi=600)
sp.get_config("venue")
sp.load_config()   # 自动查找 .sciplot.toml / pyproject.toml
sp.reset_config()

# 诊断
sp.inspect()  # 打印环境信息
```
