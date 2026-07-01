# SciPlot Academic 项目开发规则

> 本文档为 SciPlot Academic 内部开发规范，所有贡献者必须遵守。

---

## 1. 版本管理规则

### 1.1 版本号格式

采用语义化版本 (Semantic Versioning): `MAJOR.MINOR.PATCH`

| 类型 | 说明 | 示例 |
|------|------|------|
| MAJOR | 不兼容的 API 变更 | 1.0.0 → 2.0.0 |
| MINOR | 向后兼容的功能新增 | 1.0.0 → 1.1.0 |
| PATCH | 向后兼容的问题修复 | 1.0.0 → 1.0.1 |

### 1.2 版本递增规则

- **每次迭代最小版本号加一** (用户要求)
- 版本号在 `pyproject.toml` 的 `[project]` 部分维护
- 发布时同步更新所有引用版本号的位置

### 1.3 当前版本

```
当前版本: 1.9.1
```

---

## 2. 代码规范

### 2.1 代码风格工具

- 使用 **ruff** 进行代码检查和格式化
- 行宽限制: **88 字符**
- 配置文件: `pyproject.toml` 中的 `[tool.ruff]` 部分

### 2.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 函数/变量 | snake_case | `create_heatmap()` |
| 类 | PascalCase | `AcademicPlot` |
| 常量 | UPPER_SNAKE_CASE | `DEFAULT_FIGSIZE` |
| 模块文件 | snake_case | `heatmap_plot.py` |

### 2.3 类型注解

- **必须**为所有公共函数添加类型注解
- 使用 `from __future__ import annotations` 支持 Python 3.8+
- 复杂类型使用 `typing` 模块

```python
from __future__ import annotations
from typing import Optional, Union

def create_plot(
    data: list[float],
    title: Optional[str] = None,
    figsize: tuple[float, float] = (8, 6),
) -> matplotlib.figure.Figure:
    """创建学术图表。"""
    ...
```

### 2.4 文档字符串

- **必须**编写中文文档字符串
- 格式: Google style
- 所有公共函数、类、模块必须有文档字符串

```python
def create_heatmap(
    data: np.ndarray,
    labels: list[str],
    title: str = "热力图",
) -> matplotlib.figure.Figure:
    """
    创建学术热力图。

    Args:
        data: 二维数据数组
        labels: 坐标轴标签列表
        title: 图表标题，默认为 "热力图"

    Returns:
        matplotlib.figure.Figure: 生成的图表对象

    Raises:
        ValueError: 当数据维度不匹配时

    Examples:
        >>> import numpy as np
        >>> data = np.random.rand(5, 5)
        >>> fig = create_heatmap(data, labels=["A", "B", "C", "D", "E"])
    """
    ...
```

---

## 3. 测试规范

### 3.1 测试目录结构

```
tests/
├── conftest.py           # 共享 fixtures
├── unit/                 # 单元测试
│   ├── __init__.py
│   └── test_*.py
├── integration/          # 集成测试
│   ├── __init__.py
│   └── test_*.py
└── regression/           # 回归测试
    ├── __init__.py
    └── test_*.py
```

### 3.2 命名规范

- 测试目录: `tests/{unit,integration,regression}/`
- 测试文件命名: `test_*.py`
- 测试函数命名: `test_*`
- 测试类命名: `Test*`

### 3.3 测试标记

使用 pytest 标记分类测试:

```python
import pytest

@pytest.mark.unit
def test_function_basic():
    """单元测试示例。"""
    ...

@pytest.mark.integration
def test_module_interaction():
    """集成测试示例。"""
    ...

@pytest.mark.regression
def test_bug_fix_issue_123():
    """回归测试示例 - 验证 issue #123 修复。"""
    ...
```

### 3.4 测试要求

- ✅ **新功能必须附带测试**
- ✅ **Bug 修复必须添加回归测试**
- ✅ 测试覆盖率要求: **>80%**
- ✅ 测试必须独立运行，不依赖外部资源

### 3.5 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行单元测试
uv run pytest -m unit

# 运行带覆盖率的测试
uv run pytest --cov=sciplot --cov-report=html
```

---

## 4. 提交规范

### 4.1 Commit Message 格式

使用 **Conventional Commits** 格式:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### 4.2 类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | `feat(plots): 添加热力图支持` |
| fix | Bug 修复 | `fix(heatmap): 修复颜色映射错误` |
| docs | 文档更新 | `docs(readme): 更新安装说明` |
| style | 代码风格 | `style: 修复 ruff 警告` |
| refactor | 代码重构 | `refactor(core): 重构绘图引擎` |
| test | 测试相关 | `test(heatmap): 添加单元测试` |
| chore | 构建/工具 | `chore(ci): 更新 GitHub Actions` |

### 4.3 提交示例

```bash
# 简单提交
git commit -m "feat(plots): 添加热力图支持"

# 带详细说明的提交
git commit -m "fix(heatmap): 修复颜色映射错误

修复了当数据范围为负数时颜色映射不正确的问题。

Fixes #123"
```

### 4.4 范围说明

常用范围: `plots`, `core`, `utils`, `styles`, `api`, `ci`, `docs`, `deps`

---

## 5. 分支管理

### 5.1 分支类型

| 分支类型 | 命名格式 | 说明 | 示例 |
|----------|----------|------|------|
| main/master | `main` | 稳定版本分支 | - |
| develop | `develop` | 开发分支 | - |
| feature/* | `feature/<name>` | 功能分支 | `feature/heatmap` |
| fix/* | `fix/<name>` | 修复分支 | `fix/color-mapping` |
| release/* | `release/<version>` | 发布分支 | `release/2.0.0` |

### 5.2 分支工作流

```
main (稳定版本)
  ↑
  ├── release/2.0.0 (发布准备)
  │     ↑
  │     └── develop (开发分支)
  │           ├── feature/heatmap
  │           ├── feature/venn-diagram
  │           └── fix/color-mapping
```

### 5.3 分支规则

- `main` 分支始终保持可发布状态
- 所有开发在 `develop` 分支进行
- 功能分支从 `develop` 创建，完成后合并回 `develop`
- 发布分支从 `develop` 创建，测试通过后合并到 `main` 和 `develop`
- 紧急修复从 `main` 创建，同时合并到 `main` 和 `develop`

### 5.4 合并策略

- 使用 **Squash and Merge** 合并功能分支
- 使用 **Merge Commit** 合并发布分支
- 合并前必须通过 CI 测试

---

## 6. 文档规范

### 6.1 文档字符串要求

- 所有公共函数**必须**有文档字符串
- 文档字符串格式: **Google style**
- **必须**包含: 参数说明、返回值、异常 (如有)
- **建议**包含: 示例代码

### 6.2 文档字符串模板

```python
def function_name(
    param1: str,
    param2: int = 0,
    param3: Optional[list] = None,
) -> ReturnType:
    """
    函数简短描述。

    函数详细描述（可选，当简短描述不足以说明时添加）。

    Args:
        param1: 参数1的说明
        param2: 参数2的说明，默认为 0
        param3: 参数3的说明，默认为 None

    Returns:
        ReturnType: 返回值的说明

    Raises:
        ValueError: 当参数不合法时
        TypeError: 当类型不匹配时

    Examples:
        >>> result = function_name("test", param2=1)
        >>> print(result)
        'expected output'

    Note:
        一些需要注意的事项。

    See Also:
        related_function: 相关函数的说明
    """
    ...
```

### 6.3 模块文档字符串

每个模块文件顶部必须有模块文档字符串:

```python
"""
热力图绘制模块。

本模块提供学术风格热力图的绘制功能，支持自定义颜色映射、
标签显示、数值标注等特性。

Typical usage example:

    from sciplot.plots import heatmap
    fig = heatmap(data, labels=["A", "B", "C"])
"""
```

### 6.4 其他文档

- `README.md`: 项目介绍、安装说明、快速开始
- `CHANGELOG.md`: 版本更新日志
- `CONTRIBUTING.md`: 贡献指南

---

## 7. 发布流程

### 7.1 发布检查清单

- [ ] 所有测试通过
- [ ] ruff 检查通过
- [ ] mypy 类型检查通过
- [ ] 测试覆盖率 >80%
- [ ] 文档已更新

### 7.2 发布步骤

1. **更新版本号**
   ```toml
   # pyproject.toml
   [project]
   version = "2.0.0"
   ```

2. **更新 CHANGELOG.md**
   ```markdown
   ## [2.0.0] - 2025-01-01
   ### Added
   - 新增热力图功能
   ### Fixed
   - 修复颜色映射问题
   ```

3. **创建 Git tag**
   ```bash
   git tag -a v2.0.0 -m "Release version 2.0.0"
   git push origin v2.0.0
   ```

4. **GitHub Release**
   - 在 GitHub 上创建 Release
   - 触发自动发布到 PyPI

### 7.3 自动发布

发布通过 GitHub Actions 自动完成:

- 创建 Release 时触发 `.github/workflows/publish.yml`
- 自动构建并发布到 PyPI
- 自动创建 GitHub Release

---

## 8. 依赖管理

### 8.1 核心依赖

| 包名 | 版本要求 | 说明 |
|------|----------|------|
| matplotlib | >=3.5.0 | 绘图引擎 |
| numpy | >=1.20.0 | 数值计算 |
| scienceplots | >=2.1.0 | 学术样式 |
| networkx | >=3.1 | 网络图支持 |

### 8.2 可选依赖

| 依赖组 | 包名 | 说明 |
|--------|------|------|
| ml | scikit-learn>=1.0.0 | 机器学习可视化 |
| stats | scipy>=1.10.1 | 统计分析 |
| network | networkx>=2.6.0 | 网络图 |
| venn | matplotlib-venn>=0.11.0 | 韦恩图 |

### 8.3 安装方式

```bash
# 安装核心依赖
uv pip install sciplot-academic

# 安装特定可选依赖
uv pip install sciplot-academic[ml]
uv pip install sciplot-academic[stats]

# 安装所有依赖
uv pip install sciplot-academic[all]

# 开发环境
uv pip install sciplot-academic[dev]
```

### 8.4 依赖管理工具

- 使用 **uv** 管理依赖
- 锁文件: `uv.lock`
- 添加新依赖时运行 `uv lock` 更新锁文件

---

## 9. CI/CD 规则

### 9.1 CI 流程

所有 PR 必须通过以下检查:

| 检查项 | 工具 | 要求 |
|--------|------|------|
| 代码检查 | ruff | 必须通过 (不能 `\|\| true`) |
| 类型检查 | mypy | 必须通过 |
| 单元测试 | pytest | 必须通过 |
| 测试覆盖率 | pytest-cov | >80% |

### 9.2 CI 配置

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --all-extras
      - run: uv run ruff check .
      - run: uv run mypy sciplot
      - run: uv run pytest --cov=sciplot
```

### 9.3 PR 要求

- ✅ 所有 CI 检查必须通过
- ✅ 至少一个维护者审核通过
- ✅ 分支必须是最新状态 (rebase 或 merge)
- ✅ commit message 符合规范

### 9.4 发布流程

```yaml
# .github/workflows/publish.yml
name: Publish
on:
  release:
    types: [published]
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv build
      - run: uv publish
```

---

## 10. 项目文件清单

### 10.1 必须维护的文件

| 文件 | 说明 | 位置 |
|------|------|------|
| README.md | 项目介绍 | 根目录 |
| LICENSE | 开源协议 | 根目录 |
| CONTRIBUTING.md | 贡献指南 | 根目录 |
| CHANGELOG.md | 更新日志 | 根目录 |
| pyproject.toml | 项目配置 | 根目录 |
| pytest.ini | 测试配置 | 根目录 (可迁移至 pyproject.toml) |
| .github/workflows/ci.yml | CI 配置 | .github/workflows/ |
| .github/workflows/publish.yml | 发布配置 | .github/workflows/ |

### 10.2 目录结构

```
sciplot/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── publish.yml
├── sciplot/              # 源代码
│   ├── __init__.py
│   ├── plots/           # 绘图模块
│   ├── styles/          # 样式模块
│   └── utils/           # 工具模块
├── tests/               # 测试代码
│   ├── unit/
│   ├── integration/
│   └── regression/
├── docs/                # 文档
├── examples/            # 示例
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
└── uv.lock
```

### 10.3 文件维护责任

- **README.md**: 保持与项目功能同步更新
- **CHANGELOG.md**: 每次发布必须更新
- **pyproject.toml**: 版本号、依赖变更时更新
- **CI 配置**: 工具链变更时更新

---

## 附录

### A. 常用命令

```bash
# 代码检查
uv run ruff check .
uv run ruff check --fix .

# 类型检查
uv run mypy sciplot

# 运行测试
uv run pytest
uv run pytest -m unit
uv run pytest --cov=sciplot

# 构建
uv build

# 添加依赖
uv add <package>
uv add --optional <group> <package>
```

### B. 参考资源

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)

---

*最后更新: 2025-01-01*
*维护者: SciPlot Team*
