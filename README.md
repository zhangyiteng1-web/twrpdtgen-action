# TWRP Device Tree Generator Action

通过 GitHub Actions 自动使用 [twrpdtgen](https://github.com/twrpdtgen/twrpdtgen) 从 `boot.img` / `recovery.img` 提取 TWRP 兼容设备树。

**项目特点**：  
- 🚀 全云端运行，无需本地环境  
- 📦 支持 Android 4.4 至 13+（API 19 ~ 33+）  
- 🔧 自动处理缺失的 `build.prop` 属性（如 `first_api_level`、`security_patch`、`cpu.abilist` 等）  
- 🩹 若镜像中缺少 `recovery.fstab`，自动创建 fallback，保证生成流程不中断  
- 📥 结果可作为 Artifact 下载，也可自动发布为 Release，或推送到独立仓库  
- ⚡ 使用 `aria2` 多线程下载，断点续传，下载更稳定  

---

## 使用方法

### 1. Fork 本仓库
点击右上角的 **Fork** 按钮，将仓库复制到你自己的 GitHub 账号下。

### 2. 准备镜像文件
获取你设备的 `boot.img` 或 `recovery.img`：
- 若设备为 **A/B 分区**，通常应使用 `boot.img`；
- 若为 **非 A/B 分区**，则使用 `recovery.img`。

将镜像上传到可直链下载的位置，例如：
- 上传到本仓库（然后点击文件 → **Raw** 获取直链）
- 使用 GitHub Releases、MEGA、Google Drive 等（需确保链接可直接下载）

### 3. 运行 Workflow
1. 进入你的仓库，点击 **Actions** 选项卡
2. 在左侧选择 **Generate TWRP Device Tree**
3. 点击右侧的 **Run workflow** 按钮
4. 填写以下参数（必填项带 *）：

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `image_url` | ✅ | 镜像文件的直链下载地址 | `https://example.com/recovery.img` |
| `device_manufacturer` | ✅ | 设备制造商（小写） | `xiaomi` / `realme` |
| `device_codename` | ✅ | 设备代号（小写） | `beryllium` / `RMX3031CN` |
| `api_level` | ❌ | API 级别，默认 `22`（Android 5.1） | `33` (Android 13) |
| `push_to_repo` | ❌ | 是否推送到独立仓库（需勾选并填写 `repo_name`） | 勾选/不勾选 |
| `repo_name` | ❌ | 目标仓库名称（如 `android_device_xiaomi_beryllium`） | 仅在 `push_to_repo` 勾选时有效 |

5. 点击 **Run workflow** 开始运行。

### 4. 获取结果
运行完成后，生成的文件会通过以下方式提供：

- **Artifact**：在 Actions 运行页面底部，点击 `device-tree-<codename>` 下载 ZIP 包。
- **Release**（若未启用推送）：在仓库的 **Releases** 页面会创建一个新 Release，包含生成的设备树。
- **独立仓库**（若启用推送）：设备树会被强制推送到你指定的仓库（`git push -f`），方便直接 clone 用于编译。

---

## 目录结构（生成结果示例）
