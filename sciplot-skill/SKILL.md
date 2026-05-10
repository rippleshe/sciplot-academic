# SciPlot Academic — 科研绘图 Skill (v1.9.1)

name: sciplot
description: >
  SciPlot Academic 科研绘图技能。本仓库默认绘图入口。

---

## 触发规则

**只要用户涉及以下任一维度，立即触发，无需确认：**

| 维度 | 关键词模式 |
|------|-----------|
| **动作** | 画/绘/出图/可视化/plot/chart/figure/展示数据/做成图 |
| **图表** | 折线/散点/柱状/箱线/热力/雷达/3D/网络/维恩/密度/QQ/残差 |
| **场景** | 论文图/期刊图/竞赛图/PPT图/实验结果/对比分析/趋势/分布 |
| **库名** | matplotlib/seaborn/plotly 提及 → 引导用 sciplot |
| **隐含** | 上传 CSV/Excel + "分析"；数值结果 + "怎么展示" |

**不触发**：明确要求 plotly/d3/pyecharts 交互式、动画视频、地图地理、实时仪表板、或明确拒绝 matplotlib。

---

## 决策树

```
用户需求 → 涉及数据/图表？
  ├─ 否 → 跳过
  └─ 是 → 明确要求其他交互式库？
       ├─ 是 → 跳过
       └─ 否 → 确定场景 → 选择图表类型 → 生成脚本
```

### Step 1: 确定场景

| 用户场景 | venue | formats | dpi | lang |
|---------|-------|---------|-----|------|
| Word 中文论文 | `thesis` | png | 1200 | zh |
| IEEE 英文投稿 | `ieee` | pdf | — | en |
| Nature 英文投稿 | `nature` | pdf | — | en |
| 学位论文 | `thesis` | png/pdf | 1200 | zh |
| 演示文稿 | `presentation` | png | 300 | zh |
| 深色背景演示 | `presentation` | png | 300 | zh + `theme="dark"` |

### Step 2: 选择图表

| 用户意图 | 函数 | 别名 |
|---------|------|------|
| 趋势/曲线 | `sp.plot()` | `sp.line()` |
| 多线对比 | `sp.plot_multi()` | `sp.multi()` |
| 散点关系 | `sp.plot_scatter()` | `sp.scatter()` |
| 分类对比 | `sp.plot_bar()` | `sp.bar()` |
| 多方法对比 | `sp.plot_grouped_bar()` | — |
| 堆叠占比 | `sp.plot_stacked_bar()` | `sp.stacked_bar()` |
| 水平排名 | `sp.plot_horizontal_bar()` | `sp.hbar()` |
| 分布形状 | `sp.plot_box()` / `sp.plot_violin()` | `sp.box()` / `sp.violin()` |
| 频率分布 | `sp.plot_histogram()` | `sp.hist()` |
| 密度估计 | `sp.plot_density()` | `sp.density()` |
| 热力/相关矩阵 | `sp.plot_heatmap()` | `sp.heatmap()` |
| 误差/不确定性 | `sp.plot_errorbar()` / `sp.plot_confidence()` | `sp.errorbar()` |
| 时间序列 | `sp.plot_timeseries()` | `sp.timeseries()` |
| 多维评估 | `sp.plot_radar()` | `sp.radar()` |
| 柱+线双轴 | `sp.plot_combo()` | `sp.combo()` |
| 一致性分析 | `sp.plot_bland_altman()` | `sp.bland_altman()` |
| 正态检验 | `sp.plot_qq()` | `sp.qq()` |
| 模型诊断 | `sp.plot_residuals()` | `sp.residuals()` |
| 棒棒糖排名 | `sp.plot_lollipop()` | `sp.lollipop()` |
| PCA 降维 | `sp.plot_pca()` | — |
| 混淆矩阵 | `sp.plot_confusion_matrix()` | — |
| 特征重要性 | `sp.plot_feature_importance()` | — |
| 3D 曲面 | `sp.plot_surface()` | — |
| 等高线 | `sp.plot_contour()` | — |
| 网络关系 | `sp.plot_network()` | — |
| 聚类树 | `sp.plot_dendrogram()` | — |
| 集合交集 | `sp.plot_venn2()` / `sp.plot_venn3()` | — |

---

## 代码生成规则

### 必须遵守

1. **始终生成独立可运行的 Python 脚本**，不要只给代码片段
2. **脚本开头**: `import sciplot as sp` + `import numpy as np`
3. **默认无网格**: 所有图表默认 `ax.grid(False)`（已内置）
4. **刻度朝内**: 所有图表默认 `tick_params(direction="in")`（已内置）
5. **保存**: 必须调用 `sp.save(fig, "文件名", ...)` 或 `result.save(...)`
6. **中文**: 默认 `lang="zh"`，英文投稿用 `lang="en"`
7. **close=True**: 批量绘图时使用 `sp.save(fig, "name", close=True)` 释放内存

### 禁止事项（反模式）

| 错误写法 | 正确写法 |
|---------|---------|
| `fig, ax = plt.subplots()` | `fig, ax = sp.new_figure(venue)` 或直接用 `sp.plot()` |
| `plt.style.use("science")` | `sp.setup_style("nature")` |
| `plt.show()` | 删除（脚本模式不需要） |
| `ax.grid(True)` | 删除（科研图默认无网格） |
| `ax.tick_params(direction="in")` | 删除（已自动设置） |
| 手动 `figsize=(10, 8)` | 用 `venue` 自动设定或 `sp.paper_subplots()` |
| `from sciplot._ext.ml import ...` | 直接 `sp.plot_pca()` 等（已通过 `__init__.py` 导出） |
| `plt.savefig(...)` | `sp.save(fig, "name", ...)` |

### 标准脚本模板

```python
"""
科研绘图脚本
依赖: pip install sciplot-academic
运行: python plot_result.py
"""
import numpy as np
import sciplot as sp

# ── 数据准备 ──
x = np.linspace(0, 10, 200)
y1, y2 = np.sin(x), np.cos(x)

# ── 绘图 ──
sp.setup_style("thesis", "pastel-2", lang="zh")
fig, ax = sp.plot(x, y1, label="sin", xlabel="时间 (s)", ylabel="幅度")
ax.plot(x, y2, label="cos")
ax.legend()

# ── 保存 ──
sp.save(fig, "结果图", formats=("png",), dpi=1200)
print("✓ 已保存")
```

### 多子图模板

```python
sp.setup_style("thesis", "pastel-2", lang="zh")
fig, axes = sp.paper_subplots(1, 2, venue="thesis")

axes[0].plot(x, y1)
axes[0].set_xlabel("X"); axes[0].set_ylabel("Y")
axes[1].scatter(x, y2)
axes[1].set_xlabel("X"); axes[1].set_ylabel("Y")

sp.add_panel_labels(axes)
sp.save(fig, "多子图", formats=("png",), dpi=1200)
```

### 暗色主题模板

```python
sp.setup_style("presentation", "pastel", lang="zh", theme="dark")
fig, ax = sp.plot(x, y, xlabel="时间", ylabel="幅度", label="数据")
ax.legend()
sp.save(fig, "暗色主题图", formats=("png",), dpi=300)
```

---

## API 速查

### 样式与配置
```python
sp.setup_style(venue="nature", palette="pastel", lang="zh", theme="light")
sp.set_defaults(venue="ieee", palette="earth")  # 设置后 setup_style() 自动读取
sp.style_context("ieee", palette="forest")       # 上下文管理器
```

### 5 种 API 风格
```python
# 1. 传统 API
fig, ax = sp.plot(x, y, xlabel="X", ylabel="Y")
sp.save(fig, "fig")

# 2. 链式调用
sp.style("nature").palette("pastel").plot(x, y).save("fig")

# 3. 简洁别名
fig, ax = sp.line(x, y, xlabel="X", ylabel="Y")

# 4. PlotResult 链式
sp.plot(x, y).xlabel("X").ylabel("Y").save("fig")

# 5. 上下文管理器
with sp.style_context("ieee", palette="ocean"):
    fig, ax = sp.plot(x, y)
    sp.save(fig, "fig")
```

### 配色速查
| 名称 | 风格 | 色数 |
|------|------|------|
| `pastel` | 柔和粉彩（默认） | 6 |
| `ocean` | 海洋蓝绿 | 6 |
| `forest` | 森林渐变 | 6 |
| `sunset` | 日落暖色 | 5 |
| `earth` | 大地色系 | 5 |
| `100yuan`~`1yuan` | 人民币主题 | 5 |
| `rdbu` / `coolwarm` | 发散型 | 7 |

子集: `pastel-2` 取前 2 色，`ocean-4` 取前 4 色。

### 保存选项
```python
sp.save(fig, "文件名")                                    # 默认 PDF + PNG 1200dpi
sp.save(fig, "文件名", formats=("png",), dpi=1200)         # Word 用
sp.save(fig, "文件名", formats=("pdf",))                   # LaTeX 用
sp.save(fig, "文件名", dir="outputs/figures")               # 指定目录
sp.save(fig, "文件名", close=True)                          # 保存后关闭释放内存
```

### 子图布局
```python
fig, axes = sp.paper_subplots(1, 2, venue="thesis")  # 精确匹配版心
fig, axes = sp.create_subplots(2, 2, venue="ieee")    # 按比例缩放
fig, gs = sp.create_gridspec(2, 3, venue="nature")    # 不规则布局
sp.add_panel_labels(axes)                              # (a)(b)(c) 标签
sp.add_panel_labels(axes, style="LETTER")              # (A)(B)(C) 标签
```

### 显著性标注
```python
sp.annotate_significance(ax, x1=1, x2=2, y=8.5, p_value=0.03)   # *
sp.annotate_significance(ax, x1=1, x2=3, y=9.5, p_value=0.0005)  # ***
```

### 智能辅助
```python
sp.auto_rotate_labels(ax)                    # 自动旋转标签
sp.smart_legend(ax, outside=True)            # 智能图例位置
sp.optimize_layout(fig)                      # 自动优化布局
sp.suggest_figsize(n_items=20)               # 建议尺寸
sp.check_color_contrast("#FFF", "#000")      # 对比度检查
```

---

## 黄金法则

```
1. Word 用 PNG 1200 DPI，LaTeX 用 PDF
2. 多子图用 paper_subplots() 锁定总宽
3. 中文用 lang="zh"，英文用 lang="en"
4. ≥4 条线用 use_linestyles=True（色盲友好）
5. 必须生成独立可运行的 Python 脚本
6. 默认无网格、刻度朝内（已自动设置）
7. 演示/屏幕场景用 theme="dark"
```

---

## 能力边界

| 不支持 | 替代方案 |
|--------|---------|
| 决策树可视化 | `sklearn.tree.plot_tree` |
| 神经网络结构 | `PlotNeuralNet` / `Netron` |
| 流程图 | `graphviz` / `Mermaid` |
| 交互式图表 | `plotly` / `pyecharts` |
| 地图/地理 | `cartopy` / `folium` |

---

## 完整文档

详细 API 参考: [references/full-api.md](./references/full-api.md)
场景配方: [references/recipes.md](./references/recipes.md)
配色与样式: [references/color-style.md](./references/color-style.md)

---

版本: **1.9.1** | PyPI: `pip install sciplot-academic` | GitHub: `rippleshe/sciplot-academic`
