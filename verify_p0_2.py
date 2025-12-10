#!/usr/bin/env python3
"""
P0.2 快速验证脚本

验证项目结构分析器的功能
"""

import sys
import json
import tempfile
from pathlib import Path
from tech_stack_detector import detect_tech_stack
from project_structure_analyzer import analyze_project_structure


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_structure_result(result, project_path):
    """打印项目结构分析结果"""
    print(f"\n📁 项目路径: {project_path}\n")

    # 关键目录
    key_dirs = result["key_directories"]
    print(f"📂 关键目录: {', '.join(key_dirs) if key_dirs else '未检测到'}")

    # 入口文件
    entry_files = result["entry_files"]
    print(f"📄 入口文件: {', '.join(entry_files) if entry_files else '未检测到'}")

    # 配置文件
    config_files = result["config_files"]
    print(f"⚙️  配置文件: {', '.join(config_files) if config_files else '未检测到'}")

    # 统计信息
    print(f"\n📊 统计信息:")
    print(f"   文件总数: {result['total_files']}")
    print(f"   目录总数: {result['total_directories']}")

    # 目录树
    if result["directory_tree"]:
        print(f"\n🌳 目录树 (深度限制: 3):")
        print(result["directory_tree"])


def test_current_project():
    """测试当前项目"""
    print_header("测试 1: 当前项目分析")

    result = analyze_project_structure(".")
    print_structure_result(result, ".")

    assert result["key_directories"], "应该检测到关键目录"
    print("\n✅ 测试通过")


def test_python_project():
    """测试 Python 项目"""
    print_header("测试 2: Python 项目分析（模拟）")

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建 Python 项目
        Path(tmpdir, "src").mkdir()
        Path(tmpdir, "tests").mkdir()
        Path(tmpdir, "docs").mkdir()
        Path(tmpdir, "config").mkdir()

        Path(tmpdir, "main.py").touch()
        Path(tmpdir, "app.py").touch()
        Path(tmpdir, "manage.py").touch()

        Path(tmpdir, ".env").touch()
        Path(tmpdir, "settings.py").touch()
        Path(tmpdir, "config.yaml").touch()

        # 创建 requirements.txt
        requirements_path = Path(tmpdir) / "requirements.txt"
        with open(requirements_path, "w") as f:
            f.write("django==4.2.0\n")
            f.write("psycopg2-binary==2.9.0\n")

        # 分析项目结构
        structure = analyze_project_structure(tmpdir)
        print_structure_result(structure, tmpdir)

        # 分析技术栈
        tech_stack = detect_tech_stack(tmpdir)
        print(f"\n🔧 技术栈:")
        print(f"   后端: {', '.join(tech_stack['backend']) if tech_stack['backend'] else '未检测到'}")
        print(f"   数据库: {', '.join(tech_stack['database']) if tech_stack['database'] else '未检测到'}")

        # 验证结果
        assert "src" in structure["key_directories"], "应该检测到 src"
        assert "main.py" in structure["entry_files"], "应该检测到 main.py"
        assert ".env" in structure["config_files"], "应该检测到 .env"
        assert "Python" in tech_stack["backend"], "应该检测到 Python"
        print("\n✅ 测试通过")


def test_nodejs_project():
    """测试 Node.js 项目"""
    print_header("测试 3: Node.js 项目分析（模拟）")

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建 Node.js 项目
        Path(tmpdir, "src").mkdir()
        Path(tmpdir, "__tests__").mkdir()
        Path(tmpdir, "scripts").mkdir()

        Path(tmpdir, "index.js").touch()
        Path(tmpdir, "server.js").touch()
        Path(tmpdir, "App.tsx").touch()

        Path(tmpdir, ".env.example").touch()
        Path(tmpdir, "webpack.config.js").touch()
        Path(tmpdir, "tsconfig.json").touch()

        # 创建 package.json
        package_json = {
            "name": "node-app",
            "dependencies": {
                "react": "^18.0.0",
                "express": "^4.18.0",
                "mongodb": "^5.0.0",
            },
        }

        package_json_path = Path(tmpdir) / "package.json"
        with open(package_json_path, "w") as f:
            json.dump(package_json, f)

        # 分析项目结构
        structure = analyze_project_structure(tmpdir)
        print_structure_result(structure, tmpdir)

        # 分析技术栈
        tech_stack = detect_tech_stack(tmpdir)
        print(f"\n🔧 技术栈:")
        print(f"   前端: {', '.join(tech_stack['frontend']) if tech_stack['frontend'] else '未检测到'}")
        print(f"   后端: {', '.join(tech_stack['backend']) if tech_stack['backend'] else '未检测到'}")
        print(f"   数据库: {', '.join(tech_stack['database']) if tech_stack['database'] else '未检测到'}")

        # 验证结果
        assert "src" in structure["key_directories"], "应该检测到 src"
        assert "index.js" in structure["entry_files"], "应该检测到 index.js"
        assert "React" in tech_stack["frontend"], "应该检测到 React"
        print("\n✅ 测试通过")


def test_fullstack_project():
    """测试全栈项目"""
    print_header("测试 4: 全栈项目分析（模拟）")

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建全栈项目
        Path(tmpdir, "src").mkdir()
        Path(tmpdir, "app").mkdir()
        Path(tmpdir, "tests").mkdir()
        Path(tmpdir, "docs").mkdir()
        Path(tmpdir, "config").mkdir()
        Path(tmpdir, "scripts").mkdir()

        Path(tmpdir, "main.py").touch()
        Path(tmpdir, "index.js").touch()
        Path(tmpdir, "App.tsx").touch()

        Path(tmpdir, ".env").touch()
        Path(tmpdir, "config.json").touch()
        Path(tmpdir, "docker-compose.yml").touch()

        # 创建配置文件
        package_json = {
            "name": "fullstack-app",
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
            f.write("flask==2.3.0\n")
            f.write("pymongo==4.3.0\n")

        # 分析项目结构
        structure = analyze_project_structure(tmpdir)
        print_structure_result(structure, tmpdir)

        # 分析技术栈
        tech_stack = detect_tech_stack(tmpdir)
        print(f"\n🔧 技术栈:")
        print(f"   前端: {', '.join(tech_stack['frontend']) if tech_stack['frontend'] else '未检测到'}")
        print(f"   后端: {', '.join(tech_stack['backend']) if tech_stack['backend'] else '未检测到'}")
        print(f"   数据库: {', '.join(tech_stack['database']) if tech_stack['database'] else '未检测到'}")

        # 验证结果
        assert len(structure["key_directories"]) >= 5, "应该检测到至少 5 个关键目录"
        assert len(structure["entry_files"]) >= 3, "应该检测到至少 3 个入口文件"
        assert "React" in tech_stack["frontend"], "应该检测到 React"
        print("\n✅ 测试通过")


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "P0.2 项目结构分析器 - 快速验证".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    try:
        test_current_project()
        test_python_project()
        test_nodejs_project()
        test_fullstack_project()

        print_header("✅ 所有测试通过！")
        print("\n🎉 P0.2 项目结构分析器功能验证完成！\n")
        print("📚 更多信息:")
        print("   - 单元测试: python3 tests/test_project_structure_analyzer.py")
        print("   - 集成测试: python3 tests/test_p0_2_integration.py")
        print("   - 命令行使用: python3 project_structure_analyzer.py /path/to/project")
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

