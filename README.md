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
output/
└── realme/
└── RMX3031CN/
├── Android.bp
├── Android.mk
├── AndroidProducts.mk
├── BoardConfig.mk
├── README.md
├── device.mk
├── extract-files.sh
├── omni_RMX3031CN.mk
├── recovery.fstab
├── setup-makefiles.sh
├── vendorsetup.sh
├── prebuilt/
│ └── kernel # 若存在
└── recovery/
└── root/
└── *.rc # init 脚本
这些文件可直接用于 TWRP 编译。

---

## 配置独立仓库推送（可选）

若想将生成的设备树自动推送到另一个仓库（如 `android_device_xiaomi_beryllium`），需要额外配置：

1. **生成 Personal Access Token (classic)**：
   - GitHub Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
   - 勾选 `repo` 权限，生成并复制 Token。

2. **添加到 Secrets**：
   - 在**本仓库**的 Settings → Secrets and variables → Actions 中，添加一个 Repository secret：
     - Name: `GH_PAT`
     - Secret: 粘贴你的 Token。

3. **运行 Workflow 时**：
   - 勾选 `push_to_repo`
   - 在 `repo_name` 中填写目标仓库名称（如 `android_device_xiaomi_beryllium`），该仓库应**预先创建**（可为空）。

---

## 注意事项

- **镜像大小**：GitHub Actions 免费仓库有存储限制，建议镜像不超过 50MB，若过大可考虑压缩或使用其他云存储。
- **运行时限制**：每个 Action 运行时间不超过 6 小时，通常足够完成生成。
- **API 级别**：务必正确填写，否则可能影响生成的设备树兼容性。可参考 [Android 版本对照表](https://source.android.com/docs/setup/start/build-numbers)。
- **fstab 缺失**：部分镜像可能不包含 `recovery.fstab`，脚本会自动创建空 fstab，您可能需要后续手动补充。
- **内核提取**：若镜像包含内核，会自动复制到 `prebuilt/kernel`；若不包含，则需手动添加。
- **强制推送**：若启用独立仓库推送，原仓库内容会被 **强制覆盖**（`git push -f`），建议使用空仓库或备份。

---

## 常见问题

**Q: 生成失败，提示 `fstab not found`？**  
A: 脚本已自动处理，会生成占位 fstab，但仍建议你根据设备实际分区手动完善 `recovery.fstab`。

**Q: 为什么我的 Android 13 镜像生成失败？**  
A: 脚本已通过 monkey patch 兼容 Android 13 缺失的属性（如 `security_patch`、`cpu.abilist` 等）。若仍报错，请提 Issue 并附上完整日志。

**Q: 下载镜像很慢或失败？**  
A: 已使用 `aria2` 多线程下载，并启用断点续传。如果持续失败，尝试更换直链（如使用 GitHub Releases 或 CloudFlare R2）。

**Q: 生成后的设备树还需要修改吗？**  
A: 可能需要根据实际情况调整 `BoardConfig.mk` 中的分区大小、内核配置等，但基础框架已完备。

---

## 致谢 & 许可证

- 本项目基于 [twrpdtgen](https://github.com/twrpdtgen/twrpdtgen) 开发，感谢原作者的优秀工作。
- 遵循 [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) 许可证。

---

## 贡献

欢迎提交 Issue 或 PR，帮助改进本项目。若发现新问题或有改进建议，请反馈。

---
Enjoy! 🎉
