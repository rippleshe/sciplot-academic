"""
数据画像分析与图表智能推荐引擎。

先对输入数据集执行结构化画像（行数、变量类型、基数、偏度、异常值率、
相关性、对称性、时间单调性与特殊科研字段模式），再依据感知编码精度与
图表表达力规则，推荐最契合的多样化图表（优先单轴信息融合与复合布局，
避免千篇一律地退化为简单柱状图或折线图）。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np


@dataclass
class ColumnProfile:
    """单列（或单系列）数据的统计与类型画像。"""

    name: str
    kind: str  # "numeric_continuous" | "numeric_discrete" | "binary" | "categorical" | "datetime" | "id_like"
    count: int
    n_unique: int
    missing_count: int
    missing_ratio: float
    is_monotonic: bool = False
    is_positive_only: bool = False
    is_probability_like: bool = False
    spans_orders: bool = False
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    q25: Optional[float] = None
    median: Optional[float] = None
    q75: Optional[float] = None
    max: Optional[float] = None
    skewness: Optional[float] = None
    outlier_rate: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DataProfile:
    """输入数据集的全局结构画像。"""

    input_kind: str  # "dataframe" | "dict" | "matrix" | "groups" | "series"
    n_rows: int
    n_cols: int
    shape_pattern: str  # "univariate" | "bivariate" | "grouped_samples" | "category_scalar" | "matrix" | "square_corr" | "multivariate" | "timeseries" | "domain_specific"
    columns: List[ColumnProfile] = field(default_factory=list)
    numeric_cols: List[str] = field(default_factory=list)
    categorical_cols: List[str] = field(default_factory=list)
    datetime_cols: List[str] = field(default_factory=list)
    binary_cols: List[str] = field(default_factory=list)
    special_hints: List[str] = field(default_factory=list)
    corr_summary: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data

    def summary(self) -> str:
        """生成便于终端与智能体阅读的数据画像摘要。"""
        lines = [
            f"### 数据结构画像（{self.input_kind} | {self.n_rows} 行 × {self.n_cols} 列 | 形态: `{self.shape_pattern}`）",
        ]
        if self.special_hints:
            lines.append(f"- 识别到的结构信号: {', '.join(self.special_hints)}")
        for col in self.columns[:12]:
            if col.kind.startswith("numeric") or col.kind == "binary":
                lines.append(
                    f"- **{col.name}** (`{col.kind}`): n={col.count}, unique={col.n_unique}, "
                    f"range=[{col.min:.3g}, {col.max:.3g}], median={col.median:.3g}, "
                    f"skew={col.skewness:.2f}, outliers={col.outlier_rate:.1%}"
                    if col.min is not None and col.skewness is not None and col.outlier_rate is not None
                    else f"- **{col.name}** (`{col.kind}`): n={col.count}, unique={col.n_unique}"
                )
            else:
                lines.append(
                    f"- **{col.name}** (`{col.kind}`): n={col.count}, unique={col.n_unique}, missing={col.missing_ratio:.1%}"
                )
        if len(self.columns) > 12:
            lines.append(f"- ……其余 {len(self.columns) - 12} 列已省略")
        for w in self.warnings:
            lines.append(f"- ⚠️ {w}")
        return "\n".join(lines)


@dataclass
class ChartRecommendation:
    """单条图表推荐方案。"""

    chart_type: str
    sciplot_func: str
    score: float
    why_fit: str
    visual_channels: str
    palette_type: str  # "categorical" | "sequential" | "diverging"
    recommended_palette: str
    avoids_monotony: str
    code_snippet: str
    composite_suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ChartRecommendationReport:
    """完整的“数据画像 + 图表选型推荐报告”。"""

    profile: DataProfile
    goal: str
    recommendations: List[ChartRecommendation] = field(default_factory=list)
    composite_plan: Optional[str] = None

    def summary(self) -> str:
        """输出结构化 Markdown 推荐报告。"""
        lines = [self.profile.summary(), "", f"### 图表智能推荐（目标: `{self.goal}`）"]
        for rank, rec in enumerate(self.recommendations, start=1):
            lines.append(
                f"{rank}. **{rec.chart_type}** — `sp.{rec.sciplot_func}(...)` "
                f"(匹配度: {rec.score:.0f}/100)"
            )
            lines.append(f"   - 适配原因: {rec.why_fit}")
            lines.append(f"   - 视觉通道与配色: {rec.visual_channels} | 推荐配色 `{rec.recommended_palette}` ({rec.palette_type})")
            lines.append(f"   - 避免单调/误导: {rec.avoids_monotony}")
            lines.append(f"   - 示例调用: `{rec.code_snippet}`")
        if self.composite_plan:
            lines.extend(["", f"### 复合/多面板叙事建议\n- {self.composite_plan}"])
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile": self.profile.to_dict(),
            "goal": self.goal,
            "recommendations": [r.to_dict() for r in self.recommendations],
            "composite_plan": self.composite_plan,
        }


def _safe_skewness(vals: np.ndarray) -> float:
    """基于三阶中心矩计算稳健样本偏度。"""
    if vals.size < 3:
        return 0.0
    std = float(np.std(vals))
    if std <= 1e-12:
        return 0.0
    centered = vals - float(np.mean(vals))
    return float(np.mean(centered**3) / (std**3))


def _load_data_input(data: Any) -> Any:
    """将文件路径、表格或数组输入归一化以便分析。"""
    if isinstance(data, (str, Path)):
        path = Path(data)
        if not path.exists():
            raise FileNotFoundError(f"数据文件不存在: {path}")
        suffix = path.suffix.lower()
        try:
            import pandas as pd  # type: ignore
        except ImportError as exc:
            raise ImportError("读取表格文件需要安装 pandas。请运行: uv add pandas") from exc
        if suffix in {".csv"}:
            return pd.read_csv(path)
        if suffix in {".tsv", ".txt"}:
            return pd.read_csv(path, sep="\t")
        if suffix in {".xlsx", ".xls"}:
            return pd.read_excel(path)
        if suffix == ".json":
            return pd.read_json(path)
        if suffix == ".parquet":
            return pd.read_parquet(path)
        raise ValueError(f"暂不支持的数据文件格式: {suffix}")
    return data


def _profile_column(name: str, values: Sequence[Any]) -> ColumnProfile:
    """提取单个变量列的统计画像。"""
    arr_obj = np.asarray(values, dtype=object).ravel()
    total = int(arr_obj.size)
    # 缺失统计
    missing_mask = np.zeros(total, dtype=bool)
    for idx, val in enumerate(arr_obj):
        if val is None or (isinstance(val, float) and np.isnan(val)):
            missing_mask[idx] = True
        elif isinstance(val, str) and val.strip() == "":
            missing_mask[idx] = True
    missing_count = int(np.sum(missing_mask))
    valid_vals = arr_obj[~missing_mask]

    # 检测日期类型或日期字符串
    is_dt = False
    if hasattr(values, "dtype") and np.issubdtype(np.asarray(values).dtype, np.datetime64):
        is_dt = True
    elif valid_vals.size > 0 and isinstance(valid_vals[0], str):
        sample = [str(v).strip() for v in valid_vals[: min(10, valid_vals.size)]]
        if all(len(s) >= 8 and ("-" in s or "/" in s) and any(ch.isdigit() for ch in s) for s in sample):
            is_dt = True

    if is_dt:
        n_unique = len(set(str(v) for v in valid_vals))
        return ColumnProfile(
            name=name, kind="datetime", count=total,
            n_unique=n_unique, missing_count=missing_count,
            missing_ratio=(missing_count / total if total else 0.0),
            is_monotonic=True,
        )

    # 尝试作为数值解析
    numeric_vals: Optional[np.ndarray] = None
    try:
        cand = np.asarray(valid_vals, dtype=float)
        if cand.size == valid_vals.size and cand.size > 0:
            finite = cand[np.isfinite(cand)]
            if finite.size == cand.size:
                numeric_vals = cand
    except (ValueError, TypeError):
        numeric_vals = None

    if numeric_vals is not None and numeric_vals.size > 0:
        uniq = np.unique(numeric_vals)
        n_unique = int(uniq.size)
        v_min = float(np.min(numeric_vals))
        v_max = float(np.max(numeric_vals))
        q25, med, q75 = [float(x) for x in np.percentile(numeric_vals, [25, 50, 75])]
        iqr = q75 - q25
        outliers = int(np.sum((numeric_vals < q25 - 1.5 * iqr) | (numeric_vals > q75 + 1.5 * iqr)))
        is_int_like = bool(np.all(np.isclose(numeric_vals, np.round(numeric_vals))))
        is_mono = bool(
            numeric_vals.size >= 3
            and (np.all(np.diff(numeric_vals) >= 0) or np.all(np.diff(numeric_vals) <= 0))
        )
        pos_only = bool(v_min >= 0.0)
        prob_like = bool(v_min >= 0.0 and v_max <= 1.0)
        spans_orders = bool(v_min > 0 and v_max / max(v_min, 1e-12) >= 100.0)

        if set(uniq.tolist()).issubset({0.0, 1.0}) and n_unique <= 2:
            kind = "binary"
        elif (
            "id" in name.lower()
            and is_int_like
            and n_unique == total
            and total >= 10
        ):
            kind = "id_like"
        elif is_int_like and n_unique <= min(12, max(4, total // 4)):
            kind = "numeric_discrete"
        else:
            kind = "numeric_continuous"

        return ColumnProfile(
            name=name, kind=kind, count=total,
            n_unique=n_unique, missing_count=missing_count,
            missing_ratio=(missing_count / total if total else 0.0),
            is_monotonic=is_mono,
            is_positive_only=pos_only,
            is_probability_like=prob_like,
            spans_orders=spans_orders,
            mean=float(np.mean(numeric_vals)),
            std=float(np.std(numeric_vals)),
            min=v_min, q25=q25, median=med, q75=q75, max=v_max,
            skewness=_safe_skewness(numeric_vals),
            outlier_rate=outliers / numeric_vals.size,
        )

    # 非数值：字符串 / 分类变量
    str_vals = [str(v) for v in valid_vals]
    n_unique = len(set(str_vals))
    kind = "id_like" if (n_unique == total and total >= 20) else "categorical"
    return ColumnProfile(
        name=name, kind=kind, count=total,
        n_unique=n_unique, missing_count=missing_count,
        missing_ratio=(missing_count / total if total else 0.0),
    )


def profile_data(
    data: Any,
    *,
    columns: Optional[Sequence[str]] = None,
    target: Optional[str] = None,
    time_col: Optional[str] = None,
    group_col: Optional[str] = None,
) -> DataProfile:
    """分析任意输入数据的形态、变量类型、分布特征与科研领域信号。

    支持 ``pandas.DataFrame``、``dict``、二维/一维 ``numpy.ndarray``、
    数组列表 ``[group1, group2, ...]``，以及 ``.csv/.tsv/.xlsx/.json`` 路径。
    """
    loaded = _load_data_input(data)
    special_hints: List[str] = []
    warnings_list: List[str] = []

    # 1. DataFrame 路径
    if hasattr(loaded, "columns") and hasattr(loaded, "iloc"):
        df = loaded
        col_profiles = [_profile_column(str(c), df[c].to_numpy()) for c in df.columns]
        input_kind = "dataframe"
        n_rows, n_cols = int(df.shape[0]), int(df.shape[1])

    # 2. 字典路径：{系列名: 序列} 或 {列名: 列值} 或 {分组: 数值序列}
    elif isinstance(loaded, dict):
        if not loaded:
            raise ValueError("输入字典不能为空")
        col_profiles = []
        lengths = []
        for k, v in loaded.items():
            v_arr = np.asarray(v, dtype=object).ravel()
            lengths.append(int(v_arr.size))
            col_profiles.append(_profile_column(str(k), v_arr))
        input_kind = "dict"
        n_rows = max(lengths) if lengths else 0
        n_cols = len(loaded)
        if len(set(lengths)) > 1:
            special_hints.append("grouped_variable_lengths")

    # 3. 组列表：[arr1, arr2, ...]
    elif (
        isinstance(loaded, (list, tuple))
        and loaded
        and isinstance(loaded[0], (list, tuple, np.ndarray))
    ):
        lengths = [len(g) for g in loaded]
        col_profiles = [
            _profile_column(
                columns[i] if columns and i < len(columns) else f"Group_{i + 1}",
                np.asarray(g),
            )
            for i, g in enumerate(loaded)
        ]
        # 若所有列表等长，判断是否为二维矩阵 vs 多组采样
        arr_2d = np.asarray(loaded, dtype=float) if len(set(lengths)) == 1 else None
        if arr_2d is not None and arr_2d.ndim == 2 and arr_2d.shape[0] == arr_2d.shape[1] and arr_2d.shape[0] >= 3:
            input_kind = "matrix"
            n_rows, n_cols = arr_2d.shape
        else:
            input_kind = "groups"
            n_rows = max(lengths)
            n_cols = len(loaded)

    # 4. 数组路径：1D / 2D ndarray
    else:
        arr = np.asarray(loaded)
        if arr.ndim == 1:
            col_profiles = [_profile_column("value", arr)]
            input_kind = "series"
            n_rows, n_cols = int(arr.size), 1
        elif arr.ndim == 2:
            n_rows, n_cols = arr.shape
            col_names = (
                list(columns)
                if columns is not None and len(columns) == n_cols
                else [f"Col_{j + 1}" for j in range(n_cols)]
            )
            col_profiles = [_profile_column(col_names[j], arr[:, j]) for j in range(n_cols)]
            input_kind = "matrix"
        else:
            raise ValueError(f"暂仅支持 1D/2D 数组，当前维度: {arr.ndim}")

    numeric_cols = [c.name for c in col_profiles if c.kind in {"numeric_continuous", "numeric_discrete"}]
    categorical_cols = [c.name for c in col_profiles if c.kind == "categorical"]
    datetime_cols = [c.name for c in col_profiles if c.kind == "datetime"]
    binary_cols = [c.name for c in col_profiles if c.kind == "binary"]

    # 检测对称方阵 / 相关矩阵
    if input_kind == "matrix" and n_rows == n_cols and n_rows >= 3:
        mat = np.asarray(loaded, dtype=float) if not hasattr(loaded, "iloc") else np.asarray(loaded.select_dtypes(include=[np.number]), dtype=float)
        if mat.shape[0] == mat.shape[1] and np.allclose(np.nan_to_num(mat), np.nan_to_num(mat.T), atol=1e-5):
            special_hints.append("symmetric_matrix")
            finite_mat = mat[np.isfinite(mat)]
            if finite_mat.size > 0 and finite_mat.min() >= -1.001 and finite_mat.max() <= 1.001:
                special_hints.append("correlation_matrix")

    # 领域字段名识别
    lower_names = {c.name.lower(): c.name for c in col_profiles}
    if any(k in lower_names for k in ("log2fc", "logfc", "fold_change")) and any(
        k in lower_names for k in ("p", "pvalue", "p_value", "pval", "padj", "fdr")
    ):
        special_hints.append("omics_volcano")
    if any(k in lower_names for k in ("ci_low", "lower", "ci_lower")) and any(
        k in lower_names for k in ("ci_high", "upper", "ci_upper")
    ):
        special_hints.append("effect_with_ci")
    if any(k in lower_names for k in ("source", "from")) and any(
        k in lower_names for k in ("target", "to")
    ):
        special_hints.append("flow_links")
    if any(k in lower_names for k in ("before", "pre", "baseline")) and any(
        k in lower_names for k in ("after", "post", "followup")
    ):
        special_hints.append("paired_before_after")
    if binary_cols and any(c.is_probability_like and c.kind == "numeric_continuous" for c in col_profiles):
        special_hints.append("binary_probabilities")
    if time_col or datetime_cols or any(k in lower_names for k in ("time", "date", "year", "month", "epoch", "step", "week", "day")):
        special_hints.append("time_ordered")

    # 检查双变量相关性
    corr_summary: Dict[str, float] = {}
    if len(numeric_cols) >= 2 and input_kind in {"dataframe", "matrix", "dict"}:
        try:
            cols_data = []
            for cname in numeric_cols[:8]:
                if hasattr(loaded, "iloc"):
                    vals = np.asarray(loaded[cname], dtype=float)
                elif isinstance(loaded, dict):
                    vals = np.asarray(loaded[cname], dtype=float)
                else:
                    idx = [c.name for c in col_profiles].index(cname)
                    vals = np.asarray(loaded, dtype=float)[:, idx]
                cols_data.append(vals)
            mat_sub = np.column_stack(cols_data)
            valid_rows = np.all(np.isfinite(mat_sub), axis=1)
            if np.sum(valid_rows) >= 3:
                cmat = np.corrcoef(mat_sub[valid_rows], rowvar=False)
                off_diag = np.abs(cmat - np.eye(cmat.shape[0]))
                corr_summary["max_abs_r"] = float(np.nanmax(off_diag))
        except Exception:
            pass

    # 缺失值与极端偏态警告
    high_missing = [c.name for c in col_profiles if c.missing_ratio > 0.1]
    if high_missing:
        warnings_list.append(f"以下列缺失率超过 10%，可视化前请先清洗/说明: {', '.join(high_missing)}")
    heavy_skew = [
        c.name for c in col_profiles
        if c.skewness is not None and abs(c.skewness) >= 1.5
    ]
    if heavy_skew:
        warnings_list.append(f"强偏态变量 ({', '.join(heavy_skew)})，勿只用均值±柱状图掩盖长尾")

    # 判定全局数据形态
    if "symmetric_matrix" in special_hints or "correlation_matrix" in special_hints:
        shape_pattern = "square_corr"
    elif any(h in special_hints for h in ("omics_volcano", "effect_with_ci", "flow_links", "binary_probabilities", "paired_before_after")):
        shape_pattern = "domain_specific"
    elif input_kind == "groups" or (input_kind == "dict" and "grouped_variable_lengths" in special_hints) or (
        input_kind == "dict" and all(c.kind.startswith("numeric") for c in col_profiles) and n_rows >= 8 and n_cols <= 12 and not datetime_cols
    ):
        shape_pattern = "grouped_samples"
    elif input_kind == "series":
        shape_pattern = "univariate"
    elif "time_ordered" in special_hints and numeric_cols:
        shape_pattern = "timeseries"
    elif len(categorical_cols) == 1 and len(numeric_cols) == 1 and n_rows <= 30 and not group_col:
        # 检查类别是否重复（原始多样本 vs 聚合标量）
        cat_prof = next(c for c in col_profiles if c.name == categorical_cols[0])
        shape_pattern = "category_scalar" if cat_prof.n_unique == n_rows else "grouped_samples"
    elif len(numeric_cols) == 2 and not categorical_cols:
        shape_pattern = "bivariate"
    elif len(numeric_cols) >= 4:
        shape_pattern = "multivariate"
    elif len(numeric_cols) == 1 and len(categorical_cols) >= 2:
        shape_pattern = "category_scalar"
    else:
        shape_pattern = "multivariate" if len(numeric_cols) >= 2 else "category_scalar"

    # 目标参数标注辅助
    if target and target not in [c.name for c in col_profiles]:
        warnings_list.append(f"指定的 target 列 '{target}' 不存在于数据中")

    return DataProfile(
        input_kind=input_kind,
        n_rows=n_rows,
        n_cols=n_cols,
        shape_pattern=shape_pattern,
        columns=col_profiles,
        numeric_cols=numeric_cols,
        categorical_cols=categorical_cols,
        datetime_cols=datetime_cols,
        binary_cols=binary_cols,
        special_hints=special_hints,
        corr_summary=corr_summary,
        warnings=warnings_list,
    )


def recommend_charts(
    data: Any,
    *,
    goal: str = "auto",
    top_k: int = 4,
    columns: Optional[Sequence[str]] = None,
    target: Optional[str] = None,
    time_col: Optional[str] = None,
    group_col: Optional[str] = None,
) -> ChartRecommendationReport:
    """结合数据画像与分析意图，推荐多样化、高信息密度的科研图表。

    优先考虑“单轴多层融合”（如云雨图、小提琴+四分位+散点、回归+置信带+统计卡、
    上三角相关卡+下三角散点）与互补型多面板组合，避免将各类数据简单塞入普通柱状图或箱线图。

    参数:
        data   : DataFrame、字典、ndarray、组列表或数据文件路径
        goal   : 分析目标：``"auto"`` | ``"comparison"`` | ``"distribution"`` |
                 ``"relationship"`` | ``"composition"`` | ``"trend"`` |
                 ``"ranking"`` | ``"multivariate"`` | ``"evaluation"``
        top_k  : 返回最多多少条多样化候选方案（默认 4）
    """
    valid_goals = {
        "auto", "comparison", "distribution", "relationship",
        "composition", "trend", "ranking", "multivariate", "evaluation",
    }
    if goal not in valid_goals:
        raise ValueError(f"未知分析目标 goal={goal!r}，可用: {sorted(valid_goals)}")

    prof = profile_data(
        data, columns=columns, target=target, time_col=time_col, group_col=group_col
    )
    recs: List[ChartRecommendation] = []
    composite_plan: Optional[str] = None

    num_profiles = [c for c in prof.columns if c.kind.startswith("numeric")]
    max_skew = max((abs(c.skewness or 0.0) for c in num_profiles), default=0.0)
    hints = set(prof.special_hints)

    # ── 分支 1：特定领域信号 ──
    if "omics_volcano" in hints:
        recs.append(ChartRecommendation(
            chart_type="火山图 (Volcano Plot)",
            sciplot_func="plot_volcano",
            score=98,
            why_fit="数据包含效应倍数 (log2FC) 与显著性 p 值，火山图可同时映射统计显著性与生物学变化幅度",
            visual_channels="X/Y 位置 + 三态语义色相 + 自动防重叠 Top 基因直标",
            palette_type="categorical",
            recommended_palette="blue-sky",
            avoids_monotony="相比普通散点图或排序条形图，一图同时筛出兼顾高倍数与高显著性的靶标",
            code_snippet='sp.plot_volcano(log2fc, p_values, labels=gene_names, show_counts=True, palette="blue-sky")',
        ))
    if "effect_with_ci" in hints:
        recs.append(ChartRecommendation(
            chart_type="森林图 (Forest Plot)",
            sciplot_func="plot_forest",
            score=97,
            why_fit="包含效应量点估计与 95% 置信区间上下限，森林图是展示多研究/多亚组异质性与合并效应的金标准",
            visual_channels="水平位置（精度最高）+ 区间线长度 + 零效果参考线 + 汇总菱形",
            palette_type="categorical",
            recommended_palette="olive-apricot",
            avoids_monotony="禁止用普通柱状图画效应量（柱高隐含零基线误导且难看清置信区间）",
            code_snippet="sp.plot_forest(effect, ci_low, ci_high, labels=studies, summary=(eff_all, lo_all, hi_all))",
        ))
    if "binary_probabilities" in hints or goal == "evaluation":
        recs.append(ChartRecommendation(
            chart_type="ROC / PR 评价曲线 (ROC/PR Curve)",
            sciplot_func="plot_roc",
            score=96,
            why_fit="含二分类标签与连续预测概率，可评估全阈值判别能力与最优约登切点",
            visual_channels="曲线包络 + 面积/AUC 量化 + 最佳工作点圈标",
            palette_type="categorical",
            recommended_palette="blue-sky",
            avoids_monotony="优于单阈值准确率柱状图（单柱丢失阈值敏感性与类不平衡表现）",
            code_snippet='sp.plot_roc(y_true, {"Model A": prob_a, "Model B": prob_b}, palette="blue-sky")',
        ))
        recs.append(ChartRecommendation(
            chart_type="概率校准可靠性图 (Calibration Plot)",
            sciplot_func="plot_calibration",
            score=90,
            why_fit="校验模型预测概率是否贴合真实发生频率，并给出 ECE 与 Brier 指标",
            visual_channels="对角偏离位置 + ECE 摘要 + 底部预测概率直方密度",
            palette_type="categorical",
            recommended_palette="coral-teal",
            avoids_monotony="弥补 ROC 只看排序不看概率校准的盲区，常与 ROC 组成双面板",
            code_snippet='sp.plot_calibration(y_true, {"Model A": prob_a, "Model B": prob_b}, palette="coral-teal")',
        ))
        composite_plan = "建议使用 `sp.figure_panels(1, 2)` 将判别力 (`plot_roc`) 与概率可靠性 (`plot_calibration`) 或 `plot_confusion_matrix` 并排成组。"
    if "flow_links" in hints:
        recs.append(ChartRecommendation(
            chart_type="桑基图 (Sankey Diagram)",
            sciplot_func="plot_sankey",
            score=96,
            why_fit="存在明确的源节点→目标节点流向关系，适合追踪各阶段流量分配与损耗",
            visual_channels="带宽度（流强）+ 节点色相 + 分段流向",
            palette_type="categorical",
            recommended_palette="ocean-breeze",
            avoids_monotony="普通堆叠柱图完全丢失状态转移路径，桑基图清晰刻画分流比例",
            code_snippet='sp.plot_sankey(flows, palette="ocean-breeze")',
        ))
    if "paired_before_after" in hints:
        recs.append(ChartRecommendation(
            chart_type="配对个体变化图 (Paired Trajectory Plot)",
            sciplot_func="plot_paired",
            score=96,
            why_fit="同一批被试/样本存在前后配对观测，连线色相可直观展现个体响应方向的一致性与异质性",
            visual_channels="个体斜率连线 + 升降双色 + 均值加粗连线 + 配对统计 p 值",
            palette_type="categorical",
            recommended_palette="coral-teal",
            avoids_monotony="严禁用独立组均值柱状图画配对样本（会完全掩盖个体反向响应！）",
            code_snippet='sp.plot_paired(before, after, labels=("处理前", "处理后"), ylabel=ylabel)',
        ))

    # ── 分支 2：相关矩阵 / 方阵 ──
    if prof.shape_pattern == "square_corr":
        recs.append(ChartRecommendation(
            chart_type="下三角相关热力图 + 显著性星号",
            sciplot_func="plot_heatmap",
            score=97 if "correlation_matrix" in hints else 92,
            why_fit=f"{prof.n_rows}×{prof.n_cols} 对称矩阵用下三角屏蔽冗余镜像格，显著降低视觉噪音并支持零点对称双色阶",
            visual_channels="发散色彩明度（零点对齐白色）+ 格内精准数值 + p 值星号",
            palette_type="diverging",
            recommended_palette="rdbu",
            avoids_monotony="相比全矩阵热图减少近一半重复信息与边框干扰",
            code_snippet='sp.plot_heatmap(corr, row_labels=names, col_labels=names, cmap="RdBu_r", vmin=-1, vmax=1, triangle="lower", show_values=True)',
        ))
        recs.append(ChartRecommendation(
            chart_type="分层聚类热图 (Clustermap)",
            sciplot_func="plot_clustermap",
            score=89,
            why_fit="通过层次聚类重排矩阵行列顺序，自动暴露潜藏的协同模块与群落块状结构",
            visual_channels="树状拓扑 + 色彩强弱区块",
            palette_type="diverging",
            recommended_palette="rdbu",
            avoids_monotony="消除任意行列排序造成的局部相关性视觉割裂",
            code_snippet='sp.plot_clustermap(corr, labels=names, cmap="RdBu_r")',
        ))
        recs.append(ChartRecommendation(
            chart_type="双编码气泡热力图 (Bubble Heatmap)",
            sciplot_func="plot_bubble_heatmap",
            score=84,
            why_fit="用圆面积编码 |相关强度|、颜色编码正负方向，强相关条目在视觉上立即弹出",
            visual_channels="气泡面积 + 发散色相双编码",
            palette_type="diverging",
            recommended_palette="rdbu",
            avoids_monotony="比传统纯色块热力图更容易在前注意阶段抓住强相关焦点",
            code_snippet='sp.plot_bubble_heatmap(corr, row_labels=names, col_labels=names, cmap="RdBu_r")',
        ))

    # ── 分支 3：单变量 / 多组原始样本分布 ──
    if prof.shape_pattern == "univariate":
        n = prof.n_rows
        recs.extend([
            ChartRecommendation(
                chart_type="核密度叠加直方图 (Hist + KDE + Median)",
                sciplot_func="plot_histogram",
                score=94,
                why_fit=f"单变量样本量 n={n}（偏度={max_skew:.2f}），直方分箱报告真实频数，叠加 KDE 曲线与中位数参考线揭示峰态与偏斜",
                visual_channels="柱高（精确频数）+ 连续平滑密度曲线 + 中位数参考线",
                palette_type="categorical",
                recommended_palette="blue-sky",
                avoids_monotony="避免仅画裸箱线图掩盖双峰性，或仅画纯均值±误差棒",
                code_snippet='sp.plot_histogram(values, bins=30, show_kde=True, show_median=True, palette="blue-sky")',
            ),
            ChartRecommendation(
                chart_type="单组云雨图 (Raincloud Plot)",
                sciplot_func="plot_raincloud",
                score=89 if n >= 20 else 76,
                why_fit="同步显示半小提琴密度包络、IQR 四分位箱体与逐个原始数据点",
                visual_channels="KDE 轮廓 + IQR 长度 + 原始散点位置三层融合",
                palette_type="categorical",
                recommended_palette="coral-teal",
                avoids_monotony="将汇总统计量与原始样本分布同轴展示，忠实还原数据全貌",
                code_snippet='sp.plot_raincloud([values], labels=["样本分布"], palette="coral-teal")',
            ),
            ChartRecommendation(
                chart_type="正态分位 Q-Q 诊断图",
                sciplot_func="plot_qq",
                score=81,
                why_fit="检验单变量是否服从正态分布并定位重尾或截断区域",
                visual_channels="分位数位置对角线偏离",
                palette_type="categorical",
                recommended_palette="olive-apricot",
                avoids_monotony="比静态统计数字更直观判断后续 t 检验/ANOVA 前提是否成立",
                code_snippet="sp.plot_qq(values)",
            ),
        ])

    if prof.shape_pattern == "grouped_samples":
        k_groups = max(len(num_profiles), 2)
        if prof.categorical_cols and len(prof.numeric_cols) == 1:
            cat_c = next(c for c in prof.columns if c.name == prof.categorical_cols[0])
            k_groups = max(cat_c.n_unique, 2)
        per_group_n = prof.n_rows // max(k_groups if prof.categorical_cols else 1, 1)

        if k_groups <= 5 and per_group_n >= 15:
            recs.append(ChartRecommendation(
                chart_type="云雨图 (Raincloud Plot — 半提琴+箱线+原始点)",
                sciplot_func="plot_raincloud",
                score=97,
                why_fit=f"{k_groups} 组对比且每组约 {per_group_n} 个观测（最大偏度={max_skew:.2f}），足够支撑 KDE 密度估计并暴露多峰/异常点细节",
                visual_channels="半小提琴形状 + 箱体分位数 + 散点原始位置三层叠加",
                palette_type="categorical",
                recommended_palette="coral-teal",
                avoids_monotony="坚决摒弃普通柱状图/单箱线图（相同均值与 IQR 可对应截然不同的双峰或偏态分布）",
                code_snippet='sp.plot_raincloud(groups, labels=group_names, palette="coral-teal")',
            ))
        if 5 <= k_groups <= 16:
            recs.append(ChartRecommendation(
                chart_type="山脊图 (Ridgeline Plot)",
                sciplot_func="plot_ridgeline",
                score=94,
                why_fit=f"分组数达 {k_groups} 组，横向交叠 KDE 山脊可在紧凑空间内同时对比分布重心偏移与展宽演变",
                visual_channels="水平位置对齐 + 垂直层叠白色描边隔离 + 中位数竖线",
                palette_type="sequential",
                recommended_palette="ocean-breeze",
                avoids_monotony="避免画十余个并排柱/箱导致的横向压缩与标签重叠",
                code_snippet='sp.plot_ridgeline(groups, labels=group_names, show_median=True, palette="ocean-breeze")',
            ))
        recs.append(ChartRecommendation(
            chart_type="小提琴图 + 内嵌 IQR 胶囊 (+ 散点)",
            sciplot_func="plot_violin",
            score=90,
            why_fit="对称密度轮廓清晰对比各组概率质量分布，内嵌深色 IQR 胶囊与白点中位数提供精确分位读数",
            visual_channels="琴宽编码密度 + 内嵌箱须精确数值 + 可选原始点",
            palette_type="categorical",
            recommended_palette="olive-apricot",
            avoids_monotony="升级传统单薄箱线图，避免隐藏双峰或长尾特征",
            code_snippet='sp.plot_violin(groups, labels=group_names, show_box=True, show_points=True, palette="olive-apricot")',
        ))
        if per_group_n <= 40:
            recs.append(ChartRecommendation(
                chart_type="蜂群分布图 / 带点箱线图 (Beeswarm / Box+Points)",
                sciplot_func="plot_beeswarm" if per_group_n <= 35 else "plot_box",
                score=87,
                why_fit=f"中小样本（每组~{per_group_n}点）下直接展示非重叠离散样本，真实透明度最高",
                visual_channels="精确数据位置 + 防重叠水平展开",
                palette_type="categorical",
                recommended_palette="blue-sky",
                avoids_monotony="让审稿人直接看到真实样本量，避免误差棒柱图隐藏样本稀疏与偏离",
                code_snippet='sp.plot_beeswarm(groups, labels=group_names, show_median=True, palette="blue-sky")',
            ))
        if k_groups == 2:
            recs.append(ChartRecommendation(
                chart_type="配对/前后对照图 (Paired Plot)",
                sciplot_func="plot_paired",
                score=86,
                why_fit="两组样本等长且可能存在对应关系时，可检验个体跃迁方向是否一致",
                visual_channels="斜率连线 + 均值差徽章",
                palette_type="categorical",
                recommended_palette="coral-teal",
                avoids_monotony="揭露整体均值平稳背后可能隐藏的个体剧烈分化",
                code_snippet="sp.plot_paired(groups[0], groups[1], labels=tuple(group_names[:2]))",
            ))

    # ── 分支 4：类别 × 聚合指标矩阵 / 排名 / 构成 ──
    if prof.shape_pattern == "category_scalar":
        n_cats = prof.n_rows
        n_metrics = len(num_profiles)
        has_neg = any(c.min is not None and c.min < 0 for c in num_profiles)
        if n_metrics == 1:
            single_col = num_profiles[0]
            if has_neg or goal == "comparison":
                if has_neg:
                    recs.append(ChartRecommendation(
                        chart_type="发散条形图 (Diverging Bar)",
                        sciplot_func="plot_diverging_bar",
                        score=95,
                        why_fit="单一指标同时存在正负方向差异（相对基准线增减），发散条可直观区分收益与退步项",
                        visual_channels="双向长度 + 零点基准对齐 + 正负对比双色",
                        palette_type="diverging",
                        recommended_palette="coral-teal",
                        avoids_monotony="优于单向柱状图，避免正负变化幅度被混在一起读",
                        code_snippet='sp.plot_diverging_bar(categories, values, threshold=0.0, show_values=True, palette="coral-teal")',
                    ))
            if goal in {"composition", "ranking"} or (single_col.is_positive_only and n_cats >= 4):
                recs.append(ChartRecommendation(
                    chart_type="帕累托贡献分析图 (Pareto Chart)",
                    sciplot_func="plot_pareto",
                    score=93 if goal in {"ranking", "composition"} else 88,
                    why_fit=f"{n_cats} 个非负贡献项降序排列并叠加累积占比曲线与 80% 参考线，快速锁定关键少数驱动因素",
                    visual_channels="降序柱高 + 次轴累积百分比拐点 + 重点/次要双层高亮",
                    palette_type="categorical",
                    recommended_palette="blue-sky",
                    avoids_monotony="比无序普通柱状图多提供累积贡献度与重点识别维度",
                    code_snippet='sp.plot_pareto(categories, values, palette="blue-sky")',
                ))
            if n_cats >= 5:
                recs.append(ChartRecommendation(
                    chart_type="排序棒棒糖图 (Lollipop Chart)",
                    sciplot_func="plot_lollipop",
                    score=92,
                    why_fit=f"类别较多（{n_cats} 项）做纯指标排名对比，棒棒糖图用极细垂线替代宽大色块，显著降低墨水-数据比",
                    visual_channels="圆点末端位置（最高感知精度）+ 高对比高亮单点",
                    palette_type="categorical",
                    recommended_palette="olive-apricot",
                    avoids_monotony="替代笨重的 10 柱竖柱图，彻底解决 X 轴标签斜挤问题",
                    code_snippet='sp.plot_lollipop(categories, values, sort=True, orientation="h", palette="olive-apricot")',
                ))
            if goal == "composition" and single_col.is_positive_only:
                recs.extend([
                    ChartRecommendation(
                        chart_type="华夫占比图 (Waffle Chart)",
                        sciplot_func="plot_waffle",
                        score=90,
                        why_fit="用 10×10 离散单元网格精确映射百分比构成，读者无需估算扇形角度即可直读整格比例",
                        visual_channels="整数单元计数 + 分区色块 + 精确百分比图例",
                        palette_type="categorical",
                        recommended_palette="olive-apricot",
                        avoids_monotony="替代传统难以比较相近角度的饼图",
                        code_snippet='sp.plot_waffle(categories, values, palette="olive-apricot")',
                    ),
                    ChartRecommendation(
                        chart_type="矩形树图 / 环形图 (Treemap / Donut)",
                        sciplot_func="plot_treemap" if n_cats >= 6 else "plot_donut",
                        score=84,
                        why_fit="层内占比直观，环形图中心可嵌入总计核心指标",
                        visual_channels="矩形面积/圆环弧段 + 扇区直标百分比",
                        palette_type="categorical",
                        recommended_palette="soft-forest",
                        avoids_monotony="杜绝 3D 饼图或超 7 片无标注饼图",
                        code_snippet='sp.plot_donut(categories, values, palette="soft-forest")' if n_cats < 6 else 'sp.plot_treemap(categories, values)',
                    ),
                ])
            recs.append(ChartRecommendation(
                chart_type="水平条形图 / 精简竖柱 (Horizontal Bar)",
                sciplot_func="plot_horizontal_bar" if n_cats > 5 else "plot_bar",
                score=80,
                why_fit="需要准确比较各离散项绝对高度且类别名称较长时，水平排序条兼顾可读性与精度",
                visual_channels="统一零基线长度 + 尾部直标数值",
                palette_type="categorical",
                recommended_palette="blue-sky",
                avoids_monotony="自动排序并开启 L 形极简框与横轴隐藏次刻度",
                code_snippet='sp.plot_horizontal_bar(categories, values, sort=True, show_values=True)' if n_cats > 5 else 'sp.plot_bar(categories, values, show_values=True)',
            ))
        else:
            # 多方法 × 多指标
            if n_metrics == 2:
                recs.append(ChartRecommendation(
                    chart_type="哑铃前后对比图 (Dumbbell Plot)",
                    sciplot_func="plot_dumbbell",
                    score=95,
                    why_fit=f"恰好 2 列对照数值跨 {n_cats} 个项目对比，哑铃图直接用线段长度和涨跌色编码净改变量",
                    visual_channels="空心起点 + 实心终点双编码 + 净增量直标",
                    palette_type="categorical",
                    recommended_palette="coral-teal",
                    avoids_monotony="比两色并排分组柱状图更容易一眼读出“每个项目谁增谁降、差多少”",
                    code_snippet='sp.plot_dumbbell(categories, before_vals, after_vals, show_values=True, palette="coral-teal")',
                ))
            if 3 <= n_metrics <= 7 and n_cats <= 5:
                recs.extend([
                    ChartRecommendation(
                        chart_type="多维能力雷达图 (Radar Chart)",
                        sciplot_func="plot_radar",
                        score=89,
                        why_fit=f"{n_cats} 个对象在 {n_metrics} 个指标上的综合性能画像，能快速判别全面领先型与偏科型方法",
                        visual_channels="多边形包络轮廓 + 柔和半透明填充",
                        palette_type="categorical",
                        recommended_palette="blue-sky",
                        avoids_monotony="突破二维柱状图的平坦排布，突出综合均衡性（需同步配合柱图或表格给精确数值）",
                        code_snippet='sp.plot_radar(metrics, methods_dict, palette="blue-sky")',
                    ),
                    ChartRecommendation(
                        chart_type="排名轨迹凹凸图 (Bump Chart)",
                        sciplot_func="plot_bump",
                        score=86,
                        why_fit="聚焦多方法在不同基准或任务之间的排名名次交叉与稳定度",
                        visual_channels="高亮焦点轨迹 + 末端直接标签",
                        palette_type="categorical",
                        recommended_palette="blue-sky",
                        avoids_monotony="多指标尺度不一时，排名演化比原始数值柱状图更具跨基准可比性",
                        code_snippet='sp.plot_bump(ranks_matrix, time_points=metrics, labels=categories)',
                    ),
                ])
            recs.append(ChartRecommendation(
                chart_type="气泡/数值热力矩阵 (Heatmap / Grouped Bar)",
                sciplot_func="plot_grouped_bar" if n_cats <= 5 and n_metrics <= 5 else "plot_heatmap",
                score=85,
                why_fit="多组×多指标需要直接读取精确值对比时的高精度选择",
                visual_channels="共享坐标长度 / 颜色矩阵 + 格内直标",
                palette_type="categorical" if n_cats <= 5 else "sequential",
                recommended_palette="olive-apricot",
                avoids_monotony="开启柔和深轮廓与去杂次刻度提升基础柱图的发表下限",
                code_snippet='sp.plot_grouped_bar(groups, data_dict, show_values=True, palette="olive-apricot")',
            ))

    # ── 分支 5：双变量连续关系 ──
    if prof.shape_pattern == "bivariate":
        n = prof.n_rows
        max_r = prof.corr_summary.get("max_abs_r", 0.0)
        if n >= 800:
            recs.append(ChartRecommendation(
                chart_type="六边形二维密度图 (Hexbin Density)",
                sciplot_func="plot_hexbin",
                score=96,
                why_fit=f"样本量高达 n={n}，普通散点会严重重叠糊成一团（Overplotting），Hexbin 以六边形格密度忠实揭示核心簇",
                visual_channels="空间位置 + 对数/线性密度色彩",
                palette_type="sequential",
                recommended_palette="viridis",
                avoids_monotony="彻底避免大样本散点图重叠掩盖核心密度梯度的常见错误",
                code_snippet='sp.plot_hexbin(x, y, bins="log", colorbar_label="样本密度")',
            ))
        else:
            recs.append(ChartRecommendation(
                chart_type="散点 + 边际联合分布图 (Marginal Scatter + Hist/KDE)",
                sciplot_func="plot_marginal",
                score=95,
                why_fit=f"中小样本（n={n}，|r|={max_r:.2f}）下同时展示二维联合相关性与各自单变量边缘分布形态",
                visual_channels="散点位置 + 顶部/右侧直方 KDE + 相关系数标注",
                palette_type="categorical",
                recommended_palette="blue-sky",
                avoids_monotony="满足“先看单变量分布再看变量间关系”的双重可视化准则",
                code_snippet='sp.plot_marginal(x, y, marginal="kde", show_corr=True, palette="blue-sky")',
            ))
        recs.append(ChartRecommendation(
            chart_type="线性拟合 + 95%置信带 + 统计摘要散点图",
            sciplot_func="plot_scatter",
            score=91,
            why_fit="直观检验线性趋势、异常离群点与残差分布齐性（Anscombe 检验）",
            visual_channels="带白边散点 + OLS 拟合线 + 95% 置信带 + 自动避让角标 (r, R², p, n)",
            palette_type="categorical",
            recommended_palette="coral-teal",
            avoids_monotony="相比纯裸散点增加不确定度置信带与量化统计摘要卡片",
            code_snippet='sp.plot_scatter(x, y, fit_line=True, ci=True, show_stats=True, palette="coral-teal")',
        ))

    # ── 分支 6：时间序列 / 有序过程 ──
    if prof.shape_pattern == "timeseries" or goal == "trend":
        n_series = len(num_profiles)
        if n_series >= 5:
            recs.append(ChartRecommendation(
                chart_type="分面小图 / 河流面积图 / 排名凹凸图",
                sciplot_func="plot_bump" if n_series <= 8 else "plot_streamgraph",
                score=94,
                why_fit=f"序列数达到 {n_series} 条，强行画在同一单折线图上会纠缠成无法辨认的“意面图 (Spaghetti Chart)”",
                visual_channels="高亮焦点轨迹或垂直堆叠流 + 分面坐标系隔离",
                palette_type="categorical",
                recommended_palette="ocean-breeze",
                avoids_monotony="显式规避“意面式多折线混乱”，或改用 `sp.paper_subplots(...)` 分面小图",
                code_snippet='sp.plot_streamgraph(x, ys, labels=series_names, palette="ocean-breeze")',
            ))
            composite_plan = "建议使用 `sp.paper_subplots(nrows, ncols, sharex=True, sharey=True)` 绘制共享标尺的分面小图（Small Multiples）替代拥挤折线。"
        else:
            recs.extend([
                ChartRecommendation(
                    chart_type="时间序列演化曲线 + 可选趋势/突变标注",
                    sciplot_func="plot_multi_timeseries" if n_series >= 2 else "plot_timeseries",
                    score=93,
                    why_fit="时序连续轴配合智能日期刻度与重点曲线突出，适合呈现动态响应、衰减与周期波动",
                    visual_channels="连续位置 + 线型色相双冗余 + 重点序列星标强化",
                    palette_type="categorical",
                    recommended_palette="blue-sky",
                    avoids_monotony="相比基础单折线支持冗余线型防色盲与末段高亮",
                    code_snippet='sp.plot_multi_timeseries(dates, y_list, labels=names, palette="blue-sky")',
                ),
                ChartRecommendation(
                    chart_type="概率预测扇形图 (Prediction Fan Chart)",
                    sciplot_func="plot_fan",
                    score=86,
                    why_fit="若拥有多条预测/仿真轨迹或分位数区间，扇形图通过 50%/80%/95% 嵌套渐深带完整展现未来不确定性展开",
                    visual_channels="中心路径 + 多级半透明分位数包络",
                    palette_type="categorical",
                    recommended_palette="coral-teal",
                    avoids_monotony="优于单一均值曲线（后者隐藏预测置信发散风险）",
                    code_snippet='sp.plot_fan(t_future, samples=ensemble_matrix, history_x=t_hist, history_y=y_hist)',
                ),
            ])

    # ── 分支 7：高维多变量表 ──
    if prof.shape_pattern == "multivariate" and len(num_profiles) >= 3:
        n_num = len(num_profiles)
        max_r = prof.corr_summary.get("max_abs_r", 0.0)
        recs.extend([
            ChartRecommendation(
                chart_type="增强散点矩阵 (下三角散点 + 对角KDE + 上三角相关性卡)",
                sciplot_func="plot_scatter_matrix",
                score=95 if n_num <= 7 else 85,
                why_fit=f"{n_num} 个连续特征两两组合（最大 |r|={max_r:.2f}），上三角色彩相关卡片 + 下三角散点 + 对角 KDE 一览全局结构",
                visual_channels="矩阵网格位置 + 色块相关系数 + 单变量分布形态",
                palette_type="diverging",
                recommended_palette="blue-sky",
                avoids_monotony="一图取代数十张散落双变量散点图，避免只挑相关性最高的一两对作局部汇报",
                code_snippet='sp.plot_scatter_matrix(X, columns=feat_names, upper="corr", diag="kde", color_by=groups)',
            ),
            ChartRecommendation(
                chart_type="PCA 降维聚类与 95% 置信椭圆图",
                sciplot_func="plot_pca",
                score=91 if n_num >= 4 else 82,
                why_fit="当特征维数 >= 4 时投影到 PC1/PC2 并绘制群落 95% 置信椭圆与方差解释率，直接揭示可分性与离群簇",
                visual_channels="降维位置 + 群落半透明置信椭圆 + 方差解释轴标",
                palette_type="categorical",
                recommended_palette="coral-teal",
                avoids_monotony="高维特征空间不能只靠几组单指标柱状图概括整体聚类格局",
                code_snippet='sp.plot_pca(X, labels=group_labels, show_ellipse=True, palette="coral-teal")',
            ),
            ChartRecommendation(
                chart_type="平行坐标多维剖面图 (Parallel Coordinates)",
                sciplot_func="plot_parallel",
                score=86,
                why_fit="保留全部高维特征轴并行排序，擅长捕捉不同类别在多个归一化维度上的交互权衡与异常轨迹",
                visual_channels="多纵轴归一化位置 + 分类色相轨迹束",
                palette_type="categorical",
                recommended_palette="olive-apricot",
                avoids_monotony="比静态多雷达子图更精准定位不同特征轴之间的负相关交叉模式",
                code_snippet='sp.plot_parallel(X, columns=feat_names, color_by=group_col, normalize="minmax")',
            ),
            ChartRecommendation(
                chart_type="特征相关下三角热力图 (Correlation Heatmap)",
                sciplot_func="plot_heatmap",
                score=84,
                why_fit="提炼特征间共线性与冗余模块，辅助回归共线性诊断与特征筛选",
                visual_channels="下三角双色阶 + 显著性星号",
                palette_type="diverging",
                recommended_palette="rdbu",
                avoids_monotony="精简上三角镜像噪音，直达共线性核心",
                code_snippet='sp.plot_heatmap(np.corrcoef(X.T), row_labels=feat_names, col_labels=feat_names, cmap="RdBu_r", triangle="lower", show_values=True)',
            ),
        ])
        if composite_plan is None:
            composite_plan = (
                "多维数据推荐采用不对称 Hero 叙事版式 `sp.hero_layout('hero_right')`："
                "主面板放核心降维/模型对比（`plot_pca` 或 `plot_parallel`），"
                "双卫星面板分别放特征相关下三角热力图（`plot_heatmap(..., triangle='lower')`）与关键指标云雨分布（`plot_raincloud`）。"
            )

    # 目标偏好二次加权 & 按函数去重截断
    goal_boost: Dict[str, Tuple[str, ...]] = {
        "distribution": ("plot_raincloud", "plot_ridgeline", "plot_violin", "plot_histogram", "plot_beeswarm", "plot_qq"),
        "relationship": ("plot_marginal", "plot_hexbin", "plot_scatter", "plot_scatter_matrix", "plot_heatmap"),
        "comparison": ("plot_raincloud", "plot_dumbbell", "plot_paired", "plot_diverging_bar", "plot_grouped_bar", "plot_radar"),
        "composition": ("plot_waffle", "plot_pareto", "plot_treemap", "plot_donut", "plot_stacked_bar", "plot_sankey"),
        "ranking": ("plot_pareto", "plot_lollipop", "plot_bump", "plot_horizontal_bar"),
        "trend": ("plot_fan", "plot_multi_timeseries", "plot_timeseries", "plot_streamgraph", "plot_bump"),
        "multivariate": ("plot_scatter_matrix", "plot_pca", "plot_parallel", "plot_heatmap", "plot_radar"),
        "evaluation": ("plot_roc", "plot_calibration", "plot_confusion_matrix", "plot_residuals"),
    }
    preferred = goal_boost.get(goal, ())
    for r in recs:
        if r.sciplot_func in preferred:
            r.score = min(99.0, r.score + 6.0)

    deduped: Dict[str, ChartRecommendation] = {}
    for rec in sorted(recs, key=lambda item: item.score, reverse=True):
        if rec.sciplot_func not in deduped:
            deduped[rec.sciplot_func] = rec

    final_recs = list(deduped.values())[: max(1, top_k)]
    return ChartRecommendationReport(
        profile=prof,
        goal=goal,
        recommendations=final_recs,
        composite_plan=composite_plan,
    )


__all__ = [
    "ColumnProfile",
    "DataProfile",
    "ChartRecommendation",
    "ChartRecommendationReport",
    "profile_data",
    "recommend_charts",
]
