#!/bin/bash
# 验证 bmad 设置脚本

echo "🔍 验证 kiro-cli bmad 设置..."
echo "================================"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ERRORS=0

# 1. 检查目录
echo "📁 检查目录结构..."
if [ -d "$PROJECT_ROOT/_bmad" ]; then
    echo "  ✓ _bmad 目录存在"
else
    echo "  ✗ _bmad 目录不存在"
    ((ERRORS++))
fi

if [ -d "$PROJECT_ROOT/.kiro" ]; then
    echo "  ✓ .kiro 目录存在"
else
    echo "  ✗ .kiro 目录不存在"
    ((ERRORS++))
fi

if [ -d "$PROJECT_ROOT/.kiro/agents" ]; then
    echo "  ✓ .kiro/agents 目录存在"
else
    echo "  ✗ .kiro/agents 目录不存在"
    ((ERRORS++))
fi

# 2. 检查配置文件
echo ""
echo "⚙️  检查配置文件..."
if [ -f "$PROJECT_ROOT/.kiro/config.json" ]; then
    echo "  ✓ .kiro/config.json 存在"
    if grep -q "bmad_enabled" "$PROJECT_ROOT/.kiro/config.json"; then
        echo "  ✓ bmad_enabled 配置正确"
    else
        echo "  ✗ bmad_enabled 配置缺失"
        ((ERRORS++))
    fi
else
    echo "  ✗ .kiro/config.json 不存在"
    ((ERRORS++))
fi

# 3. 检查初始化脚本
echo ""
echo "🔧 检查初始化脚本..."
if [ -f "$PROJECT_ROOT/init_bmad_kiro.py" ]; then
    echo "  ✓ init_bmad_kiro.py 存在"
else
    echo "  ✗ init_bmad_kiro.py 不存在"
    ((ERRORS++))
fi

if [ -f "$PROJECT_ROOT/init_bmad.sh" ]; then
    echo "  ✓ init_bmad.sh 存在"
else
    echo "  ✗ init_bmad.sh 不存在"
    ((ERRORS++))
fi

if [ -f "$PROJECT_ROOT/start_kiro_bmad.sh" ]; then
    echo "  ✓ start_kiro_bmad.sh 存在"
else
    echo "  ✗ start_kiro_bmad.sh 不存在"
    ((ERRORS++))
fi

# 4. 检查 bmad 模块
echo ""
echo "📦 检查 bmad 模块..."
for module in core bmm bmgd cis bmb; do
    if [ -d "$PROJECT_ROOT/_bmad/$module" ]; then
        echo "  ✓ $module 模块存在"
    else
        echo "  ✗ $module 模块不存在"
        ((ERRORS++))
    fi
done

# 5. 检查工作流文件
echo ""
echo "📋 检查工作流文件..."
if [ -f "$PROJECT_ROOT/_bmad/core/tasks/workflow.xml" ]; then
    echo "  ✓ workflow.xml 存在"
else
    echo "  ✗ workflow.xml 不存在"
    ((ERRORS++))
fi

if [ -f "$PROJECT_ROOT/_bmad/core/module.yaml" ]; then
    echo "  ✓ module.yaml 存在"
else
    echo "  ✗ module.yaml 不存在"
    ((ERRORS++))
fi

# 6. 检查文档
echo ""
echo "📚 检查文档..."
if [ -f "$PROJECT_ROOT/KIRO_BMAD_SETUP.md" ]; then
    echo "  ✓ KIRO_BMAD_SETUP.md 存在"
else
    echo "  ✗ KIRO_BMAD_SETUP.md 不存在"
    ((ERRORS++))
fi

if [ -f "$PROJECT_ROOT/KIRO_BMAD_QUICK_START.md" ]; then
    echo "  ✓ KIRO_BMAD_QUICK_START.md 存在"
else
    echo "  ✗ KIRO_BMAD_QUICK_START.md 不存在"
    ((ERRORS++))
fi

if [ -f "$PROJECT_ROOT/KIRO_BMAD_SOLUTION.md" ]; then
    echo "  ✓ KIRO_BMAD_SOLUTION.md 存在"
else
    echo "  ✗ KIRO_BMAD_SOLUTION.md 不存在"
    ((ERRORS++))
fi

# 7. 总结
echo ""
echo "================================"
if [ $ERRORS -eq 0 ]; then
    echo "✅ 所有检查通过！"
    echo ""
    echo "🚀 你可以现在启动 kiro-cli:"
    echo "   bash start_kiro_bmad.sh"
    exit 0
else
    echo "⚠️  发现 $ERRORS 个问题"
    echo ""
    echo "💡 运行以下命令修复:"
    echo "   python3 init_bmad_kiro.py"
    exit 1
fi
