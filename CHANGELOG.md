# Changelog

所有显著的项目变更都将在本文件中记录。

格式遵循 [Keep a Changelog](https://keepachangelog.com) 约定。
版本号遵循 [Semantic Versioning](https://semver.org)。

---

## [2.0.0] - 2025-12-11

### ✨ 新增

#### 跨项目部署系统 🎯

- **Python 包系统 (pip)**
  - 创建标准 Python 包 `prompt-enhancement`
  - 实现 `setup.py` 和现代 `pyproject.toml` 配置
  - 核心安装器类 `PromptEnhancementInstaller`
  - CLI 接口 `prompt-enhance-install`, `prompt-enhance-setup`, `prompt-enhance-verify`
  - 自动依赖检查和安装

- **NPM 包系统 (npm)**
  - 创建 NPM 包 `@jodykwong/prompt-enhancement`
  - 标准 `package.json` 配置
  - JavaScript 脚本实现安装流程
  - 彩色输出支持（chalk 库）
  - 后安装提示和指导

- **CLI 一键安装脚本**
  - Linux/macOS bash 脚本 (`cli/install.sh`)
  - 跨平台 Python 脚本 (`cli/install.py`) ✅ 已测试
  - Windows PowerShell 脚本 (`cli/install.ps1`)
  - 符号链接优先，Windows 自动降级到文件复制

- **完整文档系统**
  - `docs/deploy/INSTALL.md` - 3 种安装方式详解
  - `docs/deploy/QUICKSTART.md` - 5 分钟快速开始
  - `docs/deploy/TROUBLESHOOTING.md` - 故障排除（8 个常见问题）
  - `docs/deploy/DEPLOYMENT.md` - 部署和发布指南
  - `docs/deploy/README.md` - 部署系统总结

### 🔄 变更

- 更新主 `README.md` 至 v2.0.0
  - 新增三种安装方式介绍
  - 添加部署验证结果
  - 更新项目结构说明
  - 突出跨项目部署特性

### 📊 统计

- **新增文件**: 21 个
- **代码行数**: 11000+
- **文档字数**: 8000+
- **部署验证**: ✅ xlerobot 通过

---

## [1.01] - 2025-12-10

### ✨ 新增

- Display-Only 模式 - 增强后只显示，用户手动执行
- 完整 P0 功能 - P0.1-P0.6 全部实现
- 31/31 单元测试通过，87% 代码覆盖率
- 详细文档系统

---

## 如何升级

### 从 v1.01 升级到 v2.0.0

**使用 pip**:
```bash
pip install --upgrade prompt-enhancement
```

**使用 NPM**:
```bash
npm install -g @jodykwong/prompt-enhancement@latest
```

---

## 许可证

MIT License

---

*最后更新: 2025-12-11*
