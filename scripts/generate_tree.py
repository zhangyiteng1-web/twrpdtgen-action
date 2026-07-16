#!/usr/bin/env python3
"""
使用 twrpdtgen Python API 从 boot/recovery 镜像生成 TWRP 设备树
手动补全 build.prop 中缺失的属性（如 first_api_level）
"""

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
        description="从 boot/recovery 镜像生成 TWRP 设备树 (Python API)"
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

    print(f"正在处理镜像: {image_path}")
    print(f"输出目录: {output_dir}")

    try:
        # 1. 创建 DeviceTree 对象（自动解析镜像）
        device_tree = DeviceTree(image_path)

        # 2. 获取内部 build.prop 字典
        build_prop = device_tree.build_prop

        # 3. 强制设置制造商和代号（防止自动识别错误）
        build_prop['ro.product.manufacturer'] = args.manufacturer
        build_prop['ro.product.vendor.manufacturer'] = args.manufacturer
        build_prop['ro.product.device'] = args.codename
        build_prop['ro.product.name'] = args.codename
        build_prop['ro.product.vendor.device'] = args.codename

        # 4. 如果缺少 first_api_level，使用用户提供的值
        if 'ro.product.first_api_level' not in build_prop:
            print(f"build.prop 缺少 ro.product.first_api_level，手动添加为 {args.api_level}")
            build_prop['ro.product.first_api_level'] = args.api_level

        # 5. 生成设备树文件
        device_tree.dump_to_folder(output_dir)
        print(f"✅ 设备树已成功生成: {output_dir}")

    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
