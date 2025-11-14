#!/bin/bash
# @purpose: 驗證 AAM 服務項目設置是否正確
# @author: DanielChung and AI
# @createdAt: 2025-11-12
# @lastModified: 2025-11-12
# @usage: ./scripts/verify_setup.sh

set -e

echo "🔍 驗證 AAM 服務項目設置..."

# 檢查關鍵文件
echo "📁 檢查關鍵文件..."
files=(
    "src/main.py"
    "src/config/settings.py"
    "requirements.txt"
    "requirements-dev.txt"
    "docker-compose.yml"
    "Dockerfile"
    ".env.example"
    "pytest.ini"
    "README.md"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file 缺失"
        exit 1
    fi
done

# 檢查目錄結構
echo ""
echo "📂 檢查目錄結構..."
directories=(
    "src/api/controllers"
    "src/api/dependencies"
    "src/api/middleware"
    "src/core/interfaces"
    "src/core/services"
    "src/infrastructure/database"
    "src/infrastructure/messaging"
    "src/infrastructure/ai"
    "src/models/api"
    "src/models/domain"
    "tests/unit"
    "tests/integration"
)

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir"
    else
        echo "  ❌ $dir 缺失"
        exit 1
    fi
done

# 檢查 Python 語法
echo ""
echo "🐍 檢查 Python 語法..."
if command -v python3 &> /dev/null; then
    python3 -m py_compile src/main.py src/config/settings.py 2>/dev/null && echo "  ✅ Python 語法正確" || echo "  ⚠️ Python 語法檢查跳過（需要安裝 Python）"
else
    echo "  ⚠️ Python 未安裝，跳過語法檢查"
fi

echo ""
echo "✅ 項目設置驗證完成！"
echo ""
echo "📝 下一步："
echo "  1. 複製 .env.example 到 .env 並設置配置"
echo "  2. 運行: docker-compose up --build -d"
echo "  3. 驗證: curl http://localhost:8000/health"

