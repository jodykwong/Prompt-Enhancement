#!/usr/bin/env python3
"""
P0.3 集成测试

验证 Git 历史分析器与 P0.1、P0.2 的集成
"""

import sys
import subprocess
import tempfile
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from tech_stack_detector import detect_tech_stack
from project_structure_analyzer import analyze_project_structure
from git_history_analyzer import analyze_git_history


class TestP0_3Integration:
    """P0.3 集成测试类"""

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

    def test_git_history_analyzer_import(self):
        """测试 Git 历史分析器导入"""
        print("\n" + "=" * 60)
        print("测试 1: Git 历史分析器导入")
        print("=" * 60)

        try:
            from git_history_analyzer import GitHistoryAnalyzer, analyze_git_history
            self.assert_true(True, "成功导入 GitHistoryAnalyzer")
            self.assert_true(True, "成功导入 analyze_git_history 函数")
        except ImportError as e:
            self.assert_true(False, f"导入失败: {e}")

    def test_git_history_analyzer_api(self):
        """测试 Git 历史分析器 API"""
        print("\n" + "=" * 60)
        print("测试 2: Git 历史分析器 API")
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

            # 测试 analyze_git_history 函数
            result = analyze_git_history(tmpdir)

            self.assert_true(isinstance(result, dict), "analyze_git_history 返回字典")
            self.assert_true("recent_commits" in result, "结果包含 recent_commits 键")
            self.assert_true("modified_files" in result, "结果包含 modified_files 键")
            self.assert_true("active_branches" in result, "结果包含 active_branches 键")
            self.assert_true("current_branch" in result, "结果包含 current_branch 键")
            self.assert_true(
                "has_uncommitted_changes" in result, "结果包含 has_uncommitted_changes 键"
            )
            self.assert_true("is_git_repo" in result, "结果包含 is_git_repo 键")

    def test_combined_context_collection(self):
        """测试组合上下文收集（P0.1 + P0.2 + P0.3）"""
        print("\n" + "=" * 60)
        print("测试 3: 组合上下文收集（P0.1 + P0.2 + P0.3）")
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

            # 创建项目结构
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "tests").mkdir()

            # 创建配置文件
            import json

            package_json = {
                "name": "test-app",
                "dependencies": {
                    "react": "^18.0.0",
                },
            }

            package_json_path = Path(tmpdir) / "package.json"
            with open(package_json_path, "w") as f:
                json.dump(package_json, f)

            # 创建入口文件
            Path(tmpdir, "index.js").touch()
            Path(tmpdir, ".env").touch()

            # 提交
            subprocess.run(
                ["git", "add", "."],
                cwd=tmpdir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                cwd=tmpdir,
                capture_output=True,
            )

            # 收集所有上下文信息
            tech_stack = detect_tech_stack(tmpdir)
            project_structure = analyze_project_structure(tmpdir)
            git_history = analyze_git_history(tmpdir)

            # 验证组合信息
            self.assert_true(
                "React" in tech_stack["frontend"],
                "技术栈检测到 React",
            )
            self.assert_in("src", project_structure["key_directories"], "项目结构检测到 src")
            self.assert_true(
                git_history["is_git_repo"],
                "Git 历史检测到仓库",
            )
            self.assert_true(
                len(git_history["recent_commits"]) > 0,
                "Git 历史检测到提交",
            )

    def test_python_project_full_context(self):
        """测试 Python 项目完整上下文"""
        print("\n" + "=" * 60)
        print("测试 4: Python 项目完整上下文")
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

            # 创建 Python 项目
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "tests").mkdir()

            requirements_path = Path(tmpdir) / "requirements.txt"
            with open(requirements_path, "w") as f:
                f.write("django==4.2.0\n")

            Path(tmpdir, "main.py").touch()
            Path(tmpdir, ".env").touch()

            # 提交
            subprocess.run(
                ["git", "add", "."],
                cwd=tmpdir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial Python project"],
                cwd=tmpdir,
                capture_output=True,
            )

            # 收集上下文
            tech_stack = detect_tech_stack(tmpdir)
            project_structure = analyze_project_structure(tmpdir)
            git_history = analyze_git_history(tmpdir)

            # 验证
            self.assert_true("Python" in tech_stack["backend"], "检测到 Python")
            self.assert_true("Django" in tech_stack["backend"], "检测到 Django")
            self.assert_in("src", project_structure["key_directories"], "检测到 src")
            self.assert_true(git_history["is_git_repo"], "是 Git 仓库")

    def test_nodejs_project_full_context(self):
        """测试 Node.js 项目完整上下文"""
        print("\n" + "=" * 60)
        print("测试 5: Node.js 项目完整上下文")
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

            # 创建 Node.js 项目
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "__tests__").mkdir()

            import json

            package_json = {
                "name": "node-app",
                "dependencies": {
                    "express": "^4.18.0",
                },
            }

            package_json_path = Path(tmpdir) / "package.json"
            with open(package_json_path, "w") as f:
                json.dump(package_json, f)

            Path(tmpdir, "server.js").touch()
            Path(tmpdir, ".env.example").touch()

            # 提交
            subprocess.run(
                ["git", "add", "."],
                cwd=tmpdir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial Node.js project"],
                cwd=tmpdir,
                capture_output=True,
            )

            # 收集上下文
            tech_stack = detect_tech_stack(tmpdir)
            project_structure = analyze_project_structure(tmpdir)
            git_history = analyze_git_history(tmpdir)

            # 验证
            self.assert_true("Node.js" in tech_stack["backend"], "检测到 Node.js")
            self.assert_true("Express" in tech_stack["backend"], "检测到 Express")
            self.assert_in("src", project_structure["key_directories"], "检测到 src")
            self.assert_true(git_history["is_git_repo"], "是 Git 仓库")

    def test_edge_cases(self):
        """测试边界情况"""
        print("\n" + "=" * 60)
        print("测试 6: 边界情况")
        print("=" * 60)

        # 测试不存在的路径
        result = analyze_git_history("/nonexistent/path")
        self.assert_true(not result["is_git_repo"], "不存在的路径不是 Git 仓库")

        # 测试空目录
        with tempfile.TemporaryDirectory() as tmpdir:
            result = analyze_git_history(tmpdir)
            self.assert_true(not result["is_git_repo"], "空目录不是 Git 仓库")

    def run_all_tests(self):
        """运行所有测试"""
        print("\n")
        print("╔" + "=" * 58 + "╗")
        print("║" + " " * 58 + "║")
        print("║" + "P0.3 集成测试".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("╚" + "=" * 58 + "╝")

        self.test_git_history_analyzer_import()
        self.test_git_history_analyzer_api()
        self.test_combined_context_collection()
        self.test_python_project_full_context()
        self.test_nodejs_project_full_context()
        self.test_edge_cases()

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
    tester = TestP0_3Integration()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

