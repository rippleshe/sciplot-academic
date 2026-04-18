# 扩展功能

## 机器学习可视化（ML 扩展）

需要安装：`pip install sciplot-academic[ml]` 或 `uv pip install sciplot-academic[ml]`

```python
from sciplot._ext.ml import (
    plot_pca,
    plot_confusion_matrix,
    plot_feature_importance,
    plot_learning_curve
)

# PCA 可视化
fig, ax = plot_pca(data, labels=labels, venue="nature")

# 混淆矩阵
fig, ax = plot_confusion_matrix(y_true, y_pred, labels=["A", "B", "C"])

# 特征重要性
fig, ax = plot_feature_importance(features, importance, top_n=15)

# 学习曲线
fig, ax = plot_learning_curve(train_scores, val_scores, sizes)
```

---

## 3D 可视化（Plot3D 扩展）

```python
from sciplot._ext.plot3d import plot_surface, plot_contour, plot_3d_scatter, plot_wireframe

# 3D 曲面
fig, ax = plot_surface(X, Y, Z, xlabel="X", ylabel="Y", zlabel="Z")

# 等高线图
fig, ax = plot_contour(X, Y, Z, levels=15, filled=True)

# 3D 散点
fig, ax = plot_3d_scatter(x, y, z, c=colors, cmap="plasma")

# 线框图
fig, ax = plot_wireframe(X, Y, Z, rstride=10, cstride=10)
```

---

## 网络图扩展

```python
from sciplot._ext.network import (
    plot_network,
    plot_network_from_matrix,
    plot_network_communities,
)

# 从节点和边绘制网络图
nodes = [("A", {"size": 10}), ("B", {"size": 20}), ("C", {"size": 15})]
edges = [("A", "B"), ("B", "C"), ("C", "A")]
fig, ax = plot_network(nodes, edges)

# 从邻接矩阵绘制
import numpy as np
adj_matrix = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
fig, ax = plot_network_from_matrix(adj_matrix, labels=["A", "B", "C"])

# 社区检测可视化
fig, ax = plot_network_communities(nodes, edges, method="louvain")
```

---

## 层次聚类扩展

```python
from sciplot._ext.hierarchical import plot_dendrogram, plot_clustermap

# 层次聚类树状图
data = np.random.randn(20, 10)
fig, ax = plot_dendrogram(data, method="ward")

# 聚类热图
fig, ax = plot_clustermap(data, row_cluster=True, col_cluster=True)
```

---

## 维恩图扩展

```python
from sciplot._ext.venn import plot_venn2, plot_venn3

# 2 集合维恩图
fig, ax = plot_venn2(set_a, set_b, labels=["A", "B"])

# 3 集合维恩图
fig, ax = plot_venn3(set_a, set_b, set_c, labels=["A", "B", "C"])
```

---

## 回归诊断图

```python
from sciplot._plots.statistical import plot_residuals, plot_qq, plot_bland_altman

# 残差图
fig, ax = plot_residuals(model, X, y)

# Q-Q 图（正态性检验）
fig, ax = plot_qq(residuals)

# Bland-Altman 图（一致性分析）
fig, ax = plot_bland_altman(method1, method2)
```
