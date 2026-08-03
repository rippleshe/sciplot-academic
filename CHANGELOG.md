# Changelog

本文件记录 SciPlot Academic 的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.12.5] - 2026-08-03

### Fixed

- 修复 `plot_sankey` 自环（源==目标）导致层级分配 while 死循环
- `plot_donut` 外圈标签溢出画布修复（label_radius 收窄 + 画布余量动态扩展），
  新增 `center_text` 中心总文本与小扇区（<22°）数值溢出保护

### Added

- 复合图模板补齐 Nature 五大布局原型（showcase 36–38）：
  - 中心-辐条（hub-and-spoke）：中心总览 + 4 卫星面板 + 虚线辐条
  - 流水线（pipeline）：5 阶段横向 + 阶段间箭头
  - 时间推进（time-march）：时刻快照网格 + 共享色标
- 复合图配色体系：条件矩阵改为双编码（行=色相、列=剂量明度梯度），
  对照双列改为“中性灰蓝基线 vs 饱和主色方法”
- README 画廊扩至 38 张；skill 新增“复合图模板”章节（五大原型 + 规范）

### Tests

- 新增 6 个边界用例（sankey 自环 / donut 单类与极端占比 / treemap 偏斜 /
  figure_panels 单面板），总数 1370 passed

---

## [1.12.4] - 2026-08-03

### Added

- 新增 3 个高级图表（均带别名，保持现有配色体系）：
  - `plot_sankey`（`sankey`）：桑基图，纯 matplotlib 分层布局，
    节点高度与流量带宽度均正比于流量，支持 labels dict / node_colors / min_flow
  - `plot_treemap`（`treemap`）：矩形树图，内置 squarify 算法，
    面积编码占比，字号随矩形尺寸自适应，支持自定义颜色
  - `plot_donut`（`donut`）：环形图，中心挖空 + 外圈“类别+百分比”标签，
    环内数值，避免百分比与数值重叠
- 新增 `figure_panels`：Nature 级复合图布局（宽高比 / 自动面板标签 /
  共享轴 / 面板间距），对齐 Nature 投稿惯例（89mm/183mm 尺寸体系）
- `plot_multi_line` 新增 `highlight_last`：最后一条线加粗 + 星形标记，
  对比图中突出“本文方法”的惯例做法
- 新增 showcase 31–35：桑基（能源流）/ 矩形树图（半导体市场）/ 环形图
  （经费构成）/ 复合图·条件矩阵 2×3 / 复合图·对照双列 1×2
- README 画廊扩展至 35 张

### Changed

- 重构：提取 `cycle_color` 统一 33 处循环取色（空列表回退防护）；
  提取 `add_colorbar` 统一 15 处 colorbar 创建（期刊默认参数收敛）
- showcase 01 重做：本文方法高亮（加粗 + 星标）+ 浅网格

### Tests

- 新增 48 个用例（sankey 13 / treemap 14 / donut 9 / figure_panels 12），
  总数 1364 passed

---

## [1.12.3] - 2026-08-03

### Changed

- 提取 `new_styled_figure` 公共入口：统一 apply_resolved_style + new_figure
  配对，消除 11 个文件约 40 处样板代码；`create_sciplot_figure` 复用同一路径
- 提取 `_require_optional`/`_try_import_optional`：统一 scipy/sklearn/
  matplotlib-venn 等可选依赖的降级与报错提示
- 提取 `_is_constant`（KDE 常数退化判断）、`_coerce_to_date`（日历日期转换）、
  `_is_datetime_value`（日期类型判断），分别消除 5/3/3 处重复
- `new_figure` 成为取色安全入口（内部保证 prop_cycle 非空），删除
  statistical.py 7 处冗余调用，空颜色循环崩溃防护覆盖全库

### Fixed

- 修复 `plot_volcano` 在 p=0 时的 log10 除零 RuntimeWarning

### Tests

- 新增 12 个用例（_coerce_to_date ×4、refactor helpers ×9 等），
  总数 1316 passed

---

## [1.12.2] - 2026-08-03

### Changed

- CI 全面修复并全绿（三平台 × 四 Python 版本 × lint/typecheck/build 共 15 job）：
  - typecheck job 修复 8 处 mypy 错误
  - 全部 job 改用 `uv sync --frozen` 锁定依赖，消除依赖漂移
  - 修复 macOS 符号链接（/var→/private/var）与 Windows 8.3 短名导致的
    跨平台路径断言失败
  - pandas 纳入 test 依赖（双版本 marker：py3.11+ 用 3.x，py3.10 用 2.x），
    DataFrame 测试进入 CI 全平台
- 重构（纯内部，无 API 变化）：
  - 提取 `contrast_text_color` 公共工具，消除 4 处亮度对比重复
  - 提取 `get_cmap_safe`/`polar_to_cart` 公共工具，消除 4 处重复
  - `plot3d._new_3d_figure` 统一 3D 图形创建，消除 5 处重复
  - network 模块 `_get_label_font_family` 消除 3 处字体获取重复
  - `_resolve_norm` 统一 vmin/vmax 推断（含除零防护）
  - Windows 保留设备名提为模块级 frozenset 常量

### Fixed

- 修复 `plot_volcano` 在 p=0 时的 log10 除零 RuntimeWarning
  （np.where 全量求值改用 safe_p + errstate）

---

## [1.12.1] - 2026-08-03

### Changed

- CI 修复：typecheck job 8 处 mypy 错误（泰勒图/边际分布/气泡图/网络图）；
  全部 job 从 `uv pip install --system` 改为 `uv sync --frozen` 锁定依赖，
  消除依赖漂移导致的偶发失败
- 弦图升级：贝塞尔线改为渐变宽度 Polygon（源端宽目标端窄）、
  `color_by` 分组着色 + 图例、`min_flow` 低频过滤、源端按流量比例定位
- 打包气泡图升级：`color_by` 分组 + 图例、浅阴影层次、文字自动对比色、
  `min_size_frac` 保证小气泡可见（跨数量级数据）
- 哑铃图升级：改善/恶化分色连线、起点空心 + 终点实心双编码、
  起点均值参考线、数值标签上下交替防重叠
- 甘特图升级：`groups` 阶段背景色带、`milestones` 菱形标记、
  `dependencies` L 形依赖箭头、`now` 当前时间线
- 3D 网络图：恢复 depthshade 深度明暗、节点柔和描边、细淡边线、标签 halo，
  消除塑料感

### Fixed

- 修复 `plot_network3d` 无 node_color_by 时按字符遍历颜色字符串崩溃

---

## [1.12.0] - 2026-08-03

### Added

- 新增 `plot_volcano` 火山图：组学差异分析，log2FC × -log10(p)，
  三分类着色（上调/下调/不显著）、阈值参考线、top-N 标注、p=0 处理（别名 `volcano`）
- 新增 `plot_calendar_heatmap` 日历热图：全年活动强度按周排列，
  月份分隔线、跨年支持、字符串日期解析（别名 `calendar_heatmap`）
- 新增 `plot_taylor` 泰勒图：模型综合评估，角度编码相关系数、
  半径编码标准差比、距离编码 RMS 误差（别名 `taylor`）
- 新增 `plot_chord` 弦图：节点间流量/共现关系，贝塞尔弦线、
  弧长编码节点总量（别名 `chord`）
- 新增 `plot_ternary` 三角相图：三组分占比投影，自动归一化、
  平行网格、连续着色（别名 `ternary`）
- 新增 `plot_waffle` 华夫图：rows×cols 格子占比构成，余数补齐、
  百分比图例（别名 `waffle`）

### Fixed

- 修复 `plot_confidence` 接受纯 list 输入崩溃（内部转 numpy 数组），
  并新增长度一致与 y_std 非负校验
- 修复 `plot_bar` 显式 color 参数与自动配色冲突（kwargs 覆盖）
- 修复 `plot_parallel` 对含分类列 DataFrame 崩溃：自动提取数值列，
  color_by 分类列仅用于着色与图例；兼容 pandas 3.x StringDtype
- 消除 boxplot 的 `vert` 弃用警告：新增 `boxplot_with_orientation` 兼容辅助，
  raincloud/beeswarm/marginal 全部迁移

---

## [1.11.1] - 2026-08-03

### Changed

- 重构 skill 目录：`sciplot-skill/` 迁移至 `.claude/skills/sciplot/`（Claude Code 标准位置），
  SKILL.md 元数据标准化为 YAML frontmatter（name/description/version/author/…），
  skill 名从 `sciplot-skill` 改为规范的 `sciplot`
- README 修正 skill 引用路径与失效的文档链接

---

## [1.11.0] - 2026-08-03

### Added

- 新增 `plot_marginal` 边际分布图：主散点 + 顶部/右侧边缘分布
  （直方图/箱线/KDE 可选），支持相关系数标注（别名 `marginal`）
- 新增 `plot_raincloud` 雨云图：原始数据点 + 箱线 + 半小提琴三合一
  （Allen et al., 2021），支持水平/垂直两种方向（别名 `raincloud`）
- 新增 `plot_beeswarm` 蜂群图：确定性 swarm 布局或随机抖动，
  可叠加箱线（别名 `beeswarm`）
- 新增 `plot_dumbbell` 哑铃图：两时点前后对比，支持 delta/start/end 排序
  （别名 `dumbbell`）
- 新增 `plot_diverging_bar` 发散条形图：正负双向水平条形（别名 `diverging_bar`）
- 新增 `plot_gantt` 甘特图：任务时间线，数值/datetime 双轴，支持类别着色
  （别名 `gantt`）
- 新增 `plot_packed_bubble` 打包气泡图：圆形面积编码占比，
  黄金角螺旋贪心打包保证无重叠（别名 `packed_bubble`）
- 新增 `plot_network3d` 3D 网络图：节点 Z 轴映射属性，分类图例/连续 colorbar
- `plot_network` 系统性升级：top-N 标签（按度降序，大图友好）、seed 可复现、
  layout_kwargs 透传、映射范围参数化、分类图例、连续 colorbar、确定性配色
- `plot_network_communities` 升级：社区自动检测（greedy_modularity）、
  社区图例、标签控制、seed/layout_kwargs

### Changed

- 图表默认无标题原则：`plot_feature_importance`/`plot_residuals`/`plot_qq`/
  `plot_bland_altman` 默认 title 改为空字符串，showcase 全部去标题
- `setup_style()` 新增 `usetex` 参数：默认关闭（避免中文混排触发 latex 崩溃），
  显式 True 启用（无 LaTeX 时警告回退），中文模式强制禁用

### Fixed

- 修复 `add_panel_labels` 对 3D 子图崩溃（改用 text2D）
- 修复 `StyleContext` 浅拷贝 rcParams 导致嵌套列表修改污染外部状态（改深拷贝）
- 修复 `plot_network` 字符串属性（node_size_by/edge_weight_by）崩溃
- 修复 `save()` 对 Windows 保留设备名（CON/PRN/NUL/COM1 等）写入控制台
- 修复英文模式自动开启 LaTeX 后中文标签保存崩溃

---

## [1.10.0] - 2026-08-03

### Added

- 新增 `plot_bubble_heatmap` 气泡热力图：格子底色 + 气泡大小双重编码数值，
  支持自动对比度标注、零值隐藏、NaN 跳过（别名 `bubble_heatmap`）
- 新增 `plot_waterfall3d` 3D 瀑布图：多组曲线沿第三轴堆叠，支持填充带、
  组间距、基线偏移（别名 `waterfall3d`）
- 新增 `plot_bubble` 二维气泡图：气泡面积编码第三维数值，支持颜色通道、
  分类图例、数值标注（别名 `bubble`）
- 新增 `plot_ridgeline` 山脊图：多组 KDE 分布堆叠对比，支持重叠比例、
  中位数刻度线（别名 `ridgeline`）
- 新增 `plot_hexbin` 六边形密度图：大样本二维密度可视化，支持 log 计数
  （别名 `hexbin`）
- `plot_heatmap` 新增 `annot_color` 参数：数值标注自动依据格子亮度选择
  黑/白文字，保证对比度可读性

### Changed

- 主题系统：`setup_style()` 现在会读取 `set_defaults(theme=...)` 配置；
  显式 `theme="light"` 会真正复位暗色参数；切换 venue 时保持当前主题；
  `style_context()` 支持 theme 状态的保存与恢复
- `plot_3d_scatter` 颜色参数鲁棒化：标量/字符串/单元素数组 c 不再崩溃，
  c=None 时不再发出 cmap 忽略警告，颜色条仅在可映射数组时创建
- `plot_radar` 接受 1D/2D ndarray 输入；`plot_density`/`plot_multi_density`/
  `plot_ridgeline` 对常数序列退化为垂直线而非 KDE 崩溃；
  `plot_bland_altman` 对单点数据给出明确校验

### Fixed

- 修复 `set_defaults(theme=...)` 被 `setup_style()` 忽略的问题
- 修复从暗色主题切换回浅色主题时暗色参数残留的问题
- 修复 `style_context` 退出时 theme 状态未恢复的问题
- 修复 `plot_3d_scatter(c=标量)` 抛 ValueError 的问题
- 修复 3D 散点 c=None 时 matplotlib 的 colormapping 警告

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
