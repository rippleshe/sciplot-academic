"""
Round-33 tests for plot_taylor (泰勒图).
"""

from __future__ import annotations

import numpy as np
import pytest

import sciplot as sp


@pytest.fixture()
def taylor_data():
    rng = np.random.default_rng(31)
    obs = rng.normal(0, 1, 500)
    pred_a = 0.9 * obs + 0.4 * rng.normal(0, 1, 500)   # 高相关
    pred_b = 0.6 * obs + 0.8 * rng.normal(0, 1, 500)   # 中相关
    pred_c = -0.3 * obs + 1.2 * rng.normal(0, 1, 500)  # 低/负相关
    return obs, {"模型A": pred_a, "模型B": pred_b, "模型C": pred_c}


def test_taylor_basic(taylor_data, cleanup_figures):
    obs, models = taylor_data
    result = sp.plot_taylor(obs, models)
    assert result.fig is not None
    # 观测点 + 3 个模型点
    n_scatter = len(result.ax.collections)
    assert n_scatter == 4


def test_taylor_correlation_encoding(taylor_data, cleanup_figures):
    """模型点角度应编码相关系数：高相关模型角度更小。"""
    obs, models = taylor_data
    result = sp.plot_taylor(obs, models)
    scatters = result.ax.collections
    # 收集模型点角度（跳过观测点：θ=0, ρ=1）
    points = []
    for coll in scatters[1:]:
        offs = np.asarray(coll.get_offsets())
        points.append((offs[0][0], offs[0][1]))  # (θ, ρ)
    # 模型A 相关最高 → θ 最小
    thetas = [p[0] for p in points]
    assert thetas[0] == min(thetas)


def test_taylor_std_ratio_encoding(taylor_data, cleanup_figures):
    """模型点半径应编码标准差比。"""
    obs, models = taylor_data
    result = sp.plot_taylor(obs, models)
    scatters = result.ax.collections
    rho_obs = float(np.asarray(scatters[0].get_offsets())[0][1])
    assert rho_obs == pytest.approx(1.0)  # 观测点在 ρ=1


def test_taylor_single_model(taylor_data, cleanup_figures):
    obs, models = taylor_data
    result = sp.plot_taylor(obs, {"only": models["模型A"]})
    assert result.fig is not None


def test_taylor_reference_toggles(taylor_data, cleanup_figures):
    obs, models = taylor_data
    result = sp.plot_taylor(
        obs, models, show_corr_lines=False, show_std_lines=False,
        show_rms_lines=False,
    )
    assert result.fig is not None


def test_taylor_custom_rms_levels(taylor_data, cleanup_figures):
    obs, models = taylor_data
    result = sp.plot_taylor(obs, models, rms_levels=[0.25, 0.75])
    assert result.fig is not None


def test_taylor_empty_models_raises(taylor_data, cleanup_figures):
    obs, _ = taylor_data
    with pytest.raises(ValueError, match="models"):
        sp.plot_taylor(obs, {})


def test_taylor_length_mismatch_raises(taylor_data, cleanup_figures):
    obs, models = taylor_data
    bad = dict(models)
    bad["bad"] = np.random.randn(100)
    with pytest.raises(ValueError, match="长度"):
        sp.plot_taylor(obs, bad)


def test_taylor_constant_obs_raises(cleanup_figures):
    obs = np.ones(50)
    with pytest.raises(ValueError, match="方差为零"):
        sp.plot_taylor(obs, {"m": np.random.randn(50)})


def test_taylor_nan_raises(taylor_data, cleanup_figures):
    obs, models = taylor_data
    bad = dict(models)
    bad["bad"] = np.array([1.0, np.nan] + [0.0] * (len(obs) - 2))
    with pytest.raises(ValueError, match="NaN 或 Inf"):
        sp.plot_taylor(obs, bad)


def test_taylor_too_few_points_raises(cleanup_figures):
    with pytest.raises(ValueError, match="至少需要 3 个"):
        sp.plot_taylor([1.0, 2.0], {"m": [1.0, 2.0]})


def test_taylor_alias_and_export(taylor_data, cleanup_figures):
    obs, models = taylor_data
    assert callable(sp.plot_taylor)
    assert callable(sp.taylor)
    assert "plot_taylor" in sp.__all__ and "taylor" in sp.__all__
    result = sp.taylor(obs, models)
    assert result.fig is not None


def test_taylor_save_png(tmp_path, taylor_data, cleanup_figures):
    obs, models = taylor_data
    result = sp.plot_taylor(obs, models, title="模型评估")
    paths = result.save(str(tmp_path / "taylor"), formats=("png",), dpi=100)
    assert paths[0].exists() and paths[0].stat().st_size > 0
