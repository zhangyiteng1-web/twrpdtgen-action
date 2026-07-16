#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# ========== Monkey patch: 让 get_first_prop 在属性缺失时返回默认值 ==========
from sebaubuntu_libs.libandroid.device_info import DeviceInfo

_global_api_level = '22'
_global_manufacturer = 'unknown'
_global_codename = 'unknown'

# 保存原始方法
original_get_first_prop = DeviceInfo.get_first_prop

def patched_get_first_prop(self, props):
    """如果属性不存在，返回合理的默认值，而不是抛出异常"""
    if not isinstance(props, (list, tuple)):
        props = [props]
    for prop in props:
        if prop in self.build_prop:
            return self.build_prop[prop]
    # 属性缺失，根据属性名生成默认值
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
        # 其他未知属性返回空字符串
        return ''
    return ''

DeviceInfo.get_first_prop = patched_get_first_prop

# 现在导入 DeviceTree
from twrpdtgen.device_tree import DeviceTree
# ==========================================================================

def main():
    global _global_api_level, _global_manufacturer, _global_codename
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

    _global_api_level = args.api_level if args.api_level else '22'
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
