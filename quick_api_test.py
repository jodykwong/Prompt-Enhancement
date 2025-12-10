#!/usr/bin/env python3
"""
快速 API 验证测试脚本

验证以下功能：
1. 基础异步调用 - 验证 enhance() 方法可用
2. 进度回调功能 - 验证 3 个回调点
3. 取消机制 - 验证 asyncio.Event 取消令牌

执行方式：
    source venv/bin/activate
    python3 quick_api_test.py
"""

import asyncio
import sys
import os
from async_prompt_enhancer import AsyncPromptEnhancer


class TestResults:
    """测试结果统计"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name, message=""):
        self.passed += 1
        msg = f"✅ {test_name}"
        if message:
            msg += f" - {message}"
        print(msg)
    
    def add_fail(self, test_name, error):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"❌ {test_name}: {error}")
    
    def print_summary(self):
        print(f"\n{'='*80}")
        print(f"测试结果: {self.passed} 通过, {self.failed} 失败")
        print(f"{'='*80}")
        if self.errors:
            print("\n失败详情:")
            for test_name, error in self.errors:
                print(f"  ❌ {test_name}")
                print(f"     错误: {error}")
        return self.failed == 0


async def test_basic_async_call(results: TestResults):
    """
    测试 1: 基础异步调用
    
    验证：
    - enhance() 方法可用
    - 返回正确的数据结构
    - success 标志正确
    - 处理时间记录正确
    """
    try:
        print("\n【测试 1】基础异步调用")
        print("-" * 80)
        
        enhancer = AsyncPromptEnhancer()
        
        # 调用 enhance() 方法
        result = await enhancer.enhance("修复登录页面的 bug")
        
        # 验证返回值结构
        required_keys = ["original", "enhanced", "reasoning", "processing_time", 
                        "success", "error", "stats", "cancelled"]
        for key in required_keys:
            assert key in result, f"返回值缺少必要字段: {key}"
        
        # 验证成功标志
        assert result["success"] is True, f"success 标志应为 True，实际: {result['success']}"
        
        # 验证原始提示词
        assert result["original"] == "修复登录页面的 bug", "原始提示词不匹配"
        
        # 验证增强后的提示词不为空
        assert result["enhanced"] is not None and len(result["enhanced"]) > 0, \
            "增强后的提示词为空"
        
        # 验证处理时间
        assert result["processing_time"] > 0, "处理时间应大于 0"
        
        # 验证统计信息
        assert result["stats"] is not None, "统计信息为空"
        assert "original_length" in result["stats"], "统计信息缺少 original_length"
        assert "enhanced_length" in result["stats"], "统计信息缺少 enhanced_length"
        assert "expansion_ratio" in result["stats"], "统计信息缺少 expansion_ratio"
        
        # 验证取消标志
        assert result["cancelled"] is False, "取消标志应为 False"
        
        results.add_pass(
            "基础异步调用",
            f"处理时间: {result['processing_time']:.2f}s, "
            f"扩展比例: {result['stats']['expansion_ratio']}x"
        )
        
        print(f"\n  原始提示词: {result['original']}")
        print(f"  增强后提示词: {result['enhanced'][:100]}...")
        print(f"  处理时间: {result['processing_time']:.2f} 秒")
        print(f"  扩展比例: {result['stats']['expansion_ratio']}x")
        
        return True
    
    except Exception as e:
        results.add_fail("基础异步调用", str(e))
        return False


async def test_progress_callback(results: TestResults):
    """
    测试 2: 进度回调功能
    
    验证：
    - 进度回调函数被正确调用
    - 3 个回调点都被触发
    - 进度值正确（0.1, 0.5, 1.0）
    - 回调消息正确
    """
    try:
        print("\n【测试 2】进度回调功能")
        print("-" * 80)
        
        enhancer = AsyncPromptEnhancer()
        progress_log = []
        
        async def progress_callback(message: str, progress: float):
            """记录进度回调"""
            progress_log.append((message, progress))
            print(f"  进度回调: {message} ({progress*100:.0f}%)")
        
        # 调用 enhance() 方法，带进度回调
        result = await enhancer.enhance(
            "优化数据库查询性能",
            progress_callback=progress_callback
        )
        
        # 验证成功
        assert result["success"] is True, f"API 调用失败: {result['error']}"
        
        # 验证回调次数
        assert len(progress_log) == 3, \
            f"进度回调次数不正确，期望 3 次，实际 {len(progress_log)} 次"
        
        # 验证第 1 个回调点
        assert progress_log[0][0] == "正在调用 API...", \
            f"第 1 个回调消息不正确: {progress_log[0][0]}"
        assert progress_log[0][1] == 0.1, \
            f"第 1 个回调进度不正确: {progress_log[0][1]}"
        
        # 验证第 2 个回调点
        assert progress_log[1][0] == "正在接收响应...", \
            f"第 2 个回调消息不正确: {progress_log[1][0]}"
        assert progress_log[1][1] == 0.5, \
            f"第 2 个回调进度不正确: {progress_log[1][1]}"
        
        # 验证第 3 个回调点
        assert progress_log[2][0] == "处理完成", \
            f"第 3 个回调消息不正确: {progress_log[2][0]}"
        assert progress_log[2][1] == 1.0, \
            f"第 3 个回调进度不正确: {progress_log[2][1]}"
        
        results.add_pass(
            "进度回调功能",
            f"回调次数: {len(progress_log)}, 进度值: {[p[1] for p in progress_log]}"
        )
        
        return True
    
    except Exception as e:
        results.add_fail("进度回调功能", str(e))
        return False


async def test_cancellation_mechanism(results: TestResults):
    """
    测试 3: 取消机制
    
    验证：
    - 取消令牌能正确中断操作
    - 返回值包含 cancelled: True
    - 错误信息正确
    - 处理时间记录正确
    """
    try:
        print("\n【测试 3】取消机制")
        print("-" * 80)
        
        enhancer = AsyncPromptEnhancer()
        cancel_token = asyncio.Event()
        
        # 立即设置取消令牌
        cancel_token.set()
        
        # 调用 enhance() 方法，带取消令牌
        result = await enhancer.enhance(
            "测试取消机制",
            cancel_token=cancel_token
        )
        
        # 验证成功标志为 False
        assert result["success"] is False, \
            f"success 标志应为 False，实际: {result['success']}"
        
        # 验证取消标志为 True
        assert result["cancelled"] is True, \
            f"cancelled 标志应为 True，实际: {result['cancelled']}"
        
        # 验证错误信息
        assert result["error"] == "用户取消操作", \
            f"错误信息不正确: {result['error']}"
        
        # 验证增强后的提示词为 None
        assert result["enhanced"] is None, \
            f"增强后的提示词应为 None，实际: {result['enhanced']}"
        
        # 验证处理时间记录
        assert result["processing_time"] >= 0, \
            f"处理时间应 >= 0，实际: {result['processing_time']}"
        
        results.add_pass(
            "取消机制",
            f"取消标志: {result['cancelled']}, 错误信息: {result['error']}"
        )
        
        return True
    
    except Exception as e:
        results.add_fail("取消机制", str(e))
        return False


async def run_all_tests():
    """运行所有测试"""
    results = TestResults()
    
    print("="*80)
    print("快速 API 验证测试")
    print("="*80)
    
    # 检查 API 密钥
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("\n❌ 错误: DEEPSEEK_API_KEY 环境变量未设置")
        print("请在 .env 文件中设置 DEEPSEEK_API_KEY，或通过以下命令设置:")
        print("  export DEEPSEEK_API_KEY='your-api-key'")
        return False
    
    print("\n✅ DEEPSEEK_API_KEY 已设置")
    
    # 运行测试
    await test_basic_async_call(results)
    await test_progress_callback(results)
    await test_cancellation_mechanism(results)
    
    # 打印总结
    success = results.print_summary()
    
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试执行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

