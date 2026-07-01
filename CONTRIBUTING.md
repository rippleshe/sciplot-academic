# 贡献指南

感谢您对 SciPlot Academic 的关注！本指南将帮助您参与项目开发，无论是修复 Bug、添加新功能还是改进文档。

## 目录

- [欢迎贡献](#欢迎贡献)
- [开发环境搭建](#开发环境搭建)
- [项目结构](#项目结构)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [测试指南](#测试指南)
- [Pull Request 流程](#pull-request-流程)
- [Issue 指南](#issue-指南)
- [版本发布规则](#版本发布规则)

---

## 欢迎贡献

SciPlot Academic 是一个开源的中文科研绘图库，我们欢迎各种形式的贡献：

- **Bug 修复**：修复已知问题或报告新 Bug
- **新功能**：添加新的图表类型或工具函数
- **文档改进**：完善文档、示例或教程
- **性能优化**：提升绘图速度或内存效率
- **测试覆盖**：补充单元测试或集成测试
- **国际化**：改进多语言支持

在开始贡献之前，请：

1. 阅读本指南
2. 查看 [Issues](https://github.com/rippleshe/sciplot-academic/issues) 了解当前需求
3. 先创建 Issue 讨论您的想法（尤其是大型改动）

---

## 开发环境搭建

### 前置要求

- Python 3.8+（推荐 3.10+）
- [uv](https://docs.astral.sh/uv/) 包管理器
- Git

### 1. Fork 并克隆仓库

```bash
# Fork 仓库后克隆
git clone https://github.com/<your-username>/sciplot-academic.git
cd sciplot-academic

# 添加上游远程仓库
git remote add upstream https://github.com/rippleshe/sciplot-academic.git
```

### 2. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 安装开发依赖（包含所有可选依赖）
uv pip install -e ".[dev,all]"
```

### 3. 验证安装

```bash
# 运行测试确认环境正常
pytest tests/ -v

# 检查代码风格
ruff check sciplot/

# 类型检查
mypy sciplot/ --ignore-missing-imports
```

### 4. 配置 IDE（可选）

推荐使用 VS Code 或 PyCharm，并安装以下插件：

- **VS Code**：
  - Python
  - Ruff
  - Pylance
  
- **PyCharm**：
  - 启用 Ruff 作为外部工具

---

## 项目结构

```
sciplot-academic/
├── sciplot/                    # 主包
│   ├── __init__.py            # 入口文件，导出公共 API
│   ├── py.typed               # PEP 561 类型标记
│   ├── _core/                 # 核心模块
│   │   ├── style.py          # 样式系统（期刊模板）
│   │   ├── palette.py        # 配色系统
│   │   ├── layout.py         # 布局和子图
│   │   ├── fluent.py         # 链式调用接口
│   │   ├── context.py        # 上下文管理器
│   │   ├── config.py         # 配置系统
│   │   ├── result.py         # 返回类型定义
│   │   ├── types.py          # 类型别名
│   │   └── utils.py          # 工具函数
│   ├── _plots/                # 图表实现
│   │   ├── basic.py          # 基础图表（折线、散点、面积）
│   │   ├── distribution.py   # 分布图表（柱状、箱线、小提琴）
│   │   ├── advanced.py       # 高级图表（误差棒、置信区间、热力图）
│   │   ├── statistical.py    # 统计图表（QQ图、密度图）
│   │   ├── timeseries.py     # 时间序列图表
│   │   ├── multivariate.py   # 多变量图表（平行坐标、散点矩阵）
│   │   ├── polar.py          # 极坐标图表（雷达图）
│   │   └── aliases.py        # 简洁别名
│   ├── _ext/                  # 扩展模块
│   │   ├── ml.py             # 机器学习可视化
│   │   ├── plot3d.py         # 3D 绘图
│   │   ├── network.py        # 网络图
│   │   ├── hierarchical.py   # 层次聚类图
│   │   └── venn.py           # 韦恩图
│   └── utils/                 # 工具模块
│       └── smart.py          # 智能辅助函数
├── tests/                     # 测试目录
│   ├── conftest.py           # pytest 配置和 fixtures
│   ├── fixtures/             # 测试数据和 fixtures
│   ├── unit/                 # 单元测试
│   ├── integration/          # 集成测试
│   └── regression/           # 回归测试
├── showcase/                  # 示例脚本和图片
├── .github/                   # GitHub 配置
│   ├── workflows/            # CI/CD 工作流
│   └── ISSUE_TEMPLATE/       # Issue 模板
├── pyproject.toml            # 项目配置
├── pytest.ini                # pytest 配置
├── uv.lock                   # 依赖锁定文件
└── README.md                 # 项目说明
```

### 核心模块说明

| 模块 | 职责 | 修改频率 |
|------|------|----------|
| `_core/style.py` | 期刊样式模板（Nature、IEEE 等） | 低 |
| `_core/palette.py` | 配色方案定义和管理 | 中 |
| `_core/layout.py` | 子图布局和保存功能 | 低 |
| `_plots/*.py` | 具体图表实现 | 高 |
| `_ext/*.py` | 可选扩展功能 | 中 |
| `aliases.py` | 简洁别名映射 | 低 |

---

## 代码规范

### 1. 代码风格

本项目使用 [Ruff](https://docs.astral.sh/ruff/) 进行代码风格检查和格式化。

```bash
# 检查代码风格
ruff check sciplot/

# 自动修复
ruff check --fix sciplot/

# 格式化代码
ruff format sciplot/
```

**Ruff 配置规则**（`pyproject.toml`）：

```toml
[tool.ruff]
target-version = "py38"

[tool.ruff.lint]
select = ["E", "F", "W"]  # pycodestyle + pyflakes
```

### 2. 类型提示

所有公共 API 必须添加类型提示：

```python
from typing import Optional, Sequence, Tuple
from matplotlib.figure import Figure
from matplotlib.axes import Axes

def plot_line(
    x: Sequence[float],
    y: Sequence[float],
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    figsize: Tuple[float, float] = (8, 6),
) -> Tuple[Figure, Axes]:
    """绘制折线图。
    
    参数:
        x: X 轴数据
        y: Y 轴数据
        xlabel: X 轴标签
        ylabel: Y 轴标签
        figsize: 图形尺寸
        
    返回:
        (fig, ax) 元组
        
    示例:
        >>> fig, ax = plot_line([1, 2, 3], [1, 4, 9])
    """
    ...
```

### 3. 文档字符串

使用 Google 风格的 docstring：

```python
def plot_scatter(
    x: Sequence[float],
    y: Sequence[float],
    *,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    title: Optional[str] = None,
    figsize: Tuple[float, float] = (8, 6),
    **kwargs,
) -> Tuple[Figure, Axes]:
    """绘制散点图。

    创建带有可选标签和标题的散点图。支持 matplotlib 的所有散点参数。

    参数:
        x: X 轴数据序列
        y: Y 轴数据序列
        xlabel: X 轴标签，默认为 None
        ylabel: Y 轴标签，默认为 None
        title: 图表标题，默认为 None
        figsize: 图形尺寸（宽，高），单位为英寸
        **kwargs: 传递给 matplotlib.pyplot.scatter 的其他参数

    返回:
        包含 Figure 和 Axes 对象的元组

    异常:
        ValueError: 当 x 和 y 长度不匹配时
        TypeError: 当输入数据类型不支持时

    示例:
        >>> import numpy as np
        >>> x = np.random.randn(100)
        >>> y = np.random.randn(100)
        >>> fig, ax = plot_scatter(x, y, xlabel="X", ylabel="Y")
        
    注意:
        此函数会自动应用当前设置的期刊样式。
    """
    ...
```

### 4. 命名约定

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块名 | 小写 + 下划线 | `basic.py`, `statistical.py` |
| 类名 | 大驼峰 | `PlotChain`, `StyleContext` |
| 函数名 | 小写 + 下划线 | `plot_line`, `create_subplots` |
| 常量 | 大写 + 下划线 | `VENUES`, `DEFAULT_PALETTE` |
| 私有成员 | 单下划线前缀 | `_core`, `_ext` |
| 类型别名 | 大驼峰 | `VenueType`, `PaletteType` |

### 5. 导入顺序

```python
# 1. 标准库
from pathlib import Path
from typing import Optional, Tuple

# 2. 第三方库
import matplotlib.pyplot as plt
import numpy as np

# 3. 本地模块
from sciplot._core.style import setup_style
from sciplot._core.palette import get_palette
```

### 6. Python 版本兼容性

- 最低支持 Python 3.8
- 使用 `from __future__ import annotations` 启用延迟注解求值
- 避免使用 3.9+ 的语法（如 `list[int]` 代替 `List[int]`）
- 使用 `tomli` 处理 TOML 文件（3.11 之前）

---

## 提交规范

本项目遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

### 提交消息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(plots): add radar chart` |
| `fix` | Bug 修复 | `fix(style): correct IEEE template colors` |
| `docs` | 文档更新 | `docs(readme): add installation guide` |
| `style` | 代码格式（不影响逻辑） | `style(core): format with ruff` |
| `refactor` | 重构（不改变功能） | `refactor(plots): extract common validation` |
| `perf` | 性能优化 | `perf(palette): cache color conversions` |
| `test` | 测试相关 | `test(unit): add scatter plot tests` |
| `build` | 构建系统或依赖 | `build(deps): bump matplotlib to 3.8` |
| `ci` | CI 配置 | `ci(actions): add Python 3.12 support` |
| `chore` | 其他杂项 | `chore: update gitignore` |
| `revert` | 回滚 | `revert: revert "feat(...)"` |

### Scope 范围

| 范围 | 说明 |
|------|------|
| `core` | 核心模块（`_core/`） |
| `plots` | 图表模块（`_plots/`） |
| `ext` | 扩展模块（`_ext/`） |
| `utils` | 工具模块 |
| `style` | 样式系统 |
| `palette` | 配色系统 |
| `layout` | 布局系统 |
| `deps` | 依赖项 |
| `ci` | CI/CD |
| `docs` | 文档 |

### 提交示例

```bash
# 新功能
git commit -m "feat(plots): add bubble chart with size encoding"

# Bug 修复
git commit -m "fix(style): fix font size not applied in IEEE template"

# 带详细说明的提交
git commit -m "feat(palette): add colorblind-friendly palettes

- Add 'deuteranopia' palette for red-green colorblind users
- Add 'protanopia' palette for blue-yellow colorblind users
- Update auto_select_palette to detect colorblind preference

Closes #123"

# 破坏性变更
git commit -m "feat(core)!: change default venue from 'nature' to 'default'

BREAKING CHANGE: Default venue is now 'default' instead of 'nature'.
Users must explicitly call sp.setup_style('nature') to restore old behavior."
```

### 提交最佳实践

1. **原子提交**：每个提交只做一件事
2. **有意义的消息**：说明"为什么"而不仅是"做了什么"
3. **关联 Issue**：使用 `Closes #123` 或 `Fixes #123`
4. **测试通过**：确保提交前测试通过

---

## 测试指南

### 测试结构

```
tests/
├── conftest.py              # 共享 fixtures 和配置
├── fixtures/                # 测试数据
├── unit/                    # 单元测试（快速，隔离）
│   ├── test_basic_charts.py
│   ├── test_style.py
│   └── ...
├── integration/             # 集成测试（较慢，跨模块）
│   └── test_end_to_end.py
└── regression/              # 回归测试（防止已修复问题重现）
    └── test_known_issues.py
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定目录
pytest tests/unit/

# 运行特定文件
pytest tests/unit/test_basic_charts.py

# 运行特定测试类
pytest tests/unit/test_basic_charts.py::TestPlotLine

# 运行特定测试函数
pytest tests/unit/test_basic_charts.py::TestPlotLine::test_plot_basic

# 显示详细输出
pytest tests/ -v

# 显示失败详情
pytest tests/ --tb=long

# 只运行失败的测试
pytest tests/ --lf

# 并行运行（需要 pytest-xdist）
pytest tests/ -n auto
```

### 测试标记

项目定义了以下 pytest markers：

```bash
# 跳过慢测试
pytest tests/ -m "not slow"

# 只运行单元测试
pytest tests/ -m unit

# 只运行集成测试
pytest tests/ -m integration

# 只运行回归测试
pytest tests/ -m regression

# 跳过需要 ML 扩展的测试
pytest tests/ -m "not requires_ml"
```

### 编写测试

#### 1. 单元测试示例

```python
"""
基础图表单元测试 - 测试所有基础绘图函数
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
import sciplot as sp
from matplotlib.figure import Figure
from matplotlib.axes import Axes


class TestPlotLine:
    """测试折线图"""
    
    def test_plot_basic(self, test_data, cleanup_figures):
        """测试基础折线图"""
        fig, ax = sp.plot(test_data["x"], test_data["y"])
        assert isinstance(fig, Figure)
        assert isinstance(ax, Axes)
        
    def test_plot_with_labels(self, test_data, cleanup_figures):
        """测试带标签的折线图"""
        fig, ax = sp.plot(
            test_data["x"], 
            test_data["y"],
            xlabel="X 轴",
            ylabel="Y 轴",
            title="测试标题"
        )
        assert ax.get_xlabel() == "X 轴"
        assert ax.get_ylabel() == "Y 轴"
        assert ax.get_title() == "测试标题"
        
    def test_plot_invalid_input(self, cleanup_figures):
        """测试无效输入处理"""
        with pytest.raises(ValueError):
            sp.plot([], [])
```

#### 2. 使用 Fixtures

```python
# 使用 conftest.py 中定义的 fixtures
def test_plot_with_temp_file(self, test_data, temp_dir, cleanup_figures):
    """测试保存到临时文件"""
    fig, ax = sp.plot(test_data["x"], test_data["y"])
    save_path = temp_dir / "test_plot.png"
    sp.save(fig, save_path)
    assert save_path.exists()
```

#### 3. 参数化测试

```python
@pytest.mark.parametrize("venue", ["nature", "ieee", "thesis", "presentation"])
def test_style_venues(venue, cleanup_figures, reset_style):
    """测试所有期刊样式"""
    sp.setup_style(venue)
    fig, ax = plt.subplots()
    assert fig is not None
```

#### 4. 跳过测试

```python
@pytest.mark.skipif(
    not _check_ml_available(),
    reason="需要安装 sciplot-academic[ml]"
)
def test_plot_pca(self, cleanup_figures):
    """测试 PCA 绘图（需要 ML 扩展）"""
    ...

@pytest.mark.slow
def test_large_dataset(self, cleanup_figures):
    """测试大数据集（慢测试）"""
    ...
```

### 测试最佳实践

1. **测试命名**：使用 `test_<功能>_<场景>` 格式
2. **一个测试一件事**：每个测试函数只验证一个行为
3. **使用 fixtures**：复用测试数据和清理逻辑
4. **清理资源**：使用 `cleanup_figures` fixture 关闭图形
5. **测试边界情况**：空输入、极大值、极小值
6. **测试错误处理**：验证异常是否正确抛出

### 覆盖率

```bash
# 生成覆盖率报告
pytest tests/ --cov=sciplot --cov-report=html

# 查看未覆盖的代码
pytest tests/ --cov=sciplot --cov-report=term-missing
```

---

## Pull Request 流程

### 1. 准备工作

```bash
# 同步上游代码
git fetch upstream
git checkout main
git merge upstream/main

# 创建功能分支
git checkout -b feature/your-feature-name
```

### 2. 开发和测试

```bash
# 编写代码
# ...

# 运行测试
pytest tests/

# 检查代码风格
ruff check sciplot/

# 类型检查
mypy sciplot/ --ignore-missing-imports

# 提交更改
git add .
git commit -m "feat(plots): add your feature"
```

### 3. 推送并创建 PR

```bash
# 推送到您的 Fork
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request。

### 4. PR 模板

```markdown
## 描述

简要描述这个 PR 的目的和实现方式。

## 变更类型

- [ ] Bug 修复
- [ ] 新功能
- [ ] 重构
- [ ] 文档更新
- [ ] 测试
- [ ] 其他

## 测试

- [ ] 添加了新的测试
- [ ] 所有测试通过
- [ ] 覆盖率没有下降

## Checklist

- [ ] 代码遵循项目规范
- [ ] 添加了类型提示
- [ ] 更新了文档（如需要）
- [ ] 更新了 CHANGELOG（如需要）

## 相关 Issue

Closes #<issue-number>

## 截图（如适用）

添加相关截图或输出示例。
```

### 5. 代码审查

- 维护者会审查您的代码
- 可能会要求修改或补充测试
- 通过审查后会合并到主分支

### 6. PR 最佳实践

1. **保持 PR 小而专注**：一个 PR 只做一件事
2. **清晰的描述**：说明为什么要做这个改动
3. **关联 Issue**：使用 `Closes #123`
4. **响应审查意见**：及时回复和修改
5. **保持同步**：定期 rebase 主分支

---

## Issue 指南

### 报告 Bug

使用 [Bug Report 模板](https://github.com/rippleshe/sciplot-academic/issues/new?template=bug_report.md)，包含：

1. **Bug 描述**：清晰描述问题
2. **重现步骤**：最小化的重现代码
3. **预期行为**：您期望发生什么
4. **实际行为**：实际发生了什么
5. **环境信息**：
   - SciPlot 版本
   - Python 版本
   - 操作系统
   - matplotlib backend
6. **错误信息**：完整的错误堆栈

### 请求功能

使用 [Feature Request 模板](https://github.com/rippleshe/sciplot-academic/issues/new?template=feature_request.md)，包含：

1. **功能描述**：您想要什么功能
2. **使用场景**：为什么需要这个功能
3. **建议方案**：如何实现（可选）
4. **替代方案**：其他可能的解决方案

### Issue 最佳实践

1. **搜索现有 Issue**：避免重复
2. **使用模板**：提供完整信息
3. **一个 Issue 一件事**：不要混合多个问题
4. **提供最小重现**：方便开发者定位问题
5. **保持沟通**：及时回复维护者的问题

---

## 版本发布规则

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

### 版本格式

```
MAJOR.MINOR.PATCH
```

### 版本类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **MAJOR** | 不兼容的 API 变更 | `1.0.0` -> `2.0.0` |
| **MINOR** | 向后兼容的新功能 | `1.0.0` -> `1.1.0` |
| **PATCH** | 向后兼容的 Bug 修复 | `1.0.0` -> `1.0.1` |

### 版本变更示例

#### PATCH 版本（1.0.0 -> 1.0.1）

- 修复 Bug
- 性能优化
- 文档更新
- 依赖版本更新（不改变 API）

```bash
git commit -m "fix(style): correct font size in IEEE template"
```

#### MINOR 版本（1.0.0 -> 1.1.0）

- 新增图表类型
- 新增配置选项
- 新增工具函数
- 废弃功能（但仍可用）

```bash
git commit -m "feat(plots): add bubble chart support"
```

#### MAJOR 版本（1.0.0 -> 2.0.0）

- 删除废弃功能
- 改变现有 API 行为
- 改变默认值
- 改变返回类型

```bash
git commit -m "feat(core)!: change default venue to 'default'

BREAKING CHANGE: Default venue is now 'default' instead of 'nature'."
```

### 预发布版本

```
1.0.0-alpha.1    # Alpha 版本
1.0.0-beta.1     # Beta 版本
1.0.0-rc.1       # Release Candidate
```

### 发布流程

1. 更新 `pyproject.toml` 中的版本号
2. 更新 `CHANGELOG.md`
3. 创建 Git tag
4. 推送到 GitHub
5. CI 自动发布到 PyPI

```bash
# 更新版本
# 编辑 pyproject.toml 中的 version 字段

# 提交版本更新
git commit -m "chore: bump version to 1.1.0"

# 创建 tag
git tag -a v1.1.0 -m "Release v1.1.0"

# 推送
git push origin main --tags
```

---

## 获取帮助

如果您在贡献过程中遇到问题：

1. **查看文档**：阅读 [README.md](README.md) 和本指南
2. **搜索 Issue**：查看是否有类似问题
3. **创建 Issue**：描述您的问题
4. **讨论区**：在 GitHub Discussions 中提问

---

## 致谢

感谢所有为 SciPlot Academic 做出贡献的开发者！

[![Contributors](https://contrib.rocks/image?repo=rippleshe/sciplot-academic)](https://github.com/rippleshe/sciplot-academic/graphs/contributors)
