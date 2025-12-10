#!/usr/bin/env python3
"""
P0.4 快速验证脚本

验证上下文收集器的功能：
1. 当前项目分析
2. Python 项目分析（模拟）
3. Node.js 项目分析（模拟）
4. 完整上下文收集
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from context_collector import collect_project_context


def test_current_project():
    """测试当前项目分析"""
    print("\n" + "=" * 70)
    print("  测试 1: 当前项目分析")
    print("=" * 70)

    context = collect_project_context(".")
    print(f"\n📁 项目路径: .")
    print(f"🔧 技术栈: {context['tech_stack']['backend'] or context['tech_stack']['frontend'] or '未检测'}")
    print(f"📂 关键目录: {', '.join(context['project_structure']['key_directories'][:3]) or '无'}")
    print(f"📝 摘要: {context['summary']}")
    print(f"\n✅ 测试通过")


def test_python_project():
    """测试 Python 项目分析"""
    print("\n" + "=" * 70)
    print("  测试 2: Python 项目分析（模拟）")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建 Python 项目
        Path(tmpdir, "src").mkdir()
        Path(tmpdir, "tests").mkdir()
        Path(tmpdir, "main.py").write_text("print('hello')")
        Path(tmpdir, "requirements.txt").write_text("django==4.0\nrequests==2.28.0")
        Path(tmpdir, "setup.py").write_text("from setuptools import setup\nsetup(name='test')")

        # 初始化 Git 仓库
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial Python project"], cwd=tmpdir, capture_output=True)

        context = collect_project_context(tmpdir)
        print(f"\n📁 项目路径: {tmpdir}")
        print(f"🔧 技术栈:")
        if context["tech_stack"]["backend"]:
            print(f"   后端: {', '.join(context['tech_stack']['backend'])}")
        if context["tech_stack"]["frontend"]:
            print(f"   前端: {', '.join(context['tech_stack']['frontend'])}")
        print(f"📂 关键目录: {', '.join(context['project_structure']['key_directories'])}")
        print(f"📝 摘要: {context['summary']}")
        print(f"\n✅ 测试通过")


def test_nodejs_project():
    """测试 Node.js 项目分析"""
    print("\n" + "=" * 70)
    print("  测试 3: Node.js 项目分析（模拟）")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建 Node.js 项目
        Path(tmpdir, "src").mkdir()
        Path(tmpdir, "tests").mkdir()
        Path(tmpdir, "index.js").write_text("console.log('hello')")
        Path(tmpdir, "package.json").write_text(
            '{"name": "test", "dependencies": {"react": "^18.0.0", "express": "^4.18.0"}}'
        )

        # 初始化 Git 仓库
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial Node.js project"], cwd=tmpdir, capture_output=True)

        context = collect_project_context(tmpdir)
        print(f"\n📁 项目路径: {tmpdir}")
        print(f"🔧 技术栈:")
        if context["tech_stack"]["backend"]:
            print(f"   后端: {', '.join(context['tech_stack']['backend'])}")
        if context["tech_stack"]["frontend"]:
            print(f"   前端: {', '.join(context['tech_stack']['frontend'])}")
        print(f"📂 关键目录: {', '.join(context['project_structure']['key_directories'])}")
        print(f"📝 摘要: {context['summary']}")
        print(f"\n✅ 测试通过")


def test_full_context_string():
    """测试完整上下文字符串"""
    print("\n" + "=" * 70)
    print("  测试 4: 完整上下文字符串")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建完整项目
        Path(tmpdir, "src").mkdir()
        Path(tmpdir, "tests").mkdir()
        Path(tmpdir, "main.py").write_text("print('hello')")
        Path(tmpdir, "requirements.txt").write_text("django==4.0")
        Path(tmpdir, "package.json").write_text('{"name": "test", "dependencies": {"react": "^18.0.0"}}')

        # 初始化 Git 仓库
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=tmpdir, capture_output=True)

        context = collect_project_context(tmpdir)
        print(f"\n📁 项目路径: {tmpdir}")
        print(f"\n📄 格式化上下文字符串:")
        print(context["context_string"])
        print(f"\n✅ 测试通过")


if __name__ == "__main__":
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  P0.4 上下文收集器 - 快速验证".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    try:
        test_current_project()
        test_python_project()
        test_nodejs_project()
        test_full_context_string()

        print("\n" + "=" * 70)
        print("  ✅ 所有测试通过！")
        print("=" * 70)
        print("\n📚 更多信息:")
        print("   - 单元测试: python3 tests/test_context_collector.py")
        print("   - 集成测试: python3 tests/test_p0_4_integration.py")
        print("   - 命令行使用: python3 context_collector.py /path/to/project")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

