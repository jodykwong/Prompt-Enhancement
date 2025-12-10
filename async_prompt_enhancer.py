#!/usr/bin/env python3
"""
异步提示词增强器 - Async Prompt Enhancer

这个模块提供异步版本的提示词增强功能，支持：
1. 异步 API 调用（不阻塞主线程）
2. 进度回调（实时反馈增强进度）
3. 取消机制（支持用户中断操作）
4. 超时控制（防止无限等待）

**使用场景**：
- Claude Code 集成（异步环境）
- 长时间运行的批量增强
- 需要进度反馈的应用

**API 签名**：
    async def enhance(
        original_prompt: str,
        timeout: int = 60,
        progress_callback: Optional[Callable[[str, float], Awaitable[None]]] = None,
        cancel_token: Optional[asyncio.Event] = None
    ) -> Dict[str, any]

**参数说明**：
- original_prompt: 原始提示词
- timeout: API 调用超时时间（秒），默认 60 秒
- progress_callback: 进度回调函数，签名为 async def callback(message: str, progress: float)
  其中 progress 范围为 0.0-1.0
- cancel_token: 取消令牌，使用 asyncio.Event 实现

**返回值**：
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

**使用示例**：

1. 基础使用：
    enhancer = AsyncPromptEnhancer()
    result = await enhancer.enhance("修复 bug")

2. 带进度回调：
    async def progress_handler(message: str, progress: float):
        print(f"{message}: {progress*100:.0f}%")
    
    result = await enhancer.enhance(
        "修复 bug",
        progress_callback=progress_handler
    )

3. 支持取消：
    cancel_token = asyncio.Event()
    
    # 在另一个任务中取消
    asyncio.create_task(cancel_after_delay(cancel_token, 5))
    
    result = await enhancer.enhance(
        "修复 bug",
        cancel_token=cancel_token
    )

4. 自定义超时：
    result = await enhancer.enhance(
        "修复 bug",
        timeout=120  # 120 秒超时
    )
"""

import os
import sys
import asyncio
import time
from typing import Dict, Optional, Callable, Any, Awaitable
from dotenv import load_dotenv

# 尝试导入 aiohttp，如果不存在则使用同步 OpenAI 客户端的异步包装
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

from openai import AsyncOpenAI

# 加载 .env 文件中的环境变量
load_dotenv()


# 系统提示词模板（与同步版本保持一致）
ENHANCEMENT_SYSTEM_PROMPT = """你是一个专业的提示词增强助手。你的任务是将用户的简单提示词转化为清晰、具体、可执行的增强版本。

**核心原则：**
1. **保持原意**：绝不改变用户的原始意图
2. **简洁实用**：增强后的提示词应该简洁、直接、易于执行
3. **结构清晰**：使用编号列表或分步骤的方式组织
4. **适度详细**：提供必要的细节，但避免过度冗长

**增强策略：**
- 将模糊的动词（如"优化"、"修复"）转化为具体的行动步骤
- 补充必要的上下文和验证标准
- 保持语言风格一致（中文/英文/混合）

**上下文补充策略：**
- 假设常见的代码仓库结构（如 src/, tests/, components/, api/, utils/）
- 推断常见的技术栈（React, Vue, Node.js, Django, FastAPI 等）
- 补充文件路径和依赖关系信息
- 提供代码模式和最佳实践建议

**长度控制：**
- 原始提示词 10-50 字：增强 3-5 倍
- 原始提示词 50+ 字：增强 2-3 倍
- 最终长度不超过 500 字

**输出格式：**
直接输出增强后的提示词，不需要额外说明。"""


class AsyncPromptEnhancer:
    """
    异步提示词增强器
    
    提供异步版本的提示词增强功能，支持进度回调和取消机制。
    """
    
    def __init__(self, model: str = "deepseek-reasoner"):
        """
        初始化异步增强器
        
        Args:
            model: 使用的模型名称，默认为 deepseek-reasoner
            
        Raises:
            ValueError: 如果 DEEPSEEK_API_KEY 环境变量未设置
        """
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "❌ DEEPSEEK_API_KEY 环境变量未设置\n"
                "请在 .env 文件中设置 DEEPSEEK_API_KEY，或通过以下命令设置：\n"
                "export DEEPSEEK_API_KEY='your-api-key'"
            )
        
        self.model = model
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
    
    async def enhance(
        self,
        original_prompt: str,
        timeout: int = 60,
        progress_callback: Optional[Callable[[str, float], Awaitable[None]]] = None,
        cancel_token: Optional[asyncio.Event] = None
    ) -> Dict[str, Any]:
        """
        异步增强提示词
        
        Args:
            original_prompt: 原始提示词
            timeout: API 调用超时时间（秒），默认 60 秒
            progress_callback: 进度回调函数，签名为 async def callback(message: str, progress: float)
            cancel_token: 取消令牌，使用 asyncio.Event 实现
            
        Returns:
            包含增强结果的字典
        """
        start_time = time.time()
        
        try:
            # 检查取消令牌
            if cancel_token and cancel_token.is_set():
                return self._create_cancelled_result(original_prompt, start_time)
            
            # 进度回调：开始
            if progress_callback:
                await progress_callback("正在调用 API...", 0.1)
            
            # 检查取消令牌
            if cancel_token and cancel_token.is_set():
                return self._create_cancelled_result(original_prompt, start_time)
            
            # 异步调用 DeepSeek API
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=4096,
                    timeout=timeout,
                    messages=[
                        {
                            "role": "system",
                            "content": ENHANCEMENT_SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content": f"请增强以下提示词：\n\n{original_prompt}"
                        }
                    ]
                ),
                timeout=timeout
            )
            
            # 进度回调：接收响应
            if progress_callback:
                await progress_callback("正在接收响应...", 0.5)
            
            # 检查取消令牌
            if cancel_token and cancel_token.is_set():
                return self._create_cancelled_result(original_prompt, start_time)
            
            # 提取结果
            reasoning_content = response.choices[0].message.reasoning_content
            enhanced_prompt = response.choices[0].message.content
            processing_time = time.time() - start_time
            
            # 计算统计信息
            stats = {
                "original_length": len(original_prompt),
                "enhanced_length": len(enhanced_prompt) if enhanced_prompt else 0,
                "reasoning_length": len(reasoning_content) if reasoning_content else 0,
                "expansion_ratio": round(
                    len(enhanced_prompt) / len(original_prompt), 2
                ) if enhanced_prompt and original_prompt else 0
            }
            
            # 进度回调：完成
            if progress_callback:
                await progress_callback("处理完成", 1.0)
            
            return {
                "original": original_prompt,
                "enhanced": enhanced_prompt,
                "reasoning": reasoning_content,
                "processing_time": processing_time,
                "success": True,
                "error": None,
                "stats": stats,
                "cancelled": False
            }
        
        except asyncio.TimeoutError:
            processing_time = time.time() - start_time
            return {
                "original": original_prompt,
                "enhanced": None,
                "reasoning": None,
                "processing_time": processing_time,
                "success": False,
                "error": f"API 调用超时（超过 {timeout} 秒）",
                "stats": None,
                "cancelled": False
            }
        
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "original": original_prompt,
                "enhanced": None,
                "reasoning": None,
                "processing_time": processing_time,
                "success": False,
                "error": str(e),
                "stats": None,
                "cancelled": False
            }
    
    def _create_cancelled_result(self, original_prompt: str, start_time: float) -> Dict[str, Any]:
        """创建被取消的结果"""
        return {
            "original": original_prompt,
            "enhanced": None,
            "reasoning": None,
            "processing_time": time.time() - start_time,
            "success": False,
            "error": "用户取消操作",
            "stats": None,
            "cancelled": True
        }
    
    async def enhance_batch(
        self,
        prompts: list,
        progress_callback: Optional[Callable[[str, float], Awaitable[None]]] = None,
        cancel_token: Optional[asyncio.Event] = None
    ) -> list:
        """
        异步批量增强提示词
        
        Args:
            prompts: 原始提示词列表
            progress_callback: 进度回调函数
            cancel_token: 取消令牌
            
        Returns:
            增强结果列表
        """
        results = []
        total = len(prompts)
        
        for i, prompt in enumerate(prompts):
            # 检查取消令牌
            if cancel_token and cancel_token.is_set():
                break
            
            # 更新进度
            if progress_callback:
                progress = i / total
                await progress_callback(f"处理第 {i+1}/{total} 个提示词", progress)
            
            result = await self.enhance(
                prompt,
                progress_callback=progress_callback,
                cancel_token=cancel_token
            )
            results.append(result)
        
        return results


# 辅助函数：在指定延迟后取消操作
async def cancel_after_delay(cancel_token: asyncio.Event, delay: float):
    """
    在指定延迟后设置取消令牌
    
    Args:
        cancel_token: 取消令牌
        delay: 延迟时间（秒）
    """
    await asyncio.sleep(delay)
    cancel_token.set()


# 辅助函数：打印异步增强结果
def print_async_result(result: Dict[str, Any], index: int = None, show_reasoning: bool = True):
    """
    打印异步增强结果
    
    Args:
        result: 增强结果字典
        index: 测试用例编号（可选）
        show_reasoning: 是否显示思考过程（默认 True）
    """
    prefix = f"测试用例 {index}" if index is not None else "增强结果"
    
    print(f"\n{'='*80}")
    print(f"{prefix}")
    print(f"{'='*80}")
    
    if result["success"]:
        print(f"\n✅ 增强成功")
        print(f"\n【原始提示词】")
        print(f"{result['original']}")
        print(f"\n【增强后的提示词】")
        print(f"{result['enhanced']}")
        
        if show_reasoning and result.get("reasoning"):
            print(f"\n【模型思考过程】")
            print(f"{result['reasoning'][:500]}...")  # 只显示前 500 字
        
        if result.get("stats"):
            print(f"\n【统计信息】")
            print(f"原始长度: {result['stats']['original_length']} 字")
            print(f"增强后长度: {result['stats']['enhanced_length']} 字")
            print(f"扩展比例: {result['stats']['expansion_ratio']}x")
            print(f"处理时间: {result['processing_time']:.2f} 秒")
    
    elif result.get("cancelled"):
        print(f"\n⚠️  操作已取消")
        print(f"处理时间: {result['processing_time']:.2f} 秒")
    
    else:
        print(f"\n❌ 增强失败")
        print(f"错误信息: {result['error']}")
        print(f"处理时间: {result['processing_time']:.2f} 秒")

