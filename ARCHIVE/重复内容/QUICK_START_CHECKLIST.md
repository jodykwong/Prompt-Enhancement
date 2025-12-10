# 快速开始清单 - Prompt Enhancement Skill

**状态**: 🚀 **立即执行**  
**预计时间**: 15 分钟

---

## ✅ **第一步：打开终端，执行这条命令**

```bash
cd /Users/jodykwong/Documents/augment-projects/Prompt-Enhancement && chmod +x install_skill.sh && ./install_skill.sh
```

**这条命令做了什么**:
1. 进入项目目录
2. 给安装脚本添加执行权限
3. 运行安装脚本

**预期输出**: 看到绿色的 ✅ 符号和"安装完成"的消息

---

## ✅ **第二步：设置 API Key**

```bash
export DEEPSEEK_API_KEY="your-api-key-here"
```

**替换 `your-api-key-here` 为您的实际 API Key**

**验证是否设置成功**:
```bash
echo $DEEPSEEK_API_KEY
```

**预期输出**: 显示您的 API Key（或至少显示前几个字符）

---

## ✅ **第三步：测试脚本是否工作**

```bash
cd ~/.claude/skills/prompt-enhancement/scripts && python3 enhance.py "修复登录页面的 bug"
```

**预期输出**: 
- 等待 30-60 秒
- 看到增强后的提示词（以 "1. **" 开头）

**如果看到这个，说明成功了** ✅

---

## ✅ **第四步：启动 Claude Code 并测试**

```bash
claude-code
```

**在 Claude Code 中输入**:
```
/pe 修复登录页面的 bug
```

**预期行为**:
1. Claude Code 识别 `/pe` 命令
2. 加载 prompt-enhancement skill
3. 执行脚本（等待 30-60 秒）
4. 显示增强后的提示词

**如果看到增强后的提示词，说明完全成功了** ✅

---

## 🔍 **快速验证清单**

执行完上面 4 步后，检查以下项目：

- [ ] 第一步：安装脚本运行成功（看到绿色 ✅）
- [ ] 第二步：API Key 已设置（`echo $DEEPSEEK_API_KEY` 显示 Key）
- [ ] 第三步：脚本测试成功（看到增强后的提示词）
- [ ] 第四步：Claude Code 测试成功（`/pe` 命令工作）

**全部打勾 = 安装成功** ✅

---

## ⚠️ **常见问题快速解决**

### **问题 1: "DEEPSEEK_API_KEY not set"**

**解决方案**:
```bash
export DEEPSEEK_API_KEY="your-api-key-here"
```

---

### **问题 2: "Cannot find Prompt-Enhancement project"**

**解决方案**:
```bash
# 检查项目是否存在
ls -la /Users/jodykwong/Documents/augment-projects/Prompt-Enhancement/

# 如果不存在，检查实际路径
find ~ -name "async_prompt_enhancer.py" 2>/dev/null
```

---

### **问题 3: "Permission denied" 或 "command not found"**

**解决方案**:
```bash
# 重新设置权限
chmod +x ~/.claude/skills/prompt-enhancement/scripts/enhance.py

# 重新测试
python3 ~/.claude/skills/prompt-enhancement/scripts/enhance.py "test"
```

---

### **问题 4: Claude Code 中 `/pe` 命令不工作**

**解决方案**:
```bash
# 1. 检查 Skill 目录是否存在
ls -la ~/.claude/skills/prompt-enhancement/

# 2. 重启 Claude Code
# 关闭 Claude Code，重新启动

# 3. 再次尝试 /pe 命令
```

---

### **问题 5: 脚本运行超过 60 秒**

**解决方案**:
```bash
# 检查网络连接
ping api.deepseek.com

# 如果网络正常，稍后重试
# 如果网络有问题，等待网络恢复后重试
```

---

## 📊 **执行流程图**

```
第一步: 运行安装脚本
    ↓
第二步: 设置 API Key
    ↓
第三步: 测试脚本
    ↓ (成功)
第四步: 在 Claude Code 中测试
    ↓ (成功)
✅ 完成！
```

---

## 🎯 **成功标志**

当您看到以下情况时，说明安装成功：

1. ✅ 安装脚本显示绿色 ✅ 符号
2. ✅ `echo $DEEPSEEK_API_KEY` 显示您的 API Key
3. ✅ 脚本测试返回增强后的提示词
4. ✅ Claude Code 中 `/pe` 命令工作正常

---

## 💡 **提示**

- **如果卡住了**: 查看"常见问题快速解决"部分
- **如果需要详细信息**: 查看 `TESTING_AND_VALIDATION_GUIDE.md`
- **如果需要手动安装**: 查看 `DAY4_COMPLETE_GUIDE.md` 的"方法 2"

---

**现在就开始吧！** 🚀

执行第一步的命令，然后按照清单继续。

