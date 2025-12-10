#!/bin/bash
# Prompt Enhancement - Claude Code Integration Installer
# Version: 1.0.0 (P0.6)
#
# This script installs Prompt Enhancement as a Claude Code command.
# It will:
# 1. Check dependencies
# 2. Prompt for DeepSeek API key
# 3. Install the /pe command
# 4. Verify installation

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
COMMANDS_DIR="$CLAUDE_DIR/commands"
SCRIPTS_DIR="$COMMANDS_DIR/scripts"
ENV_FILE="$PROJECT_ROOT/.env"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Prompt Enhancement - Claude Code Installer${NC}"
echo -e "${BLUE}  Version: 1.0.0 (P0.6)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ============================================================================
# Step 1: Check Prerequisites
# ============================================================================

echo -e "${YELLOW}[1/5]${NC} 检查系统依赖..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python 3 not found${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python ${PYTHON_VERSION} found"

# Check pip
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo -e "${RED}❌ Error: pip not found${NC}"
    echo "Please install pip for Python 3"
    exit 1
fi

echo -e "${GREEN}✓${NC} pip found"

# Check Claude Code directory
if [ ! -d "$CLAUDE_DIR" ]; then
    echo -e "${RED}❌ Error: Claude Code directory not found${NC}"
    echo "Expected: $CLAUDE_DIR"
    echo ""
    echo "Please ensure Claude Code is installed and run:"
    echo "  mkdir -p $CLAUDE_DIR/commands"
    exit 1
fi

echo -e "${GREEN}✓${NC} Claude Code directory found"

# ============================================================================
# Step 2: Install Python Dependencies
# ============================================================================

echo ""
echo -e "${YELLOW}[2/5]${NC} 安装 Python 依赖..."

cd "$PROJECT_ROOT"

if [ -f "requirements.txt" ]; then
    echo "Installing from requirements.txt..."
    python3 -m pip install -q -r requirements.txt
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${RED}❌ Error: requirements.txt not found${NC}"
    exit 1
fi

# ============================================================================
# Step 3: Configure API Key
# ============================================================================

echo ""
echo -e "${YELLOW}[3/5]${NC} 配置 DeepSeek API Key..."

# Check if .env exists and has API key
if [ -f "$ENV_FILE" ] && grep -q "^DEEPSEEK_API_KEY=" "$ENV_FILE" && [ -n "$(grep "^DEEPSEEK_API_KEY=" "$ENV_FILE" | cut -d'=' -f2)" ]; then
    EXISTING_KEY=$(grep "^DEEPSEEK_API_KEY=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    if [ -n "$EXISTING_KEY" ] && [ "$EXISTING_KEY" != "your-api-key-here" ]; then
        echo -e "${GREEN}✓${NC} API key already configured"
        echo "Current key: ${EXISTING_KEY:0:10}..."

        read -p "Do you want to update it? (y/N): " UPDATE_KEY
        if [ "$UPDATE_KEY" != "y" ] && [ "$UPDATE_KEY" != "Y" ]; then
            echo "Keeping existing API key"
        else
            PROMPT_FOR_KEY=true
        fi
    else
        PROMPT_FOR_KEY=true
    fi
else
    PROMPT_FOR_KEY=true
fi

if [ "$PROMPT_FOR_KEY" = true ]; then
    echo ""
    echo "🔑 Please enter your DeepSeek API key"
    echo "   (Get it from: https://platform.deepseek.com)"
    echo ""
    read -p "API Key: " DEEPSEEK_API_KEY

    if [ -z "$DEEPSEEK_API_KEY" ]; then
        echo -e "${RED}❌ Error: API key cannot be empty${NC}"
        exit 1
    fi

    # Create or update .env file
    if [ -f "$ENV_FILE" ]; then
        # Remove old DEEPSEEK_API_KEY if exists
        grep -v "^DEEPSEEK_API_KEY=" "$ENV_FILE" > "$ENV_FILE.tmp" || true
        mv "$ENV_FILE.tmp" "$ENV_FILE"
    else
        touch "$ENV_FILE"
    fi

    # Add new API key
    echo "DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY" >> "$ENV_FILE"

    echo -e "${GREEN}✓${NC} API key configured"
fi

# ============================================================================
# Step 4: Install Claude Code Command
# ============================================================================

echo ""
echo -e "${YELLOW}[4/5]${NC} 安装 Claude Code 命令..."

# Create scripts directory
mkdir -p "$SCRIPTS_DIR"
echo -e "${GREEN}✓${NC} Scripts directory ready: $SCRIPTS_DIR"

# Copy enhance.py script
if [ -f "$COMMANDS_DIR/scripts/enhance.py" ]; then
    echo "enhance.py already exists, updating..."
fi

cp "$PROJECT_ROOT/.claude/commands/scripts/enhance.py" "$SCRIPTS_DIR/enhance.py"
chmod +x "$SCRIPTS_DIR/enhance.py"
echo -e "${GREEN}✓${NC} enhance.py installed"

# Copy pe.md command
if [ -f "$COMMANDS_DIR/pe.md" ]; then
    echo "pe.md already exists, updating..."
fi

cp "$PROJECT_ROOT/.claude/commands/pe.md" "$COMMANDS_DIR/pe.md"
echo -e "${GREEN}✓${NC} pe.md command installed"

# ============================================================================
# Step 5: Verify Installation
# ============================================================================

echo ""
echo -e "${YELLOW}[5/5]${NC} 验证安装..."

# Check files exist
if [ ! -f "$SCRIPTS_DIR/enhance.py" ]; then
    echo -e "${RED}❌ Error: enhance.py not found${NC}"
    exit 1
fi

if [ ! -f "$COMMANDS_DIR/pe.md" ]; then
    echo -e "${RED}❌ Error: pe.md not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} All files installed correctly"

# Test Python script
echo ""
echo "Testing enhance.py..."
if python3 "$SCRIPTS_DIR/enhance.py" 2>&1 | grep -q "No prompt provided"; then
    echo -e "${GREEN}✓${NC} Script is executable"
else
    echo -e "${YELLOW}⚠${NC}  Script test inconclusive, but files are in place"
fi

# ============================================================================
# Installation Complete
# ============================================================================

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ Installation Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📍 Installation Summary:"
echo "  • Project: $PROJECT_ROOT"
echo "  • Command: $COMMANDS_DIR/pe.md"
echo "  • Script:  $SCRIPTS_DIR/enhance.py"
echo "  • Config:  $ENV_FILE"
echo ""
echo "🚀 Usage:"
echo "  In Claude Code, type:"
echo "    /pe \"your prompt here\""
echo ""
echo "📚 Documentation:"
echo "  • README: $PROJECT_ROOT/README.md"
echo "  • User Guide: $PROJECT_ROOT/USAGE_GUIDE.md"
echo "  • API Reference: $PROJECT_ROOT/API_REFERENCE.md"
echo ""
echo "💡 Next Steps:"
echo "  1. Start or restart Claude Code"
echo "  2. Try: /pe \"修复bug\""
echo "  3. Review the enhanced prompt"
echo "  4. Copy and execute if satisfied"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
