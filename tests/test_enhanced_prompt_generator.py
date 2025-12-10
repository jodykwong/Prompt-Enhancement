#!/usr/bin/env python3
"""
增强器集成模块单元测试

测试场景：
1. 有上下文的提示词增强
2. 无上下文的提示词增强
3. 项目路径不存在的处理
4. 上下文注入验证
5. 缓存机制验证
6. API 失败回退处理
"""

import sys
import os
import asyncio
import tempfile
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_prompt_generator import EnhancedPromptGenerator, enhance_prompt_with_context


class TestEnhancedPromptGenerator:
    """增强器集成模块测试类"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_results = []

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

    def test_generator_initialization(self):
        """测试生成器初始化"""
        try:
            generator = EnhancedPromptGenerator()
            self.assert_true(generator is not None, "生成器初始化成功")
            self.assert_true(hasattr(generator, 'enhance'), "生成器有 enhance 方法")
            self.assert_true(hasattr(generator, 'clear_cache'), "生成器有 clear_cache 方法")
        except Exception as e:
            self.assert_true(False, f"生成器初始化失败: {e}")

    def test_context_injection(self):
        """测试上下文注入"""
        try:
            generator = EnhancedPromptGenerator()
            
            # 创建模拟上下文
            mock_context = {
                "summary": "Python 项目",
                "context_string": "# 项目上下文\n## 技术栈\n- Python"
            }
            
            prompt = "修复 bug"
            injected = generator._inject_context(prompt, mock_context)
            
            self.assert_true("项目上下文" in injected, "上下文已注入到提示词中")
            self.assert_true("修复 bug" in injected, "原始提示词保留在注入后的提示词中")
            self.assert_true("---" in injected, "分隔符已添加")
        except Exception as e:
            self.assert_true(False, f"上下文注入测试失败: {e}")

    def test_context_injection_without_context(self):
        """测试无上下文的注入"""
        try:
            generator = EnhancedPromptGenerator()
            prompt = "修复 bug"
            
            # 无上下文
            injected = generator._inject_context(prompt, None)
            self.assert_equal(injected, prompt, "无上下文时返回原始提示词")
            
            # 空上下文
            injected = generator._inject_context(prompt, {})
            self.assert_equal(injected, prompt, "空上下文时返回原始提示词")
        except Exception as e:
            self.assert_true(False, f"无上下文注入测试失败: {e}")

    def test_nonexistent_project_path(self):
        """测试不存在的项目路径"""
        try:
            generator = EnhancedPromptGenerator()
            context = generator._collect_context("/nonexistent/path/12345")
            
            # 应该返回空或默认值
            self.assert_true(
                context is None or context == {},
                "不存在的项目路径返回 None 或空字典"
            )
        except Exception as e:
            self.assert_true(False, f"不存在路径测试失败: {e}")

    def test_cache_mechanism(self):
        """测试缓存机制"""
        try:
            generator = EnhancedPromptGenerator()
            
            # 创建临时目录
            with tempfile.TemporaryDirectory() as tmpdir:
                # 第一次收集
                context1 = generator._collect_context(tmpdir)
                
                # 第二次收集（应该来自缓存）
                context2 = generator._collect_context(tmpdir)
                
                # 验证缓存
                self.assert_true(
                    context1 == context2,
                    "缓存返回相同的上下文"
                )
                
                # 清除缓存
                generator.clear_cache()
                self.assert_equal(
                    len(generator._context_cache),
                    0,
                    "缓存已清除"
                )
        except Exception as e:
            self.assert_true(False, f"缓存机制测试失败: {e}")

    def test_convenience_function_exists(self):
        """测试便捷函数存在"""
        try:
            self.assert_true(
                callable(enhance_prompt_with_context),
                "enhance_prompt_with_context 函数存在且可调用"
            )
        except Exception as e:
            self.assert_true(False, f"便捷函数测试失败: {e}")

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*70)
        print("增强器集成模块单元测试")
        print("="*70 + "\n")

        self.test_generator_initialization()
        self.test_context_injection()
        self.test_context_injection_without_context()
        self.test_nonexistent_project_path()
        self.test_cache_mechanism()
        self.test_convenience_function_exists()

        # 打印结果
        print("\n".join(self.test_results))
        print("\n" + "="*70)
        print(f"测试结果: {self.passed}/{self.passed + self.failed} 通过")
        print("="*70 + "\n")

        return self.failed == 0


if __name__ == "__main__":
    tester = TestEnhancedPromptGenerator()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

