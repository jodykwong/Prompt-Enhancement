#!/bin/bash

# 快速验证脚本
# 使用方法: bash QUICK_VERIFICATION.sh

echo ""
echo "================================================================================"
echo "  �� DeepSeek API 迁移快速验证"
echo "================================================================================"
echo ""

# 激活虚拟环境
echo "1️⃣  激活虚拟环境..."
source venv/bin/activate
echo "   ✓ 虚拟环境已激活"
echo ""

# 验证环境变量
echo "2️⃣  验证环境变量..."
python3 << 'PYTHON_EOF'
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('DEEPSEEK_API_KEY')

if api_key:
    print(f"   ✓ DEEPSEEK_API_KEY 已配置")
    print(f"   ✓ 密钥长度: {len(api_key)} 字符")
    if api_key.startswith('sk-'):
        print(f"   ✓ 密钥格式正确 (sk- 开头)")
    else:
        print(f"   ✗ 密钥格式错误")
else:
    print(f"   ✗ DEEPSEEK_API_KEY 未找到")
PYTHON_EOF
echo ""

# 验证依赖
echo "3️⃣  验证依赖包..."
python3 << 'PYTHON_EOF'
try:
    import openai
    print(f"   ✓ openai 已安装 (版本: {openai.__version__})")
except ImportError:
    print(f"   ✗ openai 未安装")

try:
    import dotenv
    print(f"   ✓ python-dotenv 已安装")
except ImportError:
    print(f"   ✗ python-dotenv 未安装")
PYTHON_EOF
echo ""

# 运行集成测试
echo "4️⃣  运行集成测试..."
python3 test_deepseek_integration.py
echo ""

# 运行快速功能测试
echo "5️⃣  运行快速功能测试..."
python3 << 'PYTHON_EOF'
from prompt_enhancer import PromptEnhancer
import time

# 提示用户输入待增强的提示词
print("   请输入待增强的提示词（或按 Enter 使用默认示例 '优化代码'）:")
user_input = input("   > ").strip()
test_prompt = user_input if user_input else "优化代码"

print("   " + "-" * 36)
print(f"   测试提示词: '{test_prompt}'")
print("   " + "-" * 36)

enhancer = PromptEnhancer()
start = time.time()
result = enhancer.enhance(test_prompt)
elapsed = time.time() - start

if result['success']:
    print(f"   ✓ 增强成功")
    print(f"   ✓ 处理时间: {elapsed:.2f} 秒")
    print(f"   ✓ 原始长度: {len(result['original'])} 字符")
    print(f"   ✓ 增强长度: {len(result['enhanced'])} 字符")
    print(f"   ✓ 扩展比例: {len(result['enhanced']) / len(result['original']):.0f}x")
else:
    print(f"   ✗ 增强失败: {result['error']}")
PYTHON_EOF
echo ""

echo "================================================================================"
echo "  ✅ 快速验证完成！"
echo "================================================================================"
echo ""
