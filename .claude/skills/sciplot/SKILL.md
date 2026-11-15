---
name: sciplot
description: >-
  SciPlot Academic 科研绘图与数据驱动选型工作流。用户要求画科研图、论文插图、
  实验对比图、多面板论文图，提供 CSV/Excel/DataFrame 数据问“该画什么图”，
  或需要提升图表发表品质、排查视觉缺陷时触发。先完成数据画像与反单调图型选型，
  再使用 sciplot 高频视觉增强 API 生成可投稿图像。明确要求交互式网页图或地图时除外。
version: 3.0.0
author: rippleshe
user-invocable: true
allowed-tools: "Read Write Edit Bash Glob Grep"
---

# SciPlot Academic — Data-Driven Publication Figure Workflow

本 Skill 的核心原则：**先体检数据、再按感知精度与信息融合度决策选型、然后调用内置视觉守卫的 `sciplot` API 出图，绝不允许把任何数据都千篇一律拍成最简柱状图、空白箱线图或杂乱多折线。**

---

## Step 0 — 强制先做数据画像体检（Data Profiling Gate）

在写任何绘图代码前，必须先观察用户数据的真实形态与结构（变量数、样本量 `n`、偏度、异常值、正负方向、对称矩阵/配对/时序/二分类信号等）：

```python
import sciplot as sp

# 1. 支持 DataFrame / dict / ndarray / group list / CSV / Excel / JSON 路径
report = sp.recommend_charts(data, goal="auto", top_k=4)
print(report.summary())
```

或直接在命令行运行辅助脚本快速诊断数据文件：

```bash
uv run python .claude/skills/sciplot/scripts/profile_and_recommend.py data.csv --goal auto --top-k 4
```

如未直接拿到数据文件、仅凭任务描述设计图表，先列出假设的样本量、分组数和字段类型，再进入 Step 1。

---

## Step 1 — 反单调选型与候选比较（Chart Selection Gate）

拿到画像后，查阅 `references/chart-selection.md`，严格按 **“数据形态 → 主任务 → 感知通道精度 → 单轴多层融合”** 比较 **≥ 2 个候选图型**，禁止无理由直接退化到最简图：

| 常见平庸退化图（禁止默认） | 触发升级条件 | 推荐高信息密度图型与 SciPlot API |
|---|---|---|
| 普通单组/分组柱状图 | 仅是原始多次观测分布均值，未证明正态无双峰 | **`sp.plot_raincloud()`** 或 **`sp.plot_violin(..., show_box=True, show_points=True)`** |
| 独立两组并排柱状图 | 同批被试干预前 vs 干预后配对数据 | **`sp.plot_paired(before, after)`** 或 `sp.plot_dumbbell()` |
| 空白箱线图 `boxplot` | `n <= 40`/组或需看清多峰与异常样本密度 | **`sp.plot_raincloud()`** / `sp.plot_box(..., show_points=True, show_means=True)` |
| 裸散点图 | 检查线性趋势或大样本过饱和重叠 | 中小样本用 **`sp.plot_marginal()`** / `sp.plot_scatter(..., fit_line=True, show_stats=True)`；大样本 (`n>=800`) 用 **`sp.plot_hexbin()`** |
| 无序竖柱图 | 类别 >=5、正负增减并存、或非负归因排序 | 正负项→**`sp.plot_diverging_bar()`**；核心少数归因→**`sp.plot_pareto()`**；排名→`sp.plot_lollipop(sort=True)` |
| 全阵单色相关性热图 | 对称相关矩阵 | **`sp.plot_heatmap(..., triangle="lower", cmap="RdBu_r", vmin=-1, vmax=1, p_values=...)`** |
| 多条线拧成“意面图” | 时序系列 `>= 5` 条 | **`sp.paper_subplots(nrows, ncols, sharex=True, sharey=True)`** 分面 / `sp.plot_bump()` / `sp.plot_streamgraph()` |
| 多面板均分网格 | 存在 1 个核心主结论 + 2 个支撑维度 | **`sp.hero_layout("hero_left")` / `hero_layout("hero_right")`** |
| 模型准确率单一柱图 | 含二分类概率预测或回归残差 | **`sp.plot_roc()` + `sp.plot_calibration()`**（多模型同时比AUC、ECE与Brier） |
| 单一折线未来展望 | 含多条预测轨迹或分位数不确定区间 | **`sp.plot_fan(..., samples=..., history_x=..., history_y=...)`** |

> **选型产出自检**：向用户输出脚本前，先简要写明：**① 数据关键画像特征 → ② 为什么选主方案 → ③ 至少 1 个为什么不画普通柱/线/裸箱的淘汰理由。**

---

## Step 2 — 确定配色语义与期刊版式

详细色值与搭配表按需阅读 `references/color-style.md`；函数细节与完整参数速查 `references/full-api.md`；典型组合模板参考 `references/recipes.md`。

1. **期刊样式与字号基线**（绝对不在业务脚本中手搓 matplotlib 全局 `rcParams`）：
   - 英文投稿：`sp.setup_style("nature", palette=..., lang="en")` 或 `"ieee"`（导出 PDF + PNG 600 dpi）。
   - 中文学位/期刊论文：`sp.setup_style("thesis", palette=..., lang="zh")`（导出 PNG 1200 dpi 或 SVG）。
   - 幻灯/汇报：`sp.setup_style("presentation", palette=..., lang="zh")`（可按需搭配 `theme="dark"`）。
2. **配色首选原则**：
   - 离散对比优先使用 **vivid-illustration 精选高分离配色**：`blue-sky`（清晰商务/通用对比）、`coral-teal`（强对立双组/正负干预）、`olive-apricot`（自然学术 7 色）、`soft-forest`（生态生信）、`ocean-breeze`（时序演化）、`blue-pink`、`pastel-girl`，或者经典内置 `pastel` / `earth` / `ocean` / `forest` / `sunset`。
   - 有零点中心的矩阵/差异量必须用发散色图（`cmap="RdBu_r"`、`cmap="rdbu"` 或 `sp.make_palette_cmap("coral-teal", kind="diverging")`），绝不把顺序渐变直接画负相关。
   - 多系列线/散点超过 3 组时开启冗余编码（`use_linestyles=True` 或结合白色描边 + 不同 marker）。
   - 色盲安全关键发表图运行 `sp.check_colorblind_safe()` / `sp.audit_palette()`。

---

## Step 3 — 构建高质量图表与局部精细护卫

1. **优先利用 SciPlot 内置多层视觉增强参数**，不再于外部手画混乱补丁：
   - 散点分析自带回归线 + 95% 置信带 + 稀疏角统计卡：`sp.plot_scatter(x, y, fit_line=True, ci=True, show_stats=True)`
   - 分组柱自动配深轮廓、误差棒与柱顶标值：`sp.plot_grouped_bar(groups, data, errors=errs, show_values=True)`
   - 小提琴内嵌深色 IQR 胶囊与散点：`sp.plot_violin(groups, show_box=True, show_points=True)`
   - 直方图融合平滑核密度与中位线：`sp.plot_histogram(vals, show_kde=True, show_median=True)`
   - 火山图统计计数图例与防重叠引导线：`sp.plot_volcano(fc, p, labels=genes, show_counts=True)`
   - 相关矩阵去重下三角与显著性星号：`sp.plot_heatmap(corr, triangle="lower", p_values=pmat, cmap="RdBu_r", vmin=-1, vmax=1, show_values=True)`
   - PCA 降维自带 95% 置信椭圆：`sp.plot_pca(X, labels=groups, show_ellipse=True)`
2. **自定义 Matplotlib Axes 子图时的视觉护卫工具**（当使用 `sp.paper_subplots` / `sp.hero_layout` 手动在某个 `ax` 绘制多层细节时）：
   - `sp.polish_axis(ax, categorical_axis="x", clean_spines=True, grid="y")`: 清除分类轴锯齿次刻度、启用出版级 L 形极简边框与轻量化网格（绝不修改全局 `rcParams`）。
   - `sp.style_patch_edges(patches, colors)`: 为自定义柱条/多边形赋予“柔和填充 + 同色系加深边框”。
   - `sp.smart_labels(ax, texts, anchor_xy=pts, add_connectors=True)`: 基于像素 bbox 自动推开密集重叠文本并绘制微细引导线。
   - `sp.truncate_tick_labels(ax, axis="y", max_len=24)` 与 `sp.auto_rotate_labels(ax)`：防止长类别标签挤压或互撞。

---

## Step 4 — 投稿质量审计 + 必须真正看图交付

```python
report = sp.audit_figure(fig, check_visual_guards=True, verbose=True)
paths = sp.save(fig, "figures/fig1", formats=("pdf", "png"), dpi=600)
```

保存后**必须真实打开生成的 PNG（如通过图片读取工具查看）进行逐项核对**——pytest 通过不等于图好看：

- **信息清晰度**：主结论是否在第一视觉焦点？是否被过粗网格、阴影、无意义背景框遮盖？
- **文本与碰撞**：轴标签和单位是否完整？长标签、数字标记、图例、火山/散点标签或色条之间是否有任何穿插压盖？
- **坐标规范**：柱条是否从 0 基线开始？分类 X/Y 轴是否已被净化为无锯齿小次刻度？多面板是否有清晰一致的 `(a)(b)(c)` 标签？
- **发现缺陷根因修复**：若在开发包功能时发现某默认视图丑陋或布局失效，优先排查 `sciplot` 函数通用逻辑，而非只改数据掩饰。

---

## 参考资料导航（按需读取，勿一次性全读）

- `references/chart-selection.md` — 科研数据形态决策表、感知精度排序、反单调升级矩阵、单轴/Hero 融合策略
- `references/color-style.md` — vivid-illustration 精选配色、内置/人民币/发散配色、`make_palette_cmap`、视觉护卫工具及配置优先序
- `references/recipes.md` — 论文级即用场景配方（单图、云雨/提琴、帕累托、配对轨迹、ROC/校准、预测扇形、下三角相关矩阵、Hero 复合版式）
- `references/full-api.md` — 全量函数最新签名与参数细节（冲突时以运行时 `inspect.signature(sp.<fn>)` 为准）
- `scripts/profile_and_recommend.py` — 对 CSV/Excel/JSON/Parquet 或演示形态运行一键数据画像与图型推荐
