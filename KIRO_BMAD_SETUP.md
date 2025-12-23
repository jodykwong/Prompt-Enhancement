# kiro-cli 与 bmad 方法集成指南

## 问题描述
kiro-cli 无法使用 bmad-method 功能。

## 解决方案

### 方案 1: 使用初始化脚本（推荐）

```bash
# 进入项目目录
cd /home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement

# 运行初始化脚本
python3 init_bmad_kiro.py

# 加载环境变量
source init_bmad.sh

# 启动 kiro-cli
kiro-cli chat
```

### 方案 2: 手动设置环境变量

```bash
export BMAD_ROOT="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/_bmad"
export KIRO_AGENTS_PATH="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/.kiro/agents"
export BMAD_WORKFLOWS_PATH="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/_bmad/core/workflows"

kiro-cli chat
```

### 方案 3: 使用 Python 模块

```bash
cd /home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement

# 设置环境
python3 -c "from bmad_kiro_init import setup_bmad_environment; setup_bmad_environment()"

# 启动 kiro-cli
kiro-cli chat
```

## 验证配置

运行以下命令验证 bmad 配置是否正确：

```bash
# 检查配置文件
cat .kiro/config.json

# 检查 bmad 目录结构
ls -la _bmad/

# 检查工作流文件
ls -la _bmad/core/tasks/workflow.xml
```

## 配置文件说明

初始化脚本会创建以下文件：

1. **`.kiro/config.json`** - kiro-cli 配置文件
   - 启用 bmad 支持
   - 配置 bmad 路径
   - 配置工作流路径

2. **`init_bmad.sh`** - Bash 初始化脚本
   - 设置环境变量
   - 验证 bmad 配置

3. **`bmad_kiro_init.py`** - Python 初始化模块
   - 程序化设置环境
   - 可在 Python 代码中导入使用

## 故障排除

### 问题 1: 找不到 bmad 目录

**症状**: `_bmad` 目录不存在

**解决方案**:
```bash
# 检查目录是否存在
ls -la _bmad/

# 如果不存在，检查项目结构
find . -name "_bmad" -type d
```

### 问题 2: 环境变量未设置

**症状**: kiro-cli 仍然无法使用 bmad

**解决方案**:
```bash
# 验证环境变量
echo $BMAD_ROOT
echo $KIRO_AGENTS_PATH
echo $BMAD_WORKFLOWS_PATH

# 手动设置
export BMAD_ROOT="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/_bmad"
```

### 问题 3: 权限问题

**症状**: 无法执行脚本

**解决方案**:
```bash
# 添加执行权限
chmod +x init_bmad.sh
chmod +x bmad_kiro_init.py

# 重新运行
./init_bmad.sh
```

## 下一步

配置完成后，你可以：

1. 使用 bmad 工作流进行项目管理
2. 加载 bmad 任务配置
3. 使用 bmad 代理进行自动化处理

```bash
# 加载 bmad 工作流
kiro-cli chat

# 在 kiro-cli 中执行
LOAD @bmad/core/tasks/workflow.xml
```

## 相关文档

- **AGENTS.md** - 项目准则和 agent 执行逻辑
- **_bmad/core/tasks/workflow.xml** - bmad 工作流配置
- **_bmad/core/module.yaml** - bmad 核心模块配置
