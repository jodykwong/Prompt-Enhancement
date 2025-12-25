# kiro-cli 与 bmad 方法集成 - 文件索引

## 🎯 快速导航

### 立即开始
- **[README_KIRO_BMAD.md](README_KIRO_BMAD.md)** - 快速参考和启动指南

### 详细文档
- **[KIRO_BMAD_SETUP.md](KIRO_BMAD_SETUP.md)** - 详细设置指南
- **[KIRO_BMAD_QUICK_START.md](KIRO_BMAD_QUICK_START.md)** - 快速开始指南
- **[KIRO_BMAD_SOLUTION.md](KIRO_BMAD_SOLUTION.md)** - 完整解决方案文档

### 可执行脚本
- **[start_kiro_bmad.sh](start_kiro_bmad.sh)** - 一键启动脚本（推荐）
- **[init_bmad_kiro.py](init_bmad_kiro.py)** - Python 初始化脚本
- **[init_bmad.sh](init_bmad.sh)** - Bash 环境设置脚本
- **[verify_bmad_setup.sh](verify_bmad_setup.sh)** - 验证脚本

### 配置文件
- **[.kiro/config.json](.kiro/config.json)** - kiro-cli 配置文件

## 📊 文件说明

### 启动脚本

#### start_kiro_bmad.sh (2.3K)
**用途**: 一键启动 kiro-cli 与 bmad 支持
**功能**:
- 检查项目结构
- 初始化 bmad 配置
- 设置环境变量
- 验证 bmad 工作流
- 启动 kiro-cli

**使用方法**:
```bash
bash start_kiro_bmad.sh
```

#### init_bmad_kiro.py (3.9K)
**用途**: Python 初始化脚本
**功能**:
- 创建 .kiro/config.json 配置文件
- 验证 bmad 目录结构
- 生成 init_bmad.sh 脚本
- 生成 bmad_kiro_init.py 模块

**使用方法**:
```bash
python3 init_bmad_kiro.py
```

#### init_bmad.sh (680B)
**用途**: Bash 环境设置脚本
**功能**:
- 设置 BMAD_ROOT 环境变量
- 设置 KIRO_AGENTS_PATH 环境变量
- 设置 BMAD_WORKFLOWS_PATH 环境变量
- 验证 bmad 配置

**使用方法**:
```bash
source init_bmad.sh
```

#### verify_bmad_setup.sh (3.3K)
**用途**: 验证 bmad 配置脚本
**功能**:
- 检查目录结构
- 验证配置文件
- 检查初始化脚本
- 验证 bmad 模块
- 检查工作流文件
- 检查文档

**使用方法**:
```bash
bash verify_bmad_setup.sh
```

### 文档

#### README_KIRO_BMAD.md (3.9K)
**内容**:
- 问题描述
- 解决方案概述
- 快速开始指南
- 文件清单
- 验证配置
- 故障排除
- 最佳实践

#### KIRO_BMAD_SETUP.md (2.8K)
**内容**:
- 问题描述
- 解决方案详情
- 三种安装方式
- 验证配置
- 配置详情
- 故障排除

#### KIRO_BMAD_QUICK_START.md (2.1K)
**内容**:
- 最快方式（一行命令）
- 三步启动
- 在 kiro-cli 中使用 bmad
- 验证配置
- 环境变量表
- 常见问题

#### KIRO_BMAD_SOLUTION.md (5.2K)
**内容**:
- 问题总结
- 根本原因分析
- 完整解决方案
- 使用方法
- 验证配置
- 配置详情
- 故障排除
- 最佳实践

### 配置文件

#### .kiro/config.json (711B)
**内容**:
```json
{
  "version": "1.0",
  "bmad_enabled": true,
  "bmad_path": "/path/to/_bmad",
  "agents_path": "/path/to/.kiro/agents",
  "workflows": {
    "core": "/path/to/_bmad/core/workflows",
    "bmm": "/path/to/_bmad/bmm/workflows",
    "bmgd": "/path/to/_bmad/bmgd/workflows",
    "cis": "/path/to/_bmad/cis/workflows",
    "bmb": "/path/to/_bmad/bmb/workflows"
  }
}
```

## 🚀 使用流程

### 第一次使用

1. **验证配置**
   ```bash
   bash verify_bmad_setup.sh
   ```

2. **启动 kiro-cli**
   ```bash
   bash start_kiro_bmad.sh
   ```

### 日常使用

```bash
bash start_kiro_bmad.sh
```

### 开发调试

1. **验证配置**
   ```bash
   bash verify_bmad_setup.sh
   ```

2. **查看配置**
   ```bash
   cat .kiro/config.json
   ```

3. **检查环境变量**
   ```bash
   echo $BMAD_ROOT
   echo $KIRO_AGENTS_PATH
   echo $BMAD_WORKFLOWS_PATH
   ```

## 📋 文件大小统计

| 文件 | 大小 | 类型 |
|------|------|------|
| start_kiro_bmad.sh | 2.3K | 脚本 |
| init_bmad_kiro.py | 3.9K | 脚本 |
| init_bmad.sh | 680B | 脚本 |
| verify_bmad_setup.sh | 3.3K | 脚本 |
| .kiro/config.json | 711B | 配置 |
| README_KIRO_BMAD.md | 3.9K | 文档 |
| KIRO_BMAD_SETUP.md | 2.8K | 文档 |
| KIRO_BMAD_QUICK_START.md | 2.1K | 文档 |
| KIRO_BMAD_SOLUTION.md | 5.2K | 文档 |
| **总计** | **~24K** | - |

## 🔗 相关文件

- **AGENTS.md** - 项目准则和 agent 执行逻辑
- **_bmad/core/tasks/workflow.xml** - bmad 工作流配置
- **_bmad/core/module.yaml** - bmad 核心模块配置

## 💡 快速参考

### 一行命令启动
```bash
cd /home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement && bash start_kiro_bmad.sh
```

### 验证配置
```bash
bash verify_bmad_setup.sh
```

### 查看配置
```bash
cat .kiro/config.json
```

### 手动设置环境
```bash
source init_bmad.sh
```

## 📞 需要帮助？

1. 查看 **README_KIRO_BMAD.md** 了解快速参考
2. 查看 **KIRO_BMAD_SETUP.md** 了解详细设置
3. 运行 **verify_bmad_setup.sh** 验证配置
4. 查看 **KIRO_BMAD_SOLUTION.md** 了解完整解决方案

---

**状态**: ✅ 完全配置就绪
**最后更新**: 2025-12-22
**版本**: 1.0
