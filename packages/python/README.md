# Prompt Enhancement - Python Package

**版本**: 2.0.0 | **状态**: ✅ 稳定版本

AI-powered prompt enhancement tool for development workflows.

跨项目部署工具库——在任何 Claude Code 项目中使用 `/pe` 命令！

## Installation

### Using pip

```bash
pip install prompt-enhancement
```

### From source

```bash
git clone https://github.com/jodykwong/Prompt-Enhancement
cd Prompt-Enhancement/packages/python
pip install -e .
```

## Quick Start

### Install to a project

```bash
# Install to current directory
prompt-enhance-install

# Install to a specific project
prompt-enhance-install /path/to/xlerobot
```

### Configure API Key

```bash
prompt-enhance-setup
```

Or manually:

```bash
# Create .env file in target project
echo "DEEPSEEK_API_KEY=your-api-key-here" > /path/to/project/.env
```

### Verify Installation

```bash
prompt-enhance-verify
```

## Usage

Once installed in your Claude Code project:

```bash
/pe 修复登录页面的bug
/pe 添加用户配置文件导出功能支持 CSV 和 JSON 格式
/pe 优化数据库查询性能，p99 延迟 < 100ms
```

## What It Does

1. **Analyzes your prompt** - Understands your intent
2. **Collects project context** - Scans structure, tech stack, git history
3. **Enhances with AI** - Generates structured steps, acceptance criteria, context
4. **Shows comparison** - Original vs enhanced version side-by-side
5. **User control** - You choose the next action (use, modify, re-enhance, reject)

## Requirements

- Python 3.8+
- Claude Code
- DeepSeek API key (free at https://platform.deepseek.com)

## Environment Variables

```bash
DEEPSEEK_API_KEY=sk-xxxxx  # Your DeepSeek API key
```

## Dependencies

- `openai>=1.0.0` - For API integration
- `python-dotenv>=1.0.0` - For environment configuration

## Documentation

- [Installation Guide](../../docs/deploy/INSTALL.md)
- [Quick Start](../../docs/deploy/QUICKSTART.md)
- [Troubleshooting](../../docs/deploy/TROUBLESHOOTING.md)

## License

MIT

## Support

- GitHub: https://github.com/jodykwong/Prompt-Enhancement
- Issues: https://github.com/jodykwong/Prompt-Enhancement/issues
