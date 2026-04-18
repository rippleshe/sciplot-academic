# 配色重构与规范修复检查清单

## 配色系统

- [x] RMB_PALETTES 已完全移除
- [x] DIVERGING_PALETTES、SEQUENTIAL_PALETTES、THEME_PALETTES 已完全移除
- [x] pastel 配色更新为用户提供的6色渐变
- [x] ocean 配色更新为用户提供的6色渐变
- [x] forest 配色（森林蓝绿）已添加，6色
- [x] sunset 配色（日落暖色）已添加，5色
- [x] 每个配色系列的 -1 到 -N 子集已正确注册
- [x] ALL_BUILTIN_PALETTES 列表更新完整
- [x] list_palettes() 返回正确列表
- [x] get_palette("pastel") 返回正确颜色
- [x] get_palette("pastel-3") 返回前3种颜色
- [x] 旧 RMB 配色名称抛出适当错误
- [x] 模块文档字符串已更新

## 函数命名规范

- [x] 所有绘图函数使用 plot_<type> 命名
- [x] 同类功能函数命名一致
- [x] venue/palette 参数在所有绘图函数中位置一致
- [x] xlabel/ylabel/title 参数位置一致

## 参数默认值

- [x] 散点图 alpha 默认为 0.7
- [x] 填充图 alpha 默认为 0.3
- [x] venue 默认值为 None（从配置获取）
- [x] palette 默认值为 None（从配置获取）
- [x] xlabel/ylabel/title 默认值为 ""

## 文档字符串

- [x] 所有公开绘图函数有完整文档字符串
- [x] 所有公开绘图函数有 Returns 说明
- [x] 所有公开绘图函数有 Raises 说明（如适用）
- [x] 示例代码正确可运行

## 测试验证

- [x] 所有单元测试通过（356+）
- [x] 新配色正确加载
- [x] 配色子集正确注册
- [x] 无回归错误