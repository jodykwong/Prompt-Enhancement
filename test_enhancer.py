#!/usr/bin/env python3
"""
测试脚本 - 验证提示词增强功能的效果

使用多个测试用例验证提示词增强的质量和性能
"""

import json
import os
from dotenv import load_dotenv
from prompt_enhancer import PromptEnhancer, print_result

# 加载 .env 文件中的环境变量
load_dotenv()


# 测试用例集合
TEST_CASES = [
    # 1. 简单模糊指令 - 中文
    "优化代码",
    
    # 2. 简单模糊指令 - 中文
    "修复bug",
    
    # 3. 中等复杂度指令 - 中文
    "添加用户登录功能",
    
    # 4. 纯中文指令 - 更具体
    "重构数据库查询模块，提高性能",
    
    # 5. 中英文混合指令
    "为 API 接口添加 rate limiting 功能",
]


def evaluate_enhancement(result: dict) -> dict:
    """
    评估增强质量
    
    评估维度：
    1. 是否保持原意
    2. 是否更具可执行性
    3. 是否添加了有用的上下文
    4. 结构是否清晰
    
    Returns:
        评估结果字典
    """
    if not result['success']:
        return {
            "quality_score": 0,
            "notes": "增强失败"
        }
    
    enhanced = result['enhanced']
    
    # 简单的启发式评估
    evaluation = {
        "has_steps": "1." in enhanced or "一、" in enhanced or "步骤" in enhanced,
        "has_verification": any(keyword in enhanced for keyword in ["验证", "测试", "检查", "确认"]),
        "has_context": any(keyword in enhanced for keyword in ["注意", "考虑", "确保", "遵循"]),
        "is_structured": enhanced.count("\n") >= 3,  # 至少有多行结构
        "length_appropriate": 100 <= len(enhanced) <= 1000,  # 长度合理
    }
    
    # 计算质量分数
    quality_score = sum(evaluation.values()) / len(evaluation) * 100
    
    notes = []
    if evaluation["has_steps"]:
        notes.append("✓ 包含具体步骤")
    if evaluation["has_verification"]:
        notes.append("✓ 包含验证标准")
    if evaluation["has_context"]:
        notes.append("✓ 添加了上下文信息")
    if evaluation["is_structured"]:
        notes.append("✓ 结构清晰")
    if evaluation["length_appropriate"]:
        notes.append("✓ 长度适中")
    
    return {
        "quality_score": quality_score,
        "evaluation": evaluation,
        "notes": notes
    }


def run_tests():
    """运行所有测试用例"""
    print("="*80)
    print("提示词增强 MVP 测试")
    print("="*80)
    print(f"\n共 {len(TEST_CASES)} 个测试用例\n")
    
    # 初始化增强器
    try:
        enhancer = PromptEnhancer()
    except ValueError as e:
        print(f"✗ 初始化失败: {e}")
        print("\n请设置 ANTHROPIC_API_KEY 环境变量")
        return
    
    # 运行测试
    results = []
    total_time = 0
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n正在处理测试用例 {i}/{len(TEST_CASES)}...")
        result = enhancer.enhance(test_case)
        results.append(result)
        total_time += result['processing_time']
        
        # 打印结果
        print_result(result, i)
        
        # 评估质量
        if result['success']:
            evaluation = evaluate_enhancement(result)
            print(f"\n【质量评估】")
            print(f"质量分数: {evaluation['quality_score']:.1f}/100")
            for note in evaluation['notes']:
                print(f"  {note}")
    
    # 打印总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    
    success_count = sum(1 for r in results if r['success'])
    print(f"\n成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    print(f"总处理时间: {total_time:.2f} 秒")
    print(f"平均处理时间: {total_time/len(results):.2f} 秒/条")
    
    # 计算平均质量分数
    if success_count > 0:
        quality_scores = [
            evaluate_enhancement(r)['quality_score'] 
            for r in results if r['success']
        ]
        avg_quality = sum(quality_scores) / len(quality_scores)
        print(f"平均质量分数: {avg_quality:.1f}/100")
    
    # 保存详细结果到文件
    output_file = "test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_cases": TEST_CASES,
            "results": results,
            "summary": {
                "total_tests": len(results),
                "successful": success_count,
                "total_time": total_time,
                "average_time": total_time / len(results)
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细结果已保存到: {output_file}")
    
    return results


if __name__ == "__main__":
    run_tests()

