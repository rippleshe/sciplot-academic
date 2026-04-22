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
from typing import Any, List, Optional, Tuple

from sciplot._core.result import PlotResult
from sciplot._core.utils import apply_resolved_style
from sciplot._core.layout import new_figure


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
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: Any,
) -> PlotResult:
    """
    PCA 降维可视化（2D）

    参数:
        data        : 原始特征矩阵 (n_samples, n_features)
        labels      : 类别标签数组，有则按类着色
        n_components: 降维维度，目前仅支持 2
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

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

    pca = PCA(n_components=n_components)
    proj = pca.fit_transform(data)
    var = pca.explained_variance_ratio_

    if labels is not None:
        unique_labels = np.unique(labels)
        for label in unique_labels:
            mask = labels == label
            ax.scatter(proj[mask, 0], proj[mask, 1], label=str(label), **kwargs)
        ax.legend()
    else:
        ax.scatter(proj[:, 0], proj[:, 1], **kwargs)

    ax.set_xlabel(f"PC1 ({var[0]*100:.1f}%)")
    if len(var) >= 2:
        ax.set_ylabel(f"PC2 ({var[1]*100:.1f}%)")
    else:
        ax.set_ylabel("PC2")
    ax.tick_params(direction="in")
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

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

    cm = confusion_matrix(y_true, y_pred)
    if normalize:
        row_sums = cm.sum(axis=1, keepdims=True)
        row_sums = np.where(row_sums == 0, 1, row_sums)
        cm = cm.astype("float") / row_sums

    im = ax.imshow(cm, interpolation="nearest", cmap=cmap)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    if labels is not None:
        ticks = np.arange(len(labels))
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_yticklabels(labels)

    fmt = ".2f" if normalize else "d"
    thresh = cm.max() / 2.0
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        ax.text(j, i, format(cm[i, j], fmt),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black")

    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


def plot_feature_importance(
    features: List[str],
    importance: np.ndarray,
    title: str = "Feature Importance",
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

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

    # 优化排序逻辑：直接取最大的 top_n 个，然后升序排列（水平条形图从下到上）
    if top_n is not None and top_n < len(features):
        # 取重要性最高的 top_n 个索引
        indices = np.argsort(importance)[-top_n:]
    else:
        # 全部数据，按重要性排序
        indices = np.argsort(importance)

    sorted_features = [features[i] for i in indices]
    sorted_importance = importance[indices]

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]
    ax.barh(range(len(indices)), sorted_importance, color=colors[0], **kwargs)
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels(sorted_features)
    ax.set_xlabel("Importance")
    ax.set_title(title)
    ax.tick_params(direction="in")
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

    effective_venue = apply_resolved_style(venue, palette, lang)
    fig, ax = new_figure(effective_venue)

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
    ax.tick_params(direction="in")
    return PlotResult(fig, ax, metadata={"venue": venue, "palette": palette})


__all__ = [
    "plot_pca",
    "plot_confusion_matrix",
    "plot_feature_importance",
    "plot_learning_curve",
]
