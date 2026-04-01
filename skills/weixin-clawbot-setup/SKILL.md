---
name: weixin-clawbot-setup
description: 微信 ClawBot 插件配置指南。帮助用户在 OpenClaw 中配置微信 ClawBot 插件，实现通过微信与 OpenClaw 对话。触发词：微信ClawBot配置、微信插件安装、微信扫码绑定、openclaw-weixin。
---

# 微信 ClawBot 配置技能

## 概述

本技能帮助用户在 OpenClaw 中配置微信 ClawBot 插件，实现通过微信与 OpenClaw 进行对话。

## 前置条件

- OpenClaw 已安装并正常运行
- 手机上安装了微信
- OpenClaw Gateway 正在运行

## 微信版本要求

### iOS 微信

| 要求 | 说明 |
|------|------|
| **最低版本** | 8.0.70 及以上 |
| **推荐版本** | 最新版本 |
| **支持状态** | ✅ 完全支持 |

### Android 微信

| 要求 | 说明 |
|------|------|
| **最低版本** | 8.0.70 及以上（需等待官方逐步放量） |
| **推荐版本** | 最新版本 |
| **支持状态** | ✅ 支持（部分功能可能受限） |

**Android 用户注意**：
- 截至 2026 年 3 月，8.0.70 版本仅对 iOS 端开放，安卓用户需要等待官方逐步放量
- 如果没有插件权限，可以通过运行安装命令后扫码获得插件入口
- 未更新微信版本的安卓用户，每次关闭后需要重新扫码连接

### 鸿蒙微信

| 平台 | 版本 | 支持状态 | 备注 |
|------|------|----------|------|
| **鸿蒙双框** | HarmonyOS 5.0 以下 | ✅ 支持 | 兼容模式，类似 Android |
| **鸿蒙单框** | HarmonyOS 5.0 及以上 | ❌ 不支持 | 微信鸿蒙原生版，暂不支持 |

**版本说明**：
- **鸿蒙双框**：HarmonyOS 5.0 以下版本（4.x 及更早），微信以兼容模式运行（类似 Android），支持 ClawBot
- **鸿蒙单框**：HarmonyOS 5.0 及以上版本，微信为鸿蒙原生应用，目前暂不支持 ClawBot

## 微信版本支持总览

| 平台 | 版本要求 | 支持状态 | 备注 |
|------|----------|----------|------|
| **iOS** | 8.0.70+ | ✅ 完全支持 | 推荐使用 |
| **Android** | 8.0.70+ | ✅ 支持 | 需等待官方放量 |
| **鸿蒙双框** | HarmonyOS 5.0 以下 | ✅ 支持 | 兼容模式 |
| **鸿蒙单框** | HarmonyOS 5.0+ | ❌ 不支持 | 暂不支持 |

## 配置步骤

⚠️ **重要提示**：以下步骤必须在**同一个会话中连续完成**，中途不要结束对话，否则可能导致配置不生效！
⚠️ **重要提示**：如果安装过程要重启gateway，一定要明确提示用户，我要重启gateway，连接可能断开，如果断开，请稍后继续追问微信channel安装进展

### 步骤一：更新微信版本

⚠️ **重要**：请先确保微信已更新到最新版本（iOS 需要 8.0.70 及以上）。

- **iOS**：App Store → 搜索「微信」→ 更新
- **Android**：应用商店 → 搜索「微信」→ 更新

### 步骤二：安装/登录微信插件

根据你的情况选择合适的命令：

#### 场景 A：首次安装（插件未安装）

如果插件目录 `~/.openclaw/extensions/openclaw-weixin/` 不存在，执行：

```bash
npx -y @tencent-weixin/openclaw-weixin-cli@latest install
```

等待安装完成，终端会显示一个二维码链接。

#### 场景 B：已安装插件，需要登录/重新登录

如果插件已安装，**优先使用 `login` 命令**，避免重复安装导致 Gateway 重启：

```bash
openclaw channels login --channel openclaw-weixin
```

或者使用 CLI 工具：

```bash
npx -y @tencent-weixin/openclaw-weixin-cli@latest login
```

⚠️ **重要**：
- **已安装插件后，请使用 `login` 命令生成二维码**，不要重复使用 `install`
- `login` 命令不会触发插件重新安装，避免不必要的 Gateway 重启

#### 登录流程执行规范

当执行 `login` 命令时，Agent 必须遵循以下规范：

1. **同时发送 HTTP 链接和二维码截图**：
   - 命令输出中会包含二维码链接（格式：`https://liteapp.weixin.qq.com/q/...`）
   - **提取 HTTP 链接发送给用户**，不要发送 ASCII 二维码图案
   - **使用浏览器打开链接并截图**，将二维码图片一同发送给用户
   - 链接格式示例：`https://liteapp.weixin.qq.com/q/7GiQu1?qrcode=xxx&bot_type=3`

2. **等待用户扫码完成**：
   - 执行 `login` 命令后，命令会阻塞等待用户扫码
   - **不要结束对话**，保持会话直到命令返回结果
   - 命令成功返回后，会显示类似 `✅ Login confirmed!` 的提示

3. **扫码成功后立即执行后续步骤**：
   - 检查凭证是否保存：`cat ~/.openclaw/openclaw-weixin/accounts.json`
   - 检查插件是否启用：`cat ~/.openclaw/openclaw.json | grep -A 5 "openclaw-weixin"`
   - 如未启用，立即编辑配置文件启用插件
   - 重启 Gateway：`openclaw gateway restart`
   - 验证连接：`openclaw channels list`

**执行步骤**：

```bash
# 1. 执行 login 命令
openclaw channels login --channel openclaw-weixin

# 2. 从输出中提取二维码链接（格式：https://liteapp.weixin.qq.com/q/...）

# 3. 使用浏览器打开链接并截图
# browser action=open url=<二维码链接>
# browser action=screenshot

# 4. 同时发送链接和截图给用户
# send_file_to_user fileLocalUrls=[截图路径]
# 并在消息中包含 HTTP 链接
```

**示例回复格式**：

```
**微信授权登录二维码：**

🔗 https://liteapp.weixin.qq.com/q/7GiQu1?qrcode=xxx&bot_type=3

[同时发送二维码截图图片]

---

正在等待你扫码完成...扫码成功后请告诉我。
```

### 步骤三：微信扫码绑定

1. 打开手机微信
2. 点击右上角「+」→「扫一扫」
3. 扫描终端显示的二维码或点击二维码链接
4. 在微信中确认绑定
5. 等待终端显示「绑定成功」提示

⚠️ **关键**：扫码成功后，**不要结束当前对话**，立即继续执行后续步骤！

### 步骤四：启用插件配置

⚠️ **关键步骤**：扫码成功后，**立即**在 OpenClaw 配置文件中启用插件！

1. **编辑配置文件**：
   ```bash
   nano ~/.openclaw/openclaw.json
   ```
   或使用其他编辑器（vim、code 等）

2. **找到 `plugins.entries` 部分**，添加 `openclaw-weixin` 配置：
   ```json
   "plugins": {
     "entries": {
       "cspl_hook": {
         "enabled": true
       },
       "openclaw-weixin": {
         "enabled": true
       },
       "xiaoyi-channel": {
         "enabled": true
       }
     },
     ...
   }
   ```

3. **保存文件并退出**

4. **验证配置已添加**：
   ```bash
   cat ~/.openclaw/openclaw.json | grep -A 5 "openclaw-weixin"
   ```
   应该看到：
   ```json
   "openclaw-weixin": {
     "enabled": true
   },
   ```

### 步骤五：重启 Gateway

⚠️ **关键步骤**：修改配置后，**立即**重启 Gateway！

```bash
openclaw gateway restart
```

或者：

```bash
openclaw gateway stop
openclaw gateway
```

### 步骤六：验证连接

**立即**检查微信插件是否配置成功：

```bash
openclaw channels list
```

输出应包含：

```
Chat channels:
- openclaw-weixin <account-id>: configured, enabled
```

### 步骤七：验证消息监控启动

**立即**检查日志，确认消息监控已启动：

```bash
tail -100 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | grep -i "monitor started"
```

应该看到类似：
```
weixin monitor started (https://ilinkai.weixin.qq.com, account=xxx)
[xxx] Monitor started: baseUrl=https://ilinkai.weixin.qq.com timeoutMs=35000
```

### 步骤八：测试对话

1. 在微信中找到「ClawBot」或绑定的公众号/小程序
2. 发送一条消息，例如「你好」
3. 等待 OpenClaw 回复

✅ **配置完成！** 如果以上步骤都成功，微信 ClawBot 就可以正常使用了。

---

## ⚠️ 常见失败原因

**失败场景**：扫码成功 → 对话结束 → 没有后续操作 → 插件未启用 → 微信无响应

**成功场景**：扫码成功 → **同一会话中立即执行**启用插件 → 重启 Gateway → 验证 → 测试成功

**一句话总结**：扫码成功后，必须在**同一会话中连续完成**「启用插件 → 重启 Gateway → 验证」三步，否则不会生效！

## 微信界面操作说明

### 扫码绑定

1. 打开微信 → 右上角「+」→「扫一扫」
2. 扫描二维码后，会显示绑定确认页面
3. 点击「确认绑定」或「关注」
4. 绑定成功后，会出现新的对话窗口

### 发送消息

1. 在微信聊天列表中找到 ClawBot 对话
2. 像普通聊天一样发送消息
3. OpenClaw 会自动回复

## 小艺 Claw 窗口操作说明

### 首次安装插件

```bash
npx -y @tencent-weixin/openclaw-weixin-cli@latest install
```

### 生成登录二维码（已安装插件后使用）

```bash
# 推荐：使用 OpenClaw 命令
openclaw channels login --channel openclaw-weixin

# 或使用 CLI 工具
npx -y @tencent-weixin/openclaw-weixin-cli@latest login
```

⚠️ **重要**：插件已安装后，请使用 `login` 命令生成二维码，不要重复使用 `install`。

### 查看插件状态

```bash
openclaw channels list
```

### 重启 Gateway

```bash
openclaw gateway restart
```

### 查看日志

```bash
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log
```

### 查看凭证文件

```bash
ls -la ~/.openclaw/openclaw-weixin/
cat ~/.openclaw/openclaw-weixin/accounts.json
```

## 常见问题 Q&A

### Q1: 扫码成功但微信没有回复？

**原因**：Gateway 没有重启，新的凭证没有加载。

**解决方案**：
```bash
openclaw gateway restart
```

### Q2: `openclaw channels list` 中没有 openclaw-weixin？

**原因**：凭证文件不存在或格式错误。

**解决方案**：
1. 检查凭证文件是否存在：
   ```bash
   ls -la ~/.openclaw/openclaw-weixin/accounts.json
   ```
2. 如果不存在，重新运行安装命令：
   ```bash
   npx -y @tencent-weixin/openclaw-weixin-cli@latest install
   ```
3. 扫码后重启 Gateway

### Q3: 二维码过期了怎么办？

**解决方案**：使用 `login` 命令重新生成二维码：
```bash
openclaw channels login --channel openclaw-weixin
```

或：
```bash
npx -y @tencent-weixin/openclaw-weixin-cli@latest login
```

⚠️ **注意**：如果插件已安装，请使用 `login` 命令，不要使用 `install`。

### Q4: Gateway 启动失败？

**原因**：端口被占用或权限问题。

**解决方案**：
1. 检查是否有其他 Gateway 进程：
   ```bash
   ps aux | grep openclaw
   ```
2. 杀掉旧进程：
   ```bash
   kill -9 <pid>
   ```
3. 重新启动：
   ```bash
   openclaw gateway
   ```

### Q5: 如何取消绑定？

**解决方案**：
1. 删除凭证文件：
   ```bash
   rm -rf ~/.openclaw/openclaw-weixin/
   ```
2. 重启 Gateway：
   ```bash
   openclaw gateway restart
   ```
3. 在微信中取消关注或删除对话

### Q6: 提示「Unsupported channel: openclaw-weixin」？

**原因**：插件没有正确安装。

**解决方案**：
1. 重新安装插件：
   ```bash
   npx -y @tencent-weixin/openclaw-weixin-cli@latest install
   ```
2. 检查插件目录：
   ```bash
   ls -la ~/.openclaw/extensions/openclaw-weixin/
   ```

### Q7: 如何查看详细的错误日志？

**解决方案**：
```bash
tail -100 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | grep -i "weixin\|error"
```

### Q8: 多个微信账号如何切换？

**解决方案**：
1. 查看已绑定的账号：
   ```bash
   cat ~/.openclaw/openclaw-weixin/accounts.json
   ```
2. 删除不需要的账号凭证：
   ```bash
   rm ~/.openclaw/openclaw-weixin/accounts/<account-id>.json
   ```
3. 更新 accounts.json 文件
4. 重启 Gateway

### Q9: 鸿蒙单框微信（HarmonyOS 5.0+）无法使用？

**原因**：鸿蒙单框微信是鸿蒙原生应用，目前 ClawBot 暂不支持。

**解决方案**：
- 等待后续更新支持
- 或使用其他设备（iOS/Android/鸿蒙双框）进行绑定

### Q10: iOS 微信扫码后提示「无法打开页面」？

**原因**：网络问题或微信版本过旧。

**解决方案**：
1. 更新微信到最新版本（至少 8.0.70）
2. 检查网络连接
3. 尝试使用蜂窝网络或切换 Wi-Fi

### Q11: Android 用户没有插件权限怎么办？

**原因**：插件仍在逐步放量中，部分用户暂未获得权限。

**解决方案**：
1. 直接运行安装命令：
   ```bash
   npx -y @tencent-weixin/openclaw-weixin-cli@latest install
   ```
2. 扫码连接后，微信会收到更新提示
3. 更新完成后，手机微信会出现「微信ClawBot」插件
4. 再次扫码完成连接

**注意**：未更新微信版本的安卓用户，每次关闭后需要重新扫码连接。

### Q12: 微信版本低于 8.0.70 能用吗？

**答案**：**不能**。

微信 ClawBot 插件需要微信 8.0.70 及以上版本才能使用。请先更新微信到最新版本。

### Q13: 一个微信号可以连接多个 OpenClaw 吗？

**答案**：**不能**。

一个微信号只能连接一个 OpenClaw 实例，但一个 OpenClaw 可以同时连接多个微信号。

### Q14: ClawBot 支持哪些消息类型？

| 消息类型 | 接收 | 发送 |
|----------|------|------|
| 文本消息 | ✅ | ✅ |
| 图片 | ✅ | ✅ |
| 视频 | ✅ | ✅ |
| 文件 | ✅ | ✅ |
| 语音消息 | ✅ | ❌ |
| 主动发送消息 | - | ✅ |

**注意**：微信不支持图文混合输入，只能逐条发送。

### Q15: 扫码绑定成功，Gateway 也重启了，但微信发消息没有回复？

**原因**：插件没有在 `openclaw.json` 的 `plugins.entries` 中启用。

**诊断方法**：
1. 检查会话列表，看是否有 `openclaw-weixin` 渠道的会话：
   ```bash
   # 查看会话列表
   openclaw sessions list
   ```
   如果只有 `xiaoyi-channel` 会话，没有 `openclaw-weixin` 会话，说明微信消息没有被接收。

2. 检查插件是否在配置中启用：
   ```bash
   cat ~/.openclaw/openclaw.json | grep -A 10 "plugins"
   ```
   查看 `plugins.entries` 中是否有 `"openclaw-weixin": { "enabled": true }`

3. 检查日志中是否有微信消息监控启动的记录：
   ```bash
   tail -500 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | grep -i "startAccount\|monitor"
   ```
   如果没有 `startAccount` 或 `monitor started` 日志，说明消息监控没有启动。

**解决方案**：

1. 编辑 `~/.openclaw/openclaw.json`，在 `plugins.entries` 中添加 `openclaw-weixin`：
   ```json
   "plugins": {
     "entries": {
       "cspl_hook": {
         "enabled": true
       },
       "openclaw-weixin": {
         "enabled": true
       },
       "xiaoyi-channel": {
         "enabled": true
       }
     },
     ...
   }
   ```

2. 重启 Gateway：
   ```bash
   openclaw gateway restart
   ```

3. 验证插件已加载：
   ```bash
   tail -100 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | grep -i "weixin"
   ```
   应该看到类似 `Loading plugin: openclaw-weixin` 和 `startAccount` 的日志。

### Q16: 扫码成功后，为什么前几次都没有生效，最后一次才成功？

**原因**：扫码成功只是保存了凭证，但插件启用和 Gateway 重启需要在**同一个对话会话中**完成。

**失败场景**：
1. 执行扫码命令 → 显示二维码
2. 用户扫码成功 → 凭证保存
3. **对话结束** → 没有后续操作
4. 插件未启用、Gateway 未重启 → 消息监控未启动 → 微信消息无响应

**成功场景**：
1. 执行扫码命令 → 显示二维码
2. 用户扫码成功 → 凭证保存
3. **Agent 持续等待并感知扫码成功**
4. Agent 立即执行后续步骤：
   - 启用插件配置
   - 重启 Gateway
   - 验证消息监控启动
5. 微信消息正常接收和回复

**关键教训**：
- 扫码绑定成功 ≠ 插件工作
- 扫码后必须**立即**执行启用插件和重启 Gateway
- 不要在扫码后结束对话，要保持会话直到验证完成

**建议操作流程**：
```bash
# 1. 生成登录二维码（插件已安装时使用 login）
openclaw channels login --channel openclaw-weixin

# 2. 扫码绑定后，立即启用插件（编辑 openclaw.json）

# 3. 立即重启 Gateway
openclaw gateway restart

# 4. 验证消息监控启动
tail -100 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | grep -i "monitor started"
```

**一句话总结**：扫码成功后，必须在同一会话中完成「启用插件 → 重启 Gateway → 验证」三步，否则不会生效。

## 关键文件路径

| 文件/目录 | 说明 |
|----------|------|
| `~/.openclaw/extensions/openclaw-weixin/` | 插件安装目录 |
| `~/.openclaw/openclaw-weixin/accounts.json` | 账户索引文件 |
| `~/.openclaw/openclaw-weixin/accounts/*.json` | 各账户凭证文件 |
| `~/.openclaw/openclaw.json` | OpenClaw 主配置文件 |
| `/tmp/openclaw/openclaw-*.log` | 运行日志 |

## 快速检查清单

- [ ] 微信版本 ≥ 8.0.70：微信 → 我 → 设置 → 关于微信
- [ ] 插件已安装：`ls ~/.openclaw/extensions/openclaw-weixin/`
- [ ] 凭证已保存：`cat ~/.openclaw/openclaw-weixin/accounts.json`
- [ ] **插件已启用**：`cat ~/.openclaw/openclaw.json | grep -A 5 "openclaw-weixin"` ⚠️ 关键！
- [ ] Gateway 已重启：`openclaw gateway status`
- [ ] 插件已加载：`openclaw channels list | grep weixin`
- [ ] 微信已绑定：在微信中找到 ClawBot 对话

## 总结

配置微信 ClawBot 的核心步骤（**必须在同一会话中连续完成**）：

1. **更新微信** → 确保版本 ≥ 8.0.70
2. **安装/登录插件**：
   - 首次安装：`npx -y @tencent-weixin/openclaw-weixin-cli@latest install`
   - 已安装插件：`openclaw channels login --channel openclaw-weixin` ⚠️ **推荐使用 login 命令**
3. **扫码绑定** → 用微信扫描二维码或点击链接
4. **启用插件** → 在 `~/.openclaw/openclaw.json` 的 `plugins.entries` 中添加 `"openclaw-weixin": { "enabled": true }` ⚠️ **容易遗漏！**
5. **重启 Gateway** → `openclaw gateway restart`
6. **验证连接** → `openclaw channels list`
7. **验证监控** → 检查日志中 `monitor started`
8. **测试对话** → 在微信中发送消息测试

**最容易失败的原因**：扫码成功后对话结束，没有在同一会话中完成后续步骤！

**成功秘诀**：扫码成功后，**立即、连续**执行「启用插件 → 重启 Gateway → 验证」三步，不要中断！

## 命令速查表

| 场景 | 命令 |
|------|------|
| **首次安装插件** | `npx -y @tencent-weixin/openclaw-weixin-cli@latest install` |
| **生成登录二维码** | `openclaw channels login --channel openclaw-weixin` |
| **查看插件状态** | `openclaw channels list` |
| **重启 Gateway** | `openclaw gateway restart` |
| **查看日志** | `tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log` |