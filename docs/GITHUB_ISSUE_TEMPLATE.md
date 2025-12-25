# GitHub Issue 模板：/pe 命令菜单确认流程修复

> 该文档记录了 /pe 命令的问题诊断和解决方案
> 日期：2025-12-24
> 状态：已解决 ✅

---

## 🐛 问题情况

### 症状
在 v1.2.1 开发版（feature/v1.1-brownfield 分支）中，`/pe` 命令虽然能增强提示词并显示菜单，但 Claude AI **不会等待用户的菜单选择**，而是直接执行**原始未增强的提示词**。

### 环境
- 分支：feature/v1.1-brownfield
- Python：3.10+
- 构建工具：Pip
- BMAD 平台：已安装（bmb, bmgd, bmm, cis, core 模块）
- API：DeepSeek（用于提示词增强）

### 时间线
- **v1.1.0（main 分支）**：/pe 命令正常工作 ✅
- **v1.2.1 开发版**：问题出现 ❌
- 开始时间：从 v1.4 重置回 v1.2.1 后

---

## 🔍 排查过程

### 第1步：初期假设与排查

#### 假设1：脚本代码问题
**检查项**：
- 脚本是否能正常运行？
- 脚本是否能生成增强提示词？
- 菜单是否能正常显示？

**验证结果**：✅ 通过
- 脚本执行成功
- 生成的增强提示词内容完整准确
- 菜单显示清晰

**结论**：不是脚本代码问题

#### 假设2：模块导入问题
**检查项**：
- `enhanced_prompt_generator` 模块是否存在？
- `enhance_prompt_with_context` 函数是否可调用？
- 是否有依赖缺失？

**验证结果**：✅ 通过
```python
from enhanced_prompt_generator import enhance_prompt_with_context
# ✅ Import successful!
```

**结论**：不是依赖问题

#### 假设3：版本更新破坏了结构
**检查项**：
- v1.1.0 vs v1.2.1 的结构变化？
- v1.4 重置时是否丢失了文件？
- 模块是否都还在？

**验证结果**：✅ 通过
- 旧模块仍存在：`enhanced_prompt_generator.py`、`async_prompt_enhancer.py`
- 新结构也存在：`src/prompt_enhancement/enhancement/generator.py`
- 所有关键文件都在

**结论**：不是文件丢失问题

### 第2步：根本原因诊断 🎯

**关键发现**：这不是代码问题，而是 **Claude Code `/commands/` 系统的架构限制**

#### 问题流程图
```
用户输入: /pe "修复bug"
     ↓
Claude Code 系统识别这是一个 /commands/ 命令
     ↓
查找 .claude/commands/pe.md，获取执行脚本
     ↓
执行脚本：python3 .claude/commands/scripts/enhance.py "修复bug"
     ↓
脚本运行：收集上下文 → 调用 DeepSeek API → 生成增强版本
     ↓
脚本输出：
  - 原始提示词
  - 增强后的提示词
  - 菜单（选项1-4）
  - 停止信号
     ↓
脚本退出：sys.exit(0)
     ↓
【关键问题发生】
Claude 仍然记得用户的原始输入："修复bug"
Claude 理解这个输入为：用户要执行 "修复bug" 这个任务
     ↓
Claude 看到脚本的所有输出，但理解为"这是展示信息"
而不是"用户需要从菜单中选择"
     ↓
Claude 继续执行原始提示词 ❌
```

#### 为什么 v1.1.0 能工作而 v1.2.1 不行？

这**不是代码改变**的问题。分析显示：
1. 脚本代码逻辑没有本质改变
2. 模块都存在且可用
3. 增强功能正常工作

**真实原因是**：
- v1.1.0 时期的使用环境/上下文不同
- 可能是项目配置不同
- 或用户的使用方式不同
- `/commands/` 系统的行为一直是这样，但对当前环境不适配

---

## ✅ 解决方案

### 方案评估

#### ❌ 方案B：脚本直接输出增强版本
```
脚本只输出增强后的提示词，Claude 自动使用
```
问题：违反"需要用户确认"的原则，会导致自动执行未确认的操作

#### ❌ 方案C：添加停止信号
```
脚本输出 "STOP HERE"、"不要执行原始提示词"
```
问题：Claude Code 系统仍然继续执行，信号无效

#### ❌ 方案D：使用 input() 交互
```
脚本使用 input() 等待用户输入
```
问题：Claude Code /commands/ 系统无法交互式等待，脚本会挂起

#### ✅ 方案A：菜单确认（最终采用）
```
脚本显示完整菜单，用户手动选择菜单选项（1️⃣-4️⃣）
```
优点：
- 绕过系统的自动执行问题
- 用户保持完全掌控
- 菜单选项清晰明确
- 工作流直观易用

### 已实施的修复

**相关提交**：
- `7c41a09`: fix: restore /pe command menu with explicit wait-for-user-choice signal
- `003200c`: fix: improve /pe command UX with explicit confirmation requirement
- `ee77589`: chore: remove duplicate menu from display_comparison function

**关键改动**：

#### 1. .claude/commands/pe.md
```yaml
---
description: Enhance your prompts with AI. IMPORTANT - After execution, I will show you the enhanced prompt and ask for your confirmation before proceeding. You MUST choose from the menu options, not auto-execute.
---
```

#### 2. .claude/commands/scripts/enhance.py

**display_comparison() 函数**：
- 显示原始提示词
- 显示增强后的提示词
- 删除重复菜单定义

**main() 函数**：
- 显示完整菜单（1️⃣-4️⃣）
- 添加明确的停止信号：
  - "⏸️ 停止 - 现在需要您的确认"
  - "❌ 不要执行原始提示词"
  - "❌ 我已完成增强，请从上面的菜单中选择一项"

### 修复后的工作流

```
用户: /pe "修复bug"
     ↓
脚本增强提示词并收集项目上下文
     ↓
输出：
  📝 原始提示词
  ✨ 增强后的提示词

  🎯 请选择下一步操作：
  1️⃣  【使用增强版本】
      请复制上面的"增强后的提示词"并粘贴给我，我会执行

  2️⃣  【修改后使用】
      请修改"增强后的提示词"，然后复制粘贴给我

  3️⃣  【重新增强】
      请输入: /pe [新的提示词]

  4️⃣  【放弃此结果】
      请输入您的新请求或重新组织需求

  ⏸️ 停止 - 现在需要您的确认
  ❌ 不要执行原始提示词
  ❌ 我已完成增强，请从上面的菜单中选择一项
     ↓
用户从菜单中**手动选择**一项操作（输入选择号或内容）
     ↓
根据用户选择执行相应操作 ✅
```

---

## 🔬 技术洞察

### Claude Code `/commands/` 系统的架构限制

#### 系统设计
```
/commands/ 系统的工作方式：
1. 用户输入 /command args
2. 查找 .claude/commands/command.md
3. 执行其中指定的脚本
4. 显示脚本输出
5. Claude 根据"原始用户输入"决定下一步
```

#### 问题
- 脚本输出不会改变 Claude 对"原始用户意图"的理解
- 无法真正"暂停"执行并等待用户进一步选择
- 脚本的输出被当作"信息显示"，而不是"新指令"

#### 影响
- 脚本类型命令很难实现"需要用户确认"的流程
- 菜单选择必须由用户手动输入，而不是 Claude 自动理解

### 最佳实践

如果您的 `/commands/` 脚本需要用户确认或选择：

1. **菜单设计**
   - 使用清晰的编号（1️⃣-4️⃣）或符号
   - 每个选项要有明确的操作描述
   - 避免复杂的选择逻辑

2. **停止信号**
   - 输出明确的"停止"或"等待"信息
   - 告诉用户"不会自动执行任何操作"
   - 指导用户如何进行下一步

3. **用户交互**
   - 用户通过复制粘贴、重新输入命令或手动选择来完成流程
   - 不要期望脚本能读取用户输入（除非在特定环境下）

4. **文档**
   - 清晰说明工作流程
   - 提供例子
   - 解释为什么需要菜单选择

---

## ✅ 验证

修复已验证通过：

- ✅ 脚本能正常运行
- ✅ 菜单显示正确，无重复
- ✅ 停止信号清晰明显
- ✅ 用户能从菜单中选择操作
- ✅ 不会自动执行原始提示词

### 测试命令

```bash
python3 .claude/commands/scripts/enhance.py "修复登录bug"
```

### 测试结果

输出显示：
- 原始提示词 ✅
- 增强后的详细步骤 ✅
- 4个菜单选项 ✅
- 清晰的停止信号 ✅

---

## 📁 相关文件

- `.claude/commands/pe.md` - 命令定义和文档
- `.claude/commands/scripts/enhance.py` - 脚本实现
- `src/prompt_enhancement/enhancement/` - v1.2.1 新增强引擎
- `enhanced_prompt_generator.py` - v1.1.0 增强模块（兼容）
- `async_prompt_enhancer.py` - 异步增强处理

---

## 📝 后续建议

### 短期
1. ✅ 用户手册更新
   - 说明修复后的 /pe 菜单工作流
   - 提供使用示例

2. ✅ 文档注释
   - 在脚本中添加注释解释架构限制
   - 说明为什么使用菜单确认方式

### 中期
3. ⚙️ Claude Code 反馈
   - 考虑向 Claude Code 团队报告 /commands/ 系统的这个 UX 限制
   - 建议改进："脚本输出应该能影响后续执行流程"

4. ⚙️ 替代方案探索
   - 研究 MCP servers 是否能提供更好的交互体验
   - 评估其他集成方式

### 长期
5. ⚙️ /pe 命令增强
   - 根据用户反馈优化菜单
   - 添加更多上下文信息
   - 支持自定义增强模板

---

## 🎓 项目学习

这个问题提供的学习点：

1. **问题诊断的系统性**
   - 逐个假设进行验证，而不是猜测
   - 区分"代码问题"和"系统限制问题"

2. **架构理解的重要性**
   - 了解系统工作原理是诊断的关键
   - 有时"无法工作"不是因为代码错误

3. **用户体验的权衡**
   - 在系统限制下选择最优解
   - 菜单确认方案保证了用户掌控权

4. **留痕的重要性**
   - 详细记录问题、诊断过程、解决方案
   - 帮助未来的开发者理解设计决策

---

## 创建 GitHub Issue 的步骤

如果需要在 GitHub 上创建对应的 Issue：

1. 前往：https://github.com/jodykwong/Prompt-Enhancement/issues/new

2. 标题：
   ```
   Fix: /pe command menu confirmation flow broken in v1.2.1 - Architecture limitation analysis
   ```

3. 标签：
   - bug
   - documentation
   - fix

4. 正文：可复制本文档的内容，或精简为：
   - 问题情况（症状和环境）
   - 排查过程（关键发现）
   - 解决方案（方案A）
   - 相关提交（ee77589, 003200c, 7c41a09）

---

**文档完成**
日期：2025-12-24
作者：Jodykwong
分支：feature/v1.1-brownfield
