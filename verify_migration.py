#!/usr/bin/env python3
"""
DeepSeek API 迁移验证脚本
完整的手动验证工具
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_section(title):
    """打印小标题"""
    print(f"\n{title}")
    print("-" * 40)

def check_mark(condition, message):
    """打印检查结果"""
    symbol = "✓" if condition else "✗"
    print(f"  {symbol} {message}")
    return condition

# ============================================================================
# 第一部分：环境准备验证
# ============================================================================

def verify_environment():
    """验证环境准备"""
    print_header("第一部分：环境准备验证")
    
    all_passed = True
    
    # 1.1 检查虚拟环境
    print_section("1.1 虚拟环境检查")
    venv_path = Path("venv/bin/python3")
    all_passed &= check_mark(venv_path.exists(), "虚拟环境存在")
    
    # 1.2 检查 .env 文件
    print_section("1.2 .env 文件检查")
    env_path = Path(".env")
    all_passed &= check_mark(env_path.exists(), ".env 文件存在")
    
    # 1.3 加载环境变量
    print_section("1.3 环境变量加载")
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if api_key:
        all_passed &= check_mark(True, f"DEEPSEEK_API_KEY 已加载，长度: {len(api_key)}")
        all_passed &= check_mark(api_key.startswith("sk-"), "API 密钥格式正确 (sk- 开头)")
    else:
        all_passed &= check_mark(False, "DEEPSEEK_API_KEY 未找到")
    
    # 1.4 检查依赖
    print_section("1.4 依赖包检查")
    try:
        import openai
        all_passed &= check_mark(True, f"openai 已安装，版本: {openai.__version__}")
    except ImportError:
        all_passed &= check_mark(False, "openai 未安装")
    
    try:
        import dotenv
        all_passed &= check_mark(True, "python-dotenv 已安装")
    except ImportError:
        all_passed &= check_mark(False, "python-dotenv 未安装")
    
    return all_passed

# ============================================================================
# 第二部分：集成测试验证
# ============================================================================

def verify_integration():
    """验证集成测试"""
    print_header("第二部分：集成测试验证")
    
    all_passed = True
    
    # 2.1 API 密钥配置
    print_section("2.1 API 密钥配置")
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    all_passed &= check_mark(api_key is not None, "API 密钥已配置")
    
    # 2.2 导入检查
    print_section("2.2 导入检查")
    try:
        from openai import OpenAI
        all_passed &= check_mark(True, "OpenAI 导入成功")
    except ImportError as e:
        all_passed &= check_mark(False, f"OpenAI 导入失败: {e}")
        return all_passed
    
    # 2.3 客户端初始化
    print_section("2.3 客户端初始化")
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        all_passed &= check_mark(True, "OpenAI 客户端初始化成功")
        all_passed &= check_mark(True, "base_url 配置: https://api.deepseek.com")
    except Exception as e:
        all_passed &= check_mark(False, f"客户端初始化失败: {e}")
        return all_passed
    
    # 2.4 简单 API 调用
    print_section("2.4 API 调用测试")
    try:
        start_time = time.time()
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": "你是一个有帮助的助手。"},
                {"role": "user", "content": "你好"}
            ],
            max_tokens=100
        )
        elapsed = time.time() - start_time
        
        all_passed &= check_mark(True, "API 调用成功")
        all_passed &= check_mark(
            response.choices[0].message.content is not None,
            f"返回有效响应，耗时: {elapsed:.2f} 秒"
        )
    except Exception as e:
        all_passed &= check_mark(False, f"API 调用失败: {e}")
    
    return all_passed

# ============================================================================
# 第三部分：真实 API 调用验证
# ============================================================================

def verify_real_api():
    """验证真实 API 调用"""
    print_header("第三部分：真实 API 调用验证")
    
    all_passed = True
    
    try:
        from prompt_enhancer import PromptEnhancer
    except ImportError:
        check_mark(False, "prompt_enhancer 导入失败")
        return False
    
    print_section("3.1 初始化增强器")
    try:
        enhancer = PromptEnhancer()
        all_passed &= check_mark(True, "PromptEnhancer 初始化成功")
    except Exception as e:
        all_passed &= check_mark(False, f"初始化失败: {e}")
        return all_passed
    
    print_section("3.2 测试提示词增强")
    # 提示用户输入待增强的提示词
    print("  请输入待增强的提示词（或按 Enter 使用默认示例 '优化代码'）:")
    user_input = input("  > ").strip()
    test_prompt = user_input if user_input else "优化代码"

    try:
        result = enhancer.enhance(test_prompt)
        all_passed &= check_mark(True, f"增强成功，耗时: {result['processing_time']:.2f} 秒")
        all_passed &= check_mark(
            len(result['enhanced']) > len(test_prompt),
            f"增强长度: {len(test_prompt)} → {len(result['enhanced'])} 字符"
        )
    except Exception as e:
        all_passed &= check_mark(False, f"增强失败: {e}")
        return all_passed
    
    return all_passed

# ============================================================================
# 第四部分：功能验证
# ============================================================================

def verify_functionality():
    """验证功能"""
    print_header("第四部分：功能验证")
    
    all_passed = True
    
    try:
        from prompt_enhancer import PromptEnhancer
        enhancer = PromptEnhancer()
    except Exception as e:
        check_mark(False, f"初始化失败: {e}")
        return False
    
    print_section("4.1 原意保持检查")
    # 提示用户输入待增强的提示词
    print("  请输入待增强的提示词（或按 Enter 使用默认示例 '优化代码'）:")
    user_input = input("  > ").strip()
    test_prompt = user_input if user_input else "优化代码"

    result = enhancer.enhance(test_prompt)
    enhanced = result['enhanced'].lower()
    
    keywords = ["优化", "代码"]
    for keyword in keywords:
        all_passed &= check_mark(keyword in enhanced, f"包含关键词: {keyword}")
    
    print_section("4.2 输出质量检查")
    checks = {
        "包含步骤": "步骤" in enhanced or "1." in enhanced,
        "包含具体建议": "工具" in enhanced or "方法" in enhanced,
        "长度合理": len(enhanced) > 200,
        "格式清晰": "\n" in enhanced
    }
    
    for check_name, result_val in checks.items():
        all_passed &= check_mark(result_val, check_name)
    
    print_section("4.3 API 返回数据验证")
    required_fields = ['original', 'enhanced', 'processing_time']
    for field in required_fields:
        all_passed &= check_mark(field in result, f"字段 '{field}' 存在")
    
    return all_passed

# ============================================================================
# 主函数
# ============================================================================

def main():
    """主验证流程"""
    print("\n" + "=" * 80)
    print("  🔍 DeepSeek API 迁移完整验证")
    print("=" * 80)
    
    results = {
        "环境准备": verify_environment(),
        "集成测试": verify_integration(),
        "真实 API 调用": verify_real_api(),
        "功能验证": verify_functionality()
    }
    
    # 打印总结
    print_header("验证总结")
    
    all_passed = True
    for name, passed in results.items():
        symbol = "✓" if passed else "✗"
        print(f"  {symbol} {name}: {'通过' if passed else '失败'}")
        all_passed &= passed
    
    print("\n" + "=" * 80)
    if all_passed:
        print("  ✅ 所有验证通过！系统已准备就绪。")
    else:
        print("  ❌ 部分验证失败，请检查上述错误。")
    print("=" * 80 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

