# Tasks

## 第一阶段：配色系统重构

- [x] Task 1: 重构 palette.py 配色体系
  - [x] 移除 RMB_PALETTES
  - [x] 移除 DIVERGING_PALETTES、SEQUENTIAL_PALETTES、THEME_PALETTES
  - [x] 更新 PASTEL_PALETTE 颜色为用户提供的渐变配色
  - [x] 更新 OCEAN_PALETTE 颜色为用户提供的渐变配色
  - [x] 新增 FOREST_PALETTE（森林蓝绿渐变）
  - [x] 新增 SUNSET_PALETTE（日落暖色渐变）
  - [x] 更新 ALL_BUILTIN_PALETTES
  - [x] 移除相关的 list_* 函数（list_diverging_palettes 等）

- [x] Task 2: 更新 palette.py 模块文档
  - [x] 更新模块顶部的配色体系说明
  - [x] 更新 set_custom_palette 的警告信息（最大颜色数）
  - [x] 更新 get_palette 的错误消息

- [x] Task 2b: 更新 __init__.py 和 _core/__init__.py 导入和导出
  - [x] 移除 list_rmb_palettes、get_diverging_palette 等已删除函数的导入
  - [x] 添加 list_forest_subsets、list_sunset_subsets 的导入
  - [x] 添加 FOREST_PALETTE、SUNSET_PALETTE 的导入
  - [x] 移除 RMB_PALETTES、DIVERGING_PALETTES 等已删除常量的导入
  - [x] 更新 __all__ 列表

## 第二阶段：函数命名规范化

- [x] Task 3: 检查 _plots/basic.py 函数命名
  - [x] 确认所有绘图函数使用 plot_<type> 命名
  - [x] 检查参数命名一致性（xlabel/ylabel/title 位置）

- [x] Task 4: 检查 _plots/distribution.py 函数命名
  - [x] 确认 plot_combo 返回 PlotResult（已修复）
  - [x] 检查参数命名一致性

- [x] Task 5: 检查 _ext 模块函数命名
  - [x] 确认 ml.py、plot3d.py、hierarchical.py、network.py、venn.py 中所有绘图函数使用 plot_<type> 命名
  - [x] 检查参数位置一致性（venue/palette 在 **kwargs 之前）

## 第三阶段：文档与默认值修复

- [x] Task 6: 补充缺失的文档字符串
  - [x] 检查 _plots 目录下所有函数的文档字符串
  - [x] 检查 _ext 目录下所有函数的文档字符串
  - [x] 确保 Returns/Raises 部分完整

- [x] Task 7: 统一参数默认值
  - [x] 检查所有绘图函数的 alpha 默认值
  - [x] 检查 venue/palette 默认值为 None
  - [x] 检查 xlabel/ylabel/title 默认值为 ""

## 第四阶段：测试验证

- [x] Task 8: 验证配色重构
  - [x] 确认新配色正确加载
  - [x] 确认子集（-N）正确注册
  - [x] 确认旧配色名称抛出适当错误

- [x] Task 9: 运行全部测试
  - [x] 确保所有 356 测试通过
  - [x] 修复因配色变更导致的测试失败

# Task Dependencies

- Task 2 依赖 Task 1
- Task 2b 依赖 Task 1
- Task 3-5 可并行执行
- Task 6-7 可并行执行
- Task 8 依赖 Task 1-2
- Task 9 依赖 Task 1-8