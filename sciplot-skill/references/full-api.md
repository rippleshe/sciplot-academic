# SciPlot 完整 API 参考

## 安装

```bash
pip install sciplot-academic          # 基础
pip install sciplot-academic[ml]      # + scikit-learn
pip install sciplot-academic[stats]   # + scipy（统计图表）
pip install sciplot-academic[all]     # 全部
```

---

## 1. 核心函数

### plot / plot_line

```python
sp.plot(x, y, xlabel="", ylabel="", title="", label="", venue=None, palette=None, lang=None, **kwargs)
```

绘制单条折线图，返回 `PlotResult`。

| 参数 | 默认值 | 说明 |
|------|--------|------|
| x, y | — | 等长数组 |
| label | "" | 图例标签 |
| venue/palette/lang | None | 继承全局默认值 |

```python
fig, ax = sp.plot(x, np.sin(x), xlabel="时间 (s)", ylabel="电压 (V)")
```

### plot_multi

```python
sp.plot_multi(x, y_list, labels=None, xlabel="", ylabel="", title="", venue=None, palette=None, lang=None, **kwargs)
```

绘制多条折线图，自动选配色子集。`x` 可为共享数组或列表。

| 参数 | 默认值 | 说明 |
|------|--------|------|
| y_list | — | Y 数据列表 `[y1, y2, ...]` |
| labels | None | 图例标签，None 自动生成 |
| palette | "pastel" | N≤4 时自动选 `palette-N` |

```python
fig, ax = sp.plot_multi(x, [y1, y2], labels=["方法A", "方法B"], xlabel="时间", ylabel="准确率")
```

### plot_multi_line

```python
sp.plot_multi_line(x, y_list, labels=None, xlabel="", ylabel="", title="", venue=None, palette=None, lang=None, use_linestyles=False, show_legend=True, **kwargs)
```

多线折线图完整参数版。`use_linestyles=True` 叠加线型循环提升可读性。

```python
fig, ax = sp.plot_multi_line(x, [y1, y2, y3], labels=["Train", "Val", "Test"], use_linestyles=True)
```

### plot_scatter

```python
sp.plot_scatter(x, y, xlabel="", ylabel="", title="", label="", s=20, alpha=0.7, venue=None, palette=None, lang=None, **kwargs)
```

散点图。`s` 控制点大小，`alpha` 控制透明度。

```python
fig, ax = sp.plot_scatter(x, y, xlabel="X", ylabel="Y", s=30, alpha=0.6)
```

### plot_step

```python
sp.plot_step(x, y, xlabel="", ylabel="", title="", label="", where="mid", venue=None, palette=None, lang=None, **kwargs)
```

阶梯图，适用于 CDF、直方型折线。`where`: `"mid"` / `"pre"` / `"post"`。

```python
fig, ax = sp.plot_step(sorted_data, cdf, xlabel="值", ylabel="累积概率")
```

### plot_area

```python
sp.plot_area(x, y, xlabel="", ylabel="", title="", label="", alpha=0.3, fill=True, venue=None, palette=None, lang=None, **kwargs)
```

面积图。`fill=False` 仅画线。

```python
fig, ax = sp.plot_area(x, y, xlabel="时间", ylabel="数值", alpha=0.4)
```

### plot_multi_area

```python
sp.plot_multi_area(x, y_list, labels=None, xlabel="", ylabel="", title="", stacked=False, alpha=0.3, venue=None, palette=None, lang=None, **kwargs)
```

多组面积图。`stacked=True` 绘制堆叠面积图。

```python
fig, ax = sp.plot_multi_area(x, [y1, y2, y3], labels=["A", "B", "C"], stacked=True)
```

---

## 2. 柱状图家族

### plot_bar

```python
sp.plot_bar(categories, values, xlabel="", ylabel="", title="", width=0.6, venue=None, palette=None, lang=None, **kwargs)
```

单组柱状图，每个柱子自动赋不同颜色。

```python
fig, ax = sp.plot_bar(["方法A", "方法B", "方法C"], np.array([82.3, 85.1, 88.7]), ylabel="准确率 (%)")
```

### plot_grouped_bar

```python
sp.plot_grouped_bar(groups, data, xlabel="", ylabel="", title="", width=0.8, gap=0.05, show_values=False, value_fmt=".1f", legend_loc="best", venue=None, palette=None, lang=None, **kwargs)
```

分组柱状图（论文最常用）。`data` 为 `{方法名: [各组数值]}` 字典。

```python
methods = {"ResNet": [82, 84, 86], "ViT": [85, 87, 89]}
fig, ax = sp.plot_grouped_bar(["CIFAR-10", "CIFAR-100", "ImageNet"], methods, ylabel="准确率 (%)")
```

### plot_stacked_bar

```python
sp.plot_stacked_bar(categories, data, xlabel="", ylabel="", title="", width=0.6, show_values=False, value_fmt=".1f", legend_loc="best", venue=None, palette=None, lang=None, **kwargs)
```

堆叠柱状图。`data` 为 `{系列名: [各组数值]}` 字典。

```python
data = {"训练集": [80, 85], "测试集": [20, 15]}
fig, ax = sp.plot_stacked_bar(["模型A", "模型B"], data, ylabel="样本数", show_values=True)
```

### plot_horizontal_bar

```python
sp.plot_horizontal_bar(categories, values, xlabel="", ylabel="", title="", height=0.6, show_values=False, value_fmt=".1f", sort=False, venue=None, palette=None, lang=None, **kwargs)
```

水平柱状图。`sort=True` 按数值升序排列（最大值在顶部）。

```python
fig, ax = sp.plot_horizontal_bar(["特征A", "特征B", "特征C"], [0.85, 0.72, 0.91], sort=True)
```

### plot_lollipop

```python
sp.plot_lollipop(categories, values, xlabel="", ylabel="", title="", sort=True, marker_size=8, stem_width=2.0, baseline=0.0, venue=None, palette=None, lang=None, **kwargs)
```

棒棒糖图，适合类别排名与重要性展示。

```python
fig, ax = sp.plot_lollipop(["特征A", "特征B", "特征C"], [0.91, 0.85, 0.72])
```

### plot_combo

```python
sp.plot_combo(x, bar_data, line_data=None, xlabel="", ylabel_left="", ylabel_right="", title="", bar_width=0.35, venue=None, palette=None, lang=None, **kwargs)
```

柱+线双轴组合图。返回 `ComboPlotResult`，支持三元解包 `fig, ax_bar, ax_line`。

```python
result = sp.plot_combo(["Q1", "Q2", "Q3", "Q4"],
    bar_data={"销售额": [100, 120, 140, 160]},
    line_data={"增长率": [5, 8, 12, 15]},
    ylabel_left="万元", ylabel_right="%")
```

---

## 3. 分布图表

### plot_box

```python
sp.plot_box(data, labels=None, xlabel="", ylabel="", title="", showfliers=True, venue=None, palette=None, lang=None, **kwargs)
```

箱线图。`data` 为单个数组或数组列表。

```python
fig, ax = sp.plot_box([scores_a, scores_b, scores_c], labels=["算法A", "算法B", "算法C"], ylabel="得分")
```

### plot_violin

```python
sp.plot_violin(data, labels=None, xlabel="", ylabel="", title="", showmeans=False, showmedians=True, venue=None, palette=None, lang=None, **kwargs)
```

小提琴图，比箱线图更直观展示分布形状。

```python
fig, ax = sp.plot_violin([data_a, data_b], labels=["Method A", "Method B"], showmedians=True)
```

### plot_histogram

```python
sp.plot_histogram(data, bins=30, xlabel="", ylabel="Frequency", title="", density=False, alpha=0.75, venue=None, palette=None, lang=None, **kwargs)
```

直方图。`density=True` 归一化为概率密度。

```python
fig, ax = sp.plot_histogram(data, bins=40, density=True, xlabel="残差", ylabel="概率密度")
```

### plot_heatmap

```python
sp.plot_heatmap(data, row_labels=None, col_labels=None, xlabel="", ylabel="", title="", cmap="Blues", show_values=False, fmt=".2f", colorbar_label="", vmin=None, vmax=None, aspect="auto", venue=None, palette=None, lang=None, **kwargs)
```

热力图，适用于相关矩阵、混淆矩阵、参数扫描结果。

```python
corr = np.corrcoef(data.T)
fig, ax = sp.plot_heatmap(corr, row_labels=feat_names, col_labels=feat_names,
    cmap="RdBu_r", show_values=True, title="相关系数矩阵")
```

---

## 4. 误差与置信

### plot_errorbar

```python
sp.plot_errorbar(x, y, yerr, xlabel="", ylabel="", title="", label="", fmt="o", capsize=4, markersize=5, venue=None, palette=None, lang=None, **kwargs)
```

误差条图。`yerr` 支持标量、等长数组或 `[下限, 上限]`。

```python
fig, ax = sp.plot_errorbar(x, y_mean, y_std, xlabel="轮次", ylabel="损失 ± σ", fmt="o-")
```

### plot_confidence

```python
sp.plot_confidence(x, y_mean, y_std, xlabel="", ylabel="", title="", label_mean="Mean", label_std=None, n_std=1.0, alpha=0.25, fill_kwargs=None, venue=None, palette=None, lang=None, **kwargs)
```

带置信区间（阴影带）的折线图。`n_std=1.96` 画 95% CI。

```python
fig, ax = sp.plot_confidence(epochs, loss_mean, loss_std, n_std=1.96, label_std="95% CI")
```

---

## 5. 时间序列

### plot_timeseries

```python
sp.plot_timeseries(t, y, events=None, shade_regions=None, rolling_mean=None, xlabel="", ylabel="", title="", label="", marker=None, venue=None, palette=None, lang=None, **kwargs)
```

时序图，支持事件标注、背景区域、滚动均值。`t` 支持 datetime 或数值。

| 参数 | 说明 |
|------|------|
| events | `[{"time": x, "label": "事件名", "color": "red"}]` |
| shade_regions | `[{"start": x, "end": y, "color": "#CCC", "alpha": 0.2}]` |
| rolling_mean | 窗口大小，None 不绘制 |

```python
fig, ax = sp.plot_timeseries(dates, values, events=[{"time": t0, "label": "上线"}], rolling_mean=7)
```

### plot_multi_timeseries

```python
sp.plot_multi_timeseries(t, y_list, labels=None, events=None, shade_regions=None, xlabel="", ylabel="", title="", venue=None, palette=None, lang=None, **kwargs)
```

多条时序曲线。参数同 `plot_timeseries`。

```python
fig, ax = sp.plot_multi_timeseries(dates, [train_loss, val_loss], labels=["Train", "Val"])
```

### plot_slope

```python
sp.plot_slope(labels, before, after, left_label="Before", right_label="After", show_diff=True, show_grid=False, title="", venue=None, palette=None, lang=None, **kwargs)
```

斜率图，展示两时点或两条件变化。

```python
fig, ax = sp.plot_slope(["指标A", "指标B"], [80, 60], [90, 75], left_label="2023", right_label="2024")
```

---

## 6. 统计诊断

### plot_residuals

```python
sp.plot_residuals(y_true, y_pred, xlabel="预测值", ylabel="残差", title="残差图", show_zero_line=True, show_loess=False, venue=None, palette=None, lang=None, **kwargs)
```

残差图。`show_loess=True` 显示 LOESS 平滑曲线（需 statsmodels）。

```python
fig, ax = sp.plot_residuals(y_true, y_pred, title="模型残差分析")
```

### plot_qq

```python
sp.plot_qq(data, distribution="norm", xlabel="理论分位数", ylabel="样本分位数", title="Q-Q 图", show_line=True, venue=None, palette=None, lang=None, **kwargs)
```

Q-Q 图。`distribution`: `"norm"` / `"expon"` / `"uniform"` / `"t"`。

```python
fig, ax = sp.plot_qq(data, title="正态性检验")
```

### plot_bland_altman

```python
sp.plot_bland_altman(y1, y2, xlabel="均值", ylabel="差值", title="Bland-Altman 图", show_ci=True, ci=0.95, venue=None, palette=None, lang=None, **kwargs)
```

Bland-Altman 一致性分析图，需 scipy。

```python
fig, ax = sp.plot_bland_altman(method_a, method_b, title="两种方法一致性分析")
```

### plot_density

```python
sp.plot_density(data, xlabel="", ylabel="Density", title="", bw_method=None, fill=True, alpha=0.3, venue=None, palette=None, lang=None, **kwargs)
```

核密度估计曲线，需 scipy。

```python
fig, ax = sp.plot_density(data, xlabel="值", fill=True)
```

### plot_multi_density

```python
sp.plot_multi_density(data_list, labels=None, xlabel="", ylabel="Density", title="", bw_method=None, fill=False, alpha=0.2, venue=None, palette=None, lang=None, **kwargs)
```

多组密度对比，需 scipy。`fill=True` 填充密度曲线下方。

```python
fig, ax = sp.plot_multi_density([data_a, data_b], labels=["A", "B"], fill=True)
```

---

## 7. 多维/进阶

### plot_radar

```python
sp.plot_radar(categories, values_list, labels=None, fill=True, alpha=0.3, title="", show_grid=True, show_labels=False, venue=None, palette=None, lang=None, **kwargs)
```

雷达图/蜘蛛图，适合多维评估对比。

```python
categories = ["准确率", "召回率", "F1", "速度", "稳定性"]
fig, ax = sp.plot_radar(categories,
    [[0.95, 0.88, 0.91, 0.85, 0.92], [0.92, 0.91, 0.91, 0.90, 0.88]],
    labels=["方法A", "方法B"])
```

### plot_parallel

```python
sp.plot_parallel(data, columns=None, labels=None, color_by=None, normalize="minmax", show_colorbar=True, alpha=0.5, linewidth=1.0, title="", venue=None, palette=None, lang=None, **kwargs)
```

平行坐标图，展示多样本在多特征维度上的分布。`normalize`: `"minmax"` / `"zscore"` / `"none"`。`color_by` 按某列着色。

```python
fig, ax = sp.plot_parallel(data, columns=["特征A", "特征B", "特征C", "特征D"], color_by=0)
```

### plot_scatter_matrix

```python
sp.plot_scatter_matrix(data, columns=None, color_by=None, diag="hist", alpha=0.5, s=10, venue=None, palette=None, lang=None)
```

散点矩阵，展示多特征两两关系。`diag`: `"hist"` / `"kde"` / `"none"`。

```python
fig, axes = sp.plot_scatter_matrix(data, columns=["特征A", "特征B", "特征C"])
```

---

## 8. ML 扩展（`pip install sciplot-academic[ml]`）

### plot_pca

```python
sp.plot_pca(data, labels=None, n_components=2, venue=None, palette=None, lang=None, **kwargs)
```

PCA 降维可视化（2D）。`data` 为 `(n_samples, n_features)` 矩阵，`labels` 按类着色。

```python
fig, ax = sp.plot_pca(X, labels=y, venue="nature")
```

### plot_confusion_matrix

```python
sp.plot_confusion_matrix(y_true, y_pred, labels=None, normalize=False, cmap="Blues", venue=None, palette=None, lang=None, **kwargs)
```

混淆矩阵可视化。`normalize=True` 按真实类别归一化。

```python
fig, ax = sp.plot_confusion_matrix(y_test, y_pred, labels=class_names, normalize=True)
```

### plot_feature_importance

```python
sp.plot_feature_importance(features, importance, title="Feature Importance", top_n=None, venue=None, palette=None, lang=None, **kwargs)
```

特征重要性可视化（水平条形图，按重要性降序）。`top_n` 只显示前 N 个。

```python
fig, ax = sp.plot_feature_importance(feat_names, model.feature_importances_, top_n=15)
```

### plot_learning_curve

```python
sp.plot_learning_curve(train_scores, val_scores, train_sizes=None, xlabel="Training Examples", ylabel="Score", label_train="Training", label_val="Validation", venue=None, palette=None, lang=None, **kwargs)
```

学习曲线（训练集 vs 验证集得分随样本量变化）。

```python
fig, ax = sp.plot_learning_curve(tr_scores, va_scores, train_sizes=sizes)
```

---

## 9. 3D 扩展（内置）

### plot_surface

```python
sp.plot_surface(X, Y, Z, xlabel="", ylabel="", zlabel="", title="", cmap="viridis", alpha=1.0, elev=30, azim=-60, venue=None, palette=None, lang=None, **kwargs)
```

3D 曲面图。`X, Y` 由 `np.meshgrid` 生成。

```python
fig, ax = sp.plot_surface(X, Y, Z, xlabel="X", ylabel="Y", zlabel="Z")
```

### plot_contour

```python
sp.plot_contour(X, Y, Z, xlabel="", ylabel="", title="", levels=10, cmap="viridis", filled=False, show_labels=True, venue=None, palette=None, lang=None, **kwargs)
```

等高线图。`filled=True` 填充区域，`show_labels` 显示数值标签。

```python
fig, ax = sp.plot_contour(X, Y, Z, levels=15, filled=True)
```

### plot_3d_scatter

```python
sp.plot_3d_scatter(x, y, z, c=None, xlabel="", ylabel="", zlabel="", title="", s=20, alpha=0.7, cmap="viridis", elev=30, azim=-60, venue=None, palette=None, lang=None, **kwargs)
```

3D 散点图。`c` 按第四维度着色。

```python
fig, ax = sp.plot_3d_scatter(x, y, z, c=values, cmap="plasma")
```

### plot_wireframe

```python
sp.plot_wireframe(X, Y, Z, xlabel="", ylabel="", zlabel="", title="", color="#333333", alpha=0.8, rstride=1, cstride=1, elev=30, azim=-60, venue=None, palette=None, lang=None, **kwargs)
```

3D 线框图。`rstride` / `cstride` 控制网格密度。

```python
fig, ax = sp.plot_wireframe(X, Y, Z, rstride=2, cstride=2)
```

---

## 10. 网络与层次

### plot_network（`pip install networkx`）

```python
sp.plot_network(G, layout="spring", node_color_by=None, node_size_by=None, edge_weight_by=None, labels=True, node_size=300, node_alpha=0.8, edge_alpha=0.5, edge_width=1.0, with_arrows=True, title="", venue=None, palette=None, **kwargs)
```

网络图。`G` 为 networkx Graph/DiGraph。`layout`: `"spring"` / `"circular"` / `"spectral"` / `"shell"` / `"kamada_kawai"` / `"random"`。

```python
fig, ax = sp.plot_network(G, layout="spring", node_color_by="degree")
```

### plot_network_from_matrix

```python
sp.plot_network_from_matrix(adj_matrix, threshold=0.0, labels=None, layout="spring", venue=None, palette=None, **kwargs)
```

从邻接矩阵绘制网络图。`threshold` 过滤低权重边。

```python
fig, ax = sp.plot_network_from_matrix(adj, threshold=0.5, labels=["A", "B", "C"])
```

### plot_network_communities

```python
sp.plot_network_communities(G, communities, layout="spring", title="", venue=None, palette=None, **kwargs)
```

带社区结构的网络图。`communities` 为 `[[节点列表], ...]`。

```python
fig, ax = sp.plot_network_communities(G, communities)
```

### plot_dendrogram（`pip install scipy`）

```python
sp.plot_dendrogram(data_or_linkage, labels=None, orientation="top", color_threshold=None, title="", leaf_rotation=90, leaf_font_size=None, venue=None, palette=None, **kwargs)
```

树状图。`data_or_linkage` 接受数据矩阵或 linkage 矩阵。

```python
fig, ax = sp.plot_dendrogram(linkage_matrix, labels=sample_names)
```

### plot_clustermap

```python
sp.plot_clustermap(data, row_labels=None, col_labels=None, row_cluster=True, col_cluster=True, cmap="viridis", title="", venue=None, palette=None, **kwargs)
```

聚类热力图（热力图 + 行/列树状图）。无 scipy 时降级为普通热力图。

```python
fig, ax = sp.plot_clustermap(data, row_labels=row_names, col_labels=col_names)
```

---

## 11. 维恩图（`pip install matplotlib-venn`）

### plot_venn2

```python
sp.plot_venn2(subsets, set_labels=("A", "B"), title="", alpha=0.5, show_counts=True, venue=None, palette=None, **kwargs)
```

双集合 Venn 图。`subsets` 接受元组 `(仅A, 仅B, AB交集)` 或字典。

```python
fig, ax = sp.plot_venn2((10, 8, 5), set_labels=("方法A", "方法B"))
```

### plot_venn3

```python
sp.plot_venn3(subsets, set_labels=("A", "B", "C"), title="", alpha=0.5, show_counts=True, venue=None, palette=None, **kwargs)
```

三集合 Venn 图。`subsets` 接受元组 `(仅A, 仅B, AB, 仅C, AC, BC, ABC)` 或字典。

```python
fig, ax = sp.plot_venn3((10, 8, 5, 7, 4, 3, 2), set_labels=("A", "B", "C"))
```

---

## 12. 标注工具

### annotate_significance

```python
sp.annotate_significance(ax, x1, x2, y, p_value, h=0.02, tip_len=0.01, color="black", fontsize=None, ns_text="ns")
```

统计显著性标注（括号 + 星号）。规则：`p<0.001→***`，`p<0.01→**`，`p<0.05→*`，`p≥0.05→ns`。

```python
sp.annotate_significance(ax, 1, 2, y=95, p_value=0.03)
sp.annotate_significance(ax, 1, 3, y=100, p_value=0.0005)
```

### add_panel_labels

```python
sp.add_panel_labels(axes, labels=None, style="letter", x=-0.12, y=1.05, **kwargs)
```

为多子图添加面板标签 `(a)(b)(c)...`。`style`: `"letter"` / `"LETTER"` / `"number"` / `"roman"`。

```python
sp.add_panel_labels([ax1, ax2, ax3])
```

---

## 13. 智能辅助

### auto_rotate_labels

```python
sp.auto_rotate_labels(ax, axis="x", max_labels=10, threshold=6, rotation=45)
```

自动旋转轴标签以避免重叠。

```python
sp.auto_rotate_labels(ax)  # 自动检测并旋转 X 轴标签
```

### smart_legend

```python
sp.smart_legend(ax, loc="best", outside=False, ncols=None)
```

智能图例位置调整。`outside=True` 将图例放在图外右侧。

```python
sp.smart_legend(ax, outside=True)
```

### optimize_layout

```python
sp.optimize_layout(fig, tight=True)
```

自动优化图形布局，减少白边。

```python
sp.optimize_layout(fig)
```

### suggest_figsize

```python
sp.suggest_figsize(n_items, item_width=0.5, min_width=4.0, max_width=10.0, height_ratio=0.7) -> (width, height)
```

根据数据量建议合适的图形尺寸。

```python
figsize = sp.suggest_figsize(20, item_width=0.4)
fig, ax = plt.subplots(figsize=figsize)
```

### check_color_contrast

```python
sp.check_color_contrast(bg_color, fg_color, threshold=4.5) -> (passed, ratio)
```

检查颜色对比度是否符合 WCAG AA 标准。

```python
passed, ratio = sp.check_color_contrast("#FFF", "#000")
```

---

## 14. 配置系统

### setup_style

```python
sp.setup_style(venue="nature", palette="pastel", lang="zh", theme="light")
```

全局样式设置。`set_defaults(venue="ieee")` 后 `setup_style()` 自动读取。

### set_defaults

```python
sp.set_defaults(venue="ieee", palette="earth", lang="en", dpi=600, formats=("pdf", "png"))
```

设置全局默认值，影响后续所有 `setup_style()` 调用。

### get_config

```python
sp.get_config("venue")   # "nature"
sp.get_config()          # {"venue": "nature", "palette": "pastel", ...}
```

获取当前配置值。

### load_config

```python
sp.load_config()                   # 自动查找 .sciplot.toml / pyproject.toml
sp.load_config("path/to/config.toml")  # 指定路径
```

从配置文件加载设置。

### reset_config

```python
sp.reset_config()
```

重置所有用户设置和文件设置。

---

## 15. 链式调用

### style

```python
sp.style(venue) -> PlotChain
```

链式调用入口 — 设置期刊样式。

```python
fig = sp.style("nature").plot(x, y).save("output")
```

### palette

```python
sp.palette(palette_name) -> PlotChain
```

链式调用入口 — 设置配色方案。

```python
fig = sp.palette("earth").plot(x, y).save("output")
```

### chain

```python
sp.chain(venue=None, palette=None, lang=None) -> PlotChain
```

链式调用通用入口。

```python
fig = sp.chain("ieee", "earth", lang="en").plot(x, y).save("output")
```

### PlotChain

链式调用构建器类。支持方法：`style()`, `palette()`, `lang()`, `figsize()`, `plot()`, `scatter()`, `bar()`, `hist()`, `boxplot()`, `fill_between()`, `errorbar()`, `area()`。

```python
chain = sp.style("ieee").palette("forest")
fig = chain.plot(x, y, label="线1").scatter(x2, y2, label="散点").legend().save("output")
```

### FigureWrapper

`PlotChain` 绘图方法的返回类型，继承 `PlotResult`。额外方法：`get_figure()`, `get_axes()`, `unwrap()`。

---

## 16. 上下文管理器

### style_context / context

```python
sp.style_context(venue=None, palette=None, lang=None, theme=None, **rc_params) -> StyleContext
sp.context(...)  # 简写别名
```

临时切换样式，退出时自动恢复。支持嵌套。

```python
with sp.style_context("ieee", palette="earth"):
    fig, ax = sp.plot(x, y)
# 退出后恢复默认

with sp.style_context("presentation", theme="dark"):
    fig, ax = sp.plot(x, y)
```

### ieee_context

```python
sp.ieee_context(palette=None, lang=None, theme=None, **kwargs) -> StyleContext
```

IEEE 样式上下文。

```python
with sp.ieee_context(palette="earth"):
    fig, ax = sp.plot(x, y)
```

### nature_context

```python
sp.nature_context(palette=None, lang=None, theme=None, **kwargs) -> StyleContext
```

Nature 样式上下文。

```python
with sp.nature_context():
    fig, ax = sp.plot(x, y)
```

### thesis_context

```python
sp.thesis_context(palette=None, lang=None, theme=None, **kwargs) -> StyleContext
```

学位论文样式上下文。

```python
with sp.thesis_context(palette="ocean"):
    fig, ax = sp.plot(x, y)
```

---

## PlotResult 链式方法

所有绘图函数返回 `PlotResult`，支持：

```python
result = sp.plot(x, y)
result.xlabel("X").ylabel("Y").title("标题").save("fig")

# 多子图统一设置
result = sp.PlotResult(fig, axes)
result.xlabel("共同X").add_panel_labels().save("fig")
```

| 方法 | 说明 |
|------|------|
| `xlabel/ylabel(label)` | 设置轴标签 |
| `title(title)` / `suptitle(title)` | 设置标题 |
| `xlim/ylim(...)` | 设置范围 |
| `legend()` | 显示图例 |
| `grid(visible)` | 设置网格 |
| `tight_layout()` | 优化布局 |
| `plot/scatter(x, y)` | 添加图层 |
| `axhline/axvline(v)` | 参考线 |
| `annotate(text, xy)` | 标注 |
| `add_panel_labels()` | 面板标签 |
| `save(name)` / `show()` / `close()` | 输出 |

---

## 工具函数

```python
# 颜色工具
sp.hex_to_rgb("#FF0000")            # → (1.0, 0.0, 0.0)
sp.rgb_to_hex(1.0, 0.0, 0.0)       # → "#ff0000"
sp.lighten_color("#264653", 0.3)    # 变亮
sp.darken_color("#cdb4db", 0.3)     # 变暗
sp.generate_gradient("#000", "#FFF", 5)  # 渐变

# 布局
sp.new_figure(venue="nature")
sp.create_subplots(2, 2, venue="ieee")
sp.paper_subplots(1, 2, venue="thesis")
sp.create_gridspec(2, 3, venue="nature")
sp.create_twinx(ax)
sp.save(fig, "name", dpi=1200, formats=("pdf", "png"))
sp.list_paper_layouts("thesis")

# 诊断
sp.inspect()  # 打印环境信息
```
