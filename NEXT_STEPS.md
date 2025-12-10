# 下一步行动清单

**现在就执行这 5 个步骤**

---

## 步骤 1️⃣ : 运行安装脚本（2 分钟）

在终端中复制粘贴这条命令：

```bash
cd /Users/jodykwong/Documents/augment-projects/Prompt-Enhancement && chmod +x install_skill.sh && ./install_skill.sh
```

**看到绿色 ✅ 符号 = 成功**

---

## 步骤 2️⃣ : 设置 API Key（1 分钟）

```bash
export DEEPSEEK_API_KEY="your-api-key-here"
```

**将 `your-api-key-here` 替换为您的实际 API Key**

验证：
```bash
echo $DEEPSEEK_API_KEY
```

---

## 步骤 3️⃣ : 测试脚本（2 分钟）

```bash
cd ~/.claude/skills/prompt-enhancement/scripts && python3 enhance.py "修复登录页面的 bug"
```

**等待 30-60 秒，看到增强后的提示词 = 成功**

---

## 步骤 4️⃣ : 启动 Claude Code（1 分钟）

```bash
claude-code
```

---

## 步骤 5️⃣ : 在 Claude Code 中测试（2 分钟）

在 Claude Code 中输入：

```
/pe 修复登录页面的 bug
```

**看到增强后的提示词 = 完全成功** ✅

---

## 🚨 如果出错

| 错误信息 | 解决方案 |
|---------|--------|
| `DEEPSEEK_API_KEY not set` | 执行步骤 2，设置 API Key |
| `Cannot find project` | 检查路径：`ls /Users/jodykwong/Documents/augment-projects/Prompt-Enhancement/` |
| `Permission denied` | 运行：`chmod +x ~/.claude/skills/prompt-enhancement/scripts/enhance.py` |
| `/pe` 命令不工作 | 重启 Claude Code |
| 脚本超时 | 检查网络：`ping api.deepseek.com` |

---

## ✅ 完成标志

- [ ] 步骤 1 成功（看到绿色 ✅）
- [ ] 步骤 2 成功（API Key 已设置）
- [ ] 步骤 3 成功（脚本返回增强提示词）
- [ ] 步骤 4 成功（Claude Code 启动）
- [ ] 步骤 5 成功（`/pe` 命令工作）

**全部完成 = 安装成功** 🎉

---

**现在就开始吧！** 👉 执行步骤 1

