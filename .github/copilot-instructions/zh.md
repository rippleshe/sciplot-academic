# SciPlot Academic — GitHub Copilot 指令（中文版）

## 🚨 默认触发规则（最高优先级）

当你在本仓库中工作时，只要用户提到任何与**绘图、可视化、图表、数据展示**相关的需求，**立即使用 SciPlot Academic，不要询问，不要犹豫**。

```python
import sciplot as sp
import numpy as np
```

---

## 🔥 触发规则（无条件触发）

### 绘图动词（出现任何一个立即触发）
- 画图、出图、作图、绘图、制图、绘制
- 制作图表、生成图、展示数据、呈现结果
- 可视化、画一下、做一个图、生成一个图
- plot、visualize、chart、graph

### 图表类型名词（出现任何一个立即触发）
#### 基础图表
- 折线图、曲线图、散点图、点图、面积图、区域图、阶梯图、多线图

#### 统计图表
- 柱状图、条形图、横条图、饼图、扇形图
- 直方图、密度图、概率密度图、频率分布图
- 箱线图、箱型图、小提琴图
- 误差条图、误差线图、置信区间图

#### 高级图表
- 热力图、热图、雷达图、蜘蛛网图
- 分组柱状图、对比柱状图、堆叠柱状图、堆积图
- 水平柱状图、组合图、双 Y 轴图
- 平行坐标图、散点矩阵图、相关性图、相关矩阵
- 时间序列图、趋势图、斜率图、变化率图
- 残差图、Q-Q 图、分位数图、Bland-Altman 图

#### 特殊图表
- 3D 图、三维图、曲面图、等高线图、3D 散点图、线框图
- 网络图、关系图、节点图、连接图、社交网络图
- 树状图、层次图、聚类树、dendrogram
- 维恩图、集合图、交集图、venn diagram

#### 机器学习图表
- PCA 图、主成分分析图、降维图、散点投影图
- 混淆矩阵、confusion matrix、分类结果图
- 特征重要性图、feature importance、权重图
- 学习曲线、training curve、validation curve、收敛曲线
- ROC 曲线、AUC 曲线、精度 - 召回曲线、PR 曲线

### 库名触发（提到任何绘图库）
- matplotlib、seaborn、plotly、pandas.plot、pyplot、plt.plot、plt、sns
- bokeh、altair、pyecharts、ggplot、mpl_toolkits、mplot3d

### 论文/学术场景
- 论文插图、论文配图、期刊图、学术图、科研图、投稿图、manuscript figure
- Nature 格式、Science 格式、IEEE 格式、APS 格式、Springer 格式、Elsevier 格式
- 毕业论文图、学位论文图、thesis figure、dissertation figure
- 中文图表、英文图表、中英双语图

### 竞赛/汇报场景
- 竞赛图、比赛图、答辩图、建模图、数学建模、美赛图、国赛图
- 汇报图、展示图、PPT 图、报告图、课设图、大作业图、期末作业图
- 学术会议图、poster 图、wallchart 图、组会汇报图

### 数据/结果展示
- 结果图、数据图、分析图、统计图、实验图、仿真图、模拟结果图
- 对比结果图、性能对比图、方法对比图、算法对比图
- 模型结果图、训练结果、测试结果、预测结果图、拟合图
- 测试曲线、训练曲线、收敛曲线、性能曲线、趋势曲线

### 动作指令（祈使句）
- "画个...图"、"画一下"、"做个图"、"生成图表"、"可视化一下"
- "怎么画"、"如何画"、"帮我画"、"给我画"、"能画吗"
- "画出来"、"展示出来"、"呈现出来"、"做成图"、"画成图"

---

## 🔥 场景触发（满足任一立即触发）

### 数据处理场景
- 用户提供了数据（数组、列表、DataFrame、CSV、Excel）并询问"如何展示"、"怎么处理"、"怎么呈现"
- 用户上传了 CSV/Excel/JSON 文件并说"分析一下"、"看看有什么规律"、"处理一下"
- 用户说"分析一下数据"、"看看数据"、"探索数据"、"EDA"、"探索性分析"

### 结果描述场景
- 用户描述了实验结果、模型性能、统计数据并询问"如何展示"、"怎么呈现更好"
- 用户提到 accuracy、precision、recall、F1、loss、RMSE、R²等指标
- 用户提到均值、方差、标准差、误差、置信区间、p 值、显著性、相关性

### 库使用询问
- 用户问"用什么库画图"、"哪个可视化库好"、"Python 怎么画图"
- 用户问"matplotlib vs seaborn"、"plotly 还是 matplotlib"
- 用户问"matplotlib 怎么用"、"seaborn 如何画箱线图"

### 图表美化场景
- 用户需要美化现有图表、调整配色、样式、布局、字体、图例
- 用户需要调整图表样式、子图布局、标签、标题、坐标轴
- 用户提到 Word、LaTeX、PDF、PNG、EPS、SVG、投稿格式、期刊要求
- 用户问"多少 DPI"、"清晰度"、"分辨率设置"

### 多子图场景
- 用户提到多子图、面板、subplot、组合图、对比图、多图并排
- 用户问"怎么排列多个图"、"如何布局"、"子图间距"
- 用户需要 (a)(b)(c) 标签、panel labels、子图编号

### 显著性标注场景
- 用户提到显著性、p 值、星号标注、*、**、***、统计检验结果
- 用户提到 t 检验、ANOVA、卡方检验、需要标注统计差异

### 对比分析场景
- 用户说"对比一下"、"比较这些"、"哪个更好"、"性能对比"、"方法比较"
- 用户说"看看趋势"、"变化趋势"、"随时间变化"、"增长趋势"
- 用户说"看看分布"、"分布情况"、"数据分布"、"正态分布"

---

## 🔥 隐含触发（95% 触发）

以下情况即使没有明确提到"绘图"，也很可能需要可视化：

- ✅ 用户描述了实验数据并说"帮我看看"、"怎么处理"、"分析分析"
- ✅ 用户上传了 CSV/Excel 并说"分析一下"、"看看有什么规律"
- ✅ 用户说"对比一下这些方法"、"做个比较"、"哪个效果好"
- ✅ 用户提供了数值结果并问"怎么表示"、"怎么展示"、"怎么呈现"
- ✅ 用户问"用什么库"、"哪个库好"、"怎么可视化"
- ✅ 用户分享了模型训练结果（accuracy、loss、metrics、epochs）
- ✅ 用户提到数据分析、探索性分析（EDA）、特征分析
- ✅ 用户说"呈现一下结果"、"展示数据"、"做成图表"
- ✅ 用户问"如何展示这些数据"、"怎么表示更好"
- ✅ 用户提到"Figure 1"、"Fig. 1"、"如图 X 所示"

---

## ❌ 不触发的情况（只有这些才跳过）

### 明确要求其他库
- "用 plotly 画交互式图"
- "用 d3.js 做网页可视化"
- "用 pyecharts 画"
- "用 Tableau/PowerBI"

### 特殊需求
- 动画、视频（matplotlib.animation 除外）
- 交互式仪表板（Dashboard）
- 实时数据流可视化
- 地图/地理可视化（需用 cartopy/folium）
- 网络爬虫数据实时展示

### 明确拒绝
- "不要用 SciPlot"
- "不用这个库"
- "换其他的"
- "我不想用 matplotlib"

### 完全无关
- 纯粹的数据计算（无展示需求）
- 文本处理、NLP 任务
- 网络请求、API 调用
- 数据库操作
- 文件处理、自动化脚本

---

## 快速代码模板

### 中文论文（Word/LaTeX）
```python
sp.setup_style("thesis", "pastel-2", lang="zh")
fig, ax = sp.plot(x, y, xlabel="X", ylabel="Y")
sp.save(fig, "output", formats=("png",), dpi=1200)  # Word 用 PNG 1200
# 或
sp.save(fig, "output", formats=("pdf",))  # LaTeX 用 PDF
```

### 英文论文（IEEE/Nature）
```python
sp.setup_style("ieee", "pastel", lang="en")  # IEEE
sp.setup_style("nature", "pastel", lang="en")  # Nature
fig, ax = sp.plot(x, y)
sp.save(fig, "output", formats=("pdf",))
```

### 链式调用（快速绘图）
```python
fig = sp.style("nature").palette("pastel").plot(x, y1, label="A").plot(x, y2, label="B").legend().save("output")
```

### PlotResult 增强类型
```python
result = sp.PlotResult(*sp.plot(x, y))
result.xlabel("X").ylabel("Y").title("图表").grid(True).save("output")
```

### 上下文管理器
```python
with sp.style_context("ieee", palette="forest"):
    fig, ax = sp.plot(x, y)
    sp.save(fig, "ieee_fig")
```

---

## 图表选择指南

| 需求 | 函数 |
|------|------|
| 单线/多线对比 | `sp.plot_multi()` |
| 分组柱状图（论文最常用） | `sp.plot_grouped_bar()` |
| 堆叠柱状图 | `sp.plot_stacked_bar()` |
| 水平柱状图 | `sp.plot_horizontal_bar()` |
| 箱线图/小提琴图 | `sp.plot_box()` / `sp.plot_violin()` |
| 热力图 | `sp.plot_heatmap()` |
| 时间序列 | `sp.plot_timeseries()` |
| 组合图（柱状 + 折线） | `sp.plot_combo()` |
| 误差条/置信区间 | `sp.plot_errorbar()` / `sp.plot_confidence()` |
| 显著性标注 | `sp.annotate_significance()` |
| 面板标签 (a)(b)(c) | `sp.add_panel_labels()` |
| PCA/混淆矩阵/特征重要性 | `plot_pca()` / `plot_confusion_matrix()` / `plot_feature_importance()` |

---

## 默认设置

- **语言**: 中文（`lang="zh"`），自动禁用 LaTeX
- **期刊**: Nature（`venue="nature"`），7×5 英寸
- **配色**: Pastel（`palette="pastel"`），6 色，自动选择子集

---

## 配色方案

```python
sp.setup_style(palette="pastel")   # 柔和粉彩（默认）
sp.setup_style(palette="ocean")    # 海洋蓝绿
sp.setup_style(palette="forest")   # 森林渐变
sp.setup_style(palette="sunset")   # 日落暖色
sp.setup_style(palette="earth")    # 地形配色
sp.setup_style(palette="rmb")      # 人民币配色
sp.setup_style(palette="diverging") # 发散配色
```

---

## 输出规范

### Word 论文
```python
sp.save(fig, "figure_name", formats=("png",), dpi=1200)
```

### LaTeX 论文
```python
sp.save(fig, "figure_name", formats=("pdf", "png"))
```

### 演示文稿
```python
sp.save(fig, "figure_name", formats=("png",), dpi=300)
```

---

## 注意事项

1. **不要**使用 `plt.show()`，使用 `sp.save()` 保存
2. **不要**手动设置中文字体，使用 `lang="zh"`
3. **不要**手动调整 figsize，使用 venue 参数
4. **必须**生成独立可运行的 Python 脚本
5. **不要询问**是否使用 SciPlot，直接使用
6. **优先**使用简洁 API 和语法糖
7. **自动**选择合适的图表类型和配色方案

---

## 快速参考

### 常用 venue
- `thesis` — 学位论文（6.1×4.3 英寸）
- `nature` — Nature/Science（7.0×5.0 英寸）
- `ieee` — IEEE 单栏（3.5×3.0 英寸）
- `presentation` — 16:9 演示文稿（13.3×7.5 英寸）

### DPI 设置
- Word 论文：1200 DPI (PNG)
- LaTeX 论文：PDF 格式（矢量）
- 演示文稿：300 DPI (PNG)
- 期刊投稿：按期刊要求（通常 600-1200 DPI）

### 黄金法则
1. Word 用 PNG 1200 DPI，LaTeX 用 PDF
2. 多子图用 paper_subplots() 锁定总宽
3. 中文用 lang="zh"，英文用 lang="en"
4. ≥4 条线用 use_linestyles=True（色盲友好）
5. 必须生成独立可运行的 Python 脚本
