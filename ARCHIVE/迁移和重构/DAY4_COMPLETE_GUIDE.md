# Day 4 完整指南 - Prompt Enhancement Skill 实施

**日期**: 2025-12-09  
**状态**: 🚀 **立即开始**  
**预计完成时间**: 1.5 小时

---

## 📚 **文档索引**

本指南包含以下文档：

1. **DAY4_IMPLEMENTATION_PLAN.md** - 详细的实施计划和任务清单
2. **skill_templates/SKILL.md** - Skill 描述文件（完整内容）
3. **skill_templates/enhance.py** - Python 增强脚本（完整代码）
4. **skill_templates/README.md** - 用户文档
5. **TESTING_AND_VALIDATION_GUIDE.md** - 测试和验证指南
6. **install_skill.sh** - 快速安装脚本
7. **本文档** - 完整指南和快速开始

---

## 🚀 **快速开始（3 种方法）**

### **方法 1: 使用自动安装脚本（推荐）**

```bash
# 1. 进入项目目录
cd /Users/jodykwong/Documents/augment-projects/Prompt-Enhancement

# 2. 设置脚本权限
chmod +x install_skill.sh

# 3. 运行安装脚本
./install_skill.sh

# 4. 设置 API Key（如果未设置）
export DEEPSEEK_API_KEY="your-api-key-here"

# 5. 测试
cd ~/.claude/skills/prompt-enhancement/scripts
python3 enhance.py "测试提示词"
```

**优点**: 
- ✅ 一键安装
- ✅ 自动验证
- ✅ 清晰的错误提示

---

### **方法 2: 手动安装（详细步骤）**

#### **步骤 1: 创建目录结构**

```bash
mkdir -p ~/.claude/skills/prompt-enhancement/scripts
cd ~/.claude/skills/prompt-enhancement
```

#### **步骤 2: 复制文件**

```bash
# 从项目模板复制
cd /Users/jodykwong/Documents/augment-projects/Prompt-Enhancement

cp skill_templates/SKILL.md ~/.claude/skills/prompt-enhancement/
cp skill_templates/enhance.py ~/.claude/skills/prompt-enhancement/scripts/
cp skill_templates/README.md ~/.claude/skills/prompt-enhancement/
```

#### **步骤 3: 创建 requirements.txt**

```bash
cat > ~/.claude/skills/prompt-enhancement/requirements.txt << 'EOF'
openai>=1.0.0
python-dotenv>=1.0.0
EOF
```

#### **步骤 4: 设置权限**

```bash
chmod +x ~/.claude/skills/prompt-enhancement/scripts/enhance.py
```

#### **步骤 5: 配置环境变量**

```bash
# 添加到 shell 配置
echo 'export DEEPSEEK_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

#### **步骤 6: 测试**

```bash
cd ~/.claude/skills/prompt-enhancement/scripts
python3 enhance.py "测试提示词"
```

---

### **方法 3: 逐文件创建（完全手动）**

如果模板文件不可用，可以手动创建每个文件。

#### **创建 SKILL.md**

```bash
cd ~/.claude/skills/prompt-enhancement
cat > SKILL.md << 'EOF'
[复制 skill_templates/SKILL.md 的完整内容]
EOF
```

#### **创建 enhance.py**

```bash
cd ~/.claude/skills/prompt-enhancement/scripts
cat > enhance.py << 'EOF'
[复制 skill_templates/enhance.py 的完整内容]
EOF
chmod +x enhance.py
```

**注意**: 完整内容请参考 `skill_templates/` 目录中的文件。

---

## 📋 **完整任务清单**

### **阶段 1: 安装（30 分钟）**

- [ ] 创建 Skill 目录结构
- [ ] 复制 SKILL.md 文件
- [ ] 复制 enhance.py 脚本
- [ ] 创建 requirements.txt
- [ ] 复制 README.md
- [ ] 设置文件权限
- [ ] 配置 DEEPSEEK_API_KEY 环境变量

### **阶段 2: 验证（20 分钟）**

- [ ] 手动测试 enhance.py 脚本
- [ ] 测试错误处理（无参数）
- [ ] 测试错误处理（空提示词）
- [ ] 测试错误处理（无 API Key）
- [ ] 验证输出格式正确

### **阶段 3: Claude Code 集成测试（30 分钟）**

- [ ] 启动 Claude Code
- [ ] 检查 Skill 是否加载
- [ ] 测试 `/pe` 命令
- [ ] 测试自然语言触发
- [ ] 端到端集成测试

### **阶段 4: 文档和总结（10 分钟）**

- [ ] 记录测试结果
- [ ] 更新文档（如需要）
- [ ] 创建使用示例
- [ ] 生成完成报告

---

## 🧪 **快速测试命令**

### **测试 1: 基础功能**

```bash
cd ~/.claude/skills/prompt-enhancement/scripts
python3 enhance.py "修复登录页面的 bug"
```

**预期**: 输出增强后的提示词（30-60 秒）

### **测试 2: 错误处理**

```bash
# 无参数
python3 enhance.py

# 空提示词
python3 enhance.py ""

# 无 API Key
unset DEEPSEEK_API_KEY
python3 enhance.py "test"
export DEEPSEEK_API_KEY="your-api-key-here"
```

**预期**: 显示清晰的错误信息

### **测试 3: Claude Code 集成**

```bash
# 启动 Claude Code
claude-code

# 在 Claude Code 中测试
/pe 修复登录页面的 bug
```

**预期**: Skill 正常工作，返回增强后的提示词

---

## 📊 **文件清单**

安装完成后，应该有以下文件：

```
~/.claude/skills/prompt-enhancement/
├── SKILL.md              # Skill 描述和指令（必需）
├── scripts/
│   └── enhance.py        # 增强脚本（必需）
├── requirements.txt      # Python 依赖（必需）
└── README.md            # 用户文档（可选）
```

**文件大小参考**:
- SKILL.md: ~5 KB
- enhance.py: ~5 KB
- README.md: ~6 KB
- requirements.txt: ~50 bytes

---

## ⚙️ **环境要求**

### **必需**

- ✅ Python 3.8+
- ✅ Claude Code CLI
- ✅ DEEPSEEK_API_KEY 环境变量
- ✅ 网络连接（访问 DeepSeek API）

### **Python 依赖**

- openai>=1.0.0
- python-dotenv>=1.0.0

### **项目依赖**

- async_prompt_enhancer.py（已在阶段 1 完成）

---

## 🔧 **常见问题**

### **Q1: 如何验证安装成功？**

```bash
# 检查目录
ls -la ~/.claude/skills/prompt-enhancement/

# 检查文件
ls -la ~/.claude/skills/prompt-enhancement/scripts/enhance.py

# 测试脚本
cd ~/.claude/skills/prompt-enhancement/scripts
python3 enhance.py "test"
```

### **Q2: 如何更新 Skill？**

```bash
# 重新复制文件
cp skill_templates/SKILL.md ~/.claude/skills/prompt-enhancement/
cp skill_templates/enhance.py ~/.claude/skills/prompt-enhancement/scripts/

# 重启 Claude Code
```

### **Q3: 如何卸载 Skill？**

```bash
rm -rf ~/.claude/skills/prompt-enhancement/
```

---

## 📖 **相关文档**

- **实施计划**: `DAY4_IMPLEMENTATION_PLAN.md`
- **测试指南**: `TESTING_AND_VALIDATION_GUIDE.md`
- **用户文档**: `skill_templates/README.md`
- **技术分析**: `PHASE2_TECHNICAL_FEASIBILITY_ANALYSIS.md`

---

## ✅ **验收标准**

安装完成后，应该满足以下标准：

- [ ] 所有文件已创建
- [ ] 文件权限正确
- [ ] 环境变量已设置
- [ ] 手动测试通过
- [ ] Claude Code 测试通过
- [ ] 文档完整

---

## 🎯 **下一步**

完成 Day 4 后：

1. **Day 5-6**: 优化和增强功能
2. **Day 7**: 全面测试
3. **Day 8**: 文档和发布

---

**创建时间**: 2025-12-09  
**状态**: ✅ **已完成**  
**立即开始**: 选择一种安装方法并执行

