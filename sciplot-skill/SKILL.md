# SciPlot Academic — 科研绘图 Skill (v1.9.1)

name: sciplot
description: >
  SciPlot Academic 科研绘图技能。本仓库默认绘图入口。

---

## 触发规则

**只要用户涉及以下任一维度，立即触发，无需确认：**

| 维度 | 关键词模式 |
|------|-----------|
| **动作** | 画/绘/出图/可视化/plot/chart/figure/展示数据/做成图 |
| **图表** | 折线/散点/柱状/箱线/热力/雷达/3D/网络/维恩/密度/QQ/残差 |
| **场景** | 论文图/期刊图/竞赛图/PPT图/实验结果/对比分析/趋势/分布 |
| **库名** | matplotlib/seaborn/plotly 提及 → 引导用 sciplot |
| **隐含** | 上传 CSV/Excel + "分析"；数值结果 + "怎么展示" |

**不触发**：明确要求 plotly/d3/pyecharts 交互式、动画视频、地图地理、实时仪表板、或明确拒绝 matplotlib。

---

## 决策树

```
用户需求 → 涉及数据/图表？
  ├─ 否 → 跳过
  └─ 是 → 明确要求其他交互式库？
       ├─ 是 → 跳过
       └─ 否 → 确定场景 → 选择图表类型 → 生成脚本
```

### Step 1: 确定场景

| 用户场景 | venue | formats | dpi | lang |
|---------|-------|---------|-----|------|
| Word 中文论文 | `thesis` | png | 1200 | zh |
| IEEE 英文投稿 | `ieee` | pdf | — | en |
| Nature 英文投稿 | `nature` | pdf | — | en |
| 学位论文 | `thesis` | png/pdf | 1200 | zh |
| 演示文稿 | `presentation` | png | 300 | zh |
| 深色背景演示 | `presentation` | png | 300 | zh + `theme="dark"` |

### Step 2: 选择图表

| 用户意图 | 函数 | 别名 |
|---------|------|------|
| 趋势/曲线 | `sp.plot()` | `sp.line()` |
| 多线对比 | `sp.plot_multi()` | `sp.multi()` |
| 散点关系 | `sp.plot_scatter()` | `sp.scatter()` |
| 分类对比 | `sp.plot_bar()` | `sp.bar()` |
| 多方法对比 | `sp.plot_grouped_bar()` | — |
| 堆叠占比 | `sp.plot_stacked_bar()` | `sp.stacked_bar()` |
| 水平排名 | `sp.plot_horizontal_bar()` | `sp.hbar()` |
| 分布形状 | `sp.plot_box()` / `sp.plot_violin()` | `sp.box()` / `sp.violin()` |
| 频率分布 | `sp.plot_histogram()` | `sp.hist()` |
| 密度估计 | `sp.plot_density()` | `sp.density()` |
| 热力/相关矩阵 | `sp.plot_heatmap()` | `sp.heatmap()` |
| 误差/不确定性 | `sp.plot_errorbar()` / `sp.plot_confidence()` | `sp.errorbar()` |
| 时间序列 | `sp.plot_timeseries()` | `sp.timeseries()` |
| 多维评估 | `sp.plot_radar()` | `sp.radar()` |
| 柱+线双轴 | `sp.plot_combo()` | `sp.combo()` |
| 一致性分析 | `sp.plot_bland_altman()` | `sp.bland_altman()` |
| 正态检验 | `sp.plot_qq()` | `sp.qq()` |
| 模型诊断 | `sp.plot_residuals()` | `sp.residuals()` |
| 棒棒糖排名 | `sp.plot_lollipop()` | `sp.lollipop()` |
| PCA 降维 | `sp.plot_pca()` | — |
| 混淆矩阵 | `sp.plot_confusion_matrix()` | — |
| 特征重要性 | `sp.plot_feature_importance()` | — |
| 3D 曲面 | `sp.plot_surface()` | — |
| 等高线 | `sp.plot_contour()` | — |
| 网络关系 | `sp.plot_network()` | — |
| 聚类树 | `sp.plot_dendrogram()` | — |
| 集合交集 | `sp.plot_venn2()` / `sp.plot_venn3()` | — |

---

## 最佳实践骨架（必备设置）

> **核心思想**：SciPlot 的设计哲学是"一次设置，全局生效"。正确的起手骨架能让后续代码更简洁、更专业。

### 三种入口模式

| 模式 | 适用场景 | 示例 |
|------|---------|------|
| **`setup_style()`** | 脚本开头，一次性设置 | `sp.setup_style("nature", "pastel", lang="zh")` |
| **`set_defaults()`** | 项目级持久化配置 | `sp.set_defaults(venue="ieee", palette="earth")` |
| **`style_context()`** | 临时切换样式 | `with sp.style_context("ieee"): ...` |

### 配置优先级（高→低）

```
函数参数 > 代码设置(set_defaults) > 配置文件 > 内置默认
```

### 起手骨架模板

#### 模式 A：单图脚本（最常用）

```python
"""
科研绘图脚本
依赖: pip install sciplot-academic
"""
import numpy as np
import sciplot as sp

# ═══════════════════════════════════════════════════════════════
# 1️⃣ 起手设置（必须在绘图前）
# ═══════════════════════════════════════════════════════════════
sp.setup_style("thesis", "pastel-2", lang="zh")
#             ─┬─────  ─┬────────  ─┬────
#              │        │           └── 语言：zh=中文, en=英文
#              │        └── 配色：pastel/ocean/forest/sunset/earth/rmb + 子集
#              └── 期刊：nature/ieee/aps/springer/thesis/presentation

# ═══════════════════════════════════════════════════════════════
# 2️⃣ 数据准备
# ═══════════════════════════════════════════════════════════════
x = np.linspace(0, 10, 200)
y = np.sin(x)

# ═══════════════════════════════════════════════════════════════
# 3️⃣ 绘图（setup_style 已自动设置 figsize/fontsize/字体/刻度）
# ═══════════════════════════════════════════════════════════════
fig, ax = sp.plot(x, y, xlabel="时间 (s)", ylabel="幅度 (V)")

# ═══════════════════════════════════════════════════════════════
# 4️⃣ 保存（Word=PNG 1200dpi, LaTeX=PDF）
# ═══════════════════════════════════════════════════════════════
sp.save(fig, "结果图", formats=("png",), dpi=1200)
```

#### 模式 B：多子图脚本

```python
import numpy as np
import sciplot as sp

sp.setup_style("thesis", "pastel-3", lang="zh")

# ═══════════════════════════════════════════════════════════════
# 用 paper_subplots() 锁定版心尺寸（不要用 plt.subplots）
# ═══════════════════════════════════════════════════════════════
fig, axes = sp.paper_subplots(1, 2, venue="thesis")
#                             ─┬  ─┬
#                              │   └── 列数
#                              └── 行数

# 子图 (a)
axes[0].plot(x, y1, label="方法A")
axes[0].plot(x, y2, label="方法B")
axes[0].set_xlabel("X")
axes[0].set_ylabel("Y")
axes[0].legend()

# 子图 (b)
axes[1].scatter(x[::10], y1[::10], label="数据")
axes[1].set_xlabel("X")
axes[1].set_ylabel("Y")
axes[1].legend()

# ═══════════════════════════════════════════════════════════════
# 添加 (a)(b) 面板标签
# ═══════════════════════════════════════════════════════════════
sp.add_panel_labels(axes)
sp.save(fig, "多子图", formats=("png",), dpi=1200)
```

#### 模式 C：链式调用（快速出图）

```python
import numpy as np
import sciplot as sp

x = np.linspace(0, 10, 200)

# 一行搞定：设置样式 → 配色 → 绘图 → 保存
sp.style("nature").palette("ocean").plot(x, np.sin(x), xlabel="X", ylabel="Y").save("快速出图")
```

#### 模式 D：项目级配置（推荐用于大型项目）

```python
# 在项目入口文件（如 main.py）中设置一次
import sciplot as sp

# 设置项目级默认值（所有后续脚本自动继承）
sp.set_defaults(venue="thesis", palette="pastel", lang="zh")

# 或者通过配置文件（pyproject.toml）
# [tool.sciplot]
# venue = "thesis"
# palette = "pastel"
# lang = "zh"
```

### 必备设置清单

| 设置项 | 说明 | 默认值 | 何时修改 |
|--------|------|--------|---------|
| `venue` | 期刊样式 | `nature` | 投稿 IEEE/APS/Springer 时 |
| `palette` | 配色方案 | `pastel` | 需要不同风格时 |
| `lang` | 语言 | `zh` | 英文投稿改为 `en` |
| `theme` | 主题 | `light` | 演示/PPT 改为 `dark` |

### 自动化行为（无需手动设置）

SciPlot 已内置以下行为，**不要重复设置**：

| 行为 | 说明 | 代码 |
|------|------|------|
| ✅ 无网格 | 科研图默认无网格 | `ax.grid(False)` 已内置 |
| ✅ 刻度朝内 | 专业感 | `tick_params(direction="in")` 已内置 |
| ✅ 自动 figsize | 根据 venue 设定 | nature=7×5, ieee=3.5×3, thesis=6.1×4.3 |
| ✅ 自动 fontsize | 根据 venue 设定 | nature=8pt, ieee=6pt, thesis=8pt |
| ✅ 自动字体 | 中文=宋体, 英文=Times New Roman | 根据 lang 自动切换 |
| ✅ 负号修复 | 避免 Unicode 负号 | `axes.unicode_minus=False` 已内置 |

---

## 代码生成规则

### 必须遵守

1. **始终生成独立可运行的 Python 脚本**，不要只给代码片段
2. **脚本开头**: `import sciplot as sp` + `import numpy as np`
3. **默认无网格**: 所有图表默认 `ax.grid(False)`（已内置）
4. **刻度朝内**: 所有图表默认 `tick_params(direction="in")`（已内置）
5. **保存**: 必须调用 `sp.save(fig, "文件名", ...)` 或 `result.save(...)`
6. **中文**: 默认 `lang="zh"`，英文投稿用 `lang="en"`
7. **close=True**: 批量绘图时使用 `sp.save(fig, "name", close=True)` 释放内存

### 禁止事项（反模式）

| 错误写法 | 正确写法 |
|---------|---------|
| `fig, ax = plt.subplots()` | `fig, ax = sp.new_figure(venue)` 或直接用 `sp.plot()` |
| `plt.style.use("science")` | `sp.setup_style("nature")` |
| `plt.show()` | 删除（脚本模式不需要） |
| `ax.grid(True)` | 删除（科研图默认无网格） |
| `ax.tick_params(direction="in")` | 删除（已自动设置） |
| 手动 `figsize=(10, 8)` | 用 `venue` 自动设定或 `sp.paper_subplots()` |
| `from sciplot._ext.ml import ...` | 直接 `sp.plot_pca()` 等（已通过 `__init__.py` 导出） |
| `plt.savefig(...)` | `sp.save(fig, "name", ...)` |

### 标准脚本模板

```python
"""
科研绘图脚本
依赖: pip install sciplot-academic
运行: python plot_result.py
"""
import numpy as np
import sciplot as sp

# ── 数据准备 ──
x = np.linspace(0, 10, 200)
y1, y2 = np.sin(x), np.cos(x)

# ── 绘图 ──
sp.setup_style("thesis", "pastel-2", lang="zh")
fig, ax = sp.plot(x, y1, label="sin", xlabel="时间 (s)", ylabel="幅度")
ax.plot(x, y2, label="cos")
ax.legend()

# ── 保存 ──
sp.save(fig, "结果图", formats=("png",), dpi=1200)
print("✓ 已保存")
```

### 多子图模板

```python
sp.setup_style("thesis", "pastel-2", lang="zh")
fig, axes = sp.paper_subplots(1, 2, venue="thesis")

axes[0].plot(x, y1)
axes[0].set_xlabel("X"); axes[0].set_ylabel("Y")
axes[1].scatter(x, y2)
axes[1].set_xlabel("X"); axes[1].set_ylabel("Y")

sp.add_panel_labels(axes)
sp.save(fig, "多子图", formats=("png",), dpi=1200)
```

### 暗色主题模板

```python
sp.setup_style("presentation", "pastel", lang="zh", theme="dark")
fig, ax = sp.plot(x, y, xlabel="时间", ylabel="幅度", label="数据")
ax.legend()
sp.save(fig, "暗色主题图", formats=("png",), dpi=300)
```

---

## Showcase 展示案例

> 以下 12 个案例覆盖 SciPlot 最常用图表类型，每个均可独立运行。
> 展示图片位于 `showcases/` 目录。

### 01. 多线对比图 (`01_multi_line.py`)

```python
"""多线对比图 — 展示不同方法在相同数据上的表现"""
import numpy as np
import sciplot as sp

sp.setup_style("nature", "ocean", lang="en")

x = np.linspace(0, 4 * np.pi, 300)
methods = {
    "Method A": np.sin(x) + 0.1 * np.random.randn(300),
    "Method B": np.sin(x) * 0.95 + 0.05 * np.random.randn(300),
    "Method C": np.sin(x) * 1.05 + 0.15 * np.random.randn(300),
    "Ground Truth": np.sin(x),
}

fig, ax = sp.new_figure("nature")
for label, y in methods.items():
    style = {"linestyle": "--", "linewidth": 1.5} if label == "Ground Truth" else {}
    ax.plot(x, y, label=label, **style)

ax.set_xlabel("Time (s)")
ax.set_ylabel("Amplitude")
ax.legend()
sp.save(fig, "01_multi_line", formats=("pdf", "png"))
```

### 02. 分组柱状图 (`02_grouped_bar.py`)

```python
"""分组柱状图 — 多方法在多个数据集上的性能对比"""
import numpy as np
import sciplot as sp

sp.setup_style("ieee", "pastel", lang="en")

datasets = ["Dataset A", "Dataset B", "Dataset C", "Dataset D"]
methods = ["Ours", "Baseline 1", "Baseline 2"]
scores = np.array([
    [92.3, 88.1, 85.7],
    [87.5, 84.2, 82.9],
    [94.1, 90.8, 88.3],
    [89.6, 86.4, 84.0],
])

fig, ax = sp.plot_grouped_bar(
    datasets, scores, labels=methods,
    xlabel="Dataset", ylabel="Accuracy (%)"
)
ax.set_ylim(75, 100)
sp.save(fig, "02_grouped_bar", formats=("pdf", "png"))
```

### 03. 散点回归图 (`03_scatter_regression.py`)

```python
"""散点回归图 — 展示两变量关系及拟合曲线"""
import numpy as np
import sciplot as sp

sp.setup_style("thesis", "forest", lang="zh")

np.random.seed(42)
x = np.random.uniform(10, 50, 80)
y = 2.5 * x + 15 + np.random.normal(0, 8, 80)

fig, ax = sp.plot_scatter(
    x, y,
    xlabel="温度 (°C)", ylabel="反应速率 (μmol/min)",
    regression=True,  # 自动拟合线性回归
    show_r2=True,     # 显示 R² 值
)
sp.save(fig, "03_scatter_regression", formats=("png",), dpi=1200)
```

### 04. 小提琴箱线图 (`04_violin_box.py`)

```python
"""小提琴+箱线组合图 — 展示多组数据分布"""
import numpy as np
import sciplot as sp

sp.setup_style("nature", "sunset", lang="en")

np.random.seed(42)
data = {
    "Control":   np.random.normal(100, 15, 200),
    "Treatment A": np.random.normal(115, 20, 200),
    "Treatment B": np.random.normal(108, 12, 200),
    "Treatment C": np.random.normal(125, 18, 200),
}

fig, ax = sp.plot_violin(
    data, show_box=True,  # 内嵌箱线图
    xlabel="Group", ylabel="Response Score",
)
sp.annotate_significance(ax, x1=0, x2=3, y=165, p_value=0.0003)
sp.save(fig, "04_violin_box", formats=("pdf", "png"))
```

### 05. 热力图 (`05_heatmap.py`)

```python
"""热力图 — 相关性矩阵可视化"""
import numpy as np
import sciplot as sp

sp.setup_style("ieee", "rdbu", lang="en")

np.random.seed(42)
features = ["Feature A", "Feature B", "Feature C", "Feature D", "Feature E"]
corr = np.corrcoef(np.random.randn(5, 100))
np.fill_diagonal(corr, 1.0)

fig, ax = sp.plot_heatmap(
    corr, xlabels=features, ylabels=features,
    cmap="rdbu", vmin=-1, vmax=1,
    annotate=True, fmt=".2f",
    title="Feature Correlation Matrix",
)
sp.save(fig, "05_heatmap", formats=("pdf", "png"))
```

### 06. 时间序列图 (`06_timeseries.py`)

```python
"""时间序列图 — 带置信区间的时间趋势"""
import numpy as np
import pandas as pd
import sciplot as sp

sp.setup_style("thesis", "ocean", lang="zh")

dates = pd.date_range("2024-01-01", periods=365, freq="D")
trend = np.linspace(50, 80, 365)
seasonal = 10 * np.sin(2 * np.pi * np.arange(365) / 30)
noise = np.random.normal(0, 3, 365)
values = trend + seasonal + noise

fig, ax = sp.plot_timeseries(
    dates, values,
    xlabel="日期", ylabel="测量值",
    confidence=0.95,  # 95% 置信区间
    highlight_peaks=True,
)
sp.save(fig, "06_timeseries", formats=("png",), dpi=1200)
```

### 07. 雷达图 (`07_radar.py`)

```python
"""雷达图 — 多维能力评估对比"""
import numpy as np
import sciplot as sp

sp.setup_style("presentation", "pastel", lang="zh")

categories = ["准确性", "效率", "鲁棒性", "可解释性", "泛化能力", "易用性"]
model_a = [0.92, 0.85, 0.78, 0.88, 0.90, 0.95]
model_b = [0.88, 0.92, 0.85, 0.75, 0.82, 0.88]

fig, ax = sp.plot_radar(
    [model_a, model_b],
    categories=categories,
    labels=["Model A", "Model B"],
    fill=True, alpha=0.25,
)
sp.save(fig, "07_radar", formats=("png",), dpi=300)
```

### 08. 多密度 KDE 图 (`08_density.py`)

```python
"""多密度 KDE 图 — 多组数据分布对比"""
import numpy as np
import sciplot as sp

sp.setup_style("nature", "forest", lang="en")

np.random.seed(42)
groups = {
    "Group A": np.random.normal(0, 1, 500),
    "Group B": np.random.normal(1.5, 1.2, 500),
    "Group C": np.random.normal(-0.5, 0.8, 500),
}

fig, ax = sp.plot_density(
    groups,
    xlabel="Value", ylabel="Density",
    fill=True, alpha=0.3,
    show_median=True,
)
ax.legend()
sp.save(fig, "08_density", formats=("pdf", "png"))
```

### 09. PCA 可视化 (`09_pca.py`)

```python
"""PCA 降维可视化 — 高维数据投影到 2D"""
import numpy as np
import sciplot as sp

sp.setup_style("ieee", "pastel", lang="en")

np.random.seed(42)
n_per_cluster = 50
X = np.vstack([
    np.random.randn(n_per_cluster, 10) + np.array([2, 0] + [0]*8),
    np.random.randn(n_per_cluster, 10) + np.array([-2, 0] + [0]*8),
    np.random.randn(n_per_cluster, 10) + np.array([0, 2] + [0]*8),
])
labels = ["Cluster 1"] * n_per_cluster + ["Cluster 2"] * n_per_cluster + ["Cluster 3"] * n_per_cluster

fig, ax = sp.plot_pca(
    X, labels=labels,
    xlabel="PC1", ylabel="PC2",
    show_variance=True,  # 显示方差解释率
    show_ellipses=True,  # 显示置信椭圆
)
sp.save(fig, "09_pca", formats=("pdf", "png"))
```

### 10. 3D 曲面图 (`10_3d_surface.py`)

```python
"""3D 曲面图 — 二元函数可视化"""
import numpy as np
import sciplot as sp

sp.setup_style("presentation", "ocean", lang="en")

x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))

fig, ax = sp.plot_surface(
    X, Y, Z,
    xlabel="X", ylabel="Y", zlabel="Z",
    cmap="ocean", alpha=0.9,
    show_contour=True,  # 底部等高线投影
)
sp.save(fig, "10_3d_surface", formats=("png",), dpi=300)
```

### 11. 网络社区图 (`11_network.py`)

```python
"""网络社区图 — 节点聚类可视化"""
import numpy as np
import sciplot as sp

sp.setup_style("thesis", "sunset", lang="zh")

np.random.seed(42)
n_nodes = 30
# 生成邻接矩阵（块对角结构模拟社区）
adj = np.zeros((n_nodes, n_nodes))
for i in range(3):
    block = np.random.rand(10, 10)
    adj[i*10:(i+1)*10, i*10:(i+1)*10] = (block + block.T) / 2
adj = (adj > 0.6).astype(float)
np.fill_diagonal(adj, 0)

communities = [0]*10 + [1]*10 + [2]*10

fig, ax = sp.plot_network(
    adj, communities=communities,
    node_size=200, edge_alpha=0.3,
    labels=["社区 A", "社区 B", "社区 C"],
)
sp.save(fig, "11_network", formats=("png",), dpi=300)
```

### 12. 多面板组合图 (`12_multi_panel.py`)

```python
"""多面板组合图 — 2x2 布局展示完整分析"""
import numpy as np
import sciplot as sp

sp.setup_style("nature", "pastel", lang="en")

fig, axes = sp.paper_subplots(2, 2, venue="nature")

# Panel (a): 折线图
x = np.linspace(0, 10, 200)
axes[0].plot(x, np.sin(x), label="sin")
axes[0].plot(x, np.cos(x), label="cos", linestyle="--")
axes[0].set_xlabel("Time (s)")
axes[0].set_ylabel("Amplitude")
axes[0].legend(fontsize=8)

# Panel (b): 散点图
np.random.seed(42)
axes[1].scatter(np.random.randn(50), np.random.randn(50), alpha=0.7)
axes[1].set_xlabel("X")
axes[1].set_ylabel("Y")

# Panel (c): 柱状图
categories = ["A", "B", "C", "D"]
values = [23, 45, 12, 67]
axes[2].bar(categories, values)
axes[2].set_xlabel("Category")
axes[2].set_ylabel("Count")

# Panel (d): 箱线图
data = [np.random.normal(m, 1, 100) for m in [0, 2, 1, 3]]
axes[3].boxplot(data, labels=["G1", "G2", "G3", "G4"])
axes[3].set_xlabel("Group")
axes[3].set_ylabel("Value")

sp.add_panel_labels(axes, style="LETTER")
sp.save(fig, "12_multi_panel", formats=("pdf", "png"))
```

---

## Nature 质量图表

> 以下示例生成符合 Nature/Science 期刊标准的出版级图表。

### 单栏图 (89mm)

```python
"""Nature 单栏图 — 精确匹配版心宽度 89mm"""
import numpy as np
import sciplot as sp

sp.setup_style("nature", "ocean", lang="en")

fig, ax = sp.new_figure("nature")  # 自动 89mm 宽

x = np.linspace(0, 2 * np.pi, 200)
ax.plot(x, np.sin(x), label="sin(x)", linewidth=1.5)
ax.plot(x, np.cos(x), label="cos(x)", linewidth=1.5, linestyle="--")
ax.set_xlabel("x (rad)")
ax.set_ylabel("f(x)")
ax.legend(frameon=False, fontsize=8)

sp.save(fig, "nature_single", formats=("pdf",))
```

### 双栏图 (183mm)

```python
"""Nature 双栏图 — 横跨两栏的宽图"""
import numpy as np
import sciplot as sp

sp.setup_style("nature", "pastel", lang="en")

fig, axes = sp.paper_subplots(1, 3, venue="nature")  # 双栏宽度

np.random.seed(42)
for i, ax in enumerate(axes):
    data = np.random.normal(i, 0.5, 100)
    ax.violinplot(data, showmeans=True, showmedians=False)
    ax.set_xlabel(f"Group {i+1}")
    ax.set_ylabel("Value")

sp.add_panel_labels(axes)
sp.save(fig, "nature_double", formats=("pdf",))
```

### 带误差棒的柱状图

```python
"""Nature 风格 — 带误差棒和显著性标注"""
import numpy as np
import sciplot as sp

sp.setup_style("nature", "sunset", lang="en")

categories = ["WT", "KO", "Rescue"]
means = [100, 65, 88]
sems = [5.2, 7.8, 6.1]

fig, ax = sp.new_figure("nature")
bars = ax.bar(categories, means, yerr=sems, capsize=3,
              color=sp.get_palette("sunset", 3), edgecolor="black", linewidth=0.5)

sp.annotate_significance(ax, x1=0, x2=1, y=120, p_value=0.001)
sp.annotate_significance(ax, x1=1, x2=2, y=135, p_value=0.03)

ax.set_ylabel("Relative Expression (%)")
ax.set_ylim(0, 150)
sp.save(fig, "nature_bar_error", formats=("pdf",))
```

### 生存曲线 (Kaplan-Meier)

```python
"""Nature 风格 — Kaplan-Meier 生存曲线"""
import numpy as np
import sciplot as sp

sp.setup_style("nature", "ocean", lang="en")

np.random.seed(42)
time = np.linspace(0, 60, 100)
survival_treatment = np.exp(-0.02 * time) + np.random.normal(0, 0.02, 100)
survival_control = np.exp(-0.04 * time) + np.random.normal(0, 0.02, 100)

fig, ax = sp.new_figure("nature")
ax.step(time, np.clip(survival_treatment, 0, 1), where="post", label="Treatment")
ax.step(time, np.clip(survival_control, 0, 1), where="post", label="Control", linestyle="--")
ax.fill_between(time, np.clip(survival_treatment - 0.05, 0, 1),
                np.clip(survival_treatment + 0.05, 0, 1), step="post", alpha=0.15)
ax.set_xlabel("Time (months)")
ax.set_ylabel("Survival Probability")
ax.legend(frameon=False)
ax.set_ylim(0, 1.05)
sp.save(fig, "nature_kaplan", formats=("pdf",))
```

---

## 配色方案展示

> SciPlot 内置多种科研友好配色，通过 `sp.setup_style()` 或 `sp.get_palette()` 调用。

### 所有内置配色

```python
"""配色方案一览 — 展示所有内置调色板"""
import sciplot as sp

palettes = [
    ("pastel",  "柔和粉彩 (默认)"),
    ("ocean",   "海洋蓝绿"),
    ("forest",  "森林渐变"),
    ("sunset",  "日落暖色"),
    ("earth",   "大地色系"),
    ("rdbu",    "红蓝发散"),
    ("coolwarm","冷暖发散"),
    ("100yuan", "百元人民币"),
    ("50yuan",  "五十元"),
    ("20yuan",  "二十元"),
    ("10yuan",  "十元"),
    ("5yuan",   "五元"),
    ("1yuan",   "一元"),
]

fig, axes = sp.paper_subplots(len(palettes), 1, venue="thesis")
for ax, (name, desc) in zip(axes, palettes):
    colors = sp.get_palette(name)
    for i, color in enumerate(colors):
        ax.barh(0, 1, left=i, color=color, edgecolor="white", linewidth=0.5)
    ax.set_xlim(0, len(colors))
    ax.set_yticks([])
    ax.set_title(f"{name}  —  {desc}", fontsize=8, loc="left")
    ax.set_xticks([])

sp.save(fig, "palette_overview", formats=("png",), dpi=300)
```

### 子集配色

```python
"""子集配色 — 从调色板中取前 N 个颜色"""
import sciplot as sp

# 取前 2 色
colors_2 = sp.get_palette("pastel-2")   # ['#A8D8EA', '#AA96DA']

# 取前 4 色
colors_4 = sp.get_palette("ocean-4")    # 4 种蓝色调

# 用法
sp.setup_style("thesis", "pastel-2", lang="zh")  # 只用 2 种颜色
```

### 场景推荐

| 场景 | 推荐配色 | 原因 |
|------|---------|------|
| 2-3 组对比 | `pastel-2` / `pastel-3` | 柔和不刺眼 |
| 4-6 组分类 | `ocean` / `forest` | 色相区分度高 |
| 热力/相关矩阵 | `rdbu` / `coolwarm` | 发散型，中性色居中 |
| 地理/环境 | `earth` / `forest` | 自然色调 |
| 演示/PPT | `sunset` | 鲜艳醒目 |
| 色盲友好 | `ocean` + `use_linestyles=True` | 蓝色系 + 线型区分 |
| 中国特色 | `100yuan` ~ `1yuan` | 人民币配色，独特有趣 |

### 色盲友好模式

```python
"""色盲友好 — 使用线型+标记区分"""
import numpy as np
import sciplot as sp

sp.setup_style("nature", "ocean", lang="en")

x = np.linspace(0, 10, 100)
fig, ax = sp.new_figure("nature")

for i, (label, style) in enumerate(zip(
    ["Method A", "Method B", "Method C"],
    [{"linestyle": "-"}, {"linestyle": "--"}, {"linestyle": ":"}]
)):
    ax.plot(x, np.sin(x + i * 0.5), label=label, **style, marker="o",
            markevery=20, markersize=5)

ax.legend()
ax.set_xlabel("X")
ax.set_ylabel("Y")
sp.save(fig, "colorblind_friendly", formats=("pdf",))
```

### 深色主题配色

```python
"""深色背景 — 演示/海报场景"""
import numpy as np
import sciplot as sp

sp.setup_style("presentation", "pastel", lang="zh", theme="dark")

x = np.linspace(0, 10, 200)
fig, ax = sp.plot(x, np.sin(x), xlabel="时间", ylabel="幅度", label="信号")
ax.legend()
sp.save(fig, "dark_theme", formats=("png",), dpi=300)
```

---

## API 速查

### 样式与配置
```python
sp.setup_style(venue="nature", palette="pastel", lang="zh", theme="light")
sp.set_defaults(venue="ieee", palette="earth")  # 设置后 setup_style() 自动读取
sp.style_context("ieee", palette="forest")       # 上下文管理器
```

### 5 种 API 风格
```python
# 1. 传统 API
fig, ax = sp.plot(x, y, xlabel="X", ylabel="Y")
sp.save(fig, "fig")

# 2. 链式调用
sp.style("nature").palette("pastel").plot(x, y).save("fig")

# 3. 简洁别名
fig, ax = sp.line(x, y, xlabel="X", ylabel="Y")

# 4. PlotResult 链式
sp.plot(x, y).xlabel("X").ylabel("Y").save("fig")

# 5. 上下文管理器
with sp.style_context("ieee", palette="ocean"):
    fig, ax = sp.plot(x, y)
    sp.save(fig, "fig")
```

### 配色速查
| 名称 | 风格 | 色数 |
|------|------|------|
| `pastel` | 柔和粉彩（默认） | 6 |
| `ocean` | 海洋蓝绿 | 6 |
| `forest` | 森林渐变 | 6 |
| `sunset` | 日落暖色 | 5 |
| `earth` | 大地色系 | 5 |
| `100yuan`~`1yuan` | 人民币主题 | 5 |
| `rdbu` / `coolwarm` | 发散型 | 7 |

子集: `pastel-2` 取前 2 色，`ocean-4` 取前 4 色。

### 保存选项
```python
sp.save(fig, "文件名")                                    # 默认 PDF + PNG 1200dpi
sp.save(fig, "文件名", formats=("png",), dpi=1200)         # Word 用
sp.save(fig, "文件名", formats=("pdf",))                   # LaTeX 用
sp.save(fig, "文件名", dir="outputs/figures")               # 指定目录
sp.save(fig, "文件名", close=True)                          # 保存后关闭释放内存
```

### 子图布局
```python
fig, axes = sp.paper_subplots(1, 2, venue="thesis")  # 精确匹配版心
fig, axes = sp.create_subplots(2, 2, venue="ieee")    # 按比例缩放
fig, gs = sp.create_gridspec(2, 3, venue="nature")    # 不规则布局
sp.add_panel_labels(axes)                              # (a)(b)(c) 标签
sp.add_panel_labels(axes, style="LETTER")              # (A)(B)(C) 标签
```

### 显著性标注
```python
sp.annotate_significance(ax, x1=1, x2=2, y=8.5, p_value=0.03)   # *
sp.annotate_significance(ax, x1=1, x2=3, y=9.5, p_value=0.0005)  # ***
```

### 智能辅助
```python
sp.auto_rotate_labels(ax)                    # 自动旋转标签
sp.smart_legend(ax, outside=True)            # 智能图例位置
sp.optimize_layout(fig)                      # 自动优化布局
sp.suggest_figsize(n_items=20)               # 建议尺寸
sp.check_color_contrast("#FFF", "#000")      # 对比度检查
```

---

## 黄金法则

```
1. Word 用 PNG 1200 DPI，LaTeX 用 PDF
2. 多子图用 paper_subplots() 锁定总宽
3. 中文用 lang="zh"，英文用 lang="en"
4. ≥4 条线用 use_linestyles=True（色盲友好）
5. 必须生成独立可运行的 Python 脚本
6. 默认无网格、刻度朝内（已自动设置）
7. 演示/屏幕场景用 theme="dark"
8. Nature/Science 用 venue="nature" 精确匹配版心
9. 显著性标注用 sp.annotate_significance()，不要手动画线
10. 配色用 sp.get_palette() 获取，不要硬编码颜色值
```

---

## 能力边界

| 不支持 | 替代方案 |
|--------|---------|
| 决策树可视化 | `sklearn.tree.plot_tree` |
| 神经网络结构 | `PlotNeuralNet` / `Netron` |
| 流程图 | `graphviz` / `Mermaid` |
| 交互式图表 | `plotly` / `pyecharts` |
| 地图/地理 | `cartopy` / `folium` |

---

## 完整文档

详细 API 参考: [references/full-api.md](./references/full-api.md)
场景配方: [references/recipes.md](./references/recipes.md)
配色与样式: [references/color-style.md](./references/color-style.md)

---

版本: **1.9.1** | PyPI: `pip install sciplot-academic` | GitHub: `rippleshe/sciplot-academic`
