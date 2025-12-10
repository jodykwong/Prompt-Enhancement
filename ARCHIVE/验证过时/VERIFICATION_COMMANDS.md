# 🔧 验证命令快速参考

## 一键快速验证（推荐）

```bash
# 最简单的方式 - 运行快速验证脚本
bash QUICK_VERIFICATION.sh
```

---

## 分步验证命令

### 第一步：激活虚拟环境

```bash
source venv/bin/activate
```

**验证激活成功**:
```bash
which python3
# 应该显示: /Users/jodykwong/Documents/augment-projects/Prompt-Enhancement/venv/bin/python3
```

---

### 第二步：验证 API 密钥配置

```bash
# 检查 .env 文件是否存在
ls -la .env

# 查看密钥是否配置（不显示实际密钥）
python3 << 'EOF'
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('DEEPSEEK_API_KEY')

if api_key:
    print(f"✓ DEEPSEEK_API_KEY 已配置")
    print(f"✓ 密钥长度: {len(api_key)} 字符")
    print(f"✓ 密钥格式: {'正确 (sk- 开头)' if api_key.startswith('sk-') else '错误'}")
else:
    print("✗ DEEPSEEK_API_KEY 未找到")
EOF
```

---

### 第三步：验证依赖安装

```bash
# 检查 openai 包
python3 -c "import openai; print(f'✓ openai {openai.__version__}')"

# 检查 python-dotenv 包
python3 -c "import dotenv; print('✓ python-dotenv 已安装')"

# 查看所有依赖
pip list | grep -E "openai|python-dotenv"
```

---

### 第四步：运行集成测试

```bash
python3 test_deepseek_integration.py
```

**预期结果**: 4/4 测试通过

---

### 第五步：测试真实 API 调用

#### 方法 A: 简单测试（推荐）

```bash
python3 << 'EOF'
from prompt_enhancer import PromptEnhancer

enhancer = PromptEnhancer()
result = enhancer.enhance("优化代码")

print(f"✓ 增强成功")
print(f"✓ 处理时间: {result['processing_time']:.2f} 秒")
print(f"✓ 原始长度: {len(result['original'])} 字符")
print(f"✓ 增强长度: {len(result['enhanced'])} 字符")
print(f"✓ 扩展比例: {len(result['enhanced']) / len(result['original']):.0f}x")
EOF
```

#### 方法 B: 详细测试

```bash
python3 << 'EOF'
from prompt_enhancer import PromptEnhancer
import json

enhancer = PromptEnhancer()
result = enhancer.enhance("优化代码")

print("=" * 80)
print("详细测试结果")
print("=" * 80)
print(f"\n原始提示词: {result['original']}")
print(f"处理时间: {result['processing_time']:.2f} 秒")
print(f"\n增强后的提示词:\n{result['enhanced'][:500]}...")
print("\n" + "=" * 80)
EOF
```

#### 方法 C: 多个测试用例

```bash
python3 << 'EOF'
from prompt_enhancer import PromptEnhancer

enhancer = PromptEnhancer()

test_cases = [
    "修复 bug",
    "添加登录功能",
    "优化数据库查询"
]

print("=" * 80)
print("多个测试用例")
print("=" * 80)

for prompt in test_cases:
    try:
        result = enhancer.enhance(prompt)
        print(f"\n✓ '{prompt}'")
        print(f"  耗时: {result['processing_time']:.2f} 秒")
        print(f"  扩展: {len(result['original'])} → {len(result['enhanced'])} 字符")
    except Exception as e:
        print(f"\n✗ '{prompt}': {e}")

print("\n" + "=" * 80)
EOF
```

---

### 第六步：验证输出质量

```bash
python3 << 'EOF'
from prompt_enhancer import PromptEnhancer

enhancer = PromptEnhancer()
result = enhancer.enhance("优化代码")

enhanced = result['enhanced'].lower()

print("=" * 80)
print("输出质量检查")
print("=" * 80)

# 原意保持检查
print("\n1. 原意保持:")
keywords = ["优化", "代码"]
for keyword in keywords:
    status = "✓" if keyword in enhanced else "✗"
    print(f"   {status} 包含关键词: {keyword}")

# 质量检查
print("\n2. 输出质量:")
checks = {
    "包含步骤": "步骤" in enhanced or "1." in enhanced,
    "包含具体建议": "工具" in enhanced or "方法" in enhanced,
    "长度合理": len(enhanced) > 200,
    "格式清晰": "\n" in enhanced
}

for check, passed in checks.items():
    status = "✓" if passed else "✗"
    print(f"   {status} {check}")

# 数据结构检查
print("\n3. 数据结构:")
required_fields = ['original', 'enhanced', 'processing_time']
for field in required_fields:
    status = "✓" if field in result else "✗"
    print(f"   {status} 字段 '{field}' 存在")

print("\n" + "=" * 80)
EOF
```

---

## 故障排查命令

### 检查 API 连接

```bash
python3 << 'EOF'
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

try:
    client = OpenAI(
        api_key=os.getenv('DEEPSEEK_API_KEY'),
        base_url='https://api.deepseek.com'
    )
    
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[{"role": "user", "content": "hello"}],
        max_tokens=10
    )
    
    print("✓ API 连接成功")
    print(f"✓ 响应: {response.choices[0].message.content}")
except Exception as e:
    print(f"✗ API 连接失败: {e}")
EOF
```

### 检查网络连接

```bash
# 测试 DNS 解析
nslookup api.deepseek.com

# 测试网络连接
python3 << 'EOF'
import socket

try:
    socket.create_connection(('api.deepseek.com', 443), timeout=5)
    print("✓ 网络连接正常")
except Exception as e:
    print(f"✗ 网络连接失败: {e}")
EOF
```

### 检查依赖版本

```bash
pip show openai
pip show python-dotenv
```

---

## 完整验证流程（按顺序执行）

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 验证 API 密钥
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓ API Key' if os.getenv('DEEPSEEK_API_KEY') else '✗ API Key')"

# 3. 验证依赖
python3 -c "import openai; import dotenv; print('✓ Dependencies')"

# 4. 运行集成测试
python3 test_deepseek_integration.py

# 5. 测试 API 调用
python3 << 'EOF'
from prompt_enhancer import PromptEnhancer
result = PromptEnhancer().enhance("优化代码")
print(f"✓ API Call Success - {result['processing_time']:.2f}s")
EOF

# 6. 验证输出质量
python3 << 'EOF'
from prompt_enhancer import PromptEnhancer
result = PromptEnhancer().enhance("优化代码")
enhanced = result['enhanced'].lower()
print(f"✓ Quality Check - {'Pass' if '优化' in enhanced and '代码' in enhanced else 'Fail'}")
EOF

echo "✅ 验证完成！"
```

---

## 快速参考表

| 任务 | 命令 |
|------|------|
| 激活虚拟环境 | `source venv/bin/activate` |
| 验证 API 密钥 | `python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('DEEPSEEK_API_KEY'))"` |
| 检查 openai | `python3 -c "import openai; print(openai.__version__)"` |
| 运行集成测试 | `python3 test_deepseek_integration.py` |
| 快速验证 | `bash QUICK_VERIFICATION.sh` |
| 完整验证 | `python3 verify_migration.py` |
| 测试 API 调用 | `python3 -c "from prompt_enhancer import PromptEnhancer; print(PromptEnhancer().enhance('test'))"` |

---

**最后更新**: 2025-12-09  
**版本**: 1.0

