#!/bin/bash
# @purpose: 啟動 AAM 服務的 Docker 開發環境
# @author: DanielChung and AI
# @createdAt: 2025-11-12
# @lastModified: 2025-11-12
# @usage: ./scripts/start-dev.sh

set -e

echo "🔍 檢查 Docker 環境..."

# 檢查 Docker 是否安裝
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝，請先安裝 Docker Desktop"
    exit 1
fi

# 檢查 Docker daemon 是否運行
if ! docker info >/dev/null 2>&1; then
    echo "⚠️  Docker daemon 未運行"
    echo "📝 請執行以下步驟："
    echo "   1. 打開 Docker Desktop 應用程序"
    echo "   2. 等待 Docker Desktop 完全啟動（圖標不再動畫）"
    echo "   3. 再次運行此腳本"
    echo ""
    echo "💡 或手動啟動："
    echo "   open -a Docker"
    exit 1
fi

echo "✅ Docker daemon 已運行"

# 檢查 .env 文件
if [ ! -f .env ]; then
    echo "📝 創建 .env 文件..."
    cp .env.example .env
    echo "⚠️  請編輯 .env 文件，設置 API_KEY 和 SECRET_KEY"
    echo "   然後再次運行此腳本"
    exit 1
fi

# 檢查必要的配置
if grep -q "your-secret-api-key-change-in-production" .env || \
   grep -q "your-secret-key-change-in-production" .env; then
    echo "⚠️  .env 文件中仍使用默認值"
    echo "   請編輯 .env 文件，設置安全的 API_KEY 和 SECRET_KEY"
    exit 1
fi

echo "✅ 環境配置檢查通過"

# 進入項目目錄
cd "$(dirname "$0")/.."

# 檢查服務是否已經在運行
echo ""
echo "🔍 檢查服務狀態..."
if docker-compose -f docker-compose.dev.yml ps 2>/dev/null | grep -q "Up\|healthy"; then
    echo "⚠️  檢測到服務已在運行中"
    echo ""
    echo "請選擇操作："
    echo "  1) 重啟服務 (restart)"
    echo "  2) 停止服務 (stop)"
    echo "  3) 重新構建並啟動 (rebuild)"
    echo "  4) 取消 (cancel)"
    echo ""
    read -p "請輸入選項 (1-4，默認: 1): " choice
    choice=${choice:-1}
    
    case $choice in
        1)
            echo ""
            echo "🔄 重啟服務..."
            docker-compose -f docker-compose.dev.yml restart
            echo "✅ 服務已重啟"
            SKIP_STATUS=false
            ;;
        2)
            echo ""
            echo "🛑 停止服務..."
            docker-compose -f docker-compose.dev.yml down
            echo "✅ 服務已停止"
            exit 0
            ;;
        3)
            echo ""
            echo "🔨 重新構建並啟動服務..."
            echo "   這可能需要幾分鐘時間..."
            docker-compose -f docker-compose.dev.yml down
            docker-compose -f docker-compose.dev.yml up --build -d
            SKIP_STATUS=false
            ;;
        4)
            echo "❌ 操作已取消"
            exit 0
            ;;
        *)
            echo "❌ 無效選項，操作已取消"
            exit 1
            ;;
    esac
else
    echo "✅ 服務未運行，開始啟動..."
    echo ""
    echo "🚀 開始構建並啟動 Docker 服務..."
    echo "   這可能需要幾分鐘時間..."
    echo ""
    
    # 構建並啟動服務（使用開發環境配置）
    docker-compose -f docker-compose.dev.yml up --build -d
    SKIP_STATUS=false
fi

# 如果沒有跳過，顯示服務狀態
if [ "${SKIP_STATUS:-false}" = "false" ]; then
    echo ""
    echo "⏳ 等待服務啟動..."
    sleep 10
    
    # 檢查服務狀態
    echo ""
    echo "📊 服務狀態："
    docker-compose -f docker-compose.dev.yml ps
    
    echo ""
    echo "✅ 服務啟動完成！"
fi
echo ""
echo "📝 有用的命令："
echo "   查看日誌:     docker-compose -f docker-compose.dev.yml logs -f aam-service"
echo "   查看所有日誌: docker-compose -f docker-compose.dev.yml logs -f"
echo "   停止服務:     docker-compose -f docker-compose.dev.yml down"
echo "   重啟服務:     docker-compose -f docker-compose.dev.yml restart"
echo ""
echo "🌐 服務地址："
echo "   AAM Service:      http://localhost:8000"
echo "   API 文檔:         http://localhost:8000/docs"
echo "   健康檢查:         http://localhost:8000/health"
echo "   RabbitMQ 管理:    http://localhost:15672 (admin/admin)"
echo ""
echo "🧪 測試服務："
echo "   curl http://localhost:8000/health"

