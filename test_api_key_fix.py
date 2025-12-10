#!/usr/bin/env python3
"""
API 密钥加载修复验证脚本

验证修复后的脚本是否能正确加载 API 密钥
"""

import os
import sys
from pathlib import Path

def test_env_file():
    """测试 .env 文件是否存在"""
    print("\n" + "="*80)
    print("1️⃣  检查 .env 文件")
    print("="*80)
    
    env_path = Path(".env")
    if env_path.exists():
        print("✓ .env 文件存在")
        return True
    else:
        print("✗ .env 文件不存在")
        return False

def test_dotenv_import():
    """测试 python-dotenv 是否已安装"""
    print("\n" + "="*80)
    print("2️⃣  检查 python-dotenv 包")
    print("="*80)
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv 已安装")
        return True
    except ImportError:
        print("✗ python-dotenv 未安装")
        return False

def test_api_key_loading():
    """测试 API 密钥加载"""
    print("\n" + "="*80)
    print("3️⃣  检查 API 密钥加载")
    print("="*80)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        masked = api_key[:8] + "*" * (len(api_key) - 12) + api_key[-4:]
        print(f"✓ API 密钥已加载: {masked}")
        print(f"✓ 密钥长度: {len(api_key)} 字符")
        return True
    else:
        print("✗ API 密钥未找到")
        return False

def test_prompt_enhancer_init():
    """测试 PromptEnhancer 初始化"""
    print("\n" + "="*80)
    print("4️⃣  检查 PromptEnhancer 初始化")
    print("="*80)
    
    try:
        from prompt_enhancer import PromptEnhancer
        enhancer = PromptEnhancer()
        print("✓ PromptEnhancer 初始化成功")
        print("✓ API 密钥已正确加载")
        return True
    except ValueError as e:
        print(f"✗ 初始化失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 意外错误: {e}")
        return False

def test_interactive_enhance_import():
    """测试 interactive_enhance 导入"""
    print("\n" + "="*80)
    print("5️⃣  检查 interactive_enhance 导入")
    print("="*80)
    
    try:
        import interactive_enhance
        print("✓ interactive_enhance 导入成功")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def main():
    """主函数"""
    print("\n" + "="*80)
    print("  🔍 API 密钥加载修复验证")
    print("="*80)
    
    results = []
    
    # 运行所有测试
    results.append(("检查 .env 文件", test_env_file()))
    results.append(("检查 python-dotenv", test_dotenv_import()))
    results.append(("检查 API 密钥加载", test_api_key_loading()))
    results.append(("检查 PromptEnhancer 初始化", test_prompt_enhancer_init()))
    results.append(("检查 interactive_enhance 导入", test_interactive_enhance_import()))
    
    # 打印总结
    print("\n" + "="*80)
    print("  📊 验证总结")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n✅ 所有测试通过！API 密钥加载修复成功！")
        print("\n现在可以使用以下命令：")
        print("  • python interactive_enhance.py")
        print("  • python prompt_enhancer.py '待增强的提示词'")
        return 0
    else:
        print(f"\n❌ 有 {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())

