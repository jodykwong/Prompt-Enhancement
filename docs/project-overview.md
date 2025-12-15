# 项目概览 - Prompt Enhancement

**项目名称：** Prompt Enhancement（提示词增强系统）

**当前版本：** v2.0.0（跨项目部署版）| **下一版本：** v1.1（性能优化版）

**最后更新：** 2025-12-15

---

## 📋 项目概述

Prompt Enhancement 是一个智能的提示词增强系统，自动收集项目上下文并进行提示词优化，提升 AI 模型的响应质量。该系统支持跨项目部署，可以作为独立工具或集成到开发工作流中。

### 核心价值主张

- 🎯 **自动上下文收集**：自动分析项目结构、技术栈、Git历史
- 🚀 **智能提示增强**：利用 AI 模型优化和扩展用户提示词
- 📦 **多平台部署**：支持 pip、npm、CLI 脚本安装
- 🔧 **无缝集成**：可集成到 Claude Code、IDE 和 CI/CD 流程
- ⚡ **高性能设计**：v1.1 目标将响应时间从 30-60s 降低到 5-15s

---

## 🏗️ 项目类型和架构

**项目类型：** Python CLI 工具（单一整体项目/Monolith）

**架构模式：** 模块化管道架构
- **P0.1 层**：技术栈检测（tech_stack_detector.py）
- **P0.2 层**：项目结构分析（project_structure_analyzer.py）
- **P0.3 层**：Git 历史分析（git_history_analyzer.py）
- **P0.4 层**：上下文整合（context_collector.py）
- **P0.5 层**：增强器集成（enhanced_prompt_generator.py）

---

## 🛠️ 技术栈

| 类别 | 技术 | 版本 | 说明 |
|-----|------|------|------|
| **语言** | Python | 3.8+ | 核心开发语言 |
| **异步框架** | asyncio | 标准库 | 异步操作支持 |
| **API 集成** | OpenAI API | 1.0.0+ | 主要 LLM 提供商 |
| **配置管理** | python-dotenv | 1.0.0+ | 环境变量管理 |
| **测试框架** | pytest | (implicit) | 单元测试框架 |
| **版本控制** | Git | - | 历史分析数据源 |
| **文档** | Markdown | - | 项目和 API 文档 |
| **部署** | pip/npm/bash | v2.0.0 | 多平台安装系统 |

---

## 📂 项目结构

### 根目录结构
```
Prompt-Enhancement/
├── src/                           # 源代码目录
│   └── v1_1/                     # v1.1 版本代码
│
├── cli/                           # 部署脚本
│   ├── install.sh                # Linux/macOS 安装
│   ├── install.py                # 跨平台安装（已测试）
│   └── install.ps1               # Windows PowerShell 安装
│
├── 核心模块（根目录）
│   ├── context_collector.py      # P0.4: 上下文整合 ⭐
│   ├── enhanced_prompt_generator.py  # P0.5: 增强器
│   ├── async_prompt_enhancer.py  # 异步处理核心
│   ├── tech_stack_detector.py    # P0.1: 技术检测
│   ├── project_structure_analyzer.py  # P0.2: 结构分析
│   └── git_history_analyzer.py   # P0.3: Git 分析
│
├── 测试文件
│   ├── tests/                     # 单元测试目录
│   ├── verify_p0_*.py            # 各阶段验证脚本
│   └── demo_*.py                 # 演示和集成测试
│
├── 配置文件
│   ├── requirements.txt          # Python 依赖
│   └── .env.example              # 环境变量模板
│
├── 文档（44+ 文件）
│   ├── 快速开始
│   │   ├── README.md             # 主文档
│   │   ├── QUICK_START.md        # 5分钟快速开始
│   │   └── START_HERE.md         # 入门指南
│   │
│   ├── 核心文档
│   │   ├── ARCHITECTURE.md       # 系统架构
│   │   ├── API_REFERENCE.md      # API 参考
│   │   └── INTEGRATION_GUIDE.md  # 集成指南
│   │
│   ├── 版本和计划
│   │   ├── DESIGN_V1.1.md        # v1.1 设计文档
│   │   ├── ROADMAP_V1_1.md       # v1.1 路线图
│   │   ├── P0_*_COMPLETION_REPORT.md  # 各阶段报告
│   │   └── RELEASE_NOTES.md      # 发布说明
│   │
│   ├── 部署文档
│   │   ├── INSTALL.md            # 安装指南
│   │   ├── DEPLOYMENT.md         # 部署指南
│   │   └── RELEASE_INSTRUCTIONS.md   # 发布步骤
│   │
│   └── docs/                      # 文档子目录
│       ├── deploy/               # 部署相关文档
│       └── sprint-artifacts/     # Sprint 交付物
│
├── 数据和归档
│   ├── ARCHIVE/                  # 归档目录
│   └── demo_test_results.json    # 测试结果
│
└── 其他
    ├── .bmad/                    # BMad 工作流配置
    ├── .claude/                  # Claude Code 配置
    ├── .env                      # 环境变量（实际）
    └── CHANGELOG.md              # 变更历史
```

---

## 📊 项目现状和进度

### P0 阶段完成情况

| 阶段 | 名称 | 状态 | 说明 |
|------|------|------|------|
| **P0.1** | 技术栈自动识别 | ✅ 完成 | 自动检测项目框架和依赖 |
| **P0.2** | 项目结构分析 | ✅ 完成 | 解析目录和关键文件 |
| **P0.3** | Git 历史分析 | ✅ 完成 | 提取提交记录和分支信息 |
| **P0.4** | 上下文整合 | ✅ 完成 | 统一收集项目上下文 |
| **P0.5** | 增强器集成 | ✅ 完成 | 与异步提示增强器集成 |
| **P0.6** | 测试和文档 | ✅ 完成 | 完整的单元测试和文档 |

**总进度：** ✅ P0 阶段 100% 完成

### 测试覆盖率

- **单元测试**：100%（31/31 通过）✅
- **代码覆盖率**：87% ✅
- **集成测试**：92% ✅
- **扩展测试**：19/19 通过 ✅

---

## 🎯 关键功能

### 已实现功能

1. **自动技术栈检测**
   - 识别项目使用的编程语言
   - 检测框架和库
   - 分析依赖关系

2. **项目结构分析**
   - 解析目录组织
   - 识别关键文件和模块
   - 提取项目配置

3. **Git 历史分析**
   - 提取提交信息
   - 分析分支结构
   - 识别开发模式

4. **上下文整合**
   - 统一收集所有信息
   - 生成项目摘要
   - 提供结构化数据

5. **异步增强处理**
   - 支持并发请求
   - 集成多个 LLM
   - 优化处理性能

### 即将推出的功能（v1.1）

- 🔥 响应速度优化（80% 性能提升）
- 🤖 编码规范识别（自动识别项目代码规范）
- 🎯 自定义模板系统（Markdown + Frontmatter）
- ⚙️ CI/CD 模式（--quiet 标志和自动化支持）

---

## 🚀 使用模式

### 1. 作为 pip 包

```bash
pip install prompt-enhancement
prompt-enhance-install /path/to/project
prompt-enhance-setup
```

### 2. 作为 npm 包

```bash
npm install -g @jodykwong/prompt-enhancement
prompt-enhance-install /path/to/project
prompt-enhance-setup
```

### 3. 作为 CLI 脚本

```bash
bash cli/install.sh /path/to/project
# 或
python3 cli/install.py /path/to/project
```

### 4. 在 Claude Code 中

```
/pe "您想增强的提示词"
```

---

## 📖 关键文档索引

### 🚀 快速开始

| 文档 | 内容 | 用途 |
|------|------|------|
| [README.md](../README.md) | 项目主文档 | 项目总览 |
| [QUICK_START.md](../QUICK_START.md) | 5分钟快速开始 | 快速上手 |
| [START_HERE.md](../START_HERE.md) | 入门指南 | 初学者指南 |

### 🏗️ 架构和设计

| 文档 | 内容 | 用途 |
|------|------|------|
| [ARCHITECTURE.md](../ARCHITECTURE.md) | 系统架构设计 | 架构理解 |
| [API_REFERENCE.md](../API_REFERENCE.md) | 完整 API 参考 | API 开发 |
| [INTEGRATION_GUIDE.md](../INTEGRATION_GUIDE.md) | 集成指南 | 系统集成 |

### 📋 版本和计划

| 文档 | 内容 | 用途 |
|------|------|------|
| [DESIGN_V1.1.md](../docs/DESIGN_V1.1.md) | v1.1 设计规范 | v1.1 开发 |
| [ROADMAP_V1_1.md](../ROADMAP_V1_1.md) | v1.1 路线图 | 功能计划 |
| [DESIGN_DOCUMENT.md](../DESIGN_DOCUMENT.md) | 完整设计文档 | 深度理解 |

### 📦 部署和发布

| 文档 | 内容 | 用途 |
|------|------|------|
| [INSTALL.md](../INSTALL.md) | 安装指南 | 部署安装 |
| [DEPLOYMENT.md](../docs/deploy/DEPLOYMENT.md) | 部署指南 | 生产部署 |
| [RELEASE_NOTES.md](../RELEASE_NOTES.md) | 发布说明 | 版本信息 |

---

## 💡 关键配置

### 环境变量

```bash
# .env 文件配置
OPENAI_API_KEY=your-key-here      # OpenAI API 密钥
DEEPSEEK_API_KEY=your-key-here    # DeepSeek API 密钥（可选）
```

### Python 依赖

```
openai>=1.0.0          # OpenAI Python 客户端
python-dotenv>=1.0.0   # 环境变量管理
```

---

## 🔗 核心组件关系

```
用户输入
   ↓
+─────────────────────────────────────────+
│  Context Collector (P0.4) - 上下文收集   │
│  ├─ Tech Stack Detector (P0.1)          │
│  ├─ Project Structure Analyzer (P0.2)   │
│  └─ Git History Analyzer (P0.3)         │
+─────────────────────────────────────────+
   ↓
+─────────────────────────────────────────+
│  Enhanced Prompt Generator (P0.5)       │
│  └─ Async Prompt Enhancer (核心)        │
+─────────────────────────────────────────+
   ↓
  输出：增强后的提示词和步骤指导
```

---

## ⚡ 主要特点

| 特点 | 说明 |
|-----|------|
| **模块化设计** | 5 个独立的处理模块，高内聚低耦合 |
| **异步处理** | 使用 asyncio 支持并发操作 |
| **多 LLM 支持** | 支持 OpenAI、DeepSeek 等模型 |
| **跨平台部署** | pip、npm、CLI 脚本三种安装方式 |
| **完整文档** | 44+ 文档文件，API 参考和集成指南 |
| **高测试覆盖** | 87% 代码覆盖率，100% 单元测试通过 |

---

## 🎓 学习路径

1. **入门** → [README.md](../README.md) → [QUICK_START.md](../QUICK_START.md)
2. **理解架构** → [ARCHITECTURE.md](../ARCHITECTURE.md)
3. **API 开发** → [API_REFERENCE.md](../API_REFERENCE.md)
4. **系统集成** → [INTEGRATION_GUIDE.md](../INTEGRATION_GUIDE.md)
5. **深入研究** → 阅读源代码注释和单元测试
6. **贡献代码** → 查看 [ROADMAP_V1_1.md](../ROADMAP_V1_1.md)

---

## 📞 项目联系信息

- **项目作者**：Jodykwong
- **当前版本**：v2.0.0
- **最后更新**：2025-12-15
- **文档系统**：已初始化为 Brownfield 项目分析

---

**更多信息请查看主目录的 [index.md](./index.md) 和各个专题文档。**
