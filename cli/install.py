#!/usr/bin/env python3

"""
Prompt Enhancement - Cross-platform Installer

Usage:
    python3 install.py                      # Install to current directory
    python3 install.py /path/to/project     # Install to specific project
"""

import sys
import os
import shutil
from pathlib import Path
from typing import Tuple

class Colors:
    """ANSI 颜色代码"""
    RESET = '\033[0m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'

    @staticmethod
    def disable():
        """在 Windows 上禁用颜色"""
        Colors.RESET = ''
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''

# 在 Windows 上禁用颜色
if sys.platform.startswith('win'):
    Colors.disable()

class Installer:
    """提示词增强功能安装程序"""

    def __init__(self, target_project: str = None):
        """初始化安装程序"""
        self.target_project = Path(target_project or os.getcwd()).resolve()
        self.source_root = Path(__file__).parent.parent.resolve()

        self.claude_dir = self.target_project / '.claude'
        self.commands_dir = self.claude_dir / 'commands'
        self.hooks_dir = self.claude_dir / 'hooks'
        self.scripts_dir = self.commands_dir / 'scripts'
        self.env_file = self.target_project / '.env'

    def print_header(self):
        """打印标题"""
        print(f'\n{Colors.BLUE}{"="*80}{Colors.RESET}')
        print(f'{Colors.BLUE}🚀 Prompt Enhancement 安装程序{Colors.RESET}')
        print(f'{Colors.BLUE}{"="*80}{Colors.RESET}')
        print(f'\n📂 目标项目: {self.target_project}\n')

    def print_section(self, title: str):
        """打印段落标题"""
        print(f'\n{Colors.BLUE}▸ {title}{Colors.RESET}')

    def print_success(self, msg: str):
        """打印成功消息"""
        print(f'{Colors.GREEN}✓ {msg}{Colors.RESET}')

    def print_warning(self, msg: str):
        """打印警告消息"""
        print(f'{Colors.YELLOW}⚠️  {msg}{Colors.RESET}')

    def print_error(self, msg: str):
        """打印错误消息"""
        print(f'{Colors.RED}❌ {msg}{Colors.RESET}')

    def print_footer(self):
        """打印页脚"""
        print(f'\n{Colors.BLUE}{"="*80}{Colors.RESET}\n')

    def validate_target(self) -> bool:
        """验证目标项目"""
        self.print_section('验证目标项目')

        if not self.target_project.exists():
            self.print_error(f'目标项目不存在: {self.target_project}')
            return False

        self.print_success('项目路径有效')

        # 检查是否看起来像一个项目
        indicators = ['.git', 'package.json', 'setup.py', 'README.md', 'src']
        has_indicator = any(
            (self.target_project / ind).exists()
            for ind in indicators
        )

        if not has_indicator:
            self.print_warning('目标项目可能不是一个有效的项目目录')

        return True

    def setup_directories(self) -> bool:
        """设置目录结构"""
        self.print_section('设置目录结构')

        try:
            for dir_path in [self.claude_dir, self.commands_dir, self.hooks_dir, self.scripts_dir]:
                dir_path.mkdir(parents=True, exist_ok=True)

            self.print_success('创建目录: .claude/commands')
            self.print_success('创建目录: .claude/hooks')
            return True
        except Exception as e:
            self.print_error(f'无法创建目录: {e}')
            return False

    def install_pe_command(self) -> bool:
        """安装 /pe 命令"""
        self.print_section('安装 /pe 命令')

        source_pe = self.source_root / '.claude' / 'commands' / 'pe.md'
        target_pe = self.commands_dir / 'pe.md'

        if not source_pe.exists():
            self.print_error(f'找不到源 /pe 命令: {source_pe}')
            return False

        try:
            # 移除已存在的目标
            if target_pe.exists() or target_pe.is_symlink():
                target_pe.unlink()

            # 尝试创建符号链接
            try:
                target_pe.symlink_to(source_pe)
                self.print_success(f'创建符号链接: pe.md -> {source_pe}')
            except (OSError, NotImplementedError):
                # 如果符号链接失败，使用复制
                shutil.copy2(source_pe, target_pe)
                self.print_warning('使用文件复制（符号链接不支持）')
                self.print_success(f'复制文件: {source_pe}')

            return True
        except Exception as e:
            self.print_error(f'无法安装 /pe 命令: {e}')
            return False

    def install_support_scripts(self) -> bool:
        """安装支持脚本"""
        self.print_section('安装支持脚本')

        # 复制脚本目录
        source_scripts = self.source_root / '.claude' / 'commands' / 'scripts'
        if source_scripts.exists():
            try:
                if self.scripts_dir.exists():
                    shutil.rmtree(self.scripts_dir)
                shutil.copytree(source_scripts, self.scripts_dir)
                self.print_success('复制脚本目录')
            except Exception as e:
                self.print_warning(f'无法复制脚本目录: {e}')

        # 复制核心 Python 模块
        modules = [
            'enhanced_prompt_generator.py',
            'async_prompt_enhancer.py',
            'context_collector.py'
        ]

        for module in modules:
            source_module = self.source_root / module
            if source_module.exists():
                try:
                    shutil.copy2(source_module, self.commands_dir / module)
                    self.print_success(f'复制模块: {module}')
                except Exception as e:
                    self.print_warning(f'跳过: {module}')

        return True

    def setup_environment(self) -> bool:
        """设置 .env 文件"""
        self.print_section('配置环境变量')

        try:
            if not self.env_file.exists():
                # 尝试从 .env.example 复制
                source_env = self.source_root / '.env.example'
                if source_env.exists():
                    shutil.copy2(source_env, self.env_file)
                    self.print_success('从 .env.example 创建 .env')
                else:
                    # 创建最小的 .env
                    with open(self.env_file, 'w') as f:
                        f.write('# DeepSeek API 配置\n')
                        f.write('DEEPSEEK_API_KEY=your_api_key_here\n')
                    self.print_success('创建最小 .env 文件')
            else:
                self.print_success('.env 文件已存在')

            return True
        except Exception as e:
            self.print_error(f'无法设置 .env 文件: {e}')
            return False

    def verify_installation(self) -> bool:
        """验证安装"""
        self.print_section('验证安装')

        checks = {
            'pe.md': self.commands_dir / 'pe.md',
            'enhance.py': self.scripts_dir / 'enhance.py',
            '.env': self.env_file
        }

        all_ok = True
        for name, path in checks.items():
            if path.exists():
                self.print_success(f'{name} 已安装')
            else:
                self.print_warning(f'{name} 未找到')
                all_ok = False

        return all_ok

    def install(self) -> int:
        """执行安装"""
        self.print_header()

        try:
            if not self.validate_target():
                return 1
            if not self.setup_directories():
                return 1
            if not self.install_pe_command():
                return 1
            if not self.install_support_scripts():
                return 1
            if not self.setup_environment():
                return 1

            all_ok = self.verify_installation()

            self.print_footer()

            if all_ok:
                print(f'{Colors.GREEN}✅ 安装完成！{Colors.RESET}')
            else:
                print(f'{Colors.YELLOW}⚠️  安装完成，但有些文件缺失{Colors.RESET}')

            print('\n📝 后续步骤：\n')
            print('1️⃣  配置 DeepSeek API 密钥:')
            print(f'   编辑 {self.env_file}')
            print('   设置 DEEPSEEK_API_KEY=your-api-key-here\n')
            print('2️⃣  测试功能:')
            print('   在 Claude Code 中输入:')
            print('   /pe 修复登录页面的bug\n')
            print('3️⃣  获取更多帮助:')
            print('   https://github.com/jodykwong/Prompt-Enhancement')
            print('\n' + '='*80 + '\n')

            return 0

        except Exception as e:
            self.print_footer()
            self.print_error(f'安装失败: {e}')
            return 1


def main():
    """主入口"""
    target = sys.argv[1] if len(sys.argv) > 1 else None
    installer = Installer(target)
    return installer.install()


if __name__ == '__main__':
    sys.exit(main())
