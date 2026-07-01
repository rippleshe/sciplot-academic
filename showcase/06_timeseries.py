"""
06_timeseries.py — 带事件标注和背景区域的时序图

展示 SciPlot 的 plot_timeseries() 功能：365 天的日均气温序列，
包含趋势、季节性、2 个事件标注和 2 个背景区域。
Nature 默认样式，中文标签。
"""

import numpy as np
import sciplot as sp
from datetime import date, timedelta

# 可复现随机种子
np.random.seed(42)

# ── 数据生成 ──────────────────────────────────────────────────
# 生成 365 天的日期序列（2024 年）
start_date = date(2024, 1, 1)
dates = np.array([start_date + timedelta(days=i) for i in range(365)])

# 日均气温模型：季节性 + 长期趋势 + 随机波动
day_of_year = np.arange(365)
seasonal = 15 + 12 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
trend = 0.005 * day_of_year  # 微弱升温趋势
noise = np.random.normal(0, 2.5, 365)
temperature = seasonal + trend + noise

# 添加寒潮事件（第 35~42 天，约 2 月初）
cold_wave = np.zeros(365)
cold_wave[35:43] = -8 * np.exp(-0.3 * np.arange(8))
temperature += cold_wave

# 添加热浪事件（第 200~212 天，约 7 月下旬）
heat_wave = np.zeros(365)
heat_wave[200:213] = 6 * np.exp(-0.15 * np.abs(np.arange(13) - 6))
temperature += heat_wave

# ── 事件标注 ──────────────────────────────────────────────────
events = [
    {"time": date(2024, 2, 5), "label": "寒潮来袭", "color": "#2196F3"},
    {"time": date(2024, 7, 26), "label": "极端高温", "color": "#F44336"},
]

# ── 背景区域 ──────────────────────────────────────────────────
shade_regions = [
    {
        "start": date(2024, 6, 1),
        "end": date(2024, 8, 31),
        "color": "#FF9800",
        "alpha": 0.12,
    },
    {
        "start": date(2024, 12, 1),
        "end": date(2024, 12, 31),
        "color": "#2196F3",
        "alpha": 0.12,
    },
]

# ── 绘图 ──────────────────────────────────────────────────────
fig, ax = sp.plot_timeseries(
    dates,
    temperature,
    events=events,
    shade_regions=shade_regions,
    rolling_mean=14,
    xlabel="日期",
    ylabel="日均气温 (°C)",
    title="2024 年日均气温变化",
    label="日均气温",
)

# ── 保存 ──────────────────────────────────────────────────────
sp.save(fig, "showcase/06_timeseries", formats=("png",), dpi=300)
