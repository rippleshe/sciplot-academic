"""
机器学习可视化扩展

用于绘制 PCA、混淆矩阵、特征重要性、学习曲线等。
需要额外安装：uv add sciplot-academic[ml] 或 pip install sciplot-academic[ml]
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from typing import Any, List, Optional, Sequence, Tuple

from sciplot._core.layout import add_colorbar
from sciplot._core.result import PlotResult
from sciplot._core.utils import get_cycle_colors, new_styled_figure
from sciplot.utils.smart import auto_rotate_labels


def _check_sklearn() -> Tuple[Any, Any]:
    """
    检查 sklearn 是否可用
    
    返回:
        (PCA, confusion_matrix) 模块对象
    
    抛出:
        ImportError: 未安装 scikit-learn 时
    """
    try:
        from sklearn.decomposition import PCA
        from sklearn.metrics import confusion_matrix
        return PCA, confusion_matrix
    except ImportError as e:
        raise ImportError(
            "机器学习功能需要安装 scikit-learn。\n"
            "请运行: uv add scikit-learn 或 pip install scikit-learn\n"
            "或安装完整扩展: uv add sciplot-academic[ml]"
        ) from e


def plot_pca(
    data: np.ndarray,
    labels: Optional[np.ndarray] = None,
    n_components: int = 2,
    show_ellipse: bool = True,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    PCA 降维可视化（2D，自动标注方差解释率并支持 95% 置信椭圆与类别中心）

    参数:
        data        : 原始特征矩阵 (n_samples, n_features)
        labels      : 类别标签数组，有则按类着色
        n_components: 降维维度，目前仅支持 2
        show_ellipse: 有分类标签且单类样本 >= 4 时是否绘制 95% 置信椭圆，默认 True
        venue       : 期刊样式，如 "nature", "ieee"
        palette     : 配色方案，如 "pastel", "earth"
        lang        : 语言设置

    返回:
        PlotResult: 包含 fig 和 ax 的绘图结果对象

    抛出:
        ImportError: 未安装 scikit-learn 时
        ValueError: n_components 不为 2 时

    示例:
        >>> from sciplot._ext.ml import plot_pca
        >>> result = plot_pca(X, labels=y, venue="nature")
        >>> result.save("pca")
    """
    from matplotlib.patches import Ellipse
    from sciplot.utils.guards import polish_axis

    data = np.asarray(data)
    if data.ndim != 2:
        raise ValueError(f"data 必须是二维数组，当前维度: {data.ndim}")

    n_samples, n_features = data.shape
    if n_samples < n_components:
        raise ValueError(
            f"样本数不足，至少需要 {n_components} 个样本，实际: {n_samples}"
        )
    if n_features < n_components:
        raise ValueError(
            f"特征数不足，至少需要 {n_components} 个特征，实际: {n_features}"
        )

    if labels is not None and len(labels) != n_samples:
        raise ValueError(
            f"labels 长度 ({len(labels)}) 与样本数 ({n_samples}) 不一致"
        )

    if n_components != 2:
        raise ValueError(f"n_components 目前仅支持 2，实际值: {n_components}")

    PCA, _ = _check_sklearn()

    fig, ax = new_styled_figure(venue, palette, lang)

    pca = PCA(n_components=n_components)
    proj = pca.fit_transform(data)
    var = pca.explained_variance_ratio_
    scatter_kwargs = dict(kwargs)
    scatter_kwargs.setdefault("s", 28)
    scatter_kwargs.setdefault("alpha", 0.80)
    scatter_kwargs.setdefault("edgecolors", "white")
    scatter_kwargs.setdefault("linewidths", 0.45)

    ax.axhline(0.0, color="#CBD5E1", linestyle=":", linewidth=0.8, zorder=0)
    ax.axvline(0.0, color="#CBD5E1", linestyle=":", linewidth=0.8, zorder=0)

    if labels is not None:
        unique_labels = np.unique(labels)
        colors = get_cycle_colors()
        explicit_color = scatter_kwargs.pop("color", scatter_kwargs.pop("c", None))
        for idx, label in enumerate(unique_labels):
            mask = labels == label
            c = explicit_color if explicit_color is not None else colors[idx % len(colors)]
            pts_c = proj[mask]
            ax.scatter(
                pts_c[:, 0], pts_c[:, 1],
                color=c, label=str(label), zorder=3, **scatter_kwargs
            )
            if show_ellipse and pts_c.shape[0] >= 4:
                cov = np.cov(pts_c[:, 0], pts_c[:, 1])
                if np.all(np.isfinite(cov)):
                    vals, vecs = np.linalg.eigh(cov)
                    if np.all(vals > 1e-12):
                        order = vals.argsort()[::-1]
                        vals, vecs = vals[order], vecs[:, order]
                        theta = float(np.degrees(np.arctan2(*vecs[:, 0][::-1])))
                        # 2D 95% chi-square quantile sqrt(5.991) ≈ 2.4477
                        w, h = 2.0 * 2.4477 * np.sqrt(vals)
                        ell = Ellipse(
                            xy=(float(np.mean(pts_c[:, 0])), float(np.mean(pts_c[:, 1]))),
                            width=float(w), height=float(h), angle=theta,
                            facecolor=c, alpha=0.10, edgecolor=c,
                            linestyle="--", linewidth=1.0, zorder=2,
                        )
                        ax.add_patch(ell)
        from sciplot.utils.smart import smart_legend

        smart_legend(ax)
    else:
        ax.scatter(proj[:, 0], proj[:, 1], zorder=3, **scatter_kwargs)

    polish_axis(ax, clean_spines=True, grid="both", grid_alpha=0.18)
    ax.set_xlabel(f"PC1 ({var[0]*100:.1f}%)")
    if len(var) >= 2:
        ax.set_ylabel(f"PC2 ({var[1]*100:.1f}%)")
    else:
        ax.set_ylabel("PC2")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List[str]] = None,
    normalize: bool = False,
    cmap: str = "Blues",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    混淆矩阵可视化

    参数:
        y_true   : 真实标签
        y_pred   : 预测标签
        labels   : 类别名称列表
        normalize: True 则按真实类别归一化（显示比例而非计数）
        cmap     : 颜色映射
        venue    : 期刊样式
        palette  : 配色方案
        lang     : 语言设置

    返回:
        PlotResult: 包含 fig 和 ax 的绘图结果对象

    抛出:
        ImportError: 未安装 scikit-learn 时

    示例:
        >>> from sciplot._ext.ml import plot_confusion_matrix
        >>> result = plot_confusion_matrix(y_test, y_pred,
        ...     labels=class_names, normalize=True, venue="ieee")
        >>> result.save("confusion_matrix", formats=("pdf",))
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    if y_true.ndim != 1 or y_pred.ndim != 1:
        raise ValueError("y_true 和 y_pred 必须是一维数组")
    if len(y_true) != len(y_pred):
        raise ValueError(
            f"y_true 长度 ({len(y_true)}) 与 y_pred 长度 ({len(y_pred)}) 不一致"
        )
    if len(y_true) == 0:
        raise ValueError("y_true 和 y_pred 不能为空")

    import itertools
    _, confusion_matrix = _check_sklearn()

    fig, ax = new_styled_figure(venue, palette, lang)

    cm = confusion_matrix(y_true, y_pred)
    if normalize:
        row_sums = cm.sum(axis=1, keepdims=True)
        row_sums = np.where(row_sums == 0, 1, row_sums)
        cm = cm.astype("float") / row_sums

    im = ax.imshow(cm, interpolation="nearest", cmap=cmap)
    add_colorbar(fig, im, ax=ax)

    if labels is not None:
        ticks = np.arange(len(labels))
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xticklabels(labels)
        ax.set_yticklabels(labels)
        auto_rotate_labels(ax, axis="x")

    fmt = ".2f" if normalize else "d"
    thresh = cm.max() / 2.0
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        ax.text(j, i, format(cm[i, j], fmt),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black")

    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_feature_importance(
    features: List[str],
    importance: np.ndarray,
    title: str = "",
    top_n: Optional[int] = None,
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    特征重要性可视化（水平条形图，按重要性降序排列）

    参数:
        features  : 特征名列表
        importance: 对应的重要性分数数组
        title     : 图表标题
        top_n     : 只显示前 N 个最重要特征；None 则显示全部
        venue     : 期刊样式
        palette   : 配色方案
        lang      : 语言设置

    返回:
        PlotResult: 包含 fig 和 ax 的绘图结果对象

    示例:
        >>> from sciplot._ext.ml import plot_feature_importance
        >>> importances = model.feature_importances_
        >>> result = plot_feature_importance(feat_names, importances, top_n=15)
        >>> result.save("feature_importance", formats=("pdf",))
    """
    importance = np.asarray(importance)
    if importance.ndim != 1:
        raise ValueError("importance 必须是一维数组")
    if len(features) != len(importance):
        raise ValueError(
            f"features 长度 ({len(features)}) 与 importance 长度 ({len(importance)}) 不一致"
        )
    if len(features) == 0:
        raise ValueError("features 不能为空")
    if top_n is not None and top_n <= 0:
        raise ValueError(f"top_n 必须为正整数，实际值: {top_n}")

    fig, ax = new_styled_figure(venue, palette, lang)

    # 优化排序逻辑：直接取最大的 top_n 个，然后升序排列（水平条形图从下到上）
    if top_n is not None and top_n < len(features):
        # 取重要性最高的 top_n 个索引
        indices = np.argsort(importance)[-top_n:]
    else:
        # 全部数据，按重要性排序
        indices = np.argsort(importance)

    sorted_features = [features[i] for i in indices]
    sorted_importance = importance[indices]

    colors = get_cycle_colors()
    ax.barh(range(len(indices)), sorted_importance, color=colors[0], **kwargs)
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels(sorted_features)
    ax.set_xlabel("Importance")
    ax.set_title(title)
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_learning_curve(
    train_scores: np.ndarray,
    val_scores: np.ndarray,
    train_sizes: Optional[np.ndarray] = None,
    xlabel: str = "Training Examples",
    ylabel: str = "Score",
    label_train: str = "Training",
    label_val: str = "Validation",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    学习曲线可视化（训练集 vs 验证集得分随样本量变化）

    参数:
        train_scores: 训练集得分数组
        val_scores  : 验证集得分数组
        train_sizes : 训练样本数量数组
        xlabel      : X 轴标签
        ylabel      : Y 轴标签
        label_train : 训练集图例标签
        label_val   : 验证集图例标签
        venue       : 期刊样式
        palette     : 配色方案
        lang        : 语言设置

    返回:
        PlotResult: 包含 fig 和 ax 的绘图结果对象

    示例:
        >>> from sciplot._ext.ml import plot_learning_curve
        >>> from sklearn.model_selection import learning_curve
        >>> sizes, tr, va = learning_curve(clf, X, y, cv=5)
        >>> result = plot_learning_curve(tr.mean(1), va.mean(1), sizes)
        >>> result.save("learning_curve")
    """
    train_scores = np.asarray(train_scores)
    val_scores = np.asarray(val_scores)
    if train_scores.ndim != 1 or val_scores.ndim != 1:
        raise ValueError("train_scores 和 val_scores 必须是一维数组")
    if len(train_scores) != len(val_scores):
        raise ValueError(
            f"train_scores 长度 ({len(train_scores)}) 与 val_scores 长度 ({len(val_scores)}) 不一致"
        )
    if len(train_scores) == 0:
        raise ValueError("train_scores 和 val_scores 不能为空")

    fig, ax = new_styled_figure(venue, palette, lang)

    if train_sizes is None:
        train_sizes = np.arange(1, len(train_scores) + 1)
    else:
        train_sizes = np.asarray(train_sizes)
        if train_sizes.ndim != 1:
            raise ValueError("train_sizes 必须是一维数组")
        if len(train_sizes) != len(train_scores):
            raise ValueError(
                f"train_sizes 长度 ({len(train_sizes)}) 与 scores 长度 ({len(train_scores)}) 不一致"
            )

    ax.plot(train_sizes, train_scores, label=label_train, marker="o", **kwargs)
    ax.plot(train_sizes, val_scores, label=label_val, marker="s", **kwargs)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def _binary_roc_pr_arrays(y_true: np.ndarray, y_score: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, float]:
    """纯 NumPy 计算二分类 ROC（FPR, TPR）与 PR（Recall, Precision）曲线及 AUC/AP。"""
    order = np.argsort(y_score)[::-1]
    y_sorted = y_true[order]
    n_pos = int(np.sum(y_true == 1))
    n_neg = int(np.sum(y_true == 0))
    if n_pos == 0 or n_neg == 0:
        raise ValueError("y_true 必须同时包含正例(1)与负例(0)")

    tp = np.cumsum(y_sorted == 1).astype(float)
    fp = np.cumsum(y_sorted == 0).astype(float)
    tpr = np.r_[0.0, tp / n_pos]
    fpr = np.r_[0.0, fp / n_neg]
    try:
        auc_roc = float(np.trapezoid(tpr, fpr))
    except AttributeError:
        auc_roc = float(np.trapz(tpr, fpr))  # type: ignore[attr-defined]

    precision = tp / np.maximum(tp + fp, 1.0)
    recall = tp / n_pos
    rec_curve = np.r_[0.0, recall]
    prec_curve = np.r_[1.0, precision]
    ap = float(np.sum((rec_curve[1:] - rec_curve[:-1]) * precision))
    return fpr, tpr, rec_curve, prec_curve, auc_roc, ap


def plot_roc(
    y_true: Sequence[int],
    scores: Any,
    *,
    mode: str = "roc",
    show_threshold: bool = True,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    title: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """绘制 ROC 或 Precision-Recall 分类模型对比曲线（自动标注 AUC/AP 与最优约登阈值）。

    参数:
        y_true        : 二分类真实标签 (0/1)
        scores        : 一维预测概率/分数数组，或 ``{模型名: 预测分数}`` 字典
        mode          : ``"roc"``（默认）或 ``"pr"``（Precision-Recall 曲线）
        show_threshold: ROC 模式下是否用空心白圈标注最大约登指数 (TPR-FPR) 最优点
    """
    from sciplot.utils.guards import polish_axis
    from sciplot.utils.smart import smart_legend

    y_arr = np.asarray(y_true, dtype=int).ravel()
    if y_arr.size == 0 or not np.all(np.isin(y_arr, (0, 1))):
        raise ValueError("y_true 必须为非空 0/1 二分类标签数组")
    if mode not in {"roc", "pr"}:
        raise ValueError(f"mode 仅支持 'roc' 或 'pr'，实际值: {mode!r}")

    if isinstance(scores, dict):
        if not scores:
            raise ValueError("scores 字典不能为空")
        score_map = {str(k): np.asarray(v, dtype=float).ravel() for k, v in scores.items()}
    else:
        score_map = {"Model": np.asarray(scores, dtype=float).ravel()}

    for name, s_arr in score_map.items():
        if len(s_arr) != len(y_arr):
            raise ValueError(f"scores['{name}'] 长度 ({len(s_arr)}) 与 y_true ({len(y_arr)}) 不一致")
        if not np.all(np.isfinite(s_arr)):
            raise ValueError(f"scores['{name}'] 不能包含 NaN 或 Inf")

    fig, ax = new_styled_figure(venue, palette, lang)
    colors = get_cycle_colors()

    for idx, (name, s_arr) in enumerate(score_map.items()):
        fpr, tpr, rec, prec, auc_roc, ap = _binary_roc_pr_arrays(y_arr, s_arr)
        c = colors[idx % len(colors)]
        if mode == "roc":
            ax.plot(fpr, tpr, color=c, linewidth=1.8,
                    label=f"{name} (AUC = {auc_roc:.3f})", zorder=3, **kwargs)
            if show_threshold and fpr.size > 2:
                best_j = int(np.argmax(tpr - fpr))
                ax.scatter([fpr[best_j]], [tpr[best_j]], s=42, color=c,
                           edgecolors="white", linewidths=1.1, zorder=5)
        else:
            ax.plot(rec, prec, color=c, linewidth=1.8,
                    label=f"{name} (AP = {ap:.3f})", zorder=3, **kwargs)

    if mode == "roc":
        ax.plot([0, 1], [0, 1], color="#94A3B8", linestyle="--", linewidth=1.0,
                label="Random (0.500)", zorder=1)
        ax.set_xlabel(xlabel or "False Positive Rate")
        ax.set_ylabel(ylabel or "True Positive Rate")
    else:
        baseline = float(np.mean(y_arr == 1))
        ax.axhline(baseline, color="#94A3B8", linestyle="--", linewidth=1.0,
                   label=f"Baseline ({baseline:.2f})", zorder=1)
        ax.set_xlabel(xlabel or "Recall")
        ax.set_ylabel(ylabel or "Precision")

    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.04)
    polish_axis(ax, clean_spines=True, grid="both", grid_alpha=0.22)
    if title:
        ax.set_title(title)
    smart_legend(ax, loc="lower right" if mode == "roc" else "lower left")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_calibration(
    y_true: Sequence[int],
    probs: Any,
    *,
    n_bins: int = 10,
    show_hist: bool = True,
    xlabel: str = "预测概率均值",
    ylabel: str = "实测正例频率",
    title: str = "",
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
) -> PlotResult:
    """绘制概率校准曲线（可靠性图 + ECE/Brier 指标 + 可选底部预测分布直方条）。"""
    from sciplot.utils.guards import polish_axis
    from sciplot.utils.smart import smart_legend

    y_arr = np.asarray(y_true, dtype=int).ravel()
    if y_arr.size == 0 or not np.all(np.isin(y_arr, (0, 1))):
        raise ValueError("y_true 必须为非空 0/1 二分类数组")
    if n_bins < 2:
        raise ValueError("n_bins 必须 >= 2")

    if isinstance(probs, dict):
        if not probs:
            raise ValueError("probs 字典不能为空")
        prob_map = {str(k): np.asarray(v, dtype=float).ravel() for k, v in probs.items()}
    else:
        prob_map = {"Model": np.asarray(probs, dtype=float).ravel()}

    for name, p_arr in prob_map.items():
        if len(p_arr) != len(y_arr):
            raise ValueError(f"probs['{name}'] 长度与 y_true 不一致")
        if np.any(p_arr < 0.0) or np.any(p_arr > 1.0) or not np.all(np.isfinite(p_arr)):
            raise ValueError(f"probs['{name}'] 必须位于 [0, 1] 区间内")

    fig, ax = new_styled_figure(venue, palette, lang)
    colors = get_cycle_colors()
    edges = np.linspace(0.0, 1.0, n_bins + 1)

    ax.plot([0, 1], [0, 1], color="#64748B", linestyle="--", linewidth=1.0,
            label="理想校准 (Ideal)", zorder=1)

    for idx, (name, p_arr) in enumerate(prob_map.items()):
        c = colors[idx % len(colors)]
        mean_pred, frac_pos, ece = [], [], 0.0
        for b in range(n_bins):
            if b < n_bins - 1:
                mask = (p_arr >= edges[b]) & (p_arr < edges[b + 1])
            else:
                mask = (p_arr >= edges[b]) & (p_arr <= edges[b + 1])
            cnt = int(np.sum(mask))
            if cnt > 0:
                mp = float(np.mean(p_arr[mask]))
                fp = float(np.mean(y_arr[mask]))
                mean_pred.append(mp)
                frac_pos.append(fp)
                ece += (cnt / y_arr.size) * abs(mp - fp)
        brier = float(np.mean((p_arr - y_arr) ** 2))
        ax.plot(
            mean_pred, frac_pos, marker="o", markersize=4.5,
            color=c, linewidth=1.7,
            label=f"{name} (ECE={ece:.3f}, Brier={brier:.3f})", zorder=3,
        )
        if show_hist:
            hist_vals, _ = np.histogram(p_arr, bins=edges)
            max_h = max(int(hist_vals.max()), 1)
            norm_h = hist_vals / max_h * 0.14
            ax.bar(
                edges[:-1], norm_h, width=1.0 / n_bins, align="edge",
                color=c, alpha=0.14, edgecolor=c, linewidth=0.5, zorder=1,
            )

    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.04)
    polish_axis(ax, clean_spines=True, grid="both", grid_alpha=0.22)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    smart_legend(ax, loc="upper left")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = [
    "plot_pca",
    "plot_confusion_matrix",
    "plot_feature_importance",
    "plot_learning_curve",
    "plot_roc",
    "plot_calibration",
]
