# 提示词增强功能 - 完整设计文档

**项目名称**：Prompt Enhancement for Claude Code
**版本**：2.0
**作者**：BMAD Master + 专家团队
**日期**：2025-12-11
**状态**：设计阶段

---

## 📋 目录

1. [执行摘要](#执行摘要)
2. [项目背景](#项目背景)
3. [当前架构分析](#当前架构分析)
4. [功能需求](#功能需求)
5. [技术设计](#技术设计)
6. [集成策略](#集成策略)
7. [性能优化](#性能优化)
8. [实现路线图](#实现路线图)

---

## 执行摘要

### 项目愿景
为 Claude Code 集成一个智能提示词增强系统，利用项目上下文和 AI 模型自动优化用户的提示词，使其更清晰、更具体、更容易执行。

### 核心价值
- **效率提升**：用户不需要手动优化提示词
- **质量提升**：AI 增强提示包含最佳实践和项目特定知识
- **上下文感知**：系统理解项目的技术栈和架构
- **无缝集成**：以 Claude Code 斜杠命令形式提供

### 当前状态
- ✅ 核心增强引擎已实现
- ✅ 项目上下文收集已实现
- ✅ DeepSeek API 集成已实现
- ✅ `/pe` 斜杠命令已配置
- ✅ 路径和配置问题已修复

---

## 项目背景

### 问题陈述
用户在使用 Claude Code 时常常：
1. **提示词不够详细**：缺乏项目背景信息
2. **缺少最佳实践**：没有考虑编码规范和设计模式
3. **验收标准模糊**：不清楚成功的定义
4. **手动优化耗时**：需要多次迭代才能获得好的结果

### 解决方案
提示词增强系统通过：
1. **自动收集上下文**：扫描项目结构、技术栈、Git 历史
2. **智能分析**：理解用户的意图和项目的特点
3. **结构化增强**：生成包含步骤、标准、最佳实践的增强版本
4. **一键体验**：用户只需输入 `/pe 提示词` 即可

---

## 当前架构分析

### 系统组成

```
┌─────────────────────────────────────────────────────┐
│                   Claude Code                       │
│  ┌──────────────────────────────────────────────┐  │
│  │  /pe 斜杠命令                                 │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│        .claude/commands/scripts/enhance.py          │
│  (命令入口点，参数验证，环境检查)                   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│    enhanced_prompt_generator.py                     │
│  (增强器集成，上下文注入，结果处理)                 │
└─────────────────────────────────────────────────────┘
                        ↓
        ┌───────────────┴───────────────┐
        ↓                               ↓
┌──────────────────────┐      ┌──────────────────────┐
│ context_collector.py │      │async_prompt_enhance │
│ (上下文收集)         │      │r.py (AI 增强)       │
├──────────────────────┤      ├──────────────────────┤
│ • Tech Stack Detect  │      │ • DeepSeek API      │
│ • Project Structure  │      │ • 异步处理          │
│ • Git History        │      │ • 超时控制          │
│ • Configuration      │      │ • 进度回调          │
└──────────────────────┘      └──────────────────────┘
```

### 核心模块

#### 1. **async_prompt_enhancer.py** - 异步增强引擎
**职责**：调用 DeepSeek API，执行 AI 增强
```python
async def enhance(
    original_prompt: str,
    timeout: int = 60,
    progress_callback: Optional[Callable] = None,
    cancel_token: Optional[asyncio.Event] = None
) -> Dict[str, Any]
```

**特点**：
- ✅ 异步 I/O，不阻塞主线程
- ✅ 进度回调，实时反馈
- ✅ 超时控制，防止无限等待
- ✅ 取消机制，支持用户中断

#### 2. **context_collector.py** - 上下文收集器
**职责**：收集项目上下文，生成背景信息
```python
def collect_project_context(
    project_path: str
) -> Dict[str, Any]
```

**收集内容**：
- 技术栈检测（框架、语言、依赖）
- 项目结构分析（目录树、关键文件）
- Git 历史分析（最近提交、分支模式）
- 配置文件读取（package.json、tsconfig.json 等）

#### 3. **enhanced_prompt_generator.py** - 增强器集成
**职责**：整合上下文和增强器，返回最终结果
```python
async def enhance_prompt_with_context(
    prompt: str,
    project_path: Optional[str] = None,
    timeout: int = 60,
    progress_callback: Optional[Callable] = None,
    cancel_token: Optional[asyncio.Event] = None
) -> Dict[str, Any]
```

**工作流**：
1. 收集项目上下文（可选）
2. 将上下文注入提示词
3. 调用异步增强器
4. 返回增强结果

#### 4. **enhance.py** - Claude Code 命令脚本
**职责**：处理 Claude Code 集成，参数验证，输出格式化

**流程**：
1. 验证环境变量（DEEPSEEK_API_KEY）
2. 解析命令行参数
3. 调用增强器
4. 输出结果（stdout/stderr）

---

### 数据流

```
用户输入
  /pe "修复登录 bug"
    ↓
解析参数
    ↓
收集上下文
  • 项目结构
  • 技术栈
  • Git 历史
    ↓
注入上下文到提示词
  "# 项目背景
   技术栈：...
   项目结构：...

   ---

   用户请求：修复登录 bug"
    ↓
调用 DeepSeek API
  [AI 处理]
    ↓
返回增强结果
  {
    "original": "修复登录 bug",
    "enhanced": "详细的增强版本...",
    "reasoning": "思考过程...",
    "stats": {...}
  }
    ↓
显示对比
  📝 原始：...
  ✨ 增强：...
```

---

## 功能需求

### 已实现功能 ✅

| 功能 | 状态 | 说明 |
|------|------|------|
| AI 提示词增强 | ✅ | 使用 DeepSeek 模型 |
| 项目上下文收集 | ✅ | 自动检测技术栈和项目结构 |
| 异步处理 | ✅ | 非阻塞 I/O |
| 进度反馈 | ✅ | 支持进度回调 |
| 超时控制 | ✅ | 可配置超时 |
| 取消机制 | ✅ | 支持用户中断 |
| Claude Code 集成 | ✅ | `/pe` 斜杠命令 |
| 环境变量支持 | ✅ | .env 文件配置 |

### 计划功能 🔄

#### Phase 2 - 增强功能
- [ ] **缓存机制**：避免重复增强相同的提示词
  - 实现提示词指纹识别
  - Redis 或本地缓存存储
  - 缓存失效策略

- [ ] **多模型支持**：支持多种 AI 模型
  - GPT-4、Claude、Gemini 等
  - 模型性能对比
  - 自动选择最优模型

- [ ] **增强模板**：不同场景的定制模板
  - Bug 修复模板
  - 新功能实现模板
  - 代码重构模板
  - 性能优化模板

- [ ] **交互式增强**：用户反馈循环
  - 增强后可修改参数再次增强
  - 保存增强历史
  - 模板学习和优化

#### Phase 3 - 高级功能
- [ ] **智能上下文剔除**：避免过大的上下文
  - 相关性分析
  - 上下文大小优化
  - 关键信息提取

- [ ] **批量增强**：一次增强多个提示词
  - 批处理接口
  - 进度追踪
  - 结果导出

- [ ] **本地化增强**：支持多种语言
  - 自动语言检测
  - 多语言输出
  - 文化适配

- [ ] **提示词分析**：提供增强建议而不是直接增强
  - 质量评分
  - 改进建议
  - 最佳实践提示

---

## 技术设计

### 架构决策

#### 1. 为什么使用 DeepSeek？
✅ **优点**：
- 开源、性价比高
- 支持长上下文
- API 友好
- 推理能力强

⚠️ **缺点**：
- 模型还在优化阶段
- 响应时间较长（可能 20-30 秒）

**替代方案**：
- OpenAI GPT-4：更稳定，但成本更高
- Anthropic Claude：API 私有，不公开
- Llama 本地化：需要本地部署

#### 2. 为什么使用异步架构？
✅ **原因**：
- Claude Code 是事件驱动的环境
- 长时间的 API 调用需要异步处理
- 支持进度反馈和取消机制
- 更好的响应性

#### 3. 为什么分离上下文收集？
✅ **原因**：
- 上下文收集是 I/O 密集的（文件读取）
- 可以独立测试和优化
- 支持可选的上下文注入
- 便于添加新的上下文源

---

### API 设计

#### 命令行接口

```bash
/pe <prompt_text>
```

**参数**：
- `prompt_text`：原始提示词（必需）

**环境变量**：
- `DEEPSEEK_API_KEY`：API 密钥（必需）
- `CLAUDE_PROJECT_DIR`：项目根目录（可选，Claude Code 提供）

**输出**：
- 成功：增强后的提示词输出到 stdout
- 失败：错误消息输出到 stderr，exit code 1

#### Python API

```python
from enhanced_prompt_generator import enhance_prompt_with_context

# 基础使用
result = await enhance_prompt_with_context(
    "修复 bug",
    project_path="/path/to/project"
)

# 完整使用
result = await enhance_prompt_with_context(
    "修复 bug",
    project_path="/path/to/project",
    timeout=120,
    progress_callback=async_progress_handler,
    cancel_token=cancel_event
)
```

**返回值**：
```python
{
    "original": str,              # 原始提示词
    "enhanced": str,              # 增强后的提示词
    "reasoning": str,             # 模型的思考过程
    "processing_time": float,     # 处理时间（秒）
    "success": bool,              # 是否成功
    "error": str,                 # 错误信息（如果失败）
    "stats": dict,                # 统计信息
    "context_injected": bool,     # 是否注入了上下文
    "context_summary": str        # 上下文摘要
}
```

---

### 模块依赖关系

```
requirements.txt:
├── python-dotenv          # 环境变量加载
├── aiohttp               # 异步 HTTP 请求
├── pydantic              # 数据验证
├── pyyaml                # YAML 配置解析
├── gitpython             # Git 历史分析
└── asyncio               # Python 标准库，异步支持
```

---

## 集成策略

### Claude Code 集成点

#### 1. 斜杠命令集成
```yaml
# .claude/commands/pe.md
---
description: Enhance prompts with AI
exec: .claude/commands/scripts/enhance.py
---
```

**工作流**：
1. 用户输入 `/pe 提示词`
2. Claude Code 解析命令
3. 执行 enhance.py 脚本
4. 脚本返回结果
5. Claude Code 显示输出

#### 2. 环境变量集成
Claude Code 自动设置：
- `CLAUDE_PROJECT_DIR`：当前项目目录
- `HOME`：用户主目录
- 其他系统环境变量

脚本利用这些变量：
```python
PROJECT_ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
```

#### 3. 错误处理集成
```python
# 成功：输出增强结果
print(result['enhanced'])
sys.exit(0)

# 失败：输出错误信息
print(f"❌ 错误: {error_message}", file=sys.stderr)
sys.exit(1)
```

Claude Code 会：
- 成功时显示 stdout 内容
- 失败时显示 stderr 内容
- 根据 exit code 判断成功/失败

---

### 与其他功能的集成

#### 与 Story/Task 系统的集成
```
当用户说："帮我实现这个需求"
  ↓
系统提议：先用 /pe 增强您的请求？
  ↓
用户选择：/pe [原始需求]
  ↓
系统显示：增强的需求 + 实现建议
  ↓
用户确认后：创建 Story 或开始实现
```

#### 与代码审查工作流的集成
```
代码审查发现问题
  ↓
建议用 /pe 增强修复说明
  ↓
生成更清晰的修复方案
  ↓
提交改进
```

---

## 性能优化

### 当前瓶颈分析

| 瓶颈 | 原因 | 影响 | 优化方案 |
|------|------|------|---------|
| API 延迟 | DeepSeek 响应时间 | 20-30 秒 | 使用更快的模型，预热请求 |
| 上下文收集 | 文件系统 I/O | 1-5 秒 | 缓存，按需收集 |
| 内存使用 | 大项目上下文 | 可能 OOM | 上下文大小限制，分段处理 |
| 启动时间 | 模块导入 | 2-3 秒 | 延迟导入，预编译 |

### 优化策略

#### 1. 缓存机制
```python
# 缓存项目上下文
class ContextCache:
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            # 移除最旧的条目
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value
```

**缓存策略**：
- 按项目路径缓存上下文
- 设置 TTL（Time To Live），比如 1 小时
- Git 更新时自动失效缓存

#### 2. 增量上下文收集
```python
# 只收集必要的上下文
class SmartContextCollector:
    def collect(self, project_path, max_size_mb=1):
        # 只收集文件大小 < 1MB 的项目
        # 只扫描前 100 个文件
        # 跳过 node_modules、.git 等
        pass
```

#### 3. 并发请求优化
```python
# 如果支持批量增强，使用连接池
async def batch_enhance(prompts: List[str]) -> List[Dict]:
    tasks = [enhance(p) for p in prompts]
    return await asyncio.gather(*tasks)
```

#### 4. 响应流式处理
```python
# 实现流式响应，边生成边返回
async def enhance_streaming(prompt: str):
    async for chunk in api_stream(prompt):
        yield chunk  # 实时返回
```

---

## 实现路线图

### Phase 1 - 基础功能（已完成）✅
**时间线**：现在 - 完成
**目标**：确保 `/pe` 命令可用和稳定

**任务清单**：
- [x] 核心增强引擎实现
- [x] 项目上下文收集实现
- [x] DeepSeek API 集成
- [x] 异步处理和进度反馈
- [x] Claude Code `/pe` 命令集成
- [x] 修复路径和配置问题
- [x] 编写测试用例
- [x] 文档完整

**交付物**：
- 可用的 `/pe` 命令
- 完整的 Python API
- 测试用例和文档

---

### Phase 2 - 增强功能（计划）🔄
**时间线**：2 - 4 周
**目标**：提升功能完整性和用户体验

**任务清单**：
- [ ] 实现缓存机制
  - 项目上下文缓存
  - 提示词增强结果缓存
  - 缓存失效和更新策略

- [ ] 多模型支持
  - 抽象模型接口
  - 支持 OpenAI、Anthropic 等
  - 模型性能基准测试

- [ ] 增强模板系统
  - Bug 修复模板
  - 新功能模板
  - 重构模板
  - 用户自定义模板

- [ ] 交互式增强
  - 增强后修改参数再试
  - 历史记录保存
  - 评分和反馈

**优先级**：
1. 缓存机制（最重要，提升性能）
2. 多模型支持（增加灵活性）
3. 增强模板（改善用户体验）
4. 交互式增强（高级功能）

---

### Phase 3 - 高级功能（远期）📅
**时间线**：1 - 2 个月
**目标**：成为一个完整的提示词工程平台

**任务清单**：
- [ ] 智能上下文管理
  - 上下文相关性评分
  - 自动剔除不相关部分
  - 上下文大小优化

- [ ] 批量处理
  - 批量增强接口
  - 进度追踪
  - 结果导出（JSON、CSV、Markdown）

- [ ] 多语言支持
  - 自动语言检测
  - 多语言输出
  - 文化适配

- [ ] 提示词分析工具
  - 质量评分
  - 改进建议
  - 与最佳实践的对比

- [ ] 提示词库
  - 社区提示词分享
  - 版本控制
  - 使用统计

---

### Phase 4 - 生产优化（长期）🚀
**时间线**：持续改进
**目标**：生产级质量和性能

**任务清单**：
- [ ] 性能优化
  - 响应时间 < 10 秒
  - 内存使用 < 500MB
  - 100% 可用性

- [ ] 安全加固
  - API 密钥加密存储
  - 输入验证和清理
  - 速率限制和反滥用

- [ ] 监控和日志
  - 详细的执行日志
  - 性能指标收集
  - 错误追踪和告警

- [ ] 持续集成
  - 自动化测试
  - 代码质量检查
  - 发布流程自动化

---

## 实现优先级和估算

### 关键功能优先级矩阵

```
HIGH IMPACT  │  缓存机制    │  多模型支持
             │  模板系统    │
             └─────────────────────────→
             │  交互式增强  │
             │
LOW IMPACT   │
             │
LOW EFFORT                     HIGH EFFORT
```

### 建议实现顺序

1. **第一优先级（本周）**：
   - 验证 `/pe` 命令可用性 ✅ 已完成
   - 编写集成测试
   - 文档完善

2. **第二优先级（下周）**：
   - 实现缓存机制（性能最敏感）
   - 错误处理改进
   - 超时和重试逻辑

3. **第三优先级（2 周后）**：
   - 多模型支持
   - 增强模板系统
   - 用户反馈收集

---

## 总结和建议

### 项目成熟度
- **当前状态**：可用（MVP）
- **可靠性**：中等（需要更多测试）
- **可维护性**：良好（代码结构清晰）

### 立即建议
1. ✅ 修复路径问题 - 已完成
2. ✅ 测试 `/pe` 命令 - 就绪
3. 收集用户反馈 - 下一步
4. 实现缓存机制 - 性能关键

### 长期愿景
将提示词增强发展为：
- 完整的提示词工程平台
- 支持多种 AI 模型
- 社区驱动的提示词库
- 开源生态系统

---

## 附录

### A. 文件清单

```
.claude/
├── commands/
│   ├── pe.md                          # 命令定义
│   └── scripts/
│       └── enhance.py                 # 入口脚本
├── hooks/
│   ├── play-tts.sh
│   └── session-start-tts.sh

核心模块/
├── async_prompt_enhancer.py           # 异步增强引擎
├── context_collector.py               # 上下文收集器
├── enhanced_prompt_generator.py       # 增强器集成
├── tech_stack_detector.py             # 技术栈检测
├── project_structure_analyzer.py      # 项目结构分析
├── git_history_analyzer.py            # Git 历史分析
└── ...

文档/
├── PE_FIX_REPORT.md                   # 修复报告
├── DESIGN_DOCUMENT.md                 # 本文档
├── README.md                          # 快速开始
└── .claude/commands/pe.md             # 命令文档
```

### B. 关键代码示例

#### 基础增强
```python
from enhanced_prompt_generator import enhance_prompt_with_context
import asyncio

async def main():
    result = await enhance_prompt_with_context(
        "修复登录 bug",
        project_path="."
    )

    if result['success']:
        print(result['enhanced'])
    else:
        print(f"Error: {result['error']}")

asyncio.run(main())
```

#### 带进度反馈
```python
async def progress_handler(message: str, progress: float):
    print(f"{message}: {progress*100:.0f}%")

result = await enhance_prompt_with_context(
    "修复 bug",
    progress_callback=progress_handler
)
```

### C. 故障排除指南

| 问题 | 症状 | 解决方案 |
|------|------|---------|
| `/pe` 命令不可用 | "未识别的命令" | 运行 `git status`，检查是否有未保存的更改 |
| API 密钥无效 | "Authentication failed" | 检查 `.env` 文件中的 DEEPSEEK_API_KEY |
| 超时错误 | "Request timeout" | 检查网络连接，或增加超时时间 |
| 内存不足 | "Out of memory" | 限制上下文大小或使用更快的模型 |
| 路径错误 | "Project not found" | 确保 CLAUDE_PROJECT_DIR 环境变量设置正确 |

---

**文档版本**：1.0
**最后更新**：2025-12-11
**审核状态**：BMAD Master + 多领域专家审核完毕
