# SciPlot Academic 扩展开发设计文档

> 基于 v1.7.4 现状，按功能模块分批实现扩展路线图

---

## 一、设计概览

### 1.1 批次划分

| 批次 | 模块 | 主要任务 | 预计新增代码量 |
|------|------|----------|----------------|
| **第一批** | 核心架构改进 | 统一返回 PlotResult、线程安全 StyleContext、配置持久化系统 | ~300 行 |
| **第二批** | 新增图表类型 | 雷达图、时序图、平行坐标图、残差图/QQ图/Bland-Altman | ~600 行 |
| **第三批** | 配色系统扩展 | 发散型配色(2)、序列型配色(3)、场景主题配色(3) | ~150 行 |
| **第四批** | 扩展功能 | 网络图、树状图/层次聚类、Venn图 | ~500 行 |

### 1.2 核心设计原则

1. **向后兼容**：`PlotResult` 的 `__iter__` 确保现有代码 `fig, ax = sp.plot(...)` 无需修改
2. **线程安全**：使用 `threading.local()` 替代类变量
3. **配置优先级**：函数参数 > 代码设置 > 配置文件 > 内置默认
4. **可选依赖**：网络图、树状图、Venn图作为可选依赖，不影响核心功能
5. **统一风格**：所有新增图表遵循现有配色系统和样式规范

---

## 二、第一批：核心架构改进

### 2.1 统一返回 PlotResult

**改造范围**：
- `_plots/basic.py`：`plot_line`, `plot_multi`, `plot_scatter`, `plot_step`, `plot_area`, `plot_multi_area`
- `_plots/distribution.py`：`plot_bar`, `plot_grouped_bar`, `plot_stacked_bar`, `plot_hist`, `plot_box`, `plot_violin`
- `_plots/advanced.py`：`plot_errorbar`, `plot_confidence`, `plot_heatmap`
- `_ext/ml.py`：`plot_pca`, `plot_confusion_matrix`
- `_ext/plot3d.py`：`plot_surface`, `plot_contour3d`, `plot_scatter3d`, `plot_wireframe`

**改造策略**：
1. 修改函数返回类型注解为 `PlotResult`
2. 返回语句改为 `return PlotResult(fig, ax, metadata={...})`
3. metadata 仅存储 `venue`、`palette`、`lang` 等样式参数（最小化）

**示例**：
```python
# 改造前
def plot_line(...) -> Tuple[Figure, Axes]:
    ...
    return fig, ax

# 改造后
def plot_line(...) -> PlotResult:
    ...
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})
```

### 2.2 线程安全 StyleContext

**问题**：`_context_stack` 是类变量，多线程/Jupyter 并发时会冲突。

**解决方案**：
```python
import threading

class StyleContext:
    _local = threading.local()
    
    @classmethod
    def _get_stack(cls) -> List[Dict[str, Any]]:
        """获取当前线程的上下文栈"""
        if not hasattr(cls._local, "stack"):
            cls._local.stack = []
        return cls._local.stack
```

**改造点**：
- 将 `_context_stack` 类变量替换为 `_local` 线程局部存储
- 所有 `StyleContext._context_stack` 访问改为 `cls._get_stack()`
- `is_in_context()` 和 `get_current_context()` 方法相应更新

### 2.3 配置持久化系统

**新建文件**：`sciplot/_core/config.py`

**核心类设计**：
```python
class SciPlotConfig:
    _defaults = {
        "venue": "nature",
        "palette": "pastel",
        "lang": "zh",
        "dpi": 1200,
        "formats": ("pdf", "png"),
    }
    _user_settings: Dict[str, Any] = {}
    _file_settings: Dict[str, Any] = {}
    
    @classmethod
    def set_defaults(cls, **kwargs): ...
    
    @classmethod
    def get(cls, key: str) -> Any: ...
    
    @classmethod
    def load_from_file(cls, path: Optional[str] = None): ...
```

**配置优先级**：函数参数 > 代码设置 > 配置文件 > 内置默认

**支持的配置文件**：
- `pyproject.toml` 的 `[tool.sciplot]` 段
- `.sciplot.toml`（当前目录）

---

## 三、第二批：新增图表类型

### 3.1 雷达图（`plot_radar`）

**新建文件**：`sciplot/_plots/polar.py`

**函数签名**：
```python
def plot_radar(
    categories: List[str],
    values_list: List[List[float]],
    labels: Optional[List[str]] = None,
    fill: bool = True,
    alpha: float = 0.3,
    title: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> PlotResult:
```

**实现要点**：
- 使用 matplotlib 极坐标 `projection='polar'`
- 自动处理首尾闭合（将第一个值追加到末尾）
- 支持多组数据叠加对比
- 配色与现有系统对接

### 3.2 时序图（`plot_timeseries`）

**新建文件**：`sciplot/_plots/timeseries.py`

**函数签名**：
```python
def plot_timeseries(
    t: Union[List, np.ndarray],
    y: Union[List, np.ndarray],
    events: Optional[List[Dict]] = None,      # [{"time": x, "label": "事件"}]
    shade_regions: Optional[List[Dict]] = None,  # [{"start": x, "end": y, "color": "..."}]
    rolling_mean: Optional[int] = None,       # 滚动均值窗口
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> PlotResult:
```

**实现要点**：
- 自动检测 x 轴类型（datetime/数值）
- `events`：在特定时间点添加垂直标注线
- `shade_regions`：给时间段添加背景色
- `rolling_mean`：自动叠加滚动均值线

### 3.3 平行坐标图（`plot_parallel`）

**新建文件**：`sciplot/_plots/multivariate.py`

**函数签名**：
```python
def plot_parallel(
    data: Union[np.ndarray, "pd.DataFrame"],
    columns: Optional[List[str]] = None,
    labels: Optional[List[str]] = None,
    color_by: Optional[Union[int, str]] = None,  # 按某列着色
    normalize: str = "minmax",  # "minmax" 或 "zscore"
    alpha: float = 0.5,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> PlotResult:
```

### 3.4 残差图/QQ图/Bland-Altman

**新建文件**：`sciplot/_plots/statistical.py`

**函数签名**：
```python
def plot_residuals(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> PlotResult:

def plot_qq(
    data: np.ndarray,
    distribution: str = "norm",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> PlotResult:

def plot_bland_altman(
    y1: np.ndarray,
    y2: np.ndarray,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> PlotResult:
```

---

## 四、第三批：配色系统扩展

### 4.1 发散型配色

**新增配色定义**（在 `palette.py` 中）：
```python
DIVERGING_PALETTES = {
    "cherry_mint": [
        "#8B1C2D", "#C44B5E", "#E8A0AA", "#F5E6E8",  # 红到白
        "#E0F0E8", "#8ECAAA", "#3C8A66", "#1A5C3E",  # 白到绿
    ],
    "sunset_ocean": [
        "#7B1A00", "#C44200", "#F08040", "#FAD5A0",  # 橙到白
        "#C8E8F8", "#5BA8D0", "#1060A0", "#003060",  # 白到蓝
    ],
}
```

### 4.2 序列型配色

```python
SEQUENTIAL_PALETTES = {
    "pastel_seq": ["#f0e6ff", "#cdb4db", "#a07aba", "#6b4490", "#3d1560"],  # 浅紫到深紫
    "earth_seq":  ["#fef9ec", "#e9c46a", "#c07830", "#7a3c10", "#3a1a00"],  # 浅黄到深棕
    "ocean_seq":  ["#f0f8ff", "#afd1bf", "#5fa090", "#2a6860", "#0a3028"],  # 浅蓝到深青
}
```

### 4.3 场景主题配色

```python
THEME_PALETTES = {
    "medical": ["#E8D5E0", "#C4879B", "#A03060", "#6B1840", "#380C20"],
    "material": ["#F0F0F0", "#B0C8D0", "#607880", "#304048", "#101820"],
    "ml_modern": ["#FF6B6B", "#4ECDC4", "#FFE66D", "#A8E6CF", "#6C5CE7"],
}
```

### 4.4 配色系统整合

**新增函数**：
```python
def get_diverging_palette(name: str) -> List[str]: ...
def get_sequential_palette(name: str) -> List[str]: ...
def get_theme_palette(name: str) -> List[str]: ...
def list_diverging_palettes() -> List[str]: ...
def list_sequential_palettes() -> List[str]: ...
def list_theme_palettes() -> List[str]: ...
```

---

## 五、第四批：扩展功能

### 5.1 网络图（`plot_network`）

**新建文件**：`sciplot/_ext/network.py`

**可选依赖**：`networkx`

**函数签名**：
```python
def plot_network(
    G: "nx.Graph",
    layout: str = "spring",  # spring, circular, hierarchical, spectral, kamada_kawai
    node_color_by: Optional[str] = None,
    node_size_by: Optional[str] = None,
    edge_weight_by: Optional[str] = None,
    labels: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> PlotResult:

def plot_network_from_matrix(
    adj_matrix: np.ndarray,
    threshold: float = 0.0,
    **kwargs,
) -> PlotResult:

def plot_network_communities(
    G: "nx.Graph",
    communities: List[List[int]],
    **kwargs,
) -> PlotResult:
```

### 5.2 树状图/层次聚类（`plot_dendrogram`）

**新建文件**：`sciplot/_ext/hierarchical.py`

**可选依赖**：`scipy`

**函数签名**：
```python
def plot_dendrogram(
    data_or_linkage: Union[np.ndarray, "Linkage"],
    labels: Optional[List[str]] = None,
    orientation: str = "top",
    color_threshold: Optional[float] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> PlotResult:

def plot_clustermap(
    data: np.ndarray,
    row_labels: Optional[List[str]] = None,
    col_labels: Optional[List[str]] = None,
    row_cluster: bool = True,
    col_cluster: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> PlotResult:
```

### 5.3 Venn 图

**新建文件**：`sciplot/_ext/venn.py`

**可选依赖**：`matplotlib-venn`

**函数签名**：
```python
def plot_venn2(
    subsets: Union[Tuple[int, int, int], Dict[str, int]],
    set_labels: Tuple[str, str] = ("A", "B"),
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> PlotResult:

def plot_venn3(
    subsets: Union[Tuple[int, int, int, int, int, int, int], Dict[str, int]],
    set_labels: Tuple[str, str, str] = ("A", "B", "C"),
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    **kwargs,
) -> PlotResult:
```

---

## 六、测试策略

### 6.1 测试文件规划

| 批次 | 测试文件 | 测试重点 |
|------|----------|----------|
| **第一批** | `test_result_types.py`, `test_context.py`, `test_config.py` | 返回值类型、线程安全、配置加载 |
| **第二批** | `test_polar.py`, `test_timeseries.py`, `test_multivariate.py`, `test_statistical.py` | 新图表功能、边界条件 |
| **第三批** | `test_palette.py`（扩展） | 新配色应用、列表函数 |
| **第四批** | `test_network.py`, `test_hierarchical.py`, `test_venn.py` | 可选依赖处理、功能正确性 |

### 6.2 测试原则

- **无头渲染**：`matplotlib.use("Agg")`
- **输入验证**：边界条件、错误类型、错误信息
- **视觉回归**：关键图表的样式验证

---

## 七、实施计划

### 第一批（核心架构）
1. 修改 `context.py` 实现线程安全
2. 新建 `config.py` 实现配置持久化
3. 修改所有绘图函数返回 `PlotResult`
4. 更新 `__init__.py` 导出
5. 运行全部测试确保无回归

### 第二批（新图表）
1. 新建 `polar.py` 实现雷达图
2. 新建 `timeseries.py` 实现时序图
3. 新建 `multivariate.py` 实现平行坐标图
4. 新建 `statistical.py` 实现残差图/QQ图/Bland-Altman
5. 更新导出并添加测试

### 第三批（配色扩展）
1. 在 `palette.py` 添加新配色定义
2. 添加配色获取函数
3. 更新导出并添加测试

### 第四批（扩展功能）
1. 新建 `network.py` 实现网络图
2. 新建 `hierarchical.py` 实现树状图
3. 新建 `venn.py` 实现 Venn 图
4. 更新 `pyproject.toml` 添加可选依赖
5. 更新导出并添加测试

---

*版本：2026-04-17 · SciPlot Academic 扩展开发设计文档*
