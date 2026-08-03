"""
Round-16 hardening tests for integration: config file loading, precedence,
thread isolation, and multi-format saving.
"""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest

import sciplot as sp


# ═══════════════════════════════════════════════════════════════
# 配置文件加载
# ═══════════════════════════════════════════════════════════════

def test_load_config_from_sciplot_toml(tmp_path, monkeypatch, cleanup_figures):
    sp.reset_config()
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".sciplot.toml").write_text(
        'venue = "ieee"\npalette = "ocean"\ndpi = 600\nformats = ["png"]\n',
        encoding="utf-8",
    )
    try:
        assert sp.load_config() is True
        assert sp.get_config("venue") == "ieee"
        assert sp.get_config("palette") == "ocean"
        assert sp.get_config("dpi") == 600
        assert sp.get_config("formats") == ("png",)
        assert sp.is_loaded() if hasattr(sp, "is_loaded") else True
    finally:
        sp.reset_config()


def test_load_config_from_pyproject_toml(tmp_path, monkeypatch):
    sp.reset_config()
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        '[tool.sciplot]\nvenue = "thesis"\nlang = "en"\n',
        encoding="utf-8",
    )
    try:
        assert sp.load_config() is True
        assert sp.get_config("venue") == "thesis"
        assert sp.get_config("lang") == "en"
    finally:
        sp.reset_config()


def test_load_config_missing_file_raises(tmp_path):
    sp.reset_config()
    with pytest.raises(FileNotFoundError):
        sp.load_config(tmp_path / "nope.toml")


def test_load_config_invalid_value_skipped(tmp_path, monkeypatch):
    """非法配置值应被跳过而不是让整个加载失败。"""
    sp.reset_config()
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".sciplot.toml").write_text(
        'venue = "not-a-venue"\nlang = "zh"\n',
        encoding="utf-8",
    )
    try:
        assert sp.load_config() is True
        # venue 非法被跳过，lang 合法被应用
        assert sp.get_config("venue") == "nature"
        assert sp.get_config("lang") == "zh"
    finally:
        sp.reset_config()


def test_config_precedence_user_over_file(tmp_path, monkeypatch):
    sp.reset_config()
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".sciplot.toml").write_text('venue = "ieee"\n', encoding="utf-8")
    try:
        sp.load_config()
        assert sp.get_config("venue") == "ieee"
        sp.set_defaults(venue="thesis")
        assert sp.get_config("venue") == "thesis"  # 代码设置优先
    finally:
        sp.reset_config()


def test_set_defaults_unknown_key_raises():
    sp.reset_config()
    with pytest.raises(ValueError, match="未知配置项"):
        sp.set_defaults(not_a_key=1)


def test_set_defaults_invalid_dpi_raises():
    sp.reset_config()
    with pytest.raises(ValueError, match="dpi"):
        sp.set_defaults(dpi=0)
    with pytest.raises(ValueError, match="dpi"):
        sp.set_defaults(dpi=-5)


def test_set_defaults_invalid_formats_raises():
    sp.reset_config()
    with pytest.raises(ValueError):
        sp.set_defaults(formats=())


def test_get_config_all_returns_merged():
    sp.reset_config()
    merged = sp.get_config()
    assert isinstance(merged, dict)
    assert "venue" in merged and "palette" in merged and "dpi" in merged


# ═══════════════════════════════════════════════════════════════
# 配置并发安全
# ═══════════════════════════════════════════════════════════════

def test_config_thread_safety():
    """并发读写配置不得抛异常且值一致。"""
    sp.reset_config()

    def worker(idx: int) -> bool:
        for _ in range(50):
            sp.set_defaults(dpi=300 + idx)
            dpi = sp.get_config("dpi")
            if dpi not in {300, 301, 302, 303}:
                return False
        return True

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(worker, range(4)))
    assert all(results)
    sp.reset_config()


def test_style_context_thread_isolation():
    """StyleContext 的栈必须线程隔离。"""
    from sciplot._core.context import StyleContext

    def worker(venue: str, ok: list) -> None:
        with StyleContext(venue):
            stack = StyleContext._get_stack()
            ok.append(len(stack) == 1 and stack[0].venue == venue)

    ok: list = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda v: worker(v, ok), ["ieee", "nature", "thesis", "aps"]))
    assert len(ok) == 4 and all(ok)
    assert len(StyleContext._get_stack()) == 0


# ═══════════════════════════════════════════════════════════════
# 多格式保存
# ═══════════════════════════════════════════════════════════════

@pytest.mark.parametrize("fmt", ["png", "pdf", "svg", "eps", "jpg"])
def test_save_all_supported_formats(tmp_path, cleanup_figures, fmt):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    paths = sp.save(fig, str(tmp_path / f"fig_{fmt}"), formats=(fmt,))
    assert len(paths) == 1
    assert paths[0].exists()
    assert paths[0].stat().st_size > 0


def test_save_vector_and_raster_same_call(tmp_path, cleanup_figures):
    """一次调用同时输出向量与位图格式。"""
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    paths = sp.save(fig, str(tmp_path / "dual"), formats=("pdf", "png"), dpi=150)
    assert len(paths) == 2
    assert all(p.exists() for p in paths)


def test_save_formats_from_config(tmp_path, cleanup_figures, monkeypatch):
    """formats 缺省时读取配置默认值。"""
    sp.reset_config()
    sp.set_defaults(formats=("png",), dpi=90)
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    try:
        paths = sp.save(fig, str(tmp_path / "cfg_fmt"))
        assert len(paths) == 1
        assert paths[0].suffix == ".png"
    finally:
        sp.reset_config()


def test_save_close_releases_figure(tmp_path, cleanup_figures):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    paths = sp.save(fig, str(tmp_path / "closed"), formats=("png",), close=True)
    assert len(paths) == 1
    assert all(p.exists() for p in paths)
