#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# ========== Monkey patch DeviceInfo.get_first_prop ==========
from sebaubuntu_libs.libandroid.device_info import DeviceInfo

_global_api_level = None
_global_manufacturer = 'unknown'
_global_codename = 'unknown'

def patched_get_first_prop(self, props, *args, **kwargs):
    if not isinstance(props, (list, tuple)):
        props = [props]
    for prop in props:
        if prop in self.build_prop:
            return self.build_prop[prop]
    for prop in props:
        prop_lower = prop.lower()
        if 'security_patch' in prop_lower:
            return '2024-01-01'
        if 'abi' in prop_lower:
            return 'arm64-v8a,armeabi-v7a,armeabi'
        if 'manufacturer' in prop_lower:
            return _global_manufacturer
        if 'device' in prop_lower or 'name' in prop_lower or 'model' in prop_lower:
            return _global_codename
        if 'api_level' in prop_lower or 'sdk' in prop_lower:
            return _global_api_level
        if 'description' in prop_lower or 'display.id' in prop_lower:
            return f"{_global_codename}-user {_global_api_level}.0.0 release-keys"
    return ''

DeviceInfo.get_first_prop = patched_get_first_prop

# ========== Monkey patch DeviceTree.__init__ 处理 fstab 缺失 ==========
from twrpdtgen.device_tree import DeviceTree
from sebaubuntu_libs.libandroid.fstab import Fstab

original_device_tree_init = DeviceTree.__init__

def patched_device_tree_init(self, image):
    try:
        original_device_tree_init(self, image)
    except AssertionError as e:
        if str(e) == "fstab not found":
            self.fstab = Fstab()
            if not hasattr(self.fstab, 'entries'):
                self.fstab.entries = []
            from twrpdtgen.device_tree import INIT_RC_LOCATIONS
            self.init_rcs = []
            for init_rc_path in [self.image_info.ramdisk / location for location in INIT_RC_LOCATIONS]:
                if not init_rc_path.is_dir():
                    continue
                self.init_rcs += [init_rc for init_rc in init_rc_path.iterdir()
                                  if init_rc.name.endswith(".rc") and init_rc.name != "init.rc"]
            return
        else:
            raise

DeviceTree.__init__ = patched_device_tree_init
# ==========================================================================

def main():
    global _global_api_level, _global_manufacturer, _global_codename
    parser = argparse.ArgumentParser(
        description="从 boot/recovery 镜像生成 TWRP 设备树（自动处理缺失属性）"
    )
    parser.add_argument("--image", required=True, help="boot.img 或 recovery.img 路径")
    parser.add_argument("--output", required=True, help="输出根目录")
    parser.add_argument("--api-level", required=True, help="API 级别（如 22）")
    parser.add_argument("--manufacturer", required=True, help="设备制造商")
    parser.add_argument("--codename", required=True, help="设备代号")

    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.is_file():
        print(f"错误: 镜像文件不存在: {args.image}")
        sys.exit(1)

    _global_api_level = args.api_level
    _global_manufacturer = args.manufacturer
    _global_codename = args.codename
    print(f"使用的 API 级别: {_global_api_level}")
    print(f"制造商: {_global_manufacturer}, 代号: {_global_codename}")

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
