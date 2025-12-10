# Prompt Enhancement Skill for Claude Code

**版本**: 1.0.0  
**作者**: Jody Kwong  
**日期**: 2025-12-09

---

## 📖 **简介**

Prompt Enhancement Skill 是一个 Claude Code 技能，可以自动增强用户的提示词，使其更加详细、结构化和有效。

**核心功能**:
- 🚀 通过 `/pe` 命令快速增强提示词
- 🤖 使用 DeepSeek API 生成详细的任务描述
- 📝 将简短的请求转换为全面的指令
- ✅ 无缝集成到 Claude Code 工作流程中

---

## 🎯 **使用场景**

### **场景 1: 简单的 Bug 修复**

**原始提示词**: "修复登录页面的 bug"

**增强后**:
```
1. **定位登录页面文件：** 检查前端登录页面组件...
2. **检查登录逻辑：** 审查登录表单的提交逻辑...
3. **验证错误处理：** 确保登录失败时有适当的错误提示...
...
```

### **场景 2: 功能开发**

**原始提示词**: "add user authentication"

**增强后**:
```
1. **Design Authentication System:** Choose authentication method...
2. **Implement User Model:** Create database schema for users...
3. **Add Login/Logout Endpoints:** Implement API routes...
...
```

---

## 📦 **安装步骤**

### **前置要求**

1. **Python 3.8+** 已安装
2. **Claude Code CLI** 已安装
3. **DeepSeek API Key** 已获取

### **步骤 1: 创建 Skill 目录**

```bash
mkdir -p ~/.claude/skills/prompt-enhancement/scripts
cd ~/.claude/skills/prompt-enhancement
```

### **步骤 2: 复制文件**

将以下文件复制到 Skill 目录：

```bash
# 从项目模板复制文件
cp /path/to/skill_templates/SKILL.md ~/.claude/skills/prompt-enhancement/
cp /path/to/skill_templates/enhance.py ~/.claude/skills/prompt-enhancement/scripts/
cp /path/to/skill_templates/README.md ~/.claude/skills/prompt-enhancement/
```

或者手动创建文件（参考项目中的 `skill_templates/` 目录）。

### **步骤 3: 设置脚本权限**

```bash
chmod +x ~/.claude/skills/prompt-enhancement/scripts/enhance.py
```

### **步骤 4: 安装 Python 依赖**

```bash
# 创建 requirements.txt
cat > ~/.claude/skills/prompt-enhancement/requirements.txt << 'EOF'
openai>=1.0.0
python-dotenv>=1.0.0
EOF

# 安装依赖（在 Prompt-Enhancement 项目的虚拟环境中）
cd /Users/jodykwong/Documents/augment-projects/Prompt-Enhancement
source venv/bin/activate
pip install -r ~/.claude/skills/prompt-enhancement/requirements.txt
```

### **步骤 5: 配置环境变量**

```bash
# 添加 API Key 到 shell 配置文件
echo 'export DEEPSEEK_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc

# 验证配置
echo $DEEPSEEK_API_KEY
```

### **步骤 6: 验证安装**

```bash
# 测试脚本
cd ~/.claude/skills/prompt-enhancement/scripts
python3 enhance.py "测试提示词"
```

**预期输出**: 增强后的提示词文本

---

## 🚀 **使用方法**

### **方法 1: 使用 `/pe` 命令**

```bash
# 在 Claude Code 中
/pe 修复登录页面的 bug
```

### **方法 2: 自然语言触发**

```bash
# 在 Claude Code 中
请先增强这个提示词再执行：优化数据库查询
```

### **方法 3: 明确请求增强**

```bash
# 在 Claude Code 中
enhance this prompt: add user authentication
```

---

## ⚙️ **配置说明**

### **环境变量**

| 变量名 | 必需 | 说明 |
|-------|------|------|
| `DEEPSEEK_API_KEY` | ✅ | DeepSeek API 密钥 |

### **Skill 配置**

在 `SKILL.md` 的 frontmatter 中配置：

```yaml
name: prompt-enhancement
description: Enhance user prompts using DeepSeek API...
allowed-tools: "Bash(python:*), Read"
version: 1.0.0
```

---

## 🔧 **故障排除**

### **问题 1: "DEEPSEEK_API_KEY not set"**

**原因**: 环境变量未设置

**解决方案**:
```bash
export DEEPSEEK_API_KEY="your-api-key-here"
# 或添加到 ~/.zshrc
echo 'export DEEPSEEK_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### **问题 2: "Cannot find Prompt-Enhancement project"**

**原因**: enhance.py 找不到 async_prompt_enhancer.py

**解决方案**:
1. 确认项目路径正确：`/Users/jodykwong/Documents/augment-projects/Prompt-Enhancement`
2. 或修改 `enhance.py` 中的 `PROJECT_ROOT` 变量

### **问题 3: "API call timed out"**

**原因**: 网络问题或 API 响应慢

**解决方案**:
- 检查网络连接
- 稍后重试
- 增加 timeout 值（在 enhance.py 中修改）

### **问题 4: Skill 未加载**

**原因**: Claude Code 未识别 Skill

**解决方案**:
1. 确认目录路径正确：`~/.claude/skills/prompt-enhancement/`
2. 确认 `SKILL.md` 文件存在且格式正确
3. 重启 Claude Code

---

## 📊 **性能说明**

- **处理时间**: 30-60 秒（DeepSeek API 调用）
- **扩展比例**: 通常 10-50x 原始长度
- **成功率**: >95%（网络正常情况下）

---

## 🔒 **安全说明**

- ✅ 仅适用于**本地 Claude Code CLI**
- ⚠️ 云端模式（claude.com/code）可能受网络隔离限制
- ✅ API Key 通过环境变量安全存储
- ✅ 不会修改用户文件，只读取和输出文本

---

## 📝 **更新日志**

### **v1.0.0** (2025-12-09)
- ✅ 初始版本发布
- ✅ 支持 `/pe` 命令
- ✅ 集成 DeepSeek API
- ✅ 完整的错误处理

---

## 🤝 **贡献**

欢迎提交 Issue 和 Pull Request！

---

## 📄 **许可证**

MIT License

---

## 📧 **联系方式**

如有问题，请联系：[your-email@example.com]

