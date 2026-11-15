# SciPlot 数据驱动选型决策指南（Data-First Chart Selection）

> 目的：**先看数据结构再决定图形，彻底告别“无论什么数据都画普通柱状图 / 普通折线图 / 裸箱线图”。**
> 结合感知通道精度排序、安斯库姆防陷阱规范与科研单轴多层融合设计原则整理。

---

## 阶段 0：不可跳过的选图前硬检（干 0）

在写任何绘图代码前，先运行 `sp.recommend_charts(data)`（或 `uv run python .claude/skills/sciplot/scripts/profile_and_recommend.py <data>`）完成 4 项检查：

1. **分布先于汇总（Anscombe 防线）**：同一均值 ± 标准差可以对应单峰正态、双峰撕裂或极端离群长尾。绝不在未检验样本量、偏态 (`skewness`)、异常值率前用普通均值柱状图下结论。
2. **明确核心问题（主任务）**：一张图只服务一个核心论点——**对比 (Comparison)**、**分布 (Distribution)**、**关系 (Relationship)**、**构成/排名 (Composition/Ranking)**、**演化预测 (Trend/Forecast)**、**高维结构 (Multivariate)** 或 **模型诊断 (Evaluation)**。若同时要证明两件事，用多面板 `hero_layout` 或 `paper_subplots` 拆分，而不是硬挤进同坐标系。
3. **误差与置信口径检验**：涉及抽样估计与测量波动时（非全量确定性普查），必须呈现分布散度或区间（SD / SE / 95% CI / 分位数带），并在轴标题或图注写出准确口径。
4. **反单调检验**：对照下方的《单调默认退化 → 科研高表现力升级矩阵》，只有当最简基础图确属全局最佳时才能采用，并在交付中说明至少一个淘汰候选的理由。

---

## 阶段 1：数据形态快速分流（干 1）

| 数据形态 (`shape_pattern`) | 关键识别信号 | 禁止退化的惯性错误 | SciPlot 首选推荐池 |
|---|---|---|---|
| **多组原始观测** (`grouped_samples`) | 2~5 组连续测量、`n >= 15`/组 | 只画均值柱+误差棒、只画空白箱线图 | **`plot_raincloud`**（半提琴+IQR+原始点）、`plot_violin(..., show_box=True, show_points=True)`、`plot_beeswarm`（小样本）、`plot_ridgeline`（5~16 组） |
| **前后配对观测** (`paired_before_after`) | 同批被试前/后成对两列、`before/after` | 当成独立样本画并排均值柱状图 | **`plot_paired`**（个体轨迹连线 + 涨跌双色 + 均值斜率 + p 值）或 `plot_dumbbell` |
| **类别 × 聚合标量** (`category_scalar`) | 含正负增减、非负贡献构成、或 >=5 类排名 | 不排序直接竖排密挤柱状图、带正负仍混用单色竖柱 | 正负对比→**`plot_diverging_bar`**；关键少数归因→**`plot_pareto`**；纯排名→**`plot_lollipop(..., orientation="h", sort=True)`**；百分比结构→**`plot_waffle`** |
| **双变量连续关系** (`bivariate`) | 两列连续数值、检查线性/非线性/集群 | 大样本 (>800) 直接画实心黑散点糊成一团 | 中小样本→**`plot_marginal`** 或 **`plot_scatter(..., fit_line=True, show_stats=True)`**；大样本 (`n>=800`)→**`plot_hexbin`** |
| **相关矩阵 / 方阵** (`square_corr`) | 对称阵、对角线=1、取值 `[-1, 1]` | 完整对称矩阵满画冗余双倍格子 + 使用单向 `Blues`/`viridis` 色标 | **`plot_heatmap(..., triangle="lower", cmap="RdBu_r", vmin=-1, vmax=1, p_values=...)`**、`plot_clustermap`、`plot_bubble_heatmap` |
| **时间 / 过程演化** (`timeseries`) | 时间列或单调步骤列 | `>= 5` 条曲线全部叠画同一轴变成“意面图 (Spaghetti)” | `<=4` 条→`plot_multi_timeseries`；`>=5` 条→`paper_subplots(..., sharex=True, sharey=True)` 分面 / `plot_bump` / `plot_streamgraph`；预测不确定性→**`plot_fan`** |
| **高维多特征表** (`multivariate`) | `>=4` 列连续数值特征 | 拆成 5 张互不关联的单柱状图或只挑最显著的一对画散点 | **`plot_scatter_matrix(..., upper="corr", diag="kde")`**、`plot_pca(..., show_ellipse=True)`、`plot_parallel` |
| **二分类评估 / 领域专图** (`domain_specific`) | `0/1` 标签 + 连续概率；`log2FC+pvalue`；`effect+ci_low/ci_high`；`source+target` | 仅画 1 张 Accuracy 柱状图对比模型 | **`plot_roc`（ROC/PR）+ `plot_calibration`**、`plot_volcano(..., show_counts=True)`、`plot_forest`、`plot_sankey` |

---

## 阶段 2：感知编码精度与反单调准则（干 3）

### 感知精度排序（从高精度到底层概览）
1. **统一尺度与公共基线上的位置**（散点图、棒棒糖终点、森林图、配对折线端点）→ 需要精确数值比较时首选
2. **统一零基线的长度**（柱状图、水平条形图、发散条形图）→ **条形必须从 0 起算**，需要比绝对值微差时勿随意截断坐标轴
3. **方向 / 斜率**（斜率图 `plot_slope`、个体配对图 `plot_paired`、趋势折线）
4. **面积与密度**（华夫格 `plot_waffle` 优于饼图角度比较、气泡图 `plot_bubble` 仅传达量级）
5. **色彩明度与色相**（`make_palette_cmap` 连续渐变表示高低；高分离定量/分类配色表示类属，超过 4 类务必叠加线型 `use_linestyles=True` 或 marker + 白色描边）

### 单轴多图层融合与复合材料叙事（`vivid-illustration` 核心法则）
- **单轴 2–3 层互补叠加**（无需多建空白子图也能成倍提高信息密度）：
  - **分布三层**：半透明柔和底色填充 KDE + 深炭 IQR 胶囊箱线 + 带白边原始数据点（即 `sp.plot_raincloud` / `sp.plot_violin(..., show_box=True, show_points=True)`）
  - **关系四层**：带白边半透明散点 + 对比色 OLS 拟合线 + 95% 置信阴影带 + 稀疏象限自动停靠的 `r / R² / p / n` 卡片（即 `sp.plot_scatter(..., fit_line=True, ci=True, show_stats=True)`）
  - **矩阵两层**：下三角遮蔽冗余格 + 发散色彩格 + 单元格白色细缝 + 原生相关系数与显著性星号 `*/**/***`（即 `sp.plot_heatmap(..., triangle="lower", p_values=...)`）
  - **复合 Hero 版式**：用 `sp.hero_layout("hero_left")` 或 `sp.hero_layout("hero_right")` 实现 **“主机制 / 核心全景图（1 大面板） + 机制验证/亚组分布/相关分解（2 卫星面板）”**，彻底打破呆板的均分四宫格审美疲劳。

---

## 阶段 3：绝对禁例清单（交付前逐项核对）

- 禁止将 **两列完全不同物理量纲且无累积占比关系的序列** 强制画在同一双 Y 轴图上（`plot_pareto` 的次数+累积百分比和 `plot_combo` 的明确归因对照除外，不确切可比时用 `paper_subplots(2, 1, sharex=True)` 拆分）。
- 禁止用 **多组均值柱状图 + 单边须线** 掩盖小样本多峰、偏斜分布或配对个体异向波动。
- 禁止使用 **连续渐变或红绿高饱和撞色** 区分离散互斥类别（有正负零点才用发散双色）。
- 禁止在未检查 `sp.audit_figure(fig, check_visual_guards=True)` 且未实际打开 PNG 图片审视之前宣布绘图完成。
