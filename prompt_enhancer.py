#!/usr/bin/env python3
"""
Prompt Enhancement MVP - 提示词增强最小可行原型

这个脚本实现了基本的提示词增强功能，用于验证使用 LLM API 进行提示词增强的可行性。

**功能职责**：
- 接收原始提示词（用户输入）
- 调用 DeepSeek API 进行增强
- 返回增强后的提示词

**不负责的事项**：
- 不执行增强后的提示词
- 不将增强后的提示词作为新指令发送给 AI
- 只展示增强结果，由用户决定如何使用

**使用方式**：
1. 通过命令行参数: python prompt_enhancer.py "待增强的提示词"
2. 通过 Python API: enhancer = PromptEnhancer(); result = enhancer.enhance("待增强的提示词")
3. 通过交互式输入: 运行脚本后按提示输入
"""

import os
import sys
import json
import time
from typing import Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 文件中的环境变量
load_dotenv()


# 系统提示词模板 - 指导 LLM 如何增强用户输入
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
- 根据任务类型推断技术栈：
  * Web 前端开发 → React/Vue + TypeScript + Tailwind CSS
  * Web 后端开发 → Node.js/Django/FastAPI + 数据库（PostgreSQL/MongoDB）
  * 全栈开发 → 前端框架 + 后端框架 + 数据库
  * 移动开发 → React Native/Flutter
  * 数据处理 → Python + Pandas/NumPy
- 补充相关文件路径（如"在 src/components/Auth.js 中添加..."）
- 提及可能的依赖关系（如"确保已安装 bcrypt 库用于密码加密"）
- 参考现有的代码模式和约定

**输出要求：**
- 直接输出增强后的提示词，不要添加"增强后："等前缀
- **严格控制长度**：
  * 原始提示词 < 10 字符：增强后控制在 30-50 字符
  * 原始提示词 10-50 字符：增强后为原始的 3-5 倍
  * 原始提示词 > 50 字符：增强后为原始的 2-3 倍
- 确保每个步骤都有实际价值，避免冗余描述
- 步骤数量控制在 3-5 个，避免过多

**示例 1（短提示词）：**
原始：修复bug (5 字符)
增强：修复bug：
1. 重现问题，查看错误日志
2. 定位代码缺陷，修复问题
3. 测试验证，确保无副作用
(约 50 字符，扩展比例 10x)

**示例 2（中等提示词）：**
原始：添加用户认证功能 (10 字符)
增强：在 src/auth/ 目录中添加用户认证功能：
1. 创建 auth.js，实现登录/注册逻辑
2. 集成 bcrypt 库进行密码加密
3. 添加 JWT token 验证中间件
4. 编写单元测试，覆盖率 > 80%
(约 40-50 字符，扩展比例 4-5x)

**示例 3（长提示词）：**
原始：优化数据库查询性能，减少 N+1 问题，添加缓存机制 (30 字符)
增强：优化数据库查询性能：
1. 使用 JOIN 替代多次查询，消除 N+1 问题
2. 在 utils/cache.js 中实现 Redis 缓存
3. 添加查询结果缓存，设置 TTL 为 5 分钟
4. 运行性能测试，确保查询时间减少 50%
(约 60-90 字符，扩展比例 2-3x)
"""


class PromptEnhancer:
    """提示词增强器"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化提示词增强器

        Args:
            api_key: DeepSeek API 密钥，如果不提供则从环境变量读取
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "未找到 API 密钥。请设置 DEEPSEEK_API_KEY 环境变量或在初始化时提供 api_key 参数。"
            )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = "deepseek-reasoner"  # 使用 DeepSeek-V3.2-Speciale 思考模式
    
    def enhance(self, original_prompt: str, timeout: int = 60) -> Dict[str, any]:
        """
        增强提示词

        Args:
            original_prompt: 原始提示词
            timeout: API 调用超时时间（秒），默认 60 秒

        Returns:
            包含增强结果的字典，包括：
            - original: 原始提示词
            - enhanced: 增强后的提示词
            - reasoning: 模型的思考过程（DeepSeek 推理模式）
            - processing_time: 处理时间（秒）
            - success: 是否成功
            - error: 错误信息（如果失败）
            - stats: 统计信息（原始长度、增强后长度等）
        """
        start_time = time.time()

        try:
            # 调用 DeepSeek API 进行增强（使用 OpenAI 兼容接口）
            # 注意：deepseek-reasoner 模型不支持 temperature、top_p 等参数
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=4096,  # 增加到 4096，平衡质量和成本
                timeout=timeout,  # ✅ 添加超时控制
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
            )

            # 提取思考过程和增强后的提示词
            reasoning_content = response.choices[0].message.reasoning_content
            enhanced_prompt = response.choices[0].message.content
            processing_time = time.time() - start_time

            # 计算统计信息
            stats = {
                "original_length": len(original_prompt),
                "enhanced_length": len(enhanced_prompt) if enhanced_prompt else 0,
                "reasoning_length": len(reasoning_content) if reasoning_content else 0,
                "expansion_ratio": round(len(enhanced_prompt) / len(original_prompt), 2) if enhanced_prompt and original_prompt else 0
            }

            return {
                "original": original_prompt,
                "enhanced": enhanced_prompt,
                "reasoning": reasoning_content,
                "processing_time": processing_time,
                "success": True,
                "error": None,
                "stats": stats
            }

        except TimeoutError as e:
            # ✅ 添加超时异常处理
            processing_time = time.time() - start_time
            return {
                "original": original_prompt,
                "enhanced": None,
                "reasoning": None,
                "processing_time": processing_time,
                "success": False,
                "error": f"API 调用超时（超过 {timeout} 秒）",
                "stats": None
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
                "stats": None
            }
    
    def enhance_batch(self, prompts: list) -> list:
        """
        批量增强提示词
        
        Args:
            prompts: 原始提示词列表
            
        Returns:
            增强结果列表
        """
        results = []
        for prompt in prompts:
            result = self.enhance(prompt)
            results.append(result)
        return results


def print_result(result: Dict[str, any], index: int = None, show_reasoning: bool = True):
    """
    打印增强结果

    Args:
        result: 增强结果字典
        index: 测试用例编号（可选）
        show_reasoning: 是否显示思考过程（默认 True）
    """
    prefix = f"测试用例 {index}" if index is not None else "增强结果"

    print(f"\n{'='*80}")
    print(f"  {prefix}")
    print(f"{'='*80}")

    if result['success']:
        # 显示思考过程
        if show_reasoning and result.get('reasoning'):
            print(f"\n💭 【模型思考过程】")
            print(f"{'─'*80}")
            # 限制思考过程的显示长度，避免过长
            reasoning = result['reasoning']
            if len(reasoning) > 500:
                print(f"{reasoning[:500]}...")
                print(f"\n（思考过程较长，已截断。完整长度: {len(reasoning)} 字符）")
            else:
                print(reasoning)
            print(f"{'─'*80}")

        # 显示原始提示词
        print(f"\n📝 【原始提示词】")
        print(f"{result['original']}")

        # 显示增强后的提示词
        print(f"\n✨ 【增强后提示词】")
        print(f"{'─'*80}")
        print(f"{result['enhanced']}")
        print(f"{'─'*80}")

        # 显示统计信息
        if result.get('stats'):
            stats = result['stats']
            print(f"\n📊 【统计信息】")
            print(f"  • 原始长度: {stats['original_length']} 字符")
            print(f"  • 增强后长度: {stats['enhanced_length']} 字符")
            print(f"  • 扩展比例: {stats['expansion_ratio']}x")
            if stats.get('reasoning_length'):
                print(f"  • 思考过程长度: {stats['reasoning_length']} 字符")
            print(f"  • 处理时间: {result['processing_time']:.2f} 秒")
        else:
            print(f"\n⏱️  处理时间: {result['processing_time']:.2f} 秒")

        print(f"\n✅ 增强成功")
    else:
        print(f"\n📝 【原始提示词】")
        print(f"{result['original']}")
        print(f"\n❌ 【增强失败】")
        print(f"错误信息: {result['error']}")
        print(f"处理时间: {result['processing_time']:.2f} 秒")


if __name__ == "__main__":
    # 如果作为脚本运行，提供简单的命令行接口
    if len(sys.argv) > 1:
        # 从命令行参数获取提示词
        prompt = " ".join(sys.argv[1:])
        enhancer = PromptEnhancer()
        result = enhancer.enhance(prompt)
        print_result(result)
    else:
        print("用法: python prompt_enhancer.py <提示词>")
        print("或者运行 python test_enhancer.py 进行完整测试")

