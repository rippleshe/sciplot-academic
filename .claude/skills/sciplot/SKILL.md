---
name: sciplot
description: >-
  SciPlot Academic 科研绘图与论文插图工作流。用户要求画科研图、论文图、实验结果图、
  统计图、多面板图、期刊投稿图，或需要优化现有 matplotlib 科研图时触发；也适用于
  “这些数据怎么可视化”“把图做得像顶刊”“提升论文图质量”等未指定图型的任务。
  优先使用项目内 sciplot API 完成静态科研可视化；明确要求交互式网页图、地图或动画时不触发。
version: 2.0.1
author: rippleshe
user-invocable: true
allowed-tools: "Read Write Edit Bash Glob Grep"
---

# SciPlot Academic — publication figure workflow

这个 Skill 的目标不是“调用一个画图函数”，而是把数据变成**语义正确、视觉克制、可复核、可投稿**的科研图。

## 1. 先判断，不要急着画

先回答四个问题：

1. **图要证明什么？** 趋势、差异、分布、相关、构成、流向、模型诊断还是机制流程？
2. **数据是什么结构？** 连续/类别/时间/矩阵/网络/层级/多阶段流；是否有重复测量、误差或显著性？
3. **使用场景是什么？** `nature` / `ieee` / `thesis` / `presentation`，中文还是英文？
4. **读者第一眼应该看到什么？** 主结论必须比装饰、网格、背景、次要系列更抢眼。

不要为了“高级”选择复杂图型。普通折线、散点、箱线、森林图如果更准确，就优先用它们。

## 2. 图型选择

常用入口：

| 研究问题 | 首选 |
|---|---|
| 单/多组趋势 | `sp.plot()` / `sp.plot_multi()` |
| 两连续变量关系 | `sp.plot_scatter()`；高密度用 `sp.plot_hexbin()` |
| 分类数值比较 | `sp.plot_bar()` / `sp.plot_grouped_bar()` |
| 前后/两条件变化 | `sp.plot_dumbbell()` |
| 分布与原始点 | `sp.plot_raincloud()` / `sp.plot_beeswarm()` |
| 经典分布摘要 | `sp.plot_box()` / `sp.plot_violin()` |
| 矩阵/相关性 | `sp.plot_heatmap()` / `sp.plot_bubble_heatmap()` |
| 模型比较与不确定性 | `sp.plot_errorbar()` / `sp.plot_forest()` / `sp.plot_taylor()` |
| 组成占比 | `sp.plot_treemap()` / `sp.plot_donut()` / `sp.plot_waffle()` |
| 排名变化 | `sp.plot_bump()` / `sp.plot_circular_barplot()` |
| 多阶段流动 | `sp.plot_sankey()` / `sp.plot_alluvial()` |
| 层级构成 | `sp.plot_sunburst()` |
| 网络结构 | `sp.plot_network()` / `sp.plot_network_communities()` |
| 多组分 | `sp.plot_ternary()` |
| 多维性能 | `sp.plot_radar()`，但维度少且尺度一致时才用 |
| 多面板论文图 | `sp.figure_panels()` + 各绘图 API |

完整函数表和参数细节按需读取 `references/full-api.md`；常见组合范式读取 `references/recipes.md`；配色与视觉语义读取 `references/color-style.md`。不要把整个参考文件无差别读入上下文，只读当前任务需要的部分。

如果参考文档与实际安装版本冲突，以运行时为准：

```python
import inspect
import sciplot as sp
print(sp.__version__)
print(inspect.signature(sp.plot_scatter))
```

## 3. 默认工作流

### Step A — 建立样式

```python
import sciplot as sp
sp.setup_style("nature", palette="ocean", lang="en")
```

常用场景：

- 英文期刊：`nature` 或 `ieee`，优先 PDF/SVG。
- 中文论文/学位论文：`thesis`, `lang="zh"`。
- PPT/答辩：`presentation`，PNG 300 dpi 足够。
- 不要因为用户没指定，就默认深色、渐变背景、玻璃拟态、阴影卡片。

### Step B — 画主图

高层 `plot_*` 默认返回 `PlotResult`，可以继续拿 `fig` / `ax` 做最后 10% 的定制：

```python
result = sp.plot_scatter(x, y, xlabel="Dose (mg)", ylabel="Response")
fig, ax = result
```

优先调用 SciPlot 已有参数，而不是在外面重复造一套 matplotlib 样式。

### Step C — 只做有意义的收尾

可以做：参考线、置信区间、少量重点标注、轴范围、科学计数法、共享图例、面板标签。

不要做：无意义标题、厚重外框、强网格、每个点都标数值、彩虹色、3D 化普通柱状图、为了“高级感”堆渐变和阴影。

### Step D — 审计

```python
report = sp.audit_figure(fig, verbose=True)
```

至少检查：

- 轴标签和单位是否完整；
- 字号是否到出版下限；
- 多面板是否有 `(a)(b)(c)`；
- 图例是否遮挡数据；
- 色彩是否仅承担必要语义；
- 误差条/CI/显著性是否与数据和方法一致；
- 轴截断是否可能误导比较。

### Step E — 保存并真正看图

```python
sp.save(fig, "figures/fig1", formats=("pdf", "png"), dpi=600)
```

生成后必须打开 PNG 做视觉检查。**测试通过不等于图好看。**重点看：留白、主次、标签碰撞、图例位置、色条、极端值、小屏缩放、中文字体和多面板对齐。发现问题优先修通用实现，而不是只在 showcase 脚本里遮住。

## 4. 科研绘图的硬规则

### 数据语义优先

- 不篡改数据，不为了好看删异常值。
- 柱高、面积、颜色、点大小等编码必须与真实量对应。
- 误差条必须知道是 SD、SE、CI 还是其他量；不知道就不要代填。
- 显著性标记必须来自真实统计检验，不能凭均值差距画星号。
- 时间序列保持时间顺序；类别排序要有理由（数值、实验顺序或自然顺序）。

### 颜色是信息，不是装饰

- 2–5 个离散系列优先使用少量、可区分的颜色。
- 连续量用连续色图；有正负中心时用发散色图。
- 同一语义跨面板保持同色。
- 强调项用一个主色，其余可以降饱和或中性化。
- 不把不同类别全部做成高饱和“糖果色”。
- 需要色盲安全时使用 `sp.check_colorblind_safe()` / `sp.audit_palette()`。

### 线、点、字要有层级

- 数据线 > 辅助线 > 网格。
- 主方法可以加粗或提高 z-order；不要同时加粗、放大、换色、加阴影四重强调。
- 大散点样本降低 alpha 或改 hexbin；小样本保留真实点更重要。
- 标题不是必须。论文图通常由 caption 承担完整说明。
- 密集自动标注必须在最终坐标变换后用 renderer 检查真实像素碰撞；空间不够时宁可少标或省略，也不要让文字越界、压住图例或互相覆盖。

### 多面板图必须统一

优先：

```python
fig, axes = sp.figure_panels(2, 2, venue="nature", panel_labels=True)
```

保持同类面板的轴范围、单位、字体、图例、配色语义一致。共享坐标轴时减少重复标签。不要把每个 panel 做成不同风格的独立海报。

## 5. 不同图型的高质量下限

- **折线**：时间/有序 x 才连接；多系列必要时叠加线型，避免只靠颜色。
- **散点**：点重叠时降低 alpha/size；样本很大时考虑 hexbin；回归线必须说明模型。
- **柱状**：默认从零基线；长类别名优先水平条形；组数过多不要堆几十种颜色。
- **箱线/小提琴/雨云**：样本不大时尽量展示原始点；不要让小提琴形状掩盖 n 很小的事实。
- **热力图**：色图必须匹配语义；相关矩阵优先以 0 为中心的发散色；标数字时保证对比度。
- **雷达**：只用于少量同尺度维度；多组填充 alpha 要低，轮廓承担主要比较。
- **Sankey/Alluvial**：流带宽度是真实量；颜色应跟随源/类别语义，流多时先过滤视觉噪音。
- **Treemap/Sunburst**：面积/角度承担数值，颜色用于层级或分组，不再额外编码无关变量。
- **网络图**：先减少边噪音和标签密度，再谈配色；社区结构应该一眼可辨。
- **3D**：只有数据本身存在第三空间维度或曲面结构时使用，普通分类比较不要 3D。

## 6. Showcase 与包开发时的额外要求

如果任务是改 SciPlot 本身，而不只是调用它：

1. 先跑基线测试，再改代码。
2. 遇到难看的 showcase，要追到绘图实现；不要只换一组更“配合”的数据。
3. 新增/修复 API 后补回归测试，特别关注 palette、NaN/Inf、空输入、长度错配、辅助 Axes、多面板和保存。
4. 修改全局样式后，重新运行受影响 showcase 并目视检查。
5. 运行 `ruff`、`mypy`、`pytest`；能跑全量就跑全量。
6. 不用截图“证明”代码正确，也不用测试通过“证明”视觉优秀——两种证据都需要。

## 7. 交付标准

一次合格的科研绘图任务应交付：

- 可复现脚本；
- 实际生成的图；
- 清楚的轴标签/单位/统计语义；
- 与目标媒介匹配的格式和 dpi；
- 通过必要的 figure audit；
- 至少一次真实视觉检查。

当用户说“做得更像 Nature/Science/顶刊”时，不要理解成复制某一家期刊的装饰风格。真正要提高的是：**信息层级、排版纪律、数据墨水比、可读性、统计表达和跨图一致性。**
