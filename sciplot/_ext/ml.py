"""
机器学习可视化扩展

用于绘制 PCA、混淆矩阵、特征重要性、学习曲线等。
需要额外安装：pip install sciplot-academic[ml]
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from typing import Any, List, Optional, Tuple


def plot_pca(
    data: np.ndarray,
    labels: Optional[np.ndarray] = None,
    n_components: int = 2,
    venue: str = "nature",
    palette: str = "pastel",
    **kwargs: Any,
) -> Tuple[Figure, Axes]:
    """
    PCA 降维可视化（2D）

    参数:
        data        : 原始特征矩阵 (n_samples, n_features)
        labels      : 类别标签数组，有则按类着色
        n_components: 降维维度，目前支持 2

    示例:
        >>> from sciplot._ext.ml import plot_pca
        >>> fig, ax = plot_pca(X, labels=y, venue="nature")
        >>> sp.save(fig, "pca")
    """
    from sklearn.decomposition import PCA
    from sciplot._core.style import setup_style
    from sciplot._core.layout import new_figure

    setup_style(venue, palette)
    fig, ax = new_figure(venue)

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
    ax.set_ylabel(f"PC2 ({var[1]*100:.1f}%)")
    ax.tick_params(direction="in")
    return fig, ax


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List[str]] = None,
    normalize: bool = False,
    cmap: str = "Blues",
    venue: str = "nature",
    **kwargs: Any,
) -> Tuple[Figure, Axes]:
    """
    混淆矩阵可视化

    参数:
        normalize: True 则按真实类别归一化（显示比例而非计数）

    示例:
        >>> from sciplot._ext.ml import plot_confusion_matrix
        >>> fig, ax = plot_confusion_matrix(y_test, y_pred,
        ...     labels=class_names, normalize=True, venue="ieee")
        >>> sp.save(fig, "confusion_matrix", formats=("pdf",))
    """
    import itertools
    from sklearn.metrics import confusion_matrix
    from sciplot._core.style import setup_style
    from sciplot._core.layout import new_figure

    setup_style(venue)
    fig, ax = new_figure(venue)

    cm = confusion_matrix(y_true, y_pred)
    if normalize:
        cm = cm.astype("float") / cm.sum(axis=1, keepdims=True)

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
    return fig, ax


def plot_feature_importance(
    features: List[str],
    importance: np.ndarray,
    title: str = "Feature Importance",
    top_n: Optional[int] = None,
    venue: str = "nature",
    palette: str = "pastel",
    **kwargs: Any,
) -> Tuple[Figure, Axes]:
    """
    特征重要性可视化（水平条形图，按重要性降序排列）

    参数:
        features  : 特征名列表
        importance: 对应的重要性分数数组
        top_n     : 只显示前 N 个最重要特征；None 则显示全部

    示例:
        >>> from sciplot._ext.ml import plot_feature_importance
        >>> importances = model.feature_importances_
        >>> fig, ax = plot_feature_importance(feat_names, importances, top_n=15)
        >>> sp.save(fig, "feature_importance", formats=("pdf",))
    """
    from sciplot._core.style import setup_style
    from sciplot._core.layout import new_figure

    setup_style(venue, palette)
    fig, ax = new_figure(venue)

    # 排序
    indices = np.argsort(importance)[::-1]
    if top_n is not None:
        indices = indices[:top_n]
    # 倒转使最重要的在上方
    indices = indices[::-1]

    sorted_features = [features[i] for i in indices]
    sorted_importance = importance[indices]

    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]
    ax.barh(range(len(indices)), sorted_importance, color=colors[0], **kwargs)
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels(sorted_features)
    ax.set_xlabel("Importance")
    ax.set_title(title)
    ax.tick_params(direction="in")
    return fig, ax


def plot_learning_curve(
    train_scores: np.ndarray,
    val_scores: np.ndarray,
    train_sizes: Optional[np.ndarray] = None,
    xlabel: str = "Training Examples",
    ylabel: str = "Score",
    label_train: str = "Training",
    label_val: str = "Validation",
    venue: str = "nature",
    palette: str = "pastel-2",
    **kwargs: Any,
) -> Tuple[Figure, Axes]:
    """
    学习曲线可视化（训练集 vs 验证集得分随样本量变化）

    示例:
        >>> from sciplot._ext.ml import plot_learning_curve
        >>> from sklearn.model_selection import learning_curve
        >>> sizes, tr, va = learning_curve(clf, X, y, cv=5)
        >>> fig, ax = plot_learning_curve(tr.mean(1), va.mean(1), sizes)
        >>> sp.save(fig, "learning_curve")
    """
    from sciplot._core.style import setup_style
    from sciplot._core.layout import new_figure

    setup_style(venue, palette)
    fig, ax = new_figure(venue)

    if train_sizes is None:
        train_sizes = np.arange(1, len(train_scores) + 1)

    ax.plot(train_sizes, train_scores, label=label_train, marker="o", **kwargs)
    ax.plot(train_sizes, val_scores, label=label_val, marker="s", **kwargs)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.tick_params(direction="in")
    return fig, ax
