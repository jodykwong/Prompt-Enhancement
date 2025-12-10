#!/usr/bin/env python3
"""
上下文收集器单元测试

测试上下文收集器的各项功能：
1. 收集完整项目上下文
2. 处理不存在的路径
3. 处理非 Git 仓库
4. 缓存机制
5. 格式化输出
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from context_collector import collect_project_context, ContextCollector


class TestContextCollector:
    """上下文收集器测试类"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_count = 0

    def assert_true(self, condition, message=""):
        """断言为真"""
        if not condition:
            print(f"  ✗ 断言失败: {message}")
            self.failed += 1
        else:
            self.passed += 1

    def assert_equal(self, actual, expected, message=""):
        """断言相等"""
        if actual != expected:
            print(f"  ✗ 断言失败: {message}")
            print(f"    期望: {expected}")
            print(f"    实际: {actual}")
            self.failed += 1
        else:
            self.passed += 1

    def assert_in(self, item, container, message=""):
        """断言包含"""
        if item not in container:
            print(f"  ✗ 断言失败: {message}")
            print(f"    {item} 不在 {container} 中")
            self.failed += 1
        else:
            self.passed += 1

    def test_nonexistent_path(self):
        """测试不存在的路径"""
        print("\n测试 1: 不存在的路径")
        result = collect_project_context("/nonexistent/path")
        self.assert_true(isinstance(result, dict), "返回值应该是字典")
        self.assert_equal(result["tech_stack"]["frontend"], [], "前端应该为空")
        self.assert_equal(result["project_structure"]["key_directories"], [], "关键目录应该为空")
        self.assert_equal(result["git_history"]["is_git_repo"], False, "不应该是 Git 仓库")

    def test_non_git_directory(self):
        """测试非 Git 目录"""
        print("\n测试 2: 非 Git 目录")
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建一个简单的 Python 项目
            Path(tmpdir, "main.py").write_text("print('hello')")
            Path(tmpdir, "requirements.txt").write_text("requests==2.28.0")

            result = collect_project_context(tmpdir)
            self.assert_true(isinstance(result, dict), "返回值应该是字典")
            self.assert_true("tech_stack" in result, "应该包含 tech_stack")
            self.assert_true("project_structure" in result, "应该包含 project_structure")
            self.assert_true("git_history" in result, "应该包含 git_history")
            self.assert_equal(result["git_history"]["is_git_repo"], False, "不应该是 Git 仓库")

    def test_complete_project(self):
        """测试完整项目"""
        print("\n测试 3: 完整项目")
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建项目结构
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "tests").mkdir()
            Path(tmpdir, "main.py").write_text("print('hello')")
            Path(tmpdir, "requirements.txt").write_text("django==4.0\nrequests==2.28.0")
            Path(tmpdir, "package.json").write_text('{"name": "test", "dependencies": {"react": "^18.0.0"}}')

            result = collect_project_context(tmpdir)
            self.assert_true(isinstance(result, dict), "返回值应该是字典")
            self.assert_true("summary" in result, "应该包含 summary")
            self.assert_true("context_string" in result, "应该包含 context_string")
            self.assert_true(len(result["summary"]) > 0, "摘要不应该为空")
            self.assert_true(len(result["context_string"]) > 0, "格式化字符串不应该为空")

    def test_context_string_format(self):
        """测试格式化字符串"""
        print("\n测试 4: 格式化字符串")
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.py").write_text("print('hello')")
            Path(tmpdir, "requirements.txt").write_text("django==4.0")

            result = collect_project_context(tmpdir)
            context_str = result["context_string"]
            self.assert_true("# 项目上下文" in context_str, "应该包含标题")
            self.assert_true("## 技术栈" in context_str, "应该包含技术栈部分")
            self.assert_true("## 项目结构" in context_str, "应该包含项目结构部分")

    def test_cache_mechanism(self):
        """测试缓存机制"""
        print("\n测试 5: 缓存机制")
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.py").write_text("print('hello')")

            collector = ContextCollector(tmpdir)
            result1 = collector.collect()
            result2 = collector.collect()

            # 两次调用应该返回相同的对象（来自缓存）
            self.assert_true(result1 is result2, "缓存应该返回相同的对象")

            # 清除缓存后应该返回不同的对象
            collector.clear_cache()
            result3 = collector.collect()
            self.assert_true(result1 is not result3, "清除缓存后应该返回不同的对象")

    def test_summary_generation(self):
        """测试摘要生成"""
        print("\n测试 6: 摘要生成")
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.py").write_text("print('hello')")
            Path(tmpdir, "requirements.txt").write_text("django==4.0")
            Path(tmpdir, "package.json").write_text('{"name": "test"}')

            result = collect_project_context(tmpdir)
            summary = result["summary"]
            self.assert_true(len(summary) > 0, "摘要不应该为空")
            self.assert_true(isinstance(summary, str), "摘要应该是字符串")

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 70)
        print("  上下文收集器单元测试")
        print("=" * 70)

        self.test_nonexistent_path()
        self.test_non_git_directory()
        self.test_complete_project()
        self.test_context_string_format()
        self.test_cache_mechanism()
        self.test_summary_generation()

        print("\n" + "=" * 70)
        print(f"  测试结果: {self.passed} 通过, {self.failed} 失败")
        print("=" * 70)

        return self.failed == 0


if __name__ == "__main__":
    tester = TestContextCollector()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

