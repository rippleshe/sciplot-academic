"""
09_pca.py — PCA 主成分分析可视化

展示 SciPlot 的 plot_pca() 功能：对 3 个高斯聚类（共 450 个样本、8 维特征）
进行主成分分析并以 2D 散点图呈现，按聚类着色。
使用 pastel 配色，Nature 默认样式，中文标签。
"""

import numpy as np
import sciplot as sp

# 可复现随机种子
np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
# 模拟 3 个聚类的高维数据（每个聚类 150 个样本，8 个特征）
n_samples_per_cluster = 150
n_features = 8

# 聚类中心（在 8 维空间中有明显分离）
centers = np.array([
    np.tile(2.0, n_features),       # 聚类 A：中心在 (2, 2, ..., 2)
    np.tile(-2.0, n_features),      # 聚类 B：中心在 (-2, -2, ..., -2)
    np.array([3, -3, 3, -3, 0, 0, 2, -2]),  # 聚类 C：混合方向
])

# 生成数据
data_list = []
labels_list = []
cluster_names = ["聚类 α", "聚类 β", "聚类 γ"]

for i, (center, name) in enumerate(zip(centers, cluster_names)):
    cluster_data = center + np.random.randn(n_samples_per_cluster, n_features) * 0.8
    data_list.append(cluster_data)
    labels_list.extend([name] * n_samples_per_cluster)

data = np.vstack(data_list)
labels = np.array(labels_list)

# ── PCA 可视化 ────────────────────────────────────────────────
fig, ax = sp.plot_pca(
    data,
    labels=labels,
    venue="nature",
    palette="pastel",
    s=30,           # 散点大小
    alpha=0.7,      # 透明度
)

# 自定义标签（中文）
ax.set_xlabel("第一主成分 (PC1)")
ax.set_ylabel("第二主成分 (PC2)")
ax.set_title("多维特征主成分分析 (PCA)")

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/09_pca", formats=("png",), dpi=300)
