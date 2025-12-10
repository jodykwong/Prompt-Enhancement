# Changelog

All notable changes to Prompt Enhancement will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-11

### 🎉 首个正式发布版本

基于 P0.6 (100% 完成) 的完整功能，采用全新的 Display-Only 模式。

### Added - 新增功能

- **Display-Only Mode**: 增强后只显示结果，不自动执行任务
  - 符合 Auggle CLI 设计模式
  - 用户完全控制是否执行
  - 提供清晰的使用指导

- **一键安装脚本** (`install.sh`):
  - 自动检查系统依赖
  - 交互式 API key 配置
  - 自动安装到 Claude Code
  - 完整的安装验证

- **完整的文档体系**:
  - `INSTALL.md` - 详细安装指南
  - `CHANGELOG.md` - 变更记录
  - `LICENSE` - MIT 许可证
  - 更新的 `README.md`

- **优化的脚本架构**:
  - 新位置: `.claude/commands/scripts/enhance.py`
  - 引用项目核心模块（P0.6 功能）
  - 完善的错误处理和用户提示

### Changed - 变更内容

- **重写 `/pe` 命令流程**:
  - 从 "询问后自动执行" 改为 "仅显示结果"
  - 移除 `AskUserQuestion` 工具的使用
  - 添加明确的 "STOP EXECUTION" 指令

- **脚本位置变更**:
  - 从 `.claude/skills/prompt-enhancement/scripts/`
  - 迁移到 `.claude/commands/scripts/`

- **API 调用优化**:
  - 使用 P0.6 的 `enhance_prompt_with_context`
  - 自动注入项目上下文
  - 超时设置为 60 秒

### Fixed - 修复问题

- **核心问题修复**: 增强后不再自动执行任务
  - 旧版本问题: Claude 可能忽略用户选择，直接执行
  - 新版本解决: 命令只负责显示，由用户决定是否执行

- **路径混淆修复**: 明确区分 `commands` 和 `skills`
  - 统一使用 `.claude/commands/` 目录
  - 更新所有文档和脚本引用

### Security - 安全改进

- **API Key 保护**:
  - 安装脚本交互式输入
  - 存储在本地 `.env` 文件
  - 添加 `.gitignore` 防止泄露

- **依赖版本锁定**:
  - 明确 Python 3.8+ 要求
  - 指定依赖包版本范围

---

## [0.6.0] - 2025-12-10 (P0.6)

### P0.6: 测试和文档完成

- 完成所有单元测试（31/31 通过）
- 代码覆盖率达到 87%
- 完整的文档体系（8+ 文档文件）
- 项目状态：100% 完成

## [0.5.0] - 2025-12-10 (P0.5)

### P0.5: 增强器集成

- 实现 `enhanced_prompt_generator.py`
- 集成异步提示词增强器
- 支持项目上下文注入
- 完成集成测试

## [0.4.0] - 2025-12-10 (P0.4)

### P0.4: 上下文整合

- 实现 `context_collector.py`
- 统一收集技术栈、项目结构、Git 历史
- 支持缓存机制
- 完成单元测试

## [0.3.0] - 2025-12-10 (P0.3)

### P0.3: Git 历史分析

- 实现 `git_history_analyzer.py`
- 提取提交记录和分支信息
- 分析代码变更模式
- 完成单元测试

## [0.2.0] - 2025-12-09 (P0.2)

### P0.2: 项目结构分析

- 实现 `project_structure_analyzer.py`
- 解析项目目录结构
- 识别关键文件和配置
- 完成单元测试

## [0.1.0] - 2025-12-09 (P0.1)

### P0.1: 技术栈识别

- 实现 `tech_stack_detector.py`
- 自动检测项目技术框架
- 识别语言、框架、工具
- 完成单元测试

## [0.0.1] - 2025-12-09

### 项目初始化

- 基础项目结构
- `async_prompt_enhancer.py` 核心实现
- DeepSeek API 集成
- 基本文档

---

## 版本说明

### 版本号格式
- **Major.Minor.Patch** (例如: 1.0.0)
- **Major**: 重大变更或破坏性更新
- **Minor**: 新功能添加，向后兼容
- **Patch**: Bug 修复和小改进

### P0.x 系列
- P0.1 ~ P0.6: MVP 开发阶段
- 每个阶段专注一个核心功能
- 1.0.0: 基于 P0.6 的首个稳定版本

---

## 即将发布

### [1.1.0] - 计划中
- 多模型支持（OpenAI GPT-4）
- 自定义提示模板
- 批量增强功能

### [1.2.0] - 计划中
- Web UI 界面
- 增强历史记录
- 性能统计和分析

---

**Maintained by**: Jodykwong
**License**: MIT
**Repository**: https://github.com/yourusername/Prompt-Enhancement
