#!/usr/bin/env python3
"""
P0.2 集成测试

验证项目结构分析器与技术栈检测器的集成
"""

import sys
import json
import tempfile
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from tech_stack_detector import detect_tech_stack
from project_structure_analyzer import analyze_project_structure


class TestP0_2Integration:
    """P0.2 集成测试类"""

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

    def test_project_structure_analyzer_import(self):
        """测试项目结构分析器导入"""
        print("\n" + "=" * 60)
        print("测试 1: 项目结构分析器导入")
        print("=" * 60)

        try:
            from project_structure_analyzer import ProjectStructureAnalyzer, analyze_project_structure
            self.assert_true(True, "成功导入 ProjectStructureAnalyzer")
            self.assert_true(True, "成功导入 analyze_project_structure 函数")
        except ImportError as e:
            self.assert_true(False, f"导入失败: {e}")

    def test_project_structure_analyzer_api(self):
        """测试项目结构分析器 API"""
        print("\n" + "=" * 60)
        print("测试 2: 项目结构分析器 API")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试项目
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "tests").mkdir()
            Path(tmpdir, "main.py").touch()
            Path(tmpdir, ".env").touch()

            # 测试 analyze_project_structure 函数
            result = analyze_project_structure(tmpdir)

            self.assert_true(isinstance(result, dict), "analyze_project_structure 返回字典")
            self.assert_true("key_directories" in result, "结果包含 key_directories 键")
            self.assert_true("entry_files" in result, "结果包含 entry_files 键")
            self.assert_true("config_files" in result, "结果包含 config_files 键")
            self.assert_true("directory_tree" in result, "结果包含 directory_tree 键")
            self.assert_true("total_files" in result, "结果包含 total_files 键")
            self.assert_true("total_directories" in result, "结果包含 total_directories 键")

    def test_combined_context_collection(self):
        """测试组合上下文收集"""
        print("\n" + "=" * 60)
        print("测试 3: 组合上下文收集（P0.1 + P0.2）")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建混合项目
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "tests").mkdir()
            Path(tmpdir, "docs").mkdir()

            # 创建 Python 项目文件
            package_json = {
                "name": "test-app",
                "dependencies": {
                    "react": "^18.0.0",
                    "express": "^4.18.0",
                },
            }

            package_json_path = Path(tmpdir) / "package.json"
            with open(package_json_path, "w") as f:
                json.dump(package_json, f)

            requirements_path = Path(tmpdir) / "requirements.txt"
            with open(requirements_path, "w") as f:
                f.write("django==4.2.0\n")
                f.write("psycopg2-binary==2.9.0\n")

            # 创建入口文件和配置文件
            Path(tmpdir, "main.py").touch()
            Path(tmpdir, "index.js").touch()
            Path(tmpdir, ".env").touch()
            Path(tmpdir, "config.yaml").touch()

            # 收集技术栈信息
            tech_stack = detect_tech_stack(tmpdir)

            # 收集项目结构信息
            project_structure = analyze_project_structure(tmpdir)

            # 验证组合信息
            self.assert_true(
                "React" in tech_stack["frontend"],
                "技术栈检测到 React",
            )
            self.assert_true(
                "Python" in tech_stack["backend"],
                "技术栈检测到 Python",
            )
            self.assert_true(
                "Django" in tech_stack["backend"],
                "技术栈检测到 Django",
            )

            self.assert_in("src", project_structure["key_directories"], "项目结构检测到 src")
            self.assert_in("tests", project_structure["key_directories"], "项目结构检测到 tests")
            self.assert_in("main.py", project_structure["entry_files"], "项目结构检测到 main.py")
            self.assert_in(".env", project_structure["config_files"], "项目结构检测到 .env")

    def test_python_project_context(self):
        """测试 Python 项目上下文"""
        print("\n" + "=" * 60)
        print("测试 4: Python 项目上下文")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 Python 项目
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "tests").mkdir()

            requirements_path = Path(tmpdir) / "requirements.txt"
            with open(requirements_path, "w") as f:
                f.write("django==4.2.0\n")
                f.write("psycopg2-binary==2.9.0\n")
                f.write("redis==4.5.0\n")

            Path(tmpdir, "manage.py").touch()
            Path(tmpdir, ".env").touch()
            Path(tmpdir, "settings.py").touch()

            # 收集信息
            tech_stack = detect_tech_stack(tmpdir)
            project_structure = analyze_project_structure(tmpdir)

            # 验证
            self.assert_true("Python" in tech_stack["backend"], "检测到 Python")
            self.assert_true("Django" in tech_stack["backend"], "检测到 Django")
            self.assert_in("src", project_structure["key_directories"], "检测到 src 目录")
            self.assert_in("manage.py", project_structure["entry_files"], "检测到 manage.py")

    def test_nodejs_project_context(self):
        """测试 Node.js 项目上下文"""
        print("\n" + "=" * 60)
        print("测试 5: Node.js 项目上下文")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 Node.js 项目
            Path(tmpdir, "src").mkdir()
            Path(tmpdir, "__tests__").mkdir()

            package_json = {
                "name": "node-app",
                "dependencies": {
                    "express": "^4.18.0",
                    "mongodb": "^5.0.0",
                },
            }

            package_json_path = Path(tmpdir) / "package.json"
            with open(package_json_path, "w") as f:
                json.dump(package_json, f)

            Path(tmpdir, "server.js").touch()
            Path(tmpdir, ".env.example").touch()
            Path(tmpdir, "webpack.config.js").touch()

            # 收集信息
            tech_stack = detect_tech_stack(tmpdir)
            project_structure = analyze_project_structure(tmpdir)

            # 验证
            self.assert_true("Node.js" in tech_stack["backend"], "检测到 Node.js")
            self.assert_true("Express" in tech_stack["backend"], "检测到 Express")
            self.assert_in("src", project_structure["key_directories"], "检测到 src 目录")
            self.assert_in("server.js", project_structure["entry_files"], "检测到 server.js")

    def test_edge_cases(self):
        """测试边界情况"""
        print("\n" + "=" * 60)
        print("测试 6: 边界情况")
        print("=" * 60)

        # 测试不存在的路径
        tech_stack = detect_tech_stack("/nonexistent/path")
        project_structure = analyze_project_structure("/nonexistent/path")

        self.assert_true(tech_stack["backend"] == [], "不存在的路径返回空技术栈")
        self.assert_true(project_structure["key_directories"] == [], "不存在的路径返回空结构")

        # 测试空目录
        with tempfile.TemporaryDirectory() as tmpdir:
            tech_stack = detect_tech_stack(tmpdir)
            project_structure = analyze_project_structure(tmpdir)

            self.assert_true(tech_stack["backend"] == [], "空目录返回空技术栈")
            self.assert_true(project_structure["key_directories"] == [], "空目录返回空结构")

    def run_all_tests(self):
        """运行所有测试"""
        print("\n")
        print("╔" + "=" * 58 + "╗")
        print("║" + " " * 58 + "║")
        print("║" + "P0.2 集成测试".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("╚" + "=" * 58 + "╝")

        self.test_project_structure_analyzer_import()
        self.test_project_structure_analyzer_api()
        self.test_combined_context_collection()
        self.test_python_project_context()
        self.test_nodejs_project_context()
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
    tester = TestP0_2Integration()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

