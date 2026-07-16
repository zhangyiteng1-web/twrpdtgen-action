#!/usr/bin/env python3
import sys
import argparse
import os
from pathlib import Path

# ========== Monkey patch DeviceInfo 以处理缺失的 first_api_level ==========
from sebaubuntu_libs.libandroid.device_info import DeviceInfo

_PATCH_API_LEVEL = None

original_device_info_init = DeviceInfo.__init__

def patched_device_info_init(self, build_prop):
    global _PATCH_API_LEVEL
    # 如果 build.prop 缺少 ro.product.first_api_level，则用指定的值补上
    if 'ro.product.first_api_level' not in build_prop:
        if _PATCH_API_LEVEL is not None:
            build_prop['ro.product.first_api_level'] = str(_PATCH_API_LEVEL)
        else:
            # 若未提供，默认使用 22（Android 5.1）
            build_prop['ro.product.first_api_level'] = '22'
    # 调用原始初始化
    original_device_info_init(self, build_prop)

DeviceInfo.__init__ = patched_device_info_init

# 现在再导入 DeviceTree（此时 DeviceInfo 已被 patch）
from twrpdtgen.device_tree import DeviceTree
# ==========================================================================

def main():
    global _PATCH_API_LEVEL
    parser = argparse.ArgumentParser(
        description="从 boot/recovery 镜像生成 TWRP 设备树（自动处理缺失 API 级别）"
    )
    parser.add_argument("--image", required=True, help="boot.img 或 recovery.img 路径")
    parser.add_argument("--output", required=True, help="输出根目录")
    parser.add_argument("--api-level", required=False, default=None,
                        help="API 级别（如 22），不提供则默认 22")
    # 保留 manufacturer 和 codename 参数以兼容 workflow，但本脚本不使用
    parser.add_argument("--manufacturer", required=False)
    parser.add_argument("--codename", required=False)

    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.is_file():
        print(f"错误: 镜像文件不存在: {args.image}")
        sys.exit(1)

    # 设置 API 级别（若未指定则默认 22）
    _PATCH_API_LEVEL = args.api_level if args.api_level else '22'
    print(f"使用的 API 级别: {_PATCH_API_LEVEL}")

    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)

    try:
        # 创建 DeviceTree 实例（会自动解包镜像、读取 build.prop）
        device_tree = DeviceTree(image_path)

        # 生成设备树到指定目录
        output_path = device_tree.dump_to_folder(output_root, git=False)
        print(f"✅ 设备树已成功生成在: {output_path}")
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
