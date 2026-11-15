#!/usr/bin/env python3
"""SciPlot 数据画像与智能图表推荐命令行脚本。

在写入任何绘图代码前，优先运行本脚本体检输入数据（CSV/TSV/Excel/JSON/Parquet
或演示结构），输出变量类型、分布偏度、缺失警告及反单调多样化图表候选方案。

用法:
    uv run python .claude/skills/sciplot/scripts/profile_and_recommend.py data.csv
    uv run python .claude/skills/sciplot/scripts/profile_and_recommend.py data.csv --goal comparison --top-k 4
    uv run python .claude/skills/sciplot/scripts/profile_and_recommend.py --demo grouped --json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import numpy as np

import sciplot as sp


def _build_demo_data(name: str) -> Any:
    """构造不同典型数据形态的演示数据以便快速测试选型。"""
    rng = np.random.default_rng(42)
    if name == "grouped":
        return {
            "Control": rng.normal(5.2, 0.7, 36),
            "Treatment_A": rng.normal(6.5, 1.1, 36),
            "Treatment_B": rng.normal(7.4, 0.8, 36),
        }
    if name == "paired":
        b = rng.normal(60.0, 8.0, 24)
        return {"before": b, "after": b + rng.normal(8.5, 4.0, 24)}
    if name == "corr":
        return np.corrcoef(rng.normal(size=(6, 45)))
    if name == "timeseries":
        t = np.arange(30)
        return {
            "time": t,
            "Sensor_A": np.sin(t * 0.2) + 5.0,
            "Sensor_B": np.cos(t * 0.2) + 5.5,
            "Sensor_C": 0.05 * t + 4.8,
        }
    if name == "bivariate_large":
        x = rng.normal(size=1200)
        return {"x": x, "y": 0.7 * x + rng.normal(0, 0.6, 1200)}
    # multivariate default
    return {
        "Feature_1": rng.normal(0, 1, 50),
        "Feature_2": rng.normal(1, 1.2, 50),
        "Feature_3": rng.normal(-1, 0.8, 50),
        "Feature_4": rng.normal(2, 1.5, 50),
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="剖析科研数据集形态并生成 SciPlot 多样化图表推荐报告"
    )
    parser.add_argument(
        "data",
        nargs="?",
        help="输入数据文件路径（支持 .csv / .tsv / .xlsx / .json / .parquet）",
    )
    parser.add_argument(
        "--demo",
        choices=("grouped", "paired", "corr", "timeseries", "bivariate_large", "multi"),
        help="无文件时生成指定形态的演示数据并运行推荐引擎",
    )
    parser.add_argument(
        "--goal",
        default="auto",
        choices=(
            "auto",
            "comparison",
            "distribution",
            "relationship",
            "composition",
            "trend",
            "ranking",
            "multivariate",
            "evaluation",
        ),
        help="主要分析意图，默认 auto 自动推断",
    )
    parser.add_argument("--top-k", type=int, default=4, help="返回推荐方案数量")
    parser.add_argument("--target", default=None, help="目标变量列名")
    parser.add_argument("--time-col", default=None, help="时间列名")
    parser.add_argument("--group-col", default=None, help="分组列名")
    parser.add_argument("--json", action="store_true", help="输出结构化 JSON")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.demo:
        payload: Any = _build_demo_data(args.demo)
    elif args.data:
        payload = Path(args.data)
    else:
        raise SystemExit("请提供数据文件路径或使用 --demo 参数。")

    report = sp.recommend_charts(
        payload,
        goal=args.goal,
        top_k=args.top_k,
        target=args.target,
        time_col=args.time_col,
        group_col=args.group_col,
    )
    if args.json:
        out: Dict[str, Any] = report.to_dict()
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(report.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
