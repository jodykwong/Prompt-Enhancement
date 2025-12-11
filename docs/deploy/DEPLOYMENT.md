# 部署与发布指南

## 概述

本文档涵盖 Prompt Enhancement 的完整部署流程——从源代码到在全球开发者的项目中可用。

## 部署架构

```
Prompt Enhancement
├── 源代码
│   ├── .claude/commands/pe.md          ← 核心命令定义
│   ├── .claude/commands/scripts/enhance.py  ← Claude Code 脚本
│   ├── enhanced_prompt_generator.py    ← 核心模块
│   ├── async_prompt_enhancer.py        ← 异步增强器
│   ├── context_collector.py            ← 上下文收集器
│   └── requirements.txt                 ← 依赖
│
├── Python 包 (pip)
│   └── packages/python/
│       ├── setup.py                    ← 包配置
│       ├── pyproject.toml              ← 现代配置
│       └── prompt_enhancement/         ← Python 包
│           ├── __init__.py
│           ├── installer.py            ← 安装逻辑
│           └── cli.py                  ← 命令行接口
│
├── NPM 包 (npm)
│   └── packages/npm/
│       ├── package.json                ← 包配置
│       └── scripts/
│           ├── install.js              ← 主安装脚本
│           ├── post-install.js         ← 后安装提示
│           ├── configure.js            ← 配置脚本
│           └── verify.js               ← 验证脚本
│
└── 一键安装脚本
    └── cli/
        ├── install.sh                  ← Linux/macOS
        ├── install.ps1                 ← Windows PowerShell
        └── install.py                  ← 跨平台 Python
```

## 安装方式

### 方式 1：使用 pip（推荐）

```bash
# 1. 安装包
pip install prompt-enhancement

# 2. 安装到项目
prompt-enhance-install /path/to/project

# 3. 配置 API 密钥
prompt-enhance-setup

# 4. 验证
prompt-enhance-verify
```

**优势**:
- Python 开发者的标准方式
- 自动依赖管理
- 易于更新：`pip install --upgrade prompt-enhancement`

**流程**:
1. pip 下载 `prompt-enhancement` 包
2. setup.py 配置后，`prompt-enhance-install` 命令可用
3. 命令调用 `PromptEnhancementInstaller` 类
4. 所有文件复制到目标项目的 `.claude/commands/`

### 方式 2：使用 NPM

```bash
# 1. 安装包
npm install -g @jodykwong/prompt-enhancement

# 2. 自动运行 post-install.js
# （显示使用说明）

# 3. 安装到项目
prompt-enhance-install /path/to/project

# 4. 配置
prompt-enhance-setup

# 5. 验证
prompt-enhance-verify
```

**优势**:
- Node.js 开发者的标准方式
- 易于集成到 npm scripts
- 全局安装更方便

**流程**:
1. npm 下载包到 `node_modules/`
2. 后安装脚本显示使用说明
3. `npm run install-to` 或 `prompt-enhance-install` 运行 install.js
4. 通过 Node.js 和 chalk 库完成跨平台安装

### 方式 3：手动安装（高级）

```bash
# Linux/macOS
bash cli/install.sh /path/to/project

# Windows PowerShell
.\cli\install.ps1 -ProjectPath "C:\path\to\project"

# 跨平台 Python
python3 cli/install.py /path/to/project
```

**优势**:
- 无需包管理器
- 对权限有完全控制
- 适合企业环境

## 文件部署清单

### 核心文件

| 文件 | 来源 | 目标 | 用途 |
|------|------|------|------|
| `pe.md` | `.claude/commands/` | `.claude/commands/pe.md` | /pe 命令定义 |
| `enhance.py` | `.claude/commands/scripts/` | `.claude/commands/scripts/enhance.py` | 增强执行脚本 |
| 核心模块 | 项目根目录 | `.claude/commands/` | Python 依赖 |

### 核心模块清单

```
enhanced_prompt_generator.py     - 增强器集成 (3KB)
async_prompt_enhancer.py         - 异步 API (12KB)
context_collector.py             - 上下文收集 (9KB)
enhance.py                       - 命令行脚本 (8KB)
```

### 配置文件

```
.env                             - 环境变量（API 密钥）
requirements.txt                 - Python 依赖
package.json                     - NPM 配置
```

## 发布流程

### 1. 测试

在发布前：

```bash
# Python 包测试
pip install -e packages/python/
python3 -m pytest tests/

# NPM 包测试
npm install packages/npm/
npm run test

# 跨项目测试
python3 cli/install.py /path/to/test/project
```

### 2. 版本管理

更新版本号：

```bash
# Python
packages/python/setup.py        # version = "x.y.z"
packages/python/pyproject.toml  # version = "x.y.z"

# NPM
packages/npm/package.json       # "version": "x.y.z"

# 源项目
.claude/commands/pe.md          # Version: x.y.z
```

### 3. 发布到 PyPI

```bash
# 安装工具
pip install build twine

# 构建包
cd packages/python/
python3 -m build

# 上传到 PyPI
twine upload dist/*

# 验证
pip install prompt-enhancement --upgrade
```

### 4. 发布到 NPM Registry

```bash
# 登录
npm login

# 发布
cd packages/npm/
npm publish

# 验证
npm view @jodykwong/prompt-enhancement
```

### 5. GitHub Release

```bash
# 标记版本
git tag v1.0.0

# 推送标签
git push origin v1.0.0

# 创建 Release
gh release create v1.0.0 \
  --title "Release v1.0.0" \
  --notes "$(cat CHANGELOG.md)"
```

## 验证部署

### 安装后验证

```bash
# Python 包
pip show prompt-enhancement
prompt-enhance-verify

# NPM 包
npm list -g @jodykwong/prompt-enhancement
prompt-enhance-verify

# 手动安装
ls -la /path/to/project/.claude/commands/pe.md
```

### 跨项目测试

```bash
# 在 xlerobot 中测试
prompt-enhance-install /home/sunrise/xlerobot

# 在 Prompt-Enhancement 中验证原始安装
prompt-enhance-verify
```

### 功能测试

```bash
# 在 Claude Code 中
/pe 修复登录页面的bug

# 应该看到：
# - ✨ 原始提示词
# - ✨ AI 增强版本
# - 📋 快速选择菜单
```

## 故障排除

### 常见部署问题

**问题 1：PyPI 上传失败**
```bash
# 检查凭证
cat ~/.pypirc

# 使用 token（推荐）
twine upload dist/* --skip-existing
```

**问题 2：NPM 发布权限**
```bash
# 确认账户
npm whoami

# 添加为 collaborator
npm owner add username package-name
```

**问题 3：版本冲突**
```bash
# 检查已发布版本
pip index versions prompt-enhancement
npm view prompt-enhancement versions

# 增加版本号并重新发布
```

## 维护

### 更新依赖

```bash
# Python
pip-audit           # 审计安全漏洞
pip freeze > requirements.txt

# NPM
npm audit           # 审计
npm update          # 更新
```

### 监控安装

```bash
# PyPI 统计
https://pypistats.org/packages/prompt-enhancement

# NPM 统计
npm-stat prompt-enhancement
```

## 发行说明模板

创建 `RELEASE_NOTES.md`:

```markdown
# Prompt Enhancement v1.0.0

## 新功能
- [ ] 列出新功能

## 改进
- [ ] 性能改进
- [ ] 用户体验改进

## 修复
- [ ] Bug 修复

## 安装
```bash
pip install prompt-enhancement
npm install -g @jodykwong/prompt-enhancement
```

## 升级
```bash
pip install --upgrade prompt-enhancement
npm install -g @jodykwong/prompt-enhancement@latest
```

## 文档
- [快速开始](./QUICKSTART.md)
- [完整安装指南](./INSTALL.md)
- [故障排除](./TROUBLESHOOTING.md)
```

## 自动化 CI/CD

使用 GitHub Actions 自动化发布：

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  publish-pypi:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install build twine
      - run: python -m build packages/python/
      - run: twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}

  publish-npm:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## 许可和法律

- 确保所有许可证正确
- 包括 MIT 许可证副本
- 在 README 中声明开源

## 联系方式

- GitHub: https://github.com/jodykwong/Prompt-Enhancement
- Issues: https://github.com/jodykwong/Prompt-Enhancement/issues
- Email: jodykwong@example.com
