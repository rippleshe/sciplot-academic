# 图表选型决策矩阵、感知精度与反模式避坑指南

> **核心理念**（整合自科研绘图最佳实践与 `dataviz-course-skill` 理论体系）：  
> 图表的第一使命是**准确传递数据结构与统计事实**，其次才是表达力与美感。禁止在尚未评估样本量、偏度、量纲与变量语义之前，习惯性地一律使用普通柱状图、箱线图或裸折线图。

---

## 一、感知精度阶梯 (`VR-B1`) — 决定通道优先级

人眼读取数值差异的准确率从高到低排列（**精度越高越适合主变量对比**）：

1. **同一对齐坐标轴上的位置**（散点、哑铃、棒棒糖终点、森林图均值点）—— *精度最高*
2. **相同量纲但非对齐坐标轴上的位置**（分面小图、堆叠条非基准层）
3. **统一零基线长度**（竖柱、水平条形、镜像条形）
4. **方向 / 斜率 / 倾角**（折线走势、斜率图）
5. **角度 / 整体占比**（环形图、饼图）—— *必须附加直标数值*
6. **面积**（气泡图、矩形树图、华夫小格数）
7. **明度 / 饱和度**（热力图、密度地图）
8. **色相 (Hue)** —— *仅用于定性分类，绝不用于定量大小比较！*

---

## 二、干0–干9 智能决策树路由（对应 `sp.recommend_charts`）

### 干0：前置校验 (`DT-01 ~ DT-04`)
- **DT-01 先看分布再做推断**：四组完全不同的散点形态可以拥有完全相同的均值、标准差与相关系数（Anscombe 四重奏）。画图前必先检查分布形态、离群点和线性假设。
- **DT-02 准确压倒花哨**：任何装饰性 3D、圆角阴影、过度色彩变化如果削弱读数准确性，一律删除。
- **DT-04 读者定态**：论文插图追求“**静态 + 解释性**”（核心结论一目了然、无图例寻路负担）。

### 干1–干8：按数据形态与任务精确匹配

| 决策路径 | 识别条件 | 首选图表 | 次选/互补方案 | 绝对禁区（反模式） |
|---|---|---|---|---|
| **干1·单变量分布** | 1 维连续数值数组 | `plot_histogram(show_kde=True, show_median=True)` | `plot_raincloud` / `plot_qq` | 禁止只用单一“均值±SD”柱或仅箱线掩盖双峰 |
| **干2·单因素多组分布** | 1 分类 × 1 连续 ($n \ge 15$/组, $k \le 5$) | `plot_raincloud`（半提琴+箱线+点） | `plot_violin(show_box=True, show_points=True)` | **禁止**强偏态/多峰样本画误差棒柱图 |
| **干2·双因素多组分布** | 2 分类 × 1 连续（每交叉格多次采样） | **`plot_grouped_violin`** | `plot_grouped_bar`（仅展示均值补充时） | **禁止**省略内部分布只交双因素误差柱图 |
| **干2·多组分布扫描** | 5–16 组连续分布样本 | `plot_ridgeline`（山脊重叠 KDE） | `plot_raincloud` | 避免把 10 组箱线塞进单宽画布造成窄框压缩 |
| **干2·小样本分组分布** | 每组 $n < 15$ 离散点 | `plot_beeswarm(show_median=True)` | `plot_paired`（若一一配对） | **禁止**对 $n < 15$ 强拟合平滑小提琴产生伪密度峰 |
| **干3·时间序列演进** | 1–4 条时间/阶段序列 | `plot_multi_timeseries` / `plot_fan`（多实现分位带） | `plot_timeseries(events=..., rolling_mean=...)` | 只有离散分类横轴时 **禁止连折线 (VR-B5)** |
| **干3·多时序密集对比** | $\ge 5$ 条时序轨迹 | `paper_subplots` 分面小图 / `plot_bump(highlight=...)` | `plot_streamgraph` | **禁止** 6 条以上折线全部叠在一起画成“意面图” |
| **干4·占比/构成对比** | 非负分项汇总至 100% | `plot_waffle`（精确整数格）/ `plot_treemap` ($k \ge 6$) | `plot_donut(center_text=...)` ($k \le 5$) / `plot_pareto` | **禁止**超 6 片无直标饼图或 3D 饼图 (`CM-04, CM-11`) |
| **干5·单项排名/前后差** | 1 分类 × 1 连续标量或前后 2 值 | `plot_pareto` / `plot_lollipop(orientation="h")` / `plot_diverging_bar` | `plot_dumbbell` / `plot_slope` | **禁止**柱图 Y 轴不从 0 起算 (`CM-10`)；长标签旋转过密 |
| **干5·双组多指标对称对比** | 2 组 × $k$ 个非负指标 | **`plot_back_to_back_bar` (`mirror_bar`)** | `plot_dumbbell` | **禁止**左侧负数刻度直接漏负号 (`CM-09`) |
| **干6·双变量关系** | 2 连续数值变量 | $n < 300$: `plot_marginal(..., marginal="kde")`<br>$n \ge 300$: `plot_hexbin(bins="log")` | `plot_scatter(fit_line=True, show_stats=True)` | **禁止** $n \ge 500$ 不缩点降透导致 Overplotting |
| **干7·相关矩阵 / 高维表** | 方阵 / $\ge 4$ 个连续变量 | `plot_heatmap(..., triangle="lower", p_values=...)` / `plot_scatter_matrix` | `plot_clustermap` / `plot_pca` / `plot_parallel` | **禁止**对称矩阵全画造成一半重复噪音 |
| **干8·多方法跨量纲评测** | $M$ 个模型 × $K$ 个不同量纲指标 | **`plot_method_heatmap(..., higher_is_better=...)`** | `plot_radar` ($M \le 5$) / `plot_bump` | **禁止**把 AUC 和 Latency(ms) 硬画在同一 Y 轴 (`CM-07`) |
| **干8·回归误差全诊断** | 真实值 $y_{\text{true}}$ vs 预测值 $\hat{y}$ | **`plot_residual_diagnostics`**（2×2 四象限） | `plot_bland_altman` / `plot_residuals` | **禁止**只看 $R^2$/RMSE 柱子而忽视异方差与自相关 |
| **干8·敏感性扰动排名** | 参数低/高边界扰动结局 | **`plot_tornado`** | `plot_forest`（带置信区间研究估计） | **禁止**零散多柱对比敏感度 |
| **干8·领域专型数据** | `log2FC+p` / `ci_low+ci_high` / `y_true+prob` / `source+target` | `plot_volcano` / `plot_forest` / `plot_roc` + `plot_calibration` / `plot_sankey` | `plot_upset` / `plot_chord` / `plot_paired` | 用通用柱状图强行替代领域专用诊断图 |

---

## 三、常见误导与审稿红线（Common Mistakes `CM-01 ~ CM-11`）

1. **`CM-01` 低精度编码精确读数**：要求精确对比数值差异时却用圆面积/颜色深浅而未附加直接数值标注。
2. **`CM-04` 饼图强行对比**：超过 5 类、或份额相近需要比较谁更高时禁用饼/环形图，改用排序 `plot_lollipop` 或 `plot_horizontal_bar`。
3. **`CM-06` 多图坐标不一致**：并排子图做横向对比却各自采用不同 Y 轴刻度。用 `paper_subplots(..., sharey=True)` 或统一度量区间。
4. **`CM-07` 双 Y 轴量纲错觉**：尽量少用双轴比较截然不同物理量（除非明确为帕累托累积 % vs 频数），否则拆分上下子图或改用 `plot_method_heatmap`。
5. **`CM-08` 隐瞒对数刻度**：数据跨度 $\ge 100$ 倍使用对数坐标时，坐标轴标签和图题必须写明 `(log scale)`。
6. **`CM-09` 镜像条图负号误读**：金字塔 / 双向对照条左半轴必须格式化成正数绝对值（`plot_back_to_back_bar` 已自动内置）。
7. **`CM-10` 柱图截断零基线**：柱状图/条形图必须从 `0` 起算；若数值全集中于 `[92, 96]`，改用`plot_lollipop` / `plot_dumbbell` / 带断轴说明的点图。
8. **`CM-11` 3D 与冗余装饰**：普通二维统计禁止使用 3D 立体柱状图/3D 饼图，清除暗黑粗框、阴影渐变和背景杂网格。

---

## 四、定稿九维评审 Rubric (`VR-A ~ VR-I`)

交付前依次过以下 9 条门禁，前 3 条一票否决：
- **VR-A 任务匹配**：图表族与目标问题一致，未误跨类错配？
- **VR-B 编码合理 (`Start-from-Grey`)**：关键对比落在位置/长度上？离散类别颜色数 $\le 6$ 且目标结论唯一高亮 (`make_highlight_palette`)？
- **VR-C 误导风险**：通过全部 `CM-01 ~ CM-11` 核查，未隐藏偏态或异常点？
- **VR-D 无意义装饰**：开启 L 形极简脊线 (`polish_axis`)、隐藏冗余连续次刻度、无强黑色默认粗框？
- **VR-E/F 排版与比例**：复合图多子图间隔呼吸感充沛，且子图编号 `(a)(b)(c)` 不与任何轴刻度重叠 (`repel_panel_labels`)？
- **VR-G 图例与文字**：优先曲线末段直标或稀疏角标 (`pick_best_corner`)，无过长重叠标签 (`truncate_tick_labels` / `auto_rotate_labels`)？
- **VR-H/I 结论可读与规范**：`audit_figure(fig, check_visual_guards=True)` 零警告通过，并已亲眼检查导出高清 PNG？
