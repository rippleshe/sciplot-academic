# Changelog

本文件记录 SciPlot Academic 的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.9.1] - 2026-07-01

### Added

- 新增 `showcase/` 示例画廊，包含 12 张代表性图表及对应 Python 脚本
- README 新增完整效果展示区域（基础图表、统计图表、高级图表、扩展模块）
- README 新增 AI Agent 集成章节与 `sciplot-skill` 使用说明
- README 新增场景推荐表（Word 中文论文 / IEEE / Nature / 学位论文 / 演示文稿）

### Changed

- 优化 README 结构，采用居中表格展示图表缩略图
- 更新 PyPI 分类器，标注为 Beta 阶段

### Fixed

- 修复 `inspect()` 函数在缺少字体时的异常处理

---

## [1.9.0] - 2026-06-15

### Added

- 新增网络图扩展 `plot_network()`、`plot_network_from_matrix()`、`plot_network_communities()`
- 新增层次聚类扩展 `plot_dendrogram()`、`plot_clustermap()`
- 新增维恩图扩展 `plot_venn2()`、`plot_venn3()`
- 扩展模块采用延迟加载（lazy loading）机制，未安装依赖时给出友好提示
- 新增 `[network]`、`[venn]` 可选依赖组

### Changed

- `_ext` 目录重构，拆分为独立模块：`network.py`、`hierarchical.py`、`venn.py`
- `__getattr__` 实现线程安全的延迟导入

---

## [1.8.0] - 2026-05-20

### Added

- 新增统计诊断图表模块 `_plots/statistical.py`
- 新增 Q-Q 图 `plot_qq()`，支持正态性检验可视化
- 新增 Bland-Altman 图 `plot_bland_altman()`，支持一致性分析
- 新增核密度估计 `plot_density()` 和多组密度对比 `plot_multi_density()`
- 新增残差图 `plot_residuals()`，用于模型诊断
- 新增 `[stats]` 可选依赖组（scipy>=1.10.1）
- 为所有统计图表添加简洁别名：`qq()`、`bland_altman()`、`density()`、`residuals()`

---

## [1.7.0] - 2026-04-10

### Added

- 新增多维图表模块 `_plots/multivariate.py`
- 新增平行坐标图 `plot_parallel()`，支持高维数据可视化
- 新增散点矩阵图 `plot_scatter_matrix()`，支持变量关系探索

### Changed

- 优化大数据量场景下的渲染性能

---

## [1.6.0] - 2026-03-01

### Added

- 新增时间序列图表模块 `_plots/timeseries.py`
- 新增时间序列图 `plot_timeseries()`，支持日期轴自动格式化
- 新增多条时序曲线 `plot_multi_timeseries()`
- 新增斜率图 `plot_slope()`，适合前后对比分析
- 为时序图表添加别名：`timeseries()`、`multi_timeseries()`

---

## [1.5.0] - 2026-02-01

### Added

- 新增 3D 可视化扩展模块 `_ext/plot3d.py`
- 新增 3D 曲面图 `plot_surface()`
- 新增等高线图 `plot_contour()`
- 新增 3D 散点图 `plot_3d_scatter()`
- 新增线框图 `plot_wireframe()`

### Changed

- 3D 扩展为可选依赖，未安装时通过延迟加载给出提示

---

## [1.4.0] - 2026-01-15

### Added

- 新增机器学习可视化扩展模块 `_ext/ml.py`
- 新增 PCA 降维可视化 `plot_pca()`
- 新增混淆矩阵 `plot_confusion_matrix()`
- 新增特征重要性图 `plot_feature_importance()`
- 新增学习曲线 `plot_learning_curve()`
- 新增 `[ml]` 可选依赖组（scikit-learn>=1.0.0）

---

## [1.3.0] - 2025-12-20

### Added

- 新增极坐标图表模块 `_plots/polar.py`
- 新增雷达图 `plot_radar()`，支持多维度对比展示
- 为雷达图添加别名 `radar()`

---

## [1.2.0] - 2025-11-15

### Added

- 新增高级图表模块 `_plots/advanced.py`
- 新增误差条图 `plot_errorbar()`，支持标准差/标准误/置信区间
- 新增置信区间图 `plot_confidence()`
- 新增热力图 `plot_heatmap()`，支持数值标注和自定义色阶
- 为高级图表添加别名：`errorbar()`、`confidence()`、`heatmap()`

---

## [1.1.0] - 2025-10-01

### Added

- 新增分布图表模块 `_plots/distribution.py`
- 新增柱状图 `plot_bar()`、分组柱状图 `plot_grouped_bar()`、堆叠柱状图 `plot_stacked_bar()`
- 新增水平柱状图 `plot_horizontal_bar()`、棒棒糖图 `plot_lollipop()`
- 新增箱线图 `plot_box()`、小提琴图 `plot_violin()`、直方图 `plot_histogram()`
- 新增组合图 `plot_combo()`（柱状 + 折线，双 Y 轴）
- 新增显著性标注工具 `annotate_significance()`（*/**/***）
- 为分布图表添加完整别名系统

### Changed

- 配色系统重构，新增 `pastel`、`ocean`、`forest`、`sunset`、`earth` 五大色系
- 新增人民币主题配色（6 个面额）和发散配色

---

## [1.0.0] - 2025-09-01

### Added

- 首次正式发布
- 核心样式系统 `_core/style.py`：支持 Nature/IEEE/APS/Springer/Thesis/Presentation 期刊样式
- 配色系统 `_core/palette.py`：内置多套学术配色方案
- 布局系统 `_core/layout.py`：`create_subplots()`、`paper_subplots()`、`save()`
- 基础图表模块 `_plots/basic.py`：折线图、多线图、散点图、阶梯图、面积图
- 链式调用 API `_core/fluent.py`：`sp.style("nature").palette("pastel").plot(x, y).save()`
- 上下文管理器 `_core/context.py`：`style_context()`、`ieee_context()`、`nature_context()`
- 增强返回类型 `_core/result.py`：`PlotResult` 链式操作
- 配置系统 `_core/config.py`：`set_defaults()` 持久化默认值
- 工具函数 `utils/`：颜色工具、智能辅助（标签旋转、图例优化、布局调整）
- 中文优化：默认宋体环境，IEEE 中文字号自动调优
- 完整类型标注与 `py.typed` 支持

[1.9.1]: https://github.com/rippleshe/sciplot-academic/compare/v1.9.0...v1.9.1
[1.9.0]: https://github.com/rippleshe/sciplot-academic/compare/v1.8.0...v1.9.0
[1.8.0]: https://github.com/rippleshe/sciplot-academic/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/rippleshe/sciplot-academic/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/rippleshe/sciplot-academic/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/rippleshe/sciplot-academic/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/rippleshe/sciplot-academic/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/rippleshe/sciplot-academic/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/rippleshe/sciplot-academic/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/rippleshe/sciplot-academic/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/rippleshe/sciplot-academic/releases/tag/v1.0.0
