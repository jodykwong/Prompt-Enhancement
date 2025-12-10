# 阶段 2: 技术可行性分析报告

**日期**: 2025-12-09  
**状态**: ⚠️ **重要发现**

---

## 🎯 **核心问题**

用户询问：Claude Skills 方案是否支持在执行过程中调用外部 LLM API（DeepSeek）？

---

## ⚠️ **关键发现：Claude Skills 不支持执行代码**

### **重要结论**

根据深入研究，我发现了一个**关键技术限制**：

> **"Skills are not executable code. They do NOT run Python or JavaScript, and there's no HTTP server or function calling happening behind the scenes."**
> 
> — 来源: [Claude Agent Skills: A First Principles Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)

**这意味着**:
- ❌ Claude Skills **不能**执行 Python 脚本
- ❌ Claude Skills **不能**进行 HTTP 请求
- ❌ Claude Skills **不能**调用外部 API
- ✅ Claude Skills **只是**提示词模板（Prompt Templates）

---

## 📋 **Claude Skills 的实际工作原理**

### **Skills 的本质**

Claude Skills 是一个**提示词注入系统**，而不是代码执行系统：

```
Claude Skills = Prompt Templates + Context Injection
```

**工作流程**:
1. 用户触发 Skill（如 `/pdf`）
2. Claude Code 加载 `SKILL.md` 文件
3. 将 Skill 的提示词内容注入到对话上下文中
4. Claude 根据注入的提示词指令执行操作
5. **Claude 自己调用工具**（Bash, Read, Write 等）

**关键点**:
- Skills 不执行代码，只提供指令
- 实际操作由 Claude 通过 **Claude Code 的工具**（Bash, Read, Write）完成
- Skills 中的 `scripts/` 目录存放的脚本由 **Claude 通过 Bash 工具调用**，而不是 Skill 直接执行

---

## 🔍 **深入分析：Scripts 目录的真实用途**

### **误解 vs 现实**

**我之前的误解**:
```python
# 我以为 Skill 可以直接执行 Python 脚本
# enhance.py 会被 Skill 系统直接运行
async def enhance(prompt):
    enhancer = AsyncPromptEnhancer()
    result = await enhancer.enhance(prompt)
    return result
```

**实际情况**:
```markdown
# SKILL.md 中的指令
When the user wants to enhance a prompt, run the following command:

```bash
python {baseDir}/scripts/enhance.py "<user_prompt>"
```

Read the output and present it to the user.
```

**关键区别**:
- ❌ Skill 系统**不会**直接执行 `enhance.py`
- ✅ Skill 提示词**告诉 Claude** 使用 Bash 工具运行 `enhance.py`
- ✅ Claude 通过 **Bash 工具** 执行脚本
- ✅ Claude 读取脚本输出并处理

---

## 🚨 **对我们方案的影响**

### **原计划的问题**

**原计划**:
```
用户输入：/pe 修复登录页面的 bug
↓
Claude Code 识别命令并加载 prompt-enhancement skill
↓
Skill 中的 Python 脚本调用 DeepSeek API（外部 LLM）  ← ❌ 这一步不可行
↓
获取增强后的提示词
↓
Claude Code 使用增强后的提示词继续执行
```

**问题分析**:
1. ❌ Skill 不能直接执行 Python 脚本
2. ✅ 但 Claude 可以通过 Bash 工具执行 Python 脚本
3. ⚠️ 关键问题：**Claude Code 的 Bash 工具是否允许网络请求？**

---

## 🔐 **Claude Code 沙箱限制分析**

### **Claude Code 的安全模型**

根据 [Claude Code Sandboxing 文档](https://www.anthropic.com/engineering/claude-code-sandboxing)：

**Claude Code 有两种运行模式**:

#### **1. 本地运行模式（Claude Code CLI）**

```bash
# 在用户本地机器运行
claude-code
```

**特点**:
- ✅ **完全网络访问**：可以访问任何网站和 API
- ✅ **完全文件系统访问**：可以读写用户文件
- ✅ **可以执行任意命令**：包括 Python 脚本、curl、npm 等
- ⚠️ **安全性依赖用户批准**：需要用户批准每个操作

**结论**: ✅ **在本地模式下，调用 DeepSeek API 完全可行**

---

#### **2. 云端沙箱模式（Claude Code on the Web）**

```bash
# 在 claude.com/code 网页版运行
```

**特点**:
- ❌ **网络隔离**：只能访问白名单域名
- ❌ **文件系统隔离**：只能访问沙箱目录
- ❌ **受限命令执行**：某些命令被禁止

**网络访问限制**:
> "Network isolation, which ensures that Claude can only connect to approved servers."

**结论**: ❌ **在云端沙箱模式下，调用 DeepSeek API 可能被阻止**

---

## ✅ **修正后的技术方案**

### **方案 1: 本地 Claude Code + Skill（推荐）**

**适用场景**: 用户在本地运行 Claude Code CLI

**技术路径**:

1. **创建 Skill 目录结构**
   ```
   ~/.claude/skills/prompt-enhancement/
   ├── SKILL.md              # Skill 描述和指令
   ├── scripts/
   │   └── enhance.py        # 调用 DeepSeek API 的脚本
   └── requirements.txt      # 依赖列表
   ```

2. **SKILL.md 内容**
   ```markdown
   ---
   name: prompt-enhancement
   description: Enhance user prompts using DeepSeek API to make them more detailed and effective. Use this when the user wants to improve their prompt before executing a task.
   allowed-tools: "Bash(python:*), Read, Write"
   ---

   # Prompt Enhancement Skill

   ## Purpose
   This skill enhances user prompts by calling the DeepSeek API to expand and improve them.

   ## Instructions

   When the user wants to enhance a prompt:

   1. **Run the enhancement script**:
      ```bash
      python {baseDir}/scripts/enhance.py "<user_prompt>"
      ```

   2. **Read the enhanced prompt**:
      The script will output the enhanced prompt to stdout.

   3. **Use the enhanced prompt**:
      Use the enhanced prompt to complete the user's original task.

   ## Example

   User: "修复登录页面的 bug"

   1. Run: `python {baseDir}/scripts/enhance.py "修复登录页面的 bug"`
   2. Get enhanced prompt: "1. **定位登录页面文件：** 检查前端登录页面组件..."
   3. Use the enhanced prompt to fix the login bug
   ```

3. **enhance.py 脚本**
   ```python
   #!/usr/bin/env python3
   import sys
   import asyncio
   import os
   from pathlib import Path

   # 添加项目根目录到 Python 路径
   project_root = Path(__file__).parent.parent.parent.parent
   sys.path.insert(0, str(project_root))

   from async_prompt_enhancer import AsyncPromptEnhancer

   async def main():
       if len(sys.argv) < 2:
           print("Error: No prompt provided", file=sys.stderr)
           sys.exit(1)
       
       prompt = " ".join(sys.argv[1:])
       
       # 确保 API key 存在
       if not os.getenv("DEEPSEEK_API_KEY"):
           print("Error: DEEPSEEK_API_KEY not set", file=sys.stderr)
           sys.exit(1)
       
       enhancer = AsyncPromptEnhancer()
       result = await enhancer.enhance(prompt, timeout=60)
       
       if result['success']:
           # 只输出增强后的提示词到 stdout
           print(result['enhanced'])
       else:
           print(f"Error: {result['error']}", file=sys.stderr)
           sys.exit(1)

   if __name__ == "__main__":
       asyncio.run(main())
   ```

**工作流程**:
```
用户输入：/pe 修复登录页面的 bug
↓
Claude Code 加载 prompt-enhancement skill
↓
Claude 读取 SKILL.md 中的指令
↓
Claude 使用 Bash 工具执行：
  python ~/.claude/skills/prompt-enhancement/scripts/enhance.py "修复登录页面的 bug"
↓
enhance.py 调用 DeepSeek API（通过 async_prompt_enhancer.py）
↓
enhance.py 输出增强后的提示词到 stdout
↓
Claude 读取输出并使用增强后的提示词继续执行任务
```

**优点**:
- ✅ 完全可行（本地模式无网络限制）
- ✅ 符合 Claude Skills 的设计模式
- ✅ 用户体验流畅（一步完成）
- ✅ 可以调用外部 API

**缺点**:
- ⚠️ 仅适用于本地 Claude Code CLI
- ⚠️ 需要用户批准 Bash 工具执行（首次）
- ⚠️ 需要用户设置 DEEPSEEK_API_KEY 环境变量

---

### **方案 2: MCP Server（备选方案）**

**适用场景**: 需要支持云端 Claude Code 或更灵活的集成

**技术路径**:

创建 MCP Server 提供 `enhance_prompt` 工具：

```python
# mcp_prompt_enhancer.py
from mcp import Server, Tool
from async_prompt_enhancer import AsyncPromptEnhancer

server = Server("prompt-enhancer")

@server.tool()
async def enhance_prompt(prompt: str) -> dict:
    """Enhance a prompt using DeepSeek API"""
    enhancer = AsyncPromptEnhancer()
    result = await enhancer.enhance(prompt)
    return result

if __name__ == "__main__":
    server.run()
```

**配置**:
```json
// ~/.claude/mcp_servers.json
{
  "prompt-enhancer": {
    "command": "python3",
    "args": ["/path/to/mcp_prompt_enhancer.py"]
  }
}
```

**工作流程**:
```
用户输入：请先增强这个提示词再执行：修复登录页面的 bug
↓
Claude 识别需要增强提示词
↓
Claude 调用 enhance_prompt MCP 工具
↓
MCP Server 调用 DeepSeek API
↓
返回增强后的提示词
↓
Claude 使用增强后的提示词执行任务
```

**优点**:
- ✅ 使用标准 MCP 协议
- ✅ 可以与其他 MCP 工具组合
- ✅ 更灵活的集成方式

**缺点**:
- ❌ 不是斜杠命令，需要自然语言触发
- ❌ 用户体验不如 Skills 直观
- ❌ 需要 Claude 自己判断何时调用
- ⚠️ 云端模式可能仍有网络限制

---

## 📊 **方案对比**

| 维度 | 方案 1: Skill + Bash | 方案 2: MCP Server |
|-----|---------------------|-------------------|
| **触发方式** | `/pe` 或自然语言 | 自然语言 |
| **用户体验** | ⭐⭐⭐⭐⭐ 优秀 | ⭐⭐⭐ 一般 |
| **实现复杂度** | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐ 较高 |
| **本地模式支持** | ✅ 完全支持 | ✅ 完全支持 |
| **云端模式支持** | ❌ 可能受限 | ❌ 可能受限 |
| **网络请求** | ✅ 通过 Bash 执行 Python | ✅ MCP Server 执行 |
| **API 调用延迟** | 30-60 秒 | 30-60 秒 |
| **符合预期** | ✅ 完全符合 | ⚠️ 部分符合 |

---

## ✅ **最终推荐方案**

### **推荐：方案 1 - Skill + Bash 工具**

**理由**:
1. ✅ **完全符合用户预期**：可以实现 `/pe` 命令
2. ✅ **技术可行**：本地模式无网络限制
3. ✅ **用户体验最佳**：一步完成，无缝集成
4. ✅ **符合 Claude Skills 设计模式**：通过 Bash 工具执行脚本
5. ✅ **易于维护**：标准化的目录结构

**关键技术细节**:
- Skills 不执行代码，只提供提示词指令
- Claude 通过 Bash 工具执行 Python 脚本
- Python 脚本调用 DeepSeek API
- 本地模式无网络限制，完全可行

**需要注意的问题**:
1. ⚠️ **仅适用于本地 Claude Code CLI**
   - 云端模式可能受网络隔离限制
   - 建议在文档中明确说明

2. ⚠️ **首次使用需要用户批准**
   - Claude Code 会提示用户批准 Bash 工具执行
   - 可以通过 `allowed-tools` 预批准

3. ⚠️ **API 调用延迟**
   - DeepSeek API 调用需要 30-60 秒
   - 需要在 SKILL.md 中说明预期等待时间

4. ⚠️ **环境变量配置**
   - 用户需要设置 `DEEPSEEK_API_KEY`
   - 需要在安装文档中说明

---

## 🚀 **下一步行动**

1. ✅ **确认方案可行性**：已确认
2. ✅ **选择实现方案**：方案 1 - Skill + Bash 工具
3. ⏭️ **开始实现**：
   - Day 4: 创建 Skill 目录结构和 SKILL.md
   - Day 5: 实现 enhance.py 脚本
   - Day 6: 测试和优化
   - Day 7: 编写文档

---

**分析完成时间**: 2025-12-09  
**分析状态**: ✅ **已完成**  
**推荐方案**: 方案 1 - Skill + Bash 工具  
**可行性**: ✅ **完全可行**（本地模式）

