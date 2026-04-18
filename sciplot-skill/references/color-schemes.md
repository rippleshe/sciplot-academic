# 配色方案

## 四大内置色系（推荐）

| 系列 | 风格 | 颜色数 | 子集 |
|------|------|--------|------|
| `pastel` | 柔和粉彩 | 6 | pastel-1~6 |
| `ocean` | 海洋蓝绿 | 6 | ocean-1~6 |
| `forest` | 森林渐变 | 6 | forest-1~6 |
| `sunset` | 日落暖色 | 5 | sunset-1~5 |

```python
sp.setup_style(palette="pastel-3")   # 使用前3色
sp.setup_style(palette="forest-4")   # 使用前4色
sp.setup_style(palette="ocean")      # 使用完整版
```

### 配色详情

**pastel（柔和粉彩）**
- 默认首选，适合大多数论文场景
- 颜色：`#845EC2 → #D65DB1 → #FF6F91 → #FF9671 → #FFC75F → #F9F871`

**ocean（海洋蓝绿）**
- 适合水文/海洋/气象类图表
- 颜色：`#5E98C2 → #26B3D1 → #00CCCB → #56E2B0 → #A6F18C → #F9F871`

**forest（森林渐变）**
- 适合生态/环保/农业类图表
- 颜色：`#5EC299 → #00B3A2 → #00A2AD → #0090B8 → #007DBD → #0067B9`

**sunset（日落暖色）**
- 适合能量/热力/温度类图表
- 颜色：`#D44132 → #F45E4A → #FF7A62 → #FF967C → #FFB296`

---

## 自定义配色

### 简单自定义

```python
# 简单自定义配色
sp.set_custom_palette(["#E74C3C", "#3498DB"], name="brand")
sp.setup_style(palette="brand")     # 2 色
sp.setup_style(palette="brand-1")   # 只取第1色
```

### 注册完整配色方案

```python
# 注册完整配色方案（支持自动选择）
my_scheme = {
    "single":    ["#264653"],
    "double":    ["#264653", "#2a9d8f"],
    "triple":    ["#264653", "#2a9d8f", "#e9c46a"],
    "quadruple": ["#264653", "#2a9d8f", "#e9c46a", "#f4a261"],
    "quintuple": ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"],
}
sp.register_color_scheme("mytheme", my_scheme)

# 使用
sp.setup_style(palette="mytheme-triple")  # 明确使用3色
sp.plot_multi(x, [y1, y2, y3], palette="mytheme")  # 自动选择3色
```

---

## 智能配色选择

```python
# 自动根据数据量选择配色子集
sp.plot_multi(x, [y1, y2])        # 自动使用 pastel-2
sp.plot_multi(x, [y1, y2, y3])    # 自动使用 pastel-3
sp.plot_multi(x, [y1, y2, y3, y4]) # 自动使用 pastel-4
```

---

## 配色工具函数

```python
# 列出所有可用配色
sp.list_palettes()
sp.list_resident_palettes()

# 列出特定系列子集
sp.list_pastel_subsets()
sp.list_ocean_subsets()
sp.list_forest_subsets()
sp.list_sunset_subsets()

# 获取配色 HEX 列表
colors = sp.get_palette("pastel")
colors = sp.get_palette("forest-3")

# 从 HEX 颜色列表生成渐变色
from sciplot.utils import generate_gradient
gradient = generate_gradient("#845EC2", "#F9F871", 5)
```
