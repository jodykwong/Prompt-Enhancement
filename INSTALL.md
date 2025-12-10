# 📦 Prompt Enhancement - 安装指南

**Version**: 1.0.0 (P0.6)
**Last Updated**: 2025-12-11

快速安装 Prompt Enhancement 并集成到 Claude Code。

## 🚀 一键安装（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/Prompt-Enhancement.git
cd Prompt-Enhancement

# 2. 运行安装脚本
./install.sh
```

安装脚本会自动完成：
- ✅ 检查系统依赖（Python 3.8+）
- ✅ 安装 Python 依赖包
- ✅ 提示您输入 DeepSeek API Key
- ✅ 安装 `/pe` 命令到 Claude Code
- ✅ 验证安装是否成功

## 📋 系统要求

### 必需
- **Python**: 3.8 或更高版本
- **pip**: Python 包管理器
- **Claude Code**: 已安装并配置

### 可选
- **Git**: 用于克隆仓库（也可下载ZIP）

## 🔧 手动安装

如果自动安装失败，可以手动安装：

### Step 1: 克隆项目

```bash
git clone https://github.com/yourusername/Prompt-Enhancement.git
cd Prompt-Enhancement
```

或下载ZIP并解压到：
```
~/Documents/augment-projects/Prompt-Enhancement/
```

### Step 2: 安装依赖

```bash
pip3 install -r requirements.txt
```

### Step 3: 配置 API Key

创建 `.env` 文件：

```bash
cat > .env << 'EOF'
DEEPSEEK_API_KEY=your-api-key-here
EOF
```

获取API Key：https://platform.deepseek.com

### Step 4: 安装 Claude Code 命令

```bash
# 创建目录
mkdir -p ~/.claude/commands/scripts

# 复制文件
cp .claude/commands/scripts/enhance.py ~/.claude/commands/scripts/
cp .claude/commands/pe.md ~/.claude/commands/

# 设置权限
chmod +x ~/.claude/commands/scripts/enhance.py
```

### Step 5: 验证安装

重启 Claude Code，然后测试：

```
/pe "测试提示词增强"
```

应该看到增强后的提示词。

## 🔐 API Key 配置详解

### 方式 1: .env 文件（推荐）

在项目根目录创建 `.env` 文件：

```bash
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
```

### 方式 2: 环境变量

```bash
export DEEPSEEK_API_KEY='sk-xxxxxxxxxxxxxxxxxxxxx'

# 永久设置（添加到 ~/.zshrc 或 ~/.bashrc）
echo 'export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxx"' >> ~/.zshrc
source ~/.zshrc
```

### 方式 3: 重新运行安装脚本

```bash
./install.sh
# 选择 "y" 更新 API key
```

## 📍 文件位置

安装后的文件位置：

```
项目源代码:
~/Documents/augment-projects/Prompt-Enhancement/
├── .env                           # API key配置
├── install.sh                     # 安装脚本
├── requirements.txt               # Python依赖
├── enhanced_prompt_generator.py   # P0.6 核心模块
├── async_prompt_enhancer.py      # 异步增强器
├── context_collector.py          # 上下文收集器
└── ...

Claude Code 集成:
~/.claude/
├── commands/
│   ├── pe.md                      # /pe 命令定义
│   └── scripts/
│       └── enhance.py             # 增强脚本
```

## 🧪 测试安装

### 1. 基础测试

```bash
# 测试脚本可执行
python3 ~/.claude/commands/scripts/enhance.py
# 应该显示: "Error: No prompt provided"

# 测试 API key
python3 ~/.claude/commands/scripts/enhance.py "test" 2>&1 | head -5
# 应该显示增强结果或明确的错误信息
```

### 2. Claude Code 测试

在 Claude Code 中：

```
/pe "简单测试"
```

预期输出：
- 显示原始提示词
- 显示增强后的提示词
- 提供使用建议
- **命令结束，不自动执行**

## ❓ 常见问题

### Q1: "python3: command not found"

**解决方案**：安装 Python 3
```bash
# macOS
brew install python3

# Linux (Ubuntu/Debian)
sudo apt-get install python3 python3-pip
```

### Q2: "Cannot find Prompt-Enhancement project"

**解决方案**：确保项目路径正确
```bash
# 检查项目是否存在
ls ~/Documents/augment-projects/Prompt-Enhancement/

# 如果不存在，创建目录并移动项目
mkdir -p ~/Documents/augment-projects/
mv /path/to/Prompt-Enhancement ~/Documents/augment-projects/
```

### Q3: "DEEPSEEK_API_KEY not configured"

**解决方案**：
```bash
cd ~/Documents/augment-projects/Prompt-Enhancement
echo 'DEEPSEEK_API_KEY=your-key-here' > .env
```

### Q4: "/pe command not found in Claude Code"

**解决方案**：
1. 重启 Claude Code
2. 检查文件是否存在：
   ```bash
   ls -la ~/.claude/commands/pe.md
   ls -la ~/.claude/commands/scripts/enhance.py
   ```
3. 如果缺失，重新运行 `./install.sh`

### Q5: "增强结果后 Claude 自动执行了任务"

这是**旧版本**的行为。新版本（1.0.0）采用 **Display-Only 模式**：
- ✅ 只显示增强结果
- ❌ 不会自动执行
- ✅ 用户手动复制并执行

如果遇到此问题，请重新安装：
```bash
./install.sh
```

## 🔄 更新安装

已安装旧版本？更新到 1.0.0：

```bash
cd ~/Documents/augment-projects/Prompt-Enhancement
git pull origin main
./install.sh
```

安装脚本会自动更新所有文件。

## 🗑️ 卸载

```bash
# 删除 Claude Code 命令
rm -f ~/.claude/commands/pe.md
rm -f ~/.claude/commands/scripts/enhance.py

# 删除项目（可选）
rm -rf ~/Documents/augment-projects/Prompt-Enhancement
```

## 📞 获取帮助

- **文档**: [README.md](README.md)
- **使用指南**: [USAGE_GUIDE.md](USAGE_GUIDE.md)
- **API文档**: [API_REFERENCE.md](API_REFERENCE.md)
- **GitHub Issues**: https://github.com/yourusername/Prompt-Enhancement/issues

---

**享受提示词增强！** 🚀
