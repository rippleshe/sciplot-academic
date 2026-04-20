#!/usr/bin/env python3
"""
SciPlot Academic — PyPI 发布脚本
===================================

使用前提：
  pip install build twine

步骤：
  1. 修改 pyproject.toml 中的 version
  2. 运行本脚本：python publish.py
  3. 按提示输入 PyPI token（前缀 __token__）

首次发布前确认：
  - pyproject.toml 中 [project.urls] 填写正确的 GitHub 地址
  - PyPI 账户已注册：https://pypi.org/account/register/
  - 创建 API Token：https://pypi.org/manage/account/token/
"""

import subprocess
import sys
import shutil
from pathlib import Path


def run(cmd: str) -> None:
    print(f"\n>>> {cmd}")
    result = subprocess.run(cmd, shell=True, check=False)
    if result.returncode != 0:
        print(f"❌ 命令失败，退出码 {result.returncode}")
        sys.exit(result.returncode)


def main():
    # 清理旧构建产物
    for d in ["dist", "build"]:
        if Path(d).exists():
            shutil.rmtree(d)
            print(f"✓ 已清理 {d}/")

    # 构建
    run("python -m build")
    print("\n✓ 构建完成，dist/ 目录：")
    for f in Path("dist").iterdir():
        print(f"  {f.name}")

    # 上传到 PyPI（输入 __token__ + API Token）
    answer = input("\n是否上传到 PyPI？(y/N): ").strip().lower()
    if answer == "y":
        run("python -m twine upload dist/*")
        print("\n✅ 发布成功！")
        print("查看：https://pypi.org/project/sciplot-academic/")
    else:
        print("\n跳过上传。如需手动上传：python -m twine upload dist/*")


if __name__ == "__main__":
    main()
