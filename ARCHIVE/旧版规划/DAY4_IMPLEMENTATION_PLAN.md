# Day 4: 实施计划 - Prompt Enhancement Skill

**日期**: 2025-12-09  
**状态**: 🚀 **立即开始**

---

## 🎯 **今天的目标**

创建完整的 Prompt Enhancement Skill，使用户能够在 Claude Code 中通过 `/pe` 命令增强提示词。

---

## 📋 **任务清单**

### **任务 1: 创建 Skill 目录结构**（10 分钟）

#### **步骤 1.1: 创建目录**

```bash
# 在终端中执行
mkdir -p ~/.claude/skills/prompt-enhancement/scripts
cd ~/.claude/skills/prompt-enhancement
```

**目录结构**:
```
~/.claude/skills/prompt-enhancement/
├── SKILL.md              # Skill 描述和指令
├── scripts/
│   └── enhance.py        # 增强脚本
├── requirements.txt      # Python 依赖
└── README.md            # 用户文档
```

#### **步骤 1.2: 验证目录创建**

```bash
# 验证目录存在
ls -la ~/.claude/skills/prompt-enhancement/
```

**预期输出**:
```
drwxr-xr-x  4 user  staff  128 Dec  9 14:00 .
drwxr-xr-x  3 user  staff   96 Dec  9 14:00 ..
-rw-r--r--  1 user  staff    0 Dec  9 14:00 SKILL.md
drwxr-xr-x  2 user  staff   64 Dec  9 14:00 scripts
```

---

### **任务 2: 创建 SKILL.md**（15 分钟）

#### **步骤 2.1: 创建文件**

```bash
cd ~/.claude/skills/prompt-enhancement
touch SKILL.md
```

#### **步骤 2.2: 编写内容**

**完整的 SKILL.md 内容**（见下一节）

---

### **任务 3: 创建 enhance.py 脚本**（20 分钟）

#### **步骤 3.1: 创建文件**

```bash
cd ~/.claude/skills/prompt-enhancement/scripts
touch enhance.py
chmod +x enhance.py
```

#### **步骤 3.2: 编写脚本**

**完整的 enhance.py 内容**（见下一节）

---

### **任务 4: 创建依赖文件**（5 分钟）

#### **步骤 4.1: 创建 requirements.txt**

```bash
cd ~/.claude/skills/prompt-enhancement
cat > requirements.txt << 'EOF'
openai>=1.0.0
python-dotenv>=1.0.0
EOF
```

#### **步骤 4.2: 安装依赖**

```bash
# 在项目虚拟环境中安装
cd /Users/jodykwong/Documents/augment-projects/Prompt-Enhancement
source venv/bin/activate
pip install -r ~/.claude/skills/prompt-enhancement/requirements.txt
```

---

### **任务 5: 配置环境变量**（5 分钟）

#### **步骤 5.1: 检查 API Key**

```bash
# 检查环境变量是否已设置
echo $DEEPSEEK_API_KEY
```

**如果未设置**:
```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
echo 'export DEEPSEEK_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

#### **步骤 5.2: 验证配置**

```bash
# 验证 API Key 已设置
python3 -c "import os; print('API Key:', 'SET' if os.getenv('DEEPSEEK_API_KEY') else 'NOT SET')"
```

**预期输出**:
```
API Key: SET
```

---

### **任务 6: 创建用户文档**（10 分钟）

#### **步骤 6.1: 创建 README.md**

```bash
cd ~/.claude/skills/prompt-enhancement
touch README.md
```

**完整的 README.md 内容**（见下一节）

---

### **任务 7: 测试 Skill**（15 分钟）

#### **步骤 7.1: 手动测试脚本**

```bash
# 测试 enhance.py 脚本是否正常工作
cd ~/.claude/skills/prompt-enhancement/scripts
python3 enhance.py "修复登录页面的 bug"
```

**预期输出**:
```
1. **定位登录页面文件：** 检查前端登录页面组件...
2. **检查登录逻辑：** 审查登录表单的提交逻辑...
...
```

#### **步骤 7.2: 在 Claude Code 中测试**

```bash
# 启动 Claude Code
claude-code
```

**在 Claude Code 中测试**:
```
# 测试 1: 检查 Skill 是否加载
/help

# 测试 2: 使用 Skill
/pe 修复登录页面的 bug

# 测试 3: 自然语言触发
请先增强这个提示词再执行：修复登录页面的 bug
```

---

## 📝 **预期完成时间**

| 任务 | 预计时间 | 累计时间 |
|-----|---------|---------|
| 任务 1: 创建目录结构 | 10 分钟 | 10 分钟 |
| 任务 2: 创建 SKILL.md | 15 分钟 | 25 分钟 |
| 任务 3: 创建 enhance.py | 20 分钟 | 45 分钟 |
| 任务 4: 创建依赖文件 | 5 分钟 | 50 分钟 |
| 任务 5: 配置环境变量 | 5 分钟 | 55 分钟 |
| 任务 6: 创建用户文档 | 10 分钟 | 65 分钟 |
| 任务 7: 测试 Skill | 15 分钟 | 80 分钟 |
| **总计** | **80 分钟** | **1.5 小时** |

---

## ✅ **验收标准**

- [ ] 目录结构创建完成
- [ ] SKILL.md 文件创建并包含正确内容
- [ ] enhance.py 脚本创建并可执行
- [ ] requirements.txt 创建并依赖已安装
- [ ] DEEPSEEK_API_KEY 环境变量已设置
- [ ] README.md 用户文档创建完成
- [ ] 手动测试脚本成功
- [ ] Claude Code 中测试 Skill 成功

---

## 🚀 **立即开始**

**第一步**: 打开终端，执行任务 1 的命令

```bash
mkdir -p ~/.claude/skills/prompt-enhancement/scripts
cd ~/.claude/skills/prompt-enhancement
```

**第二步**: 继续执行后续任务

---

**计划创建时间**: 2025-12-09  
**计划状态**: ✅ **已完成**  
**下一步**: 开始执行任务 1

