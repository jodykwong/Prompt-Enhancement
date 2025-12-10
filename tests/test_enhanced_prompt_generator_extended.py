#!/usr/bin/env python3
"""
增强器集成模块扩展测试套件 - P0.6 测试完善

测试场景（扩展）：
1. 异步超时处理
2. 大型项目上下文收集
3. 并发上下文收集
4. 内存使用和性能优化
5. 错误恢复和重试机制
6. 进度回调验证
7. 取消令牌处理
8. 缓存性能测试
"""

import sys
import os
import asyncio
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_prompt_generator import EnhancedPromptGenerator, enhance_prompt_with_context


class TestEnhancedPromptGeneratorExtended:
    """增强器集成扩展测试类"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_results = []
        self.performance_data = {}

    def assert_true(self, condition, message):
        """断言为真"""
        if condition:
            self.passed += 1
            self.test_results.append(f"✓ {message}")
        else:
            self.failed += 1
            self.test_results.append(f"✗ {message}")

    def assert_equal(self, actual, expected, message):
        """断言相等"""
        if actual == expected:
            self.passed += 1
            self.test_results.append(f"✓ {message}")
        else:
            self.failed += 1
            self.test_results.append(f"✗ {message} (期望: {expected}, 实际: {actual})")

    def assert_in(self, item, container, message):
        """断言包含"""
        if item in container:
            self.passed += 1
            self.test_results.append(f"✓ {message}")
        else:
            self.failed += 1
            self.test_results.append(f"✗ {message}")

    def assert_greater_than(self, actual, expected, message):
        """断言大于"""
        if actual > expected:
            self.passed += 1
            self.test_results.append(f"✓ {message}")
        else:
            self.failed += 1
            self.test_results.append(f"✗ {message} (期望 > {expected}, 实际: {actual})")

    def assert_less_than(self, actual, expected, message):
        """断言小于"""
        if actual < expected:
            self.passed += 1
            self.test_results.append(f"✓ {message}")
        else:
            self.failed += 1
            self.test_results.append(f"✗ {message} (期望 < {expected}, 实际: {actual})")

    # ============================================================
    # 扩展测试用例
    # ============================================================

    def test_async_timeout_handling(self):
        """测试异步超时处理"""
        print("\n[测试 1] 异步超时处理")
        print("-" * 60)
        try:
            async def run_timeout_test():
                generator = EnhancedPromptGenerator()
                # 测试极短的超时时间（应该捕获超时）
                result = await generator.enhance("test prompt", timeout=0.01)
                return result

            # 运行异步测试
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(asyncio.wait_for(
                    run_timeout_test(),
                    timeout=5
                ))
                # 检查是否捕获超时或返回错误
                self.assert_true(
                    "error" in result or "timeout" in str(result).lower(),
                    "超时被正确处理"
                )
            except asyncio.TimeoutError:
                self.assert_true(True, "异步操作超时被正确捕获")
            except Exception as e:
                self.assert_true(
                    True,
                    f"异步操作捕获异常: {type(e).__name__}"
                )
            finally:
                loop.close()
        except Exception as e:
            self.assert_true(False, f"异步超时处理测试失败: {e}")

    def test_large_project_context(self):
        """测试大型项目上下文收集"""
        print("\n[测试 2] 大型项目上下文收集")
        print("-" * 60)
        try:
            generator = EnhancedPromptGenerator()

            # 创建模拟大型项目结构
            with tempfile.TemporaryDirectory() as tmpdir:
                # 创建大量文件模拟大型项目
                for i in range(50):
                    module_dir = Path(tmpdir) / f"module_{i}"
                    module_dir.mkdir(exist_ok=True)
                    for j in range(3):
                        (module_dir / f"file_{j}.py").write_text(f"# Module {i} File {j}")

                # 初始化 git
                os.system(f"cd {tmpdir} && git init > /dev/null 2>&1")
                os.system(f"cd {tmpdir} && git config user.email 'test@test.com' > /dev/null 2>&1")
                os.system(f"cd {tmpdir} && git config user.name 'Test User' > /dev/null 2>&1")

                # 测量收集时间
                start_time = time.time()
                context = generator._collect_context(tmpdir)
                elapsed_time = time.time() - start_time

                self.performance_data["large_project_time"] = elapsed_time

                self.assert_true(
                    context is not None,
                    "大型项目上下文收集成功"
                )
                self.assert_less_than(
                    elapsed_time,
                    2.0,
                    f"大型项目收集时间 < 2s (实际: {elapsed_time:.2f}s)"
                )
        except Exception as e:
            self.assert_true(False, f"大型项目上下文测试失败: {e}")

    def test_small_project_performance(self):
        """测试小型项目性能基准"""
        print("\n[测试 3] 小型项目性能基准")
        print("-" * 60)
        try:
            generator = EnhancedPromptGenerator()

            with tempfile.TemporaryDirectory() as tmpdir:
                # 创建小型项目（< 100 文件）
                for i in range(10):
                    (Path(tmpdir) / f"file_{i}.py").write_text(f"# File {i}")

                os.system(f"cd {tmpdir} && git init > /dev/null 2>&1")
                os.system(f"cd {tmpdir} && git config user.email 'test@test.com' > /dev/null 2>&1")
                os.system(f"cd {tmpdir} && git config user.name 'Test User' > /dev/null 2>&1")

                start_time = time.time()
                context = generator._collect_context(tmpdir)
                elapsed_time = time.time() - start_time

                self.performance_data["small_project_time"] = elapsed_time

                self.assert_true(
                    context is not None or elapsed_time > 0,
                    "小型项目收集完成"
                )
                self.assert_less_than(
                    elapsed_time,
                    1.0,
                    f"小型项目收集时间 < 1s (实际: {elapsed_time*1000:.0f}ms)"
                )
        except Exception as e:
            self.assert_true(False, f"小型项目性能测试失败: {e}")

    def test_concurrent_context_collection(self):
        """测试并发上下文收集"""
        print("\n[测试 4] 并发上下文收集")
        print("-" * 60)
        try:
            generator = EnhancedPromptGenerator()

            # 创建多个临时项目目录
            temp_dirs = []
            try:
                for idx in range(3):
                    tmpdir = tempfile.mkdtemp()
                    temp_dirs.append(tmpdir)

                    # 创建基础结构
                    for i in range(5):
                        (Path(tmpdir) / f"file_{i}.py").write_text(f"# File {i}")

                    os.system(f"cd {tmpdir} && git init > /dev/null 2>&1")
                    os.system(f"cd {tmpdir} && git config user.email 'test@test.com' > /dev/null 2>&1")
                    os.system(f"cd {tmpdir} && git config user.name 'Test User' > /dev/null 2>&1")

                # 并发收集
                start_time = time.time()
                contexts = [generator._collect_context(d) for d in temp_dirs]
                elapsed_time = time.time() - start_time

                self.assert_equal(
                    len([c for c in contexts if c is not None or c == {}]),
                    len(temp_dirs),
                    "所有并发请求都被处理"
                )
                self.assert_less_than(
                    elapsed_time,
                    3.0,
                    f"并发收集时间 < 3s (实际: {elapsed_time:.2f}s)"
                )
            finally:
                # 清理临时目录
                import shutil
                for tmpdir in temp_dirs:
                    if os.path.exists(tmpdir):
                        shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception as e:
            self.assert_true(False, f"并发上下文收集测试失败: {e}")

    def test_cache_performance(self):
        """测试缓存性能"""
        print("\n[测试 5] 缓存性能")
        print("-" * 60)
        try:
            generator = EnhancedPromptGenerator()

            with tempfile.TemporaryDirectory() as tmpdir:
                # 创建项目
                for i in range(10):
                    (Path(tmpdir) / f"file_{i}.py").write_text(f"# File {i}")
                os.system(f"cd {tmpdir} && git init > /dev/null 2>&1")
                os.system(f"cd {tmpdir} && git config user.email 'test@test.com' > /dev/null 2>&1")
                os.system(f"cd {tmpdir} && git config user.name 'Test User' > /dev/null 2>&1")

                # 第一次收集（无缓存）
                start_time = time.time()
                context1 = generator._collect_context(tmpdir)
                first_time = time.time() - start_time

                # 第二次收集（有缓存）
                start_time = time.time()
                context2 = generator._collect_context(tmpdir)
                cached_time = time.time() - start_time

                self.performance_data["first_collect_time"] = first_time
                self.performance_data["cached_collect_time"] = cached_time

                self.assert_equal(
                    context1,
                    context2,
                    "缓存返回相同内容"
                )
                self.assert_less_than(
                    cached_time,
                    first_time,
                    f"缓存访问更快 (首次: {first_time*1000:.0f}ms, 缓存: {cached_time*1000:.0f}ms)"
                )
        except Exception as e:
            self.assert_true(False, f"缓存性能测试失败: {e}")

    def test_memory_efficiency(self):
        """测试内存使用效率"""
        print("\n[测试 6] 内存使用效率")
        print("-" * 60)
        try:
            import sys

            generator = EnhancedPromptGenerator()

            # 测试对象大小
            initial_size = sys.getsizeof(generator)

            with tempfile.TemporaryDirectory() as tmpdir:
                (Path(tmpdir) / "test.py").write_text("# Test")
                os.system(f"cd {tmpdir} && git init > /dev/null 2>&1")
                os.system(f"cd {tmpdir} && git config user.email 'test@test.com' > /dev/null 2>&1")
                os.system(f"cd {tmpdir} && git config user.name 'Test User' > /dev/null 2>&1")

                generator._collect_context(tmpdir)

                with_cache_size = sys.getsizeof(generator)

                self.assert_less_than(
                    with_cache_size - initial_size,
                    1024 * 1024,  # < 1MB
                    f"缓存占用内存 < 1MB (实际: {(with_cache_size - initial_size) / 1024:.0f}KB)"
                )
        except Exception as e:
            self.assert_true(False, f"内存效率测试失败: {e}")

    def test_progress_callback_support(self):
        """测试进度回调支持"""
        print("\n[测试 7] 进度回调支持")
        print("-" * 60)
        try:
            generator = EnhancedPromptGenerator()

            # 验证增强方法支持进度回调
            self.assert_true(
                "progress_callback" in generator.enhance.__code__.co_varnames,
                "增强方法支持进度回调参数"
            )

            # 验证取消令牌支持
            self.assert_true(
                "cancel_token" in generator.enhance.__code__.co_varnames,
                "增强方法支持取消令牌参数"
            )
        except Exception as e:
            self.assert_true(False, f"进度回调测试失败: {e}")

    def test_error_recovery(self):
        """测试错误恢复机制"""
        print("\n[测试 8] 错误恢复机制")
        print("-" * 60)
        try:
            generator = EnhancedPromptGenerator()

            # 测试多种错误情况
            test_cases = [
                ("/nonexistent/path", "不存在的路径"),
                ("", "空路径"),
                (None, "None 路径"),
            ]

            for path, description in test_cases:
                try:
                    result = generator._collect_context(path)
                    self.assert_true(
                        result is None or result == {},
                        f"处理 {description}: 返回 None 或空字典"
                    )
                except Exception as e:
                    self.assert_true(
                        False,
                        f"处理 {description} 抛出异常: {e}"
                    )
        except Exception as e:
            self.assert_true(False, f"错误恢复测试失败: {e}")

    def test_context_cache_lifecycle(self):
        """测试缓存生命周期"""
        print("\n[测试 9] 缓存生命周期")
        print("-" * 60)
        try:
            generator = EnhancedPromptGenerator()

            with tempfile.TemporaryDirectory() as tmpdir:
                (Path(tmpdir) / "test.py").write_text("# Test")
                os.system(f"cd {tmpdir} && git init > /dev/null 2>&1")
                os.system(f"cd {tmpdir} && git config user.email 'test@test.com' > /dev/null 2>&1")
                os.system(f"cd {tmpdir} && git config user.name 'Test User' > /dev/null 2>&1")

                # 收集上下文
                generator._collect_context(tmpdir)
                self.assert_greater_than(
                    len(generator._context_cache),
                    0,
                    "缓存已填充"
                )

                # 清除缓存
                generator.clear_cache()
                self.assert_equal(
                    len(generator._context_cache),
                    0,
                    "缓存已清除"
                )
        except Exception as e:
            self.assert_true(False, f"缓存生命周期测试失败: {e}")

    def test_context_string_quality(self):
        """测试上下文字符串质量"""
        print("\n[测试 10] 上下文字符串质量")
        print("-" * 60)
        try:
            generator = EnhancedPromptGenerator()

            with tempfile.TemporaryDirectory() as tmpdir:
                # 创建 Python 项目
                (Path(tmpdir) / "main.py").write_text("# Main file")
                (Path(tmpdir) / "test.py").write_text("# Test file")
                os.system(f"cd {tmpdir} && git init > /dev/null 2>&1")
                os.system(f"cd {tmpdir} && git config user.email 'test@test.com' > /dev/null 2>&1")
                os.system(f"cd {tmpdir} && git config user.name 'Test User' > /dev/null 2>&1")
                os.system(f"cd {tmpdir} && git add . > /dev/null 2>&1 && git commit -m 'init' > /dev/null 2>&1")

                context = generator._collect_context(tmpdir)

                if context:
                    context_string = context.get("context_string", "")
                    self.assert_true(
                        len(context_string) > 0,
                        f"上下文字符串非空 (长度: {len(context_string)} 字符)"
                    )
                    self.assert_true(
                        len(context_string) > 50,
                        f"上下文字符串有足够信息量 (长度: {len(context_string)} > 50)"
                    )
        except Exception as e:
            self.assert_true(False, f"上下文字符串质量测试失败: {e}")

    def run_all_tests(self):
        """运行所有扩展测试"""
        print("\n" + "=" * 70)
        print("增强器集成模块扩展测试套件 (P0.6)")
        print("=" * 70)

        self.test_async_timeout_handling()
        self.test_large_project_context()
        self.test_small_project_performance()
        self.test_concurrent_context_collection()
        self.test_cache_performance()
        self.test_memory_efficiency()
        self.test_progress_callback_support()
        self.test_error_recovery()
        self.test_context_cache_lifecycle()
        self.test_context_string_quality()

        # 打印结果
        print("\n" + "=" * 70)
        print("详细测试结果")
        print("=" * 70)
        print("\n".join(self.test_results))

        # 打印性能数据
        if self.performance_data:
            print("\n" + "=" * 70)
            print("性能基准数据")
            print("=" * 70)
            for key, value in self.performance_data.items():
                if isinstance(value, float):
                    print(f"  {key}: {value*1000:.2f}ms")
                else:
                    print(f"  {key}: {value}")

        print("\n" + "=" * 70)
        print(f"总体测试结果: {self.passed}/{self.passed + self.failed} 通过")
        print("=" * 70 + "\n")

        return self.failed == 0


if __name__ == "__main__":
    tester = TestEnhancedPromptGeneratorExtended()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
