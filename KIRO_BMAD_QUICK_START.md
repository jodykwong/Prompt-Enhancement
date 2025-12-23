# kiro-cli + bmad 快速开始

## ⚡ 最快方式（一行命令）

```bash
cd /home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement && bash start_kiro_bmad.sh
```

## 📋 三步启动

### 步骤 1: 初始化
```bash
cd /home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement
python3 init_bmad_kiro.py
```

### 步骤 2: 加载环境
```bash
source init_bmad.sh
```

### 步骤 3: 启动 kiro-cli
```bash
kiro-cli chat
```

## 🎯 在 kiro-cli 中使用 bmad

启动后，在 kiro-cli 中执行：

```
# 加载 bmad 工作流
LOAD @bmad/core/tasks/workflow.xml

# 查看可用的 bmad 代理
LIST @bmad/agents

# 执行 bmad 任务
RUN @bmad/core/tasks/workflow.xml
```

## ✅ 验证配置

```bash
# 检查配置文件
cat .kiro/config.json

# 检查环境变量
echo $BMAD_ROOT
echo $KIRO_AGENTS_PATH

# 检查 bmad 结构
ls -la _bmad/core/tasks/
```

## 🔧 环境变量

| 变量 | 值 |
|------|-----|
| `BMAD_ROOT` | `_bmad` 目录路径 |
| `KIRO_AGENTS_PATH` | `.kiro/agents` 目录路径 |
| `BMAD_WORKFLOWS_PATH` | `_bmad/core/workflows` 目录路径 |

## 📚 相关文件

- `start_kiro_bmad.sh` - 一键启动脚本
- `init_bmad_kiro.py` - 初始化脚本
- `init_bmad.sh` - 环境变量设置脚本
- `KIRO_BMAD_SETUP.md` - 详细设置指南
- `AGENTS.md` - 项目准则

## 🆘 常见问题

**Q: 脚本无法执行？**
```bash
chmod +x start_kiro_bmad.sh
chmod +x init_bmad.sh
chmod +x bmad_kiro_init.py
```

**Q: 找不到 bmad 目录？**
```bash
ls -la _bmad/
# 如果不存在，检查项目结构是否完整
```

**Q: 环境变量未生效？**
```bash
# 手动设置
export BMAD_ROOT="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/_bmad"
export KIRO_AGENTS_PATH="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/.kiro/agents"
export BMAD_WORKFLOWS_PATH="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/_bmad/core/workflows"
```

## 💡 提示

- 首次运行会自动初始化配置
- 配置文件保存在 `.kiro/config.json`
- 所有 bmad 模块都已预配置
- 支持的模块: core, bmm, bmgd, cis, bmb
