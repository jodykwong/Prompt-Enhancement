#!/usr/bin/env python3
"""
Command-line interface for Prompt Enhancement

提供三个主要命令：
1. prompt-enhance-install - 安装到目标项目
2. prompt-enhance-setup - 交互式配置（API 密钥等）
3. prompt-enhance-verify - 验证安装状态
"""

import sys
import os
from pathlib import Path
from typing import Optional
import logging

from .installer import PromptEnhancementInstaller, InstallationError

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)
logger = logging.getLogger(__name__)


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"🚀 {title}")
    print("=" * 70)


def print_footer():
    """打印页脚"""
    print("=" * 70 + "\n")


def install_command():
    """
    prompt-enhance-install 命令
    用法: prompt-enhance-install [project_path]
    """
    target = sys.argv[1] if len(sys.argv) > 1 else None

    print_header("提示词增强功能安装程序")

    try:
        installer = PromptEnhancementInstaller(target)
        success, message = installer.install()
        print_footer()

        return 0 if success else 1

    except Exception as e:
        print(f"❌ 错误: {e}")
        print_footer()
        return 1


def setup_command():
    """
    prompt-enhance-setup 命令
    交互式配置 API 密钥和环境变量
    """
    print_header("提示词增强功能配置向导")

    project_dir = Path.cwd()
    env_file = project_dir / ".env"

    print(f"\n📂 项目目录: {project_dir}")
    print(f"📄 配置文件: {env_file}")

    # 检查 .env 是否存在
    if env_file.exists():
        print("\n✓ .env 文件已存在")
    else:
        print("\n⚠️  .env 文件不存在")

    # 交互式配置 API 密钥
    print("\n" + "-" * 70)
    print("🔑 DeepSeek API 密钥配置")
    print("-" * 70)

    print("\n请获取您的 API 密钥:")
    print("1. 访问 https://platform.deepseek.com")
    print("2. 登录或注册账户")
    print("3. 创建 API 密钥")
    print("4. 复制密钥")

    api_key = input("\n请输入您的 DeepSeek API 密钥 (留空跳过): ").strip()

    if api_key:
        # 更新或创建 .env 文件
        env_content = ""
        if env_file.exists():
            with open(env_file, "r") as f:
                env_content = f.read()

        # 更新或添加 DEEPSEEK_API_KEY
        if "DEEPSEEK_API_KEY=" in env_content:
            env_content = env_content.replace(
                env_content.split("DEEPSEEK_API_KEY=")[0] + "DEEPSEEK_API_KEY=" +
                env_content.split("DEEPSEEK_API_KEY=")[1].split("\n")[0],
                f"DEEPSEEK_API_KEY={api_key}"
            )
        else:
            env_content += f"\nDEEPSEEK_API_KEY={api_key}\n"

        with open(env_file, "w") as f:
            f.write(env_content)

        print(f"\n✅ API 密钥已保存到 {env_file}")
    else:
        print("\n⏭️  跳过 API 密钥配置")
        print("   您可以稍后编辑 .env 文件手动添加")

    # 验证安装
    print("\n" + "-" * 70)
    print("✔️  验证安装")
    print("-" * 70)

    installer = PromptEnhancementInstaller(str(project_dir))
    try:
        installer.verify_installation()
    except Exception:
        pass

    print("\n" + "-" * 70)
    print("✅ 配置完成！")
    print("-" * 70)
    print("\n📝 下一步:")
    print("  输入 /pe 您的提示词 来测试功能")
    print_footer()

    return 0


def verify_command():
    """
    prompt-enhance-verify 命令
    检查安装状态并诊断问题
    """
    print_header("提示词增强功能检查")

    project_dir = Path.cwd()
    claude_dir = project_dir / ".claude"
    commands_dir = claude_dir / "commands"
    env_file = project_dir / ".env"

    print(f"\n📂 项目目录: {project_dir}\n")

    checks = {
        ".claude 目录": claude_dir,
        ".claude/commands 目录": commands_dir,
        "pe.md 命令": commands_dir / "pe.md",
        "enhance.py 脚本": commands_dir / "scripts" / "enhance.py",
        ".env 文件": env_file,
    }

    print("检查清单:")
    print("-" * 70)

    all_passed = True
    for check_name, path in checks.items():
        if path.exists():
            size = path.stat().st_size if path.is_file() else "-"
            print(f"  ✅ {check_name:<30} {path}")
        else:
            print(f"  ❌ {check_name:<30} {path} (缺失)")
            all_passed = False

    # 检查环境变量
    print("\n环境变量:")
    print("-" * 70)

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        masked_key = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "****"
        print(f"  ✅ DEEPSEEK_API_KEY 已设置: {masked_key}")
    else:
        print(f"  ⚠️  DEEPSEEK_API_KEY 未设置")
        if env_file.exists():
            with open(env_file, "r") as f:
                if "DEEPSEEK_API_KEY=" in f.read():
                    print("      (在 .env 文件中存在，但未加载)")
        all_passed = False

    # 检查 Python 依赖
    print("\nPython 依赖:")
    print("-" * 70)

    dependencies = ["openai", "dotenv"]
    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            print(f"  ✅ {dep} 已安装")
        except ImportError:
            print(f"  ❌ {dep} 未安装")
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("✅ 所有检查通过！/pe 命令已准备好使用")
    else:
        print("⚠️  有些检查失败，请运行以下命令修复:")
        print("  1. 重新安装: prompt-enhance-install")
        print("  2. 配置环境: prompt-enhance-setup")
        print("  3. 安装依赖: pip install -r requirements.txt")
    print("=" * 70 + "\n")

    return 0 if all_passed else 1


def main():
    """主入口点"""
    if len(sys.argv) < 2:
        print_header("提示词增强功能 - 使用帮助")
        print("""
可用命令:

  prompt-enhance-install [path]
    在指定项目中安装 /pe 命令
    示例: prompt-enhance-install /path/to/xlerobot

  prompt-enhance-setup
    交互式配置 DeepSeek API 密钥

  prompt-enhance-verify
    检查安装状态和诊断问题

示例:
  # 在当前项目中安装
  prompt-enhance-install

  # 在其他项目中安装
  prompt-enhance-install ~/projects/xlerobot

  # 配置 API 密钥
  prompt-enhance-setup

  # 验证安装
  prompt-enhance-verify

更多信息: https://github.com/jodykwong/Prompt-Enhancement
        """)
        print_footer()
        return 0

    command = sys.argv[1]

    if command in ["install", "-i", "--install"]:
        return install_command()
    elif command in ["setup", "-s", "--setup"]:
        return setup_command()
    elif command in ["verify", "-v", "--verify"]:
        return verify_command()
    elif command in ["help", "-h", "--help"]:
        return main()
    else:
        print(f"❌ 未知命令: {command}")
        print("运行 prompt-enhance-install --help 查看帮助")
        return 1


if __name__ == "__main__":
    sys.exit(main())
