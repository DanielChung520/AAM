#!/bin/bash
# @purpose: 推送代碼到 GitHub 的便捷腳本
# @author: DanielChung and AI
# @createdAt: 2025-11-12
# @lastModified: 2025-11-12
# @usage: ./scripts/push-to-github.sh

set -e

echo "🚀 準備推送代碼到 GitHub..."
echo ""

# 檢查遠端倉庫
if ! git remote | grep -q origin; then
    echo "⚠️  遠端倉庫未配置"
    echo "📝 正在設置遠端倉庫..."
    git remote add origin https://github.com/DanielChung520/aam-service.git
    echo "✅ 遠端倉庫已設置"
fi

echo "📋 遠端倉庫配置："
git remote -v
echo ""

# 檢查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  發現未提交的更改："
    git status --short
    echo ""
    read -p "是否要先提交這些更改？(Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo ""
        echo "📝 請輸入提交信息："
        read -r COMMIT_MSG
        if [ -z "$COMMIT_MSG" ]; then
            COMMIT_MSG="chore: 更新代碼"
        fi
        git add .
        git commit -m "$COMMIT_MSG"
        echo "✅ 更改已提交"
    fi
fi

# 顯示當前分支和提交
echo ""
echo "📊 當前狀態："
echo "   分支: $(git branch --show-current)"
echo "   最新提交: $(git log -1 --oneline)"
echo ""

# 確認推送
read -p "是否要推送到 GitHub？(Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "❌ 已取消"
    exit 0
fi

echo ""
echo "📤 正在推送到 GitHub..."
echo ""

# 推送代碼
if git push -u origin main 2>&1; then
    echo ""
    echo "✅ 代碼已成功推送到 GitHub！"
    echo ""
    echo "🌐 倉庫地址："
    echo "   https://github.com/DanielChung520/aam-service"
else
    echo ""
    echo "❌ 推送失敗"
    echo ""
    echo "💡 可能的原因："
    echo "   1. GitHub 倉庫尚未創建"
    echo "      → 請先訪問 https://github.com/new 創建倉庫"
    echo "   2. 認證失敗"
    echo "      → HTTPS: 需要使用 Personal Access Token（不是密碼）"
    echo "      → SSH: 需要配置 SSH key"
    echo ""
    echo "📚 詳細說明請查看：docs/GITHUB_SETUP.md"
    exit 1
fi

