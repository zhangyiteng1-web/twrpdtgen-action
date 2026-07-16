#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# ========== Monkey patch DeviceInfo 以处理缺失的属性 ==========
from sebaubuntu_libs.libandroid.device_info import DeviceInfo

_PATCH_API_LEVEL = None
_PATCH_MANUFACTURER = None
_PATCH_CODENAME = None

original_device_info_init = DeviceInfo.__init__

def patched_device_info_init(self, build_prop):
    global _PATCH_API_LEVEL, _PATCH_MANUFACTURER, _PATCH_CODENAME
    
    # 补全所有可能缺失的属性
    if _PATCH_API_LEVEL is not None:
        build_prop['ro.product.first_api_level'] = str(_PATCH_API_LEVEL)
    if _PATCH_MANUFACTURER is not None:
        build_prop['ro.product.manufacturer'] = _PATCH_MANUFACTURER
        build_prop['ro.product.vendor.manufacturer'] = _PATCH_MANUFACTURER
        build_prop['ro.product.system.manufacturer'] = _PATCH_MANUFACTURER
        build_prop['ro.product.board'] = _PATCH_MANUFACTURER  # 某些版本可能需要
    if _PATCH_CODENAME is not None:
        build_prop['ro.product.device'] = _PATCH_CODENAME
        build_prop['ro.product.vendor.device'] = _PATCH_CODENAME
        build_prop['ro.product.system.device'] = _PATCH_CODENAME
        build_prop['ro.product.name'] = _PATCH_CODENAME
        build_prop['ro.product.vendor.name'] = _PATCH_CODENAME
        build_prop['ro.product.system.name'] = _PATCH_CODENAME
        build_prop['ro.product.model'] = _PATCH_CODENAME  # 有时用 model
        build_prop['ro.product.vendor.model'] = _PATCH_CODENAME
    
    # 调用原始初始化
    original_device_info_init(self, build_prop)

DeviceInfo.__init__ = patched_device_info_init

# 现在再导入 DeviceTree
from twrpdtgen.device_tree import DeviceTree
# ==========================================================================

def main():
    global _PATCH_API_LEVEL, _PATCH_MANUFACTURER, _PATCH_CODENAME
    parser = argparse.ArgumentParser(
        description="从 boot/recovery 镜像生成 TWRP 设备树（自动处理缺失属性）"
    )
    parser.add_argument("--image", required=True, help="boot.img 或 recovery.img 路径")
    parser.add_argument("--output", required=True, help="输出根目录")
    parser.add_argument("--api-level", required=False, default=None,
                        help="API 级别（如 22），不提供则默认 22")
    parser.add_argument("--manufacturer", required=True, help="设备制造商")
    parser.add_argument("--codename", required=True, help="设备代号")

    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.is_file():
        print(f"错误: 镜像文件不存在: {args.image}")
        sys.exit(1)

    # 设置全局变量供 patch 使用
    _PATCH_API_LEVEL = args.api_level if args.api_level else '22'
    _PATCH_MANUFACTURER = args.manufacturer
    _PATCH_CODENAME = args.codename
    print(f"使用的 API 级别: {_PATCH_API_LEVEL}")
    print(f"制造商: {_PATCH_MANUFACTURER}, 代号: {_PATCH_CODENAME}")

    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)

    try:
        device_tree = DeviceTree(image_path)
        output_path = device_tree.dump_to_folder(output_root, git=False)
        print(f"✅ 设备树已成功生成在: {output_path}")
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
