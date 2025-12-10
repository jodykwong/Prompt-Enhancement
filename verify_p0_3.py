#!/usr/bin/env python3
"""
P0.3 快速验证脚本

验证 Git 历史分析器的功能
"""

import sys
import json
import subprocess
import tempfile
from pathlib import Path
from tech_stack_detector import detect_tech_stack
from project_structure_analyzer import analyze_project_structure
from git_history_analyzer import analyze_git_history


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_git_result(result, project_path):
    """打印 Git 分析结果"""
    print(f"\n📁 项目路径: {project_path}\n")

    # 仓库状态
    print(f"📦 Git 仓库: {'是' if result['is_git_repo'] else '否'}")

    # 当前分支
    if result["current_branch"]:
        print(f"🌿 当前分支: {result['current_branch']}")

    # 最近提交
    if result["recent_commits"]:
        print(f"\n📝 最近提交 ({len(result['recent_commits'])} 条):")
        for commit in result["recent_commits"]:
            print(f"   • {commit['hash']} - {commit['message']}")
            print(f"     作者: {commit['author']} ({commit['date']})")

    # 活跃分支
    if result["active_branches"]:
        print(f"\n🌳 活跃分支: {', '.join(result['active_branches'][:5])}")

    # 修改文件
    if result["modified_files"]:
        print(f"\n📄 修改文件: {', '.join(result['modified_files'][:5])}")

    # 未提交更改
    print(f"\n⚠️  未提交更改: {'有' if result['has_uncommitted_changes'] else '无'}")


def test_current_project():
    """测试当前项目"""
    print_header("测试 1: 当前项目分析")

    result = analyze_git_history(".")
    print_git_result(result, ".")

    # 当前项目可能不是 Git 仓库，所以只检查返回值有效
    assert isinstance(result, dict), "应该返回字典"
    assert "is_git_repo" in result, "应该包含 is_git_repo 键"
    print("\n✅ 测试通过")


def test_python_project():
    """测试 Python 项目"""
    print_header("测试 2: Python 项目分析（模拟）")

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

        # 分析 Git 历史
        git_history = analyze_git_history(tmpdir)
        print_git_result(git_history, tmpdir)

        # 分析技术栈
        tech_stack = detect_tech_stack(tmpdir)
        print(f"\n🔧 技术栈:")
        print(f"   后端: {', '.join(tech_stack['backend']) if tech_stack['backend'] else '未检测到'}")

        # 分析项目结构
        project_structure = analyze_project_structure(tmpdir)
        print(f"\n📂 项目结构:")
        print(f"   关键目录: {', '.join(project_structure['key_directories'])}")

        # 验证结果
        assert git_history["is_git_repo"], "应该是 Git 仓库"
        assert len(git_history["recent_commits"]) > 0, "应该有提交记录"
        assert "Python" in tech_stack["backend"], "应该检测到 Python"
        print("\n✅ 测试通过")


def test_nodejs_project():
    """测试 Node.js 项目"""
    print_header("测试 3: Node.js 项目分析（模拟）")

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

        package_json = {
            "name": "node-app",
            "dependencies": {
                "react": "^18.0.0",
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

        # 分析 Git 历史
        git_history = analyze_git_history(tmpdir)
        print_git_result(git_history, tmpdir)

        # 分析技术栈
        tech_stack = detect_tech_stack(tmpdir)
        print(f"\n🔧 技术栈:")
        print(f"   前端: {', '.join(tech_stack['frontend']) if tech_stack['frontend'] else '未检测到'}")
        print(f"   后端: {', '.join(tech_stack['backend']) if tech_stack['backend'] else '未检测到'}")

        # 验证结果
        assert git_history["is_git_repo"], "应该是 Git 仓库"
        assert "React" in tech_stack["frontend"], "应该检测到 React"
        print("\n✅ 测试通过")


def test_uncommitted_changes():
    """测试未提交更改检测"""
    print_header("测试 4: 未提交更改检测（模拟）")

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
        git_history = analyze_git_history(tmpdir)
        print_git_result(git_history, tmpdir)

        # 验证结果
        assert git_history["has_uncommitted_changes"], "应该检测到未提交更改"
        assert len(git_history["modified_files"]) > 0, "应该检测到修改文件"
        print("\n✅ 测试通过")


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "P0.3 Git 历史分析器 - 快速验证".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    try:
        test_current_project()
        test_python_project()
        test_nodejs_project()
        test_uncommitted_changes()

        print_header("✅ 所有测试通过！")
        print("\n🎉 P0.3 Git 历史分析器功能验证完成！\n")
        print("📚 更多信息:")
        print("   - 单元测试: python3 tests/test_git_history_analyzer.py")
        print("   - 集成测试: python3 tests/test_p0_3_integration.py")
        print("   - 命令行使用: python3 git_history_analyzer.py /path/to/project")
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

