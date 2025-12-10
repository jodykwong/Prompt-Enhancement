#!/usr/bin/env python3
"""
DeepSeek API 集成测试脚本

验证 DeepSeek-V3.2-Speciale API 的集成是否正确
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_api_key():
    """测试 API 密钥配置"""
    print("=" * 80)
    print("1. 测试 API 密钥配置")
    print("=" * 80)
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("✗ 未找到 DEEPSEEK_API_KEY")
        return False
    
    masked_key = api_key[:8] + "*" * (len(api_key) - 12) + api_key[-4:]
    print(f"✓ API 密钥已配置: {masked_key}")
    print(f"✓ 密钥长度: {len(api_key)} 字符\n")
    return True


def test_imports():
    """测试必要的导入"""
    print("=" * 80)
    print("2. 测试必要的导入")
    print("=" * 80)
    
    try:
        from openai import OpenAI
        print("✓ OpenAI SDK 导入成功")
        
        from prompt_enhancer import PromptEnhancer
        print("✓ PromptEnhancer 导入成功\n")
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}\n")
        return False


def test_client_initialization():
    """测试客户端初始化"""
    print("=" * 80)
    print("3. 测试 DeepSeek 客户端初始化")
    print("=" * 80)
    
    try:
        from prompt_enhancer import PromptEnhancer
        
        enhancer = PromptEnhancer()
        print(f"✓ PromptEnhancer 初始化成功")
        print(f"✓ 使用模型: {enhancer.model}")
        print(f"✓ API 基础 URL: https://api.deepseek.com\n")
        return True
    except Exception as e:
        print(f"✗ 初始化失败: {e}\n")
        return False


def test_simple_enhancement():
    """测试简单的提示词增强"""
    print("=" * 80)
    print("4. 测试提示词增强（调用 DeepSeek API）")
    print("=" * 80)
    
    try:
        from prompt_enhancer import PromptEnhancer
        
        enhancer = PromptEnhancer()
        
        # 测试简单提示词
        test_prompt = "优化代码"
        print(f"原始提示词: {test_prompt}")
        print(f"正在调用 DeepSeek API...")
        
        result = enhancer.enhance(test_prompt)
        
        if result["success"]:
            print(f"✓ 增强成功")
            print(f"✓ 处理时间: {result['processing_time']:.2f} 秒")
            print(f"\n【增强后的提示词】")
            print(f"{result['enhanced'][:200]}...")  # 显示前200个字符
            print()
            return True
        else:
            print(f"✗ 增强失败: {result['error']}\n")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}\n")
        return False


def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "DeepSeek API 集成测试".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    tests = [
        ("API 密钥配置", test_api_key),
        ("导入检查", test_imports),
        ("客户端初始化", test_client_initialization),
        ("提示词增强", test_simple_enhancement),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}\n")
            results.append((test_name, False))
    
    # 打印总结
    print("=" * 80)
    print("测试总结")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {test_name}")
    
    print()
    print(f"总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n✓ 所有测试通过！DeepSeek API 集成成功。")
        return 0
    else:
        print(f"\n✗ 有 {total - passed} 个测试失败。请检查配置。")
        return 1


if __name__ == "__main__":
    sys.exit(main())

