#!/usr/bin/env python3
"""
P0.5 集成测试

验证增强器集成模块与 P0.1-P0.4 的完全兼容性
"""

import sys
import os
import tempfile
import subprocess
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_prompt_generator import EnhancedPromptGenerator, enhance_prompt_with_context
from context_collector import collect_project_context
from tech_stack_detector import detect_tech_stack
from project_structure_analyzer import analyze_project_structure
from git_history_analyzer import analyze_git_history


class TestP0_5Integration:
    """P0.5 集成测试类"""

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
            self.test_results.append(f"✗ {message}")

    def assert_in(self, item, container, message):
        """断言包含"""
        if item in container:
            self.passed += 1
            self.test_results.append(f"✓ {message}")
        else:
            self.failed += 1
            self.test_results.append(f"✗ {message}")

    def test_module_imports(self):
        """测试模块导入"""
        try:
            # 验证所有模块都可以导入
            self.assert_true(EnhancedPromptGenerator is not None, "EnhancedPromptGenerator 导入成功")
            self.assert_true(enhance_prompt_with_context is not None, "enhance_prompt_with_context 导入成功")
            self.assert_true(collect_project_context is not None, "collect_project_context 导入成功")
            self.assert_true(detect_tech_stack is not None, "detect_tech_stack 导入成功")
            self.assert_true(analyze_project_structure is not None, "analyze_project_structure 导入成功")
            self.assert_true(analyze_git_history is not None, "analyze_git_history 导入成功")
        except Exception as e:
            self.assert_true(False, f"模块导入失败: {e}")

    def test_api_compatibility(self):
        """测试 API 兼容性"""
        try:
            generator = EnhancedPromptGenerator()
            
            # 验证 enhance 方法签名
            self.assert_true(
                hasattr(generator, 'enhance'),
                "EnhancedPromptGenerator 有 enhance 方法"
            )
            
            # 验证 _collect_context 方法
            self.assert_true(
                hasattr(generator, '_collect_context'),
                "EnhancedPromptGenerator 有 _collect_context 方法"
            )
            
            # 验证 _inject_context 方法
            self.assert_true(
                hasattr(generator, '_inject_context'),
                "EnhancedPromptGenerator 有 _inject_context 方法"
            )
        except Exception as e:
            self.assert_true(False, f"API 兼容性测试失败: {e}")

    def test_context_collector_integration(self):
        """测试与 context_collector 的集成"""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # 创建简单的项目结构
                Path(tmpdir, "test.py").touch()
                
                # 初始化 Git 仓库
                subprocess.run(
                    ["git", "init"],
                    cwd=tmpdir,
                    capture_output=True,
                    timeout=5
                )
                
                # 收集上下文
                context = collect_project_context(tmpdir)
                
                self.assert_true(
                    "tech_stack" in context,
                    "上下文包含 tech_stack"
                )
                self.assert_true(
                    "project_structure" in context,
                    "上下文包含 project_structure"
                )
                self.assert_true(
                    "git_history" in context,
                    "上下文包含 git_history"
                )
                self.assert_true(
                    "summary" in context,
                    "上下文包含 summary"
                )
                self.assert_true(
                    "context_string" in context,
                    "上下文包含 context_string"
                )
        except Exception as e:
            self.assert_true(False, f"context_collector 集成测试失败: {e}")

    def test_generator_with_context(self):
        """测试生成器与上下文的集成"""
        try:
            generator = EnhancedPromptGenerator()
            
            with tempfile.TemporaryDirectory() as tmpdir:
                # 创建简单的项目结构
                Path(tmpdir, "test.py").touch()
                
                # 初始化 Git 仓库
                subprocess.run(
                    ["git", "init"],
                    cwd=tmpdir,
                    capture_output=True,
                    timeout=5
                )
                
                # 收集上下文
                context = generator._collect_context(tmpdir)
                
                # 注入上下文
                prompt = "修复 bug"
                injected = generator._inject_context(prompt, context)
                
                self.assert_true(
                    len(injected) > len(prompt),
                    "注入上下文后提示词长度增加"
                )
                self.assert_true(
                    "项目上下文" in injected or "技术栈" in injected,
                    "注入的提示词包含上下文信息"
                )
        except Exception as e:
            self.assert_true(False, f"生成器与上下文集成测试失败: {e}")

    def test_error_handling_nonexistent_path(self):
        """测试错误处理：不存在的路径"""
        try:
            generator = EnhancedPromptGenerator()
            context = generator._collect_context("/nonexistent/path/xyz")
            
            self.assert_true(
                context is None or context == {},
                "不存在的路径返回 None 或空字典"
            )
        except Exception as e:
            self.assert_true(False, f"错误处理测试失败: {e}")

    def test_cache_across_instances(self):
        """测试缓存在实例间的行为"""
        try:
            generator1 = EnhancedPromptGenerator()
            generator2 = EnhancedPromptGenerator()
            
            # 每个实例有独立的缓存
            self.assert_equal(
                len(generator1._context_cache),
                0,
                "新实例的缓存为空"
            )
            self.assert_equal(
                len(generator2._context_cache),
                0,
                "另一个新实例的缓存也为空"
            )
        except Exception as e:
            self.assert_true(False, f"缓存实例测试失败: {e}")

    def test_convenience_function_signature(self):
        """测试便捷函数签名"""
        try:
            import inspect
            
            sig = inspect.signature(enhance_prompt_with_context)
            params = list(sig.parameters.keys())
            
            self.assert_in("prompt", params, "enhance_prompt_with_context 有 prompt 参数")
            self.assert_in("project_path", params, "enhance_prompt_with_context 有 project_path 参数")
            self.assert_in("timeout", params, "enhance_prompt_with_context 有 timeout 参数")
        except Exception as e:
            self.assert_true(False, f"便捷函数签名测试失败: {e}")

    def test_p0_1_p0_4_compatibility(self):
        """测试与 P0.1-P0.4 的兼容性"""
        try:
            # 验证所有 P0.1-P0.4 的模块都可以正常导入和使用
            with tempfile.TemporaryDirectory() as tmpdir:
                Path(tmpdir, "test.py").touch()
                
                # P0.1: 技术栈检测
                tech_stack = detect_tech_stack(tmpdir)
                self.assert_true(
                    isinstance(tech_stack, dict),
                    "P0.1 技术栈检测返回字典"
                )
                
                # P0.2: 项目结构分析
                structure = analyze_project_structure(tmpdir)
                self.assert_true(
                    isinstance(structure, dict),
                    "P0.2 项目结构分析返回字典"
                )
                
                # P0.3: Git 历史分析
                subprocess.run(
                    ["git", "init"],
                    cwd=tmpdir,
                    capture_output=True,
                    timeout=5
                )
                git_history = analyze_git_history(tmpdir)
                self.assert_true(
                    isinstance(git_history, dict),
                    "P0.3 Git 历史分析返回字典"
                )
                
                # P0.4: 上下文收集
                context = collect_project_context(tmpdir)
                self.assert_true(
                    isinstance(context, dict),
                    "P0.4 上下文收集返回字典"
                )
        except Exception as e:
            self.assert_true(False, f"P0.1-P0.4 兼容性测试失败: {e}")

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*70)
        print("P0.5 集成测试")
        print("="*70 + "\n")

        self.test_module_imports()
        self.test_api_compatibility()
        self.test_context_collector_integration()
        self.test_generator_with_context()
        self.test_error_handling_nonexistent_path()
        self.test_cache_across_instances()
        self.test_convenience_function_signature()
        self.test_p0_1_p0_4_compatibility()

        # 打印结果
        print("\n".join(self.test_results))
        print("\n" + "="*70)
        print(f"测试结果: {self.passed}/{self.passed + self.failed} 通过")
        print("="*70 + "\n")

        return self.failed == 0


if __name__ == "__main__":
    tester = TestP0_5Integration()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

