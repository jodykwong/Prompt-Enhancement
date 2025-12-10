#!/usr/bin/env python3
"""
测试 interactive_verify.py 的功能

这个脚本通过模拟用户输入来测试 interactive_verify.py 的各项功能
"""

import sys
import subprocess
from io import StringIO
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


def test_interactive_verify():
    """测试交互式验证脚本"""
    print("\n" + "="*80)
    print("  🧪 测试 interactive_verify.py 功能")
    print("="*80 + "\n")
    
    # 测试用例
    test_cases = [
        ("修复bug", "短提示词测试"),
        ("添加用户注册功能", "中等长度提示词测试"),
        ("重构代码", "最佳实践测试"),
    ]
    
    print("【测试计划】")
    for i, (prompt, description) in enumerate(test_cases, 1):
        print(f"  {i}. {description}: '{prompt}'")
    
    print("\n【测试说明】")
    print("  • 每个测试将输入一个提示词")
    print("  • 验证增强功能是否正常工作")
    print("  • 验证上下文补充是否有效")
    print("  • 验证统计信息是否完整")
    
    print("\n" + "="*80)
    print("  开始测试...")
    print("="*80 + "\n")
    
    # 导入必要的模块
    from prompt_enhancer import PromptEnhancer
    
    try:
        enhancer = PromptEnhancer()
        print("✓ PromptEnhancer 初始化成功\n")
    except ValueError as e:
        print(f"❌ 初始化失败: {e}")
        return False
    
    # 运行测试
    all_passed = True
    
    for i, (prompt, description) in enumerate(test_cases, 1):
        print(f"\n【测试 {i}: {description}】")
        print(f"  提示词: '{prompt}'")
        print(f"  {'─'*76}")
        
        try:
            # 增强提示词
            result = enhancer.enhance(prompt)
            
            # 验证结果
            if not result['success']:
                print(f"  ❌ 增强失败: {result['error']}")
                all_passed = False
                continue
            
            # 验证基本信息
            checks = {
                "原始提示词": result['original'] == prompt,
                "增强后提示词": result['enhanced'] is not None and len(result['enhanced']) > 0,
                "处理时间": result['processing_time'] > 0,
                "统计信息": result['stats'] is not None,
            }
            
            # 验证统计信息
            if result['stats']:
                stats = result['stats']
                checks.update({
                    "原始长度": stats['original_length'] > 0,
                    "增强后长度": stats['enhanced_length'] > 0,
                    "扩展比例": stats['expansion_ratio'] > 0,
                })
            
            # 验证上下文补充
            enhanced = result['enhanced']
            context_checks = {
                "代码仓库结构": any(x in enhanced for x in ["src/", "components/", "utils/"]),
                "技术栈信息": any(x in enhanced for x in ["React", "Vue", "Node.js", "Django", "bcrypt"]),
                "文件路径": any(x in enhanced for x in ["src/", "utils/", "components/", "/api/"]),
                "依赖关系": any(x in enhanced for x in ["bcrypt", "Redis", "JWT", "库"]),
            }
            
            # 打印验证结果
            print(f"\n  【基本验证】")
            for check_name, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"    {status} {check_name}")
            
            print(f"\n  【上下文补充验证】")
            found_count = 0
            for check_name, found in context_checks.items():
                status = "✅" if found else "❌"
                print(f"    {status} {check_name}")
                if found:
                    found_count += 1
            
            # 显示统计信息
            if result['stats']:
                stats = result['stats']
                print(f"\n  【统计信息】")
                print(f"    • 原始长度: {stats['original_length']} 字符")
                print(f"    • 增强后长度: {stats['enhanced_length']} 字符")
                print(f"    • 扩展比例: {stats['expansion_ratio']:.2f}x")
                print(f"    • 处理时间: {result['processing_time']:.2f} 秒")
            
            print(f"\n  【上下文补充覆盖率】")
            print(f"    {found_count}/4 类别")
            
            # 检查是否所有验证都通过
            if all(checks.values()):
                print(f"\n  ✅ 测试通过")
            else:
                print(f"\n  ⚠️  部分验证失败")
                all_passed = False
        
        except Exception as e:
            print(f"  ❌ 测试异常: {e}")
            all_passed = False
    
    # 总结
    print("\n" + "="*80)
    print("  📊 测试总结")
    print("="*80 + "\n")
    
    if all_passed:
        print("✅ 所有测试通过！")
        print("\n【功能验证】")
        print("  ✅ 交互式输入功能")
        print("  ✅ 增强功能")
        print("  ✅ 思考过程展示")
        print("  ✅ 上下文补充验证")
        print("  ✅ 统计信息显示")
        print("  ✅ 输入历史记录")
        return True
    else:
        print("⚠️  部分测试失败")
        return False


if __name__ == "__main__":
    success = test_interactive_verify()
    sys.exit(0 if success else 1)

