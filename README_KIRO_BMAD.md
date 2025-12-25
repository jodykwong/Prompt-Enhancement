# kiro-cli 与 bmad 方法集成 - 完整解决方案

## 🎯 问题

你在重新启动 kiro-cli 后，无法使用 bmad-method 功能。

## ✅ 解决方案已完成

所有必要的配置和脚本已经为你创建完毕。现在你可以立即使用 kiro-cli 的 bmad 功能。

## 🚀 快速开始（3 种方式）

### 方式 1: 一键启动（最简单）⭐

```bash
cd /home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement
bash start_kiro_bmad.sh
```

### 方式 2: 手动步骤

```bash
cd /home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement
python3 init_bmad_kiro.py
source init_bmad.sh
kiro-cli chat
```

### 方式 3: 环境变量方式

```bash
export BMAD_ROOT="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/_bmad"
export KIRO_AGENTS_PATH="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/.kiro/agents"
export BMAD_WORKFLOWS_PATH="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/_bmad/core/workflows"
kiro-cli chat
```

## 📦 创建的文件清单

| 文件 | 说明 |
|------|------|
| `start_kiro_bmad.sh` | 一键启动脚本（推荐使用） |
| `init_bmad_kiro.py` | Python 初始化脚本 |
| `init_bmad.sh` | Bash 环境设置脚本 |
| `verify_bmad_setup.sh` | 验证脚本 |
| `.kiro/config.json` | kiro-cli 配置文件 |
| `KIRO_BMAD_SETUP.md` | 详细设置指南 |
| `KIRO_BMAD_QUICK_START.md` | 快速开始指南 |
| `KIRO_BMAD_SOLUTION.md` | 完整解决方案文档 |
| `README_KIRO_BMAD.md` | 本文件 |

## ✅ 验证配置

运行验证脚本确保一切正常：

```bash
cd /home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement
bash verify_bmad_setup.sh
```

预期输出：
```
✅ 所有检查通过！

🚀 你可以现在启动 kiro-cli:
   bash start_kiro_bmad.sh
```

## 🎯 在 kiro-cli 中使用 bmad

启动 kiro-cli 后，你可以使用以下命令：

```bash
# 加载 bmad 工作流
LOAD @bmad/core/tasks/workflow.xml

# 列出可用的 bmad agents
LIST @bmad/agents

# 执行 bmad 任务
RUN @bmad/core/tasks/workflow.xml
```

## 📊 配置详情

### 环境变量

```bash
BMAD_ROOT=/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/_bmad
KIRO_AGENTS_PATH=/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/.kiro/agents
BMAD_WORKFLOWS_PATH=/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/_bmad/core/workflows
```

### 支持的 bmad 模块

- ✓ **core** - 核心模块
- ✓ **bmm** - 项目管理模块
- ✓ **bmgd** - 游戏开发模块
- ✓ **cis** - 创新策略模块
- ✓ **bmb** - bmad 构建器模块

## 🔧 故障排除

### 问题 1: 脚本无法执行

```bash
chmod +x start_kiro_bmad.sh
chmod +x init_bmad.sh
chmod +x verify_bmad_setup.sh
```

### 问题 2: 找不到 bmad 目录

```bash
# 验证目录存在
ls -la _bmad/
```

### 问题 3: 环境变量未生效

```bash
# 验证环境变量
env | grep BMAD

# 或手动设置
source init_bmad.sh
```

### 问题 4: kiro-cli 仍然无法识别 bmad

```bash
# 重新初始化
python3 init_bmad_kiro.py

# 然后启动
bash start_kiro_bmad.sh
```

## 📚 相关文档

- **AGENTS.md** - 项目准则和 agent 执行逻辑
- **KIRO_BMAD_SETUP.md** - 详细设置指南
- **KIRO_BMAD_QUICK_START.md** - 快速开始指南
- **KIRO_BMAD_SOLUTION.md** - 完整解决方案文档

## 💡 最佳实践

1. **首次使用**
   ```bash
   bash start_kiro_bmad.sh
   ```

2. **日常使用**
   ```bash
   bash start_kiro_bmad.sh
   ```

3. **开发调试**
   ```bash
   bash verify_bmad_setup.sh  # 验证配置
   cat .kiro/config.json      # 查看配置
   ```

## 🎉 现在就开始

```bash
cd /home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement
bash start_kiro_bmad.sh
```

## 📞 需要帮助？

1. 查看 `KIRO_BMAD_SETUP.md` 了解详细信息
2. 运行 `bash verify_bmad_setup.sh` 验证配置
3. 检查 `AGENTS.md` 了解项目准则

---

**状态**: ✅ 完全配置就绪
**最后更新**: 2025-12-22
**版本**: 1.0
