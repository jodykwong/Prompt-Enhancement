# 🏗️ 系统架构设计

**版本**: P0.6 | **最后更新**: 2025-12-10

本文档详细说明 Prompt Enhancement 系统的整体架构、设计原则和模块间的关系。

---

## 📚 目录

1. [系统概览](#系统概览)
2. [架构设计](#架构设计)
3. [模块设计](#模块设计)
4. [数据流](#数据流)
5. [依赖关系](#依赖关系)
6. [扩展性设计](#扩展性设计)

---

## 系统概览

### 核心任务

Prompt Enhancement 系统旨在通过自动收集项目上下文，智能增强用户提示词，提升 AI 模型的响应质量。

### 系统目标

✅ **自动上下文收集** - 无需用户手动输入，自动识别项目的技术栈、结构和历史
✅ **智能提示词增强** - 基于项目上下文，将模糊的提示转化为清晰、具体的指令
✅ **高性能异步处理** - 支持并发处理，不阻塞主线程
✅ **完整的缓存机制** - 避免重复分析，提升响应速度
✅ **灵活的集成接口** - 易于集成到 Claude Code 等工具中

---

## 架构设计

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    用户输入 (提示词)                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │  enhanced_prompt_generator.py    │  (P0.5) 增强器集成
        │  (统一接口)                       │
        └──────────────┬───────────────────┘
                       │
        ┌──────────────┴──────────────────┐
        │                                  │
        ▼                                  ▼
┌──────────────────┐            ┌──────────────────────┐
│ 上下文收集       │            │ 异步增强              │
│ (可选)          │            │ (必须)               │
└──────┬───────────┘            └──────┬───────────────┘
       │                               │
       │ 如果提供 project_path        │
       │                               │
       ▼                               ▼
┌─────────────────────────────┐ ┌──────────────────────┐
│  context_collector.py (P0.4)│ │async_prompt_enhancer │
│  (统一上下文收集器)          │ │  .py (P0.5)          │
└──────┬──────────────────────┘ └──────┬───────────────┘
       │                               │
   ┌───┴─────┬──────────┬──────────┐   │
   ▼         ▼          ▼          ▼   │
 P0.1      P0.2       P0.3    缓存机制  │ DeepSeek
 技术栈    项目结构   Git历史    (内存)   │ API
 检测      分析       分析      │       │
   │         │          │        │       │
   └─────────┴──────────┴────────┘       │
                 │                       │
                 │ 合并上下文             │
                 │                       │
                 └───────────┬───────────┘
                             │
                    ┌────────▼──────────┐
                    │  增强的上下文      │
                    │ + 原始提示词       │
                    └────────┬──────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │  增强后的提示词         │
                │  + 推理过程             │
                │  + 统计信息             │
                └────────────────────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │   返回给用户        │
                    └────────────────────┘
```

### 分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                        应用层 (CLI/API)                      │
│                  enhanced_prompt_generator                  │
├─────────────────────────────────────────────────────────────┤
│                        服务层 (业务逻辑)                      │
│  ┌──────────────────┐         ┌─────────────────────────┐  │
│  │ context_collector│         │async_prompt_enhancer    │  │
│  │   (P0.4)         │         │  (P0.5)                 │  │
│  └──────────────────┘         └─────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                        模块层 (基础分析)                      │
│  ┌──────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │ tech_stack   │  │ project_struct│  │ git_history   │  │
│  │ detector     │  │ analyzer      │  │ analyzer      │  │
│  │  (P0.1)      │  │  (P0.2)       │  │  (P0.3)       │  │
│  └──────────────┘  └───────────────┘  └───────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                        工具层 (外部服务)                      │
│  ┌──────────┐  ┌──────────────┐  ┌──────┐  ┌────────────┐ │
│  │ AST分析  │  │  文件系统    │  │ Git  │  │DeepSeek API│ │
│  └──────────┘  └──────────────┘  └──────┘  └────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                        支撑层 (缓存和配置)                     │
│  ┌────────────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ 内存缓存机制    │  │ 环境配置 │  │ 日志和监控       │   │
│  └────────────────┘  └──────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 模块设计

### P0.1: 技术栈检测器 (TechStackDetector)

**职责**: 自动检测项目使用的编程语言、框架和工具

**输入**: 项目路径
**输出**: 技术栈列表和详细信息

**关键方法**:
- `detect()` - 检测项目技术栈
- `get_details()` - 获取详细信息

**示例输出**:
```python
{
    "languages": ["Python", "JavaScript"],
    "frameworks": ["Django", "React"],
    "databases": ["PostgreSQL"],
    "tools": ["Docker", "Webpack"],
    "confidence": 0.95
}
```

---

### P0.2: 项目结构分析器 (ProjectStructureAnalyzer)

**职责**: 分析项目的目录结构和关键文件

**输入**: 项目路径
**输出**: 项目结构信息

**关键方法**:
- `analyze()` - 分析项目结构
- `get_key_files()` - 获取关键文件

**设计特点**:
- 递归遍历目录树
- 识别关键配置文件 (package.json, requirements.txt 等)
- 统计文件类型分布
- 忽略通常的输出目录 (node_modules, venv, .git 等)

---

### P0.3: Git 历史分析器 (GitHistoryAnalyzer)

**职责**: 提取和分析项目的 Git 仓库信息

**输入**: 项目路径
**输出**: Git 历史和提交信息

**关键方法**:
- `analyze()` - 分析 Git 信息
- `get_recent_commits()` - 获取最近提交

**收集的信息**:
- 当前分支和暂存区状态
- 提交总数和提交历史
- 贡献者列表
- 最后修改日期

---

### P0.4: 上下文收集器 (ContextCollector)

**职责**: 统一整合 P0.1-P0.3 的结果，生成项目完整上下文

**输入**: 项目路径
**输出**: 完整项目上下文

**关键功能**:
- 调用所有基础分析模块
- 合并各模块的输出
- 生成易于理解的上下文摘要
- 生成格式化的上下文字符串

**输出格式**:
```python
{
    "summary": "Python/Django Web 应用，使用 PostgreSQL 和 React 前端",
    "tech_stack": ["Python", "Django", "React", "PostgreSQL"],
    "project_structure": {...},  # 详细的结构信息
    "git_history": {...},        # Git 信息
    "context_string": "# 项目上下文\n..."  # 格式化字符串
}
```

---

### P0.5: 异步提示词增强器 (AsyncPromptEnhancer)

**职责**: 通过 API 调用异步增强用户提示词

**输入**: 提示词、超时时间、回调函数、取消令牌
**输出**: 增强后的提示词和处理统计

**关键特性**:
- 异步 API 调用 (基于 asyncio)
- 进度回调支持
- 取消机制
- 超时控制
- 错误恢复

**设计模式**:
```python
async def enhance(
    prompt: str,
    timeout: int = 60,
    progress_callback: Optional[Callable] = None,
    cancel_token: Optional[asyncio.Event] = None
) -> Dict:
    # 1. 调用进度回调 (0%)
    # 2. 发起 API 请求
    # 3. 监听取消令牌
    # 4. 处理超时异常
    # 5. 调用进度回调 (100%)
    # 6. 返回增强结果
```

---

### P0.6: 增强器集成 (EnhancedPromptGenerator)

**职责**: 提供高层接口，集成上下文收集和异步增强

**设计特点**:
- **上下文注入**: 自动将项目上下文注入到提示词中
- **缓存机制**: 避免重复收集同一项目的上下文
- **便捷函数**: 提供一行代码的快速接口

**调用流程**:
```
用户输入 (prompt, project_path)
     │
     ▼
检查缓存中是否有该项目的上下文
     │
     ├─ 缓存命中 → 使用缓存的上下文
     │
     └─ 缓存未命中 → 收集项目上下文 → 缓存
              │
              ▼
        将上下文注入到提示词
              │
              ▼
        调用异步增强器增强提示词
              │
              ▼
        返回增强结果 (包含上下文标志)
```

---

## 数据流

### 完整请求流程

```
用户调用: await enhance_prompt_with_context("修复 bug", project_path="/path")
│
├─ 1. 初始化生成器
│    └─ 创建 EnhancedPromptGenerator 实例
│
├─ 2. 收集项目上下文 (如果提供了 project_path)
│    ├─ 检查缓存
│    ├─ 如果缓存未命中:
│    │  ├─ 检测技术栈 (P0.1)
│    │  ├─ 分析项目结构 (P0.2)
│    │  ├─ 分析 Git 历史 (P0.3)
│    │  └─ 合并结果 (P0.4)
│    └─ 缓存结果
│
├─ 3. 注入上下文到提示词
│    └─ 如果有上下文: 将其添加到提示词前面
│
├─ 4. 调用异步增强器
│    ├─ 发起 DeepSeek API 调用
│    ├─ 监听进度和取消
│    ├─ 处理超时和错误
│    └─ 获取增强结果
│
└─ 5. 返回最终结果
   ├─ 原始提示词
   ├─ 增强后的提示词
   ├─ 推理过程
   ├─ 处理时间
   ├─ 上下文注入标志
   └─ 上下文摘要
```

### 缓存数据流

```
第一次请求: /path/to/project
     │
     ▼
缓存不存在 → 收集上下文 (800ms) → 存储到缓存
                                    │
                                    ▼
                            _context_cache[path] = context

第二次请求: /path/to/project
     │
     ▼
缓存存在 → 直接返回 (< 2ms)
```

---

## 依赖关系

### 模块依赖图

```
enhanced_prompt_generator.py (P0.6)
    ├─ context_collector.py (P0.4)
    │   ├─ tech_stack_detector.py (P0.1)
    │   ├─ project_structure_analyzer.py (P0.2)
    │   └─ git_history_analyzer.py (P0.3)
    └─ async_prompt_enhancer.py (P0.5)
        └─ OpenAI AsyncClient
            └─ DEEPSEEK_API
```

### 外部依赖

| 依赖 | 用途 | 版本 |
|-----|------|------|
| openai | 异步 API 调用 | >= 1.3.0 |
| python-dotenv | 环境变量管理 | >= 0.19.0 |
| git | Git 仓库分析 | 系统自带 |

### 可选依赖

| 依赖 | 用途 | 场景 |
|-----|------|------|
| pytest | 单元测试 | 开发环境 |
| pytest-asyncio | 异步测试 | 开发环境 |
| coverage | 覆盖率分析 | 开发环境 |

---

## 扩展性设计

### 插件式架构

系统采用分层设计，便于添加新的分析模块：

```python
# 添加新的分析模块示例
class DatabaseAnalyzer:
    """数据库分析器"""

    def __init__(self, project_path: str):
        self.project_path = project_path

    def analyze(self) -> Dict[str, Any]:
        # 实现数据库分析逻辑
        return {
            "databases": ["PostgreSQL", "Redis"],
            "migrations": 42,
            "schema_version": "1.2.3"
        }

# 在 context_collector.py 中集成
class ContextCollector:
    def collect(self, project_path: str) -> Dict:
        # ...
        db_analyzer = DatabaseAnalyzer(project_path)
        context["database"] = db_analyzer.analyze()
        # ...
```

### 模型扩展性

当前支持 DeepSeek，可扩展支持其他模型：

```python
class AsyncPromptEnhancer:
    def __init__(self, model: str = "deepseek-reasoner"):
        if model.startswith("deepseek"):
            self.client = AsyncOpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"))
        elif model.startswith("openai"):
            self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # ...
```

### 缓存策略扩展

当前使用内存缓存，可扩展支持持久化缓存：

```python
# 未来实现: 持久化缓存
class PersistentCacheEnhancer(EnhancedPromptGenerator):
    def __init__(self, cache_dir: str = ".cache"):
        super().__init__()
        self.cache_dir = cache_dir

    def _save_cache(self, path: str, context: Dict):
        # 保存到磁盘
        cache_file = f"{self.cache_dir}/{hash(path)}.json"
        with open(cache_file, 'w') as f:
            json.dump(context, f)

    def _load_cache(self, path: str) -> Dict:
        # 从磁盘加载
        cache_file = f"{self.cache_dir}/{hash(path)}.json"
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        return None
```

---

## 性能考虑

### 优化策略

1. **缓存机制**
   - 内存缓存避免重复分析
   - 缓存命中率 > 99%
   - 平均响应时间从 800ms 降至 < 2ms

2. **异步处理**
   - 使用 asyncio 避免阻塞
   - 支持并发处理多个请求
   - 进度回调实时反馈

3. **智能分析**
   - 忽略不相关的目录 (node_modules, .git 等)
   - 限制 Git 历史行数
   - 只分析关键配置文件

### 扩展性指标

| 场景 | 性能 | 瓶颈 |
|-----|-----|------|
| 小型项目 (< 100 文件) | 585ms | Git 分析 |
| 中型项目 (100-1000) | 700ms | 结构分析 |
| 大型项目 (> 1000) | 850ms | 整体 I/O |
| 缓存命中 | < 2ms | 网络延迟 |

---

## 安全性设计

### API 密钥管理

- ✅ 使用环境变量存储 API 密钥
- ✅ 从不硬编码密钥
- ✅ 支持 .env 文件配置
- ✅ 在错误消息中不暴露密钥

### 输入验证

- ✅ 检查项目路径有效性
- ✅ 处理空或 None 输入
- ✅ 验证提示词长度
- ✅ 清理日志中的敏感信息

---

## 相关文档

- [API_REFERENCE.md](API_REFERENCE.md) - API 完整参考
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - 测试指南
- [QUICK_REFERENCE_INIT.md](QUICK_REFERENCE_INIT.md) - 快速参考

---

**架构设计者**: Jodykwong
**最后更新**: 2025-12-10
**版本**: P0.6
