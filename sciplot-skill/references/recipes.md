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
for i in range(4):
    mask = y == i
    ax.scatter(X_pca[mask, 0], X_pca[mask, 1], label=cluster_names[i], alpha=0.7, s=30)

ax.set_xlabel(f"PC1 ({variance_ratio[0]:.1f}% variance)")
ax.set_ylabel(f"PC2 ({variance_ratio[1]:.1f}% variance)")
ax.set_title("PCA Visualization of High-Dimensional Data")
ax.legend()
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
axes[0, 1].bar(categories, values, color=sp.get_palette("pastel-3", 4))
axes[0, 1].set_ylabel("准确率 (%)")
axes[0, 1].set_ylim(60, 95)

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

sp.setup_style("thesis", "pastel-2", lang="zh")
fig, ax = sp.new_figure("thesis")

# 绘制散点
ax.scatter(x, y, alpha=0.6, s=40, label="观测值")

# 绘制回归线
ax.plot(x_line, y_line, color="#e76f51", linewidth=2, linestyle="--", label="拟合线")

# 添加 R² 标注
textstr = f"R² = {r_squared:.3f}\ny = {slope:.2f}x + {intercept:.2f}"
props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment="top", bbox=props)

ax.set_xlabel("施肥量 (kg/亩)")
ax.set_ylabel("产量 (kg)")
ax.set_title("施肥量与产量的线性关系")
ax.legend()
sp.save(fig, "散点回归图", formats=("png", "pdf"), dpi=1200)
```
