"""
05_heatmap.py — 相关系数矩阵热力图

展示 SciPlot 的 plot_heatmap() 功能：6 个气象变量之间的皮尔逊相关系数矩阵。
使用 RdBu_r 发散色标，显示数值标注，Nature 默认样式，中文标签。
"""

import numpy as np
import sciplot as sp

# 可复现随机种子
np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
# 模拟 6 个气象变量的观测数据（365 天）
n_days = 365

# 温度 (°C)：季节性 + 随机波动
day_of_year = np.arange(n_days)
temperature = 15 + 12 * np.sin(2 * np.pi * (day_of_year - 80) / 365) + np.random.normal(0, 2, n_days)

# 气压 (hPa)：与温度负相关
pressure = 1015 - 0.3 * temperature + np.random.normal(0, 3, n_days)

# 相对湿度 (%)：与温度负相关，与降水正相关
humidity = 70 - 0.5 * temperature + np.random.normal(0, 5, n_days)

# 风速 (m/s)：独立变量
wind_speed = 4.5 + np.random.exponential(2, n_days)

# 降水量 (mm)：与湿度正相关
precipitation = np.maximum(0, 0.5 * humidity - 20 + np.random.exponential(3, n_days))

# 太阳辐射 (W/m²)：与温度正相关，与湿度负相关
radiation = 200 + 3 * temperature - 1.5 * humidity + np.random.normal(0, 15, n_days)

# 组装数据矩阵
data_matrix = np.column_stack([
    temperature, pressure, humidity, wind_speed, precipitation, radiation
])

# 计算皮尔逊相关系数矩阵
corr_matrix = np.corrcoef(data_matrix.T)

# ── 变量标签 ──────────────────────────────────────────────────
var_labels = [
    "温度", "气压", "湿度", "风速", "降水量", "辐射"
]

# ── 绘图 ──────────────────────────────────────────────────────
fig, ax = sp.plot_heatmap(
    corr_matrix,
    row_labels=var_labels,
    col_labels=var_labels,
    cmap="RdBu_r",
    vmin=-1,
    vmax=1,
    show_values=True,
    fmt=".2f",
    colorbar_label="相关系数",
    title="气象变量相关系数矩阵",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/05_heatmap", formats=("png",), dpi=300)
