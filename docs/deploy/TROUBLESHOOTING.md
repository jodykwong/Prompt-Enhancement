# 故障排除指南

## 常见问题

### 1. `/pe` 命令找不到

**症状**: 输入 `/pe 提示词` 后出现 "command not found" 或命令不可用

**解决步骤**:

```bash
# 1. 检查安装状态
prompt-enhance-verify

# 2. 检查文件是否存在
ls -la .claude/commands/pe.md
ls -la .claude/commands/scripts/enhance.py

# 3. 重新安装
prompt-enhance-install /path/to/project

# 4. 验证
prompt-enhance-verify
```

**可能原因**:
- 命令未正确安装
- 文件被删除
- Claude Code 缓存问题

**进阶调试**:

```bash
# 查看完整错误信息
cd /path/to/project
python3 .claude/commands/scripts/enhance.py "测试提示词"

# 检查 Python 路径
which python3
python3 --version
```

---

### 2. API 密钥错误

**症状**:
- "DEEPSEEK_API_KEY not configured"
- "Invalid API key"
- "Authentication failed"

**解决步骤**:

```bash
# 1. 验证 API 密钥
echo $DEEPSEEK_API_KEY  # Linux/Mac
echo $env:DEEPSEEK_API_KEY  # Windows

# 如果为空，需要配置

# 2. 交互式配置（推荐）
prompt-enhance-setup

# 3. 或手动添加到 .env
nano /path/to/project/.env
# 确保行: DEEPSEEK_API_KEY=sk-xxxxx
# 保存并退出

# 4. 重新加载环境
source /path/to/project/.env  # Linux/Mac

# 5. 验证
echo $DEEPSEEK_API_KEY
```

**获取 API 密钥**:

1. 访问 https://platform.deepseek.com
2. 注册或登录
3. 创建新 API 密钥
4. 复制密钥（格式: `sk-xxxxx`）

**如果密钥有效但仍然出错**:

```bash
# 测试 API 连接
python3 <<'EOF'
import os
from openai import OpenAI

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    print("❌ API key not set")
else:
    print(f"✓ API key found: {api_key[:10]}...")
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        print("✓ Connection test successful")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
EOF
```

---

### 3. Python 模块未找到

**症状**:
- "ModuleNotFoundError: No module named 'openai'"
- "No module named 'dotenv'"
- "ImportError"

**解决步骤**:

```bash
# 1. 检查依赖
pip list | grep -E "openai|dotenv"

# 2. 安装缺失的依赖
pip install openai python-dotenv

# 3. 或从项目的 requirements.txt 安装
pip install -r /path/to/project/requirements.txt

# 4. 验证
python3 -c "import openai; print('✓ openai installed')"
python3 -c "import dotenv; print('✓ dotenv installed')"
```

**使用虚拟环境**（推荐）:

```bash
# 创建虚拟环境
python3 -m venv /path/to/project/venv

# 激活
source /path/to/project/venv/bin/activate  # Linux/Mac
# 或
/path/to/project/venv\Scripts\activate  # Windows

# 安装依赖
pip install openai python-dotenv

# 测试
python3 .claude/commands/scripts/enhance.py "测试"
```

---

### 4. 权限被拒绝

**症状**:
- "Permission denied"
- "Access denied"
- 无法创建 `.claude` 目录

**解决步骤**:

```bash
# Linux/Mac: 检查权限
ls -la /path/to/project/.claude

# 修改权限
chmod -R u+w /path/to/project/.claude

# 或以更高权限运行
sudo prompt-enhance-install /path/to/project
```

**Windows**: 以管理员身份运行 PowerShell，然后：

```powershell
prompt-enhance-install "C:\path\to\project"
```

---

### 5. 增强超时

**症状**:
- "API request timeout"
- "Timeout after 60 seconds"
- 增强过程在 60+ 秒后失败

**解决步骤**:

```bash
# 1. 检查网络连接
ping api.deepseek.com

# 2. 增加超时时间（编辑 enhance.py）
# 修改 timeout=60 为 timeout=120

# 3. 检查 API 状态
# 访问 https://status.deepseek.com

# 4. 重试
/pe 您的提示词
```

**可能原因**:
- 网络连接缓慢
- DeepSeek API 响应慢
- 提示词太长

---

### 6. 符号链接问题（Windows）

**症状**:
- Windows 上符号链接无法创建
- 错误: "A required privilege is not held by the client"

**解决方案**:

这是预期行为。安装脚本会自动使用文件复制替代符号链接。

```bash
# 验证文件被复制而非链接
ls -la .claude/commands/pe.md
# 应该显示一个普通文件，而非 ->
```

**如果需要符号链接**:

```powershell
# 以管理员身份运行 PowerShell
New-Item -ItemType SymbolicLink -Path ".claude\commands\pe.md" `
  -Target "C:\path\to\source\pe.md"
```

---

### 7. 缓存问题

**症状**:
- 修改 `.env` 后仍使用旧密钥
- Claude Code 显示过时的命令
- 增强结果不变

**解决步骤**:

```bash
# 1. 清除 Claude Code 缓存
# 重启 Claude Code

# 2. 重新加载环境
source /path/to/project/.env  # Linux/Mac
# 或重启 terminal/PowerShell

# 3. 清除 Python 缓存
find /path/to/project -type d -name "__pycache__" -exec rm -rf {} +
find /path/to/project -type f -name "*.pyc" -delete
```

---

### 8. 跨项目安装失败

**症状**:
- 在其他项目中安装失败
- "Cannot find source files"
- "Target project is not valid"

**解决步骤**:

```bash
# 1. 验证源项目
cd /home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement
ls -la .claude/commands/pe.md

# 2. 验证目标项目存在
ls -la /path/to/xlerobot

# 3. 检查权限
test -w /path/to/xlerobot && echo "✓ Writable" || echo "❌ Not writable"

# 4. 使用绝对路径重试
prompt-enhance-install /absolute/path/to/xlerobot

# 5. 验证
prompt-enhance-verify
```

---

## 诊断命令

### 完整状态检查

```bash
#!/bin/bash
echo "=== Prompt Enhancement Diagnostic ==="
echo ""
echo "1. File Check:"
ls -la .claude/commands/pe.md
ls -la .claude/commands/scripts/enhance.py
echo ""
echo "2. Environment:"
echo "DEEPSEEK_API_KEY: $(echo $DEEPSEEK_API_KEY | cut -c1-10)..."
echo ""
echo "3. Python:"
python3 --version
python3 -c "import openai; print('✓ openai')" || echo "❌ openai"
python3 -c "import dotenv; print('✓ dotenv')" || echo "❌ dotenv"
echo ""
echo "4. API Test:"
python3 .claude/commands/scripts/enhance.py "test prompt" || echo "❌ API test failed"
```

### 收集调试信息

```bash
# 生成调试报告
{
  echo "=== System Info ==="
  uname -a
  echo ""
  echo "=== Python ==="
  python3 --version
  which python3
  echo ""
  echo "=== Installation Status ==="
  prompt-enhance-verify
  echo ""
  echo "=== Environment ==="
  echo "DEEPSEEK_API_KEY set: $([ -n $DEEPSEEK_API_KEY ] && echo 'yes' || echo 'no')"
} > debug_report.txt

cat debug_report.txt
```

---

## 获取帮助

### 检查清单

在寻求帮助前，请确保已尝试：

- [ ] 运行 `prompt-enhance-verify`
- [ ] 检查 .env 文件
- [ ] 重新安装：`prompt-enhance-install /path`
- [ ] 重启 Claude Code
- [ ] 检查网络连接
- [ ] 更新包：`pip install --upgrade prompt-enhancement`

### 报告问题

访问 GitHub issues：https://github.com/jodykwong/Prompt-Enhancement/issues

包含以下信息：

1. 错误消息（完整输出）
2. 诊断命令输出
3. 操作系统和版本
4. Python 版本
5. 安装方式（pip/npm/手动）
6. 重现步骤

### 获取支持

- 📖 [完整文档](../README.md)
- 🚀 [快速开始](./QUICKSTART.md)
- 📦 [安装指南](./INSTALL.md)
- 💬 GitHub Discussions

---

## 高级调试

### 启用调试模式

```bash
# 设置调试标志
export DEBUG=1
python3 .claude/commands/scripts/enhance.py "test"

# 查看详细日志
python3 -u .claude/commands/scripts/enhance.py "test" 2>&1 | tee debug.log
```

### 本地测试增强功能

```bash
python3 <<'EOF'
import asyncio
from enhanced_prompt_generator import enhance_prompt_with_context

async def test():
    result = await enhance_prompt_with_context(
        "测试提示词",
        project_path="/path/to/project",
        timeout=30
    )
    print(f"Success: {result['success']}")
    print(f"Enhanced: {result.get('enhanced', 'N/A')[:100]}")
    if result['error']:
        print(f"Error: {result['error']}")

asyncio.run(test())
EOF
```

---

## 常见错误代码

| 代码 | 含义 | 解决方案 |
|------|------|--------|
| 1 | 一般错误 | 检查错误信息，运行 `prompt-enhance-verify` |
| 2 | 找不到命令 | 重新安装：`prompt-enhance-install` |
| 3 | API 密钥错误 | 配置 API 密钥：`prompt-enhance-setup` |
| 4 | 网络错误 | 检查网络连接，重试 |
| 5 | 超时 | 增加超时时间或检查网络 |
| 127 | 命令未找到 | 检查 PATH，重新安装 pip 或 NPM 包 |
| 255 | 权限错误 | 检查文件权限，以管理员身份运行 |

---

问题依然存在？访问 GitHub Issues 获取帮助！
