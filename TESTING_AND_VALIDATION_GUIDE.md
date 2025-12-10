# 测试和验证指南 - Prompt Enhancement Skill

**日期**: 2025-12-09  
**版本**: 1.0.0

---

## 🎯 **测试目标**

验证 Prompt Enhancement Skill 在 Claude Code 中正常工作，包括：
1. ✅ Skill 正确加载
2. ✅ `/pe` 命令可用
3. ✅ DeepSeek API 调用成功
4. ✅ 增强后的提示词正确返回
5. ✅ 错误处理正常工作

---

## 📋 **测试前准备**

### **检查清单**

- [ ] Skill 目录已创建：`~/.claude/skills/prompt-enhancement/`
- [ ] SKILL.md 文件已创建
- [ ] enhance.py 脚本已创建并可执行
- [ ] requirements.txt 已创建
- [ ] Python 依赖已安装
- [ ] DEEPSEEK_API_KEY 环境变量已设置
- [ ] Claude Code CLI 已安装

### **验证命令**

```bash
# 1. 检查目录结构
ls -la ~/.claude/skills/prompt-enhancement/
ls -la ~/.claude/skills/prompt-enhancement/scripts/

# 2. 检查文件权限
ls -l ~/.claude/skills/prompt-enhancement/scripts/enhance.py

# 3. 检查环境变量
echo $DEEPSEEK_API_KEY

# 4. 检查 Python 依赖
python3 -c "import openai; print('openai:', openai.__version__)"
python3 -c "from dotenv import load_dotenv; print('python-dotenv: OK')"

# 5. 检查项目路径
ls -la /Users/jodykwong/Documents/augment-projects/Prompt-Enhancement/async_prompt_enhancer.py
```

---

## 🧪 **测试步骤**

### **测试 1: 手动测试 enhance.py 脚本**

#### **目的**: 验证脚本可以独立运行并调用 DeepSeek API

#### **步骤**:

```bash
# 1. 进入脚本目录
cd ~/.claude/skills/prompt-enhancement/scripts

# 2. 运行脚本
python3 enhance.py "修复登录页面的 bug"
```

#### **预期结果**:

```
1. **定位登录页面文件：** 检查前端登录页面组件...
2. **检查登录逻辑：** 审查登录表单的提交逻辑...
3. **验证错误处理：** 确保登录失败时有适当的错误提示...
...
```

#### **验收标准**:

- ✅ 脚本执行成功（exit code 0）
- ✅ 输出增强后的提示词到 stdout
- ✅ 处理时间在 30-60 秒内
- ✅ 增强后的提示词长度 > 原始提示词长度

#### **如果失败**:

**错误 1**: `DEEPSEEK_API_KEY not set`
```bash
# 解决方案
export DEEPSEEK_API_KEY="your-api-key-here"
```

**错误 2**: `Cannot find Prompt-Enhancement project`
```bash
# 解决方案：检查项目路径
ls -la /Users/jodykwong/Documents/augment-projects/Prompt-Enhancement/

# 如果路径不同，修改 enhance.py 中的 PROJECT_ROOT
```

**错误 3**: `Cannot import AsyncPromptEnhancer`
```bash
# 解决方案：检查 Python 路径
cd /Users/jodykwong/Documents/augment-projects/Prompt-Enhancement
python3 -c "from async_prompt_enhancer import AsyncPromptEnhancer; print('OK')"
```

---

### **测试 2: 测试错误处理**

#### **目的**: 验证脚本的错误处理机制

#### **测试 2.1: 无参数**

```bash
cd ~/.claude/skills/prompt-enhancement/scripts
python3 enhance.py
```

**预期输出** (stderr):
```
Error: No prompt provided

Usage:
  python enhance.py "<prompt_text>"
```

**验收标准**: ✅ Exit code = 1

---

#### **测试 2.2: 空提示词**

```bash
python3 enhance.py ""
```

**预期输出** (stderr):
```
Error: Prompt is empty
```

**验收标准**: ✅ Exit code = 1

---

#### **测试 2.3: 无 API Key**

```bash
# 临时取消环境变量
unset DEEPSEEK_API_KEY
python3 enhance.py "test"

# 恢复环境变量
export DEEPSEEK_API_KEY="your-api-key-here"
```

**预期输出** (stderr):
```
Error: DEEPSEEK_API_KEY environment variable is not set

Please set your API key:
  export DEEPSEEK_API_KEY='your-api-key-here'
```

**验收标准**: ✅ Exit code = 1

---

### **测试 3: 在 Claude Code 中测试 Skill**

#### **目的**: 验证 Skill 在 Claude Code 中正常工作

#### **前置条件**:

- Claude Code CLI 已安装
- Skill 已正确安装

#### **步骤 3.1: 启动 Claude Code**

```bash
# 启动 Claude Code
claude-code
```

#### **步骤 3.2: 检查 Skill 是否加载**

在 Claude Code 中输入：
```
/help
```

**预期结果**: 应该看到 `prompt-enhancement` 或相关的帮助信息

---

#### **步骤 3.3: 测试 `/pe` 命令**

在 Claude Code 中输入：
```
/pe 修复登录页面的 bug
```

**预期行为**:
1. Claude Code 识别 `/pe` 命令
2. 加载 prompt-enhancement skill
3. 执行 enhance.py 脚本
4. 显示 "Enhancing your prompt... This may take 30-60 seconds."
5. 返回增强后的提示词
6. 询问是否继续执行任务

**验收标准**:
- ✅ 命令被识别
- ✅ Skill 被加载
- ✅ 脚本执行成功
- ✅ 返回增强后的提示词
- ✅ 无错误信息

---

#### **步骤 3.4: 测试自然语言触发**

在 Claude Code 中输入：
```
请先增强这个提示词再执行：优化数据库查询
```

**预期行为**:
1. Claude 识别需要增强提示词
2. 自动加载 prompt-enhancement skill
3. 执行增强流程
4. 返回增强后的提示词

**验收标准**:
- ✅ Claude 正确识别意图
- ✅ Skill 被自动加载
- ✅ 增强流程正常执行

---

### **测试 4: 端到端集成测试**

#### **目的**: 验证完整的工作流程

#### **测试场景**: 使用增强后的提示词完成任务

**步骤**:

1. 在 Claude Code 中输入：
   ```
   /pe 创建一个简单的 Python Web API
   ```

2. 等待增强结果

3. 确认使用增强后的提示词

4. 观察 Claude 是否使用增强后的提示词执行任务

**验收标准**:
- ✅ 提示词成功增强
- ✅ Claude 使用增强后的提示词
- ✅ 任务执行更加详细和结构化

---

## 🐛 **调试指南**

### **问题 1: Skill 未加载**

**症状**: `/pe` 命令无效，Claude Code 不识别

**调试步骤**:

```bash
# 1. 检查 Skill 目录
ls -la ~/.claude/skills/

# 2. 检查 SKILL.md 格式
cat ~/.claude/skills/prompt-enhancement/SKILL.md | head -20

# 3. 检查 frontmatter 语法
# 确保 frontmatter 以 --- 开始和结束
```

**解决方案**:
- 确认目录路径正确
- 确认 SKILL.md 格式正确
- 重启 Claude Code

---

### **问题 2: 脚本执行失败**

**症状**: Claude Code 显示错误信息

**调试步骤**:

```bash
# 1. 手动运行脚本查看详细错误
cd ~/.claude/skills/prompt-enhancement/scripts
python3 enhance.py "test" 2>&1

# 2. 检查 Python 路径
python3 -c "import sys; print('\n'.join(sys.path))"

# 3. 检查项目导入
python3 -c "import sys; sys.path.insert(0, '/Users/jodykwong/Documents/augment-projects/Prompt-Enhancement'); from async_prompt_enhancer import AsyncPromptEnhancer; print('OK')"
```

**解决方案**:
- 修复 Python 路径问题
- 确认依赖已安装
- 检查 API Key 配置

---

### **问题 3: API 调用超时**

**症状**: 脚本运行超过 60 秒

**调试步骤**:

```bash
# 测试网络连接
curl -I https://api.deepseek.com

# 测试 API Key
python3 -c "
import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv('DEEPSEEK_API_KEY'), base_url='https://api.deepseek.com')
print('API Key valid')
"
```

**解决方案**:
- 检查网络连接
- 验证 API Key 有效性
- 增加 timeout 值

---

## ✅ **验收标准总结**

### **必须通过的测试**

- [ ] 测试 1: 手动测试脚本成功
- [ ] 测试 2.1: 无参数错误处理正确
- [ ] 测试 2.2: 空提示词错误处理正确
- [ ] 测试 2.3: 无 API Key 错误处理正确
- [ ] 测试 3.2: Skill 在 Claude Code 中加载
- [ ] 测试 3.3: `/pe` 命令正常工作
- [ ] 测试 3.4: 自然语言触发正常工作
- [ ] 测试 4: 端到端集成测试成功

### **性能指标**

- [ ] 脚本执行时间 < 60 秒
- [ ] 增强后提示词长度 > 原始长度
- [ ] 错误处理响应时间 < 1 秒

---

**测试完成时间**: ___________  
**测试状态**: [ ] 通过 / [ ] 失败  
**测试人员**: ___________

