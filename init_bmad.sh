#!/bin/bash
# kiro-cli bmad 初始化脚本

export BMAD_ROOT="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/_bmad"
export KIRO_AGENTS_PATH="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/.kiro/agents"
export BMAD_WORKFLOWS_PATH="/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/_bmad/core/workflows"

echo "✓ BMAD 环境变量已设置"
echo "  BMAD_ROOT=$BMAD_ROOT"
echo "  KIRO_AGENTS_PATH=$KIRO_AGENTS_PATH"
echo "  BMAD_WORKFLOWS_PATH=$BMAD_WORKFLOWS_PATH"

# 加载 bmad 工作流
if [ -f "/home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/_bmad/core/tasks/workflow.xml" ]; then
    echo "✓ 检测到 bmad 工作流配置"
fi
