#!/bin/bash

################################################################################
# Prompt Enhancement v2.0.0 - 推送到 GitHub 脚本
#
# 用途：一键推送所有代码和标签到 GitHub
# 使用方法：bash PUSH_TO_GITHUB.sh
#
# 该脚本将执行以下操作：
# 1. 推送 main 分支到 GitHub
# 2. 推送 v2.0.0 标签到 GitHub
# 3. 验证推送结果
# 4. 显示 GitHub 链接供确认
################################################################################

set -e  # 任何命令失败都会停止脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示头部
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Prompt Enhancement v2.0.0 - 推送到 GitHub              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 检查 Git 是否已安装
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 Git，请先安装 Git${NC}"
    exit 1
fi

# 检查是否在 Git 仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ 错误：当前目录不是 Git 仓库${NC}"
    exit 1
fi

# 显示当前分支和状态
echo -e "${YELLOW}📋 当前状态检查：${NC}"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "   分支：$CURRENT_BRANCH"
git status --short

echo ""

# 前置条件检查
echo -e "${YELLOW}🔍 前置条件验证：${NC}"

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}❌ 错误：有未提交的更改，请先提交：${NC}"
    git status
    exit 1
fi
echo "   ✅ 工作目录干净"

# 检查是否在 main 分支
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo -e "${YELLOW}⚠️  警告：当前不在 main/master 分支${NC}"
    echo "   当前分支：$CURRENT_BRANCH"
    read -p "   是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}操作已取消${NC}"
        exit 0
    fi
fi

# 检查远程仓库
echo -n "   检查远程仓库..."
if git remote get-url origin > /dev/null 2>&1; then
    REMOTE_URL=$(git remote get-url origin)
    echo " ✅"
    echo "   远程 URL：$REMOTE_URL"
else
    echo -e "${RED}❌${NC}"
    echo -e "${RED}❌ 错误：未找到远程仓库${NC}"
    exit 1
fi

echo ""

# 显示待推送的提交
echo -e "${YELLOW}📤 待推送的提交：${NC}"
git log --oneline origin/${CURRENT_BRANCH}..HEAD 2>/dev/null | head -10 || git log --oneline -5

echo ""

# 显示待推送的标签
echo -e "${YELLOW}🏷️  待推送的标签：${NC}"
if git tag -l v2.0.0 | grep -q "v2.0.0"; then
    echo "   ✅ v2.0.0"
    git tag -l v2.0.0 -n 1
else
    echo "   ⚠️  未找到 v2.0.0 标签"
fi

echo ""

# 用户确认
echo -e "${BLUE}是否确认推送到 GitHub?${NC}"
read -p "请输入 'yes' 或 'y' 确认: " CONFIRM

if [[ ! "$CONFIRM" =~ ^[Yy][Ee][Ss]?$ ]]; then
    echo -e "${YELLOW}操作已取消${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}🚀 开始推送...${NC}"
echo ""

# ============================================================================
# 步骤 1: 推送主分支
# ============================================================================
echo -e "${YELLOW}第 1/2 步：推送 $CURRENT_BRANCH 分支...${NC}"
if git push origin "$CURRENT_BRANCH"; then
    echo -e "${GREEN}✅ $CURRENT_BRANCH 分支推送成功${NC}"
else
    echo -e "${RED}❌ $CURRENT_BRANCH 分支推送失败${NC}"
    echo -e "${RED}错误信息：${NC}"
    echo "常见原因："
    echo "  1. 网络连接失败 - 检查网络"
    echo "  2. 认证失败 - 检查 GitHub token 配置"
    echo "  3. 权限不足 - 检查是否有 push 权限"
    echo "  4. 分支保护规则 - 检查 GitHub 保护规则"
    exit 1
fi

echo ""

# ============================================================================
# 步骤 2: 推送标签
# ============================================================================
echo -e "${YELLOW}第 2/2 步：推送 v2.0.0 标签...${NC}"
if git push origin v2.0.0; then
    echo -e "${GREEN}✅ v2.0.0 标签推送成功${NC}"
else
    echo -e "${RED}❌ v2.0.0 标签推送失败${NC}"
    echo -e "${RED}可能原因：${NC}"
    echo "  1. 标签已存在 - 使用 git push origin :refs/tags/v2.0.0 删除后重试"
    echo "  2. 权限不足 - 检查是否有标签 push 权限"
    exit 1
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

# ============================================================================
# 验证步骤
# ============================================================================
echo -e "${YELLOW}🔍 验证推送结果...${NC}"
echo ""

echo "验证 1：检查本地与远程同步"
git status
echo ""

echo "验证 2：检查远程分支最新提交"
git log origin/${CURRENT_BRANCH} --oneline -3
echo ""

echo "验证 3：检查远程标签"
if git ls-remote --tags origin | grep -q "v2.0.0"; then
    echo -e "${GREEN}✅ v2.0.0 标签已推送到远程${NC}"
    git ls-remote --tags origin | grep v2.0.0
else
    echo -e "${RED}⚠️  v2.0.0 标签未在远程仓库中找到${NC}"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ 推送完成！${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================================================
# 提供 GitHub 链接
# ============================================================================
REPO_OWNER="jodykwong"
REPO_NAME="Prompt-Enhancement"

echo -e "${BLUE}📍 请访问以下链接确认推送结果：${NC}"
echo ""
echo "1️⃣  提交历史："
echo "   🔗 https://github.com/$REPO_OWNER/$REPO_NAME/commits/${CURRENT_BRANCH}"
echo ""
echo "2️⃣  版本标签："
echo "   🔗 https://github.com/$REPO_OWNER/$REPO_NAME/tags"
echo ""
echo "3️⃣  最新版本标签详情："
echo "   🔗 https://github.com/$REPO_OWNER/$REPO_NAME/releases/tag/v2.0.0"
echo ""

# ============================================================================
# 后续步骤提示
# ============================================================================
echo -e "${BLUE}📋 下一步操作：${NC}"
echo ""
echo "1. 创建 GitHub Release（推荐）"
echo "   访问：https://github.com/$REPO_OWNER/$REPO_NAME/releases/new"
echo "   选择 v2.0.0 标签，添加 Release Notes"
echo ""
echo "2. 发布到 PyPI"
echo "   cd packages/python/"
echo "   twine upload dist/*"
echo ""
echo "3. 发布到 NPM"
echo "   cd packages/npm/"
echo "   npm login"
echo "   npm publish"
echo ""
echo "4. 更新项目元数据"
echo "   在 GitHub 项目设置中添加话题标签和描述"
echo ""

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}🎉 v2.0.0 已成功推送到 GitHub！${NC}"
echo ""
echo "提示：如需查看详细的发布说明，请阅读 RELEASE_COMMANDS.md 文件"
echo ""
