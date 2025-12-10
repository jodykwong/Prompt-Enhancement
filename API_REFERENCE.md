# 📖 API 参考文档

**版本**: P0.6 | **最后更新**: 2025-12-10

本文档提供了 Prompt Enhancement 系统的完整 API 参考，包括所有公共接口、参数说明和使用示例。

---

## 📚 目录

1. [context_collector 模块](#context_collector-模块)
2. [tech_stack_detector 模块](#tech_stack_detector-模块)
3. [project_structure_analyzer 模块](#project_structure_analyzer-模块)
4. [git_history_analyzer 模块](#git_history_analyzer-模块)
5. [async_prompt_enhancer 模块](#async_prompt_enhancer-模块)
6. [enhanced_prompt_generator 模块](#enhanced_prompt_generator-模块)

---

## context_collector 模块

### 概述

`context_collector` 是 P0.4 的核心模块，负责统一收集项目的完整上下文信息，包括技术栈、项目结构和 Git 历史。

### 导入

```python
from context_collector import collect_project_context, ContextCollector
```

### `collect_project_context(project_path: str) -> Dict[str, Any]`

**功能**: 收集完整的项目上下文

**参数**:
- `project_path` (str): 项目根目录的绝对路径

**返回值** (Dict):
```python
{
    "summary": str,              # 项目摘要信息
    "tech_stack": List[str],     # 检测到的技术栈
    "project_structure": Dict,   # 项目结构信息
    "git_history": Dict,         # Git 仓库信息
    "context_string": str        # 格式化的上下文字符串
}
```

**异常**:
- `ValueError`: 如果 `project_path` 不存在

**示例**:
```python
context = collect_project_context("/path/to/my/project")
print(f"技术栈: {context['tech_stack']}")
print(f"项目摘要: {context['summary']}")
```

---

## tech_stack_detector 模块

### 概述

`tech_stack_detector` (P0.1) 自动检测项目使用的技术框架和编程语言。

### 导入

```python
from tech_stack_detector import TechStackDetector
```

### `TechStackDetector` 类

#### 初始化

```python
detector = TechStackDetector(project_path: str)
```

**参数**:
- `project_path` (str): 项目根目录路径

#### 方法

##### `detect() -> List[str]`

**功能**: 检测项目的技术栈

**返回值**: 检测到的技术框架列表

**示例**:
```python
detector = TechStackDetector("/path/to/project")
tech_stack = detector.detect()
# 可能返回: ["Python", "Django", "PostgreSQL"]
```

##### `get_details() -> Dict[str, Any]`

**功能**: 获取技术栈检测的详细信息

**返回值** (Dict):
```python
{
    "languages": List[str],        # 编程语言
    "frameworks": List[str],       # 框架
    "databases": List[str],        # 数据库
    "tools": List[str],            # 工具
    "confidence": float            # 检测置信度 (0-1)
}
```

**示例**:
```python
details = detector.get_details()
print(f"编程语言: {details['languages']}")
print(f"框架: {details['frameworks']}")
```

---

## project_structure_analyzer 模块

### 概述

`project_structure_analyzer` (P0.2) 分析项目的目录结构和关键文件。

### 导入

```python
from project_structure_analyzer import ProjectStructureAnalyzer
```

### `ProjectStructureAnalyzer` 类

#### 初始化

```python
analyzer = ProjectStructureAnalyzer(project_path: str)
```

#### 方法

##### `analyze() -> Dict[str, Any]`

**功能**: 分析项目结构

**返回值** (Dict):
```python
{
    "total_files": int,                  # 文件总数
    "directories": int,                  # 目录总数
    "file_distribution": Dict[str, int], # 文件类型分布
    "structure": Dict,                   # 目录树结构
    "key_files": List[str]               # 关键文件列表
}
```

**示例**:
```python
analyzer = ProjectStructureAnalyzer("/path/to/project")
structure = analyzer.analyze()
print(f"总文件数: {structure['total_files']}")
print(f"文件分布: {structure['file_distribution']}")
```

##### `get_key_files(limit: int = 10) -> List[str]`

**功能**: 获取项目的关键文件

**参数**:
- `limit` (int): 返回的关键文件数量上限，默认为 10

**返回值**: 关键文件路径列表

**示例**:
```python
key_files = analyzer.get_key_files(limit=15)
for file in key_files:
    print(f"  - {file}")
```

---

## git_history_analyzer 模块

### 概述

`git_history_analyzer` (P0.3) 提取和分析 Git 仓库的历史信息。

### 导入

```python
from git_history_analyzer import GitHistoryAnalyzer
```

### `GitHistoryAnalyzer` 类

#### 初始化

```python
analyzer = GitHistoryAnalyzer(project_path: str)
```

#### 方法

##### `analyze() -> Dict[str, Any]`

**功能**: 分析 Git 历史

**返回值** (Dict):
```python
{
    "is_git_repo": bool,           # 是否为 Git 仓库
    "current_branch": str,         # 当前分支名
    "total_commits": int,          # 总提交数
    "recent_commits": List[Dict],  # 最近提交记录
    "contributors": List[str],     # 贡献者列表
    "last_commit_date": str        # 最后提交日期
}
```

**示例**:
```python
analyzer = GitHistoryAnalyzer("/path/to/project")
git_info = analyzer.analyze()
if git_info["is_git_repo"]:
    print(f"当前分支: {git_info['current_branch']}")
    print(f"提交总数: {git_info['total_commits']}")
```

##### `get_recent_commits(limit: int = 5) -> List[Dict]`

**功能**: 获取最近的提交记录

**参数**:
- `limit` (int): 返回的提交数量，默认为 5

**返回值**: 提交信息列表，每个提交包含：
```python
{
    "hash": str,        # 提交哈希
    "author": str,      # 作者
    "message": str,     # 提交信息
    "date": str         # 提交日期
}
```

**示例**:
```python
commits = analyzer.get_recent_commits(limit=10)
for commit in commits:
    print(f"{commit['date']}: {commit['author']} - {commit['message']}")
```

---

## async_prompt_enhancer 模块

### 概述

`async_prompt_enhancer` (P0.5) 提供异步版本的提示词增强功能，支持进度回调和取消机制。

### 导入

```python
from async_prompt_enhancer import AsyncPromptEnhancer
```

### `AsyncPromptEnhancer` 类

#### 初始化

```python
enhancer = AsyncPromptEnhancer(model: str = "deepseek-reasoner")
```

**参数**:
- `model` (str): 使用的模型名称，默认为 "deepseek-reasoner"

**异常**:
- `ValueError`: 如果 DEEPSEEK_API_KEY 环境变量未设置

#### 方法

##### `async enhance(original_prompt: str, timeout: int = 60, progress_callback: Optional[Callable] = None, cancel_token: Optional[asyncio.Event] = None) -> Dict[str, Any]`

**功能**: 异步增强提示词

**参数**:
- `original_prompt` (str): 原始提示词
- `timeout` (int): API 调用超时时间（秒），默认为 60
- `progress_callback` (Optional[Callable]): 进度回调函数，签名为 `async def callback(message: str, progress: float)`
- `cancel_token` (Optional[asyncio.Event]): 取消令牌，用于中断操作

**返回值** (Dict):
```python
{
    "original": str,           # 原始提示词
    "enhanced": str,           # 增强后的提示词
    "reasoning": str,          # 模型的思考过程
    "processing_time": float,  # 处理时间（秒）
    "success": bool,           # 是否成功
    "error": str,              # 错误信息（如果失败）
    "stats": dict,             # 统计信息
    "cancelled": bool          # 是否被取消
}
```

**示例**:

**基础使用**:
```python
import asyncio
from async_prompt_enhancer import AsyncPromptEnhancer

async def main():
    enhancer = AsyncPromptEnhancer()
    result = await enhancer.enhance("修复 bug")
    print(result["enhanced"])

asyncio.run(main())
```

**带进度回调**:
```python
async def progress_handler(message: str, progress: float):
    print(f"{message}: {progress*100:.0f}%")

async def main():
    enhancer = AsyncPromptEnhancer()
    result = await enhancer.enhance(
        "修复 bug",
        progress_callback=progress_handler
    )
    print(result["enhanced"])

asyncio.run(main())
```

**带取消机制**:
```python
async def main():
    enhancer = AsyncPromptEnhancer()
    cancel_token = asyncio.Event()

    # 在另一个任务中取消（5 秒后）
    async def cancel_after_5s():
        await asyncio.sleep(5)
        cancel_token.set()

    asyncio.create_task(cancel_after_5s())

    result = await enhancer.enhance(
        "修复 bug",
        cancel_token=cancel_token
    )
    if result["cancelled"]:
        print("操作已取消")

asyncio.run(main())
```

**自定义超时**:
```python
result = await enhancer.enhance(
    "修复 bug",
    timeout=120  # 120 秒超时
)
```

---

## enhanced_prompt_generator 模块

### 概述

`enhanced_prompt_generator` (P0.5) 整合了上下文收集和异步增强功能，提供高级接口用于基于项目上下文的提示词增强。

### 导入

```python
from enhanced_prompt_generator import EnhancedPromptGenerator, enhance_prompt_with_context
```

### `EnhancedPromptGenerator` 类

#### 初始化

```python
generator = EnhancedPromptGenerator(model: str = "deepseek-reasoner")
```

#### 方法

##### `async enhance(original_prompt: str, project_path: Optional[str] = None, timeout: int = 60, progress_callback: Optional[Callable] = None, cancel_token: Optional[asyncio.Event] = None) -> Dict[str, Any]`

**功能**: 增强提示词，可选地注入项目上下文

**参数**:
- `original_prompt` (str): 原始提示词
- `project_path` (Optional[str]): 项目路径（可选）
- `timeout` (int): API 调用超时时间（秒）
- `progress_callback` (Optional[Callable]): 进度回调函数
- `cancel_token` (Optional[asyncio.Event]): 取消令牌

**返回值** (Dict):
```python
{
    "original": str,           # 原始提示词
    "enhanced": str,           # 增强后的提示词
    "reasoning": str,          # 模型的思考过程
    "processing_time": float,  # 处理时间（秒）
    "success": bool,           # 是否成功
    "error": str,              # 错误信息（如果失败）
    "stats": dict,             # 统计信息
    "context_injected": bool,  # 是否注入了上下文
    "context_summary": str     # 上下文摘要
}
```

**示例**:
```python
import asyncio
from enhanced_prompt_generator import EnhancedPromptGenerator

async def main():
    generator = EnhancedPromptGenerator()
    result = await generator.enhance(
        "修复登录模块的 bug",
        project_path="/path/to/project"
    )
    print(f"原始: {result['original']}")
    print(f"增强: {result['enhanced']}")
    print(f"上下文已注入: {result['context_injected']}")

asyncio.run(main())
```

##### `clear_cache()`

**功能**: 清除上下文缓存

**示例**:
```python
generator = EnhancedPromptGenerator()
# ... 使用生成器 ...
generator.clear_cache()  # 清除缓存，释放内存
```

---

### 便捷函数

#### `async enhance_prompt_with_context(prompt: str, project_path: Optional[str] = None, timeout: int = 60, progress_callback: Optional[Callable] = None, cancel_token: Optional[asyncio.Event] = None) -> Dict[str, Any]`

**功能**: 便捷函数，一行代码增强提示词

**参数**: 同 `EnhancedPromptGenerator.enhance()`

**返回值**: 同 `EnhancedPromptGenerator.enhance()`

**示例**:
```python
import asyncio
from enhanced_prompt_generator import enhance_prompt_with_context

async def main():
    result = await enhance_prompt_with_context(
        "添加用户身份验证功能",
        project_path="/path/to/project"
    )
    print(result["enhanced"])

asyncio.run(main())
```

---

## 错误处理

### 常见错误和解决方案

#### 1. `ValueError: DEEPSEEK_API_KEY 环境变量未设置`

**原因**: 缺少 DeepSeek API 密钥

**解决**:
```bash
# 方案 1: 在 .env 文件中设置
echo "DEEPSEEK_API_KEY=your-api-key-here" > .env

# 方案 2: 通过环境变量设置
export DEEPSEEK_API_KEY=your-api-key-here
```

#### 2. `FileNotFoundError: 项目路径不存在`

**原因**: 提供的项目路径不存在

**解决**:
```python
from pathlib import Path

project_path = "/path/to/project"
if not Path(project_path).exists():
    print(f"项目路径不存在: {project_path}")
else:
    context = collect_project_context(project_path)
```

#### 3. `asyncio.TimeoutError: 操作超时`

**原因**: API 调用超过指定的超时时间

**解决**:
```python
# 增加超时时间
result = await enhancer.enhance(
    "提示词",
    timeout=120  # 从默认 60 秒增加到 120 秒
)
```

---

## 性能基准

基于 P0.6 扩展测试套件的性能数据：

| 场景 | 性能 | 备注 |
|-----|-----|------|
| 小型项目 (< 100 文件) | ~ 585ms | 缓存后: < 2ms |
| 中型项目 (100-1000 文件) | ~ 700ms | 包括 Git 分析 |
| 大型项目 (> 1000 文件) | ~ 850ms | 缓存效率高 |
| 缓存命中率 | > 99% | 相同路径下 |

---

## 最佳实践

### 1. 缓存管理

```python
# 不好: 每次都重新收集
for project in projects:
    context = collect_project_context(project)

# 好: 使用单个生成器实例，利用缓存
generator = EnhancedPromptGenerator()
for project in projects:
    result = await generator.enhance("prompt", project_path=project)
    # 缓存会自动重用相同项目的上下文
```

### 2. 错误处理

```python
try:
    result = await generator.enhance(prompt, project_path=path)
    if not result["success"]:
        print(f"增强失败: {result.get('error')}")
except Exception as e:
    print(f"异常发生: {e}")
```

### 3. 超时配置

```python
# 根据项目大小调整超时
if project_size > 5000:  # 文件数
    timeout = 120
elif project_size > 1000:
    timeout = 90
else:
    timeout = 60

result = await enhancer.enhance(prompt, timeout=timeout)
```

### 4. 进度反馈

```python
async def show_progress(message: str, progress: float):
    bar_length = 20
    filled = int(bar_length * progress)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"{message}: [{bar}] {progress*100:.0f}%")

result = await generator.enhance(
    prompt,
    project_path=path,
    progress_callback=show_progress
)
```

---

## 相关文档

- [ARCHITECTURE.md](ARCHITECTURE.md) - 系统架构设计
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - 测试运行和编写指南
- [QUICK_REFERENCE_INIT.md](QUICK_REFERENCE_INIT.md) - 快速参考

---

**文档维护者**: Jodykwong
**最后更新**: 2025-12-10
**状态**: ✅ P0.6 完成
