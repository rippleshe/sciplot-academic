# SciPlot 配色与样式

## 内置配色系

### 基础色系（自动子集）

| 系列 | 风格 | HEX 色值 | 子集 |
|------|------|---------|------|
| `pastel` | 柔和粉彩（默认） | #845EC2 → #D65DB1 → #FF6F91 → #FF9671 → #FFC75F → #F9F871 | pastel-1~6 |
| `ocean` | 海洋蓝绿 | #5E98C2 → #26B3D1 → #00CCCB → #56E2B0 → #A6F18C → #F9F871 | ocean-1~6 |
| `forest` | 森林渐变 | #5EC299 → #00B3A2 → #00A2AD → #0090B8 → #007DBD → #0067B9 | forest-1~6 |
| `sunset` | 日落暖色 | #D44132 → #F45E4A → #FF7A62 → #FF967C → #FFB296 | sunset-1~5 |
| `earth` | 大地色系 | #264653 → #2a9d8f → #e9c46a → #f4a261 → #e76f51 | earth-1~5 |

### 特殊色系

| 系列 | 说明 |
|------|------|
| `100yuan` ~ `1yuan` | 人民币主题（6 个面额） |
| `rdbu` | 红蓝发散（热力图/相关矩阵） |
| `coolwarm` | 冷暖发散 |

### 使用

```python
sp.setup_style(palette="pastel-3")   # 前 3 色
sp.setup_style(palette="ocean")      # 完整 6 色
sp.setup_style(palette="100yuan")    # 人民币红
sp.setup_style(palette="rdbu")       # 发散型
```

### 自定义配色

```python
# 简单注册（自动生成 1-N 子集）
sp.set_custom_palette(["#E74C3C", "#3498DB", "#2ECC71"], name="brand")
sp.setup_style(palette="brand")     # 3 色
sp.setup_style(palette="brand-2")   # 前 2 色

# 完整配色方案（支持自动选择）
scheme = {
    "single": ["#264653"],
    "double": ["#264653", "#2a9d8f"],
    "triple": ["#264653", "#2a9d8f", "#e9c46a"],
    "quadruple": ["#264653", "#2a9d8f", "#e9c46a", "#f4a261"],
    "quintuple": ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"],
}
sp.register_color_scheme("mytheme", scheme)
sp.plot_multi(x, [y1, y2, y3], palette="mytheme")  # 自动选 3 色
```

---

## 主题

### 浅色主题（默认）

```python
sp.setup_style("nature", "pastel", lang="zh")
# 或
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

---

## 语言与字体

| lang | 字体 | LaTeX | 适用 |
|------|------|-------|------|
| `zh` / `zh-cn` | 宋体 (SimSun) | 禁用 | 中文论文 |
| `en` | Times New Roman | 自动检测 | 英文投稿 |

```python
sp.setup_style(lang="zh")   # 中文宋体，禁用 LaTeX
sp.setup_style(lang="en")   # Times New Roman，可选 LaTeX
```

---

## 期刊尺寸

| venue | 尺寸 (英寸) | 场景 |
|-------|------------|------|
| `nature` | 7.0 × 5.0 | Nature/Science 双栏 |
| `ieee` | 3.5 × 3.0 | IEEE 单栏 |
| `aps` | 3.4 × 2.8 | APS Physical Review |
| `springer` | 6.0 × 4.5 | Springer |
| `thesis` | 6.1 × 4.3 | 学位论文 (A4 版心) |
| `presentation` | 8.0 × 5.5 | 演示文稿 |

### 论文子图预设尺寸

```python
sp.list_paper_layouts("thesis")
# {'thesis': {'1x1': (6.1, 4.3), '1x2': (6.1, 3.0), '2x2': (6.1, 5.0), ...}}
```

---

## 链式调用语法

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

---

## 配置持久化

```python
# 设置默认值（影响后续 setup_style()）
sp.set_defaults(venue="ieee", palette="earth", lang="en", dpi=600)

# 从配置文件加载
sp.load_config()  # 自动查找 .sciplot.toml 或 pyproject.toml [tool.sciplot]

# 获取当前配置
sp.get_config()        # 全部
sp.get_config("venue") # 单项

# 重置
sp.reset_config()
```

配置文件格式 (.sciplot.toml):
```toml
venue = "ieee"
palette = "earth"
lang = "zh"
dpi = 1200
formats = ["pdf", "png"]
```
