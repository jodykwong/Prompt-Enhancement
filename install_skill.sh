#!/bin/bash
#
# Prompt Enhancement Skill - 快速安装脚本
#
# 用法:
#   ./install_skill.sh
#
# 功能:
#   1. 创建 Skill 目录结构
#   2. 复制所有必要文件
#   3. 设置文件权限
#   4. 验证安装
#

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# 检查前置条件
check_prerequisites() {
    print_header "检查前置条件"
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 未安装"
        exit 1
    fi
    print_success "Python 3 已安装: $(python3 --version)"
    
    # 检查项目目录
    PROJECT_DIR="/Users/jodykwong/Documents/augment-projects/Prompt-Enhancement"
    if [ ! -d "$PROJECT_DIR" ]; then
        print_error "项目目录不存在: $PROJECT_DIR"
        exit 1
    fi
    print_success "项目目录存在: $PROJECT_DIR"
    
    # 检查 async_prompt_enhancer.py
    if [ ! -f "$PROJECT_DIR/async_prompt_enhancer.py" ]; then
        print_error "async_prompt_enhancer.py 不存在"
        exit 1
    fi
    print_success "async_prompt_enhancer.py 存在"
    
    # 检查环境变量
    if [ -z "$DEEPSEEK_API_KEY" ]; then
        print_warning "DEEPSEEK_API_KEY 环境变量未设置"
        print_info "请在安装后设置: export DEEPSEEK_API_KEY='your-api-key-here'"
    else
        print_success "DEEPSEEK_API_KEY 已设置"
    fi
}

# 创建目录结构
create_directories() {
    print_header "创建目录结构"
    
    SKILL_DIR="$HOME/.claude/skills/prompt-enhancement"
    
    # 创建主目录
    mkdir -p "$SKILL_DIR/scripts"
    print_success "创建目录: $SKILL_DIR"
    print_success "创建目录: $SKILL_DIR/scripts"
}

# 复制文件
copy_files() {
    print_header "复制文件"
    
    SKILL_DIR="$HOME/.claude/skills/prompt-enhancement"
    TEMPLATE_DIR="$(pwd)/skill_templates"
    
    # 检查模板目录
    if [ ! -d "$TEMPLATE_DIR" ]; then
        print_error "模板目录不存在: $TEMPLATE_DIR"
        print_info "请确保在项目根目录运行此脚本"
        exit 1
    fi
    
    # 复制 SKILL.md
    if [ -f "$TEMPLATE_DIR/SKILL.md" ]; then
        cp "$TEMPLATE_DIR/SKILL.md" "$SKILL_DIR/"
        print_success "复制: SKILL.md"
    else
        print_error "SKILL.md 不存在: $TEMPLATE_DIR/SKILL.md"
        exit 1
    fi
    
    # 复制 enhance.py
    if [ -f "$TEMPLATE_DIR/enhance.py" ]; then
        cp "$TEMPLATE_DIR/enhance.py" "$SKILL_DIR/scripts/"
        print_success "复制: enhance.py"
    else
        print_error "enhance.py 不存在: $TEMPLATE_DIR/enhance.py"
        exit 1
    fi
    
    # 复制 README.md
    if [ -f "$TEMPLATE_DIR/README.md" ]; then
        cp "$TEMPLATE_DIR/README.md" "$SKILL_DIR/"
        print_success "复制: README.md"
    else
        print_warning "README.md 不存在，跳过"
    fi
    
    # 创建 requirements.txt
    cat > "$SKILL_DIR/requirements.txt" << 'EOF'
openai>=1.0.0
python-dotenv>=1.0.0
EOF
    print_success "创建: requirements.txt"
}

# 设置权限
set_permissions() {
    print_header "设置文件权限"
    
    SKILL_DIR="$HOME/.claude/skills/prompt-enhancement"
    
    chmod +x "$SKILL_DIR/scripts/enhance.py"
    print_success "设置 enhance.py 为可执行"
}

# 验证安装
verify_installation() {
    print_header "验证安装"
    
    SKILL_DIR="$HOME/.claude/skills/prompt-enhancement"
    
    # 检查文件存在
    if [ -f "$SKILL_DIR/SKILL.md" ]; then
        print_success "SKILL.md 存在"
    else
        print_error "SKILL.md 不存在"
        return 1
    fi
    
    if [ -f "$SKILL_DIR/scripts/enhance.py" ]; then
        print_success "enhance.py 存在"
    else
        print_error "enhance.py 不存在"
        return 1
    fi
    
    if [ -x "$SKILL_DIR/scripts/enhance.py" ]; then
        print_success "enhance.py 可执行"
    else
        print_error "enhance.py 不可执行"
        return 1
    fi
    
    # 测试脚本（如果 API Key 已设置）
    if [ -n "$DEEPSEEK_API_KEY" ]; then
        print_info "测试 enhance.py 脚本..."
        if python3 "$SKILL_DIR/scripts/enhance.py" "test" > /dev/null 2>&1; then
            print_success "脚本测试通过"
        else
            print_warning "脚本测试失败（可能是网络问题）"
        fi
    fi
}

# 显示后续步骤
show_next_steps() {
    print_header "安装完成！"
    
    echo ""
    echo -e "${GREEN}✅ Prompt Enhancement Skill 已成功安装！${NC}"
    echo ""
    echo -e "${BLUE}📍 安装位置:${NC}"
    echo "   $HOME/.claude/skills/prompt-enhancement/"
    echo ""
    
    if [ -z "$DEEPSEEK_API_KEY" ]; then
        echo -e "${YELLOW}⚠️  下一步: 设置 API Key${NC}"
        echo ""
        echo "   1. 添加到 shell 配置文件:"
        echo "      echo 'export DEEPSEEK_API_KEY=\"your-api-key-here\"' >> ~/.zshrc"
        echo "      source ~/.zshrc"
        echo ""
        echo "   2. 或临时设置:"
        echo "      export DEEPSEEK_API_KEY=\"your-api-key-here\""
        echo ""
    fi
    
    echo -e "${BLUE}🚀 使用方法:${NC}"
    echo ""
    echo "   1. 启动 Claude Code:"
    echo "      claude-code"
    echo ""
    echo "   2. 使用 /pe 命令:"
    echo "      /pe 修复登录页面的 bug"
    echo ""
    echo "   3. 或自然语言触发:"
    echo "      请先增强这个提示词再执行：优化数据库查询"
    echo ""
    echo -e "${BLUE}📖 更多信息:${NC}"
    echo "   查看 README: $HOME/.claude/skills/prompt-enhancement/README.md"
    echo ""
}

# 主函数
main() {
    print_header "Prompt Enhancement Skill - 安装程序"
    
    check_prerequisites
    create_directories
    copy_files
    set_permissions
    verify_installation
    show_next_steps
}

# 运行主函数
main

