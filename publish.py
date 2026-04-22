#!/usr/bin/env python3
"""
SciPlot Academic — PyPI 发布脚本
===================================

使用前提：
  uv add --dev build twine

步骤：
  1. 修改 pyproject.toml 中的 version
  2. 运行本脚本：python publish.py
  3. 按提示输入 PyPI token（前缀 __token__）

首次发布前确认：
  - pyproject.toml 中 [project.urls] 填写正确的 GitHub 地址
  - PyPI 账户已注册：https://pypi.org/account/register/
  - 创建 API Token：https://pypi.org/manage/account/token/
"""

import glob
import subprocess
import sys
import shutil
from pathlib import Path


def run(cmd: list[str]) -> None:
    print(f"\n>>> {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main():
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

    # 上传到 PyPI（输入 __token__ + API Token）
    answer = input("\n是否上传到 PyPI？(y/N): ").strip().lower()
    if answer == "y":
        run([sys.executable, "-m", "twine", "upload", *dist_files])
        print("\n✅ 发布成功！")
        print("查看：https://pypi.org/project/sciplot-academic/")
    else:
        print("\n跳过上传。如需手动上传：python -m twine upload dist/*")


if __name__ == "__main__":
    main()
