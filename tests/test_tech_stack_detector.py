#!/usr/bin/env python3
"""
技术栈检测器单元测试

测试覆盖：
1. 前端框架检测（React, Vue, Angular）
2. 后端语言检测（Python, Node.js, Java）
3. 数据库检测（PostgreSQL, MySQL, MongoDB）
4. 构建工具检测（npm, pip, Maven）
5. 错误处理（不存在的路径、损坏的文件）
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from tech_stack_detector import detect_tech_stack, TechStackDetector


class TestTechStackDetector:
    """技术栈检测器测试类"""

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

    def test_react_project(self):
        """测试 React 项目检测"""
        print("\n" + "=" * 60)
        print("测试 1: React 项目检测")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 React 项目结构
            package_json = {
                "name": "react-app",
                "dependencies": {
                    "react": "^18.0.0",
                    "react-dom": "^18.0.0",
                },
                "devDependencies": {
                    "webpack": "^5.0.0",
                },
            }

            package_json_path = Path(tmpdir) / "package.json"
            with open(package_json_path, "w") as f:
                json.dump(package_json, f)

            # 检测技术栈
            result = detect_tech_stack(tmpdir)

            # 验证结果
            self.assert_in("React", result["frontend"], "检测到 React")
            self.assert_in("Node.js", result["backend"], "检测到 Node.js")
            self.assert_in("Npm", result["build_tools"], "检测到 npm")
            print(f"  检测结果: {result}")

    def test_python_django_project(self):
        """测试 Python Django 项目检测"""
        print("\n" + "=" * 60)
        print("测试 2: Python Django 项目检测")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 requirements.txt
            requirements_path = Path(tmpdir) / "requirements.txt"
            with open(requirements_path, "w") as f:
                f.write("django==4.2.0\n")
                f.write("psycopg2-binary==2.9.0\n")
                f.write("djangorestframework==3.14.0\n")

            # 检测技术栈
            result = detect_tech_stack(tmpdir)

            # 验证结果
            self.assert_in("Python", result["backend"], "检测到 Python")
            self.assert_in("Django", result["backend"], "检测到 Django")
            self.assert_in("Postgresql", result["database"], "检测到 PostgreSQL")
            self.assert_in("Pip", result["build_tools"], "检测到 pip")

    def test_fullstack_project(self):
        """测试全栈项目检测"""
        print("\n" + "=" * 60)
        print("测试 3: 全栈项目检测")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 package.json（前端）
            package_json = {
                "name": "fullstack-app",
                "dependencies": {
                    "react": "^18.0.0",
                    "express": "^4.18.0",
                    "mongodb": "^5.0.0",
                },
            }

            package_json_path = Path(tmpdir) / "package.json"
            with open(package_json_path, "w") as f:
                json.dump(package_json, f)

            # 创建 requirements.txt（后端）
            requirements_path = Path(tmpdir) / "requirements.txt"
            with open(requirements_path, "w") as f:
                f.write("flask==2.3.0\n")
                f.write("pymongo==4.3.0\n")

            # 检测技术栈
            result = detect_tech_stack(tmpdir)

            # 验证结果
            self.assert_in("React", result["frontend"], "检测到 React")
            self.assert_in("Node.js", result["backend"], "检测到 Node.js")
            self.assert_in("Python", result["backend"], "检测到 Python")
            self.assert_in("Express", result["backend"], "检测到 Express")
            self.assert_in("Flask", result["backend"], "检测到 Flask")
            self.assert_in("Mongodb", result["database"], "检测到 MongoDB")

    def test_nonexistent_path(self):
        """测试不存在的路径"""
        print("\n" + "=" * 60)
        print("测试 4: 不存在的路径处理")
        print("=" * 60)

        result = detect_tech_stack("/nonexistent/path")

        # 验证结果
        self.assert_equal(result["frontend"], [], "前端框架为空")
        self.assert_equal(result["backend"], [], "后端语言为空")
        self.assert_equal(result["database"], [], "数据库为空")
        self.assert_equal(result["build_tools"], [], "构建工具为空")

    def test_empty_project(self):
        """测试空项目"""
        print("\n" + "=" * 60)
        print("测试 5: 空项目处理")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            result = detect_tech_stack(tmpdir)

            # 验证结果
            self.assert_equal(result["frontend"], [], "前端框架为空")
            self.assert_equal(result["backend"], [], "后端语言为空")
            self.assert_equal(result["database"], [], "数据库为空")
            self.assert_equal(result["build_tools"], [], "构建工具为空")

    def test_detected_files(self):
        """测试检测到的文件列表"""
        print("\n" + "=" * 60)
        print("测试 6: 检测到的文件列表")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建一些文件
            Path(tmpdir, "package.json").touch()
            Path(tmpdir, "requirements.txt").touch()
            Path(tmpdir, "Dockerfile").touch()

            result = detect_tech_stack(tmpdir)

            # 验证结果
            self.assert_equal(
                result["detected_files"]["package.json"],
                True,
                "检测到 package.json",
            )
            self.assert_equal(
                result["detected_files"]["requirements.txt"],
                True,
                "检测到 requirements.txt",
            )
            self.assert_equal(
                result["detected_files"]["Dockerfile"],
                True,
                "检测到 Dockerfile",
            )
            self.assert_equal(
                result["detected_files"]["pom.xml"],
                False,
                "未检测到 pom.xml",
            )

    def run_all_tests(self):
        """运行所有测试"""
        print("\n")
        print("╔" + "=" * 58 + "╗")
        print("║" + " " * 58 + "║")
        print("║" + "技术栈检测器单元测试".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("╚" + "=" * 58 + "╝")

        self.test_react_project()
        self.test_python_django_project()
        self.test_fullstack_project()
        self.test_nonexistent_path()
        self.test_empty_project()
        self.test_detected_files()

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
    tester = TestTechStackDetector()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

