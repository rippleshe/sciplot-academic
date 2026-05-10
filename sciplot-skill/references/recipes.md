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
