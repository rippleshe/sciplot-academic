# Changelog

本文件记录 SciPlot Academic 的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## Unreleased

---

## [1.14.0] - 2026-08-24

### Fixed

- 修复 `audit_figure()` 将 colorbar、twin axis、边际分布辅助轴误判为独立论文面板的问题；
  `save()` 不再对这些组合图错误提示缺少 `(a)(b)` 标签。
- 修复 `plot_upset()` 的 `metadata["intersections"]` 泄露一次性 generator，
  现在返回可重复读取、可序列化的 tuple 列表。
- 修复 `plot_marginal()` 在保存时触发不兼容 `tight_layout` 警告。
- 修复 `plot_alluvial()` 流带贝塞尔路径未完整闭合造成的斜切/漏口，并增加
  `flow_alpha` / `node_width` 参数校验。
- 修复 `plot_circular_barplot()`、`plot_packed_bubble()`、`plot_waffle()`、
  `plot_sankey()`、`plot_treemap()`、`plot_donut()`、`plot_sunburst()` 的 palette
  应用顺序：显式 `palette=` 不再可能继承上一张图的颜色循环。
- 修复 `plot_treemap()` 忽略 `border_color` / `border_width` 的 API bug，并重做
  面积、画布尺寸和标签长度共同约束的字号与双行间距，避免大块文字过小或标签/数值挤压。
- 修复 `plot_sunburst()` 层级半径方向颠倒的问题：第一层现在位于内环，后代逐层向外展开；
  同时拒绝重复标签、与根不连通的环/孤立层级以及非法 `ring_gap`。
- 修复 `plot_packed_bubble()` 仅按半径估算字号导致长标签跨出气泡、互相覆盖的问题；
  现在基于最终坐标变换后的 renderer 像素边界适配文字，空间不足时宁可省略标签而不输出溢出文字，
  并补齐 `min_font` / `max_font` 校验与 Circle kwargs 覆盖语义。
- 修复 `plot_volcano()` 顶部自动标注只按数据坐标“错开”、却仍会与图例/相邻文字/轴框重叠的问题；
  现在按真实渲染后的 bounding box 逐个试放，并避免 `kwargs` 中 `c` / `alpha` 与火山图语义参数冲突。
- 修复 `plot_network3d()` 将标签直接贴在 3D 节点中心导致透视投影后集中重叠的问题；
  现在先固定最终视角，再将 top-N 节点投影到屏幕平面并按 renderer bbox 避让，同时降低边线默认视觉权重，
  使节点、标签和社区层级在静态科研图中更清楚。
- 修复 `plot_chord()` 的两处数据编码错误：节点弧长原先先占满 `2π` 再额外加入 `gap`，会使圆周超出一圈；
  弦端点也未按累计流量分槽，多条流会挤在固定位置。现在基于 `min_flow` 过滤后的可见流严格扣除全部 gap，
  并在源端/目标端按真实流量守恒切分弧段；`show_values=True` 同步显示过滤后的可见总量并使用稳定双行标签。
- 修复 `plot_ternary()` 两族斜向网格端点公式错误导致辅助线穿出 simplex 边界的问题；
  现在三族网格分别按 `a/b/c = 常数` 的重心坐标精确计算端点，所有线段严格落在等边三角形内部或边界上。

### Changed

- 进一步把出版级视觉下限固化为 SciPlot 自身契约：所有 venue 显式启用四边向内主/次刻度、完整四边轴脊、无框图例与稳定线宽/保存边距，不再依赖 SciencePlots 的间接默认；直接 `fig.savefig()` 的位图兜底提升至 600 DPI，`sp.save()` 仍保持配置默认 1200 DPI。
- 清理普通绘图函数与布局 helper 中历史遗留的 `tick_params(direction="in")` 补丁，让新建主轴统一由底层 publication rcParams 提供视觉纪律；showcase 全量重画验证删补丁不改变输出。
- `auto_rotate_labels()` 改为优先使用 renderer 的真实像素 bbox 判断标签是否碰撞，只有确实重叠时才旋转；`smart_legend()` 对 5–12 项自动使用多列布局，减少默认图例吞占绘图区。
- 多系列折线在当前 palette 颜色耗尽后自动增加线型冗余编码，避免同色同线型系列不可区分；`plot_multi()` / `plot_multi_line()` 同时修正为真正尊重 `set_defaults(palette=...)`。
- 统一 `add_colorbar()` 的辅助信息层级：拒绝非法 `fraction` / `pad`，并让 outline、ticks 与字号略弱于主轴而不改变默认版心几何；热力图、混淆矩阵、聚类图、棒棒糖图和平行坐标不再机械 45° 旋转类别标签，改为真实 bbox 碰撞后才旋转。
- `plot_multi_density()`、`plot_ridgeline()` 与 `plot_multi_timeseries()` 接入智能多列图例，在系列较多时自动压缩 legend 占用，少系列时保持原有单列行为。
- 统一多系列线图的冗余编码策略：`plot_multi_line()`、`plot_multi_timeseries()`、`plot_multi_density()`、`plot_ridgeline()` 在 palette 颜色复用后自动切换线型；用户显式 `linestyle` / `ls` 始终优先，显式单色 `color=` 时也会自动用线型维持系列可辨识度。
- `smart_legend()` 新增 IEEE/单栏窄画布压力策略：仅在 9 项以上、默认 `loc="best"` 且真实 renderer bbox 已明显侵占数据区时，将大型长图例移至图外下方，并按真实宽度控制列数；显式 `loc=` / `outside=True` 不受自动策略改写。
- 清理 PyPI sdist 发布内容：不再把 `.claude/`、`.github/`、docs、tests、50 张 showcase PNG、QA 临时目录和根目录调试图片打进源码分发包；发布工作流在上传前新增 `twine check`。
- 清理 showcase 中纯粹用于“补基础风格”的 `tick_params(direction="in")`，示例只保留图本身需要的特殊设置，用真实输出验证默认层即可维持出版级完成度。
- 重做并目视检查多个 showcase，降低雷达图填充遮挡、网络图边/标签密度，优化环形排名配色，
  并从实现层修复 Alluvial 流带视觉质量。
- Claude Skill 重构为精简的科研绘图工作流（Skill v2.0.0）：主文件聚焦选图、视觉纪律、
  audit 与真实视觉检查，完整 API/recipes/配色细节按需读取 references，且 Skill 版本与包版本解耦。
- 项目版本规范与现有 `setuptools-scm` 动态版本机制对齐，不再要求手改 `pyproject.toml` 静态版本。

### Tests

- 新增辅助 Axes 审计、UpSet 元数据、Alluvial 闭合路径、出版样式基线、多类图表 palette 隔离，
  Treemap 边框/字号、Sunburst 层级拓扑/环方向、Packed Bubble / Volcano / Network3D 像素级文字布局，
  Chord 圆周闭合/流槽守恒/过滤后总量、Ternary simplex 网格几何，以及所有 venue 四边 inward/minor tick 与 600 DPI 原生保存兜底契约测试。
- 最新全量验证：`1596 passed`；Ruff 全绿；Mypy 对 33 个源码文件无错误；47 个 showcase 脚本全部重跑并目视检查 50 张输出图；另以无 `setup_style()` / 无手工 tick / 无显式 DPI 的零配置调用实测原生 `fig.savefig()` 输出 600 DPI 完成图，并以 IEEE 3.5 英寸单栏对 12 系列长图例做 hostile 压力验证。

---

## [1.13.10] - 2026-08-04

### Added

- **11 个新短别名**：parallel / pca / slope / surface / contour /
  confusion / learning_curve / feature_importance / venn2 / venn3 / network

### Fixed

- **甘特图图例重复**：color_by 与 groups 同标签时图例出现两份
  → 按标签去重
- **分类色中文乱序**：4 处 `sorted(set(..., key=str))` 按 Unicode 码点排中文
  （中期 < 前期 < 后期）→ 改为首次出现顺序
  （gantt / parallel / 网络节点着色 / 其他 color_by）
- **桑基图标签重叠**：同层标签按 y 累积推挤，最小间距 0.045，
  多节点小流量时不再重叠

### Tests

- 新增：别名完整性、gantt 图例去重、sankey 标签避让、
  histogram 自定义色、box patch_artist 三态
- 总数 1537 passed

---

## [1.13.9] - 2026-08-04

### Fixed

- **plot_histogram 透传 color 崩溃**：内部硬编码 `color=colors[0]` 与
  用户 kwargs 冲突 → TypeError；改为显式 color 覆盖自动配色
- **plot_box 透传 patch_artist 崩溃**：内部硬编码 `patch_artist=True` 冲突；
  改为尊重用户值，且 `patch_artist=False` 时跳过面着色（boxes 为 Line2D）

### Changed

- 参数一致性扫描：验证 10 类图表的显式颜色参数均生效
  （donut/bar/scatter/waterfall/forest/sankey 等无硬编码覆盖）

### Tests

- 新增 histogram 自定义/默认色、box patch_artist 三态测试
- 总数 1535 passed

---

## [1.13.8] - 2026-08-04

### Added

- **plot_network / plot_network3d 边列表输入**：G 支持 networkx 图对象
  或边列表 `[(u, v)]` / 带权重 `[(u, v, w)]`（数值三元组自动转为
  `weight` 属性，可直接配 `edge_weight_by="weight"`）；
  非法输入给明确 TypeError

### Changed

- 全函数 dark theme 冒烟（52 个函数）：全部通过，无硬编码浅色元素
- 全 NaN/Inf 输入冒烟：全部优雅报错或安全处理

### Tests

- 新增 network 边列表/带权重/非法输入/3D 边列表 4 个测试
- 总数 1531 passed

---

## [1.13.7] - 2026-08-04

### Fixed

- **火山图标注重叠**：`annotate_top` 对 y 距离过近的 top 基因
  自动纵向错开（原先固定偏移，多个显著基因聚集时标签重叠）

### Tests

- 新增火山图标注重叠回归测试
- 总数 1527 passed

---

## [1.13.6] - 2026-08-04

### Fixed

- **audit_figure 3D 轴支持**：3D 图审计新增 z 轴标签检查，
  缺 z 标签时正确检出（原先只检查 x/y）

### Tests

- 新增 3D 审计测试（带 z 标签 clean / 缺 z 标签检出）
- 总数 1526 passed

---

## [1.13.5] - 2026-08-04

### Fixed

- **桑基图极小节点不可见**：新增 `min_node_height` 参数（默认 0.012），
  极小流量节点提升到最小可见高度（原先条高被 0.02 间隙吞掉只剩标签）；
  布局/流带/标签统一使用提升后高度，收缩时保证最小节点仍可见
- **docstring `**var:` 误解析**：9 处 `**kwargs:`/`**rc_params:` 参数行
  改为反引号包裹，消除 Sphinx "Inline strong start-string without end-string"；
  conf.py 加 `suppress_warnings=["docutils"]` 抑制 rst 可读性提示，
  Sphinx 构建从 139 警告 → 0 警告

### Changed

- showcase 34/35/37/38 重构为 `figure_panels(template=...)` 一键模板：
  34 条件矩阵、35 对照双列、37 流水线、38 时间推进，删除手写标签循环
  （37 比例从超宽 2.98 修正为 1.32）
- skill：recipes.md 追加 Meta 分析/UpSet/三联画/色盲安全配方

### Tests

- 新增桑基图 min_node_height 行为测试（提升生效 / 0 禁用）
- 总数 1525 passed

---

## [1.13.4] - 2026-08-03

### Fixed

- **冲积图流带对齐 bug**：流带高度改为按源/目标节点自身流量归一化
  （原用全局总量），修复节点流入≠流出时流带溢出节点条边界
  产生视觉残留细条的问题

### Tests

- 新增冲积图不平衡节点防溢出回归测试（流带不超出节点条 y 范围）
- 总数 1523 passed

---

## [1.13.3] - 2026-08-03

### Fixed

- **PlotResult.save / GridSpecResult.save 补 audit 参数**：与 layout.save 对齐，
  链式调用时可用 audit=False 关闭投稿质量审计
- **showcase 36 重构**：中心-辐条复合图改用 hero_layout("hub_spoke") API，
  替换手写 3×3 gridspec（代码 90 行 → 1 行布局），验证 API 落地
- **skill 同步**：触发词表补新图表关键词（森林/漏斗/旭日/UpSet/Meta 分析），
  版本号残留清理，全部同步至 v1.13.1

---

## [1.13.2] - 2026-08-03

### Fixed

- **字体回退链重构**：`font.family` 改用字体名列表（matplotlib 3.6+ 逐字符回退），
  en 模式混排中文不再缺字形；按系统已安装字体动态过滤，消除 findfont 警告噪音
- **tight_layout 兼容**：`_safe_tight_layout` 失败时回退 `constrained_layout`
  （支持 gridspec 多轴自定义布局），消除 marginal/raincloud 等图的布局警告
- **plot_taylor 输入兼容**：models 接受单个数组（自动命名），修复
  "truth value of an array is ambiguous" 崩溃
- **plot_combo 输入兼容**：bar_data/line_data 接受数组（自动包装单系列）
- **plot_upset 参数修复**：`intersection_color` 之前被渐变蓝硬编码覆盖失效
- **plot_network3d 增强**：Z 坐标默认归一化到 XY 量级（长尾分布不再压成平面），
  新增 `view=(elev, azim)` 视角参数与 `normalize_z` 开关
- **docs 修复**：conf.py 版本读取兼容 dynamic version（setuptools_scm）；
  补全 quickstart / api / examples / changelog 页面，Sphinx 构建恢复成功

### Tests

- 新增 plot_taylor/plot_combo 数组输入兼容测试（9 个）
- 更新 network3d z 语义测试（单调性 + normalize_z 开关）
- 总数 1522 passed

---

## [1.13.1] - 2026-08-03

### Fixed

- **旭日图重写**：弃用 ax.pie 单值 hack，改用 Wedge patch 直接绘制。
  修复扇区 autoscale 异常导致整图被压缩成竖条的问题；
  配色改为按第一层分支分配色相、层内按深度明度渐变，
  根节点不再绘制（中心留白，符合标准旭日图惯例）
- **矩形树图配色重做**：默认配色从多色循环改为单色系明度渐变
  （面积与颜色双编码有序），文字增加百分比标注
- **瀑布图补全标准结构**：start_value ≠ 0 时新增浅灰色期初条，
  累计连接线对齐；负值标签移至条底下方避免与正值重叠
- **UpSet 图打磨**：集合柱加柱尾数值、交集柱渐变蓝 + 加粗数值、
  点阵加大（先线后点）、底部标签自适应截断
- **漏斗图增强**：点大小随精度（1/SE²）加权、三角带加边界虚线、
  更清晰的参考线
- **排名变化图增强**：起点/终点大圆点、逐点圆点标记、末端排名小字、
  高亮对象最后绘制（前置置灰）

### Tests

- 瀑布图新增期初条行为测试（start=0 时不画，start≠0 时画且高度正确）
- 总数 1513 passed

---

## [1.13.0] - 2026-08-03

### Added

- **复合图模板系统**：`figure_panels(template=...)` 一键生成 Nature 级多面板布局，
  内置 5 大原型：`condition_matrix`（2×3 条件矩阵）/ `time_march`（2×2 时间推进）/
  `comparative`（1×2 对照双列）/ `pipeline`（1×5 流水线）/ `triptych`（3×2 临床三联画）
  - 模板自动配置网格结构、间距、共享轴策略与 **8pt 加粗面板标签**（Nature 规范）
  - 新增 `list_composite_templates()` 查询模板注册表
  - 显式参数可覆盖模板值，`template=None` 完全向后兼容
- **不对称 Hero 布局**：`hero_layout(template=...)` 主面板 + 卫星面板架构
  - `hero_right`（左侧 2/3 主面板 + 右双卫星）/ `hero_top`（顶部通栏 + 底部三列）/
    `hub_spoke`（3×3 中心 + 四向卫星）
  - `GridSpecResult` 新增 `ax_hero` / `satellites` / `ax_satellite(i)` 属性
- **6 个新图表类型**（均带简洁别名，纯 matplotlib 无新依赖）：
  - `plot_forest`（`forest`）：森林图，Meta 分析标配；交替行带、CI 区间、
    合并菱形、右侧数值标签
  - `plot_funnel`（`funnel`）：漏斗图，发表偏倚检测；95% 置信三角带、
    逆方差加权参考线
  - `plot_bump`（`bump`）：排名变化图，端点放大 + 末端直接标注，支持单条高亮
  - `plot_alluvial`（`alluvial`）：冲积图，多阶段类别流动（贝塞尔流带）
  - `plot_sunburst`（`sunburst`）：旭日图，分层占比（递归扇区）
  - `plot_upset`（`upset`）：UpSet 图，集合交集可视化（韦恩图替代方案）
- **色盲安全防线**（审稿七宗罪之一）：
  - `simulate_colorblind()`：Brettel-Viénot-Mollon (1997) 矩阵模拟三类色觉缺失
  - `check_colorblind_safe()`：色盲视角下颜色区分度校验
  - `audit_palette()`：内置配色色盲安全体检
  - 内置 **Okabe-Ito 色盲安全调色板**（okabe-ito / okabe-ito-4 / okabe-ito-6），
    可直接 `setup_style(palette="okabe-ito")`
- **投稿质量审计**（审稿七宗罪防线）：
  - `audit_figure()`：检查字号下限（Nature 最小 5pt）、多面板标签缺失、轴未标注
  - `save()` 默认执行必拒项审计（字号 + 面板标签），`audit=False` 或
    `set_defaults(audit=False)` 可关闭
- 新增 `relative_fontsize()` 字号工具（统一相对字号 + 下限保护）
- 新增 showcase 42–50（森林/漏斗/排名/冲积/旭日/UpSet/临床三联画/色盲安全/Hero 布局）

### Changed

- `figure_panels` 面板标签默认字号改为 8pt（模板场景，Nature 规范）
- `add_panel_labels` 支持通过 `fontsize` 参数显式控制标签字号
- 新图表内部统一使用 `relative_fontsize`，消除重复字号计算

### Tests

- 新增 119 个用例（复合图模板 12 / Meta 分析 14 / 排名冲积 16 / 旭日 Upset 20 /
  色盲安全 15 / Hero 布局 10 / 质量审计 11 / 回归加固 21），总数 1511 passed

---

## [1.12.6] - 2026-08-03

### Added

- 新增 3 个高级图表（均带别名，纯 matplotlib 无新依赖）：
  - `plot_streamgraph`（`streamgraph`）：流图，wiggle/center/zero 三种基线，
    Byron-Wattenberg 平滑，Evolution 家族经典类型
  - `plot_circular_barplot`（`circular_barplot`）：环形条形图，极坐标排名，
    外圈水平标签，默认降序
  - `plot_waterfall`（`waterfall`）：瀑布图，增/减/总计三色、累计虚线连接、
    起始值与数值标注
- 新增 `dual_encode_colors`：双编码配色生成器（色相 × 明度矩阵），
  复合图“行=色相、列=剂量梯度”一键生成
- `plot_grouped_bar` 新增 `colors` 参数（自定义系列颜色）
- `plot_heatmap` 支持 NaN 掩膜格（不写文字），相关矩阵下三角惯例可用
- 新增 showcase 39–41（流图/环形条形/瀑布）；05 改为下三角掩膜、
  02 本文方法高亮、03 协调配色、34 改用 dual_encode_colors

### Changed

- 重构：拆分 advanced.py（1807 → 1264 行），sankey 移至 `_plots/flow.py`，
  treemap/donut 移至 `_plots/proportions.py`，按图表家族归档

### Tests

- 新增 30 个用例（streamgraph 9 / circular_barplot 10 / waterfall 11 /
  dual_encode 9 / grouped_bar colors 4），总数 1413 passed

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
