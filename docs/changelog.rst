更新日志
========

完整的变更记录见仓库根目录 ``CHANGELOG.md``。

v1.15.0 (2026-11-15)
--------------------

- **数据画像与智能选图**：新增 ``profile_data()`` 与 ``recommend_charts()``，自动识别数据形态并推荐高信息密度图表与配色
- **Vivid 高对比配色与连续色带**：新增 7 套 ``vivid`` 学术配色板、``list_vivid_palettes()`` 及 ``make_palette_cmap()``
- **视觉下限守卫**：新增 ``polish_axis()`` / ``inspect_figure_guards()`` / ``smart_labels()`` 等守卫函数与 ``audit_figure(..., check_visual_guards=True)``
- **5 个新图表**：帕累托 ``plot_pareto``、前后配对斜率 ``plot_paired``、概率预测扇形 ``plot_fan``、ROC/PR ``plot_roc``、概率校准 ``plot_calibration``
- **默认图型升级与缺陷修复**：升级散点回归/小提琴盒线/下三角显著性热图/PCA 置信椭圆，修复雨云/山脊中位数对齐及火山图引导线避让
- **Companion Skill v3.0.0**：接入先画像后推荐工作流（``scripts/profile_and_recommend.py``）

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
