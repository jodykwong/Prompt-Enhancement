# 推送到 GitHub - 快速指南

## 📋 概述

本指南说明如何将 Prompt Enhancement v2.0.0 推送到 GitHub。

**状态**：
- ✅ 所有代码已提交并标记
- ✅ 推送脚本已准备好
- ⏳ 需要在本地环境中执行

---

## 🚀 快速开始（选择一种方式）

### 方式 1️⃣：使用 Python 脚本（推荐 - 跨平台）

```bash
# 在项目根目录执行
python3 push_to_github.py
```

**优点**：
- ✅ 跨平台支持（Windows、macOS、Linux）
- ✅ 交互式界面，友好提示
- ✅ 自动验证和错误检查
- ✅ 详细的彩色输出

**适用平台**：所有平台

---

### 方式 2️⃣：使用 Bash 脚本（Linux/macOS）

```bash
# 在项目根目录执行
bash PUSH_TO_GITHUB.sh

# 或直接执行
./PUSH_TO_GITHUB.sh
```

**优点**：
- ✅ 无需 Python 环境
- ✅ 原生 Linux/macOS 脚本
- ✅ 轻量级

**适用平台**：macOS、Linux、WSL

---

### 方式 3️⃣：手动执行命令

```bash
# 第 1 步：推送主分支
git push origin main

# 第 2 步：推送标签
git push origin v2.0.0

# 第 3 步：验证
git status
git log origin/main --oneline -3
git ls-remote --tags origin | grep v2.0.0
```

**适用场景**：
- ✅ 调试或自定义流程
- ✅ 了解每个步骤的细节
- ✅ 集成到其他脚本

---

## 📦 前置条件

在执行推送之前，请确保：

- ✅ 已安装 Git
- ✅ 当前目录是 Prompt-Enhancement 项目根目录
- ✅ 已配置 GitHub token 或 SSH 密钥
- ✅ 工作目录干净（无未提交更改）
- ✅ 有网络连接

### 检查 Git 配置

```bash
# 检查 Git 是否已安装
git --version

# 检查用户信息
git config user.name
git config user.email

# 检查远程仓库
git remote -v

# 检查当前分支
git branch -vv
```

---

## 🔑 GitHub 认证配置

### 如果使用 HTTPS 和 Token

```bash
# 方式 1：使用 Git credential helper（推荐）
git config --global credential.helper store

# 方式 2：在 GitHub 网页生成 token
# https://github.com/settings/tokens
# 创建 Personal Access Token，范围包括 'repo'

# 第一次推送时会提示输入用户名和密码
# 用户名：<你的 GitHub 用户名>
# 密码：<你的 Personal Access Token>
```

### 如果使用 SSH 密钥（更推荐）

```bash
# 生成 SSH 密钥（如果还没有）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 将公钥添加到 GitHub
# https://github.com/settings/keys

# 测试 SSH 连接
ssh -T git@github.com

# 如果使用 SSH，远程 URL 应该是
# git@github.com:jodykwong/Prompt-Enhancement.git

# 将本地仓库切换为 SSH（如果需要）
git remote set-url origin git@github.com:jodykwong/Prompt-Enhancement.git
```

---

## 📋 逐步执行说明

### 步骤 1：进入项目目录

```bash
cd /path/to/Prompt-Enhancement
```

### 步骤 2：验证本地状态

```bash
# 检查工作目录
git status

# 预期输出：
# On branch main
# Your branch is ahead of 'origin/main' by 2 commits.
# nothing to commit, working tree clean
```

### 步骤 3：执行推送脚本

**选择以下一种方式**：

**推荐：使用 Python 脚本**
```bash
python3 push_to_github.py
```

**或使用 Bash 脚本**
```bash
bash PUSH_TO_GITHUB.sh
```

**或手动执行**
```bash
git push origin main
git push origin v2.0.0
```

### 步骤 4：查看交互式提示

脚本会显示：
- 当前状态
- 待推送的提交
- 待推送的标签
- 确认提示

根据提示输入 `yes` 或 `y` 确认。

### 步骤 5：验证推送结果

脚本完成后会自动验证并显示：
- ✅ 推送成功状态
- 📍 GitHub 确认链接
- 📋 后续步骤建议

---

## ✅ 推送成功的标志

推送完成后，您应该看到：

### 本地验证

```bash
# 应该看到：Your branch is up to date with 'origin/main'
git status

# 应该看到本地提交在远程
git log origin/main --oneline -3

# 应该看到标签已推送
git ls-remote --tags origin | grep v2.0.0
```

### GitHub 网页确认

访问这些链接验证：

1. **提交历史**
   https://github.com/jodykwong/Prompt-Enhancement/commits/main

   应该看到：
   - 最新提交：`chore: Finalize v2.0.0 release package build` (e05cd61)
   - 次新提交：`release: v2.0.0 - Comprehensive cross-project deployment system` (9dfe0a0)

2. **标签列表**
   https://github.com/jodykwong/Prompt-Enhancement/tags

   应该看到：
   - v2.0.0 标签在列表中

3. **Release 页面**
   https://github.com/jodykwong/Prompt-Enhancement/releases

   应该看到：
   - v2.0.0 标签可用（虽然 release notes 尚未创建）

---

## 🆘 故障排除

### 问题 1：认证失败

**错误信息**：
```
fatal: could not read Username for 'https://github.com': No such device or address
```

**解决方案**：

```bash
# 检查网络连接
ping github.com

# 清除缓存的凭据并重新认证
git config --global credential.reject

# 重新推送（会提示输入凭据）
git push origin main

# 输入 GitHub 用户名 + Personal Access Token
```

---

### 问题 2：推送被拒绝

**错误信息**：
```
! [rejected] main -> main (fetch first)
error: failed to push some refs to 'https://github.com/...'
```

**解决方案**：

```bash
# 拉取最新更新
git fetch origin

# 检查差异
git log HEAD..origin/main

# 合并远程更改（如果有新提交）
git pull --rebase origin main

# 重新推送
git push origin main
```

---

### 问题 3：标签冲突

**错误信息**：
```
! [rejected] v2.0.0 -> v2.0.0 (already exists)
error: failed to push some refs to 'https://github.com/...'
```

**解决方案**：

```bash
# 检查远程是否已有该标签
git ls-remote --tags origin | grep v2.0.0

# 如果确实存在，两个选项：

# 选项 A：删除远程标签后重新推送
git push origin :refs/tags/v2.0.0
git push origin v2.0.0

# 选项 B：强制覆盖（谨慎！）
git push origin v2.0.0 --force
```

---

### 问题 4：权限不足

**错误信息**：
```
remote: error: GH006: Protected branch update failed
```

**原因**：分支有保护规则，需要 Pull Request

**解决方案**：

1. 访问 GitHub 仓库设置
2. 检查 Settings > Branches > Branch protection rules
3. 确认您的账户有足够的权限
4. 如果需要 PR，改为创建 Pull Request

---

### 问题 5：网络超时

**错误信息**：
```
fatal: unable to access 'https://github.com/...': Failed to connect
```

**解决方案**：

```bash
# 增加 Git 超时配置
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999

# 稍后重试
git push origin main
```

---

### 问题 6：Python 脚本找不到

**错误信息**：
```
python3: command not found
```

**解决方案**：

```bash
# 使用 Bash 脚本代替
bash PUSH_TO_GITHUB.sh

# 或手动执行命令
git push origin main
git push origin v2.0.0
```

---

## 📊 推送前的最终检查清单

在执行推送前，请确认：

- [ ] 在 Prompt-Enhancement 项目目录中
- [ ] `git status` 显示 "up to date" 或有领先的提交
- [ ] `git log --oneline -3` 显示 e05cd61 和 9dfe0a0 提交
- [ ] `git tag -l v2.0.0` 显示标签存在
- [ ] 网络连接正常
- [ ] GitHub 凭据已配置（可通过 `git push --dry-run origin main` 测试）
- [ ] 有足够的 GitHub 权限推送到远程仓库

---

## 🎯 推送后的后续步骤

推送成功后，继续执行发布流程：

### 1. 创建 GitHub Release（推荐）

```bash
# 使用 GitHub CLI
gh release create v2.0.0 \
  --title "v2.0.0 - Comprehensive Cross-Project Deployment System" \
  --notes "$(cat RELEASE_NOTES.md)"
```

或手动：
https://github.com/jodykwong/Prompt-Enhancement/releases/new

### 2. 发布到 PyPI

```bash
cd packages/python/
twine upload dist/*
```

### 3. 发布到 NPM

```bash
cd packages/npm/
npm login
npm publish
```

### 4. 更新项目元数据

https://github.com/jodykwong/Prompt-Enhancement/settings

- 更新项目描述
- 添加话题标签：prompt-engineering, ai, claude-code, deployment
- 添加 PyPI/NPM 徽章

---

## 📚 相关文档

- **RELEASE_COMMANDS.md** - 完整发布命令参考
- **RELEASE_BUILD_SUMMARY.md** - 构建状态和工件
- **docs/deploy/INSTALL.md** - 用户安装指南

---

## 💬 需要帮助？

如有问题，请：

1. 检查错误消息并参考故障排除部分
2. 查看 RELEASE_COMMANDS.md 中的详细说明
3. 访问 GitHub 文档：https://docs.github.com/

---

**准备好了吗？** 选择您喜欢的方式执行推送脚本！🚀

```bash
# Python（推荐）
python3 push_to_github.py

# 或 Bash
bash PUSH_TO_GITHUB.sh

# 或手动
git push origin main && git push origin v2.0.0
```

祝发布顺利！✨
