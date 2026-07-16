#!/usr/bin/env python3
"""
使用 twrpdtgen 命令行从 boot/recovery 镜像生成 TWRP 设备树
"""

import sys
import argparse
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="从 boot/recovery 镜像生成 TWRP 设备树 (调用 twrpdtgen 命令行)"
    )
    parser.add_argument("--image", required=True, help="boot.img 或 recovery.img 的路径")
    parser.add_argument("--output", required=True, help="输出目录")
    parser.add_argument("--manufacturer", required=True, help="设备制造商 (如: xiaomi)")
    parser.add_argument("--codename", required=True, help="设备代号 (如: beryllium)")
    parser.add_argument("--api-level", required=True, help="API 级别 (如 22)")

    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.is_file():
        print(f"错误: 镜像文件不存在: {args.image}")
        sys.exit(1)

    output_dir = Path(args.output) / args.manufacturer / args.codename
    output_dir.mkdir(parents=True, exist_ok=True)

    # 使用 python -m 方式调用 twrpdtgen
    cmd = [
        "python", "-m", "twrpdtgen",
        "-i", str(image_path),
        "-o", str(output_dir),
        "--manufacturer", args.manufacturer,
        "--codename", args.codename,
        "--api-level", args.api_level,
    ]

    print("运行命令:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ 生成失败!")
        print("错误输出:", result.stderr)
        sys.exit(result.returncode)
    else:
        print(result.stdout)
        print(f"✅ 设备树已成功生成: {output_dir}")

if __name__ == "__main__":
    main()
