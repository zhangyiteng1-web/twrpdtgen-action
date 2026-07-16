#!/usr/bin/env python3
import sys
import argparse
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--api-level", required=True)
    parser.add_argument("--manufacturer", required=False)
    parser.add_argument("--codename", required=False)

    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.is_file():
        print(f"错误: 镜像文件不存在: {args.image}")
        sys.exit(1)

    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)

    # 使用等号语法，避免参数解析歧义
    cmd = [
        "python", "-m", "twrpdtgen",
        "-o", str(output_root),
        f"--api-level={args.api_level}",
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
        print(f"✅ 设备树已成功生成在 {output_root}")

if __name__ == "__main__":
    main()
