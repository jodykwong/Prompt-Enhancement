#!/usr/bin/env python3
"""
增强器集成模块 - Enhanced Prompt Generator

这个模块实现将项目上下文与异步提示词增强器整合的功能，包括：
1. 自动收集项目上下文（技术栈、项目结构、Git 历史）
2. 将上下文注入到提示词增强流程中
3. 根据项目类型自动调整增强策略
4. 利用缓存机制避免重复分析

**使用示例**：

```python
from enhanced_prompt_generator import enhance_prompt_with_context
import asyncio

# 基础使用
result = await enhance_prompt_with_context(
    "修复 bug",
    project_path="/path/to/project"
)
print(result["enhanced"])

# 不带项目上下文
result = await enhance_prompt_with_context("修复 bug")
print(result["enhanced"])
```

**返回值结构**：

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
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional, Callable, Any, Awaitable

from async_prompt_enhancer import AsyncPromptEnhancer
from context_collector import collect_project_context

# 配置日志
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


class EnhancedPromptGenerator:
    """增强器集成类"""

    def __init__(self, model: str = "deepseek-reasoner"):
        """
        初始化增强器集成器

        Args:
            model: 使用的模型名称，默认为 deepseek-reasoner
        """
        self.enhancer = AsyncPromptEnhancer(model=model)
        self._context_cache = {}

    async def enhance(
        self,
        original_prompt: str,
        project_path: Optional[str] = None,
        timeout: int = 60,
        progress_callback: Optional[Callable[[str, float], Awaitable[None]]] = None,
        cancel_token: Optional[asyncio.Event] = None
    ) -> Dict[str, Any]:
        """
        增强提示词，可选地注入项目上下文

        Args:
            original_prompt: 原始提示词
            project_path: 项目路径（可选）
            timeout: API 调用超时时间（秒）
            progress_callback: 进度回调函数
            cancel_token: 取消令牌

        Returns:
            包含增强结果的字典
        """
        context_info = None
        context_injected = False
        context_summary = ""

        # 尝试收集项目上下文
        if project_path:
            try:
                context_info = self._collect_context(project_path)
                if context_info:
                    context_injected = True
                    context_summary = context_info.get("summary", "")
            except Exception as e:
                logger.warning(f"收集项目上下文失败: {e}")

        # 构建增强后的提示词
        enhanced_original = self._inject_context(original_prompt, context_info)

        # 调用异步增强器
        result = await self.enhancer.enhance(
            enhanced_original,
            timeout=timeout,
            progress_callback=progress_callback,
            cancel_token=cancel_token
        )

        # 添加上下文相关信息
        result["context_injected"] = context_injected
        result["context_summary"] = context_summary

        return result

    def _collect_context(self, project_path: str) -> Optional[Dict[str, Any]]:
        """收集项目上下文"""
        try:
            # 验证路径有效性
            if not project_path:
                logger.warning("项目路径不能为空")
                return None

            path_obj = Path(project_path)
            if not path_obj.exists():
                logger.warning(f"项目路径不存在: {project_path}")
                return None

            path = str(path_obj.resolve())
            if path not in self._context_cache:
                context = collect_project_context(project_path)
                # 如果返回空字典，缓存为 None
                self._context_cache[path] = context if context else None
            return self._context_cache[path]
        except Exception as e:
            logger.warning(f"收集上下文失败: {e}")
            return None

    def _inject_context(
        self,
        original_prompt: str,
        context_info: Optional[Dict[str, Any]]
    ) -> str:
        """将上下文注入到提示词中"""
        if not context_info:
            return original_prompt

        context_string = context_info.get("context_string", "")
        if not context_string:
            return original_prompt

        return f"""{context_string}

---

**用户请求**：

{original_prompt}"""

    def clear_cache(self):
        """清除缓存"""
        self._context_cache.clear()


async def enhance_prompt_with_context(
    prompt: str,
    project_path: Optional[str] = None,
    timeout: int = 60,
    progress_callback: Optional[Callable[[str, float], Awaitable[None]]] = None,
    cancel_token: Optional[asyncio.Event] = None
) -> Dict[str, Any]:
    """
    便捷函数：增强提示词，可选地注入项目上下文

    Args:
        prompt: 原始提示词
        project_path: 项目路径（可选）
        timeout: API 调用超时时间（秒）
        progress_callback: 进度回调函数
        cancel_token: 取消令牌

    Returns:
        包含增强结果的字典
    """
    generator = EnhancedPromptGenerator()
    return await generator.enhance(
        prompt,
        project_path=project_path,
        timeout=timeout,
        progress_callback=progress_callback,
        cancel_token=cancel_token
    )


if __name__ == "__main__":
    # 命令行使用示例
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python3 enhanced_prompt_generator.py <prompt> [project_path]")
        sys.exit(1)

    prompt = sys.argv[1]
    project_path = sys.argv[2] if len(sys.argv) > 2 else None

    async def main():
        result = await enhance_prompt_with_context(prompt, project_path)
        print(f"原始提示词: {result['original'][:100]}...")
        print(f"增强提示词: {result['enhanced'][:100]}...")
        print(f"上下文已注入: {result['context_injected']}")

    asyncio.run(main())

