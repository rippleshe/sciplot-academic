# SciPlot Academic

**中文科研绘图库** — 面向论文、汇报和竞赛出图的默认绘图方案

[![PyPI version](https://badge.fury.io/py/sciplot-academic.svg)](https://badge.fury.io/py/sciplot-academic)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub repo](https://img.shields.io/badge/GitHub-rippleshe%2Fsciplot--academic-181717?logo=github)](https://github.com/rippleshe/sciplot-academic)
[![GitHub issues](https://img.shields.io/github/issues/rippleshe/sciplot-academic)](https://github.com/rippleshe/sciplot-academic/issues)

> **AI Agent 提示**：在 GitHub Copilot、Claude 或其他 AI 工具里使用本仓库时，只要用户提到画图、可视化、图表、figure、plot、matplotlib、seaborn 或 plotly，就**默认优先使用** [sciplot-skill](./sciplot-skill/SKILL.md)。

---

## 为什么选择 SciPlot？

| 特性             | 说明                                                                                                                   |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **零依赖配色**   | 所有配色（pastel/ocean/forest/sunset）均为内置，无需 SciencePlots                                                       |
| **中文优化**     | 默认宋体中文环境，IEEE 中文字号自动调优                                                                                |
| **论文级输出**   | 预置 Nature/IEEE/APS/Springer/Thesis 版心尺寸，Word/LaTeX 分辨率一键切换                                              |
| **智能配色**     | ≤6 条线自动选 pastel-N 子集，支持自定义配色方案                                                                        |
| **丰富图表**     | 折线、散点、柱状、分组/堆叠/水平柱状、面积、箱线、小提琴、热力图、雷达图、时间序列、平行坐标、网络图、维恩图、组合图、3D 等 |
| **智能辅助**     | 自动标签旋转、智能图例、布局优化、颜色对比度检查                                                                       |
| **3D 扩展**      | 支持 3D 曲面、等高线、3D 散点                                                                                          |
| **完整工作流**   | 从单图到多子图，从绘图到显著性标注，全链路覆盖                                                                         |
| **增强返回类型** | `PlotResult`、`GridSpecResult` 支持元组解包、属性访问、链式调用                                                        |

---

## 安装

```bash
# uv（推荐）
uv pip install sciplot-academic

# pip
pip install sciplot-academic

# ML 扩展（可选）
uv pip install sciplot-academic[ml]

# 全部扩展
uv pip install sciplot-academic[all]
```

### 扩展模块

```python
# 机器学习可视化
from sciplot._ext.ml import plot_pca, plot_confusion_matrix, plot_learning_curve

# 3D 可视化
from sciplot._ext.plot3d import plot_surface, plot_contour, plot_3d_scatter
```

---

## 快速上手

```python
import sciplot as sp
import numpy as np

x = np.linspace(0, 10, 200)

# 单线图 → 自动保存 PDF + PNG
fig, ax = sp.plot(x, np.sin(x), xlabel="时间 (s)", ylabel="电压 (V)")
sp.save(fig, "结果图")

# 多线对比 → 自动选 pastel-2
fig, ax = sp.plot_multi(x, [np.sin(x), np.cos(x)],
                       labels=["方法 A", "方法 B"])
sp.save(fig, "对比")

# 链式调用风格
sp.style("nature").palette("pastel").plot(x, np.sin(x)).save("链式调用示例")

# PlotResult 增强返回类型
result = sp.PlotResult(*sp.plot(x, np.sin(x)))
result.xlabel("时间 (s)").ylabel("电压 (V)").save("PlotResult示例")
```

---

## 核心功能

### 📊 图表类型

| 函数                                | 用途                         |
| ----------------------------------- | ---------------------------- |
| `plot()` / `plot_line()`            | 折线图                       |
| `plot_multi()`                      | 多线对比（自动配色）         |
| `plot_scatter()`                    | 散点图                       |
| `plot_step()`                       | 阶梯图（CDF/直方）           |
| `plot_area()` / `plot_multi_area()` | 面积图（支持堆叠）           |
| `plot_bar()`                        | 柱状图                       |
| `plot_grouped_bar()`                | **分组柱状图**（论文最常用） |
| `plot_stacked_bar()`                | 堆叠柱状图                   |
| `plot_horizontal_bar()`             | 水平柱状图                   |
| `plot_combo()`                      | 组合图（柱状+折线，双Y轴）   |
| `plot_box()`                        | 箱线图                       |
| `plot_violin()`                     | 小提琴图                     |
| `plot_histogram()`                  | 直方图                       |
| `plot_errorbar()`                   | 误差条                       |
| `plot_confidence()`                 | 置信区间                     |
| `plot_heatmap()`                    | 热力图                       |
| `plot_radar()`                      | 雷达图                       |
| `plot_timeseries()`                 | 时间序列图                   |
| `plot_parallel()`                   | 平行坐标图                   |
| `plot_residuals()` / `plot_qq()`    | 回归诊断图                   |
| `plot_network()`                    | 网络图                       |
| `plot_dendrogram()`                 | 层次聚类树状图               |
| `plot_venn2()` / `plot_venn3()`     | 维恩图                       |
| `annotate_significance()`           | 显著性标注（*/**/***）       |

### 🎨 配色方案

```
四大内置色系（推荐）：
  pastel    → 柔和粉彩（默认，6色）
  ocean     → 海洋蓝绿（6色）
  forest    → 森林渐变（6色）
  sunset    → 日落暖色（5色）

自定义配色：
  sp.set_custom_palette(["#E74C3C", "#3498DB"])  # 简单配色
  sp.register_color_scheme("mytheme", scheme)     # 完整配色方案
```

### 📐 期刊样式

| venue     | 尺寸 (英寸) | 适用场景            |
| --------- | ----------- | ------------------- |
| `nature`  | 7.0 × 5.0   | Nature/Science 双栏 |
| `ieee`    | 3.5 × 3.0   | IEEE 单栏           |
| `aps`     | 3.4 × 2.8   | APS Physical Review |
| `springer`| 6.0 × 4.5   | Springer 期刊       |
| `thesis`  | 6.1 × 4.3   | 学位论文            |

### 🔬 高级功能

```python
# 分组柱状图（论文最常见）
sp.plot_grouped_bar(groups=["A", "B", "C"],
                   data={"方法1": [1,2,3], "方法2": [2,3,4]})

# 堆叠柱状图
sp.plot_stacked_bar(categories=["A", "B", "C"],
                    data={"训练": [80,85,90], "验证": [10,8,5]})

# 组合图（柱状+折线，双Y轴）
sp.plot_combo(x=["Q1", "Q2", "Q3"],
              bar_data={"销量": [100,120,140]},
              line_data={"增长率": [0.1, 0.2, 0.15]})

# 显著性标注
sp.annotate_significance(ax, x1=1, x2=2, y=8.5, p_value=0.03)  # *

# 面板标签
sp.add_panel_labels(axes)  # (a) (b) (c)

# 智能辅助
sp.auto_rotate_labels(ax)      # 自动旋转标签
sp.smart_legend(ax, outside=True)  # 智能图例位置
```

---

## AI Agent 使用

本项目附带 **sciplot-skill** 文件，这是**默认绘图入口**，不是可选说明。只要用户在对话里提到画图、出图、可视化、图表、figure、plot、matplotlib、seaborn、plotly、论文插图、竞赛图或实验结果展示，就**先走这个 skill**。只有当用户明确要求不用 SciPlot，或需求明显超出本包能力时，才退回通用方案。

> 使用 SciPlot 技能时，请参考 [sciplot-skill/SKILL.md](./sciplot-skill/SKILL.md)。该文件包含完整的函数签名、场景选型速查和最佳实践规范。

> GitHub Copilot 的仓库级提示见 [`.github/copilot-instructions.md`](./.github/copilot-instructions.md)。

```python
# AI 生成脚本的标准结构
import sciplot as sp
import numpy as np

# 按 SKILL.md 规范生成代码
```

---

## 依赖

```
matplotlib >= 3.5.0
numpy >= 1.20.0
```

> v1.7 起，所有配色均为内置，**配色系统不依赖 SciencePlots**。
> 注：期刊样式渲染仍使用 SciencePlots（已随安装自动解决依赖）。

## 更新日志

### v1.8.0

- 新增 `plot_lollipop()` 棒棒糖图
- 新增 `plot_slope()` 斜率图
- 新增 `plot_density()` / `plot_multi_density()` 密度图
- 新增 `plot_scatter_matrix()` 散点矩阵图
- 新增 `earth` 色系（地形配色，6色）
- 新增 `rmb` 色系（人民币配色，5色）
- 新增 `diverging` 色系（发散配色，8色）
- 扩展配置系统：支持从 JSON/YAML 文件加载配置
- 优化 `PlotResult` 链式调用支持更多方法
- 新增 `adjust_subplots()` 布局微调工具
- 新增 `suggest_figsize()` 根据数据量建议图形尺寸
- 新增多语言支持：`list_languages()` 查看支持语言

### v1.7.4

- 新增 `PlotResult` 增强返回类型，支持元组解包、属性访问、链式调用
- 新增 `GridSpecResult` GridSpec 结果封装
- 修复 `save()` 函数递归创建嵌套目录问题
- 统一 `bar()` 和 `plot_bar()` 参数签名

### v1.7.0

- 新增配色方案系统 `register_color_scheme()`，支持单/双/三/四/五色自动选择
- 新增面积图 `plot_area()` / `plot_multi_area()`
- 新增堆叠柱状图 `plot_stacked_bar()`
- 新增水平柱状图 `plot_horizontal_bar()`
- 新增组合图 `plot_combo()`（柱状+折线，双Y轴）
- 新增 3D 可视化扩展模块 `_ext/plot3d.py`
- 新增智能辅助工具 `utils/smart.py`

---

## License

MIT © SciPlot Team
