# kiro-cli 与 bmad 方法集成 - 完整解决方案

## 问题总结

你在重新启动 kiro-cli 后，无法使用 bmad-method 功能。

## 根本原因

kiro-cli 需要正确的环境变量和配置文件才能识别和加载 bmad 模块。项目中虽然有完整的 `_bmad` 目录结构和 `.kiro/agents` 配置，但缺少必要的初始化步骤。

## 解决方案

我已经为你创建了完整的初始化和启动系统：

### 📦 创建的文件

1. **`init_bmad_kiro.py`** - Python 初始化脚本
   - 自动创建 `.kiro/config.json` 配置文件
   - 验证 bmad 目录结构
   - 生成初始化脚本

2. **`init_bmad.sh`** - Bash 环境设置脚本
   - 设置必要的环境变量
   - 验证 bmad 配置

3. **`start_kiro_bmad.sh`** - 一键启动脚本
   - 完整的初始化流程
   - 环境变量设置
   - 直接启动 kiro-cli

4. **`.kiro/config.json`** - kiro-cli 配置文件
   - 启用 bmad 支持
   - 配置所有工作流路径

5. **`KIRO_BMAD_SETUP.md`** - 详细设置指南
6. **`KIRO_BMAD_QUICK_START.md`** - 快速开始指南

## 🚀 使用方法

### 方法 1: 一键启动（推荐）

```bash
cd /home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement
bash start_kiro_bmad.sh
```

### 方法 2: 手动步骤

```bash
# 1. 进入项目目录
cd /home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement

# 2. 初始化配置
python3 init_bmad_kiro.py

# 3. 加载环境变量
source init_bmad.sh

# 4. 启动 kiro-cli
kiro-cli chat
```

### 方法 3: 手动设置环境变量

```bash
export BMAD_ROOT="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/_bmad"
export KIRO_AGENTS_PATH="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/.kiro/agents"
export BMAD_WORKFLOWS_PATH="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/_bmad/core/workflows"

kiro-cli chat
```

## ✅ 验证配置

运行以下命令验证一切正常：

```bash
# 1. 检查配置文件
cat .kiro/config.json

# 2. 检查环境变量
echo "BMAD_ROOT: $BMAD_ROOT"
echo "KIRO_AGENTS_PATH: $KIRO_AGENTS_PATH"
echo "BMAD_WORKFLOWS_PATH: $BMAD_WORKFLOWS_PATH"

# 3. 检查 bmad 结构
ls -la _bmad/core/tasks/workflow.xml
ls -la _bmad/core/module.yaml

# 4. 检查 kiro agents
ls -la .kiro/agents/ | head -10
```

## 📊 配置详情

### 环境变量

| 变量 | 路径 | 说明 |
|------|------|------|
| `BMAD_ROOT` | `_bmad` | bmad 根目录 |
| `KIRO_AGENTS_PATH` | `.kiro/agents` | kiro agents 配置目录 |
| `BMAD_WORKFLOWS_PATH` | `_bmad/core/workflows` | bmad 工作流目录 |

### 支持的 bmad 模块

- **core** - 核心模块（工作流、任务、工具）
- **bmm** - 项目管理模块（开发、设计、分析）
- **bmgd** - 游戏开发模块（游戏设计、开发、QA）
- **cis** - 创新策略模块（头脑风暴、设计思维）
- **bmb** - bmad 构建器模块

### 配置文件结构

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

## 🎯 在 kiro-cli 中使用 bmad

启动 kiro-cli 后，你可以使用以下命令：

```bash
# 加载 bmad 工作流
LOAD @bmad/core/tasks/workflow.xml

# 列出可用的 bmad agents
LIST @bmad/agents

# 执行 bmad 任务
RUN @bmad/core/tasks/workflow.xml

# 查看 bmad 配置
SHOW @bmad/config
```

## 🔧 故障排除

### 问题 1: 脚本无法执行

```bash
# 添加执行权限
chmod +x start_kiro_bmad.sh
chmod +x init_bmad.sh
chmod +x bmad_kiro_init.py
```

### 问题 2: 找不到 bmad 目录

```bash
# 验证目录存在
ls -la _bmad/

# 如果不存在，检查项目结构
find . -name "_bmad" -type d
```

### 问题 3: 环境变量未生效

```bash
# 验证环境变量
env | grep BMAD

# 手动设置
export BMAD_ROOT="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/_bmad"
```

### 问题 4: kiro-cli 仍然无法识别 bmad

```bash
# 检查 kiro-cli 版本
kiro-cli --version

# 检查 kiro-cli 配置
kiro-cli config show

# 重新初始化
python3 init_bmad_kiro.py
```

## 📚 相关文档

- **AGENTS.md** - 项目准则和 agent 执行逻辑
- **KIRO_BMAD_SETUP.md** - 详细设置指南
- **KIRO_BMAD_QUICK_START.md** - 快速开始指南
- **_bmad/core/tasks/workflow.xml** - bmad 工作流配置
- **_bmad/core/module.yaml** - bmad 核心模块配置

## 💡 最佳实践

1. **首次使用**
   - 运行 `python3 init_bmad_kiro.py` 初始化配置
   - 使用 `bash start_kiro_bmad.sh` 启动

2. **日常使用**
   - 使用 `bash start_kiro_bmad.sh` 一键启动
   - 或在 shell 中 `source init_bmad.sh` 后启动

3. **开发调试**
   - 检查 `.kiro/config.json` 配置
   - 验证环境变量设置
   - 查看 `_bmad` 目录结构

## 🎉 总结

现在你已经拥有：

✅ 完整的 bmad 初始化系统
✅ 自动化的环境配置
✅ 一键启动脚本
✅ 详细的文档和指南
✅ 故障排除方案

**立即开始使用：**

```bash
cd /home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement
bash start_kiro_bmad.sh
```

祝你使用愉快！🚀
