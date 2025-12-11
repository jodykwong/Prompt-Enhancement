#!/usr/bin/env python3
"""
Installation and Deployment Module for Prompt Enhancement

Handles:
1. 检测目标项目的 .claude 目录
2. 创建/验证必要的目录结构
3. 安装 /pe 命令和所有依赖
4. 配置环境变量
5. 验证部署成功
"""

import os
import sys
import shutil
import json
from pathlib import Path
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class InstallationError(Exception):
    """安装失败异常"""
    pass


class PromptEnhancementInstaller:
    """提示词增强功能的安装程序"""

    def __init__(self, target_project: Optional[str] = None):
        """
        初始化安装程序

        Args:
            target_project: 目标项目路径。如果为 None，使用当前目录
        """
        self.target_project = Path(target_project or os.getcwd()).resolve()
        self.claude_dir = self.target_project / ".claude"
        self.commands_dir = self.claude_dir / "commands"
        self.hooks_dir = self.claude_dir / "hooks"
        self.package_root = Path(__file__).parent.parent.resolve()

        # 获取源项目根目录 (项目根的 packages/python 的上上级)
        self.source_root = self.package_root.parent.parent

    def validate_target_project(self) -> bool:
        """验证目标项目有效性"""
        if not self.target_project.exists():
            raise InstallationError(
                f"❌ 目标项目路径不存在: {self.target_project}"
            )

        # 检查是否看起来像一个项目目录
        # （有 .git, src, package.json, etc.）
        indicators = [".git", "src", "package.json", "setup.py", "README.md"]
        has_indicator = any(
            (self.target_project / indicator).exists()
            for indicator in indicators
        )

        if not has_indicator:
            print(f"⚠️  警告: {self.target_project} 可能不是一个有效的项目目录")
            print("   （缺少 .git, src, package.json 等标准文件）")

        return True

    def setup_directory_structure(self) -> bool:
        """设置必要的目录结构"""
        print("📁 设置目录结构...")

        try:
            self.claude_dir.mkdir(parents=True, exist_ok=True)
            self.commands_dir.mkdir(parents=True, exist_ok=True)
            self.hooks_dir.mkdir(parents=True, exist_ok=True)
            print(f"   ✓ 创建 .claude/commands")
            print(f"   ✓ 创建 .claude/hooks")
            return True
        except Exception as e:
            raise InstallationError(f"无法创建目录结构: {e}")

    def install_pe_command(self) -> bool:
        """安装 /pe 命令"""
        print("📝 安装 /pe 命令...")

        try:
            # 查找源 pe.md 文件
            source_pe = self.source_root / ".claude" / "commands" / "pe.md"

            if not source_pe.exists():
                raise InstallationError(
                    f"❌ 找不到源 /pe 命令文件: {source_pe}"
                )

            target_pe = self.commands_dir / "pe.md"

            # 优先使用符号链接（如果支持）
            if target_pe.exists() or target_pe.is_symlink():
                target_pe.unlink()

            try:
                # 尝试创建符号链接
                target_pe.symlink_to(source_pe)
                print(f"   ✓ 创建符号链接: {target_pe} -> {source_pe}")
            except (OSError, NotImplementedError):
                # 如果符号链接失败（例如 Windows 或权限问题），使用文件复制
                shutil.copy2(source_pe, target_pe)
                print(f"   ✓ 复制文件: {source_pe} -> {target_pe}")

            return True
        except Exception as e:
            raise InstallationError(f"无法安装 /pe 命令: {e}")

    def install_support_scripts(self) -> bool:
        """安装支持脚本和模块"""
        print("🔧 安装支持脚本...")

        try:
            # 复制 Python 模块
            source_scripts = self.source_root / ".claude" / "commands" / "scripts"
            target_scripts = self.commands_dir / "scripts"

            if source_scripts.exists():
                if target_scripts.exists():
                    shutil.rmtree(target_scripts)
                shutil.copytree(source_scripts, target_scripts)
                print(f"   ✓ 复制脚本目录")

            # 复制根目录的核心 Python 模块
            core_modules = [
                "enhanced_prompt_generator.py",
                "async_prompt_enhancer.py",
                "context_collector.py",
            ]

            for module in core_modules:
                source_module = self.source_root / module
                target_module = self.commands_dir / module

                if source_module.exists():
                    shutil.copy2(source_module, target_module)
                    print(f"   ✓ 复制模块: {module}")

            return True
        except Exception as e:
            raise InstallationError(f"无法安装支持脚本: {e}")

    def setup_environment_file(self) -> bool:
        """设置 .env 文件"""
        print("🔑 配置环境变量...")

        try:
            env_file = self.target_project / ".env"
            env_example = self.source_root / ".env.example"

            # 如果 .env 不存在，从 .env.example 创建
            if not env_file.exists():
                if env_example.exists():
                    shutil.copy2(env_example, env_file)
                    print(f"   ✓ 从 .env.example 创建 .env")
                else:
                    # 创建最小的 .env
                    env_content = "# DeepSeek API 配置\nDEEPSEEK_API_KEY=your_api_key_here\n"
                    with open(env_file, "w") as f:
                        f.write(env_content)
                    print(f"   ✓ 创建最小 .env 文件")
            else:
                print(f"   ✓ .env 文件已存在")

            return True
        except Exception as e:
            raise InstallationError(f"无法设置 .env 文件: {e}")

    def verify_installation(self) -> bool:
        """验证安装"""
        print("✔️  验证安装...")

        checks = {
            "pe.md 命令": self.commands_dir / "pe.md",
            "enhance.py 脚本": self.commands_dir / "scripts" / "enhance.py",
            ".env 文件": self.target_project / ".env",
        }

        all_passed = True
        for check_name, path in checks.items():
            if path.exists():
                print(f"   ✓ {check_name}: {path}")
            else:
                print(f"   ⚠️  {check_name}: 未找到 {path}")
                all_passed = False

        return all_passed

    def install(self) -> Tuple[bool, str]:
        """
        执行完整的安装流程

        Returns:
            (成功, 消息)
        """
        try:
            print("\n" + "=" * 70)
            print("🚀 提示词增强功能安装程序")
            print("=" * 70)
            print(f"📂 目标项目: {self.target_project}\n")

            self.validate_target_project()
            self.setup_directory_structure()
            self.install_pe_command()
            self.install_support_scripts()
            self.setup_environment_file()
            is_valid = self.verify_installation()

            print("\n" + "=" * 70)
            if is_valid:
                print("✅ 安装完成！")
                print("=" * 70)
                print("\n📝 后续步骤：")
                print("1️⃣  配置 DeepSeek API 密钥:")
                print(f"   编辑 {self.target_project / '.env'}")
                print("   设置 DEEPSEEK_API_KEY=your-key-here")
                print("\n2️⃣  测试功能:")
                print("   /pe 修复登录页面的bug")
                print("\n3️⃣  获取更多帮助:")
                print("   查看 /pe 命令的使用文档")
                return True, "安装成功"
            else:
                print("⚠️  安装完成，但有些文件缺失")
                print("=" * 70)
                return True, "安装完成（有警告）"

        except InstallationError as e:
            print("\n" + "=" * 70)
            print(f"❌ 安装失败: {e}")
            print("=" * 70)
            return False, str(e)
        except Exception as e:
            print("\n" + "=" * 70)
            print(f"❌ 出现意外错误: {e}")
            print("=" * 70)
            return False, f"意外错误: {e}"


def install_pe(target_project: Optional[str] = None) -> bool:
    """
    便捷函数：安装提示词增强功能

    Args:
        target_project: 目标项目路径

    Returns:
        安装是否成功
    """
    installer = PromptEnhancementInstaller(target_project)
    success, message = installer.install()
    return success


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else None
    success = install_pe(target)
    sys.exit(0 if success else 1)
