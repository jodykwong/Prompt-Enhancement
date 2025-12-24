#!/usr/bin/env python3
"""
Prompt Enhancement Script for Claude Code
Version: 1.0.0 (P0.6)

Display-Only Mode: 此脚本只负责增强提示词并显示结果，不执行任何任务。
用户需要手动复制增强后的提示词并重新输入以执行。

Usage:
    python3 enhance.py "<prompt_text>"

Environment Variables:
    DEEPSEEK_API_KEY: Required. Your DeepSeek API key.

Output Format:
    成功时输出增强后的提示词到stdout
    错误时输出错误信息到stderr并返回exit code 1
"""

import sys
import os
import asyncio
from pathlib import Path

# ============================================================================
# 环境检查和依赖导入
# ============================================================================

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ Error: python-dotenv is not installed", file=sys.stderr)
    print("📦 Please run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

# 项目根目录 - 使用相对路径自动检测
# 优先使用 CLAUDE_PROJECT_DIR 环境变量（由 Claude Code 设置）
# 否则使用脚本所在位置的上级目录
if "CLAUDE_PROJECT_DIR" in os.environ:
    PROJECT_ROOT = Path(os.environ["CLAUDE_PROJECT_DIR"])
else:
    # 脚本路径: .claude/commands/scripts/enhance.py
    # 项目根目录应该是脚本所在位置的上上上级目录
    script_dir = Path(__file__).resolve().parent
    PROJECT_ROOT = script_dir.parent.parent.parent

if not PROJECT_ROOT.exists():
    print(f"❌ Error: Cannot find Prompt-Enhancement project at {PROJECT_ROOT}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Debug info:", file=sys.stderr)
    print(f"  Script dir: {Path(__file__).resolve().parent}", file=sys.stderr)
    print(f"  Detected PROJECT_ROOT: {PROJECT_ROOT}", file=sys.stderr)
    print(f"  CLAUDE_PROJECT_DIR: {os.environ.get('CLAUDE_PROJECT_DIR', 'Not set')}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Please set CLAUDE_PROJECT_DIR environment variable or ensure correct directory structure.", file=sys.stderr)
    sys.exit(1)

# 添加项目到Python路径
sys.path.insert(0, str(PROJECT_ROOT))

# 加载.env文件
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    print("⚠️  Warning: .env file not found", file=sys.stderr)
    print(f"Expected location: {env_file}", file=sys.stderr)
    print("", file=sys.stderr)

# 导入核心模块
try:
    from enhanced_prompt_generator import enhance_prompt_with_context
except ImportError as e:
    print(f"❌ Error: Cannot import enhanced_prompt_generator: {e}", file=sys.stderr)
    print("", file=sys.stderr)
    print(f"Project root: {PROJECT_ROOT}", file=sys.stderr)
    print(f"Python path: {sys.path[:3]}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Please ensure all P0.6 modules are available in the project directory.", file=sys.stderr)
    sys.exit(1)


# ============================================================================
# 验证和参数处理
# ============================================================================

def validate_environment():
    """验证环境变量配置"""
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        print("❌ Error: DEEPSEEK_API_KEY not configured", file=sys.stderr)
        print("", file=sys.stderr)
        print("🔑 Please set your DeepSeek API key:", file=sys.stderr)
        print("", file=sys.stderr)
        print("Option 1 - Add to .env file:", file=sys.stderr)
        print(f"  echo 'DEEPSEEK_API_KEY=your-api-key' >> {PROJECT_ROOT}/.env", file=sys.stderr)
        print("", file=sys.stderr)
        print("Option 2 - Set environment variable:", file=sys.stderr)
        print("  export DEEPSEEK_API_KEY='your-api-key'", file=sys.stderr)
        print("", file=sys.stderr)
        print("💡 Get your API key from: https://platform.deepseek.com", file=sys.stderr)
        return False

    return True


def parse_arguments():
    """解析命令行参数"""
    if len(sys.argv) < 2:
        print("❌ Error: No prompt provided", file=sys.stderr)
        print("", file=sys.stderr)
        print("Usage:", file=sys.stderr)
        print('  python3 enhance.py "your prompt text"', file=sys.stderr)
        print("", file=sys.stderr)
        print("Example:", file=sys.stderr)
        print('  python3 enhance.py "修复登录页面的bug"', file=sys.stderr)
        return None

    # 合并所有参数处理空格
    prompt = " ".join(sys.argv[1:])

    if not prompt.strip():
        print("❌ Error: Prompt is empty", file=sys.stderr)
        return None

    return prompt.strip()


# ============================================================================
# 核心增强功能
# ============================================================================

async def enhance_prompt(prompt: str) -> dict:
    """
    使用P0.6的完整功能增强提示词

    Args:
        prompt: 原始提示词

    Returns:
        包含增强结果的字典
    """
    try:
        # 使用P0.6的enhance_prompt_with_context
        # 它会自动收集项目上下文（如果在项目目录中运行）
        result = await enhance_prompt_with_context(
            prompt=prompt,
            project_path=str(PROJECT_ROOT),  # 可选：提供项目路径以收集上下文
            timeout=60
        )

        return result

    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": "API调用超时（60秒）。请检查网络连接或稍后重试。",
            "original": prompt,
            "enhanced": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"增强失败: {str(e)}",
            "original": prompt,
            "enhanced": None
        }


# ============================================================================
# 结果展示和菜单
# ============================================================================

def display_comparison(result: dict):
    """
    显示原始和增强后的提示词对比，提供菜单给用户选择

    Args:
        result: 增强结果字典
    """
    print("\n" + "=" * 70)
    print("📝 原始提示词")
    print("=" * 70)
    print(result['original'])

    print("\n" + "=" * 70)
    print("✨ 增强后的提示词")
    print("=" * 70)
    print(result['enhanced'])

    print("\n" + "=" * 70)
    print("🎯 请选择下一步操作")
    print("=" * 70)
    print("""
[1] ✅ 使用增强版本
    将上面的"增强后的提示词"复制粘贴给我，我会按增强版本执行

[2] 📝 修改后使用
    修改"增强后的提示词"，然后复制粘贴给我

[3] 🔄 重新增强
    输入新的提示词重新增强: /pe [新的提示词]

[4] ❌ 放弃此结果
    丢弃结果，重新组织需求
""")
    print("=" * 70)
    print("\n💡 提示：我现在停止，等待您的选择。请选择上面的选项之一。")


def display_error(error_message: str):
    """显示错误信息"""
    print("\n" + "=" * 70)
    print("❌ 增强失败")
    print("=" * 70)
    print(error_message)
    print("=" * 70)


# ============================================================================
# 主程序入口
# ============================================================================

async def main():
    """主函数"""
    # 验证环境
    if not validate_environment():
        sys.exit(1)

    # 解析参数
    prompt = parse_arguments()
    if prompt is None:
        sys.exit(1)

    # 增强提示词
    result = await enhance_prompt(prompt)

    # 输出结果
    if result['success']:
        # 显示对比和菜单（用户自主选择模式）
        display_comparison(result)

        # 关键：输出特殊的停止信号
        # 告诉 Claude Code 停止执行，等待用户的菜单选择
        print("\n" + "!" * 70)
        print("⏸️  STOP HERE - 请等待用户选择上面的菜单选项")
        print("!" * 70)
        print("\n❌ 不要执行原始提示词")
        print("❌ 不要执行任何自动任务")
        print("✅ 等待用户的选择")
        print("\n" + "!" * 70)

        # 等待用户输入选择（尝试从 stdin 读取）
        try:
            print("\n请输入选择 (1-4):")
            choice = input().strip()

            if choice == "1":
                print("\n✅ 请复制上面的'增强后的提示词'并粘贴给我重新执行")
            elif choice == "2":
                print("\n✅ 请修改'增强后的提示词'，然后粘贴给我")
            elif choice == "3":
                print("\n✅ 请输入新的提示词: /pe [新提示词]")
            elif choice == "4":
                print("\n✅ 已放弃此结果，您可以重新输入请求")
            else:
                print("\n❌ 无效选择，请输入 1-4")
        except EOFError:
            # 如果无法读取 stdin（非交互环境），只显示菜单
            print("\n（非交互环境，请根据菜单手动选择）")

        sys.exit(0)
    else:
        # 输出错误信息
        display_error(result['error'])
        sys.exit(1)


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
