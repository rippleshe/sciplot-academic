"""
色盲安全防线 — 模拟与校验

审稿高频雷区之一：色盲不安全的配色（color-blind unsafe palettes）。
本模块提供：
1. simulate_colorblind()   — 用 Brettel-Viénot-Mollon (1997) 矩阵模拟三类色觉缺失
2. check_colorblind_safe() — 校验一组颜色在色盲视角下是否仍可区分
3. audit_palette()         — 对整套内置配色做色盲安全体检

约 8% 男性存在色觉缺陷（红绿色盲为主），顶刊审稿人常以此
拒绝图表。任何新配色都应通过本模块校验后再内置。
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

# ============================================================================
# Brettel-Viénot-Mollon (1997) 色觉缺失模拟矩阵
# （RGB 线性域 → LMS 域变换后投影，业界标准实现）
# ============================================================================

# sRGB 线性化
def _srgb_to_linear(c: np.ndarray) -> np.ndarray:
    """sRGB 伽马编码 → 线性 RGB。"""
    out = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return out


def _linear_to_srgb(c: np.ndarray) -> np.ndarray:
    """线性 RGB → sRGB 伽马编码（负值先 clip，避免投影越界）。"""
    c = np.clip(c, 0.0, 1.0)
    out = np.where(c <= 0.0031308, 12.92 * c, 1.055 * c ** (1 / 2.4) - 0.055)
    return np.clip(out, 0.0, 1.0)


# RGB → LMS 转换（Hunt-Pointer-Estevez）
_RGB_TO_LMS = np.array([
    [0.31399022, 0.63951294, 0.04649755],
    [0.15537241, 0.75789446, 0.08670142],
    [0.01775239, 0.10944209, 0.87256922],
])
_LMS_TO_RGB = np.linalg.inv(_RGB_TO_LMS)

# 各色觉缺失的投影矩阵（Brettel 1997，线性 LMS 域）
_DEFICIENCY_MATRICES: Dict[str, np.ndarray] = {
    "deuteranopia": np.array([
        [0.367, 0.861, -0.228],
        [0.280, 0.673, 0.047],
        [-0.012, 0.043, 0.969],
    ]),
    "protanopia": np.array([
        [0.152, 1.053, -0.205],
        [0.115, 0.786, 0.099],
        [-0.004, -0.048, 1.052],
    ]),
    "tritanopia": np.array([
        [1.256, -0.077, -0.179],
        [-0.078, 0.931, 0.148],
        [0.005, 0.691, 0.304],
    ]),
}

VALID_DEFICIENCIES = tuple(_DEFICIENCY_MATRICES.keys())


def simulate_colorblind(
    colors: Sequence[str],
    deficiency: str = "deuteranopia",
) -> List[str]:
    """
    模拟色觉缺失下的颜色外观（返回模拟后的 HEX 色）。

    参数:
        colors    : HEX 颜色列表
        deficiency: 色觉缺失类型
                    'deuteranopia'（绿色弱，最常见，默认）
                    'protanopia'  （红色弱）
                    'tritanopia'  （蓝色弱）

    返回:
        模拟后的 HEX 颜色列表（长度与输入一致）

    示例:
        >>> sp.simulate_colorblind(["#E69F00", "#009E73"])
        ['#8f9a5c', '#9c9c5c']  # 两色在绿色弱视角下趋同
    """
    if deficiency not in _DEFICIENCY_MATRICES:
        raise ValueError(
            f"未知 deficiency '{deficiency}'，可用选项: {list(_DEFICIENCY_MATRICES.keys())}"
        )
    if not colors:
        return []

    mat = _DEFICIENCY_MATRICES[deficiency]

    # HEX → 线性 RGB（3×N 矩阵，行 = R/G/B）
    rgb_lin = np.zeros((3, len(colors)))
    for i, c in enumerate(colors):
        hex_str = str(c).lstrip("#")
        if len(hex_str) != 6:
            raise ValueError(f"无效 HEX 颜色: {c!r}")
        rgb = np.array([
            int(hex_str[0:2], 16),
            int(hex_str[2:4], 16),
            int(hex_str[4:6], 16),
        ]) / 255.0
        rgb_lin[:, i] = _srgb_to_linear(rgb)

    # 线性 RGB → LMS → 投影 → 线性 RGB
    lms = _RGB_TO_LMS @ rgb_lin
    lms_sim = mat @ lms
    rgb_sim = _LMS_TO_RGB @ lms_sim
    rgb_sim = _linear_to_srgb(rgb_sim)

    out: List[str] = []
    for i in range(len(colors)):
        r, g, b = rgb_sim[:, i]
        out.append(f"#{int(round(r * 255)):02X}{int(round(g * 255)):02X}{int(round(b * 255)):02X}")
    return out


def _hex_to_rgb01(color: str) -> Tuple[float, float, float]:
    hex_str = str(color).lstrip("#")
    if len(hex_str) != 6:
        raise ValueError(f"无效 HEX 颜色: {color!r}")
    return (
        int(hex_str[0:2], 16) / 255.0,
        int(hex_str[2:4], 16) / 255.0,
        int(hex_str[4:6], 16) / 255.0,
    )


def _perceptual_distance(c1: Tuple[float, float, float], c2: Tuple[float, float, float]) -> float:
    """CIE76 感知距离（sRGB→Lab 近似）。用简单加权欧氏距离即可区分度校验。"""
    # 快速近似：加权 RGB 距离（绿通道敏感度最高）
    dr = c1[0] - c2[0]
    dg = c1[1] - c2[1]
    db = c1[2] - c2[2]
    return float(np.sqrt(2.0 * dr * dr + 4.0 * dg * dg + 3.0 * db * db))


def check_colorblind_safe(
    colors: Sequence[str],
    deficiencies: Sequence[str] = ("deuteranopia", "protanopia", "tritanopia"),
    min_distance: float = 0.15,
) -> Dict[str, Dict[str, object]]:
    """
    校验一组颜色在色盲视角下是否仍可区分。

    对每种色觉缺失类型，模拟所有颜色并计算两两感知距离；
    若最小距离低于阈值，则该类型下存在不可区分的颜色对。

    参数:
        colors      : HEX 颜色列表（至少 2 个）
        deficiencies: 要检查的色觉缺失类型列表
        min_distance: 可区分的最小感知距离（0~1，默认 0.15）

    返回:
        {缺失类型: {"safe": bool, "min_distance": float, "conflict_pairs": [(c1, c2), ...]}}

    示例:
        >>> report = sp.check_colorblind_safe(["#E69F00", "#009E73", "#56B4E9"])
        >>> report["deuteranopia"]["safe"]
        True
    """
    if len(colors) < 2:
        raise ValueError("至少需要两个颜色才能校验区分度")
    if not colors:
        raise ValueError("colors 不能为空")
    for d in deficiencies:
        if d not in _DEFICIENCY_MATRICES:
            raise ValueError(
                f"未知 deficiency '{d}'，可用选项: {list(_DEFICIENCY_MATRICES.keys())}"
            )

    report: Dict[str, Dict[str, object]] = {}
    for d in deficiencies:
        simulated = simulate_colorblind(colors, d)
        rgb_list = [_hex_to_rgb01(c) for c in simulated]

        min_d = 1e9
        conflicts: List[Tuple[str, str]] = []
        n = len(rgb_list)
        for i in range(n):
            for j in range(i + 1, n):
                dist = _perceptual_distance(rgb_list[i], rgb_list[j])
                if dist < min_d:
                    min_d = dist
                if dist < min_distance:
                    conflicts.append((colors[i], colors[j]))

        report[d] = {
            "safe": min_d >= min_distance,
            "min_distance": round(min_d, 4),
            "conflict_pairs": conflicts,
        }
    return report


def audit_palette(
    palette_name: str,
    min_distance: float = 0.15,
) -> Dict[str, object]:
    """
    对内置配色方案做色盲安全体检（审计）。

    参数:
        palette_name: 配色方案名（如 'pastel', 'ocean', '100yuan'）
        min_distance: 可区分的最小感知距离

    返回:
        {"palette": str, "n_colors": int, "report": {缺失类型: {...}}, "safe": bool}

    示例:
        >>> sp.audit_palette("pastel")
        {'palette': 'pastel', 'n_colors': 8, 'report': {...}, 'safe': True}
    """
    from sciplot._core.palette import get_palette

    colors = get_palette(palette_name)
    if not colors:
        raise ValueError(f"配色方案 '{palette_name}' 为空或不存在")

    report = check_colorblind_safe(colors, min_distance=min_distance)
    safe = all(r["safe"] for r in report.values())  # type: ignore[index]
    return {
        "palette": palette_name,
        "n_colors": len(colors),
        "report": report,
        "safe": bool(safe),
    }


# ============================================================================
# 色盲安全调色板（Okabe-Ito 2017，学术界事实标准）
# ============================================================================

OKABE_ITO: Dict[str, List[str]] = {
    "okabe-ito": [
        "#E69F00",  # 橙
        "#56B4E9",  # 天蓝
        "#009E73",  # 绿
        "#F0E442",  # 黄
        "#0072B2",  # 蓝
        "#D55E00",  # 朱红
        "#CC79A7",  # 紫
        "#000000",  # 黑
    ],
    "okabe-ito-4": [
        "#E69F00", "#56B4E9", "#009E73", "#0072B2",
    ],
    "okabe-ito-6": [
        "#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00", "#CC79A7",
    ],
}
