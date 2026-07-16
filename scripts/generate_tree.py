#!/usr/bin/env python3
"""
使用 twrpdtgen 命令行生成 TWRP 设备树
"""

import sys
import argparse
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="从 boot/recovery 镜像生成 TWRP 设备树（调用 twrpdtgen 命令行）"
    )
    parser.add_argument("--image", required=True, help="boot.img 或 recovery.img 的路径")
    parser.add_argument("--output", required=True, help="输出根目录（twrpdtgen 会自动创建 manufacturer/codename 子目录）")
    parser.add_argument("--api-level", required=True, help="API 级别（如 22）")
    # 制造商和代号不再需要，twrpdtgen 会自动从镜像中提取
    parser.add_argument("--manufacturer", required=False, help="（忽略，仅作兼容）")
    parser.add_argument("--codename", required=False, help="（忽略，仅作兼容）")

    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.is_file():
        print(f"错误: 镜像文件不存在: {args.image}")
        sys.exit(1)

    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)

    # 构建 twrpdtgen 命令：只使用 -o 和 --api-level，位置参数为镜像
    cmd = [
        "python", "-m", "twrpdtgen",
        "-o", str(output_root),
        "--api-level", args.api_level,
        str(image_path)
    ]

    print("运行命令:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ 生成失败!")
        print("错误输出:", result.stderr)
        sys.exit(result.returncode)
    else:
        print(result.stdout)
        print(f"✅ 设备树已成功生成在 {output_root} 下的子目录中")

if __name__ == "__main__":
    main()
