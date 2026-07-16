#!/usr/bin/env python3
"""
使用 twrpdtgen 从 boot/recovery 镜像生成 TWRP 设备树
"""

import os
import sys
import argparse
from pathlib import Path

try:
    from twrpdtgen.device_tree import DeviceTree
except ImportError:
    print("错误: 请先安装 twrpdtgen: pip install twrpdtgen")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="从 boot/recovery 镜像生成 TWRP 设备树"
    )
    parser.add_argument(
        "--image",
        required=True,
        help="boot.img 或 recovery.img 的路径"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="输出目录"
    )
    parser.add_argument(
        "--manufacturer",
        required=True,
        help="设备制造商 (如: xiaomi)"
    )
    parser.add_argument(
        "--codename",
        required=True,
        help="设备代号 (如: beryllium)"
    )

    args = parser.parse_args()

    # 检查镜像文件是否存在
    if not os.path.exists(args.image):
        print(f"错误: 镜像文件不存在: {args.image}")
        sys.exit(1)

    # 构建输出路径: output/manufacturer/codename
    output_path = Path(args.output) / args.manufacturer / args.codename
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"正在处理镜像: {args.image}")
    print(f"输出目录: {output_path}")

    try:
        # 创建 DeviceTree 对象并生成设备树
        device_tree = DeviceTree(args.image)
        device_tree.dump_to_folder(str(output_path))
        print(f"✅ 设备树已成功生成: {output_path}")
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
