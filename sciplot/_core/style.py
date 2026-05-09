"""
样式管理 — 期刊/场合样式配置
"""

from __future__ import annotations

import shutil
import threading
from typing import Any, Dict, List, Optional, Tuple, NamedTuple, cast

import matplotlib.pyplot as plt


# ============================================================================
# 线程局部状态 — 语言设置
# ============================================================================

_thread_local = threading.local()

# LaTeX 可用性缓存（None = 未检测）
_latex_available: Optional[bool] = None


def _ensure_thread_local_initialized() -> None:
    """确保线程局部状态已初始化。"""
    if not getattr(_thread_local, "_initialized", False):
        _thread_local.lang = None
        _thread_local.venue = None
        _thread_local.palette = None
        _thread_local._initialized = True


def get_current_lang() -> Optional[str]:
    """获取当前设置的语言代码（线程安全）"""
    _ensure_thread_local_initialized()
    return cast(Optional[str], _thread_local.lang)


def set_current_lang(lang: Optional[str]) -> None:
    """设置当前语言代码（线程安全）"""
    _ensure_thread_local_initialized()
    _thread_local.lang = lang


def get_current_venue() -> Optional[str]:
    """获取当前设置的 venue（线程安全）。"""
    _ensure_thread_local_initialized()
    return cast(Optional[str], _thread_local.venue)


def set_current_venue(venue: Optional[str]) -> None:
    """设置当前 venue（线程安全）。"""
    _ensure_thread_local_initialized()
    _thread_local.venue = venue


def get_current_palette() -> Optional[str]:
    """获取当前设置的 palette（线程安全）。"""
    _ensure_thread_local_initialized()
    return cast(Optional[str], _thread_local.palette)


def set_current_palette(palette: Optional[str]) -> None:
    """设置当前 palette（线程安全）。"""
    _ensure_thread_local_initialized()
    _thread_local.palette = palette


# ============================================================================
# Venues — 期刊/场合预设
# 使用具名配置，避免位置索引带来的可维护性风险。
# ============================================================================

class VenueConfig(NamedTuple):
    styles: Tuple[str, ...]
    figsize: Tuple[float, float]
    fontsize: int


VENUES: Dict[str, VenueConfig] = {
    "nature": VenueConfig(("science", "nature", "no-latex"), (7.0, 5.0), 8),
    "ieee": VenueConfig(("science", "ieee", "no-latex"), (3.5, 3.0), 6),
    "aps": VenueConfig(("science", "no-latex"), (3.4, 2.8), 6),
    "springer": VenueConfig(("science", "no-latex"), (6.0, 4.5), 8),
    "thesis": VenueConfig(("science", "no-latex"), (6.1, 4.3), 8),
    "presentation": VenueConfig(("science", "notebook", "no-latex"), (8.0, 5.5), 12),
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

# 有效的语言代码列表
VALID_LANGS = set(LANGUAGES.keys())


# ============================================================================
# Themes — 主题预设
# ============================================================================

THEMES: Dict[str, Dict[str, Any]] = {
    "light": {},  # 默认浅色，无需额外 rcParams
    "dark": {
        "figure.facecolor": "#1a1a2e",
        "axes.facecolor": "#16213e",
        "axes.edgecolor": "#e0e0e0",
        "axes.labelcolor": "#e0e0e0",
        "text.color": "#e0e0e0",
        "xtick.color": "#b0b0b0",
        "ytick.color": "#b0b0b0",
        "xtick.labelcolor": "#b0b0b0",
        "ytick.labelcolor": "#b0b0b0",
        "axes.titlecolor": "#e0e0e0",
        "legend.facecolor": "#16213e",
        "legend.edgecolor": "#404060",
        "legend.labelcolor": "#e0e0e0",
        "figure.edgecolor": "#1a1a2e",
        "savefig.facecolor": "#1a1a2e",
        "grid.color": "#303050",
    },
}


def setup_style(
    venue: Optional[str] = None,
    palette: Optional[str] = None,
    lang: Optional[str] = None,
    theme: Optional[str] = None,
) -> None:
    """
    配置 Matplotlib 绘图样式（每次绘图前调用一次，或通过各绘图函数的 venue/palette 参数自动调用）

    参数:
        venue  : 期刊/场合预设，默认从 Config 读取（回退 'nature'）
                 'nature' | 'ieee' | 'aps' | 'springer' | 'thesis' | 'presentation'
        palette: 配色方案，默认从 Config 读取（回退 'pastel'）
                 三大常驻系列（含 -1/-2/-3/-4 子集）：pastel / earth / ocean
                 人民币系列：100yuan / 50yuan / 20yuan / 10yuan / 5yuan / 1yuan
                 用户自定义：set_custom_palette() 注册后按名称使用
        lang   : 语言/字体，默认从 Config 读取（回退 'zh'，中文宋体）
                 'zh' | 'zh-cn' → 中文宋体 + CJK 布局
                 'en'           → Times New Roman
        theme  : 主题模式，默认 'light'
                 'light' → 浅色背景（默认）
                 'dark'  → 深色背景（适合演示/屏幕展示）

    示例:
        >>> import sciplot as sp
        >>> sp.setup_style()                          # 从 Config 读取（默认 nature + pastel + 中文）
        >>> sp.set_defaults(venue="ieee")
        >>> sp.setup_style()                          # 使用 Config 中的 ieee
        >>> sp.setup_style("ieee", "pastel-2")        # 显式指定：IEEE + pastel 前 2 色
        >>> sp.setup_style("thesis", "100yuan")       # 学位论文 + 人民币红
        >>> sp.setup_style(lang="en")                 # 英文模式
        >>> sp.setup_style("presentation", theme="dark")  # 演示文稿 + 深色主题
    """
    # 从 Config 读取默认值（仅在参数未显式传入时）
    if venue is None or palette is None or lang is None:
        from sciplot._core.config import get_config as _get_config
        if venue is None:
            cfg_venue = _get_config("venue")
            venue = cfg_venue if isinstance(cfg_venue, str) and cfg_venue else "nature"
        if palette is None:
            cfg_palette = _get_config("palette")
            palette = cfg_palette if isinstance(cfg_palette, str) and cfg_palette else "pastel"
        if lang is None:
            cfg_lang = _get_config("lang")
            lang = cfg_lang if isinstance(cfg_lang, str) and cfg_lang else "zh"

    if venue not in VENUES:
        raise ValueError(
            f"未知 venue '{venue}'，可用选项: {list(VENUES.keys())}"
        )

    venue_cfg = VENUES[venue]
    styles = list(venue_cfg.styles)
    fontsize = venue_cfg.fontsize

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

    # ── 应用样式（优先 SciencePlots，缺失时自动降级） ──
    active_styles = styles + ([lang_style] if lang_style else [])
    try:
        # 若已安装则确保样式注册到 matplotlib
        import scienceplots  # noqa: F401
    except ImportError:
        pass

    available_styles = set(plt.style.available)
    resolved_styles = [s for s in active_styles if s in available_styles]
    if resolved_styles:
        plt.style.use(resolved_styles)
    else:
        plt.style.use("default")

    # ── 配色 ──
    from sciplot._core.palette import apply_palette
    apply_palette(palette)

    # ── LaTeX 设置 ──
    # 中文模式下禁用 LaTeX（LaTeX 不支持中文）
    # 英文模式下可启用 LaTeX 以获得更好的数学公式渲染
    if lang == "en":
        # 英文模式：检测系统是否安装 LaTeX（结果缓存，避免重复调用 shutil.which）
        global _latex_available
        if _latex_available is None:
            _latex_available = bool(
                shutil.which("latex") or shutil.which("xelatex") or shutil.which("pdflatex")
            )
        plt.rcParams["text.usetex"] = _latex_available
    else:
        # 中文模式：禁用 LaTeX，确保中文正常渲染
        plt.rcParams["text.usetex"] = False

    # ── 修复负号显示问题 ──
    # 必须在字体设置之前，确保使用 ASCII 减号而不是 Unicode 减号
    plt.rcParams["axes.unicode_minus"] = False
    # 禁用 mathtext 用于刻度标签，避免 scienceplots 的 no-latex 样式设置 use_mathtext=True
    plt.rcParams["axes.formatter.use_mathtext"] = False

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

    # ── 数学文本字体设置 ──
    # 使用与正文字体一致的设置，避免字体缺失导致的负号问题
    plt.rcParams["mathtext.fontset"] = "custom"
    plt.rcParams["mathtext.rm"] = "Times New Roman"
    plt.rcParams["mathtext.it"] = "Times New Roman:italic"
    plt.rcParams["mathtext.bf"] = "Times New Roman:bold"

    # ── 字号 ──
    effective_fontsize = fontsize
    # IEEE + 中文：中文在相同 pt 下视觉偏大，自动下调 1pt
    if venue == "ieee" and lang in {"zh", "zh-cn"}:
        effective_fontsize = max(5, fontsize - 1)

    plt.rcParams["font.size"]       = effective_fontsize
    plt.rcParams["axes.labelsize"]  = effective_fontsize
    plt.rcParams["axes.titlesize"]  = effective_fontsize
    plt.rcParams["xtick.labelsize"] = max(6, effective_fontsize - 1)
    plt.rcParams["ytick.labelsize"] = max(6, effective_fontsize - 1)
    plt.rcParams["legend.fontsize"] = max(6, effective_fontsize - 1)

    # ── 其他规范 ──
    plt.rcParams["axes.grid"] = False   # 科研图默认不加网格

    # ── 主题 ──
    effective_theme = theme if theme is not None else "light"
    if effective_theme not in THEMES:
        raise ValueError(
            f"未知主题 '{effective_theme}'，可用选项: {list(THEMES.keys())}"
        )
    theme_rc = THEMES[effective_theme]
    if theme_rc:  # "light" 是空字典，无需更新
        plt.rcParams.update(theme_rc)

    # 所有样式应用成功后再写入线程局部状态，避免异常路径污染状态。
    set_current_lang(lang)
    set_current_venue(venue)
    set_current_palette(palette)


def reset_style() -> None:
    """重置 Matplotlib 为系统默认样式"""
    plt.rcdefaults()
    set_current_lang(None)
    set_current_venue(None)
    set_current_palette(None)


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
    venue_cfg = VENUES[venue]
    return {
        "name": venue,
        "styles": venue_cfg.styles,
        "figsize": venue_cfg.figsize,
        "fontsize": venue_cfg.fontsize,
    }


def list_venues() -> List[str]:
    """列出所有可用期刊预设名称"""
    return list(VENUES.keys())


def list_languages() -> List[str]:
    """列出所有可用语言代码"""
    return list(LANGUAGES.keys())


def list_themes() -> List[str]:
    """列出所有可用主题名称"""
    return list(THEMES.keys())

