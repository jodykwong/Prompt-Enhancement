# Phase 1-3 集成流程文档

**版本**: v1.2.1
**状态**: ✅ Phase 1-3 完成
**最后更新**: 2025-12-25

---

## 概述

Prompt Enhancement v1.2.1 的前三个阶段（Phase 1-3）构成了完整的**代码项目智能增强流程**。本文档描述三个阶段如何协同工作，从用户的模糊指令开始，最终生成增强的结构化提示词。

### 完整流程图

```
┌─────────────────────────────────────────────────────────────┐
│ 用户输入: "添加用户认证功能"                                  │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: 智能文件发现                                        │
├─────────────────────────────────────────────────────────────┤
│ 【输入】用户的模糊指令                                        │
│ 【处理】                                                     │
│   1. KeywordExtractor → 提取关键词                          │
│   2. FileMatcher → 在代码库中匹配相关文件                    │
│ 【输出】按相关性排序的文件列表 (Top 5-10)                    │
│                                                              │
│ 示例:                                                       │
│   输入: "添加用户认证"                                       │
│   ↓                                                          │
│   关键词: ['认证', 'auth', '用户', 'user']                   │
│   ↓                                                          │
│   发现文件: [auth.py, user.py, models.py, ...]             │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: 符号索引                                            │
├─────────────────────────────────────────────────────────────┤
│ 【输入】Phase 1 发现的文件列表                               │
│ 【处理】                                                     │
│   1. SymbolIndexer → 逐文件提取符号                         │
│      - Python: 使用 AST 解析                                │
│      - JavaScript: 使用正则提取                              │
│   2. SymbolCache → 缓存索引结果                             │
│      - 内存缓存（快速访问）                                  │
│      - 磁盘缓存（跨会话持久化）                              │
│ 【输出】函数/类签名而非完整代码                               │
│                                                              │
│ 示例:                                                       │
│   输入文件: auth.py                                         │
│   ↓                                                          │
│   提取符号:                                                  │
│     - def authenticate(username: str, password: str) → bool │
│     - class User: __init__(self, username, email)          │
│     - async def verify_token(token: str) → Optional[User]  │
│   ↓                                                          │
│   缓存策略: 文件哈希 + 磁盘持久化                            │
│                                                              │
│ 优势:                                                       │
│   - 减少 token 使用量 50%+                                   │
│   - 保留关键信息，去除冗余代码                               │
│   - 缓存命中率 >95%                                          │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: 编码模板系统                                        │
├─────────────────────────────────────────────────────────────┤
│ 【输入】                                                     │
│   - 用户的原始指令（"添加用户认证"）                         │
│   - Phase 1-2 的发现结果（文件和符号）                      │
│ 【处理】                                                     │
│   1. TemplateTrigger → 匹配任务类型                         │
│      - 识别指令中的触发词（添加→implement）                 │
│      - 计算匹配置信度 (0.0-1.0)                            │
│   2. CodingTemplateManager → 加载对应模板                  │
│      - 5 种任务模板: implement/fix/refactor/test/review    │
│      - 每个模板包含: 检查清单、最佳实践、验收标准           │
│   3. 应用语言特定的指导                                      │
│      - 检测项目主语言（Python/JavaScript/Java/Go）        │
│      - 应用语言特定的最佳实践                               │
│ 【输出】增强的结构化提示词                                    │
│                                                              │
│ 示例:                                                       │
│   输入指令: "添加用户认证"                                  │
│   ↓                                                          │
│   检测任务: implement (confidence: 100%)                   │
│   ↓                                                          │
│   应用模板: implement.yaml                                 │
│   ↓                                                          │
│   应用语言: Python (从 Phase 2 检测)                        │
│   ↓                                                          │
│   增强输出:                                                  │
│     ✓ 相关文件列表 (auth.py, user.py, ...)                │
│     ✓ 现有代码结构 (authenticate(), User class, ...)      │
│     ✓ 实现清单 (设计接口, 实现逻辑, 编写测试, ...)         │
│     ✓ Python 最佳实践 (类型注解, docstring, ...)           │
│     ✓ 常见陷阱提醒 (避免硬编码, 检查输入, ...)            │
│     ✓ 验收标准 (所有测试通过, 覆盖率>80%, ...)            │
│                                                              │
│ 性能优化:                                                   │
│   - 初始化: 0.17ms (懒加载)                                 │
│   - 单模板加载: 33.6ms                                      │
│   - 格式化缓存: 0.01ms (13x 性能提升)                       │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│ 最终输出: 增强的结构化提示词                                  │
├─────────────────────────────────────────────────────────────┤
│ • 自动发现的相关文件列表                                     │
│ • 现有代码函数/类的签名                                      │
│ • 分步骤的实现检查清单                                       │
│ • 项目语言的最佳实践指导                                     │
│ • 常见陷阱和错误避免建议                                     │
│ • 清晰的验收标准定义                                         │
│                                                              │
│ → LLM 用这个增强的提示词生成更高质量的代码建议             │
└─────────────────────────────────────────────────────────────┘
```

---

## 阶段详解

### Phase 1: 智能文件发现 (Smart File Discovery)

**目标**: 从模糊的用户指令自动找到代码库中最相关的源文件

**核心组件**:
- **KeywordExtractor**: 从指令中提取关键词
  - 中文多字词识别（"用户认证" → ['用户', '认证']）
  - 英文分词（"add authentication" → ['add', 'authentication']）
  - 编程词优先级排序
  - 停用词去除

- **FileMatcher**: 在代码库中查找相关文件
  - 精确文件名匹配（关键词 → 文件名）
  - 模糊路径匹配（auth → auth.py, authentication.js）
  - 语义相关性映射（user → user.py, models.py）
  - 按相关性评分并排序

**工作流**:
```python
from file_discoverer import FileDiscoverer

discoverer = FileDiscoverer('/path/to/project')

# 输入用户指令
task = "添加用户认证功能"

# 发现相关文件
files = discoverer.discover(task, max_results=10)

# 输出: [
#   FoundFile(path='src/auth.py', relevance_score=0.95, ...),
#   FoundFile(path='src/user.py', relevance_score=0.88, ...),
#   FoundFile(path='src/models.py', relevance_score=0.72, ...),
#   ...
# ]
```

**验收标准** (✅ 全部达成):
- 关键词提取准确率 >80% (实际: 100%)
- 文件发现速度 <2 秒 (实际: 0.47 秒)
- 18/18 测试通过 ✅

---

### Phase 2: 符号索引 (Symbol Indexing)

**目标**: 从发现的文件中提取函数/类签名，减少 token 浪费并加速处理

**核心组件**:
- **PythonSymbolExtractor**: Python 代码符号提取
  - 使用 AST 解析，100% 准确
  - 提取函数、类、方法、装饰器
  - 保留完整的类型注解和 docstring

- **JavaScriptSymbolExtractor**: JavaScript 代码符号提取
  - 使用正则表达式（快速但精确度依赖于模式）
  - 支持函数声明、箭头函数、ES6 类

- **SymbolCache**: 智能缓存系统
  - **内存缓存**: 加快重复访问（0.0067ms）
  - **磁盘缓存**: 跨会话持久化（`.cache/symbols/` 目录）
  - **失效检测**: 通过文件哈希自动检测更新
  - **缓存命中率**: >95%

**工作流**:
```python
from symbol_indexer import SymbolIndexer

indexer = SymbolIndexer()

# 索引 Phase 1 发现的文件
files = ['src/auth.py', 'src/user.py', 'src/models.py']
symbols = indexer.batch_index(files)

# 输出示例 (src/auth.py):
# [
#   ExtractedSymbol(
#     name='authenticate',
#     symbol_type='function',
#     signature='def authenticate(username: str, password: str) -> bool:',
#     line_number=42,
#     decorators=['@staticmethod']
#   ),
#   ExtractedSymbol(
#     name='verify_token',
#     symbol_type='async_function',
#     signature='async def verify_token(token: str) -> Optional[User]:',
#     line_number=85,
#     docstring='验证访问令牌并返回关联的用户对象'
#   ),
#   ...
# ]

# 缓存效果
# 首次访问: 156.20ms (全量加载)
# 缓存命中: 0.0067ms (速度提升 23,313x)
```

**优势**:
- 减少 token 使用 50%+（完整代码 → 仅签名）
- 缓存命中率 >95%，提升响应速度
- 保留关键信息，去除噪音

**验收标准** (✅ 全部达成):
- 提取准确率 100% (所有函数/类完整提取)
- 缓存命中率 >95% ✅
- 34/34 测试通过 ✅

---

### Phase 3: 编码模板系统 (Coding Template System)

**目标**: 根据任务类型（实现/修复/重构/测试/审查），提供结构化的检查清单和最佳实践指导

**核心组件**:
- **5 个 YAML 模板**:
  - `implement.yaml` - 新功能实现
  - `fix.yaml` - 缺陷修复
  - `refactor.yaml` - 代码重构
  - `test.yaml` - 测试编写
  - `review.yaml` - 代码审查

- **TemplateTrigger**: 任务类型识别
  - 双语触发词匹配（中文 + 英文）
  - 置信度评分机制（0.0-1.0）
  - 智能选择最合适的模板

- **CodingTemplateManager**: 模板管理和优化
  - **懒加载架构**: 初始化仅扫描文件（0.17ms）
  - **按需加载**: 访问时加载单个模板（33.6ms）
  - **格式化缓存**: 重复调用时利用缓存（0.01ms）
  - 语言检测（自动识别项目主语言）

**工作流**:
```python
from coding_templates import CodingTemplateManager

# 初始化（非常快，仅扫描文件）
manager = CodingTemplateManager()  # 0.17ms

# 匹配用户指令中的任务类型
trigger = TemplateTrigger()
user_input = "添加用户认证功能"
match = trigger.match(user_input, manager.list_templates())

# 获取模板
template = manager.get_template(match.template.task_type)  # 33.6ms

# 格式化模板（支持语言过滤）
language = 'python'  # 从 Phase 2 检测
formatted = manager.format_template(template, language)

# 输出包含:
# ✓ 实现检查清单 (理解需求, 设计接口, ...)
# ✓ Python 最佳实践 (类型注解, docstring, ...)
# ✓ 常见陷阱 (没有考虑边界情况, ...)
# ✓ 验收标准 (所有测试通过, ...)
```

**每个模板的内容**:
1. **检查清单** (8-10 项)
   - 分步骤的任务清单
   - 可视化进度跟踪

2. **最佳实践** (语言特定)
   - Python: 类型注解、docstring、异常处理
   - JavaScript: TypeScript、async/await、null 检查
   - Java: 接口设计、equals/hashCode、异常安全
   - Go: error 返回、defer、context 使用

3. **常见陷阱**
   - 易犯的错误
   - 如何避免
   - 测试覆盖提醒

4. **验收标准**
   - 功能完成标准
   - 代码质量标准
   - 测试覆盖标准

**性能优化** (全部达成):

| 操作 | 目标 | 实际 | 状态 | 优化类型 |
|------|------|------|------|----------|
| 初始化 | <5ms | 0.17ms | ✅ | 懒加载 |
| 单模板加载 | <50ms | 33.6ms | ✅ | 按需加载 |
| 全量加载 | <150ms | 84.77ms | ✅ | 批量加载 |
| 格式化（首次） | <5ms | 0.13ms | ✅ | 高效实现 |
| 格式化（缓存） | <1ms | 0.01ms | ✅ | 缓存机制 |
| 重复访问 | <1ms | 0.0067ms | ✅ | 内存缓存 |

**验收标准** (✅ 全部达成):
- 5 个完整模板 ✅
- 双语触发词 ✅
- 语言特定最佳实践 ✅
- 性能目标全部达成 ✅
- 38/38 测试通过 ✅

---

## 完整工作示例

### 场景: "为用户模块添加身份验证"

#### 步骤 1: Phase 1 文件发现

```
用户输入: "为用户模块添加身份验证"

KeywordExtractor:
  - 提取关键词: ['用户', 'user', '身份验证', 'authentication', '模块']
  - 优先级排序: ['authentication', 'user'] (编程词优先)

FileMatcher:
  - 精确匹配: user.py ✓
  - 模糊匹配: auth.py, login.py, password.py
  - 语义映射: models.py (包含 User 类)

结果:
  auth.py (relevance: 0.95)
  user.py (relevance: 0.92)
  models.py (relevance: 0.85)
  password_utils.py (relevance: 0.72)
  ...
```

#### 步骤 2: Phase 2 符号提取

```
输入文件: auth.py

PythonSymbolExtractor (AST):
  ✓ def hash_password(password: str) -> str:
  ✓ def verify_password(plain: str, hashed: str) -> bool:
  ✓ async def authenticate(username: str, password: str) -> User:
  ✓ class AuthenticationError(Exception):

SymbolCache:
  - 第一次: 加载 + 缓存 (156ms)
  - 后续访问: 从缓存读取 (0.0067ms)
  - 文件变更时自动失效

输入文件: user.py

PythonSymbolExtractor (AST):
  ✓ class User(BaseModel):
      __init__(self, username: str, email: str)
  ✓ def create_user(username: str, email: str, password: str) -> User:
  ✓ def get_user_by_username(username: str) -> Optional[User]:
  ...
```

#### 步骤 3: Phase 3 模板应用

```
用户指令: "为用户模块添加身份验证"

TemplateTrigger:
  - 识别触发词: "添加" → implement task
  - 置信度: 100%

CodingTemplateManager:
  - 加载: implement.yaml
  - 检测语言: Python (从代码库)
  - 格式化输出

增强的提示词包含:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 为用户模块添加身份验证

**相关文件**:
- src/auth.py - 认证模块 (relevance: 0.95)
- src/user.py - 用户模块 (relevance: 0.92)
- src/models.py - 数据模型 (relevance: 0.85)

**现有代码结构**:
```python
# auth.py 中的现有函数
async def authenticate(username: str, password: str) -> User:
class AuthenticationError(Exception):

# user.py 中的现有类
class User(BaseModel):
  username: str
  email: str
```

**📋 实现检查清单**:
- [ ] 理解需求: 身份验证机制、安全要求
- [ ] 设计接口: 定义 API 端点和数据结构
- [ ] 考虑边界情况: 无效用户、密码错误、超时
- [ ] 实现核心逻辑: 验证函数、令牌生成
- [ ] 添加输入验证: 参数检查、SQL 注入防护
- [ ] 编写单元测试: 正常路径、错误情况
- [ ] 更新文档: API 文档、使用示例
- [ ] 考虑性能: 缓存策略、数据库查询优化

**✨ Python 最佳实践**:
- 使用类型注解: `def authenticate(username: str, ...) -> bool:`
- 编写 docstring: Google 格式的完整文档
- 异常处理: 自定义异常 (AuthenticationError)
- 使用 logging: 记录认证事件
- 避免可变默认参数: `def func(x, lst=None):`
- 使用上下文管理器: with 语句处理资源

**⚠️ 常见陷阱**:
- ❌ 硬编码密钥或密码
- ❌ 缺少速率限制（防止暴力破解）
- ❌ 直接存储明文密码
- ❌ 缺少输入验证
- ❌ 不记录认证失败

**✅ 验收标准**:
- 所有认证测试通过
- 代码覆盖率 ≥ 80%
- 通过安全审查
- 文档完整

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### 结果

→ LLM 收到这个增强的提示词，能够：
- ✅ 准确理解项目结构和现有代码
- ✅ 遵循项目语言的最佳实践
- ✅ 提供符合验收标准的实现建议
- ✅ 避免常见陷阱和错误

---

## 性能对比

### 场景: 提供用户认证的增强建议

#### 不使用 Phase 1-3 (传统方式)

```
用户给 LLM 的提示词: "为用户模块添加身份验证"

↓ (LLM 缺少上下文)

LLM 的回应:
- 🤔 不确定项目使用的框架
- 🤔 不知道现有的代码结构
- 🤔 给出通用建议而非项目特定建议
- ⚠️ 可能建议重复实现现有功能
- ⚠️ 可能不遵循项目的编码规范

结果: 🔴 需要多轮对话澄清和修改
```

#### 使用 Phase 1-3 (增强方式)

```
Phase 1: 发现相关文件 → auth.py, user.py, models.py
Phase 2: 提取现有符号 → authenticate(), User class, ...
Phase 3: 应用任务模板 → implement.yaml + Python 最佳实践

↓ (LLM 获得完整上下文)

LLM 的回应:
- ✅ 准确理解项目结构
- ✅ 知道现有的函数和类
- ✅ 给出项目特定的建议
- ✅ 遵循项目的编码规范
- ✅ 避免重复实现

结果: 🟢 一次生成高质量建议，通常无需修改
```

---

## 集成点和扩展

### 与 Phase 4-5 的关系

**Phase 4** (AGENTS.md 生成):
- 输入: Phase 1-3 的发现结果
- 处理: 生成项目边界约束文档
- 输出: AGENTS.md 文件

**Phase 5** (性能优化):
- 优化: Phase 1-3 的性能
- 目标: 冷启动 <15s，缓存命中 <5s

### 与 v1.1.0 (生产版本) 的区别

| 维度 | v1.1.0 | v1.2.1 (Phase 1-3) |
|------|--------|-------------------|
| **范围** | 通用提示增强 | 代码项目专用 |
| **文件发现** | 手动指定 | 自动发现 ✨ |
| **符号索引** | 不支持 | 自动提取 ✨ |
| **模板系统** | 5 个通用模板 | 5 个任务模板 ✨ |
| **测试数** | 874 个 | 90 个 (Phase 1-3) |
| **状态** | ✅ 生产就绪 | ✅ 生产就绪 (Phase 1-3) |

---

## 最佳实践

### 使用 Phase 1-3 的建议

1. **针对代码项目使用**
   - ✅ 代码项目增强
   - ✅ 功能实现指导
   - ❌ 不适合非代码内容

2. **启用缓存以提升性能**
   ```python
   # 自动启用磁盘缓存
   manager = CodingTemplateManager()
   # 性能显著提升 (缓存命中 >95%)
   ```

3. **正确配置项目路径**
   ```python
   discoverer = FileDiscoverer('/absolute/path/to/project')
   # 使用绝对路径确保准确发现
   ```

4. **监听文件变更**
   - Phase 2 SymbolCache 自动检测文件哈希变更
   - 缓存在需要时自动失效

---

## 故障排除

### Phase 1: 文件发现不完整

**问题**: 找不到相关文件
- **原因**: 关键词提取不准确
- **解决**: 检查关键词是否在文件名或路径中出现

**问题**: 文件相关性排序不正确
- **原因**: 文件名与关键词匹配度低
- **解决**: 考虑项目的命名约定

### Phase 2: 符号提取失败

**问题**: Python 文件提取错误
- **原因**: 可能是 AST 解析异常（语法错误）
- **解决**: 确保文件有效的 Python 语法

**问题**: 缓存没有更新
- **原因**: 文件修改后缓存仍然使用旧数据
- **解决**: SymbolCache 通过文件哈希自动检测，应自动更新

### Phase 3: 模板匹配不准确

**问题**: 识别错误的任务类型
- **原因**: 触发词不在用户输入中
- **解决**: 添加更多相关的触发词

**问题**: 语言特定建议不适用
- **原因**: 项目语言检测不正确
- **解决**: 手动指定语言参数

---

## 性能监控

### 基准测试结果

执行命令:
```bash
python -m pytest tests/test_coding_templates.py::TestPerformance -v
```

预期结果:
```
test_manager_initialization_time   PASSED [0.17ms < 5ms] ✅
test_single_template_load_time     PASSED [33.6ms < 50ms] ✅
test_full_template_load_time       PASSED [84.77ms < 150ms] ✅
test_template_formatting_performance PASSED [0.01ms cached] ✅
test_trigger_matching_performance  PASSED [<50ms] ✅
test_repeated_access_performance   PASSED [0.0067ms avg] ✅
test_stress_multiple_managers      PASSED [<100ms] ✅
```

---

## 总结

**Phase 1-3 的协同工作** 构成了完整的代码增强流程：

1. **Phase 1** 快速定位相关文件（0.47s）
2. **Phase 2** 提取关键符号，减少 token（>95% 缓存命中）
3. **Phase 3** 应用任务模板和最佳实践（0.17ms 初始化）

**最终效果**:
- 为 LLM 提供完整的项目上下文
- 生成更高质量、更项目特定的代码建议
- 显著减少回合制对话和修改次数

**生产就绪**: ✅ 90/90 测试通过，零回归，性能优异

---

**相关文档**:
- Phase 1-3 综合审查报告: `docs/PHASE_1_2_3_REVIEW_REPORT.md`
- Phase 3 完成总结: `docs/PHASE3_COMPLETION_SUMMARY.txt`
- 架构决策: `docs/ARCHITECTURE.md`
