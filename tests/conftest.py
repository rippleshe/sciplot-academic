"""
Pytest 配置文件 - 测试共享 fixtures 和配置
"""

import pytest
import matplotlib
import numpy as np
import tempfile
import shutil
from pathlib import Path

# 设置非交互式后端，避免测试时弹出窗口
matplotlib.use("Agg")


def _check_ml_available():
    """检查 ML 扩展是否可用"""
    try:
        from sciplot._ext import ml
        return True
    except ImportError:
        return False


def _check_scipy_available():
    """检查 scipy 是否可用"""
    try:
        import scipy
        return True
    except ImportError:
        return False


@pytest.fixture(scope="session")
def test_data():
    """生成标准测试数据"""
    np.random.seed(42)
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    y2 = np.cos(x)
    y3 = np.sin(x) + np.cos(x)
    categories = ["A", "B", "C", "D"]
    values = [23, 45, 56, 78]
    data_list = [np.random.normal(0, 1, 100) for _ in range(3)]

    return {
        "x": x,
        "y": y,
        "y2": y2,
        "y3": y3,
        "categories": categories,
        "values": values,
        "data_list": data_list,
        "matrix": np.random.rand(5, 5),
    }


@pytest.fixture(scope="function")
def temp_dir():
    """创建临时目录用于保存测试输出"""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)


@pytest.fixture(scope="function")
def cleanup_figures():
    """测试后清理 matplotlib 图形"""
    import matplotlib.pyplot as plt
    yield
    plt.close("all")


@pytest.fixture(scope="function")
def reset_style():
    """测试后重置样式"""
    yield
    import sciplot as sp
    sp.reset_style()


# 标记慢测试
slow = pytest.mark.skipif(
    False,  # 默认不跳过，可以通过 --run-slow 控制
    reason="需要 --run-slow 选项来运行慢测试"
)

# 标记需要 ML 扩展的测试
requires_ml = pytest.mark.skipif(
    not _check_ml_available(),
    reason="需要安装 sciplot-academic[ml]"
)

# 标记需要 scipy 的测试
requires_scipy = pytest.mark.skipif(
    not _check_scipy_available(),
    reason="需要安装 scipy"
)
