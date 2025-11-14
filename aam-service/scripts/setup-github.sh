#!/bin/bash
# @purpose: 設置 GitHub 遠端倉庫連接
# @author: DanielChung and AI
# @createdAt: 2025-11-12
# @lastModified: 2025-11-12
# @usage: ./scripts/setup-github.sh [github-username] [repo-name]

set -e

GITHUB_USERNAME=${1:-""}
REPO_NAME=${2:-"aam-service"}

echo "🔧 設置 GitHub 遠端倉庫連接..."
echo ""

# 檢查是否已配置遠端倉庫
if git remote | grep -q origin; then
    echo "⚠️  遠端倉庫已配置："
    git remote -v
    echo ""
    read -p "是否要更新遠端倉庫 URL？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "✅ 保持現有配置"
        exit 0
    fi
    git remote remove origin
fi

# 如果沒有提供用戶名，提示輸入
if [ -z "$GITHUB_USERNAME" ]; then
    echo "📝 請輸入您的 GitHub 用戶名："
    read -r GITHUB_USERNAME
fi

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ GitHub 用戶名不能為空"
    exit 1
fi

echo ""
echo "📋 配置信息："
echo "   GitHub 用戶名: $GITHUB_USERNAME"
echo "   倉庫名稱: $REPO_NAME"
echo ""

# 檢查是否使用 SSH
if [ -f ~/.ssh/id_rsa ] || [ -f ~/.ssh/id_ed25519 ]; then
    echo "🔑 檢測到 SSH key，使用 SSH 協議"
    REPO_URL="git@github.com:${GITHUB_USERNAME}/${REPO_NAME}.git"
else
    echo "🔐 使用 HTTPS 協議"
    REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
fi

echo "   遠端 URL: $REPO_URL"
echo ""

# 確認
read -p "是否繼續設置？(Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "❌ 已取消"
    exit 0
fi

# 添加遠端倉庫
echo ""
echo "📝 添加遠端倉庫..."
git remote add origin "$REPO_URL"

# 驗證
echo ""
echo "✅ 遠端倉庫已配置："
git remote -v

echo ""
echo "📋 下一步操作："
echo ""
echo "1. 在 GitHub 創建倉庫："
echo "   - 訪問: https://github.com/new"
echo "   - 倉庫名稱: $REPO_NAME"
echo "   - 描述: AI-Augmented Memory (AAM) Service"
echo "   - 選擇 Private 或 Public"
echo "   - ⚠️  不要勾選「Initialize with README」（我們已有 README）"
echo "   - 點擊「Create repository」"
echo ""
echo "2. 推送代碼到 GitHub："
echo "   git push -u origin main"
echo ""
echo "💡 提示：如果倉庫已存在，可以直接執行推送命令"

