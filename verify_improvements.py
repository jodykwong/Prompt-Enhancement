#!/usr/bin/env python3
"""
优先级 1 改进任务 - 验证脚本
用于快速验证改进效果是否符合目标
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from prompt_enhancer import PromptEnhancer


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def verify_expansion_ratio(original_len, enhanced_len, test_name):
    """验证扩展比例"""
    if original_len == 0:
        return None
    
    ratio = enhanced_len / original_len
    
    # 根据原始长度确定目标
    if original_len < 10:
        target_min, target_max = 6, 10  # 30-50 字符 / 5 字符 = 6-10x
        target_desc = "6-10x"
    elif original_len <= 50:
        target_min, target_max = 3, 5
        target_desc = "3-5x"
    else:
        target_min, target_max = 2, 3
        target_desc = "2-3x"
    
    status = "✅" if target_min <= ratio <= target_max else "⚠️"
    
    print(f"  {test_name}:")
    print(f"    原始长度: {original_len} 字符")
    print(f"    增强后长度: {enhanced_len} 字符")
    print(f"    扩展比例: {ratio:.2f}x {status} (目标: {target_desc})")
    
    return ratio


def verify_context_supplement(enhanced_prompt, test_name):
    """验证上下文补充"""
    print(f"\n  {test_name} - 上下文补充验证:")
    
    context_items = {
        "代码仓库结构": ["src/", "components/", "utils/", "api/", "tests/"],
        "技术栈信息": ["React", "Vue", "Node.js", "Django", "FastAPI", "bcrypt", "Redis", "JWT"],
        "文件路径": ["RegisterForm", "/api/", "src/"],
        "依赖关系": ["bcrypt", "Redis", "JWT", "库", "安装"]
    }
    
    found_items = {}
    for category, keywords in context_items.items():
        found = [kw for kw in keywords if kw in enhanced_prompt]
        found_items[category] = found
        status = "✅" if found else "❌"
        print(f"    {status} {category}: {', '.join(found) if found else '未找到'}")
    
    return found_items


def main():
    """主函数"""
    print_header("🔍 优先级 1 改进任务 - 验证脚本")
    
    # 初始化增强器
    try:
        enhancer = PromptEnhancer()
        print("✓ PromptEnhancer 初始化成功\n")
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        return
    
    # 测试用例
    test_cases = [
        ("修复bug", "指令扩展功能"),
        ("添加用户注册功能", "上下文补充功能"),
        ("重构代码", "最佳实践注入功能"),
    ]
    
    results = []
    
    for prompt, category in test_cases:
        print_header(f"测试: {prompt} ({category})")
        
        try:
            result = enhancer.enhance(prompt)
            
            if result["success"]:
                original_len = len(prompt)
                enhanced_len = len(result["enhanced"])
                
                # 验证扩展比例
                ratio = verify_expansion_ratio(original_len, enhanced_len, prompt)
                
                # 验证上下文补充
                context = verify_context_supplement(result["enhanced"], prompt)
                
                # 显示增强后的提示词
                print(f"\n  增强后提示词:")
                print(f"  {'-' * 76}")
                print(f"  {result['enhanced']}")
                print(f"  {'-' * 76}")
                
                results.append({
                    "prompt": prompt,
                    "ratio": ratio,
                    "context": context,
                    "success": True
                })
            else:
                print(f"✗ 增强失败: {result['error']}")
                results.append({
                    "prompt": prompt,
                    "success": False,
                    "error": result["error"]
                })
        
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            results.append({
                "prompt": prompt,
                "success": False,
                "error": str(e)
            })
    
    # 验证总结
    print_header("📊 验证总结")
    
    successful_tests = [r for r in results if r["success"]]
    
    if successful_tests:
        ratios = [r["ratio"] for r in successful_tests if r["ratio"]]
        avg_ratio = sum(ratios) / len(ratios) if ratios else 0
        
        print(f"✅ 成功测试: {len(successful_tests)}/{len(results)}")
        print(f"✅ 平均扩展比例: {avg_ratio:.2f}x (目标: < 20x)")
        
        if avg_ratio < 20:
            print(f"✅ 扩展比例目标达成!")
        else:
            print(f"⚠️ 扩展比例未完全达成 (实际: {avg_ratio:.2f}x, 目标: < 20x)")
        
        # 检查上下文补充
        all_context_found = all(
            any(r["context"].get(cat, []) for r in successful_tests)
            for cat in ["代码仓库结构", "技术栈信息", "文件路径", "依赖关系"]
        )
        
        if all_context_found:
            print(f"✅ 上下文补充目标达成!")
        else:
            print(f"⚠️ 上下文补充不完整")
    
    print("\n" + "=" * 80)
    print("  验证完成")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

