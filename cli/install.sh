#!/bin/bash

###############################################################################
# Prompt Enhancement - One-Click Installer for Linux/macOS
#
# 用法：
#   bash install.sh                      # 安装到当前目录
#   bash install.sh /path/to/project     # 安装到指定项目
#
# 或远程运行：
#   bash <(curl -fsSL https://repo/install.sh) /path/to/project
###############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SOURCE_ROOT="$(dirname "$SCRIPT_DIR")"

# 获取目标项目路径
TARGET_PROJECT="${1:-.}"
TARGET_PROJECT="$(cd "$TARGET_PROJECT" && pwd)"

# 验证和变量
CLAUDE_DIR="$TARGET_PROJECT/.claude"
COMMANDS_DIR="$CLAUDE_DIR/commands"
HOOKS_DIR="$CLAUDE_DIR/hooks"
SCRIPTS_DIR="$COMMANDS_DIR/scripts"
ENV_FILE="$TARGET_PROJECT/.env"

###############################################################################
# 辅助函数
###############################################################################

print_header() {
    echo ""
    echo "${BLUE}================================================================================${NC}"
    echo "${BLUE}🚀 Prompt Enhancement 一键安装程序${NC}"
    echo "${BLUE}================================================================================${NC}"
    echo ""
}

print_section() {
    echo ""
    echo "${BLUE}▸ $1${NC}"
}

print_success() {
    echo "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo "${RED}❌ $1${NC}"
}

print_footer() {
    echo ""
    echo "${BLUE}================================================================================${NC}"
    echo ""
}

###############################################################################
# 主安装流程
###############################################################################

main() {
    print_header

    # 显示目标项目
    echo "📂 目标项目: $TARGET_PROJECT"
    echo ""

    # 1. 验证目标项目
    print_section "验证目标项目"
    if [ ! -d "$TARGET_PROJECT" ]; then
        print_error "目标项目路径不存在: $TARGET_PROJECT"
        exit 1
    fi
    print_success "项目路径有效"

    # 检查是否看起来像一个项目
    if [ ! -f "$TARGET_PROJECT/.git" ] && [ ! -f "$TARGET_PROJECT/package.json" ] && [ ! -f "$TARGET_PROJECT/setup.py" ]; then
        print_warning "目标项目可能不是一个有效的项目目录"
    fi

    # 2. 创建目录结构
    print_section "设置目录结构"
    mkdir -p "$COMMANDS_DIR"
    mkdir -p "$HOOKS_DIR"
    mkdir -p "$SCRIPTS_DIR"
    print_success "创建目录: .claude/commands"
    print_success "创建目录: .claude/hooks"

    # 3. 安装 /pe 命令
    print_section "安装 /pe 命令"

    SOURCE_PE="$SOURCE_ROOT/.claude/commands/pe.md"
    TARGET_PE="$COMMANDS_DIR/pe.md"

    if [ ! -f "$SOURCE_PE" ]; then
        print_error "找不到源 /pe 命令: $SOURCE_PE"
        exit 1
    fi

    # 尝试符号链接
    rm -f "$TARGET_PE" 2>/dev/null || true

    if ln -s "$SOURCE_PE" "$TARGET_PE" 2>/dev/null; then
        print_success "创建符号链接: pe.md -> $SOURCE_PE"
    else
        # 如果符号链接失败，使用复制
        cp "$SOURCE_PE" "$TARGET_PE"
        print_warning "使用文件复制（符号链接不支持）"
        print_success "复制文件: $SOURCE_PE"
    fi

    # 4. 安装支持脚本
    print_section "安装支持脚本"

    SOURCE_SCRIPTS="$SOURCE_ROOT/.claude/commands/scripts"
    if [ -d "$SOURCE_SCRIPTS" ]; then
        cp -r "$SOURCE_SCRIPTS"/* "$SCRIPTS_DIR/" 2>/dev/null || true
        print_success "复制脚本目录"
    fi

    # 复制核心 Python 模块
    for module in enhanced_prompt_generator.py async_prompt_enhancer.py context_collector.py; do
        if [ -f "$SOURCE_ROOT/$module" ]; then
            cp "$SOURCE_ROOT/$module" "$COMMANDS_DIR/"
            print_success "复制模块: $module"
        fi
    done

    # 5. 设置 .env 文件
    print_section "配置环境变量"

    if [ ! -f "$ENV_FILE" ]; then
        # 尝试从 .env.example 复制
        if [ -f "$SOURCE_ROOT/.env.example" ]; then
            cp "$SOURCE_ROOT/.env.example" "$ENV_FILE"
            print_success "从 .env.example 创建 .env"
        else
            # 创建最小的 .env
            cat > "$ENV_FILE" <<'EOF'
# DeepSeek API 配置
DEEPSEEK_API_KEY=your_api_key_here
EOF
            print_success "创建最小 .env 文件"
        fi
    else
        print_success ".env 文件已存在"
    fi

    # 6. 验证安装
    print_section "验证安装"

    all_ok=true

    if [ -f "$COMMANDS_DIR/pe.md" ]; then
        print_success "pe.md 命令已安装"
    else
        print_warning "pe.md 未找到"
        all_ok=false
    fi

    if [ -f "$SCRIPTS_DIR/enhance.py" ]; then
        print_success "enhance.py 脚本已安装"
    else
        print_warning "enhance.py 未找到"
        all_ok=false
    fi

    if [ -f "$ENV_FILE" ]; then
        print_success ".env 文件已创建"
    else
        print_warning ".env 未找到"
        all_ok=false
    fi

    # 显示后续步骤
    print_footer

    if [ "$all_ok" = true ]; then
        echo "${GREEN}✅ 安装完成！${NC}"
    else
        echo "${YELLOW}⚠️  安装完成，但有些文件缺失${NC}"
    fi

    echo ""
    echo "📝 后续步骤："
    echo ""
    echo "1️⃣  配置 DeepSeek API 密钥:"
    echo "   编辑 $ENV_FILE"
    echo "   设置 DEEPSEEK_API_KEY=your-api-key-here"
    echo ""
    echo "2️⃣  测试功能:"
    echo "   在 Claude Code 中输入:"
    echo "   /pe 修复登录页面的bug"
    echo ""
    echo "3️⃣  获取更多帮助:"
    echo "   https://github.com/jodykwong/Prompt-Enhancement"
    echo ""
    echo "================================================================================"
    echo ""
}

# 运行主函数
main "$@"
