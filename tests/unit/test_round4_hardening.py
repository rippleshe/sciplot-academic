"""
Round-4 hardening tests for ML extension validations and compatibility edges.
"""

from __future__ import annotations

import numpy as np
import pytest

from sciplot._ext.ml import (
    plot_confusion_matrix,
    plot_feature_importance,
    plot_learning_curve,
    plot_pca,
)


class TestMLHardening:
    def test_plot_confusion_matrix_validates_length_before_dependency(self):
        with pytest.raises(ValueError):
            plot_confusion_matrix(np.array([0, 1, 1]), np.array([0, 1]))

    def test_plot_pca_validates_label_length_before_dependency(self):
        data = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        with pytest.raises(ValueError):
            plot_pca(data, labels=np.array([0, 1]))

    def test_plot_feature_importance_validates_length(self, cleanup_figures):
        with pytest.raises(ValueError):
            plot_feature_importance(["a", "b"], np.array([0.2]))

    def test_plot_feature_importance_validates_top_n(self, cleanup_figures):
        with pytest.raises(ValueError):
            plot_feature_importance(["a"], np.array([0.2]), top_n=0)

    def test_plot_learning_curve_validates_score_lengths(self, cleanup_figures):
        with pytest.raises(ValueError):
            plot_learning_curve(np.array([0.8, 0.85]), np.array([0.7]))

    def test_plot_learning_curve_validates_train_sizes_lengths(self, cleanup_figures):
        with pytest.raises(ValueError):
            plot_learning_curve(
                np.array([0.8, 0.85]),
                np.array([0.7, 0.75]),
                train_sizes=np.array([10]),
            )
