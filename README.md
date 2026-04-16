# SciPlot Academic

**中文科研绘图库** — 基于 Matplotlib，专为中文论文场景优化

[![PyPI version](https://badge.fury.io/py/sciplot-academic.svg)](https://badge.fury.io/py/sciplot-academic)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 为什么选择 SciPlot？

| 特性 | 说明 |
|------|------|
| **零依赖配色** | 所有配色（pastel/earth/ocean/人民币）均为内置，无需 SciencePlots |
| **中文优化** | 默认宋体中文环境，IEEE 中文字号自动调优 |
| **论文级输出** | 预置 Nature/IEEE/Thesis 版心尺寸，Word/LaTeX 分辨率一键切换 |
| **智能配色** | ≤4 条线自动选 pastel-N 子集，支持自定义配色方案 |
| **丰富图表** | 折线、散点、柱状、分组/堆叠/水平柱状、面积、箱线、小提琴、热力图、组合图等 |
| **智能辅助** | 自动标签旋转、智能图例、布局优化、颜色对比度检查 |
| **3D 扩展** | 支持 3D 曲面、等高线、3D 散点 |
| **完整工作流** | 从单图到多子图，从绘图到显著性标注，全链路覆盖 |

---

## 安装

```bash
# pip
pip install sciplot-academic

# uv（推荐）
uv pip install sciplot-academic

# ML 扩展（可选）
uv pip install sciplot-academic[ml]
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
```

---

## 核心功能

### 📊 图表类型

| 函数 | 用途 |
|------|------|
| `plot()` / `plot_line()` | 折线图 |
| `plot_multi()` | 多线对比（自动配色） |
| `plot_scatter()` | 散点图 |
| `plot_step()` | 阶梯图（CDF/直方） |
| `plot_area()` / `plot_multi_area()` | 面积图（支持堆叠） |
| `plot_bar()` | 柱状图 |
| `plot_grouped_bar()` | **分组柱状图**（论文最常用） |
| `plot_stacked_bar()` | 堆叠柱状图 |
| `plot_horizontal_bar()` | 水平柱状图 |
| `plot_combo()` | 组合图（柱状+折线，双Y轴） |
| `plot_box()` | 箱线图 |
| `plot_violin()` | 小提琴图 |
| `plot_histogram()` | 直方图 |
| `plot_errorbar()` | 误差条 |
| `plot_confidence()` | 置信区间 |
| `plot_heatmap()` | 热力图 |
| `annotate_significance()` | 显著性标注（*/**/***） |

### 🎨 配色方案

```
三大常驻色系（推荐）：
  pastel    → 柔和粉彩（默认）
  earth     → 大地色系
  ocean     → 海洋蓝绿

人民币系列：100yuan / 50yuan / 20yuan / 10yuan / 5yuan / 1yuan

自定义配色：
  sp.set_custom_palette(["#E74C3C", "#3498DB"])  # 简单配色
  sp.register_color_scheme("mytheme", scheme)     # 完整配色方案
```

### 📐 期刊样式

| venue | 尺寸 (英寸) | 适用场景 |
|-------|-------------|----------|
| `nature` | 7.0 × 5.0 | Nature/Science 双栏 |
| `ieee` | 3.5 × 3.0 | IEEE 单栏 |
| `thesis` | 6.1 × 4.3 | 学位论文 |

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
              line_data={"增长": [5,8,12]})

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

本项目附带 **SKILL.md** 文件，AI Agent（如 Claude、Cursor）可直接调用：

> 使用 SciPlot 技能时，请参考项目根目录的 `SKILL.md` 文件。该文件包含完整的函数签名、场景选型速查、最佳实践规范。

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

> v1.6 起，所有配色均为内置，**不再依赖 SciencePlots**。

## 更新日志

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
