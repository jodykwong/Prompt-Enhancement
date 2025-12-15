# Prompt Enhancement v1.1 - API 参考文档

**版本**: 1.1.0
**日期**: 2025-12-15

---

## 目录

1. [概述](#概述)
2. [AgentDocParser](#agentdocparser)
3. [ClarityScorer](#clarityscorer)
4. [Clarifier](#clarifier)
5. [ContextCollector (升级)](#contextcollector-升级)
6. [EnhancedPromptGenerator (升级)](#enhancedpromptgenerator-升级)
7. [ResponseCache](#responsecache)
8. [数据类型](#数据类型)
9. [错误处理](#错误处理)

---

## 概述

v1.1 API 在现有 context_collector 和 enhanced_prompt_generator 基础上，新增了 4 个模块：

| 模块 | 职责 | P0/P1 | 状态 |
|------|------|-------|------|
| **AgentDocParser** | 解析 AGENTS.md | P0 | 核心 |
| **ClarityScorer** | 评估意图明确度 | P0 | 核心 |
| **Clarifier** | 交互问询 | P1 | 可选 |
| **ResponseCache** | 缓存优化 | P1 | 可选 |

---

## AgentDocParser

### 类定义

```python
from agent_docs_parser import AgentDocParser, AgentConfig
```

### 初始化

```python
# 基础初始化
parser = AgentDocParser()

# 带日志的初始化
parser = AgentDocParser(logger=logging.getLogger(__name__))
```

### 方法

#### `find_config_file(project_root, force_source=None) -> Optional[str]`

**功能**: 查找 AGENTS.md 文件

**参数**:
- `project_root` (str): 项目根目录路径
- `force_source` (Optional[str]): 强制指定的源文件名

**返回**: 找到的文件路径，或 None

**异常**: `FileNotFoundError` - 如果强制指定的文件不存在

**示例**:
```python
# 自动查找
config_file = parser.find_config_file(".")

# 强制指定
config_file = parser.find_config_file(".", force_source="AGENTS.md")

# 处理多个文件（会选择优先级最高的）
config_file = parser.find_config_file(".")
# 如果找到多个，日志会显示警告
```

**搜索优先级**:
1. `./AGENTS.md`
2. `./CLAUDE.md`
3. `./.github/copilot-instructions.md`
4. `./.github/agents/*.md`
5. `./.bmad/**/*.md`

---

#### `parse(file_path) -> AgentConfig`

**功能**: 解析 AGENTS.md 文件

**参数**:
- `file_path` (str): 文件路径

**返回**: `AgentConfig` 对象

**异常**: 解析失败时返回空的 `AgentConfig`

**示例**:
```python
config = parser.parse("./AGENTS.md")

# 访问解析结果
print(config.commands)      # List[str]
print(config.guidelines)    # List[str]
print(config.warnings)      # List[str]
print(config.boundaries)    # Dict
print(config.format_type)   # "structured" 或 "flexible"

# 检查有效性
if config.is_valid:
    # 有有效内容
    pass
```

---

#### `parse_from_content(content, source_name="inline") -> AgentConfig`

**功能**: 从字符串内容解析，不读取文件

**参数**:
- `content` (str): Markdown 内容
- `source_name` (str): 源文件名（用于日志）

**返回**: `AgentConfig` 对象

**示例**:
```python
content = """
## Commands
npm run test

## Code Style
- Type hints required
"""

config = parser.parse_from_content(content)
```

---

#### `detect_format(content) -> str`

**功能**: 检测格式类型

**参数**:
- `content` (str): Markdown 内容

**返回**: `"structured"` 或 `"flexible"`

**示例**:
```python
format_type = parser.detect_format(content)
# "structured" - 有明确的 ## Commands 等章节
# "flexible"  - 自由格式
```

---

### 数据类型

#### `AgentConfig` (数据类)

```python
@dataclass
class AgentConfig:
    source_file: str              # 源文件路径
    format_type: str              # "structured" 或 "flexible"
    raw_content: str              # 原始文件内容

    commands: List[str]           # 识别的命令
    guidelines: List[str]         # 代码规范
    boundaries: Dict[str, List]   # 边界约束
    warnings: List[str]           # 警告信息
    testing: Dict[str, str]       # 测试配置

    sections: Dict[str, str]      # 按标题组织的内容
    code_blocks: List[CodeBlock]  # 代码块列表

    last_modified: datetime       # 最后修改时间
    parse_errors: List[str]       # 解析错误列表

    @property
    def is_valid(self) -> bool:
        """检查是否有有效内容"""
```

**示例**:
```python
config = parser.parse("./AGENTS.md")

# 访问字段
for cmd in config.commands:
    print(f"Command: {cmd}")

for guideline in config.guidelines:
    print(f"Guideline: {guideline}")

for warning in config.warnings:
    print(f"Warning: {warning}")

# 访问嵌套结构
for boundary_type, items in config.boundaries.items():
    print(f"{boundary_type}: {items}")
```

---

#### `CodeBlock` (数据类)

```python
@dataclass
class CodeBlock:
    language: str                 # bash, python, js 等
    content: str                  # 代码内容
    line_number: int              # 源文件行号

config.code_blocks[0].language  # "bash"
config.code_blocks[0].content   # "npm run test"
```

---

## ClarityScorer

### 类定义

```python
from clarity_scorer import ClarityScorer
```

### 初始化

```python
# 基础初始化
scorer = ClarityScorer()

# 带上下文初始化
context = {
    "project_files": ["src/auth.py", "src/models.py"],
    "symbols": ["User", "authenticate", "login"]
}
scorer = ClarityScorer(context=context)
```

### 方法

#### `score(prompt) -> float`

**功能**: 计算 prompt 的意图明确度评分

**参数**:
- `prompt` (str): 用户输入的任务描述

**返回**: 0.0-1.0 之间的浮点数

**评分规则**:
- 0.6 - 1.0: 明确（直接增强）
- 0.3 - 0.6: 一般（可选问询）
- 0.0 - 0.3: 模糊（强制问询）

**示例**:
```python
# 明确的 prompt
score = scorer.score("为 src/auth/login.py 添加 JWT 认证")
# 返回: 0.85

# 一般的 prompt
score = scorer.score("添加用户登录功能")
# 返回: 0.45

# 模糊的 prompt
score = scorer.score("改进安全性")
# 返回: 0.25
```

---

#### `interpret(score) -> dict`

**功能**: 解释评分结果

**参数**:
- `score` (float): 评分值

**返回**:
```python
{
    "level": "clear" | "medium" | "unclear",
    "action": "direct_enhance" | "enhance_with_optional_clarify" | "force_clarify",
    "need_clarify": bool
}
```

**示例**:
```python
score = 0.25
interpretation = scorer.interpret(score)
# {
#     "level": "unclear",
#     "action": "force_clarify",
#     "need_clarify": True
# }

if interpretation["need_clarify"]:
    # 触发 Clarifier
    pass
```

---

## Clarifier

### 类定义

```python
from clarifier import Clarifier
```

### 初始化

```python
clarifier = Clarifier(templates_dir="skill_templates/clarifier")
```

### 方法

#### `find_template(prompt) -> Optional[str]`

**功能**: 根据 prompt 查找匹配的问询模板

**参数**:
- `prompt` (str): 用户 prompt

**返回**: 模板名称（不含 .yaml），或 None

**示例**:
```python
template_name = clarifier.find_template("添加 JWT 认证")
# 返回: "authentication"

template_name = clarifier.find_template("优化代码性能")
# 返回: "performance"

template_name = clarifier.find_template("不知道说什么")
# 返回: "general"
```

---

#### `clarify(prompt, answers) -> str`

**功能**: 根据用户回答澄清 prompt

**参数**:
- `prompt` (str): 原始 prompt
- `answers` (dict): 用户对问题的回答

**返回**: 澄清后的 prompt

**示例**:
```python
answers = {
    "auth_method": "jwt",
    "third_party": "是（Google/GitHub）",
    "mfa": "是"
}

clarified = clarifier.clarify(
    "添加认证功能",
    answers
)
# 返回: "为项目添加认证功能，使用 JWT Token，支持 Google 和 GitHub 登录，实现双因素认证"
```

---

#### `interactive_clarify(prompt) -> tuple[str, dict]`

**功能**: 交互式澄清流程

**参数**:
- `prompt` (str): 原始 prompt

**返回**: (澄清后的 prompt, 用户回答字典)

**示例**:
```python
# 这在 CLI 中使用
clarified_prompt, answers = clarifier.interactive_clarify(
    "改进安全性"
)

# 流程：
# [1/3] 关注哪类安全问题？
#   (1) XSS 跨站脚本
#   (2) SQL 注入
#   (3) 认证/授权
# > 3
#
# [2/3] 有哪些代码需要重点关注？
# > auth/ api/
#
# ...
```

---

## ContextCollector (升级)

### 变更

v1.1 的 `ContextCollector` 新增了对 AGENTS.md 的支持。

### 方法

#### `collect(project_root, config_file=None) -> EnhancementContext`

**功能**: 收集完整的增强上下文

**参数**:
- `project_root` (str): 项目根目录
- `config_file` (Optional[str]): AGENTS.md 文件路径

**返回**: `EnhancementContext` 对象

**新增字段** (v1.1):
- `agents_config: AgentConfig` - 解析后的 AGENTS.md 配置
- `clarity_score: float` - 意图明确度评分
- `clarity_level: str` - 明确度级别

**示例**:
```python
from context_collector import ContextCollector

collector = ContextCollector()
context = collector.collect(".")

# 访问新字段
print(context.agents_config.commands)
print(context.clarity_score)  # 0.0-1.0

# 现有字段仍然可用
print(context.tech_stack)
print(context.project_structure)
```

---

## EnhancedPromptGenerator (升级)

### 变更

v1.1 的 `EnhancedPromptGenerator` 新增了 3 个输出区块。

### 方法

#### `generate(context) -> EnhancedPrompt`

**功能**: 生成增强 prompt

**参数**:
- `context` (EnhancementContext): 增强上下文

**返回**: `EnhancedPrompt` 对象

**新增字段** (v1.1):
- `project_norms: str` - 项目规范（来自 AGENTS.md）
- `boundary_constraints: str` - 边界约束（⚠️）
- `special_warnings: str` - 特别警告（🚨）
- `clarified_task: Optional[str]` - 澄清后的任务

**示例**:
```python
from enhanced_prompt_generator import EnhancedPromptGenerator

generator = EnhancedPromptGenerator()
enhanced = generator.generate(context)

# 访问新字段
print(enhanced.project_norms)
print(enhanced.boundary_constraints)
print(enhanced.special_warnings)
print(enhanced.clarified_task)

# 现有字段仍然可用
print(enhanced.project_context)
print(enhanced.relevant_files)
```

---

#### `format_output(prompt, format="markdown") -> str`

**功能**: 格式化输出

**参数**:
- `prompt` (EnhancedPrompt): 增强后的 prompt 对象
- `format` (str): 输出格式（"markdown" 或 "plain"）

**返回**: 格式化的字符串

**示例**:
```python
# Markdown 格式（默认）
output = generator.format_output(enhanced, format="markdown")
print(output)

# 纯文本格式
output = generator.format_output(enhanced, format="plain")
```

---

## ResponseCache

### 类定义

```python
from response_cache import ResponseCache
```

### 初始化

```python
cache = ResponseCache(cache_dir=".pe-cache")
```

### 方法

#### `get_or_compute(key, compute_fn, ttl_seconds=300) -> tuple[Any, bool]`

**功能**: 获取缓存或计算新值

**参数**:
- `key` (str): 缓存键
- `compute_fn` (callable): 计算函数
- `ttl_seconds` (int): 缓存过期时间（秒）

**返回**: (结果值, 是否命中缓存) 的元组

**示例**:
```python
# 缓存上下文收集结果
def collect_context():
    return collector.collect(".")

context, cache_hit = cache.get_or_compute(
    key="context:main",
    compute_fn=collect_context,
    ttl_seconds=300
)

print(f"Cache hit: {cache_hit}")
```

---

#### `watch_file(file_path) -> None`

**功能**: 监控文件变更，自动失效缓存

**参数**:
- `file_path` (str): 要监控的文件路径

**示例**:
```python
# 监控 AGENTS.md，当它变更时自动失效缓存
cache.watch_file("./AGENTS.md")
cache.watch_file("./.claude/commands/pe.md")
```

---

#### `clear() -> None`

**功能**: 清空所有缓存

**示例**:
```python
cache.clear()
```

---

## 数据类型

### EnhancementContext

```python
@dataclass
class EnhancementContext:
    # 输入
    user_prompt: str

    # AGENTS.md 配置
    agents_config: AgentConfig

    # 意图评估
    clarity_score: float
    clarity_level: str  # "clear" / "medium" / "unclear"

    # 澄清
    clarified_prompt: Optional[str] = None
    clarification_answers: Optional[dict] = None

    # 项目上下文（现有）
    tech_stack: dict
    project_structure: dict
    git_history: dict
    relevant_files: List[str]
    code_snippets: dict

    # 缓存
    cache_hit: bool = False
    cache_age_seconds: Optional[int] = None
```

---

### EnhancedPrompt

```python
@dataclass
class EnhancedPrompt:
    # 输入
    original_prompt: str
    clarity_score: float

    # 新增区块 (v1.1)
    project_norms: str
    boundary_constraints: str
    special_warnings: str
    clarified_task: Optional[str] = None

    # 现有区块
    project_context: str
    relevant_files: str
    code_snippets: str
    best_practices: str

    # 元数据
    generation_time_ms: float
    cache_hit: bool
    agents_config_source: str
```

---

## 错误处理

### 异常类型

```python
# 文件不找异常
from agent_docs_parser import FileNotFoundError

# 解析异常
from agent_docs_parser import ParseError

# 缓存异常
from response_cache import CacheError
```

### 错误处理最佳实践

```python
# 示例 1：安全的 AGENTS.md 解析
parser = AgentDocParser()
try:
    config_file = parser.find_config_file(".")
    config = parser.parse(config_file) if config_file else AgentConfig.empty()
except Exception as e:
    logger.error(f"Failed to parse AGENTS.md: {e}")
    config = AgentConfig.empty()  # 优雅降级

# 示例 2：缓存失败处理
cache = ResponseCache()
try:
    result, hit = cache.get_or_compute(
        key="main_context",
        compute_fn=compute_fn,
        ttl_seconds=300
    )
except CacheError:
    # 缓存失败，直接计算
    result = compute_fn()
```

---

## 集成示例

### 完整的增强流程

```python
from agent_docs_parser import AgentDocParser
from clarity_scorer import ClarityScorer
from clarifier import Clarifier
from context_collector import ContextCollector
from enhanced_prompt_generator import EnhancedPromptGenerator
from response_cache import ResponseCache

def enhance_prompt(user_prompt: str, project_root: str = ".") -> str:
    """
    完整的 prompt 增强流程
    """
    # 1. 初始化组件
    parser = AgentDocParser()
    scorer = ClarityScorer()
    clarifier = Clarifier()
    collector = ContextCollector()
    generator = EnhancedPromptGenerator()
    cache = ResponseCache()

    # 2. 收集上下文
    context, cache_hit = cache.get_or_compute(
        key="context:main",
        compute_fn=lambda: collector.collect(project_root)
    )

    # 3. 评分
    score = scorer.score(user_prompt)
    context.clarity_score = score

    # 4. 澄清（如果需要）
    interpretation = scorer.interpret(score)
    if interpretation["need_clarify"]:
        clarified, answers = clarifier.interactive_clarify(user_prompt)
        context.clarified_prompt = clarified
        context.clarification_answers = answers
    else:
        context.clarified_prompt = user_prompt

    # 5. 生成
    enhanced = generator.generate(context)

    # 6. 格式化输出
    output = generator.format_output(enhanced)

    return output

# 使用
result = enhance_prompt("为 src/auth 添加 JWT 认证")
print(result)
```

---

## CLI 集成

### /pe 命令

```bash
# 基本用法
pe "添加 JWT 认证"

# 强制交互模式
pe -i "改进安全性"

# 跳过问询
pe --no-clarify "优化代码"

# 跳过缓存
pe --no-cache "修复 bug"

# 详细输出
pe --verbose "添加测试"
```

---

## 性能提示

1. **缓存优化**
   ```python
   # 第一次调用会计算，后续 5 分钟内使用缓存
   result, hit = cache.get_or_compute(key, fn, ttl_seconds=300)
   ```

2. **文件监控**
   ```python
   # 监控 AGENTS.md，变更时自动失效缓存
   cache.watch_file("./AGENTS.md")
   ```

3. **批量处理**
   ```python
   # 避免重复解析，缓存 AgentConfig
   config = cache.get_or_compute("agents_config", parse_agents_md)
   ```

---

**文档完成时间**: 2025-12-15
**API 版本**: 1.1.0
**兼容版本**: 1.0+
