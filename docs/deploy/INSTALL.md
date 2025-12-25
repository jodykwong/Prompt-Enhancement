# 完整安装指南

## 安装提示词增强功能到您的项目

Prompt Enhancement 支持多种安装方式。选择最适合您的方式。

## 方式 1：使用 Python/pip（推荐）

如果您的项目使用 Python 或已安装 Python 3.8+：

### 1. 安装 pip 包

```bash
pip install prompt-enhancement
```

### 2. 安装到项目

```bash
# 安装到当前目录
prompt-enhance-install

# 安装到其他项目
prompt-enhance-install /path/to/xlerobot
```

### 3. 配置 API 密钥

```bash
# 交互式配置
prompt-enhance-setup

# 或手动编辑 .env 文件
echo "DEEPSEEK_API_KEY=sk-your-key" >> /path/to/project/.env
```

### 4. 验证

```bash
prompt-enhance-verify
```

## 方式 2：使用 NPM

如果您的项目使用 Node.js：

### 1. 安装 NPM 包

```bash
npm install -g @jodykwong/prompt-enhancement

# 或用于项目级安装
npm install --save-dev @jodykwong/prompt-enhancement
```

### 2. 安装到项目

```bash
prompt-enhance-install /path/to/xlerobot
```

### 3. 配置

```bash
prompt-enhance-setup
```

### 4. 验证

```bash
prompt-enhance-verify
```

## 方式 3：手动安装（高级）

对于不想使用包管理器的用户：

### 1. 克隆或下载源代码

```bash
git clone https://github.com/jodykwong/Prompt-Enhancement
cd Prompt-Enhancement
```

### 2. 运行安装脚本

**Linux / macOS:**
```bash
bash cli/install.sh /path/to/xlerobot
```

**Windows (PowerShell):**
```powershell
.\cli\install.ps1 -ProjectPath "C:\path\to\xlerobot"
```

**跨平台 (Python):**
```bash
python3 cli/install.py /path/to/xlerobot
```

### 3. 配置 .env

```bash
cd /path/to/xlerobot
echo "DEEPSEEK_API_KEY=sk-your-key" > .env
```

## 验证您的安装

### 检查文件

```bash
# 在您的项目目录中
ls -la .claude/commands/pe.md
ls -la .claude/commands/scripts/enhance.py
cat .env | grep DEEPSEEK_API_KEY
```

### 运行验证命令

```bash
prompt-enhance-verify
```

预期输出：

```
✅ .claude 目录
✅ .claude/commands 目录
✅ pe.md 命令
✅ enhance.py 脚本
✅ .env 文件
✅ DEEPSEEK_API_KEY (环境变量)
```

## 配置 DeepSeek API 密钥

### 获取 API 密钥

1. 访问 https://platform.deepseek.com
2. 注册或登录账户
3. 创建新的 API 密钥
4. 复制密钥

### 设置方式

**方式 A：交互式配置（推荐）**
```bash
prompt-enhance-setup
```

**方式 B：编辑 .env 文件**
```bash
# 在您的项目根目录
echo "DEEPSEEK_API_KEY=sk-your-key-here" >> .env
```

**方式 C：环境变量**
```bash
# Linux / macOS
export DEEPSEEK_API_KEY="sk-your-key-here"

# Windows (PowerShell)
$env:DEEPSEEK_API_KEY = "sk-your-key-here"
```

**方式 D：在 Claude Code 中设置**
```
Settings → Environment Variables → Add
Name: DEEPSEEK_API_KEY
Value: sk-your-key-here
```

## 安装后下一步

### 1. 测试功能

在 Claude Code 中输入：

```bash
/pe 修复登录页面的bug
```

应该看到：
- ✨ 您的原始提示词
- ✨ AI 增强后的版本
- 📋 快速选择菜单

### 2. 查看 /pe 命令文档

```bash
/pe
# 或查看完整文档
cat /path/to/project/.claude/commands/pe.md
```

### 3. 在其他项目中安装

```bash
# 安装到另一个项目
prompt-enhance-install /path/to/another/project

# 配置 API 密钥
cd /path/to/another/project
prompt-enhance-setup
```

## 故障排除

### 常见问题

**Q: 我找不到 /pe 命令**
```bash
# 检查安装状态
prompt-enhance-verify

# 重新安装
prompt-enhance-install /path/to/project
```

**Q: API 密钥错误**
```bash
# 检查 API 密钥
echo $DEEPSEEK_API_KEY  # Linux/Mac
echo $env:DEEPSEEK_API_KEY  # Windows

# 如果为空，编辑 .env
nano .env  # 编辑并保存
```

**Q: Python 模块未找到**
```bash
# 安装依赖
pip install -r requirements.txt

# 或单独安装
pip install openai python-dotenv
```

**Q: 符号链接不工作（Windows）**
这是正常的，安装脚本会自动使用文件复制替代。

**Q: 权限被拒绝**
```bash
# Linux/Mac: 确保有写权限
chmod -R u+w /path/to/project/.claude

# 或以管理员身份运行
sudo prompt-enhance-install /path/to/project
```

更详细的故障排除：[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

## 卸载

### 使用 pip

```bash
pip uninstall prompt-enhancement
```

### 使用 NPM

```bash
npm uninstall -g @jodykwong/prompt-enhancement
```

### 手动移除（从项目中）

```bash
# 移除 /pe 命令
rm /path/to/project/.claude/commands/pe.md
rm -rf /path/to/project/.claude/commands/scripts

# 移除模块
rm /path/to/project/.claude/commands/*.py
```

## 获取帮助

- 📖 文档: https://github.com/jodykwong/Prompt-Enhancement
- 🐛 报告问题: https://github.com/jodykwong/Prompt-Enhancement/issues
- 💬 讨论: https://github.com/jodykwong/Prompt-Enhancement/discussions

## 下一步

- [快速开始指南](./QUICKSTART.md)
- [故障排除](./TROUBLESHOOTING.md)
- [项目 README](../../README.md)
