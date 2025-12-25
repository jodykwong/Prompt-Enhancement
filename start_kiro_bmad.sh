#!/bin/bash
# kiro-cli 与 bmad 一键启动脚本
# One-click startup script for kiro-cli with bmad support

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BMAD_ROOT="$PROJECT_ROOT/_bmad"
KIRO_AGENTS_PATH="$PROJECT_ROOT/.kiro/agents"
BMAD_WORKFLOWS_PATH="$PROJECT_ROOT/_bmad/core/workflows"

echo "🚀 kiro-cli bmad 启动脚本"
echo "================================"
echo ""

# 1. 检查必要的目录
echo "📋 检查项目结构..."
if [ ! -d "$BMAD_ROOT" ]; then
    echo "✗ 错误: _bmad 目录不存在"
    exit 1
fi
echo "✓ _bmad 目录存在"

if [ ! -d "$KIRO_AGENTS_PATH" ]; then
    echo "⚠ 警告: .kiro/agents 目录不存在，正在创建..."
    mkdir -p "$KIRO_AGENTS_PATH"
fi
echo "✓ .kiro/agents 目录存在"

# 2. 初始化 bmad 配置
echo ""
echo "⚙️  初始化 bmad 配置..."
if [ ! -f "$PROJECT_ROOT/.kiro/config.json" ]; then
    python3 "$PROJECT_ROOT/init_bmad_kiro.py" > /dev/null 2>&1
    echo "✓ bmad 配置已初始化"
else
    echo "✓ bmad 配置已存在"
fi

# 3. 设置环境变量
echo ""
echo "🔧 设置环境变量..."
export BMAD_ROOT="$BMAD_ROOT"
export KIRO_AGENTS_PATH="$KIRO_AGENTS_PATH"
export BMAD_WORKFLOWS_PATH="$BMAD_WORKFLOWS_PATH"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

echo "✓ BMAD_ROOT=$BMAD_ROOT"
echo "✓ KIRO_AGENTS_PATH=$KIRO_AGENTS_PATH"
echo "✓ BMAD_WORKFLOWS_PATH=$BMAD_WORKFLOWS_PATH"

# 4. 验证 bmad 工作流
echo ""
echo "✅ 验证 bmad 工作流..."
if [ -f "$BMAD_ROOT/core/tasks/workflow.xml" ]; then
    echo "✓ 检测到 bmad 核心工作流"
fi

if [ -f "$BMAD_ROOT/core/module.yaml" ]; then
    echo "✓ 检测到 bmad 核心模块配置"
fi

# 5. 显示可用的 bmad 模块
echo ""
echo "📦 可用的 bmad 模块:"
for module in core bmm bmgd cis bmb; do
    if [ -d "$BMAD_ROOT/$module" ]; then
        echo "  ✓ $module"
    fi
done

# 6. 启动 kiro-cli
echo ""
echo "================================"
echo "🎯 启动 kiro-cli..."
echo ""
echo "💡 提示:"
echo "  - 在 kiro-cli 中使用 bmad 功能"
echo "  - 加载工作流: LOAD @bmad/core/tasks/workflow.xml"
echo "  - 查看帮助: /help"
echo ""

# 启动 kiro-cli
kiro-cli chat

# 清理
unset BMAD_ROOT
unset KIRO_AGENTS_PATH
unset BMAD_WORKFLOWS_PATH
