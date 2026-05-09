"""ML 扩展测试 — plot_pca, plot_confusion_matrix, plot_feature_importance, plot_learning_curve"""
import pytest
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sciplot as sp

try:
    from sklearn.decomposition import PCA
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

pytestmark = pytest.mark.skipif(not HAS_SKLEARN, reason="scikit-learn not installed")


@pytest.fixture(autouse=True)
def cleanup():
    yield
    plt.close("all")
    sp.reset_style()


@pytest.fixture
def classification_data():
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.array([0] * 50 + [1] * 50)
    return X, y


@pytest.fixture
def confusion_data():
    np.random.seed(42)
    y_true = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])
    y_pred = np.array([0, 0, 1, 1, 1, 0, 2, 2, 1])
    return y_true, y_pred


class TestPlotPca:
    def test_basic(self, classification_data):
        X, y = classification_data
        result = sp.plot_pca(X, labels=y)
        assert isinstance(result, sp.PlotResult)
        assert result.fig is not None

    def test_without_labels(self, classification_data):
        X, y = classification_data
        result = sp.plot_pca(X)
        assert result.fig is not None

    def test_1d_data_raises(self):
        with pytest.raises(ValueError):
            sp.plot_pca(np.array([1, 2, 3]))

    def test_too_few_samples(self):
        # n_samples=1 < n_components=2, should raise
        X = np.array([[1, 2]])
        with pytest.raises(ValueError):
            sp.plot_pca(X)

    def test_too_few_features(self):
        X = np.array([[1], [2], [3]])
        with pytest.raises(ValueError):
            sp.plot_pca(X)

    def test_label_length_mismatch(self, classification_data):
        X, y = classification_data
        with pytest.raises(ValueError):
            sp.plot_pca(X, labels=np.array([0, 1]))

    def test_n_components_not_2(self, classification_data):
        X, y = classification_data
        with pytest.raises(ValueError):
            sp.plot_pca(X, n_components=3)

    def test_venue_parameter(self, classification_data):
        X, y = classification_data
        result = sp.plot_pca(X, labels=y, venue="ieee")
        assert result.fig is not None


class TestPlotConfusionMatrix:
    def test_basic(self, confusion_data):
        y_true, y_pred = confusion_data
        result = sp.plot_confusion_matrix(y_true, y_pred)
        assert isinstance(result, sp.PlotResult)

    def test_with_labels(self, confusion_data):
        y_true, y_pred = confusion_data
        result = sp.plot_confusion_matrix(y_true, y_pred, labels=["Cat", "Dog", "Bird"])
        assert result.fig is not None

    def test_normalized(self, confusion_data):
        y_true, y_pred = confusion_data
        result = sp.plot_confusion_matrix(y_true, y_pred, normalize=True)
        assert result.fig is not None

    def test_custom_cmap(self, confusion_data):
        y_true, y_pred = confusion_data
        result = sp.plot_confusion_matrix(y_true, y_pred, cmap="Reds")
        assert result.fig is not None

    def test_empty_arrays(self):
        with pytest.raises(ValueError):
            sp.plot_confusion_matrix(np.array([]), np.array([]))

    def test_length_mismatch(self):
        with pytest.raises(ValueError):
            sp.plot_confusion_matrix(np.array([0, 1]), np.array([0]))

    def test_2d_array_raises(self):
        with pytest.raises(ValueError):
            sp.plot_confusion_matrix(np.array([[0, 1]]), np.array([0, 1]))


class TestPlotFeatureImportance:
    def test_basic(self):
        features = ["A", "B", "C", "D"]
        importance = np.array([0.3, 0.1, 0.4, 0.2])
        result = sp.plot_feature_importance(features, importance)
        assert isinstance(result, sp.PlotResult)

    def test_top_n(self):
        features = [f"F{i}" for i in range(20)]
        importance = np.random.rand(20)
        result = sp.plot_feature_importance(features, importance, top_n=5)
        assert result.fig is not None

    def test_empty_features(self):
        with pytest.raises(ValueError):
            sp.plot_feature_importance([], np.array([]))

    def test_length_mismatch(self):
        with pytest.raises(ValueError):
            sp.plot_feature_importance(["A", "B"], np.array([1.0]))

    def test_top_n_zero(self):
        with pytest.raises(ValueError):
            sp.plot_feature_importance(["A"], np.array([1.0]), top_n=0)

    def test_2d_importance_raises(self):
        with pytest.raises(ValueError):
            sp.plot_feature_importance(["A"], np.array([[1.0]]))


class TestPlotLearningCurve:
    def test_basic(self):
        train_scores = np.array([0.9, 0.92, 0.94, 0.95, 0.96])
        val_scores = np.array([0.8, 0.85, 0.88, 0.90, 0.91])
        result = sp.plot_learning_curve(train_scores, val_scores)
        assert isinstance(result, sp.PlotResult)

    def test_with_sizes(self):
        train_scores = np.array([0.9, 0.92, 0.94])
        val_scores = np.array([0.8, 0.85, 0.88])
        sizes = np.array([100, 200, 300])
        result = sp.plot_learning_curve(train_scores, val_scores, train_sizes=sizes)
        assert result.fig is not None

    def test_length_mismatch(self):
        with pytest.raises(ValueError):
            sp.plot_learning_curve(np.array([0.9, 0.92]), np.array([0.8]))

    def test_empty(self):
        with pytest.raises(ValueError):
            sp.plot_learning_curve(np.array([]), np.array([]))

    def test_2d_raises(self):
        with pytest.raises(ValueError):
            sp.plot_learning_curve(np.array([[0.9]]), np.array([[0.8]]))

    def test_sizes_length_mismatch(self):
        with pytest.raises(ValueError):
            sp.plot_learning_curve(np.array([0.9, 0.92]), np.array([0.8, 0.85]),
                                   train_sizes=np.array([100]))
