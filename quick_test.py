#!/usr/bin/env python3
"""
快速测试脚本 - 验证优化后的功能
"""

from prompt_enhancer import PromptEnhancer, print_result

def main():
    print("\n" + "="*80)
    print("  🧪 快速测试 - 验证优化后的功能")
    print("="*80)
    
    # 初始化
    try:
        enhancer = PromptEnhancer()
        print("\n✓ PromptEnhancer 初始化成功")
        print(f"✓ 模型: {enhancer.model}")
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        return 1
    
    # 测试用例
    test_prompt = "优化代码"
    
    print(f"\n测试提示词: {test_prompt}")
    print("⏳ 正在增强提示词，请稍候...")
    print("   (DeepSeek 推理模式需要 30-40 秒)")
    
    # 执行增强
    result = enhancer.enhance(test_prompt)
    
    # 打印结果
    print_result(result, show_reasoning=True)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

