# @jodykwong/prompt-enhancement

**版本**: 2.0.0 | **状态**: ✅ 稳定版本

AI-powered prompt enhancement tool for development workflows.

跨项目部署工具库——在任何 Claude Code 项目中使用 `/pe` 命令！

> **简体中文**: 用 AI 和项目上下文来优化您的提示词

## Installation

```bash
npm install -g @jodykwong/prompt-enhancement
```

Or with `npm`/`yarn`:

```bash
npm install --save-dev @jodykwong/prompt-enhancement
```

## Quick Start

### 1. Install to your Claude Code project

```bash
# Install to current directory
prompt-enhance-install

# Install to a specific project
prompt-enhance-install /path/to/xlerobot
```

### 2. Configure DeepSeek API key

```bash
prompt-enhance-setup
```

### 3. Verify installation

```bash
prompt-enhance-verify
```

## Usage

Once installed in your Claude Code project, use:

```bash
/pe 修复登录页面的bug
/pe 添加用户配置文件导出功能支持 CSV 和 JSON 格式
/pe 优化数据库查询性能，p99 延迟 < 100ms
```

## Available Commands

```bash
# Install to a project
prompt-enhance-install [path]

# Interactive setup
prompt-enhance-setup

# Verify installation
prompt-enhance-verify
```

## What It Does

1. **Analyzes your prompt** - Understands your intent
2. **Collects project context** - Scans structure, tech stack, git history
3. **Enhances with AI** - Generates detailed steps, acceptance criteria, context
4. **Shows comparison** - Original vs enhanced version side-by-side
5. **User control** - You choose the next action

## Requirements

- Node.js 14+
- Claude Code
- DeepSeek API key (free at https://platform.deepseek.com)

## Configuration

### Environment Variables

```bash
DEEPSEEK_API_KEY=sk-xxxxx  # Your DeepSeek API key
```

### Setup Methods

**Option 1: Using setup command**
```bash
prompt-enhance-setup
```

**Option 2: Manual .env file**
```bash
echo "DEEPSEEK_API_KEY=your-api-key-here" > /path/to/project/.env
```

## Documentation

- [Installation Guide](../../docs/deploy/INSTALL.md)
- [Quick Start](../../docs/deploy/QUICKSTART.md)
- [Troubleshooting](../../docs/deploy/TROUBLESHOOTING.md)

## License

MIT

## Support

- GitHub: https://github.com/jodykwong/Prompt-Enhancement
- Issues: https://github.com/jodykwong/Prompt-Enhancement/issues
