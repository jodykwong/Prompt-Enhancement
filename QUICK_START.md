# 🚀 快速开始指南 (5 分钟)

**版本**: P0.6 | **最后更新**: 2025-12-10

5 分钟内上手 Prompt Enhancement 系统！

---

## ⚡ 安装 (1 分钟)

### 1. 克隆项目

```bash
git clone <repository-url>
cd Prompt-Enhancement
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API 密钥

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，添加你的 API 密钥
nano .env  # 或使用其他编辑器
```

编辑内容示例：
```
DEEPSEEK_API_KEY=sk-your-key-here
OPENAI_API_KEY=sk-your-key-here  # 可选
```

---

## 💻 基础使用 (2 分钟)

### 方式 1: 不带项目上下文

**最简单** - 直接增强提示词，不需要项目信息

```python
import asyncio
from enhanced_prompt_generator import enhance_prompt_with_context

async def main():
    result = await enhance_prompt_with_context("修复 bug")
    print("增强后的提示词:")
    print(result["enhanced"])

asyncio.run(main())
```

### 方式 2: 带项目上下文 (推荐)

**最强大** - 自动分析项目，提升增强质量

```python
import asyncio
from enhanced_prompt_generator import enhance_prompt_with_context

async def main():
    result = await enhance_prompt_with_context(
        "修复登录模块的 bug",
        project_path="/path/to/my/project"
    )
    print("原始提示词:")
    print(result["original"])
    print("\n增强后的提示词:")
    print(result["enhanced"])
    print(f"\n上下文已注入: {result['context_injected']}")

asyncio.run(main())
```

### 方式 3: 收集项目上下文

**低级接口** - 仅收集上下文，不增强提示词

```python
from context_collector import collect_project_context

context = collect_project_context("/path/to/my/project")
print("项目摘要:")
print(context["summary"])
print("\n技术栈:")
print(context["tech_stack"])
print("\n完整上下文:")
print(context["context_string"])
```

---

## 🎯 常见使用场景

### 场景 1: 快速开发提示

**需求**: 你想快速告诉 AI 你要做什么

```python
import asyncio
from enhanced_prompt_generator import enhance_prompt_with_context

async def main():
    # 简单的提示词
    result = await enhance_prompt_with_context(
        "添加用户认证功能",
        project_path="./"  # 当前项目
    )
    # 得到详细的、结构化的增强提示词
    print(result["enhanced"])

asyncio.run(main())
```

### 场景 2: 批量处理多个提示词

**需求**: 你有多个提示词要增强，想复用项目上下文

```python
import asyncio
from enhanced_prompt_generator import EnhancedPromptGenerator

async def main():
    generator = EnhancedPromptGenerator()

    prompts = [
        "优化数据库查询",
        "修复 API 超时问题",
        "添加错误日志记录"
    ]

    for prompt in prompts:
        result = await generator.enhance(
            prompt,
            project_path="/path/to/project"
        )
        print(f"原始: {prompt}")
        print(f"增强: {result['enhanced']}\n")

    # 清除缓存，释放内存
    generator.clear_cache()

asyncio.run(main())
```

### 场景 3: 带进度反馈

**需求**: 你想看到实时的处理进度

```python
import asyncio
from enhanced_prompt_generator import EnhancedPromptGenerator

async def show_progress(message: str, progress: float):
    """显示进度"""
    bar_length = 20
    filled = int(bar_length * progress)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\r{message}: [{bar}] {progress*100:.0f}%", end="")

async def main():
    generator = EnhancedPromptGenerator()

    result = await generator.enhance(
        "优化应用性能",
        project_path="/path/to/project",
        progress_callback=show_progress
    )

    print("\n增强完成!")
    print(result["enhanced"])

asyncio.run(main())
```

### 场景 4: 控制超时和取消

**需求**: 你想限制处理时间或支持用户取消

```python
import asyncio
from enhanced_prompt_generator import EnhancedPromptGenerator

async def main():
    generator = EnhancedPromptGenerator()
    cancel_token = asyncio.Event()

    # 在 5 秒后自动取消
    async def auto_cancel():
        await asyncio.sleep(5)
        cancel_token.set()

    asyncio.create_task(auto_cancel())

    try:
        result = await generator.enhance(
            "处理大型数据集",
            project_path="/path/to/project",
            timeout=120,  # 最多等待 120 秒
            cancel_token=cancel_token
        )

        if result.get("cancelled"):
            print("操作已被用户取消")
        else:
            print(result["enhanced"])

    except asyncio.TimeoutError:
        print("操作超时，请增加超时时间或项目较大")

asyncio.run(main())
```

---

## 📊 理解输出结果

运行增强后，你会得到以下结构的结果：

```python
{
    # 基础信息
    "original": str,           # 原始提示词，例如: "修复 bug"
    "enhanced": str,           # 增强后的提示词（最重要！）

    # 额外信息
    "reasoning": str,          # AI 的思考过程
    "processing_time": 2.3,    # 处理耗时（秒）
    "success": True,           # 是否成功

    # 上下文相关
    "context_injected": True,  # 是否注入了项目上下文
    "context_summary": "...",  # 上下文摘要

    # 统计信息
    "stats": {
        "input_tokens": 150,
        "output_tokens": 450,
        "total_tokens": 600
    }
}
```

### 最重要的字段

✨ **`result["enhanced"]`** - 增强后的提示词，直接用于 AI 提示

---

## 🔧 命令行使用

### 快速增强单个提示词

```bash
python3 enhanced_prompt_generator.py "优化代码性能" "/path/to/project"
```

### 输出示例

```
原始提示词: 优化代码性能
增强提示词: 针对项目的代码性能优化
          1. 性能诊断...
          2. 优化策略...
          3. 验证方法...
上下文已注入: True
```

---

## ✅ 验证安装

运行验证脚本确保一切正常工作：

```bash
# 验证 P0.4 (上下文收集器)
python3 verify_p0_4.py

# 验证 P0.5 (增强器集成)
python3 verify_p0_5.py

# 预期输出: 所有测试通过 ✓
```

---

## 🚨 常见问题

### 问题 1: `ValueError: DEEPSEEK_API_KEY 环境变量未设置`

**原因**: 没有配置 API 密钥

**解决**:
```bash
# 检查 .env 文件是否存在
cat .env

# 或设置环境变量
export DEEPSEEK_API_KEY=your-api-key
```

### 问题 2: `FileNotFoundError: 项目路径不存在`

**原因**: 提供的项目路径错误

**解决**:
```python
from pathlib import Path

# 验证路径
project_path = "/path/to/project"
print(f"路径存在: {Path(project_path).exists()}")

# 使用绝对路径
import os
absolute_path = os.path.abspath("./my-project")
result = await enhance_prompt_with_context(prompt, project_path=absolute_path)
```

### 问题 3: `asyncio.TimeoutError`

**原因**: 操作超过了超时时间

**解决**:
```python
# 增加超时时间
result = await generator.enhance(
    prompt,
    project_path=path,
    timeout=180  # 增加到 180 秒
)
```

### 问题 4: 性能较慢（> 1 秒）

**原因**: 项目较大或网络延迟

**解决**:
```python
generator = EnhancedPromptGenerator()

# 第一次会较慢（收集上下文）
result1 = await generator.enhance(prompt, project_path=path)  # ~ 800ms

# 同一项目的后续请求会快得多（使用缓存）
result2 = await generator.enhance(prompt2, project_path=path)  # < 5ms
```

---

## 📚 下一步

现在你已经掌握了基础！继续学习：

- **[USER_GUIDE.md](USER_GUIDE.md)** - 详细的使用指南，涵盖所有功能
- **[API_REFERENCE.md](API_REFERENCE.md)** - 完整的 API 文档
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - 如何编写和运行测试
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 理解系统设计

---

## 💡 最佳实践速查

| 场景 | 推荐做法 |
|-----|--------|
| 快速增强 | 使用 `enhance_prompt_with_context()` 函数 |
| 批量处理 | 创建一个 `EnhancedPromptGenerator()` 实例并复用 |
| 大项目 | 增加 `timeout` 参数或使用缓存 |
| 监控进度 | 提供 `progress_callback` 参数 |
| 支持取消 | 使用 `cancel_token` 参数 |
| 释放内存 | 调用 `generator.clear_cache()` |

---

**快速开始指南完成！🎉**

有任何问题？查看 [USER_GUIDE.md](USER_GUIDE.md) 获取更详细的帮助。

---

**作者**: Jodykwong
**最后更新**: 2025-12-10
