# 📖 用户使用指南

**版本**: P0.6 | **最后更新**: 2025-12-10

Prompt Enhancement 系统的完整使用指南，涵盖所有功能和高级特性。

---

## 📚 目录

1. [系统介绍](#系统介绍)
2. [安装和配置](#安装和配置)
3. [核心概念](#核心概念)
4. [基础使用](#基础使用)
5. [高级功能](#高级功能)
6. [集成到工具](#集成到工具)
7. [性能优化](#性能优化)
8. [故障排除](#故障排除)

---

## 系统介绍

### 什么是 Prompt Enhancement？

Prompt Enhancement 是一个智能提示词增强系统，能够：

1. **自动分析项目** - 识别技术栈、项目结构、Git 历史
2. **智能增强提示词** - 根据项目上下文，将模糊的提示转化为清晰的指令
3. **提升 AI 响应质量** - 为 AI 模型提供充分的上下文，获得更好的回答

### 工作原理

```
用户提示词 (模糊)
    ↓
项目上下文分析 (自动)
    ↓
智能增强 (AI 驱动)
    ↓
增强提示词 (具体且可执行)
```

### 核心特点

✨ **自动化** - 无需手动输入项目信息，自动检测和分析
⚡ **高效** - 智能缓存，相同项目后续处理 < 2ms
🔄 **异步** - 完全异步设计，不阻塞主线程
🛡️ **可靠** - 完善的错误处理和容错机制
🎯 **灵活** - 支持多种使用模式和集成方式

---

## 安装和配置

### 前置要求

- **Python 3.8+**
- **pip** (Python 包管理工具)
- **Git** (用于分析项目 Git 历史)

### 完整安装步骤

#### 1. 获取项目

```bash
# 克隆项目
git clone <your-repo-url>
cd Prompt-Enhancement

# 或从 ZIP 解压
unzip Prompt-Enhancement.zip
cd Prompt-Enhancement
```

#### 2. 创建虚拟环境 (推荐)

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### 3. 安装依赖

```bash
# 安装项目依赖
pip install -r requirements.txt

# 安装开发依赖 (可选)
pip install pytest pytest-asyncio coverage
```

#### 4. 配置 API 密钥

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件
nano .env
```

编辑内容：
```env
# 必须配置：DeepSeek API 密钥
DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# 可选配置：OpenAI API 密钥
OPENAI_API_KEY=sk-your-openai-key-here
```

#### 5. 验证安装

```bash
# 运行验证脚本
python3 verify_p0_5.py

# 预期输出
# 验证结果: 5/5 通过 ✓
```

---

## 核心概念

### 1. 项目上下文

项目上下文包含以下信息：

```python
context = {
    "summary": "Python Django Web 应用",  # 项目摘要
    "tech_stack": ["Python", "Django"],   # 技术栈
    "project_structure": {...},           # 项目结构
    "git_history": {...},                 # Git 信息
    "context_string": "..."               # 格式化字符串
}
```

**何时收集**：
- 首次指定 `project_path` 时自动收集
- 后续使用缓存，< 2ms 返回

### 2. 提示词增强

增强过程：
```
原始: "优化代码"
↓
增强: "
1. 性能分析
   - 使用性能分析工具测试
   - 识别瓶颈
2. 优化方案
   - 重构热点代码
   - 优化数据结构
..."
```

**何时发生**：
- 每次调用 `enhance()` 时通过 DeepSeek API 进行
- 不使用缓存（始终获得最新结果）

### 3. 缓存机制

**缓存对象**：项目上下文（不缓存增强结果）

**缓存策略**：
- Key: 项目路径的绝对路径
- Value: 项目上下文信息
- 有效期: 直到手动 `clear_cache()` 或程序退出

**性能影响**：
```
首次加载: 800ms  (收集 + 缓存)
后续使用: < 2ms  (从缓存读取)
```

---

## 基础使用

### 模式 1: 纯提示词增强 (无上下文)

**何时使用**：通用提示词，不涉及特定项目

```python
import asyncio
from enhanced_prompt_generator import enhance_prompt_with_context

async def main():
    result = await enhance_prompt_with_context("优化代码性能")
    print(result["enhanced"])

asyncio.run(main())
```

### 模式 2: 基于项目的增强 (推荐)

**何时使用**：涉及特定项目的任务

```python
import asyncio
from enhanced_prompt_generator import enhance_prompt_with_context

async def main():
    result = await enhance_prompt_with_context(
        "添加用户认证功能",
        project_path="/path/to/my/project"
    )
    print(f"增强后的提示词:\n{result['enhanced']}")
    print(f"\n上下文已注入: {result['context_injected']}")

asyncio.run(main())
```

**项目路径方式**：
```python
# 方式 1: 绝对路径 (推荐)
project_path="/Users/john/projects/my-app"

# 方式 2: 相对路径
project_path="./my-app"

# 方式 3: 当前目录
project_path="./"  # 或 os.getcwd()
```

### 模式 3: 仅收集上下文

**何时使用**：只需获取项目信息，不进行增强

```python
from context_collector import collect_project_context

context = collect_project_context("/path/to/project")

print("项目摘要:", context["summary"])
print("技术栈:", context["tech_stack"])
print("上下文字符串:")
print(context["context_string"])
```

### 模式 4: 使用类接口 (完整控制)

**何时使用**：需要复用生成器实例，管理缓存

```python
import asyncio
from enhanced_prompt_generator import EnhancedPromptGenerator

async def main():
    # 创建生成器实例
    generator = EnhancedPromptGenerator()

    # 增强多个提示词
    prompts = [
        "修复 bug",
        "优化数据库查询",
        "添加日志记录"
    ]

    for prompt in prompts:
        result = await generator.enhance(
            prompt,
            project_path="/path/to/project"
        )
        print(f"✓ {prompt}")
        print(f"  {result['enhanced'][:50]}...\n")

    # 清除缓存，释放内存
    generator.clear_cache()

asyncio.run(main())
```

---

## 高级功能

### 1. 进度监控

**使用场景**：长时间操作，用户需要知道处理进度

```python
import asyncio
from enhanced_prompt_generator import EnhancedPromptGenerator

async def progress_handler(message: str, progress: float):
    """进度回调函数"""
    bar_length = 30
    filled = int(bar_length * progress)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\r{message}: [{bar}] {progress*100:.0f}%", end="", flush=True)
    await asyncio.sleep(0)

async def main():
    generator = EnhancedPromptGenerator()

    result = await generator.enhance(
        "重构数据库层",
        project_path="/path/to/project",
        progress_callback=progress_handler
    )

    print("\n完成!")
    print(result["enhanced"])

asyncio.run(main())
```

**进度值说明**：
- `0.0` - 开始
- `0.5` - 中间
- `1.0` - 完成

### 2. 超时控制

**使用场景**：防止长时间等待，限制单个操作的耗时

```python
import asyncio
from enhanced_prompt_generator import enhance_prompt_with_context

async def main():
    try:
        result = await enhance_prompt_with_context(
            "处理大型数据集",
            project_path="/path/to/project",
            timeout=30  # 最多等待 30 秒
        )
        print("成功！", result["enhanced"])

    except asyncio.TimeoutError:
        print("操作超时，请增加超时时间或重试")

asyncio.run(main())
```

**超时时间建议**：
- 网络良好: 30-60 秒
- 网络不稳定: 90-120 秒
- 大型项目: 120-180 秒

### 3. 取消机制

**使用场景**：用户想中断长时间的操作

```python
import asyncio
from enhanced_prompt_generator import EnhancedPromptGenerator

async def main():
    generator = EnhancedPromptGenerator()
    cancel_token = asyncio.Event()

    # 创建取消任务 (例如: 用户按 Ctrl+C)
    async def handle_user_cancel():
        # 在实际使用中，这里会监听用户输入
        await asyncio.sleep(3)  # 3 秒后取消
        print("\n用户取消操作")
        cancel_token.set()

    asyncio.create_task(handle_user_cancel())

    result = await generator.enhance(
        "优化应用",
        project_path="/path/to/project",
        cancel_token=cancel_token
    )

    if result.get("cancelled"):
        print("操作已被取消")
    else:
        print(result["enhanced"])

asyncio.run(main())
```

### 4. 批量处理

**使用场景**：有多个提示词要处理

```python
import asyncio
from enhanced_prompt_generator import EnhancedPromptGenerator

async def main():
    generator = EnhancedPromptGenerator()

    tasks_file = [
        ("优化查询性能", "/path/to/backend"),
        ("改进 UI 响应", "/path/to/frontend"),
        ("增加错误处理", "/path/to/backend")
    ]

    results = []

    # 方式 1: 串行处理 (简单，但较慢)
    for prompt, path in tasks_file:
        result = await generator.enhance(prompt, project_path=path)
        results.append((prompt, result["enhanced"]))

    # 方式 2: 并行处理 (快，但需要注意 API 速率限制)
    tasks = [
        generator.enhance(prompt, project_path=path)
        for prompt, path in tasks_file
    ]
    results = await asyncio.gather(*tasks)

    # 输出结果
    for prompt, enhanced in results:
        print(f"✓ {prompt}")
        print(f"  {enhanced[:60]}...\n")

asyncio.run(main())
```

---

## 集成到工具

### 集成到 Claude Code CLI

```bash
# 在 Claude Code 中作为自定义命令使用
aug enhance "修复 bug" --project ./

# 交互式模式
aug enhance --interactive --project ./
```

### 集成到 Python 项目

```python
# 在你的项目中导入使用
from enhanced_prompt_generator import enhance_prompt_with_context

async def generate_fix_prompt(bug_description: str):
    """根据 bug 描述生成修复提示词"""
    result = await enhance_prompt_with_context(
        bug_description,
        project_path="./"
    )
    return result["enhanced"]
```

### 集成到 Web 应用

```python
from fastapi import FastAPI
from enhanced_prompt_generator import enhance_prompt_with_context
import asyncio

app = FastAPI()

@app.post("/enhance-prompt")
async def enhance(prompt: str, project_path: str = None):
    """增强提示词的 API 端点"""
    result = await enhance_prompt_with_context(
        prompt,
        project_path=project_path
    )
    return {
        "enhanced": result["enhanced"],
        "success": result["success"],
        "processing_time": result["processing_time"]
    }
```

---

## 性能优化

### 1. 缓存管理

**最小化缓存大小**：
```python
generator = EnhancedPromptGenerator()

# 处理多个项目
for project_path in ["/project1", "/project2", "/project3"]:
    result = await generator.enhance(prompt, project_path=project_path)
    # 每个项目会被缓存

# 定期清除缓存
generator.clear_cache()
```

**缓存大小估计**：
- 单个项目: ~ 10-50KB
- 100 个项目: ~ 1-5MB

### 2. 批量处理优化

**使用相同的生成器实例**：
```python
# ✅ 好: 复用实例，利用缓存
generator = EnhancedPromptGenerator()
for prompt in prompts:
    result = await generator.enhance(prompt, project_path)

# ❌ 不好: 每次创建新实例，缓存失效
for prompt in prompts:
    generator = EnhancedPromptGenerator()  # 每次都重新创建
    result = await generator.enhance(prompt, project_path)
```

### 3. 并发优化

**合理设置并发数**：
```python
import asyncio
from enhanced_prompt_generator import EnhancedPromptGenerator

async def main():
    generator = EnhancedPromptGenerator()
    prompts = [...]

    # 限制并发数 (避免过载)
    semaphore = asyncio.Semaphore(5)  # 最多 5 个并发

    async def enhance_with_limit(prompt):
        async with semaphore:
            return await generator.enhance(prompt, project_path)

    results = await asyncio.gather(*[
        enhance_with_limit(p) for p in prompts
    ])
```

---

## 故障排除

### 错误: `DEEPSEEK_API_KEY 未设置`

**原因**: 没有配置 API 密钥

**解决**:
```bash
# 检查 .env 文件
cat .env

# 验证 DEEPSEEK_API_KEY 已设置
grep DEEPSEEK_API_KEY .env
```

如果文件不存在或密钥缺失，创建/编辑 `.env`：
```env
DEEPSEEK_API_KEY=sk-your-key-here
```

### 错误: `FileNotFoundError: 项目路径不存在`

**原因**: 提供的项目路径不存在

**解决**:
```python
from pathlib import Path
import os

# 检查路径是否存在
project_path = "/path/to/project"
if not Path(project_path).exists():
    print(f"错误: 路径不存在: {project_path}")

# 使用绝对路径
import os
absolute_path = os.path.abspath("./my-project")
print(f"绝对路径: {absolute_path}")

# 验证路径
print(f"路径存在: {os.path.isdir(absolute_path)}")
```

### 错误: `asyncio.TimeoutError`

**原因**: 操作超过了超时时间

**解决**:
```python
# 增加超时时间
result = await generator.enhance(
    prompt,
    project_path=path,
    timeout=180  # 从默认 60 增加到 180 秒
)
```

**何时需要更长的超时**：
- 项目文件超过 1000 个
- 网络连接不稳定
- API 服务响应较慢

### 错误: `Memory Error / 内存不足`

**原因**: 缓存了过多项目的上下文

**解决**:
```python
generator = EnhancedPromptGenerator()

# ... 处理多个项目 ...

# 定期清除缓存
generator.clear_cache()
print("缓存已清除")

# 或使用上下文管理器 (未来支持)
# async with EnhancedPromptGenerator() as gen:
#     result = await gen.enhance(prompt, project_path)
# # 自动清除缓存
```

### 性能较慢

**原因**: 可能是网络问题或项目较大

**诊断**:
```python
import time

start = time.time()
result = await generator.enhance(prompt, project_path)
elapsed = time.time() - start

print(f"处理耗时: {elapsed:.2f}s")
print(f"处理时间: {result['processing_time']:.2f}s")

# 如果网络正常，可以尝试
# 1. 增加项目大小限制
# 2. 优化网络连接
# 3. 使用缓存
```

### API 限速错误

**原因**: 超过了 API 的速率限制

**解决**:
```python
import asyncio
from enhanced_prompt_generator import EnhancedPromptGenerator

async def rate_limited_enhance(generator, prompts):
    """带速率限制的增强"""
    for prompt in prompts:
        try:
            result = await generator.enhance(prompt, project_path)
            print(f"✓ {prompt}")
        except Exception as e:
            if "rate limit" in str(e).lower():
                print(f"触发速率限制，等待 60 秒...")
                await asyncio.sleep(60)  # 等待后重试
                result = await generator.enhance(prompt, project_path)
            else:
                raise

asyncio.run(rate_limited_enhance(generator, prompts))
```

---

## 相关资源

- **[QUICK_START.md](QUICK_START.md)** - 5 分钟快速开始
- **[API_REFERENCE.md](API_REFERENCE.md)** - 完整 API 参考
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - 测试指南
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 系统架构

---

**用户指南完整！**

如有任何问题或建议，欢迎反馈。

---

**作者**: Jodykwong
**最后更新**: 2025-12-10
**版本**: P0.6
