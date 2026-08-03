快速上手
========

SciPlot Academic 是面向中文科研论文场景的 Matplotlib 封装库。
安装与五分钟上手。

安装
----

.. code-block:: bash

   pip install sciplot-academic
   # 或 uv
   uv pip install sciplot-academic

   # 可选扩展
   pip install "sciplot-academic[all]"   # ML + 统计 + 网络 + 维恩

基础绘图
--------

.. code-block:: python

   import numpy as np
   import sciplot as sp

   x = np.linspace(0, 10, 200)
   fig, ax = sp.plot(x, np.sin(x), xlabel="时间 (s)", ylabel="电压 (V)")
   sp.save(fig, "结果图")          # 默认输出 PDF + PNG 1200dpi

五种 API 风格
-------------

.. code-block:: python

   # 1. 传统 API
   fig, ax = sp.plot(x, y, xlabel="X", ylabel="Y")
   sp.save(fig, "fig")

   # 2. 链式调用
   sp.style("nature").palette("pastel").plot(x, y).save("fig")

   # 3. 简洁别名
   fig, ax = sp.line(x, y, xlabel="X", ylabel="Y")

   # 4. PlotResult 链式
   sp.plot(x, y).xlabel("X").ylabel("Y").save("fig")

   # 5. 上下文管理器
   with sp.style_context("ieee", palette="ocean"):
       fig, ax = sp.plot(x, y)
       sp.save(fig, "fig")

期刊样式
--------

.. code-block:: python

   # nature | ieee | aps | springer | thesis | presentation
   sp.setup_style("thesis", "pastel", lang="zh")   # 中文论文
   sp.setup_style("nature", "ocean", lang="en")    # Nature 投稿

复合图模板
----------

.. code-block:: python

   # 五大 Nature 布局原型一键生成（自动 8pt 面板标签）
   fig, axes = sp.figure_panels(template="condition_matrix")
   fig, axes = sp.figure_panels(template="triptych")

   # 不对称 Hero 布局
   result = sp.hero_layout("hero_right")
   result.ax_hero.plot(x, y)
   sp.save(result.fig, "hero")

色盲安全与质量审计
------------------

.. code-block:: python

   sp.setup_style("nature", "okabe-ito")      # 色盲安全调色板
   sp.audit_palette("pastel")                 # 配色体检
   sp.audit_figure(fig)                       # 投稿质量审计
   # save() 默认已审计必拒项（字号<5pt、多面板缺标签）
