更新日志
========

完整的变更记录见仓库根目录 ``CHANGELOG.md``。

v1.13.1 (2026-08-03)
--------------------

- 旭日图重写（Wedge patch，修复压缩竖条 bug，分支色相 + 层内明度渐变）
- 矩形树图单色系明度渐变 + 百分比标注
- 瀑布图补标准期初条结构
- UpSet / 漏斗 / 排名变化图视觉增强
- 修复：en 模式中文字体回退、tight_layout 兼容、plot_taylor/plot_combo 数组输入

v1.13.0 (2026-08-03)
--------------------

- 复合图模板系统：figure_panels(template=...) 五大原型 + triptych
- Hero 不对称布局：hero_layout()
- 6 个新图表：森林图 / 漏斗图 / 排名变化 / 冲积 / 旭日 / UpSet
- 色盲安全防线：simulate_colorblind / check_colorblind_safe / Okabe-Ito
- 投稿质量审计：audit_figure + save() 默认审计
