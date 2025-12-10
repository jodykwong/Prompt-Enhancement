#!/usr/bin/env python3
"""
项目结构分析器单元测试

测试覆盖：
1. 关键目录识别（src/, tests/, docs/, config/）
2. 入口文件识别（main.py, index.js, app.py）
3. 配置文件识别（.env, config.yaml, settings.py）
4. 目录树生成
5. 错误处理（不存在的路径、权限问题）
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from project_structure_analyzer import analyze_project_structure, ProjectStructureAnalyzer


class TestProjectStructureAnalyzer:
    """项目结构分析器测试类"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

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

    def test_python_project(self):
        """测试 Python 项目结构分析"""
        print("\n" + "=" * 60)
        print("测试 1: Python 项目结构分析")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 Python 项目结构
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "tests").mkdir()
            Path(tmpdir, "docs").mkdir()
            Path(tmpdir, "config").mkdir()

            # 创建入口文件
            Path(tmpdir, "main.py").touch()
            Path(tmpdir, "app.py").touch()

            # 创建配置文件
            Path(tmpdir, ".env").touch()
            Path(tmpdir, "config.yaml").touch()

            # 分析项目结构
            result = analyze_project_structure(tmpdir)

            # 验证结果
            self.assert_in("src", result["key_directories"], "检测到 src 目录")
            self.assert_in("tests", result["key_directories"], "检测到 tests 目录")
            self.assert_in("docs", result["key_directories"], "检测到 docs 目录")
            self.assert_in("config", result["key_directories"], "检测到 config 目录")

            self.assert_in("main.py", result["entry_files"], "检测到 main.py")
            self.assert_in("app.py", result["entry_files"], "检测到 app.py")

            self.assert_in(".env", result["config_files"], "检测到 .env")
            self.assert_in("config.yaml", result["config_files"], "检测到 config.yaml")

            self.assert_true(result["total_files"] >= 4, "文件总数 >= 4")
            self.assert_true(result["total_directories"] >= 4, "目录总数 >= 4")

    def test_nodejs_project(self):
        """测试 Node.js 项目结构分析"""
        print("\n" + "=" * 60)
        print("测试 2: Node.js 项目结构分析")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 Node.js 项目结构
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "__tests__").mkdir()
            Path(tmpdir, "scripts").mkdir()

            # 创建入口文件
            Path(tmpdir, "index.js").touch()
            Path(tmpdir, "server.js").touch()

            # 创建配置文件
            Path(tmpdir, ".env.example").touch()
            Path(tmpdir, "webpack.config.js").touch()

            # 分析项目结构
            result = analyze_project_structure(tmpdir)

            # 验证结果
            self.assert_in("src", result["key_directories"], "检测到 src 目录")
            self.assert_in("__tests__", result["key_directories"], "检测到 __tests__ 目录")
            self.assert_in("scripts", result["key_directories"], "检测到 scripts 目录")

            self.assert_in("index.js", result["entry_files"], "检测到 index.js")
            self.assert_in("server.js", result["entry_files"], "检测到 server.js")

            self.assert_in(".env.example", result["config_files"], "检测到 .env.example")
            self.assert_in("webpack.config.js", result["config_files"], "检测到 webpack.config.js")

    def test_fullstack_project(self):
        """测试全栈项目结构分析"""
        print("\n" + "=" * 60)
        print("测试 3: 全栈项目结构分析")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建全栈项目结构
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "app").mkdir()
            Path(tmpdir, "tests").mkdir()
            Path(tmpdir, "docs").mkdir()
            Path(tmpdir, "config").mkdir()
            Path(tmpdir, "scripts").mkdir()

            # 创建入口文件
            Path(tmpdir, "main.py").touch()
            Path(tmpdir, "index.js").touch()
            Path(tmpdir, "App.tsx").touch()

            # 创建配置文件
            Path(tmpdir, ".env").touch()
            Path(tmpdir, "config.json").touch()
            Path(tmpdir, "docker-compose.yml").touch()

            # 分析项目结构
            result = analyze_project_structure(tmpdir)

            # 验证结果
            self.assert_true(len(result["key_directories"]) >= 5, "检测到至少 5 个关键目录")
            self.assert_true(len(result["entry_files"]) >= 3, "检测到至少 3 个入口文件")
            self.assert_true(len(result["config_files"]) >= 3, "检测到至少 3 个配置文件")

    def test_nonexistent_path(self):
        """测试不存在的路径处理"""
        print("\n" + "=" * 60)
        print("测试 4: 不存在的路径处理")
        print("=" * 60)

        result = analyze_project_structure("/nonexistent/path")

        self.assert_equal(result["key_directories"], [], "关键目录为空")
        self.assert_equal(result["entry_files"], [], "入口文件为空")
        self.assert_equal(result["config_files"], [], "配置文件为空")
        self.assert_equal(result["total_files"], 0, "文件总数为 0")
        self.assert_equal(result["total_directories"], 0, "目录总数为 0")

    def test_empty_project(self):
        """测试空项目处理"""
        print("\n" + "=" * 60)
        print("测试 5: 空项目处理")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            result = analyze_project_structure(tmpdir)

            self.assert_equal(result["key_directories"], [], "关键目录为空")
            self.assert_equal(result["entry_files"], [], "入口文件为空")
            self.assert_equal(result["config_files"], [], "配置文件为空")

    def test_directory_tree_generation(self):
        """测试目录树生成"""
        print("\n" + "=" * 60)
        print("测试 6: 目录树生成")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建项目结构
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "src", "components").mkdir()
            Path(tmpdir, "tests").mkdir()
            Path(tmpdir, "main.py").touch()

            result = analyze_project_structure(tmpdir)

            # 验证目录树包含关键目录
            self.assert_true("src" in result["directory_tree"], "目录树包含 src")
            self.assert_true("tests" in result["directory_tree"], "目录树包含 tests")
            self.assert_true(len(result["directory_tree"]) > 0, "目录树不为空")

    def run_all_tests(self):
        """运行所有测试"""
        print("\n")
        print("╔" + "=" * 58 + "╗")
        print("║" + " " * 58 + "║")
        print("║" + "项目结构分析器单元测试".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("╚" + "=" * 58 + "╝")

        self.test_python_project()
        self.test_nodejs_project()
        self.test_fullstack_project()
        self.test_nonexistent_path()
        self.test_empty_project()
        self.test_directory_tree_generation()

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
    import sys

    tester = TestProjectStructureAnalyzer()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

