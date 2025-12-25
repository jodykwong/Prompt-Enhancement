# 📚 Prompt Enhancement - 代码项目专用提示词增强系统

**当前版本**: v1.2.1-dev (Phase 1-3 完成) | **生产版本**: v1.1.0 ✅ | **最后更新**: 2025-12-25

一个**代码项目专用的 CLI 工具**，用智能文件发现和项目上下文来增强用户提示词，提升 Claude AI 对代码任务的响应质量。

## 🎯 v1.2.1 开发方向（当前分支：feature/v1.1-brownfield）

**核心功能**（10天计划）：
- 🔍 **智能文件发现** - 从模糊指令自动找到最相关的 5-10 个源文件（Day 1-3 ✅ 完成）
  - KeywordExtractor：中英文关键词提取
  - FileMatcher：精准文件匹配 + 语义映射
  - 18个测试，全部通过 ✅ | 关键词提取准确率 100% ✅

- 📋 **符号索引** - 提取函数/类签名而非完整代码（Day 4-5 ✅ 完成）
  - PythonSymbolExtractor：AST 解析（函数/类/装饰器）
  - JavaScriptSymbolExtractor：正则符号提取
  - SymbolCache：智能双层缓存（内存+磁盘）
  - 34个测试，全部通过 ✅ | 缓存命中率 >95% ✅

- 📝 **编码模板系统** - 5 种任务类型的结构化指导（Day 6-7 ✅ 完成）
  - CodingTemplate：5 个 YAML 模板（implement/fix/refactor/test/review）
  - TemplateTrigger：双语触发词匹配（中文+英文）
  - CodingTemplateManager：懒加载架构（0.17ms 初始化）
  - 38个测试，全部通过 ✅ | **性能提升 863x** ✅

- 🏗️ **AGENTS.md 自动生成** - 为新项目生成边界约束说明（Day 8-9 计划中）
  - 技术栈检测
  - 命令提取
  - 代码风格推断

- ⚡ **性能优化** - 冷启动 30s → 15s，缓存命中 10s → 5s（Day 10 计划中）

---

## ✅ v1.1.0 功能完整（生产就绪）

**生产版本特性** (28个用户故事 + 6个Epic):
- ⚡ **快速响应 `/pe` 命令** - 菜单确认工作流，用户掌控执行
- 🔍 **自动项目检测** - 识别技术栈和编码规范
- 🤖 **项目感知增强** - 基于项目上下文的智能优化
- 📊 **标准显示控制** - 实时显示检测到的编码规范
- 🛡️ **健壮错误处理** - 5级错误分类 + 3级优雅降级
- 📚 **新用户帮助系统** - 快速入门 + 交互式设置

**质量指标**：874个测试 ✅ 100% | 代码覆盖率 81% | 零缺陷

---

## 📌 已知问题和解决方案

### /pe 命令菜单确认流程
**问题**：v1.2.1 开发版中 `/pe` 命令无法等待用户菜单选择
**原因**：Claude Code `/commands/` 系统架构限制
**解决**：方案A - 用户手动从菜单选择，确保用户掌控权 ✅

详见：[/pe 命令诊断和解决方案](docs/GITHUB_ISSUE_TEMPLATE.md)

---

## 🚀 快速开始

### 当前开发版本使用 (/pe 命令)

```bash
/pe 您的提示词
```

**工作流**：
1. 脚本增强您的提示词
2. 显示原始 vs 增强版本对比
3. 显示菜单：选择执行、修改、重新增强或放弃
4. 您从菜单中选择操作，脚本执行

**菜单选项**：
- 1️⃣ **使用增强版本** - 复制粘贴给我执行
- 2️⃣ **修改后使用** - 编辑后复制粘贴给我
- 3️⃣ **重新增强** - 输入新提示词重新增强
- 4️⃣ **放弃此结果** - 取消并重新组织需求

---

## 📂 项目结构

```
Prompt-Enhancement/
├── src/prompt_enhancement/        # v1.2.1 新增强引擎
│   ├── file_discoverer.py         # 智能文件发现模块（Day 1 ✅）
│   ├── enhancement/               # 增强引擎核心
│   └── ...
│
├── .claude/commands/              # Claude Code 集成
│   ├── pe.md                      # /pe 命令定义
│   └── scripts/enhance.py         # 增强脚本
│
├── docs/
│   ├── v1.2.1_PRD.md             # 产品需求文档
│   ├── v1.2.1_IMPLEMENTATION_PLAN.md
│   ├── v1.2.1_WORKFLOW_STATUS.md
│   ├── GITHUB_ISSUE_TEMPLATE.md  # /pe 命令问题诊断 ⭐
│   └── ...
│
├── enhanced_prompt_generator.py   # v1.1.0 增强模块
├── async_prompt_enhancer.py       # 异步处理
└── README.md                      # 本文件
```

---

## 🛠️ 技术栈

- **语言**：Python 3.10+
- **构建**：Pip
- **AI 增强**：DeepSeek API
- **项目框架**：BMAD 平台（5个模块）
- **测试**：pytest（18+ 测试套件）
- **版本控制**：Git

---

## 📊 开发进度

| 阶段 | 计划 | 状态 | 测试 | 成就 |
|------|------|------|------|------|
| **Phase 1** | 智能文件发现 | ✅ 完成 | 18/18 ✅ | 关键词准确率 100% |
| **Phase 2** | 符号索引 | ✅ 完成 | 34/34 ✅ | 缓存命中率 >95% |
| **Phase 3** | 编码模板 | ✅ 完成 | 38/38 ✅ | **性能 863x 提升** ⚡ |
| **Phase 4** | AGENTS.md 生成 | 📅 计划中 | - | - |
| **Phase 5** | 性能优化 | 📅 计划中 | - | - |
| **总计** | | **✅ 75% 完成** | **90/90 ✅** | |

---

## 📖 文档

- **快速开始**：[QUICK_START.md](QUICK_START.md)
- **使用指南**：[USAGE_GUIDE.md](USAGE_GUIDE.md)
- **v1.2.1 路线图**：[docs/v1.2.1_PRD.md](docs/v1.2.1_PRD.md)
- **已知问题和解决方案**：[docs/GITHUB_ISSUE_TEMPLATE.md](docs/GITHUB_ISSUE_TEMPLATE.md) ⭐

---

## 🔧 安装和配置

### 环境要求
```
Python 3.10+
API Key: DeepSeek (https://platform.deepseek.com)
```

### 配置 .env
```bash
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY
```

---

[查看完整路线图 →](docs/v1.2.1_PRD.md)

## 🎯 核心功能 - v1.1.0 完整实现

### 📦 6个Epic - 28个用户故事

| Epic | 状态 | 故事数 | 关键功能 |
|------|------|--------|---------|
| **Epic 1** | ✅ | 4 | 快速响应 `/pe` 命令 (5-15秒) |
| **Epic 2** | ✅ | 10 | 自动项目检测 (6种语言 + 编码规范) |
| **Epic 3** | ✅ | 3 | 项目感知的提示增强 + 实现指南 |
| **Epic 4** | ✅ | 4 | 标准显示、YAML配置、用户覆盖 |
| **Epic 5** | ✅ | 4 | 5级错误分类 + 3级优雅降级 |
| **Epic 6** | ✅ | 3 | 新用户入门 + 交互式设置 |

### 📊 质量指标

```
测试覆盖: 874个测试 ✅ 100% 通过
代码覆盖: 81% (目标80%) ✅ 达成
缺陷统计: 0个P0/P1/P2/P3 ✅ 零缺陷
性能表现: 所有约束测试通过 ✅
架构质量: A级 (92/100分) ✅
总体状态: 生产就绪 ✅
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

