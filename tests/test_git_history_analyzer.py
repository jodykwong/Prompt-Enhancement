#!/usr/bin/env python3
"""
Git 历史分析器单元测试

测试 git_history_analyzer 模块的功能
"""

import sys
import subprocess
import tempfile
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from git_history_analyzer import analyze_git_history, GitHistoryAnalyzer


class TestGitHistoryAnalyzer:
    """Git 历史分析器测试类"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def assert_true(self, condition, test_name):
        """断言为真"""
        if condition:
            self.passed += 1
            print(f"✓ {test_name}")
        else:
            self.failed += 1
            error_msg = f"✗ {test_name}"
            self.errors.append(error_msg)
            print(error_msg)

    def assert_equal(self, actual, expected, test_name):
        """断言相等"""
        if actual == expected:
            self.passed += 1
            print(f"✓ {test_name}")
        else:
            self.failed += 1
            error_msg = f"✗ {test_name}\n  期望: {expected}\n  实际: {actual}"
            self.errors.append(error_msg)
            print(error_msg)

    def assert_in(self, item, container, test_name):
        """断言包含"""
        if item in container:
            self.passed += 1
            print(f"✓ {test_name}")
        else:
            self.failed += 1
            error_msg = f"✗ {test_name}\n  期望 {item} 在 {container} 中"
            self.errors.append(error_msg)
            print(error_msg)

    def test_non_git_directory(self):
        """测试非 Git 目录"""
        print("\n" + "=" * 60)
        print("测试 1: 非 Git 目录处理")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            result = analyze_git_history(tmpdir)

            self.assert_equal(result["is_git_repo"], False, "is_git_repo 为 False")
            self.assert_equal(result["recent_commits"], [], "提交列表为空")
            self.assert_equal(result["modified_files"], [], "修改文件列表为空")
            self.assert_equal(result["active_branches"], [], "分支列表为空")
            self.assert_equal(result["current_branch"], "", "当前分支为空")
            self.assert_equal(
                result["has_uncommitted_changes"], False, "无未提交更改"
            )

    def test_nonexistent_path(self):
        """测试不存在的路径"""
        print("\n" + "=" * 60)
        print("测试 2: 不存在的路径处理")
        print("=" * 60)

        result = analyze_git_history("/nonexistent/path")

        self.assert_equal(result["is_git_repo"], False, "is_git_repo 为 False")
        self.assert_equal(result["recent_commits"], [], "提交列表为空")
        self.assert_equal(result["modified_files"], [], "修改文件列表为空")

    def test_git_repository_with_commits(self):
        """测试有提交历史的 Git 仓库"""
        print("\n" + "=" * 60)
        print("测试 3: Git 仓库（有提交历史）")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 初始化 Git 仓库
            subprocess.run(
                ["git", "init"],
                cwd=tmpdir,
                capture_output=True,
            )

            # 配置 Git 用户
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
            )

            # 创建文件并提交
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Hello World")

            subprocess.run(
                ["git", "add", "test.txt"],
                cwd=tmpdir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                cwd=tmpdir,
                capture_output=True,
            )

            # 分析 Git 历史
            result = analyze_git_history(tmpdir)

            self.assert_equal(result["is_git_repo"], True, "is_git_repo 为 True")
            self.assert_true(
                len(result["recent_commits"]) > 0, "有提交记录"
            )
            self.assert_true(
                "hash" in result["recent_commits"][0], "提交包含 hash"
            )
            self.assert_true(
                "author" in result["recent_commits"][0], "提交包含 author"
            )
            self.assert_true(
                "date" in result["recent_commits"][0], "提交包含 date"
            )
            self.assert_true(
                "message" in result["recent_commits"][0], "提交包含 message"
            )

    def test_git_repository_with_changes(self):
        """测试有未提交更改的 Git 仓库"""
        print("\n" + "=" * 60)
        print("测试 4: Git 仓库（有未提交更改）")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 初始化 Git 仓库
            subprocess.run(
                ["git", "init"],
                cwd=tmpdir,
                capture_output=True,
            )

            # 配置 Git 用户
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
            )

            # 创建文件并提交
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Hello World")

            subprocess.run(
                ["git", "add", "test.txt"],
                cwd=tmpdir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                cwd=tmpdir,
                capture_output=True,
            )

            # 修改文件（不提交）
            test_file.write_text("Hello World Modified")

            # 分析 Git 历史
            result = analyze_git_history(tmpdir)

            self.assert_equal(
                result["has_uncommitted_changes"], True, "有未提交更改"
            )
            self.assert_true(
                len(result["modified_files"]) > 0, "有修改文件"
            )

    def test_git_repository_branches(self):
        """测试 Git 仓库分支"""
        print("\n" + "=" * 60)
        print("测试 5: Git 仓库分支")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 初始化 Git 仓库
            subprocess.run(
                ["git", "init"],
                cwd=tmpdir,
                capture_output=True,
            )

            # 配置 Git 用户
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
            )

            # 创建文件并提交
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Hello World")

            subprocess.run(
                ["git", "add", "test.txt"],
                cwd=tmpdir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                cwd=tmpdir,
                capture_output=True,
            )

            # 创建新分支
            subprocess.run(
                ["git", "checkout", "-b", "develop"],
                cwd=tmpdir,
                capture_output=True,
            )

            # 分析 Git 历史
            result = analyze_git_history(tmpdir)

            self.assert_true(
                len(result["active_branches"]) > 0, "有分支"
            )
            self.assert_true(
                result["current_branch"] in ["main", "master", "develop"],
                "当前分支有效",
            )

    def test_analyzer_class(self):
        """测试 GitHistoryAnalyzer 类"""
        print("\n" + "=" * 60)
        print("测试 6: GitHistoryAnalyzer 类")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = GitHistoryAnalyzer(tmpdir, max_commits=3)

            self.assert_equal(
                analyzer.max_commits, 3, "max_commits 设置正确"
            )
            self.assert_true(
                analyzer.project_path.exists(), "项目路径存在"
            )

            result = analyzer.analyze()
            self.assert_true(
                isinstance(result, dict), "analyze() 返回字典"
            )
            self.assert_true(
                "is_git_repo" in result, "结果包含 is_git_repo"
            )

    def run_all_tests(self):
        """运行所有测试"""
        print("\n")
        print("╔" + "=" * 58 + "╗")
        print("║" + " " * 58 + "║")
        print("║" + "Git 历史分析器单元测试".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("╚" + "=" * 58 + "╝")

        self.test_non_git_directory()
        self.test_nonexistent_path()
        self.test_git_repository_with_commits()
        self.test_git_repository_with_changes()
        self.test_git_repository_branches()
        self.test_analyzer_class()

        # 打印总结
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        print(f"✓ 通过: {self.passed}")
        print(f"✗ 失败: {self.failed}")
        print(f"总计: {self.passed + self.failed}")

        if self.errors:
            print("\n错误详情:")
            for error in self.errors:
                print(error)

        print("=" * 60)

        return self.failed == 0


if __name__ == "__main__":
    tester = TestGitHistoryAnalyzer()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

