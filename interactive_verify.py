#!/usr/bin/env python3
"""
交互式验证脚本 - 支持自定义提示词和上下文补充验证

功能：
1. 交互式输入自定义提示词
2. 显示思考过程和增强结果
3. 验证上下文补充效果
4. 支持多次连续测试
5. 输入历史记录

使用方式：
python interactive_verify.py
"""

import sys
import time
from dotenv import load_dotenv
from prompt_enhancer import PromptEnhancer, print_result

# 加载 .env 文件中的环境变量
load_dotenv()


# ✅ 添加非交互模式检测
def check_interactive_mode():
    """检测是否在交互式环境中运行"""
    if not sys.stdin.isatty():
        print("⚠️  检测到非交互环境，此脚本需要在交互式终端中运行")
        print("提示：请在交互式终端中运行此脚本，例如：")
        print("  python3 interactive_verify.py")
        sys.exit(0)


def verify_context_supplement(enhanced_prompt: str) -> dict:
    """
    验证上下文补充效果
    
    Args:
        enhanced_prompt: 增强后的提示词
        
    Returns:
        包含验证结果的字典
    """
    context_items = {
        "代码仓库结构": ["src/", "components/", "utils/", "api/", "tests/"],
        "技术栈信息": ["React", "Vue", "Node.js", "Django", "FastAPI", "bcrypt", "Redis", "JWT"],
        "文件路径": ["RegisterForm", "/api/", "src/", "utils/", "components/"],
        "依赖关系": ["bcrypt", "Redis", "JWT", "库", "安装", "依赖"]
    }
    
    found_items = {}
    for category, keywords in context_items.items():
        found = [kw for kw in keywords if kw in enhanced_prompt]
        found_items[category] = found
    
    return found_items


def print_context_verification(context_items: dict):
    """打印上下文补充验证结果"""
    print(f"\n🔍 【上下文补充验证】")
    print(f"{'─'*80}")
    
    for category, found in context_items.items():
        if found:
            status = "✅"
            items_str = ", ".join(found)
        else:
            status = "❌"
            items_str = "未找到"
        print(f"  {status} {category}: {items_str}")
    
    print(f"{'─'*80}")


def print_header():
    """打印欢迎信息"""
    print("\n" + "="*80)
    print("  🔍 交互式验证脚本 - 自定义提示词测试")
    print("="*80)
    print("\n【功能说明】")
    print("  • 输入自定义的提示词进行增强")
    print("  • 查看模型的思考过程")
    print("  • 验证上下文补充效果")
    print("  • 查看详细的统计信息")
    print("\n【命令说明】")
    print("  • 输入提示词: 直接输入您的提示词")
    print("  • 输入 'quit' 或 'exit': 退出程序")
    print("  • 输入 'history': 查看输入历史")
    print("  • 输入 'help': 显示帮助信息")
    print("\n【处理时间】")
    print("  • 每次增强需要 30-40 秒（DeepSeek 推理模式）")
    print("\n" + "="*80 + "\n")


def print_help():
    """打印帮助信息"""
    print("\n【帮助信息】")
    print("  quit/exit/q: 退出程序")
    print("  history: 查看输入历史")
    print("  help: 显示此帮助信息")
    print("  clear: 清空输入历史")
    print("\n【示例提示词】")
    print("  • 修复bug")
    print("  • 添加用户注册功能")
    print("  • 重构代码")
    print("  • 优化数据库查询")
    print("  • 实现 API 端点")
    print()


def main():
    """主函数"""
    # ✅ 检测是否在交互式环境中运行
    check_interactive_mode()

    try:
        enhancer = PromptEnhancer()
        print("✓ PromptEnhancer 初始化成功")
    except ValueError as e:
        print(f"❌ 错误: {e}")
        print("\n请确保已设置 DEEPSEEK_API_KEY 环境变量")
        return 1

    print_header()
    
    # 询问是否显示思考过程
    show_reasoning_input = input("是否显示模型的思考过程？(y/n，默认 y): ").strip().lower()
    show_reasoning = show_reasoning_input != 'n'
    
    # 输入历史记录
    history = []
    test_count = 0
    
    while True:
        print("\n" + "─"*80)
        print(f"【测试 #{test_count + 1}】请输入待增强的提示词")
        print("(输入 'quit' 退出, 'help' 查看帮助, 'history' 查看历史):")
        user_input = input("> ").strip()
        
        # 处理特殊命令
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 感谢使用交互式验证脚本！")
            print(f"📊 本次会话共进行了 {test_count} 次测试")
            break
        
        if user_input.lower() == 'help':
            print_help()
            continue
        
        if user_input.lower() == 'history':
            if history:
                print("\n【输入历史】")
                for i, prompt in enumerate(history, 1):
                    print(f"  {i}. {prompt}")
            else:
                print("\n⚠️  暂无输入历史")
            continue
        
        if user_input.lower() == 'clear':
            history.clear()
            print("\n✓ 输入历史已清空")
            continue
        
        if not user_input:
            print("⚠️  请输入有效的提示词")
            continue
        
        # 保存到历史记录
        history.append(user_input)
        
        # 增强提示词
        print("\n⏳ 正在增强提示词，请稍候...")
        print("   (DeepSeek 推理模式需要 30-40 秒)\n")
        
        result = enhancer.enhance(user_input)
        
        # 打印结果
        print_result(result, show_reasoning=show_reasoning)
        
        # 验证上下文补充
        if result['success']:
            context_items = verify_context_supplement(result['enhanced'])
            print_context_verification(context_items)
            
            # 统计上下文补充情况
            found_count = sum(1 for items in context_items.values() if items)
            total_count = len(context_items)
            print(f"\n📈 上下文补充覆盖率: {found_count}/{total_count} 类别")
        
        test_count += 1
        
        # 提示用户可以继续测试
        print("\n【下一步】")
        print("  ✓ 输入新的提示词继续测试")
        print("  ✓ 输入 'quit' 退出程序")
        print("  ✓ 输入 'history' 查看历史记录")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

