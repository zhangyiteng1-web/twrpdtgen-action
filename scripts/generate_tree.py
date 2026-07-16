#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# ========== Monkey patch DeviceInfo 以处理缺失的属性 ==========
from sebaubuntu_libs.libandroid.device_info import DeviceInfo

_PATCH_API_LEVEL = None
_PATCH_MANUFACTURER = None
_PATCH_CODENAME = None

def get_default_props(api_level, manufacturer, codename):
    """生成可能缺失的 build.prop 属性默认值"""
    desc = f"{codename}-user {api_level}.0.0 release-keys"
    defaults = {
        # 制造商
        'ro.product.manufacturer': manufacturer,
        'ro.product.vendor.manufacturer': manufacturer,
        'ro.product.system.manufacturer': manufacturer,
        'ro.product.board': manufacturer,
        # 代号
        'ro.product.device': codename,
        'ro.product.vendor.device': codename,
        'ro.product.system.device': codename,
        'ro.product.name': codename,
        'ro.product.vendor.name': codename,
        'ro.product.system.name': codename,
        'ro.product.model': codename,
        'ro.product.vendor.model': codename,
        'ro.product.system.model': codename,
        # API
        'ro.product.first_api_level': str(api_level),
        'ro.build.version.sdk': str(api_level),
        # 描述（不设置 fingerprint，避免解析错误）
        'ro.build.description': desc,
        'ro.system.build.description': desc,
        'ro.vendor.build.description': desc,
        'ro.build.display.id': desc,
        'ro.system.build.display.id': desc,
        'ro.vendor.build.display.id': desc,
        # 其他
        'ro.build.version.release': str(api_level),
        'ro.build.date': 'Mon Jan 1 00:00:00 UTC 2024',
        'ro.build.date.utc': '1704067200',
        'ro.build.type': 'user',
        'ro.build.user': 'android-build',
        'ro.build.host': 'android-host',
        'ro.build.tags': 'release-keys',
        'ro.system.build.version.sdk': str(api_level),
        'ro.system.build.version.release': str(api_level),
        'ro.vendor.build.version.sdk': str(api_level),
        'ro.vendor.build.version.release': str(api_level),
    }
    return defaults

original_device_info_init = DeviceInfo.__init__

def patched_device_info_init(self, build_prop):
    global _PATCH_API_LEVEL, _PATCH_MANUFACTURER, _PATCH_CODENAME
    
    defaults = get_default_props(_PATCH_API_LEVEL, _PATCH_MANUFACTURER, _PATCH_CODENAME)
    for key, value in defaults.items():
        if key not in build_prop:
            build_prop[key] = value
    
    original_device_info_init(self, build_prop)

DeviceInfo.__init__ = patched_device_info_init

# 现在导入 DeviceTree
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
