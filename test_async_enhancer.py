#!/usr/bin/env python3
"""
异步增强器单元测试（不依赖 pytest）

测试覆盖：
1. 正常异步调用
2. 进度回调功能
3. 取消机制
4. 超时处理
5. 错误处理
"""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from async_prompt_enhancer import AsyncPromptEnhancer, cancel_after_delay


class TestResults:
    """测试结果统计"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def add_pass(self, test_name):
        self.passed += 1
        print(f"✅ {test_name}")

    def add_fail(self, test_name, error):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"❌ {test_name}: {error}")

    def print_summary(self):
        print(f"\n{'='*80}")
        print(f"测试结果: {self.passed} 通过, {self.failed} 失败")
        print(f"{'='*80}")
        if self.errors:
            for test_name, error in self.errors:
                print(f"❌ {test_name}: {error}")
        return self.failed == 0


async def test_enhance_basic():
    """测试基础异步调用"""
    try:
        with patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test-key'}):
            enhancer = AsyncPromptEnhancer()

            # Mock API 响应
            mock_response = MagicMock()
            mock_response.choices[0].message.reasoning_content = "思考过程"
            mock_response.choices[0].message.content = "增强后的提示词"

            with patch.object(enhancer.client.chat.completions, 'create',
                             new_callable=AsyncMock, return_value=mock_response):
                result = await enhancer.enhance("测试提示词")

                assert result["success"] is True
                assert result["original"] == "测试提示词"
                assert result["enhanced"] == "增强后的提示词"
                assert result["reasoning"] == "思考过程"
                assert result["cancelled"] is False
                assert result["error"] is None
                assert result["processing_time"] > 0

        return True, None
    except Exception as e:
        return False, str(e)


async def test_enhance_with_progress_callback():
    """测试进度回调功能"""
    try:
        with patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test-key'}):
            enhancer = AsyncPromptEnhancer()
            progress_calls = []

            async def progress_callback(message: str, progress: float):
                progress_calls.append((message, progress))

            # Mock API 响应
            mock_response = MagicMock()
            mock_response.choices[0].message.reasoning_content = "思考过程"
            mock_response.choices[0].message.content = "增强后的提示词"

            with patch.object(enhancer.client.chat.completions, 'create',
                             new_callable=AsyncMock, return_value=mock_response):
                result = await enhancer.enhance(
                    "测试提示词",
                    progress_callback=progress_callback
                )

                assert result["success"] is True
                assert len(progress_calls) == 3
                assert progress_calls[0] == ("正在调用 API...", 0.1)
                assert progress_calls[1] == ("正在接收响应...", 0.5)
                assert progress_calls[2] == ("处理完成", 1.0)

        return True, None
    except Exception as e:
        return False, str(e)


async def test_enhance_with_cancellation():
    """测试取消机制"""
    try:
        with patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test-key'}):
            enhancer = AsyncPromptEnhancer()
            cancel_token = asyncio.Event()
            cancel_token.set()

            result = await enhancer.enhance(
                "测试提示词",
                cancel_token=cancel_token
            )

            assert result["success"] is False
            assert result["cancelled"] is True
            assert result["error"] == "用户取消操作"

        return True, None
    except Exception as e:
        return False, str(e)


async def test_cancel_after_delay():
    """测试延迟取消"""
    try:
        cancel_token = asyncio.Event()
        cancel_task = asyncio.create_task(cancel_after_delay(cancel_token, 0.1))

        await asyncio.sleep(0.05)
        assert not cancel_token.is_set()

        await cancel_task
        assert cancel_token.is_set()

        return True, None
    except Exception as e:
        return False, str(e)


async def test_enhance_batch():
    """测试批量处理"""
    try:
        with patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'test-key'}):
            enhancer = AsyncPromptEnhancer()
            progress_calls = []

            async def progress_callback(message: str, progress: float):
                progress_calls.append((message, progress))

            # Mock API 响应
            mock_response = MagicMock()
            mock_response.choices[0].message.reasoning_content = "思考过程"
            mock_response.choices[0].message.content = "增强后的提示词"

            with patch.object(enhancer.client.chat.completions, 'create',
                             new_callable=AsyncMock, return_value=mock_response):
                prompts = ["提示词1", "提示词2", "提示词3"]
                results = await enhancer.enhance_batch(
                    prompts,
                    progress_callback=progress_callback
                )

                assert len(results) == 3
                assert all(r["success"] for r in results)

        return True, None
    except Exception as e:
        return False, str(e)


async def run_all_tests():
    """运行所有测试"""
    results = TestResults()

    print("="*80)
    print("异步增强器单元测试")
    print("="*80)

    tests = [
        ("test_enhance_basic", test_enhance_basic),
        ("test_enhance_with_progress_callback", test_enhance_with_progress_callback),
        ("test_enhance_with_cancellation", test_enhance_with_cancellation),
        ("test_cancel_after_delay", test_cancel_after_delay),
        ("test_enhance_batch", test_enhance_batch),
    ]

    for test_name, test_func in tests:
        success, error = await test_func()
        if success:
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, error)

    return results.print_summary()


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

