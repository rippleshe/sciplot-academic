#!/usr/bin/env python3
"""
SciPlot Academic — PyPI 发布脚本
===================================

使用前提：
  uv add --dev build twine

步骤：
  1. 修改 pyproject.toml 中的 version
  2. 运行本脚本：python publish.py
     - 交互模式：直接运行 python publish.py
     - 一键发布：python publish.py --token <your-pypi-token> --yes
  3. 如果是交互模式，按提示输入 PyPI token（前缀 __token__）

首次发布前确认：
  - pyproject.toml 中 [project.urls] 填写正确的 GitHub 地址
  - PyPI 账户已注册：https://pypi.org/account/register/
  - 创建 API Token：https://pypi.org/manage/account/token/
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _load_env_token() -> str:
    """从 .env 文件或环境变量读取 PYPI_TOKEN。"""
    # 1. 环境变量
    env_token = os.environ.get("PYPI_TOKEN", "").strip()
    if env_token:
        return env_token

    # 2. .env 文件
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("PYPI_TOKEN="):
                return line[len("PYPI_TOKEN="):].strip().strip('"').strip("'")

    return ""


def run(cmd: list[str]) -> None:
    print(f"\n>>> {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="SciPlot Academic — PyPI 发布脚本")
    parser.add_argument("--token", help="PyPI API Token (前缀 pypi-)，也可通过 .env 或 PYPI_TOKEN 环境变量提供")
    parser.add_argument("--yes", "-y", action="store_true", help="跳过确认步骤，直接发布")
    args = parser.parse_args()

    # 优先级: --token > 环境变量 > .env 文件
    token = args.token or _load_env_token()

    # 清理旧构建产物
    for d in ["dist", "build"]:
        if Path(d).exists():
            shutil.rmtree(d)
            print(f"✓ 已清理 {d}/")

    # 构建
    run([sys.executable, "-m", "build"])
    print("\n✓ 构建完成，dist/ 目录：")
    for f in sorted(Path("dist").iterdir()):
        print(f"  {f.name}")

    dist_files = glob.glob("dist/*")
    if not dist_files:
        print("❌ dist/ 目录为空，构建可能失败")
        sys.exit(1)

    # 准备上传指令
    upload_cmd = [sys.executable, "-m", "twine", "upload"]
    if token:
        upload_cmd.extend(["-u", "__token__", "-p", token])

    upload_cmd.extend(dist_files)

    # 确认发布
    if args.yes:
        do_upload = True
    else:
        answer = input("\n是否上传到 PyPI？(y/N): ").strip().lower()
        do_upload = (answer == "y")

    if do_upload:
        run(upload_cmd)
        print("\n✅ 发布成功！")
        print("查看：https://pypi.org/project/sciplot-academic/")
    else:
        print("\n跳过上传。如需手动上传：python -m twine upload dist/*")


if __name__ == "__main__":
    main()
