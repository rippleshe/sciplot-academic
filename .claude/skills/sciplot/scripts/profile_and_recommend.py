#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SciPlot Academic 数据自动画像与智能图表推荐脚本。

用法:
    uv run python .claude/skills/sciplot/scripts/profile_and_recommend.py data.csv --goal auto
    uv run python .claude/skills/sciplot/scripts/profile_and_recommend.py data.xlsx --goal comparison --top-k 5 --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _ensure_sciplot_importable() -> None:
    """若当前运行目录尚未安装可编辑 sciplot，则回退将仓库根路径加入 sys.path。"""
    try:
        import sciplot  # noqa: F401
    except ImportError:
        repo_root = Path(__file__).resolve().parents[4]
        if (repo_root / "sciplot" / "__init__.py").exists():
            sys.path.insert(0, str(repo_root))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="SciPlot 数据画像分析与多样化图表智能推荐工具 (v4.0.0)",
    )
    parser.add_argument(
        "data_path",
        type=str,
        help="输入数据文件路径（支持 .csv / .tsv / .xlsx / .json / .parquet）",
    )
    parser.add_argument(
        "--goal",
        type=str,
        default="auto",
        choices=[
            "auto",
            "comparison",
            "distribution",
            "relationship",
            "composition",
            "trend",
            "ranking",
            "multivariate",
            "evaluation",
        ],
        help="分析目标（默认 auto 自动推断）",
    )
    parser.add_argument("--top-k", type=int, default=4, help="返回最多多少条候选图表推荐（默认 4）")
    parser.add_argument("--target", type=str, default=None, help="目标响应/标签列名（可选）")
    parser.add_argument("--time-col", type=str, default=None, help="显式指定时间/有序轴列名（可选）")
    parser.add_argument("--group-col", type=str, default=None, help="显式指定分组列名（可选）")
    parser.add_argument("--json", action="store_true", help="以结构化 JSON 格式输出报告")

    args = parser.parse_args(argv)
    _ensure_sciplot_importable()

    import sciplot as sp

    path = Path(args.data_path)
    if not path.exists():
        print(f"[错误] 数据文件不存在: {path}", file=sys.stderr)
        return 1

    report = sp.recommend_charts(
        path,
        goal=args.goal,
        top_k=args.top_k,
        target=args.target,
        time_col=args.time_col,
        group_col=args.group_col,
    )

    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(report.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
