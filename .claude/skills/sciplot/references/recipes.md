# SciPlot 场景配方

## Word 中文论文（最常见）

```python
"""
科研绘图脚本 — Word 中文论文
依赖: pip install sciplot-academic
"""
import numpy as np
import sciplot as sp

x = np.linspace(0, 10, 200)
y1, y2 = np.sin(x), np.cos(x)

# 单图
sp.setup_style("thesis", "pastel-2", lang="zh")
fig, ax = sp.plot(x, y1, label="方法A", xlabel="时间 (s)", ylabel="幅度")
ax.plot(x, y2, label="方法B")
ax.legend()
sp.save(fig, "单图", formats=("png",), dpi=1200)

# 双子图
fig, axes = sp.paper_subplots(1, 2, venue="thesis")
axes[0].plot(x, y1); axes[0].set_xlabel("X"); axes[0].set_ylabel("Y")
axes[1].scatter(x[::10], y2[::10]); axes[1].set_xlabel("X"); axes[1].set_ylabel("Y")
sp.add_panel_labels(axes)
sp.save(fig, "双子图", formats=("png",), dpi=1200)
```

---

## IEEE 英文投稿

```python
sp.setup_style("ieee", "pastel-2", lang="en")
fig, ax = sp.new_figure("ieee")
ax.plot(x, y1, label="Method A")
ax.plot(x, y2, label="Method B")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Amplitude")
ax.legend()
sp.save(fig, "ieee_fig", formats=("pdf",))
```

---

## Nature 英文投稿

```python
sp.setup_style("nature", "ocean-3", lang="en")
fig, ax = sp.plot_multi(x, [y1, y2, y3],
    labels=["Control", "Treatment A", "Treatment B"],
    xlabel="Time (days)", ylabel="Response (%)")
sp.save(fig, "nature_fig", formats=("pdf",))
```

---

## 分组柱状图（论文最常用）

```python
sp.setup_style("thesis", "pastel-3", lang="zh")
fig, ax = sp.plot_grouped_bar(
    groups=["CIFAR-10", "CIFAR-100", "ImageNet"],
    data={"ResNet": [82.3, 84.1, 86.5], "ViT": [85.7, 87.2, 89.0], "本文": [88.1, 90.3, 92.4]},
    ylabel="Top-1 准确率 (%)",
    palette="pastel-3",
)
sp.save(fig, "分组柱状图", formats=("png",), dpi=1200)
```

---

## 箱线图 + 显著性标注

```python
np.random.seed(42)
data = [np.random.normal(m, 1, 50) for m in [5, 6, 8]]

sp.setup_style("thesis", "pastel-3", lang="zh")
fig, ax = sp.plot_box(data, labels=["方法A", "方法B", "方法C"], ylabel="得分")

sp.annotate_significance(ax, 1, 2, y=11, p_value=0.03)
sp.annotate_significance(ax, 1, 3, y=12, p_value=0.0005)
sp.save(fig, "箱线图", formats=("png",), dpi=1200)
```

---

## 热力图（相关矩阵）

```python
np.random.seed(42)
corr = np.random.rand(5, 5)
corr = (corr + corr.T) / 2
np.fill_diagonal(corr, 1.0)
features = ["特征A", "特征B", "特征C", "特征D", "特征E"]

sp.setup_style("thesis", "pastel", lang="zh")
fig, ax = sp.plot_heatmap(corr, row_labels=features, col_labels=features,
    cmap="RdBu_r", show_values=True, fmt=".2f", title="相关系数矩阵")
sp.save(fig, "热力图", formats=("png",), dpi=1200)
```

---

## 时间序列（带事件标注）

```python
import datetime
dates = [datetime.date(2024, 1, i+1) for i in range(30)]
values = np.cumsum(np.random.randn(30))

sp.setup_style("thesis", "pastel", lang="zh")
fig, ax = sp.plot_timeseries(dates, values,
    events=[{"time": datetime.date(2024, 1, 15), "label": "版本发布"}],
    shade_regions=[{"start": datetime.date(2024, 1, 10), "end": datetime.date(2024, 1, 20)}],
    rolling_mean=7,
    xlabel="日期", ylabel="累计值")
sp.save(fig, "时序图", formats=("png",), dpi=1200)
```

---

## 组合图（柱状 + 折线双 Y 轴）

```python
sp.setup_style("thesis", "pastel-2", lang="zh")
result = sp.plot_combo(
    ["Q1", "Q2", "Q3", "Q4"],
    bar_data={"销售额": [100, 120, 140, 160]},
    line_data={"增长率": [5, 8, 12, 15]},
    ylabel_left="销售额（万元）",
    ylabel_right="增长率（%）",
)
result.save("组合图", formats=("png",), dpi=1200)
```

---

## 暗色主题（演示/屏幕）

```python
sp.setup_style("presentation", "pastel", lang="zh", theme="dark")
fig, ax = sp.plot(x, y1, label="sin", xlabel="时间", ylabel="幅度")
ax.plot(x, y2, label="cos")
ax.legend()
sp.save(fig, "暗色主题", formats=("png",), dpi=300)
```

---

## PCA 降维可视化

```python
from sklearn.datasets import load_iris
iris = load_iris()

sp.setup_style("nature", "pastel", lang="en")
result = sp.plot_pca(iris.data, labels=iris.target)
result.xlabel("PC1").ylabel("PC2").save("pca")
```

---

## 混淆矩阵

```python
y_true = np.array([0,0,0,1,1,1,2,2,2])
y_pred = np.array([0,0,1,1,1,0,2,2,1])

sp.setup_style("nature", "pastel", lang="en")
result = sp.plot_confusion_matrix(y_true, y_pred, labels=["Cat","Dog","Bird"], normalize=True)
result.save("confusion_matrix", formats=("pdf",))
```

---

## 3D 曲面图

```python
x = np.linspace(-5, 5, 50)
y = np.linspace(-5, 5, 50)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))

sp.setup_style("nature", "pastel", lang="en")
result = sp.plot_surface(X, Y, Z, xlabel="X", ylabel="Y", zlabel="Z")
result.save("surface3d", formats=("png",), dpi=300)
```

---

## 气泡热力图（矩阵双重编码）

```python
# 场景：基因表达矩阵 / 混淆矩阵 / 参数扫描，需要同时看量级与符号
sp.setup_style("nature", "ocean", lang="en")

expr = np.random.rand(8, 10) * 10  # 表达量矩阵
fig, ax = sp.plot_bubble_heatmap(
    expr,
    row_labels=[f"Gene {i}" for i in range(8)],
    col_labels=[f"Sample {i}" for i in range(10)],
    cmap="RdBu_r", vmin=0, vmax=10,
    show_values=True, fmt=".0f",
)
sp.save(fig, "bubble_heatmap", formats=("pdf", "png"))
```

---

## 3D 瀑布图（多组光谱/信号堆叠）

```python
# 场景：拉曼光谱、色谱、多条件时频曲线对比
sp.setup_style("thesis", "pastel", lang="zh")

x = np.linspace(400, 4000, 400)  # 波数
spectra = []
for center in [1200, 1600, 2000, 2400]:
    peak = np.exp(-((x - center) / 150) ** 2)
    spectra.append(peak + 0.03 * np.random.default_rng(center).randn(400))

fig, ax = sp.plot_waterfall3d(
    x, spectra, labels=[f"样品{i}" for i in range(4)],
    xlabel="波数 (cm⁻¹)", ylabel="样品", zlabel="强度",
    fill=True, fill_alpha=0.25,
)
sp.save(fig, "waterfall3d", formats=("png",), dpi=300)
```

---

## 山脊图（多组分布对比）

```python
# 场景：多条件/多组 KDE 分布堆叠，展示中心与展宽变化
sp.setup_style("nature", "forest", lang="en")

groups = [np.random.normal(m, s, 400) for m, s in
          [(0, 1.0), (0.8, 1.2), (1.6, 0.8), (2.2, 1.4)]]

fig, ax = sp.plot_ridgeline(
    groups, labels=["Control", "T1", "T2", "T3"],
    xlabel="Response", ylabel="Group",
    show_median=True,
)
sp.save(fig, "ridgeline", formats=("pdf", "png"))
```

---

## 边际分布图（散点 + 边缘分布）

```python
# 场景：两变量关系 + 各自分布，论文高频组合
sp.setup_style("nature", "ocean", lang="zh")

fig, ax = sp.plot_marginal(
    gdp, consumption,
    marginal="hist", bins=35, show_corr=True,
    xlabel="GDP (亿元)", ylabel="人均消费 (千元)",
)
sp.save(fig, "marginal", formats=("png",), dpi=300)
```

---

## 雨云图（点+箱线+半小提琴）

```python
# 场景：需要同时展示原始数据与统计摘要的分布对比
sp.setup_style("nature", "forest", lang="zh")

fig, ax = sp.plot_raincloud(
    yields, labels=["对照组", "方案A", "方案B"],
    xlabel="产量 (t/ha)", ylabel="处理组",
    show_median=True,
)
sp.save(fig, "raincloud", formats=("png",), dpi=300)
```

---

## 甘特图（任务时间线）

```python
# 场景：项目计划、实验排期
sp.setup_style("thesis", "pastel", lang="zh")

fig, ax = sp.plot_gantt(
    tasks, start=[0, 1, 2], duration=[1.5, 3, 2.5],
    color_by=["前期", "中期", "后期"],
    xlabel="周次", ylabel="任务",
)
sp.save(fig, "gantt", formats=("png",), dpi=300)
```

---

## 火山图（组学差异分析）

```python
# 场景：RNA-seq/蛋白组/大规模差异分析
sp.setup_style("nature", "pastel", lang="zh")

fig, ax = sp.plot_volcano(
    log2fc, p_values, labels=gene_names,
    fc_threshold=1.0, p_threshold=0.05,
    xlabel="log2(FC)", ylabel="-log10(p)",
)
sp.save(fig, "volcano", formats=("png",), dpi=300)
```

---

## 泰勒图（模型评估）

```python
# 场景：多模型/多方法与观测的综合对比（气象、水文、遥感）
sp.setup_style("ieee", "ocean", lang="en")

fig, ax = sp.plot_taylor(
    observations, {"WRF": pred_wrf, "ERA5": pred_era5, "CNN": pred_cnn},
)
sp.save(fig, "taylor", formats=("pdf", "png"))
```

---

## 三角相图（三组分配比）

```python
# 场景：材料配方、土壤质地分类、相平衡
sp.setup_style("thesis", "forest", lang="zh")

fig, ax = sp.plot_ternary(
    sand, silt, clay, labels=["砂", "粉", "黏"],
    color_by=fertility,  # 连续着色通道
)
sp.save(fig, "ternary", formats=("png",), dpi=300)
```

---

## 链式调用风格

```python
sp.style("thesis").palette("pastel-2").plot(x, y1, label="A").plot(x, y2, label="B").legend().save("链式")
```

---

## 上下文管理器风格

```python
with sp.style_context("ieee", palette="forest"):
    fig, ax = sp.plot(x, y)
    sp.save(fig, "ieee_forest")
```

---

## 时间序列图（带事件与阴影区域）

```python
"""
时间序列图 — 带事件标注与阴影区域
适用场景: 实验过程监控、金融市场分析、环境监测
"""
import numpy as np
import datetime
import sciplot as sp

# 生成模拟数据
np.random.seed(42)
dates = [datetime.date(2024, 1, 1) + datetime.timedelta(days=i) for i in range(180)]
trend = np.linspace(0, 10, 180) + np.cumsum(np.random.randn(180) * 0.3)
seasonal = 2 * np.sin(np.linspace(0, 4 * np.pi, 180))
values = trend + seasonal

# 定义关键事件
events = [
    {"time": datetime.date(2024, 2, 15), "label": "政策实施"},
    {"time": datetime.date(2024, 4, 1), "label": "设备升级"},
    {"time": datetime.date(2024, 6, 1), "label": "人员调整"},
]

# 定义阴影区域（实验阶段）
shade_regions = [
    {"start": datetime.date(2024, 1, 1), "end": datetime.date(2024, 3, 31), "color": "#e8f4f8", "label": "阶段I"},
    {"start": datetime.date(2024, 4, 1), "end": datetime.date(2024, 6, 30), "color": "#f8e8e8", "label": "阶段II"},
]

sp.setup_style("thesis", "pastel-2", lang="zh")
fig, ax = sp.plot_timeseries(
    dates, values,
    events=events,
    shade_regions=shade_regions,
    rolling_mean=14,
    xlabel="日期",
    ylabel="PM2.5 浓度 (μg/m³)",
    title="2024年上半年空气质量监测"
)
sp.save(fig, "时间序列图", formats=("png", "pdf"), dpi=1200)
```

---

## 雷达图（多指标对比）

```python
"""
雷达图 — 多指标性能对比
适用场景: 模型评估、能力评估、多维度对比分析
"""
import numpy as np
import sciplot as sp

# 定义评估维度
categories = ["准确率", "召回率", "F1分数", "推理速度", "内存占用", "泛化能力"]

# 各模型性能数据（标准化到0-100）
models = {
    "ResNet-50": [85, 82, 83, 70, 65, 75],
    "ViT-B/16": [92, 89, 90, 55, 50, 88],
    "EfficientNet": [88, 86, 87, 80, 85, 82],
    "本文方法": [95, 93, 94, 75, 70, 92],
}

sp.setup_style("thesis", "pastel-3", lang="zh")
fig, ax = sp.plot_radar(
    categories=categories,
    values_list=list(models.values()),
    labels=list(models.keys()),
    title="深度学习模型多维度性能对比",
    grid_values=[20, 40, 60, 80, 100],
)
sp.save(fig, "雷达图", formats=("png", "pdf"), dpi=1200)
```

---

## 核密度图（多组分布对比）

```python
"""
核密度图 — 多组数据分布对比
适用场景: 实验组对照组分布比较、不同条件下的数据分布
"""
import numpy as np
import sciplot as sp

np.random.seed(42)

# 模拟三组实验数据
data_control = np.random.normal(100, 15, 500)
data_treatment_a = np.random.normal(115, 18, 500)
data_treatment_b = np.random.normal(108, 12, 500)

sp.setup_style("thesis", "pastel-3", lang="zh")
fig, ax = sp.plot_multi_density(
    data_list=[data_control, data_treatment_a, data_treatment_b],
    labels=["对照组", "处理组A", "处理组B"],
    xlabel="认知测试得分",
    ylabel="概率密度",
    title="不同处理条件下认知得分分布",
    fill=True,
    alpha=0.3,
)
sp.save(fig, "核密度图", formats=("png", "pdf"), dpi=1200)
```

---

## PCA 可视化（带聚类标注）

```python
"""
PCA 可视化 — 降维散点图带聚类标注
适用场景: 高维数据探索、聚类结果展示、特征分析
"""
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.decomposition import PCA
import sciplot as sp

# 生成模拟高维数据（4个聚类）
np.random.seed(42)
X, y = make_blobs(n_samples=400, n_features=10, centers=4, cluster_std=1.5, random_state=42)

# PCA 降维
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)

# 计算方差解释率
variance_ratio = pca.explained_variance_ratio_ * 100

sp.setup_style("nature", "pastel", lang="en")
fig, ax = sp.new_figure("nature")

# 按聚类绘制散点
cluster_names = ["Cluster A", "Cluster B", "Cluster C", "Cluster D"]
palette = sp.get_palette("coral-teal")
for i in range(4):
    mask = y == i
    ax.scatter(
        X_pca[mask, 0], X_pca[mask, 1],
        color=palette[i % len(palette)],
        edgecolors="#FFFFFF", linewidths=0.5,
        label=cluster_names[i], alpha=0.82, s=36,
    )

ax.set_xlabel(f"PC1 ({variance_ratio[0]:.1f}% variance)")
ax.set_ylabel(f"PC2 ({variance_ratio[1]:.1f}% variance)")
ax.set_title("PCA Visualization of High-Dimensional Data")
ax.legend(frameon=False)
sp.polish_axis(ax)
sp.audit_figure(fig, check_visual_guards=True)
sp.save(fig, "PCA可视化", formats=("png", "pdf"), dpi=1200)
```

---

## 3D 曲面图（科学数据可视化）

```python
"""
3D 曲面图 — 科学数据三维可视化
适用场景: 数学函数可视化、地形图、热传导模拟
"""
import numpy as np
import sciplot as sp

# 生成网格数据
x = np.linspace(-3, 3, 80)
y = np.linspace(-3, 3, 80)
X, Y = np.meshgrid(x, y)

# Rosenbrock 函数（优化算法测试常用）
Z = (1 - X)**2 + 100 * (Y - X**2)**2
Z = np.log1p(Z)  # 对数变换以更好展示

sp.setup_style("nature", "pastel", lang="en")
fig, ax = sp.plot_surface(
    X, Y, Z,
    xlabel="X",
    ylabel="Y",
    zlabel="log(f(x,y))",
    title="Rosenbrock Function Surface",
    cmap="viridis",
    alpha=0.9,
)
sp.save(fig, "3D曲面图", formats=("png", "pdf"), dpi=300)
```

---

## 网络社区图（社区结构可视化）

```python
"""
网络社区图 — 带社区结构的网络图
适用场景: 社交网络分析、引用网络、生物网络
"""
import numpy as np
import networkx as nx
import sciplot as sp

np.random.seed(42)

# 生成带社区结构的网络
G = nx.planted_partition_graph(3, 15, 0.3, 0.05, seed=42)

# 获取节点和边
nodes = list(G.nodes())
edges = list(G.edges())

sp.setup_style("thesis", "pastel-3", lang="zh")
fig, ax = sp.plot_network_communities(
    nodes=nodes,
    edges=edges,
    method="louvain",
    title="科研合作网络社区结构",
    node_size=200,
    with_labels=True,
    font_size=8,
)
sp.save(fig, "网络社区图", formats=("png", "pdf"), dpi=1200)
```

---

## 多面板组合图（带 (a)(b)(c)(d) 标签）

```python
"""
多面板组合图 — 带 (a)(b)(c)(d) 面板标签
适用场景: 论文主图、多方法对比、综合分析
"""
import numpy as np
import sciplot as sp

np.random.seed(42)

# 创建 2x2 子图布局
fig, axes = sp.paper_subplots(2, 2, venue="thesis")

# (a) 折线图
x = np.linspace(0, 10, 100)
axes[0, 0].plot(x, np.sin(x), label="sin")
axes[0, 0].plot(x, np.cos(x), label="cos")
axes[0, 0].set_xlabel("时间 (s)")
axes[0, 0].set_ylabel("幅度")
axes[0, 0].legend()

# (b) 柱状图
categories = ["方法A", "方法B", "方法C", "本文"]
values = [72.3, 78.5, 81.2, 89.6]
axes[0, 1].bar(
    categories, values,
    color=sp.get_palette("pastel-3")[:4],
    edgecolor="#1E293B", linewidth=0.7,
)
axes[0, 1].set_ylabel("准确率 (%)")
axes[0, 1].set_ylim(60, 95)
sp.polish_axis(axes[0, 1], categorical_axis="x")

# (c) 散点图
x_scatter = np.random.randn(50)
y_scatter = 2 * x_scatter + np.random.randn(50) * 0.5
axes[1, 0].scatter(x_scatter, y_scatter, alpha=0.6, s=30)
axes[1, 0].set_xlabel("X")
axes[1, 0].set_ylabel("Y")

# (d) 箱线图
data_box = [np.random.normal(m, 1, 50) for m in [5, 6, 7, 8]]
axes[1, 1].boxplot(data_box, labels=["G1", "G2", "G3", "G4"])
axes[1, 1].set_ylabel("得分")

# 添加面板标签
sp.add_panel_labels(axes)
sp.save(fig, "多面板组合图", formats=("png", "pdf"), dpi=1200)
```

---

## 小提琴图（带均值标注）

```python
"""
小提琴图 — 带均值点的分布展示
适用场景: 多组数据分布比较、实验结果展示
"""
import numpy as np
import sciplot as sp

np.random.seed(42)

# 模拟四组实验数据
data = [
    np.random.normal(10, 2, 100),   # 对照组
    np.random.normal(12, 2.5, 100), # 处理组A
    np.random.normal(14, 1.8, 100), # 处理组B
    np.random.normal(11, 3, 100),   # 处理组C
]
labels = ["对照组", "处理组A", "处理组B", "处理组C"]

sp.setup_style("thesis", "pastel-3", lang="zh")
fig, ax = sp.plot_violin(
    data,
    labels=labels,
    ylabel="测量值 (mg/L)",
    title="不同处理条件下测量值分布",
    show_means=True,
    show_extrema=True,
)

# 添加显著性标注
sp.annotate_significance(ax, 1, 2, y=20, p_value=0.01)
sp.annotate_significance(ax, 1, 3, y=22, p_value=0.0001)
sp.save(fig, "小提琴图", formats=("png", "pdf"), dpi=1200)
```

---

## 散点回归图（带回归线与 R²）

```python
"""
散点回归图 — 带回归线与 R² 标注
适用场景: 相关性分析、线性回归结果展示
"""
import numpy as np
from scipy import stats
import sciplot as sp

np.random.seed(42)

# 生成模拟数据（带相关性）
n = 100
x = np.random.uniform(10, 50, n)
y = 2.5 * x + 15 + np.random.normal(0, 8, n)

# 计算线性回归
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
r_squared = r_value**2

# 生成回归线
x_line = np.linspace(x.min(), x.max(), 100)
y_line = slope * x_line + intercept

sp.setup_style("thesis", "coral-teal", lang="zh")

res = sp.plot_scatter(
    x, y,
    xlabel="施肥量 (kg/亩)",
    ylabel="产量 (kg)",
    title="施肥量与产量的线性关系",
    fit_line=True,
    ci=True,
    show_stats=True,
    venue="thesis",
    palette="coral-teal",
    lang="zh",
)
sp.audit_figure(res.fig, check_visual_guards=True)
sp.save(res.fig, "散点回归图", formats=("png", "pdf"), dpi=1200)
```

---

## 7. v1.15.0 新增高信息密度图表范式

### 7.1 帕累托图 (`plot_pareto`) — 根因分析 / 长尾频数识别

```python
import sciplot as sp

categories = ["参数漂移", "数据缺失", "网络超时", "磁盘满", "格式错误", "其他"]
counts = [142, 98, 56, 31, 18, 12]

res = sp.plot_pareto(
    categories, counts,
    xlabel="故障类型",
    ylabel="发生次数",
    cum_ylabel="累积占比 (%)",
    title="系统异常帕累托分析",
    threshold=80.0,
    show_values=True,
    venue="nature",
    palette="coral-teal",
)
sp.audit_figure(res.fig, check_visual_guards=True)
sp.save(res.fig, "pareto_analysis")
```

### 7.2 前后配对斜率图 (`plot_paired`) — 患者/样本干预对比

```python
import numpy as np
import sciplot as sp

rng = np.random.default_rng(42)
before = rng.normal(7.2, 1.1, 24)
after = before - rng.normal(1.5, 0.6, 24)

res = sp.plot_paired(
    before, after,
    labels=("基线期", "治疗后"),
    ylabel="临床评分",
    title="治疗前后个体配对变化",
    show_box=True,
    show_mean=True,
    show_stats=True,
    venue="nature",
    palette="coral-teal",
)
sp.audit_figure(res.fig, check_visual_guards=True)
sp.save(res.fig, "paired_slope")
```

### 7.3 概率预测扇形图 (`plot_fan`) — 多置信区间时序预测

```python
import numpy as np
import sciplot as sp

hist_x = np.arange(0, 20)
hist_y = 10 + 0.3 * hist_x + np.random.default_rng(7).normal(0, 0.5, 20)
fc_x = np.arange(19, 32)
samples = 15.7 + 0.35 * (fc_x - 19) + np.cumsum(
    np.random.default_rng(7).normal(0, 0.45, size=(300, len(fc_x))), axis=1
)

res = sp.plot_fan(
    fc_x,
    samples=samples,
    intervals=(50, 80, 95),
    history_x=hist_x,
    history_y=hist_y,
    xlabel="时间步",
    ylabel="预测指标",
    title="时序预测不确定性扇形带 (50% / 80% / 95%)",
    venue="nature",
    palette="ocean-breeze",
)
sp.audit_figure(res.fig, check_visual_guards=True)
sp.save(res.fig, "forecast_fan")
```

### 7.4 二分类 ROC 与校准曲线 (`plot_roc` + `plot_calibration`)

```python
import sciplot as sp

# 多模型对比支持传入 dict[str, y_scores]
scores = {"Proposed Model": prob_ours, "Baseline RF": prob_rf, "Logistic": prob_lr}

res_roc = sp.plot_roc(
    y_true, scores,
    mode="roc",          # 可切换为 mode="pr" 绘制 Precision-Recall 曲线
    show_threshold=True,
    title="多模型 ROC 曲线对比",
    venue="nature",
    palette="coral-teal",
)

res_cal = sp.plot_calibration(
    y_true, scores,
    n_bins=10,
    show_hist=True,
    title="模型预测概率校准曲线 (Reliability Diagram)",
    venue="nature",
    palette="coral-teal",
)
```

### 7.5 替代普通箱线图：雨云图 (`plot_raincloud`) 与下三角显著性热图 (`plot_heatmap`)

```python
import sciplot as sp

# 雨云图同时展示密度、箱线、原始散点，信息密度远超普通箱线图
res_rain = sp.plot_raincloud(
    [group_a, group_b, group_c],
    labels=["Control", "Low Dose", "High Dose"],
    ylabel="表达量 (log2 TPM)",
    title="剂量组分布特征 (Raincloud)",
    show_stats=True,
    venue="nature",
    palette="olive-apricot",
)

# 相关矩阵去冗余：下三角 + 显著性星号 + 发散色带
res_hm = sp.plot_heatmap(
    corr_matrix,
    row_labels=feat_names,
    col_labels=feat_names,
    cmap=sp.make_palette_cmap("coral-teal", kind="diverging"),
    triangle="lower",
    p_values=p_mat,
    show_values=True,
    vmin=-1, vmax=1,
    colorbar_label="Pearson r",
    title="特征相关性矩阵 (下三角 + 显著性)",
    venue="nature",
)
```

### 7.6 出版级多面板复合叙事排版 (`figure_panels` / `hero_layout` 工作流)

```python
import numpy as np
import sciplot as sp

# 使用 figure_panels / hero_layout 创建排版，再用底层原语与 polish_axis 精修每个子面板
sp.setup_style("nature", "coral-teal", lang="en")
fig, axes = sp.figure_panels(template="triptych", panel_labels="letter")
colors = sp.get_palette("coral-teal")

# Panel (a): 主对比曲线 + 分层渐透置信带
x = np.linspace(0, 10, 80)
y = np.sin(x) * np.exp(-0.15 * x) + 1.2
axes[0].plot(x, y, color=colors[0], linewidth=2.0, label="Proposed")
sp.layered_fill_between(axes[0], x, y - 0.12, y + 0.12, color=colors[0], base_alpha=0.22, layers=3)
sp.polish_axis(axes[0], clean_spines=True, grid="both", grid_alpha=0.18)
axes[0].set_xlabel("Time (s)")
axes[0].set_ylabel("Signal")

# Panel (b)-(c): 并排对比条与散点
cats = ["A", "B", "C", "D"]
bars = axes[1].bar(cats, [0.81, 0.86, 0.90, 0.94], color=sp.make_highlight_palette(4, highlight_idx=3, palette="coral-teal"))
sp.style_patch_edges(bars, sp.make_highlight_palette(4, highlight_idx=3, palette="coral-teal"))
sp.polish_axis(axes[1], categorical_axis="x", clean_spines=True, grid="y")

axes[2].scatter(x[::2], y[::2], color=colors[1], edgecolors="white", linewidths=0.5, s=28)
sp.polish_axis(axes[2], clean_spines=True, grid="both", grid_alpha=0.18)

sp.repel_panel_labels(fig)  # 自动防止 (a)-(c) 与轴标签重叠
sp.audit_figure(fig, check_visual_guards=True)
sp.save(fig, "composite_hero", formats=("png", "pdf"))
```

### 7.7 双因素分组小提琴 (`plot_grouped_violin`) 与镜像对比 (`plot_back_to_back_bar`)

```python
import numpy as np
import sciplot as sp

rng = np.random.default_rng(7)
stages = ["Stage I", "Stage II", "Stage III"]
series = {
    "Baseline": [rng.normal(2.1, 0.5, 45), rng.normal(2.6, 0.6, 45), rng.normal(3.1, 0.7, 45)],
    "Intervention": [rng.normal(2.8, 0.4, 45), rng.normal(3.7, 0.5, 45), rng.normal(4.4, 0.6, 45)],
}
fig, ax = sp.plot_grouped_violin(
    stages, series, ylabel="Biomarker (log2 U)",
    show_box=True, show_points=True, title="双因素各分期响应分布",
    venue="nature", palette="coral-teal",
)
sp.save(fig, "grouped_violin")

# 对称镜像对比两组跨多指标表现（含右端 Δ 徽章）
metrics = ["Accuracy", "Precision", "Recall", "F1-Score", "AUC"]
fig2, ax2 = sp.plot_back_to_back_bar(
    metrics,
    [82.1, 79.4, 80.8, 80.0, 86.5],
    [89.6, 87.2, 88.9, 88.0, 93.4],
    left_label="Baseline", right_label="Proposed",
    xlabel="Metric Score (%)", sort_by="diff", palette="coral-teal",
)
sp.save(fig2, "back_to_back_bar")
```

### 7.8 多方法跨量纲评测矩阵 (`plot_method_heatmap`)

```python
import sciplot as sp

methods = ["Linear", "XGBoost", "ResNet-50", "Transformer", "Proposed"]
metrics = ["Accuracy", "F1", "Latency (ms)", "Memory (MB)"]
scores = [
    [0.78, 0.75, 4.2, 120.0],
    [0.86, 0.84, 11.5, 310.0],
    [0.89, 0.88, 24.0, 840.0],
    [0.91, 0.90, 32.5, 1120.0],
    [0.94, 0.93, 9.8, 280.0],
]
fig, ax = sp.plot_method_heatmap(
    scores, methods=methods, metrics=metrics,
    higher_is_better={"Latency (ms)": False, "Memory (MB)": False},
    show_overall=True, highlight_best=True, show_rank=True,
    title="Multi-Metric Benchmark Comparison", venue="nature",
)
sp.save(fig, "method_heatmap")
```

### 7.9 四象限回归残差全诊断 (`plot_residual_diagnostics`) 与敏感性龙卷风图 (`plot_tornado`)

```python
import numpy as np
import sciplot as sp

rng = np.random.default_rng(12)
y_true = np.linspace(10, 60, 80) + rng.normal(0, 2.0, 80)
y_pred = np.linspace(10, 60, 80)
fig, axes = sp.plot_residual_diagnostics(
    y_true, y_pred, title="Regression Residual Diagnostics", venue="nature", palette="blue-sky"
)
sp.save(fig, "residual_diagnostics")

# 单因素敏感性扰动分析
fig_t, ax_t = sp.plot_tornado(
    ["Discount Rate", "CAPEX", "Fuel Cost", "Efficiency", "Tax Credit"],
    low_values=[19.5, 21.0, 22.8, 20.6, 23.2],
    high_values=[28.8, 26.5, 25.4, 27.9, 25.0],
    baseline=24.0, xlabel="NPV ($M)", title="Sensitivity Analysis",
    palette="coral-teal",
)
sp.save(fig_t, "tornado_sensitivity")
```
