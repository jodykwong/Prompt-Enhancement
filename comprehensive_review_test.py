#!/usr/bin/env python3
"""
全面功能评审测试脚本
测试三大核心功能：指令扩展、上下文补充、最佳实践注入
"""

from prompt_enhancer import PromptEnhancer, print_result

def main():
    print("\n" + "="*80)
    print("  🔍 Prompt Enhancement 功能评审测试")
    print("="*80)
    
    # 初始化
    try:
        enhancer = PromptEnhancer()
        print("\n✓ PromptEnhancer 初始化成功")
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        return 1
    
    # 测试用例
    test_cases = [
        {
            "name": "测试 1: 指令扩展功能",
            "prompt": "修复bug",
            "focus": "验证是否将简短指令转化为结构化步骤"
        },
        {
            "name": "测试 2: 上下文补充功能",
            "prompt": "添加用户注册功能",
            "focus": "验证是否补充必要的上下文信息"
        },
        {
            "name": "测试 3: 最佳实践注入功能",
            "prompt": "重构代码",
            "focus": "验证是否注入编程规范和质量标准"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"  {test_case['name']}")
        print(f"  关注点: {test_case['focus']}")
        print("="*80)
        print(f"\n原始提示词: {test_case['prompt']}")
        print("⏳ 正在增强提示词，请稍候...")
        
        # 执行增强
        result = enhancer.enhance(test_case['prompt'])
        results.append({
            "test_case": test_case,
            "result": result
        })
        
        # 打印结果（不显示思考过程以节省空间）
        print_result(result, index=i, show_reasoning=False)
        
        print("\n" + "-"*80)
    
    # 生成评审报告
    print("\n" + "="*80)
    print("  📊 评审总结")
    print("="*80)
    
    for i, item in enumerate(results, 1):
        test_case = item["test_case"]
        result = item["result"]
        stats = result.get("stats", {})
        
        print(f"\n{test_case['name']}")
        print(f"  原始提示词: {test_case['prompt']}")
        print(f"  增强后长度: {stats.get('enhanced_length', 0)} 字符")
        print(f"  扩展比例: {stats.get('expansion_ratio', 0)}x")
        print(f"  处理时间: {result.get('processing_time', 0):.2f} 秒")
    
    print("\n" + "="*80)
    print("  ✅ 评审测试完成")
    print("="*80)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

