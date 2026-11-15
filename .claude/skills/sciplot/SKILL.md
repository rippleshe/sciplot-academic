---
name: sciplot
description: >-
  科研与竞赛级学术可视化技能（v4.0.0）。基于数据画像自动匹配最优图表形态，拒绝千篇一律的基础柱状图/箱线图/折线图。
  凡涉及画图、出图、科研配图、学术图表、数据可视化、探索性分析、模型评估、论文排版（Nature/IEEE/APS/Springer/学位论文）或美化 matplotlib/seaborn 图表时立即使用。
---

# SciPlot Academic — 数据驱动的高下限科研绘图规范 (v4.0.0)

> **核心铁律**：严禁不看数据结构就盲目画简单柱状图、裸箱线图或乱线折线图！  
> **首要动作**：拿到任何数据（DataFrame / dict / CSV / ndarray）或可视化需求，**先画像、走决策树、防误导，再选高信息密度图表并应用视觉守卫。**

---

## 0. 环境与执行约定

- **Python 环境**：优先使用 `uv run python ...` 运行脚本或检查数据。
- **即刻画像脚本**（强烈建议拿到数据文件时第一时间调用）：
  ```bash
  uv run python .claude/skills/sciplot/scripts/profile_and_recommend.py <data.csv> --goal auto
  ```
  或在 Python 中调用：
  ```python
  import sciplot as sp
  report = sp.recommend_charts(data, goal="auto")
  print(report.summary())
  ```

---

## 一、强制四步工作流（拒绝千篇一律）

### Step 1：数据画像与前置检验（Mandatory Profiling，对应 DT-01）
在动笔写任何绘图代码前，必须检查：
1. **变量结构**：连续列 / 离散分类列 / 时间列 / 二元列 / 组别嵌套列 (`grouped_samples` vs `two_factor_samples` vs `category_scalar` vs `method_metric_matrix`)。
2. **分布特征**：样本量 $n$（每组是否 $\ge 15$？是否 $\ge 300$ 需防过绘制？）、偏度（$|\text{skew}| \ge 1.5$ 禁用裸均值±柱状图）、是否跨 $\ge 2$ 个数量级（需显式对数坐标）。
3. **领域信号**：是否有 `actual`/`y_true` + `pred`/`y_pred`（回归全诊断）、`low`/`high` + `baseline`（敏感性分析）、`log2FC` + `pvalue`（火山图）、`ci_low`/`ci_high`（森林图）、`before`/`after`（配对）、`y_true` + 概率（ROC/校准）。
4. **Anscombe 检验 (DT-01)**：永远先画真实分布或散点，不凭汇总均值/相关系数下结论。

### Step 2：走 `干0–干9` 决策树 & 感知阶梯 (`VR-B1`) 选型
按照人眼感知精度从高到低匹配编码通道：**统一位置 > 长度 > 方向/斜率/角度 > 面积 > 体积 > 明度/饱和度 > 色相**。  
根据 [references/chart-selection.md](references/chart-selection.md) 与 `sp.recommend_charts()` 优先挑选高信息密度图表：

| 数据场景 | 禁止使用的低效默认图 | 首选高表现图表（SciPlot 函数） |
|---|---|---|
| 单因素多组分布 ($n \ge 15$/组) | 均值±误差柱、裸箱线图 | `plot_raincloud`（半提琴+箱线+点） / `plot_violin(..., show_box=True, show_points=True)` |
| **双因素交互分布（组×阶段/亚组）** | 仅看均值的分组柱状图 | **`plot_grouped_violin`**（并排双因素小提琴+IQR 胶囊+白点中位数） |
| 小样本分组分布 ($n < 15$/组) | 强行 KDE 小提琴 | `plot_beeswarm`（真实点分布+中位线） / `plot_paired`（若前后配对） |
| $\ge 5$ 组分布横向扫描 | 并排超宽箱线/柱图 | `plot_ridgeline`（山脊重叠 KDE） |
| **两组在多项非负指标上的对称对比** | 拥挤并排细柱图 | **`plot_back_to_back_bar` (`mirror_bar`)**（中心零轴镜像条 + $\Delta$ 徽章）/ `plot_dumbbell` |
| **多方法 × 多指标跨量纲对比表** | 强拼同一 Y 轴的分组柱图 | **`plot_method_heatmap`**（独立方向列归一化 + 真实值 + `#1` 冠军金框 + `Overall`） |
| **模型预测 vs 真实值回归评价** | 单一 $R^2$/RMSE 柱状图 | **`plot_residual_diagnostics`**（2×2 四象限：残差齐性 + Normal Q-Q 95% CI + 残差分布 + ACF） |
| **参数敏感性 / 扰动幅度分析** | 无基准对称的普通条图 | **`plot_tornado`**（基准零线双向摆幅排序 + 斑马底纹） |
| 多项净变化对比 (正/负双向) | 单向柱图混合正负 | `plot_diverging_bar` / `plot_waterfall`（分解增减瀑布） |
| 关键少数贡献 / 类别排名 ($k \ge 5$) | 无序竖柱图（标签斜挤） | `plot_pareto`（80% 累积线） / `plot_lollipop(..., orientation="h")` |
| 双变量连续关系 ($n \ge 300$) | 纯实心默认点（严重 Overplotting） | `plot_hexbin(bins="log")` / `plot_marginal(..., marginal="kde")` / `plot_scatter(..., fit_line=True)` |
| 高维表格 ($\ge 4$ 连续列) | 挑 1-2 对分散散点 | `plot_scatter_matrix(upper="corr", diag="kde")` / `plot_pca` / `plot_parallel` / `plot_heatmap(..., triangle="lower")` |
| 多序列时序 ($\ge 5$ 条) | 纠缠“意面式多线图” | `paper_subplots(..., sharex=True, sharey=True)` 分面 / `plot_bump(..., highlight=...)` / `plot_streamgraph` |

### Step 3：美学增强与聚焦叙事 (`VR-B4 Start-from-Grey`)
1. **高对比配色**：优先使用 `vivid` 系列高对比配色（`coral-teal`, `blue-sky`, `olive-apricot`, `ocean-breeze`, `okabe-ito`）。顺序值选用单调递增顺序色（如 `YlGnBu`, `viridis`），正负偏差选用以白为界的发散色（`RdBu_r`）。
2. **Start-from-Grey（焦点唯一突出，VR-B4）**：多方法或多系列对比中，使用：
   ```python
   cols = sp.make_highlight_palette(n_series=4, highlight_idx=3, palette="coral-teal")
   ```
   将对照组退居微梯度浅灰、仅赋予目标/Ours 组饱和主色，大幅增强前注意视觉聚焦。
3. **自动下限守卫**：SciPlot 绘图函数已内置 `polish_axis`（去顶部/右侧脊线、柔和 `#5A6270` 脊线与 `#CBD5E1` 浅虚线网格、默认清理连续轴噪声次刻度）、`style_patch_edges`（半透明填色+微深轮廓边）、`smart_marker_style`（随样本量缩点降透+白边+自动栅格化）、`layered_fill_between`（分层渐透填充）与 `repel_panel_labels`（复合子图编号防遮挡）。

### Step 4：9 维审稿质检 (`VR-A ~ VR-I`) 与出图验证
保存图像前执行质量审计与自查：
```python
report = sp.audit_figure(fig, check_visual_guards=True)
sp.save(fig, "figure_out", formats=("png", "pdf"), dpi=600)
```
完成后务必检查生成图：
- **VR-A/B**：任务与编码通道是否精准？有无低精度渠道（角度/面积）充当精确数值比较而缺少直标？
- **VR-C 常见坑 (`CM-01 ~ CM-11`)**：是否柱状图误截断 Y 轴、强偏态只画均值柱、双 Y 轴混淆不同量纲、金字塔/镜像左轴未转正、使用 3D 装饰或斑马阴影？
- **VR-D/F/G**：多面板图是否调用 `add_panel_labels()` + `repel_panel_labels(fig)` 防遮挡？长分类名是否水平置放并截断/旋转清晰？图例是否避开数据密集区？

---

## 二、参考资料按需加载指南

- **先查怎么选图与反模式避坑**：阅读 [references/chart-selection.md](references/chart-selection.md)
- **查配色、vivid/Start-from-Grey、期刊版面尺寸、视觉守卫**：阅读 [references/color-style.md](references/color-style.md)
- **查 55+ 图表完整函数签名与别名**：阅读 [references/full-api.md](references/full-api.md)
- **直接复用多场景完整科研代码模板**：阅读 [references/recipes.md](references/recipes.md)
