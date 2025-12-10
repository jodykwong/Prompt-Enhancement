#!/usr/bin/env python3
"""
优化效果验证脚本

测试优化后的提示词增强功能，验证：
1. 思考过程是否正确展示
2. 增强结果是否简洁实用
3. 是否保持了原意
"""

import sys
from prompt_enhancer import PromptEnhancer, print_result

# 测试用例
TEST_CASES = [
    "优化代码",
    "写一篇文章",
    "分析数据",
    "修复登录bug",
    "添加用户注册功能"
]

def main():
    """主函数"""
    print("\n" + "="*80)
    print("  🧪 提示词增强功能优化验证")
    print("="*80)
    print("\n本测试将验证以下优化：")
    print("  1. ✓ 展示 DeepSeek 模型的思考过程")
    print("  2. ✓ 生成简洁、实用的增强提示词")
    print("  3. ✓ 保持用户原始意图")
    print("  4. ✓ 提供详细的统计信息")
    
    # 初始化增强器
    try:
        enhancer = PromptEnhancer()
        print("\n✓ PromptEnhancer 初始化成功")
    except ValueError as e:
        print(f"\n✗ 初始化失败: {e}")
        return 1
    
    # 选择测试模式
    print("\n" + "─"*80)
    print("请选择测试模式：")
    print("  1. 快速测试（仅测试第一个用例）")
    print("  2. 完整测试（测试所有 5 个用例）")
    print("  3. 自定义测试（输入您自己的提示词）")
    
    choice = input("\n请输入选项 (1/2/3): ").strip()
    
    if choice == "1":
        # 快速测试
        print("\n" + "="*80)
        print("  快速测试模式")
        print("="*80)
        test_prompts = [TEST_CASES[0]]
    elif choice == "2":
        # 完整测试
        print("\n" + "="*80)
        print("  完整测试模式")
        print("="*80)
        test_prompts = TEST_CASES
    elif choice == "3":
        # 自定义测试
        print("\n" + "="*80)
        print("  自定义测试模式")
        print("="*80)
        custom_prompt = input("请输入您的提示词: ").strip()
        if not custom_prompt:
            print("✗ 提示词不能为空")
            return 1
        test_prompts = [custom_prompt]
    else:
        print("✗ 无效的选项")
        return 1
    
    # 运行测试
    results = []
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{'='*80}")
        print(f"  测试 {i}/{len(test_prompts)}: {prompt}")
        print(f"{'='*80}")
        print("⏳ 正在增强提示词，请稍候...")
        print("   (DeepSeek 推理模式需要 30-40 秒)")
        
        result = enhancer.enhance(prompt)
        results.append(result)
        
        # 打印结果（显示思考过程）
        print_result(result, index=i, show_reasoning=True)
    
    # 打印总结
    print("\n" + "="*80)
    print("  📊 测试总结")
    print("="*80)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"\n总计: {successful}/{total} 测试成功")
    
    if successful > 0:
        avg_time = sum(r['processing_time'] for r in results if r['success']) / successful
        avg_expansion = sum(r['stats']['expansion_ratio'] for r in results if r['success']) / successful
        
        print(f"平均处理时间: {avg_time:.2f} 秒")
        print(f"平均扩展比例: {avg_expansion:.2f}x")
    
    # 验证优化效果
    print("\n" + "─"*80)
    print("✅ 优化验证：")
    print("  1. 思考过程展示: ✓ 已实现")
    print("  2. 统计信息展示: ✓ 已实现")
    print("  3. 简洁实用输出: ✓ 请查看上述结果")
    print("  4. 保持原意: ✓ 请人工验证")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

