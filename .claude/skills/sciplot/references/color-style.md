# SciPlot 配色与样式参考

## 1. 配色系统

### 基础色系（自动子集）

| 系列 | 风格 | HEX 色值 | 子集 |
|------|------|---------|------|
| `pastel` | 柔和粉彩（默认） | #845EC2 → #D65DB1 → #FF6F91 → #FF9671 → #FFC75F → #F9F871 | pastel-1 ~ pastel-6 |
| `ocean` | 海洋蓝绿 | #5E98C2 → #26B3D1 → #00CCCB → #56E2B0 → #A6F18C → #F9F871 | ocean-1 ~ ocean-6 |
| `forest` | 森林渐变 | #5EC299 → #00B3A2 → #00A2AD → #0090B8 → #007DBD → #0067B9 | forest-1 ~ forest-6 |
| `sunset` | 日落暖色 | #D44132 → #F45E4A → #FF7A62 → #FF967C → #FFB296 | sunset-1 ~ sunset-5 |
| `earth` | 大地色系 | #264653 → #2a9d8f → #e9c46a → #f4a261 → #e76f51 | earth-1 ~ earth-5 |

### 人民币主题

| 系列 | 说明 | 色值 |
|------|------|------|
| `100yuan` | 百元红 | #780018 → #AA0033 → #DD0022 → #CC0044 → #FA8095 |
| `50yuan` | 五十元绿 | #25362B → #276E3D → #56B76A → #3C4061 → #8E8E99 |
| `20yuan` | 二十元棕 | #532F1A → #6B4E25 → #7F5643 → #796A5D → #BE9A62 |
| `10yuan` | 十元蓝 | #242F4D → #465A66 → #6382AA → #828E99 → #7F606D |
| `5yuan` | 五元紫 | #413A4C → #63576F → #56B76A → #6F8DB1 → #B3A479 |
| `1yuan` | 一元橄榄 | #3C3F27 → #5A5745 → #9DA780 → #937539 → #C5AB71 |

### 发散型配色

| 系列 | 说明 | 用途 |
|------|------|------|
| `rdbu` | 红蓝发散（7色） | 热力图、相关矩阵、正负值对比 |
| `coolwarm` | 冷暖发散（7色） | 温度分布、偏差可视化 |

自动注册为 matplotlib colormap，可直接用 `cmap="rdbu"`。

---

## 2. 子集选择

所有基础色系自动生成 1-N 色子集：

```python
sp.setup_style(palette="pastel")      # 完整 6 色
sp.setup_style(palette="pastel-3")    # 前 3 色
sp.setup_style(palette="ocean-2")     # 前 2 色
sp.setup_style(palette="earth-5")     # 前 5 色
```

**智能自动选择**：在 `plot_multi` 等多系列函数中，传入 `palette="pastel"` 会根据系列数自动选择子集：
- 2 条线 → 自动用 `pastel-2`
- 3 条线 → 自动用 `pastel-3`
- 5 条线 → 使用完整 5 色
- 6+ 条线 → 循环完整配色

---

## 3. 自定义配色

### set_custom_palette

```python
sp.set_custom_palette(colors, name="custom")
```

注册单色组，自动生成 1-N 子集。推荐 2-8 色。

```python
sp.set_custom_palette(["#E74C3C", "#3498DB", "#2ECC71"], name="brand")
sp.setup_style(palette="brand")     # 3 色
sp.setup_style(palette="brand-2")   # 前 2 色
```

### register_color_scheme

```python
sp.register_color_scheme(name, scheme)
```

注册完整配色方案，支持按数据量自动选择。

```python
scheme = {
    "single":    ["#264653"],
    "double":    ["#264653", "#2a9d8f"],
    "triple":    ["#264653", "#2a9d8f", "#e9c46a"],
    "quadruple": ["#264653", "#2a9d8f", "#e9c46a", "#f4a261"],
    "quintuple": ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"],
}
sp.register_color_scheme("mytheme", scheme)

# 使用
sp.plot_multi(x, [y1, y2, y3], palette="mytheme")      # 自动选 3 色
sp.setup_style(palette="mytheme-triple")                 # 明确指定
```

### 辅助查询

```python
sp.get_palette("pastel")           # → ['#845EC2', '#D65DB1', ...]
sp.get_color_scheme("mytheme")     # → {"single": [...], "double": [...], ...}
sp.list_palettes()                 # 所有可用配色名
sp.auto_select_palette("mytheme", 3)  # 自动选择 3 色
sp.list_color_schemes()            # 已注册的配色方案
```

---

## 4. 期刊样式

### 可用 venue

| venue | 尺寸 (英寸) | 适用场景 |
|-------|------------|----------|
| `nature` | 7.0 × 5.0 | Nature / Science 双栏（默认） |
| `ieee` | 3.5 × 3.0 | IEEE 单栏 |
| `aps` | 3.4 × 2.8 | APS Physical Review |
| `springer` | 6.0 × 4.5 | Springer |
| `thesis` | 6.1 × 4.3 | 学位论文（A4 版心） |
| `presentation` | 8.0 × 5.5 | 演示文稿 / 海报 |

### 使用方式

```python
# 全局设置
sp.setup_style(venue="ieee")

# 函数级覆盖
fig, ax = sp.plot(x, y, venue="nature")

# 链式调用
sp.style("ieee").plot(x, y).save("fig")

# 上下文管理器
with sp.style_context("thesis"):
    fig, ax = sp.plot(x, y)
```

### 子图预设尺寸

```python
sp.list_paper_layouts("thesis")
# {'1x1': (6.1, 4.3), '1x2': (6.1, 3.0), '2x2': (6.1, 5.0), ...}
```

---

## 5. 语言设置

| lang | 字体 | LaTeX | 适用 |
|------|------|-------|------|
| `zh` / `zh-cn` | 宋体 (SimSun) | 禁用 | 中文论文 |
| `en` | Times New Roman | 自动检测 | 英文投稿 |

```python
sp.setup_style(lang="zh")   # 中文宋体，禁用 LaTeX
sp.setup_style(lang="en")   # Times New Roman，可选 LaTeX

# 函数级覆盖
fig, ax = sp.plot(x, y, lang="en")
```

---

## 6. 主题设置

### 浅色主题（默认）

```python
sp.setup_style("nature", "pastel", lang="zh")
sp.setup_style("nature", "pastel", lang="zh", theme="light")
```

### 暗色主题

```python
sp.setup_style("presentation", "pastel", lang="zh", theme="dark")
```

暗色主题自动设置：
- 深色背景 (#1a1a2e)
- 浅色文字 (#e0e0e0)
- 深色轴框 (#16213e)
- 适合演示、屏幕展示、海报

### 上下文管理器中使用

```python
with sp.style_context("presentation", theme="dark"):
    fig, ax = sp.plot(x, y)
```

---

## 7. 配置系统

### set_defaults（代码设置）

```python
sp.set_defaults(venue="ieee", palette="earth", lang="en", dpi=600, formats=("pdf", "png"))
```

影响后续所有 `setup_style()` 调用。

### 配置文件（.sciplot.toml）

```toml
venue = "ieee"
palette = "earth"
lang = "zh"
dpi = 1200
formats = ["pdf", "png"]
```

### 配置文件（pyproject.toml）

```toml
[tool.sciplot]
venue = "ieee"
palette = "earth"
lang = "zh"
dpi = 1200
formats = ["pdf", "png"]
```

### 加载与查询

```python
sp.load_config()               # 自动查找配置文件
sp.load_config("custom.toml")  # 指定路径
sp.get_config("venue")         # "ieee"
sp.get_config()                # 所有配置
sp.reset_config()              # 重置
```

### 配置优先级（高→低）

1. 函数参数（`venue="ieee"`）
2. 代码设置（`set_defaults()`）
3. 配置文件（`.sciplot.toml` / `pyproject.toml`）
4. 内置默认（`venue="nature"`, `palette="pastel"`, `lang="zh"`, `dpi=1200`）

---

## 链式调用语法速查

```python
# 入口
sp.style("nature")                    # 设置 venue
sp.palette("pastel")                  # 设置配色
sp.chain("ieee", "earth", lang="en")  # 完整设置

# 绘图
sp.style("nature").plot(x, y).save("fig")
sp.style("ieee").palette("forest").scatter(x, y).xlabel("X").save("fig")

# 上下文管理器
with sp.style_context("ieee", palette="ocean"):
    fig, ax = sp.plot(x, y)
    sp.save(fig, "fig")

# 便捷上下文
with sp.ieee_context(palette="earth"): ...
with sp.nature_context(): ...
with sp.thesis_context(palette="ocean"): ...
```
