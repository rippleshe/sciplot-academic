"""
样式管理 — 期刊/场合样式配置
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt


# ============================================================================
# Venues — 期刊/场合预设
# 格式：(SciencePlots 样式列表, 图尺寸(宽, 高)英寸, 基础字号 pt)
# ============================================================================

VENUES: Dict[str, tuple] = {
    "nature":       (["science", "nature",   "no-latex"], (7.0, 5.0), 10),
    "ieee":         (["science", "ieee",     "no-latex"], (3.5, 3.0),  8),
    "aps":          (["science",             "no-latex"], (3.4, 2.8),  8),
    "springer":     (["science",             "no-latex"], (6.0, 4.5), 10),
    "thesis":       (["science",             "no-latex"], (6.1, 4.3), 10),
    "presentation": (["science", "notebook", "no-latex"], (8.0, 5.5), 14),
    "default":      (["science", "nature",   "no-latex"], (7.0, 5.0), 10),
}

# ============================================================================
# Languages — 语言/字体预设
# 格式：(SciencePlots CJK 样式名 | None, 主字体名)
# ============================================================================

LANGUAGES: Dict[str, Tuple[Optional[str], str]] = {
    "zh":    ("cjk-sc-font", "SimSun"),       # 简体中文（宋体）
    "zh-cn": ("cjk-sc-font", "SimSun"),       # 简体中文（别名）
    "en":    (None,           "Times New Roman"),  # 纯英文
}


def setup_style(
    venue: str = "nature",
    palette: str = "pastel",
    lang: Optional[str] = "zh",
) -> None:
    """
    配置 Matplotlib 绘图样式（每次绘图前调用一次，或通过各绘图函数的 venue/palette 参数自动调用）

    参数:
        venue  : 期刊/场合预设，默认 'nature'
                 'nature' | 'ieee' | 'aps' | 'springer' | 'thesis' | 'presentation'
        palette: 配色方案，默认 'pastel'
                 三大常驻系列（含 -1/-2/-3/-4 子集）：pastel / earth / ocean
                 人民币系列：100yuan / 50yuan / 20yuan / 10yuan / 5yuan / 1yuan
                 用户自定义：set_custom_palette() 注册后按名称使用
        lang   : 语言/字体，默认 'zh'（中文宋体）
                 'zh' | 'zh-cn' → 中文宋体 + CJK 布局
                 'en'           → Times New Roman

    示例:
        >>> import sciplot as sp
        >>> sp.setup_style()                          # 默认：nature + pastel + 中文
        >>> sp.setup_style("ieee", "pastel-2")        # IEEE + pastel 前 2 色
        >>> sp.setup_style("ieee", "earth-3")         # IEEE + earth 前 3 色
        >>> sp.setup_style("thesis", "100yuan")       # 学位论文 + 人民币红
        >>> sp.setup_style(lang="en")                 # 英文模式
    """
    if venue not in VENUES:
        raise ValueError(
            f"未知 venue '{venue}'，可用选项: {list(VENUES.keys())}"
        )

    styles, _, fontsize = VENUES[venue]

    # ── 语言 / 字体 ──
    lang_style: Optional[str] = None
    cjk_font: Optional[str] = None
    if lang is not None:
        if lang not in LANGUAGES:
            raise ValueError(
                f"未知 lang '{lang}'，可用选项: {list(LANGUAGES.keys())}"
            )
        lang_style, main_font = LANGUAGES[lang]
        if lang == "en":
            # 英文模式：不加载 CJK 样式，字体只用 Times New Roman
            lang_style = None
            cjk_font = None
        else:
            cjk_font = main_font

    # ── 重置并应用 SciencePlots 样式 ──
    plt.rcdefaults()
    active_styles = styles + ([lang_style] if lang_style else [])
    plt.style.use(active_styles)

    # ── 配色 ──
    from sciplot._core.palette import apply_palette
    apply_palette(palette)

    # ── 禁用 LaTeX（确保中文/特殊字符正常渲染）──
    plt.rcParams["text.usetex"] = False

    # ── 字体 ──
    plt.rcParams["font.family"] = "serif"
    if cjk_font:
        plt.rcParams["font.serif"] = [
            cjk_font,
            "Noto Serif CJK SC",
            "Source Han Serif SC",
            "Times New Roman",
            "DejaVu Serif",
        ]
    else:
        plt.rcParams["font.serif"] = [
            "Times New Roman",
            "DejaVu Serif",
            "serif",
        ]
    plt.rcParams["axes.unicode_minus"] = False  # 修复负号显示

    # ── 字号 ──
    effective_fontsize = fontsize
    # IEEE + 中文：中文在相同 pt 下视觉偏大，自动下调 1pt
    if venue == "ieee" and lang in {"zh", "zh-cn"}:
        effective_fontsize = max(7, fontsize - 1)

    plt.rcParams["font.size"]       = effective_fontsize
    plt.rcParams["axes.labelsize"]  = effective_fontsize
    plt.rcParams["axes.titlesize"]  = effective_fontsize
    plt.rcParams["xtick.labelsize"] = max(6, effective_fontsize - 1)
    plt.rcParams["ytick.labelsize"] = max(6, effective_fontsize - 1)
    plt.rcParams["legend.fontsize"] = max(6, effective_fontsize - 1)

    # ── 其他规范 ──
    plt.rcParams["axes.grid"] = False   # 科研图默认不加网格


def reset_style() -> None:
    """重置 Matplotlib 为系统默认样式"""
    plt.rcdefaults()


def get_venue_info(venue: str) -> Dict[str, Any]:
    """
    获取期刊预设的详细配置

    返回:
        {'name', 'styles', 'figsize', 'fontsize'}

    示例:
        >>> sp.get_venue_info("ieee")
        {'name': 'ieee', 'styles': ['science', 'ieee', 'no-latex'],
         'figsize': (3.5, 3.0), 'fontsize': 8}
    """
    if venue not in VENUES:
        raise ValueError(f"未知 venue '{venue}'，可用选项: {list(VENUES.keys())}")
    styles, figsize, fontsize = VENUES[venue]
    return {"name": venue, "styles": styles, "figsize": figsize, "fontsize": fontsize}


def list_venues() -> List[str]:
    """列出所有可用期刊预设名称"""
    return list(VENUES.keys())


def list_languages() -> List[str]:
    """列出所有可用语言代码"""
    return list(LANGUAGES.keys())
