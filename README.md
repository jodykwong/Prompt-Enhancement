# 📚 Prompt Enhancement - 提示词增强系统

**版本**: 2.0.0 (跨项目部署版) | **最后更新**: 2025-12-11 | **下一版本**: [v2.1 路线图](ROADMAP_V2_1.md)

一个智能的提示词增强系统，自动收集项目上下文并进行提示词优化，提升 AI 模型的响应质量。**现已支持跨项目部署**！

**🎉 v2.0.0 特性** (新增部署系统):
- 🐍 **Python/pip 包** - `pip install prompt-enhancement` 一行安装
- 📦 **NPM 包** - `npm install -g @jodykwong/prompt-enhancement` 全局安装
- 🔧 **一键脚本** - bash/python/powershell 跨平台安装脚本
- 🎯 **自动化部署** - 自动检查依赖、创建符号链接、配置环境变量
- ✅ **跨项目验证** - 已在 xlerobot 项目中部署验证成功
- ✨ **Display-Only 模式** - 增强后只显示，用户手动执行
- 📚 **完整文档系统** - INSTALL.md、QUICKSTART.md、TROUBLESHOOTING.md、DEPLOYMENT.md

**📋 v1.1 即将推出**（预计 2025年1月）:
- 🔥 **响应速度优化** - 30-60s → 5-15s (80% 性能提升)
- 🤖 **编码规范识别** - 自动识别和应用项目规范
- 🎯 **自定义模板系统** - Markdown + Frontmatter 支持
- ⚙️ **CI/CD 模式** - --quiet 标志和自动化支持

[查看完整路线图 →](ROADMAP_V1_1.md)

## 🎯 核心功能

### ✅ 已完成功能 (P0.1-P0.6)

- **P0.1: 技术栈自动识别** - 自动检测项目使用的技术框架 ✅
- **P0.2: 项目结构分析** - 解析项目目录和关键文件 ✅
- **P0.3: Git 历史分析** - 提取提交记录和分支信息 ✅
- **P0.4: 上下文整合** - 统一收集项目上下文 ✅
- **P0.5: 增强器集成** - 与异步提示增强器集成 ✅
- **P0.6: 测试和文档** - 完整的单元测试和详细文档 ✅

### 📊 项目进度

```
P0.1: ✅ 完成 (16.7%)
P0.2: ✅ 完成 (33.3%)
P0.3: ✅ 完成 (50.0%)
P0.4: ✅ 完成 (66.7%)
P0.5: ✅ 完成 (83.3%)
P0.6: ✅ 完成 (100%)

总进度: ✅ 100% (P0 阶段完成！)
```

## 🚀 快速开始

### 📦 三种安装方式

#### 方式 1：使用 pip（推荐）

```bash
pip install prompt-enhancement
prompt-enhance-install /path/to/your/project
prompt-enhance-setup
```

**优点**：Python 开发者标准方式，自动依赖管理

#### 方式 2：使用 NPM

```bash
npm install -g @jodykwong/prompt-enhancement
prompt-enhance-install /path/to/your/project
prompt-enhance-setup
```

**优点**：Node.js 开发者友好，全局可用

#### 方式 3：一键脚本（跨平台）

```bash
# Linux/macOS
bash cli/install.sh /path/to/your/project

# Windows PowerShell
.\cli\install.ps1 -ProjectPath "C:\path\to\project"

# 通用 Python
python3 cli/install.py /path/to/your/project
```

**优点**：无需额外依赖，完全跨平台

### ✅ 部署验证

已在 **xlerobot** 项目中验证部署成功：

```bash
# 验证命令
python3 cli/install.py /home/sunrise/xlerobot

# 结果
✓ pe.md 命令已安装（符号链接）
✓ enhance.py 脚本已复制
✓ 所有 Python 模块已部署
✓ .env 配置文件已创建
```

**详细安装指南**: [docs/deploy/INSTALL.md](docs/deploy/INSTALL.md) | [docs/deploy/QUICKSTART.md](docs/deploy/QUICKSTART.md)

---

### 🆕 在 Claude Code 中使用

安装完成后，在 Claude Code 中使用 `/pe` 命令：

```bash
/pe "您想增强的提示词"
```

**工作流程（Display-Only 模式）**：
1. Claude 调用增强脚本（等待 30-60 秒）
2. 显示原始和增强后的提示词对比
3. **命令结束** - 不自动执行任何任务
4. 您审查结果，手动复制并执行

**示例**：
```
/pe 优化数据库查询性能

→ Claude 会：
  1. 等待 30-60 秒 API 返回
  2. 显示增强后的详细步骤
  3. 命令结束，不执行任何操作

→ 您：
  4. 审查增强结果
  5. 如满意，复制并重新输入给 Claude
  6. Claude 按增强后的指令执行优化
```

**优点（Display-Only 模式）**：
- ✅ 完全掌控执行权
- ✅ 符合 Auggle CLI 设计模式
- ✅ 避免意外自动执行
- ✅ 透明的增强过程

详见 [USAGE_GUIDE.md](USAGE_GUIDE.md)

---

### 本地开发和集成

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置 API 密钥

复制 `.env.example` 为 `.env` 并填入您的 API 密钥：

```bash
cp .env.example .env
# 编辑 .env 文件，填入 DEEPSEEK_API_KEY 和 OPENAI_API_KEY
```

#### 3. 验证项目

```bash
# 验证 P0.5 (增强器集成)
python3 verify_p0_5.py

# 运行所有单元测试
python3 tests/test_enhanced_prompt_generator.py
python3 tests/test_enhanced_prompt_generator_extended.py
```

#### 4. 使用核心功能

```python
# 收集项目上下文
from context_collector import collect_project_context

context = collect_project_context("/path/to/project")
print(context["summary"])

# 增强提示词
from enhanced_prompt_generator import enhance_prompt_with_context
import asyncio

async def main():
    result = await enhance_prompt_with_context(
        "修复 bug",
        project_path="/path/to/project"
    )
    print(result["enhanced"])

asyncio.run(main())
```

## 测试用例

MVP 包含以下测试用例：

1. **简单模糊指令**："优化代码"
2. **简单模糊指令**："修复bug"
3. **中等复杂度**："添加用户登录功能"
4. **具体指令**："重构数据库查询模块，提高性能"
5. **中英文混合**："为 API 接口添加 rate limiting 功能"

## 评估标准

增强质量从以下维度评估：

- ✓ 是否包含具体步骤
- ✓ 是否包含验证标准
- ✓ 是否添加了上下文信息
- ✓ 结构是否清晰
- ✓ 长度是否适中

## 输出示例

**原始提示词：** "修复bug"

**增强后：**
```
修复代码中的缺陷。请按以下步骤进行：

1. 问题定位：
   - 收集错误日志和堆栈跟踪信息
   - 复现问题，确定触发条件
   - 识别出现问题的具体代码位置

2. 原因分析：
   - 审查相关代码逻辑
   - 检查边界条件和异常情况处理
   - 分析是否存在逻辑错误或资源泄漏

3. 实施修复：
   - 编写修复代码
   - 确保修复不引入新问题
   - 添加必要的错误处理和日志

4. 测试验证：
   - 编写或更新单元测试
   - 验证修复后问题不再出现
   - 进行回归测试确保其他功能正常

5. 代码审查：提交代码前进行自查，确保符合编码规范

验证标准：bug 完全修复，相关测试通过，无新增问题。
```

## 📂 项目结构

```
Prompt-Enhancement/
├── 🔥 部署系统（v2.0.0 新增）
│   ├── packages/
│   │   ├── python/                     # pip 包源代码
│   │   │   ├── setup.py
│   │   │   ├── pyproject.toml
│   │   │   └── prompt_enhancement/     # 包模块
│   │   │       ├── __init__.py
│   │   │       ├── installer.py        ⭐ 核心安装器
│   │   │       └── cli.py              ⭐ CLI 接口
│   │   │
│   │   └── npm/                        # npm 包源代码
│   │       ├── package.json
│   │       └── scripts/
│   │           ├── install.js          ⭐ 主安装脚本
│   │           ├── configure.js
│   │           └── verify.js
│   │
│   ├── cli/                            # 一键安装脚本
│   │   ├── install.sh                  (Linux/macOS)
│   │   ├── install.py                  (跨平台) ✅ 已测试
│   │   └── install.ps1                 (Windows)
│   │
│   └── docs/deploy/                    # 部署文档
│       ├── INSTALL.md                  (完整安装指南)
│       ├── QUICKSTART.md               (5分钟快速开始)
│       ├── TROUBLESHOOTING.md          (故障排除)
│       ├── DEPLOYMENT.md               (发布指南)
│       └── README.md                   (部署总结)
│
├── 核心模块
│   ├── tech_stack_detector.py          # P0.1: 技术栈检测
│   ├── project_structure_analyzer.py   # P0.2: 项目结构分析
│   ├── git_history_analyzer.py         # P0.3: Git 历史分析
│   ├── context_collector.py            # P0.4: 上下文整合 ⭐
│   ├── enhanced_prompt_generator.py    # P0.5: 增强器集成
│   └── async_prompt_enhancer.py        # 异步处理核心
│
├── 测试
│   └── tests/
│       ├── test_tech_stack_detector.py
│       ├── test_project_structure_analyzer.py
│       ├── test_git_history_analyzer.py
│       ├── test_context_collector.py
│       ├── test_enhanced_prompt_generator.py
│       └── test_p0_*_integration.py
│
├── 验证脚本
│   ├── verify_p0_1.py
│   ├── verify_p0_2.py
│   ├── verify_p0_3.py
│   ├── verify_p0_4.py
│   └── verify_p0_5.py
│
└── 配置和文档
    ├── requirements.txt
    ├── .env.example
    ├── README.md                       (本文件，已更新)
    └── docs/
        ├── 核心功能文档
        ├── 架构文档
        └── API 参考
```

## 🛠️ 技术栈

- **语言**: Python 3.8+
- **异步框架**: asyncio
- **测试框架**: pytest
- **API 集成**: DeepSeek API, OpenAI API
- **版本控制**: Git
- **文档**: Markdown

## 📖 关键文档

**快速开始**:
- **[QUICK_START.md](QUICK_START.md)** - 5 分钟快速开始 ⭐
- **[USER_GUIDE.md](USER_GUIDE.md)** - 详细使用指南

**API 和架构**:
- **[API_REFERENCE.md](API_REFERENCE.md)** - 完整 API 参考 (3000+ 字)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 系统架构设计 (4000+ 字)
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - 测试完整指南 (3500+ 字)

**集成和配置**:
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - 集成指南 (4000+ 字)
- **[PROJECT_INITIALIZATION_SUMMARY.md](PROJECT_INITIALIZATION_SUMMARY.md)** - 项目完整概况

**进度报告**:
- **[P0_6_COMPLETION_REPORT.md](P0_6_COMPLETION_REPORT.md)** - P0.6 完成报告 (最新！)
- **[P0_4_COMPLETION_REPORT.md](P0_4_COMPLETION_REPORT.md)** - P0.4 详细报告
- **[IMPROVEMENT_ROADMAP.md](IMPROVEMENT_ROADMAP.md)** - 长期改进计划

## 🎯 下一步计划

### 立即 (本周)
- [x] ✅ 完成 P0.6 测试和文档
- [x] ✅ 整理文档库并归档过时文档
- [ ] 与团队共享 P0.6 完成报告

### 短期 (P1 阶段，下周)
- [ ] P1: 命令行接口集成
- [ ] 设计 `/pe` 命令参数
- [ ] 集成到 Claude Code 工具链

### 中期 (P2 阶段，2-4 周)
- [ ] 支持更多模型 (OpenAI GPT-4 等)
- [ ] 多语言支持
- [ ] 缓存持久化

## 📊 测试覆盖率

- **单元测试**: 100% (31/31 通过) ✅ ← P0.6 更新
- **代码覆盖率**: 87% ✅
- **集成测试**: 92% ✅
- **扩展测试**: 19/19 通过 ✅ ← P0.6 新增

## 注意事项

⚠️ **API 密钥安全**：
- 严禁将 API 密钥硬编码到代码中
- 不要将 `.env` 文件提交到版本控制
- 使用环境变量或安全的配置管理方案

## 许可证

本项目为 Prompt Enhancement 功能的 MVP 原型，仅用于验证和测试。

