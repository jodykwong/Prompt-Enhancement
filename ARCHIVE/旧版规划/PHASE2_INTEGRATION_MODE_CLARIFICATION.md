# 阶段 2: 集成模式澄清报告

**日期**: 2025-12-09  
**状态**: ✅ **已澄清**

---

## 🎯 **核心问题**

用户询问：当前规划的集成模式是什么？是否符合"在 Claude Code 内部使用 `/pe` 命令"的预期？

---

## 📊 **当前规划的集成模式分析**

### **当前规划采用的是：模式 B - 独立 CLI 工具 + 管道集成模式**

根据 `PHASE2_CLI_INTEGRATION_PLAN.md` 的设计：

```bash
# 方案 A: 独立 CLI 工具（推荐）
prompt-enhance "修复登录 bug"

# 方案 B: 作为 Claude Code 的前置处理器
prompt-enhance "修复登录 bug" | claude-code

# 方案 C: 集成到 Claude Code（如果支持插件）
claude-code enhance "修复登录 bug"
```

**当前规划的核心特征**:
- ✅ 创建独立的 CLI 工具 `prompt-enhance`
- ✅ 通过管道/文件方式与 Claude Code 集成
- ✅ 用户需要在独立终端中先运行 `prompt-enhance`
- ❌ **不是** 在 Claude Code 内部使用斜杠命令

---

## 🔍 **Claude Code 的实际情况**

### **研究发现**

根据对 Claude Code 的研究（来自 Hacker News 讨论和官方文档）：

1. **Claude Code 支持斜杠命令（Slash Commands）**
   - Claude Code 确实支持斜杠命令系统
   - 用户可以在 Claude Code 内部使用 `/` 开头的命令
   - 示例：`/help`, `/clear`, `/subagent` 等

2. **Claude Code 支持自定义命令**
   - Claude Code 支持通过配置文件添加自定义命令
   - 可以通过 `CLAUDE.md` 文件定义项目级别的指令
   - 可以通过 Skills 系统添加可重用的技能

3. **Claude Code 的扩展机制**
   - **MCP (Model Context Protocol)**: 用于连接外部工具和 API
   - **Skills**: 用于定义可重用的指令和脚本
   - **Sub-agents**: 用于委派子任务
   - **Slash Commands**: 用于快速触发预定义的操作

---

## ✅ **用户预期 vs 当前规划**

### **用户预期：模式 A - Claude Code 插件模式**

```bash
# 在 Claude Code 内部使用斜杠命令
claude-code> /pe 修复登录页面的 bug
# Claude Code 内部调用 prompt-enhance，自动增强后执行
```

**用户预期的核心特征**:
- ✅ 在 Claude Code 内部直接使用
- ✅ 通过斜杠命令 `/pe` 触发
- ✅ 无需切换到独立终端
- ✅ 增强过程自动完成
- ✅ 增强后的提示词自动传递给 Claude Code

### **当前规划：模式 B - 独立 CLI 工具 + 管道集成模式**

```bash
# 在独立终端中先增强提示词
prompt-enhance "修复登录页面的 bug" | claude-code
```

**当前规划的核心特征**:
- ❌ 需要在独立终端中运行
- ❌ 需要手动输入完整命令
- ❌ 需要在两个工具之间切换
- ❌ 增强过程需要手动触发
- ❌ 用户体验不够流畅

---

## 🔄 **差异分析**

| 维度 | 用户预期（模式 A） | 当前规划（模式 B） | 差异 |
|-----|------------------|------------------|------|
| **调用位置** | Claude Code 内部 | 独立终端 | ❌ 不符合 |
| **触发方式** | `/pe` 斜杠命令 | `prompt-enhance` CLI 命令 | ❌ 不符合 |
| **用户体验** | 无缝集成 | 需要切换工具 | ❌ 不符合 |
| **自动化程度** | 自动增强 | 手动触发 | ❌ 不符合 |
| **工作流程** | 一步完成 | 两步完成 | ❌ 不符合 |

**结论**: **当前规划不符合用户预期**

---

## 💡 **修正方案：实现模式 A - Claude Code 插件模式**

### **技术实现路径**

基于 Claude Code 的扩展机制，有以下几种实现方式：

#### **方案 1: 使用 Claude Skills（推荐）**

**原理**: 
- Claude Skills 是 Claude Code 的官方扩展机制
- Skills 可以包含指令（Markdown）和可执行脚本（Python/Shell）
- Skills 会在需要时自动加载到上下文中

**实现步骤**:

1. **创建 Skill 目录结构**
   ```
   ~/.claude/skills/prompt-enhancement/
   ├── SKILL.md              # Skill 描述和使用说明
   ├── enhance.py            # 增强脚本（调用 async_prompt_enhancer.py）
   └── requirements.txt      # 依赖列表
   ```

2. **SKILL.md 内容**
   ```markdown
   # Prompt Enhancement Skill
   
   ## Description
   Automatically enhance user prompts using DeepSeek API to make them more detailed and effective.
   
   ## When to use
   Use this skill when the user wants to enhance a prompt before executing it.
   
   ## Usage
   When the user types `/pe <prompt>`, automatically:
   1. Call the enhance.py script with the prompt
   2. Wait for the enhanced result
   3. Use the enhanced prompt for the task
   
   ## Example
   User: /pe 修复登录页面的 bug
   System: [Enhancing prompt...]
   System: [Enhanced prompt ready, executing...]
   ```

3. **enhance.py 脚本**
   ```python
   #!/usr/bin/env python3
   import sys
   import asyncio
   from async_prompt_enhancer import AsyncPromptEnhancer
   
   async def main():
       if len(sys.argv) < 2:
           print("Usage: enhance.py <prompt>")
           sys.exit(1)
       
       prompt = " ".join(sys.argv[1:])
       enhancer = AsyncPromptEnhancer()
       result = await enhancer.enhance(prompt)
       
       if result['success']:
           print(result['enhanced'])
       else:
           print(f"Error: {result['error']}")
           sys.exit(1)
   
   if __name__ == "__main__":
       asyncio.run(main())
   ```

4. **用户使用方式**
   ```bash
   # 在 Claude Code 中
   claude-code> /pe 修复登录页面的 bug
   
   # Claude Code 自动：
   # 1. 识别 /pe 命令
   # 2. 加载 prompt-enhancement skill
   # 3. 调用 enhance.py 脚本
   # 4. 获取增强后的提示词
   # 5. 使用增强后的提示词执行任务
   ```

**优点**:
- ✅ 完全符合用户预期
- ✅ 使用 Claude Code 官方扩展机制
- ✅ 无缝集成，用户体验流畅
- ✅ 自动加载，无需手动配置
- ✅ 可以与其他 Skills 组合使用

**缺点**:
- ⚠️ 需要研究 Claude Skills 的具体实现细节
- ⚠️ 可能需要适配 Claude Code 的 Skill 规范

---

#### **方案 2: 使用 MCP Server（备选）**

**原理**:
- MCP (Model Context Protocol) 是 Claude 的工具调用协议
- 可以创建 MCP Server 提供 `enhance_prompt` 工具
- Claude Code 可以自动调用 MCP 工具

**实现步骤**:

1. **创建 MCP Server**
   ```python
   # mcp_prompt_enhancer.py
   from mcp import Server, Tool
   from async_prompt_enhancer import AsyncPromptEnhancer
   
   server = Server("prompt-enhancer")
   
   @server.tool()
   async def enhance_prompt(prompt: str) -> str:
       """Enhance a prompt using DeepSeek API"""
       enhancer = AsyncPromptEnhancer()
       result = await enhancer.enhance(prompt)
       return result['enhanced'] if result['success'] else prompt
   
   if __name__ == "__main__":
       server.run()
   ```

2. **配置 MCP Server**
   ```json
   // ~/.claude/mcp_servers.json
   {
     "prompt-enhancer": {
       "command": "python3",
       "args": ["/path/to/mcp_prompt_enhancer.py"]
     }
   }
   ```

3. **用户使用方式**
   ```bash
   # 在 Claude Code 中
   claude-code> 请先增强这个提示词再执行：修复登录页面的 bug
   
   # Claude Code 自动：
   # 1. 识别需要增强提示词
   # 2. 调用 enhance_prompt MCP 工具
   # 3. 获取增强后的提示词
   # 4. 使用增强后的提示词执行任务
   ```

**优点**:
- ✅ 使用标准 MCP 协议
- ✅ 可以与其他 MCP 工具组合
- ✅ 自动工具调用

**缺点**:
- ❌ 不是斜杠命令，需要自然语言触发
- ❌ 用户体验不如 Skills 直观
- ❌ 需要 Claude 自己判断何时调用

---

## 📝 **推荐方案总结**

### **最终推荐：方案 1 - 使用 Claude Skills**

**理由**:
1. ✅ **完全符合用户预期**: 可以实现 `/pe` 斜杠命令
2. ✅ **官方支持**: Claude Skills 是官方扩展机制
3. ✅ **用户体验最佳**: 无缝集成，一步完成
4. ✅ **易于维护**: 标准化的目录结构和规范
5. ✅ **可扩展性强**: 可以添加更多功能（如 `--show-reasoning`）

### **修正后的阶段 2 计划**

**核心变化**:
- ❌ 删除：创建独立 CLI 工具 `prompt-enhance`
- ✅ 新增：创建 Claude Skill `prompt-enhancement`
- ✅ 新增：实现 `/pe` 斜杠命令支持
- ✅ 新增：研究 Claude Skills 规范和最佳实践

---

## 🚀 **下一步行动**

1. **Day 4: 研究 Claude Skills**
   - 研究 Claude Skills 的官方文档
   - 了解 Skill 的目录结构和规范
   - 研究如何实现自定义斜杠命令

2. **Day 5-6: 实现 Prompt Enhancement Skill**
   - 创建 Skill 目录结构
   - 编写 SKILL.md 描述文件
   - 实现 enhance.py 脚本
   - 集成 async_prompt_enhancer.py

3. **Day 7: 测试和优化**
   - 测试 `/pe` 命令功能
   - 测试进度显示
   - 测试错误处理
   - 优化用户体验

4. **Day 8: 文档和发布**
   - 编写使用文档
   - 创建安装指南
   - 发布到 Skills 仓库（如果有）

---

**澄清完成时间**: 2025-12-09  
**澄清状态**: ✅ **已完成**  
**推荐方案**: 方案 1 - 使用 Claude Skills 实现 `/pe` 斜杠命令

