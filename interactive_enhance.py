#!/usr/bin/env python3
"""
交互式提示词增强工具

这个脚本展示了如何正确使用提示词增强功能：
1. 接收用户输入的原始提示词
2. 调用 DeepSeek API 进行增强
3. 展示增强结果
4. 由用户决定如何使用增强后的提示词

**功能职责**：
- 只负责增强提示词
- 不执行增强后的提示词
- 不将增强后的提示词作为新指令发送给 AI

**使用方式**：
python interactive_enhance.py
"""

import sys
import time
from dotenv import load_dotenv
from prompt_enhancer import PromptEnhancer, print_result

# 加载 .env 文件中的环境变量
load_dotenv()


def main():
    """主函数 - 交互式增强"""
    print("\n" + "="*80)
    print("  🚀 提示词增强工具 - 交互式模式（优化版）")
    print("="*80)
    print("\n【功能说明】")
    print("  • 输入您的原始提示词")
    print("  • 系统将调用 DeepSeek API 进行增强")
    print("  • 展示模型的思考过程和增强结果")
    print("  • 您可以复制增强后的提示词用于其他用途")
    print("\n【优化特性】")
    print("  ✨ 展示 DeepSeek 模型的推理过程")
    print("  ✨ 生成简洁、实用的增强提示词")
    print("  ✨ 提供详细的统计信息")
    print("\n【重要提醒】")
    print("  • 增强后的提示词由您决定如何使用")
    print("  • 系统不会自动执行增强后的提示词")
    print("  • 处理时间约 30-40 秒（DeepSeek 思考模式）")
    print("\n" + "="*80 + "\n")

    try:
        enhancer = PromptEnhancer()
        print("✓ PromptEnhancer 初始化成功\n")
    except ValueError as e:
        print(f"❌ 错误: {e}")
        print("\n请确保已设置 DEEPSEEK_API_KEY 环境变量")
        return 1

    # 询问是否显示思考过程
    show_reasoning_input = input("是否显示模型的思考过程？(y/n，默认 y): ").strip().lower()
    show_reasoning = show_reasoning_input != 'n'

    while True:
        print("\n" + "─"*80)
        print("请输入待增强的提示词（或输入 'quit' 退出）:")
        user_prompt = input("> ").strip()

        if user_prompt.lower() in ['quit', 'exit', 'q']:
            print("\n👋 感谢使用提示词增强工具！")
            break

        if not user_prompt:
            print("⚠️  请输入有效的提示词")
            continue

        print("\n⏳ 正在增强提示词，请稍候...")
        print("   (DeepSeek 推理模式需要 30-40 秒)\n")

        result = enhancer.enhance(user_prompt)

        # 打印结果（根据用户选择是否显示思考过程）
        print_result(result, show_reasoning=show_reasoning)

        # 提示用户可以复制增强后的提示词
        if result['success']:
            print("\n【下一步】")
            print("  ✓ 您可以复制上面的增强后提示词")
            print("  ✓ 在其他 AI 工具中使用增强后的提示词")
            print("  ✓ 根据需要进一步修改或优化")

    return 0


if __name__ == "__main__":
    sys.exit(main())

