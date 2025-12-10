#!/usr/bin/env python3
"""
P0 阶段集成测试

验证技术栈检测器与提示词增强器的集成
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from tech_stack_detector import detect_tech_stack


class TestP0Integration:
    """P0 阶段集成测试类"""

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

    def test_tech_stack_detector_import(self):
        """测试技术栈检测器导入"""
        print("\n" + "=" * 60)
        print("测试 1: 技术栈检测器导入")
        print("=" * 60)

        try:
            from tech_stack_detector import TechStackDetector, detect_tech_stack
            self.assert_true(True, "成功导入 TechStackDetector")
            self.assert_true(True, "成功导入 detect_tech_stack 函数")
        except ImportError as e:
            self.assert_true(False, f"导入失败: {e}")

    def test_tech_stack_detector_api(self):
        """测试技术栈检测器 API"""
        print("\n" + "=" * 60)
        print("测试 2: 技术栈检测器 API")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试项目
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

            # 测试 detect_tech_stack 函数
            result = detect_tech_stack(tmpdir)

            self.assert_true(
                isinstance(result, dict),
                "detect_tech_stack 返回字典",
            )
            self.assert_true(
                "frontend" in result,
                "结果包含 frontend 键",
            )
            self.assert_true(
                "backend" in result,
                "结果包含 backend 键",
            )
            self.assert_true(
                "database" in result,
                "结果包含 database 键",
            )
            self.assert_true(
                "build_tools" in result,
                "结果包含 build_tools 键",
            )
            self.assert_true(
                "detected_files" in result,
                "结果包含 detected_files 键",
            )

    def test_tech_stack_detector_accuracy(self):
        """测试技术栈检测准确性"""
        print("\n" + "=" * 60)
        print("测试 3: 技术栈检测准确性")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 Python 项目
            requirements_path = Path(tmpdir) / "requirements.txt"
            with open(requirements_path, "w") as f:
                f.write("django==4.2.0\n")
                f.write("psycopg2-binary==2.9.0\n")
                f.write("redis==4.5.0\n")

            result = detect_tech_stack(tmpdir)

            self.assert_true(
                "Python" in result["backend"],
                "检测到 Python",
            )
            self.assert_true(
                "Django" in result["backend"],
                "检测到 Django",
            )
            self.assert_true(
                "Postgresql" in result["database"],
                "检测到 PostgreSQL",
            )
            self.assert_true(
                "Redis" in result["database"],
                "检测到 Redis",
            )
            self.assert_true(
                "Pip" in result["build_tools"],
                "检测到 pip",
            )

    def test_tech_stack_detector_multiple_frameworks(self):
        """测试多框架检测"""
        print("\n" + "=" * 60)
        print("测试 4: 多框架检测")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建混合项目
            package_json = {
                "name": "mixed-app",
                "dependencies": {
                    "react": "^18.0.0",
                    "vue": "^3.0.0",
                    "express": "^4.18.0",
                    "mongodb": "^5.0.0",
                },
            }

            package_json_path = Path(tmpdir) / "package.json"
            with open(package_json_path, "w") as f:
                json.dump(package_json, f)

            result = detect_tech_stack(tmpdir)

            self.assert_true(
                "React" in result["frontend"],
                "检测到 React",
            )
            self.assert_true(
                "Vue" in result["frontend"],
                "检测到 Vue",
            )
            self.assert_true(
                "Express" in result["backend"],
                "检测到 Express",
            )
            self.assert_true(
                "Mongodb" in result["database"],
                "检测到 MongoDB",
            )

    def test_tech_stack_detector_file_detection(self):
        """测试文件检测"""
        print("\n" + "=" * 60)
        print("测试 5: 文件检测")
        print("=" * 60)

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建多个文件
            Path(tmpdir, "package.json").touch()
            Path(tmpdir, "requirements.txt").touch()
            Path(tmpdir, "Dockerfile").touch()
            Path(tmpdir, "docker-compose.yml").touch()

            result = detect_tech_stack(tmpdir)

            self.assert_true(
                result["detected_files"]["package.json"],
                "检测到 package.json",
            )
            self.assert_true(
                result["detected_files"]["requirements.txt"],
                "检测到 requirements.txt",
            )
            self.assert_true(
                result["detected_files"]["Dockerfile"],
                "检测到 Dockerfile",
            )
            self.assert_true(
                result["detected_files"]["docker-compose.yml"],
                "检测到 docker-compose.yml",
            )
            self.assert_true(
                not result["detected_files"]["pom.xml"],
                "未检测到 pom.xml",
            )

    def test_tech_stack_detector_edge_cases(self):
        """测试边界情况"""
        print("\n" + "=" * 60)
        print("测试 6: 边界情况")
        print("=" * 60)

        # 测试不存在的路径
        result = detect_tech_stack("/nonexistent/path")
        self.assert_true(
            result["frontend"] == [],
            "不存在的路径返回空列表",
        )

        # 测试空目录
        with tempfile.TemporaryDirectory() as tmpdir:
            result = detect_tech_stack(tmpdir)
            self.assert_true(
                result["backend"] == [],
                "空目录返回空列表",
            )

    def run_all_tests(self):
        """运行所有测试"""
        print("\n")
        print("╔" + "=" * 58 + "╗")
        print("║" + " " * 58 + "║")
        print("║" + "P0 阶段集成测试".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("╚" + "=" * 58 + "╝")

        self.test_tech_stack_detector_import()
        self.test_tech_stack_detector_api()
        self.test_tech_stack_detector_accuracy()
        self.test_tech_stack_detector_multiple_frameworks()
        self.test_tech_stack_detector_file_detection()
        self.test_tech_stack_detector_edge_cases()

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
    tester = TestP0Integration()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

