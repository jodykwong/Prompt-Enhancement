#!/usr/bin/env python3
"""
P0.1 快速验证脚本

验证技术栈检测器的功能
"""

import sys
import json
from pathlib import Path
from tech_stack_detector import detect_tech_stack


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(result, project_path):
    """打印检测结果"""
    print(f"\n📁 项目路径: {project_path}\n")

    # 前端框架
    frontend = result["frontend"]
    print(f"🎨 前端框架: {', '.join(frontend) if frontend else '未检测到'}")

    # 后端语言和框架
    backend = result["backend"]
    print(f"⚙️  后端语言/框架: {', '.join(backend) if backend else '未检测到'}")

    # 数据库
    database = result["database"]
    print(f"🗄️  数据库: {', '.join(database) if database else '未检测到'}")

    # 构建工具
    build_tools = result["build_tools"]
    print(f"🔨 构建工具: {', '.join(build_tools) if build_tools else '未检测到'}")

    # 检测到的文件
    print(f"\n📄 检测到的文件:")
    detected_files = result["detected_files"]
    for file, exists in detected_files.items():
        if exists:
            print(f"   ✓ {file}")

    not_detected = [f for f, e in detected_files.items() if not e]
    if not_detected:
        print(f"\n   未检测到的文件:")
        for file in not_detected[:5]:  # 只显示前 5 个
            print(f"   ✗ {file}")
        if len(not_detected) > 5:
            print(f"   ... 还有 {len(not_detected) - 5} 个文件")


def test_current_project():
    """测试当前项目"""
    print_header("测试 1: 当前项目检测")

    result = detect_tech_stack(".")
    print_result(result, ".")

    # 验证结果
    assert result["backend"], "应该检测到后端语言"
    print("\n✅ 测试通过")


def test_react_project():
    """测试 React 项目"""
    print_header("测试 2: React 项目检测（模拟）")

    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建 React 项目
        package_json = {
            "name": "react-app",
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0",
                "axios": "^1.0.0",
            },
            "devDependencies": {
                "webpack": "^5.0.0",
                "typescript": "^4.0.0",
            },
        }

        package_json_path = Path(tmpdir) / "package.json"
        with open(package_json_path, "w") as f:
            json.dump(package_json, f)

        result = detect_tech_stack(tmpdir)
        print_result(result, tmpdir)

        # 验证结果
        assert "React" in result["frontend"], "应该检测到 React"
        assert "Node.js" in result["backend"], "应该检测到 Node.js"
        print("\n✅ 测试通过")


def test_django_project():
    """测试 Django 项目"""
    print_header("测试 3: Django 项目检测（模拟）")

    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建 Django 项目
        requirements_path = Path(tmpdir) / "requirements.txt"
        with open(requirements_path, "w") as f:
            f.write("django==4.2.0\n")
            f.write("djangorestframework==3.14.0\n")
            f.write("psycopg2-binary==2.9.0\n")
            f.write("redis==4.5.0\n")

        result = detect_tech_stack(tmpdir)
        print_result(result, tmpdir)

        # 验证结果
        assert "Python" in result["backend"], "应该检测到 Python"
        assert "Django" in result["backend"], "应该检测到 Django"
        assert "Postgresql" in result["database"], "应该检测到 PostgreSQL"
        assert "Redis" in result["database"], "应该检测到 Redis"
        print("\n✅ 测试通过")


def test_fullstack_project():
    """测试全栈项目"""
    print_header("测试 4: 全栈项目检测（模拟）")

    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建全栈项目
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

        requirements_path = Path(tmpdir) / "requirements.txt"
        with open(requirements_path, "w") as f:
            f.write("flask==2.3.0\n")
            f.write("pymongo==4.3.0\n")

        result = detect_tech_stack(tmpdir)
        print_result(result, tmpdir)

        # 验证结果
        assert "React" in result["frontend"], "应该检测到 React"
        assert "Node.js" in result["backend"], "应该检测到 Node.js"
        assert "Python" in result["backend"], "应该检测到 Python"
        assert "Express" in result["backend"], "应该检测到 Express"
        assert "Flask" in result["backend"], "应该检测到 Flask"
        assert "Mongodb" in result["database"], "应该检测到 MongoDB"
        print("\n✅ 测试通过")


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "P0.1 技术栈检测器 - 快速验证".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    try:
        test_current_project()
        test_react_project()
        test_django_project()
        test_fullstack_project()

        print_header("✅ 所有测试通过！")
        print("\n🎉 P0.1 技术栈检测器功能验证完成！\n")
        print("📚 更多信息:")
        print("   - 详细报告: P0_1_COMPLETION_REPORT.md")
        print("   - 最终总结: P0_1_FINAL_SUMMARY.md")
        print("   - 单元测试: python3 tests/test_tech_stack_detector.py")
        print("   - 集成测试: python3 tests/test_p0_integration.py")
        print()

        return 0

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

