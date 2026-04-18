# 图表类型

## 基础图表

### 折线图

```python
sp.plot(x, y)                    # 简化入口
sp.plot_line(x, y, ...)          # 完整参数
sp.plot_multi(x, [y1, y2])       # 多线（自动配色子集）
sp.plot_multi_line(x, y_list, use_linestyles=False, ...)
```

### 散点图

```python
sp.plot_scatter(x, y, s=20, alpha=0.7, ...)
```

### 阶梯图

```python
sp.plot_step(x, y, where="mid")  # CDF/直方风格
```

### 面积图

```python
sp.plot_area(x, y, alpha=0.3)                    # 单组面积
sp.plot_multi_area(x, [y1, y2], stacked=True)    # 堆叠面积
```

### 多系列图表

```python
sp.plot_multi(x, [y1, y2, y3])           # 多线图（自动配色）
sp.plot_multi_line(x, y_list, use_linestyles=False)  # 多线图（完整参数）
sp.multi(x, [y1, y2])                    # 简洁别名
sp.multi_line(x, [y1, y2])               # 简洁别名
sp.multi_area(x, [y1, y2], stacked=True) # 多面积图
```

---

## 柱状图

### 单组柱状图

```python
sp.plot_bar(categories, values)
```

### 分组柱状图（论文最常用）

```python
sp.plot_grouped_bar(groups, data)
```

### 堆叠柱状图

```python
sp.plot_stacked_bar(categories, data)
```

### 水平柱状图

```python
sp.plot_horizontal_bar(categories, values, sort=True)
```

---

## 分布图表

### 箱线图

```python
sp.plot_box(data_list, labels=..., showfliers=True)
```

### 小提琴图

```python
sp.plot_violin(data_list, labels=..., showmedians=True)
```

### 直方图

```python
sp.plot_histogram(data, bins=30, density=False)
```

### 热力图

```python
sp.plot_heatmap(data, cmap="Blues", show_values=False)
sp.heatmap(data, cmap="viridis")  # 简洁别名
```

---

## 时序图表

### 时间序列图

```python
import pandas as pd
dates = pd.date_range("2023-01-01", periods=365, freq="D")
values = np.cumsum(np.random.randn(365))

sp.plot_timeseries(dates, values, xlabel="日期", ylabel="累计值")
sp.timeseries(dates, values)  # 简洁别名
```

### 多时间序列图

```python
sp.plot_multi_timeseries(dates, [series1, series2], labels=["A", "B"])
```

---

## 多维图表

### 平行坐标图

```python
sp.plot_parallel(data, labels=feature_names)
sp.parallel(data, labels=feature_names)  # 简洁别名
```

---

## 统计诊断图表

### 残差图

```python
sp.plot_residuals(model, X, y)
```

### Q-Q 图

```python
sp.plot_qq(residuals)
```

### Bland-Altman 图

```python
sp.plot_bland_altman(method1, method2)
```

---

## 误差与置信

### 误差条

```python
sp.plot_errorbar(x, y, yerr, fmt="o", capsize=4)
```

### 置信区间

```python
sp.plot_confidence(x, mean, std, alpha=0.25)
```

---

## 组合与标注

### 组合图（柱状 + 折线，双 Y 轴）

```python
sp.plot_combo(
    x=["Q1", "Q2", "Q3", "Q4"],
    bar_data={"销售额": [100, 120, 140, 160]},
    line_data={"增长率": [5, 8, 12, 15]},
)
```

### 显著性标注

```python
# 在箱线图/小提琴图上标注显著性
sp.annotate_significance(ax, x1=1, x2=2, y=8.5, p_value=0.03)   # *
sp.annotate_significance(ax, x1=1, x2=3, y=9.5, p_value=0.0005)  # ***
```
