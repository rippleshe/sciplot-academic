"""
60_residual_diagnostics.py — 四合一回归残差诊断面板

展示 SciPlot v1.16.0 新增的 `plot_residual_diagnostics()`：
一次生成 (a) Residuals vs Fitted + Lowess、(b) Normal Q-Q + 95% Beta CI、
(c) 残差直方分布 + 正态曲线叠加、(d) 滞后自相关图 (ACF)。
"""

import numpy as np
import sciplot as sp

rng = np.random.default_rng(314)

sp.setup_style("nature", "blue-sky", lang="en")

n = 110
y_pred = np.linspace(12.0, 68.0, n)
noise = rng.normal(0.0, 2.1, size=n)
# 刻意植入 3 个强异常残差点以触发 |z|>2.5 自动高亮标注
noise[18] = 6.9
noise[54] = -7.2
noise[92] = 6.4
y_true = y_pred + noise

fig, _ = sp.plot_residual_diagnostics(
    y_true,
    y_pred,
    title="Regression Model Four-Panel Residual Diagnostics",
    panel_labels=True,
)
sp.save(fig, "showcase/60_residual_diagnostics", formats=("png",), dpi=300)
