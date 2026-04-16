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
| **智能配色** | ≤4 条线自动选 pastel-N 子集，无需手动指定 |
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
| `plot_bar()` | 柱状图 |
| `plot_grouped_bar()` | **分组柱状图**（论文最常用） |
| `plot_box()` | 箱线图 |
| `plot_violin()` | 小提琴图 |
| `plot_histogram()` | 直方图 |
| `plot_errorbar()` | 误差条 |
| `plot_confidence()` | 置信区间 |
| `plot_heatmap()` | 热力图 |

### 🎨 配色方案

```
三大常驻色系（推荐）：
  pastel    → 柔和粉彩（默认）
  earth     → 大地色系
  ocean     → 海洋蓝绿

人民币系列：100yuan / 50yuan / 20yuan / 10yuan / 5yuan / 1yuan

自定义：sp.set_custom_palette(["#E74C3C", "#3498DB"])
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
                   data=[[1,2,3], [2,3,4], [3,4,5]],
                   labels=["方法1", "方法2"])

# 显著性标注
sp.annotate_significance(ax, x1=1, x2=2, y=8.5, p_value=0.03)  # *

# 面板标签
sp.add_panel_labels(axes)  # (a) (b) (c)
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

---

## License

MIT © SciPlot Team
