#!/usr/bin/env python3
"""
Prompt Enhancement v2.0.0 - 推送到 GitHub 脚本（Python 版本）

用途：跨平台推送所有代码和标签到 GitHub
使用方法：python3 push_to_github.py

该脚本将执行以下操作：
1. 验证 Git 环境
2. 检查前置条件
3. 推送 main 分支到 GitHub
4. 推送 v2.0.0 标签到 GitHub
5. 验证推送结果并提供 GitHub 链接
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Tuple, Optional

# 颜色定义（ANSI）
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @staticmethod
    def disable_if_windows():
        """Windows 不支持 ANSI 颜色，需要禁用"""
        if sys.platform == 'win32':
            for attr in dir(Colors):
                if not attr.startswith('_') and attr != 'disable_if_windows':
                    setattr(Colors, attr, '')


def run_command(cmd: list, description: str = "") -> Tuple[bool, str]:
    """执行 git 命令并返回结果"""
    try:
        if description:
            print(f"   {description}...", end=" ", flush=True)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            if description:
                print(f"{Colors.GREEN}✅{Colors.END}")
            return True, result.stdout.strip()
        else:
            if description:
                print(f"{Colors.RED}❌{Colors.END}")
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        if description:
            print(f"{Colors.RED}❌ (超时){Colors.END}")
        return False, "命令执行超时"
    except Exception as e:
        if description:
            print(f"{Colors.RED}❌ (异常){Colors.END}")
        return False, str(e)


def check_git_installed() -> bool:
    """检查 Git 是否已安装"""
    success, _ = run_command(['git', '--version'], "检查 Git 安装")
    return success


def check_git_repo() -> bool:
    """检查当前目录是否是 Git 仓库"""
    try:
        subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            check=True
        )
        return True
    except:
        return False


def get_git_config(key: str) -> str:
    """获取 Git 配置值"""
    _, value = run_command(['git', 'config', '--get', key])
    return value


def get_current_branch() -> str:
    """获取当前分支"""
    _, branch = run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    return branch


def check_working_tree_clean() -> bool:
    """检查工作目录是否干净"""
    _, status = run_command(['git', 'status', '--porcelain'])
    return len(status) == 0


def get_remote_url() -> str:
    """获取远程仓库 URL"""
    _, url = run_command(['git', 'remote', 'get-url', 'origin'])
    return url


def show_unpushed_commits(branch: str) -> str:
    """显示待推送的提交"""
    _, commits = run_command(['git', 'log', '--oneline', f'origin/{branch}..HEAD'])
    return commits or "（通过 git log 检查）"


def tag_exists(tag: str) -> bool:
    """检查标签是否存在"""
    success, _ = run_command(['git', 'tag', '-l', tag])
    return success


def push_branch(branch: str) -> bool:
    """推送分支"""
    print(f"{Colors.YELLOW}📤 第 1/2 步：推送 {branch} 分支...{Colors.END}")
    success, output = run_command(['git', 'push', 'origin', branch])

    if success:
        print(f"{Colors.GREEN}✅ {branch} 分支推送成功{Colors.END}")
        return True
    else:
        print(f"{Colors.RED}❌ {branch} 分支推送失败{Colors.END}")
        print(f"{Colors.RED}错误信息：{output}{Colors.END}")
        print()
        print("常见原因：")
        print("  1. 网络连接失败 - 检查网络连接")
        print("  2. 认证失败 - 检查 GitHub token 配置")
        print("  3. 权限不足 - 检查是否有 push 权限")
        print("  4. 分支保护规则 - 检查 GitHub 保护规则")
        return False


def push_tag(tag: str) -> bool:
    """推送标签"""
    print(f"{Colors.YELLOW}📤 第 2/2 步：推送 {tag} 标签...{Colors.END}")
    success, output = run_command(['git', 'push', 'origin', tag])

    if success:
        print(f"{Colors.GREEN}✅ {tag} 标签推送成功{Colors.END}")
        return True
    else:
        print(f"{Colors.RED}❌ {tag} 标签推送失败{Colors.END}")
        print(f"{Colors.RED}错误信息：{output}{Colors.END}")
        print()
        print("可能原因：")
        print("  1. 标签已存在 - 使用 git push origin :refs/tags/v2.0.0 删除后重试")
        print("  2. 权限不足 - 检查是否有标签 push 权限")
        return False


def verify_push(branch: str, tag: str) -> None:
    """验证推送结果"""
    print(f"{Colors.YELLOW}🔍 验证推送结果...{Colors.END}")
    print()

    # 验证 1
    print("验证 1：检查本地与远程同步")
    run_command(['git', 'status'])
    print()

    # 验证 2
    print("验证 2：检查远程分支最新提交")
    run_command(['git', 'log', f'origin/{branch}', '--oneline', '-3'])
    print()

    # 验证 3
    print("验证 3：检查远程标签")
    success, output = run_command(['git', 'ls-remote', '--tags', 'origin'])
    if tag in output:
        print(f"{Colors.GREEN}✅ {tag} 标签已推送到远程{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️  {tag} 标签未在远程仓库中找到{Colors.END}")


def show_github_links(owner: str, repo: str, branch: str, tag: str) -> None:
    """显示 GitHub 链接"""
    print()
    print(f"{Colors.BLUE}📍 请访问以下链接确认推送结果：{Colors.END}")
    print()
    print("1️⃣  提交历史：")
    print(f"   🔗 https://github.com/{owner}/{repo}/commits/{branch}")
    print()
    print("2️⃣  版本标签：")
    print(f"   🔗 https://github.com/{owner}/{repo}/tags")
    print()
    print("3️⃣  版本标签详情：")
    print(f"   🔗 https://github.com/{owner}/{repo}/releases/tag/{tag}")
    print()


def show_next_steps(owner: str, repo: str) -> None:
    """显示后续步骤"""
    print(f"{Colors.BLUE}📋 下一步操作：{Colors.END}")
    print()
    print("1. 创建 GitHub Release（推荐）")
    print(f"   访问：https://github.com/{owner}/{repo}/releases/new")
    print("   选择 v2.0.0 标签，添加 Release Notes")
    print()
    print("2. 发布到 PyPI")
    print("   cd packages/python/")
    print("   twine upload dist/*")
    print()
    print("3. 发布到 NPM")
    print("   cd packages/npm/")
    print("   npm login")
    print("   npm publish")
    print()
    print("4. 更新项目元数据")
    print("   在 GitHub 项目设置中添加话题标签和描述")
    print()


def main():
    """主函数"""
    Colors.disable_if_windows()

    # 显示头部
    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.BLUE}║   Prompt Enhancement v2.0.0 - 推送到 GitHub              ║{Colors.END}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════╝{Colors.END}")
    print()

    # ========================================================================
    # 检查前置条件
    # ========================================================================
    print(f"{Colors.YELLOW}🔍 前置条件检查：{Colors.END}")

    # 检查 Git
    if not check_git_installed():
        print(f"{Colors.RED}❌ 错误：未找到 Git，请先安装 Git{Colors.END}")
        sys.exit(1)

    # 检查仓库
    if not check_git_repo():
        print(f"{Colors.RED}❌ 错误：当前目录不是 Git 仓库{Colors.END}")
        sys.exit(1)

    # 获取基本信息
    current_branch = get_current_branch()
    user_name = get_git_config('user.name')
    user_email = get_git_config('user.email')
    remote_url = get_remote_url()

    print(f"   用户：{user_name} <{user_email}>")
    print(f"   分支：{current_branch}")
    print(f"   远程：{remote_url}")
    print()

    # 检查工作目录
    print(f"{Colors.YELLOW}📋 工作目录状态：{Colors.END}")
    if check_working_tree_clean():
        print("   ✅ 工作目录干净（无未提交更改）")
    else:
        print(f"   {Colors.RED}❌ 工作目录有未提交的更改{Colors.END}")
        print()
        run_command(['git', 'status'])
        print()
        print(f"{Colors.RED}请先提交所有更改后再推送{Colors.END}")
        sys.exit(1)

    print()

    # ========================================================================
    # 显示待推送内容
    # ========================================================================
    print(f"{Colors.YELLOW}📤 待推送内容：{Colors.END}")

    commits = show_unpushed_commits(current_branch)
    print(f"   提交：{commits}")

    if tag_exists('v2.0.0'):
        print("   标签：✅ v2.0.0")
    else:
        print("   标签：❌ v2.0.0 不存在")

    print()

    # ========================================================================
    # 用户确认
    # ========================================================================
    print(f"{Colors.BLUE}是否确认推送到 GitHub?{Colors.END}")
    confirm = input("请输入 'yes' 或 'y' 确认 (其他任何键取消): ").lower()

    if confirm not in ['yes', 'y']:
        print(f"{Colors.YELLOW}操作已取消{Colors.END}")
        sys.exit(0)

    print()
    print(f"{Colors.BLUE}🚀 开始推送...{Colors.END}")
    print()
    print(f"{Colors.BLUE}════════════════════════════════════════════════════════════{Colors.END}")
    print()

    # ========================================================================
    # 推送操作
    # ========================================================================
    if not push_branch(current_branch):
        sys.exit(1)

    print()

    if not push_tag('v2.0.0'):
        sys.exit(1)

    print()
    print(f"{Colors.BLUE}════════════════════════════════════════════════════════════{Colors.END}")

    # ========================================================================
    # 验证
    # ========================================================================
    print()
    verify_push(current_branch, 'v2.0.0')

    # ========================================================================
    # 显示结果和链接
    # ========================================================================
    print()
    print(f"{Colors.GREEN}════════════════════════════════════════════════════════════{Colors.END}")
    print(f"{Colors.GREEN}✅ 推送完成！{Colors.END}")
    print(f"{Colors.GREEN}════════════════════════════════════════════════════════════{Colors.END}")

    show_github_links('jodykwong', 'Prompt-Enhancement', current_branch, 'v2.0.0')

    show_next_steps('jodykwong', 'Prompt-Enhancement')

    print(f"{Colors.BLUE}════════════════════════════════════════════════════════════{Colors.END}")
    print()
    print(f"{Colors.GREEN}🎉 v2.0.0 已成功推送到 GitHub！{Colors.END}")
    print()
    print("提示：如需查看详细的发布说明，请阅读 RELEASE_COMMANDS.md 文件")
    print()


if __name__ == '__main__':
    main()
