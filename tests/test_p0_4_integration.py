#!/usr/bin/env python3
"""
P0.4 集成测试

测试上下文收集器与 P0.1、P0.2、P0.3 的集成：
1. 导入所有模块
2. 验证 API 兼容性
3. 测试完整的上下文收集流程
4. 测试不同类型的项目
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from context_collector import collect_project_context, ContextCollector
from tech_stack_detector import detect_tech_stack
from project_structure_analyzer import analyze_project_structure
from git_history_analyzer import analyze_git_history


class TestP0_4Integration:
    """P0.4 集成测试类"""

    def __init__(self):
        self.passed = 0
        self.failed = 0

    def assert_true(self, condition, message=""):
        """断言为真"""
        if not condition:
            print(f"  ✗ {message}")
            self.failed += 1
        else:
            self.passed += 1

    def assert_equal(self, actual, expected, message=""):
        """断言相等"""
        if actual != expected:
            print(f"  ✗ {message}")
            self.failed += 1
        else:
            self.passed += 1

    def assert_in(self, item, container, message=""):
        """断言包含"""
        if item not in container:
            print(f"  ✗ {message}")
            self.failed += 1
        else:
            self.passed += 1

    def test_module_imports(self):
        """测试模块导入"""
        print("\n测试 1: 模块导入")
        try:
            from context_collector import collect_project_context, ContextCollector
            from tech_stack_detector import detect_tech_stack
            from project_structure_analyzer import analyze_project_structure
            from git_history_analyzer import analyze_git_history
            self.assert_true(True, "所有模块导入成功")
        except ImportError as e:
            self.assert_true(False, f"模块导入失败: {e}")

    def test_api_compatibility(self):
        """测试 API 兼容性"""
        print("\n测试 2: API 兼容性")
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.py").write_text("print('hello')")
            Path(tmpdir, "requirements.txt").write_text("django==4.0")

            # 测试各个模块的 API
            tech_stack = detect_tech_stack(tmpdir)
            self.assert_true(isinstance(tech_stack, dict), "tech_stack 应该返回字典")
            self.assert_in("frontend", tech_stack, "tech_stack 应该包含 frontend")
            self.assert_in("backend", tech_stack, "tech_stack 应该包含 backend")

            structure = analyze_project_structure(tmpdir)
            self.assert_true(isinstance(structure, dict), "structure 应该返回字典")
            self.assert_in("key_directories", structure, "structure 应该包含 key_directories")

            history = analyze_git_history(tmpdir)
            self.assert_true(isinstance(history, dict), "history 应该返回字典")
            self.assert_in("is_git_repo", history, "history 应该包含 is_git_repo")

    def test_context_collector_api(self):
        """测试上下文收集器 API"""
        print("\n测试 3: 上下文收集器 API")
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.py").write_text("print('hello')")

            context = collect_project_context(tmpdir)
            self.assert_true(isinstance(context, dict), "context 应该是字典")
            self.assert_in("tech_stack", context, "context 应该包含 tech_stack")
            self.assert_in("project_structure", context, "context 应该包含 project_structure")
            self.assert_in("git_history", context, "context 应该包含 git_history")
            self.assert_in("summary", context, "context 应该包含 summary")
            self.assert_in("context_string", context, "context 应该包含 context_string")

    def test_python_project_context(self):
        """测试 Python 项目上下文"""
        print("\n测试 4: Python 项目上下文")
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 Python 项目
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "tests").mkdir()
            Path(tmpdir, "main.py").write_text("print('hello')")
            Path(tmpdir, "requirements.txt").write_text("django==4.0\nrequests==2.28.0")
            Path(tmpdir, "setup.py").write_text("from setuptools import setup\nsetup(name='test')")

            context = collect_project_context(tmpdir)
            self.assert_true(len(context["tech_stack"]["backend"]) > 0, "应该检测到后端技术")
            self.assert_true(len(context["project_structure"]["key_directories"]) > 0, "应该检测到关键目录")
            self.assert_true(len(context["summary"]) > 0, "应该生成摘要")

    def test_nodejs_project_context(self):
        """测试 Node.js 项目上下文"""
        print("\n测试 5: Node.js 项目上下文")
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 Node.js 项目
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "tests").mkdir()
            Path(tmpdir, "index.js").write_text("console.log('hello')")
            Path(tmpdir, "package.json").write_text(
                '{"name": "test", "dependencies": {"react": "^18.0.0", "express": "^4.18.0"}}'
            )

            context = collect_project_context(tmpdir)
            self.assert_true(len(context["tech_stack"]["backend"]) > 0, "应该检测到后端技术")
            self.assert_true(len(context["project_structure"]["key_directories"]) > 0, "应该检测到关键目录")
            self.assert_true(len(context["summary"]) > 0, "应该生成摘要")

    def test_context_string_completeness(self):
        """测试格式化字符串的完整性"""
        print("\n测试 6: 格式化字符串完整性")
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.py").write_text("print('hello')")
            Path(tmpdir, "requirements.txt").write_text("django==4.0")
            Path(tmpdir, "package.json").write_text('{"name": "test"}')

            context = collect_project_context(tmpdir)
            context_str = context["context_string"]

            self.assert_true("# 项目上下文" in context_str, "应该包含项目上下文标题")
            self.assert_true("## 技术栈" in context_str, "应该包含技术栈部分")
            self.assert_true("## 项目结构" in context_str, "应该包含项目结构部分")

    def test_error_handling(self):
        """测试错误处理"""
        print("\n测试 7: 错误处理")
        # 测试不存在的路径
        context = collect_project_context("/nonexistent/path")
        self.assert_true(isinstance(context, dict), "应该返回字典")
        self.assert_equal(context["git_history"]["is_git_repo"], False, "不应该是 Git 仓库")

    def test_cache_across_instances(self):
        """测试缓存机制"""
        print("\n测试 8: 缓存机制")
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.py").write_text("print('hello')")

            collector1 = ContextCollector(tmpdir)
            result1 = collector1.collect()

            collector2 = ContextCollector(tmpdir)
            result2 = collector2.collect()

            # 不同实例应该有不同的缓存
            self.assert_true(result1 is not result2, "不同实例应该有不同的缓存")

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 70)
        print("  P0.4 集成测试")
        print("=" * 70)

        self.test_module_imports()
        self.test_api_compatibility()
        self.test_context_collector_api()
        self.test_python_project_context()
        self.test_nodejs_project_context()
        self.test_context_string_completeness()
        self.test_error_handling()
        self.test_cache_across_instances()

        print("\n" + "=" * 70)
        print(f"  测试结果: {self.passed} 通过, {self.failed} 失败")
        print("=" * 70)

        return self.failed == 0


if __name__ == "__main__":
    tester = TestP0_4Integration()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

