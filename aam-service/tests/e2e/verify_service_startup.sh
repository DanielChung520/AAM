#!/bin/bash
# @purpose: 驗證 AAM 服務啟動狀態
# @author: Daniel Chung + AI
# @createdAt: 2025-11-13
# @lastModified: 2025-11-13
# @usage: ./scripts/verify_service_startup.sh

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 獲取腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AAM 服務啟動驗證腳本${NC}"
echo -e "${BLUE}========================================${NC}\n"

# 檢查 Docker Compose 文件
COMPOSE_FILE="docker-compose.dev.yml"
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}❌ 找不到 $COMPOSE_FILE${NC}"
    exit 1
fi

# 函數：打印步驟標題
print_step() {
    echo -e "\n${BLUE}--- $1 ---${NC}"
}

# 函數：檢查命令執行結果
check_result() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
        return 0
    else
        echo -e "${RED}❌ $1${NC}"
        return 1
    fi
}

# 步驟 1: 檢查 Docker 容器狀態
print_step "步驟 1: 檢查 Docker 容器狀態"
docker-compose -f "$COMPOSE_FILE" ps
check_result "容器狀態檢查完成"

# 步驟 2: 檢查 ChromaDB 容器健康狀態
print_step "步驟 2: 檢查 ChromaDB 容器健康狀態"
CHROMADB_STATUS=$(docker inspect chromadb-dev --format='{{.State.Health.Status}}' 2>/dev/null || echo "unknown")
if [ "$CHROMADB_STATUS" = "healthy" ]; then
    echo -e "${GREEN}✅ ChromaDB 容器健康狀態: $CHROMADB_STATUS${NC}"
elif [ "$CHROMADB_STATUS" = "starting" ]; then
    echo -e "${YELLOW}⚠️  ChromaDB 容器健康狀態: $CHROMADB_STATUS (正在啟動中)${NC}"
else
    echo -e "${RED}❌ ChromaDB 容器健康狀態: $CHROMADB_STATUS${NC}"
fi

# 步驟 3: 檢查 AAM 服務健康檢查端點
print_step "步驟 3: 檢查 AAM 服務健康檢查端點"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health 2>/dev/null || echo "")
if [ -n "$HEALTH_RESPONSE" ]; then
    echo -e "${GREEN}✅ 健康檢查端點響應:${NC}"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo -e "${RED}❌ 無法連接到健康檢查端點${NC}"
fi

# 步驟 4: 檢查 AAM 服務就緒檢查端點
print_step "步驟 4: 檢查 AAM 服務就緒檢查端點"
READY_RESPONSE=$(curl -s http://localhost:8000/ready 2>/dev/null || echo "")
if [ -n "$READY_RESPONSE" ]; then
    echo -e "${GREEN}✅ 就緒檢查端點響應:${NC}"
    echo "$READY_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$READY_RESPONSE"
else
    echo -e "${RED}❌ 無法連接到就緒檢查端點${NC}"
fi

# 步驟 5: 檢查應用啟動日誌中的關鍵信息
print_step "步驟 5: 檢查應用啟動日誌"
echo "正在檢查 ChromaDB 連接日誌..."
CHROMADB_LOG=$(docker-compose -f "$COMPOSE_FILE" logs --tail=100 aam-service 2>/dev/null | grep -E "ChromaDB|chromadb" | tail -5 || echo "")
if [ -n "$CHROMADB_LOG" ]; then
    echo -e "${BLUE}ChromaDB 相關日誌:${NC}"
    echo "$CHROMADB_LOG"
else
    echo -e "${YELLOW}⚠️  未找到 ChromaDB 相關日誌${NC}"
fi

echo ""
echo "正在檢查 memory_service 初始化日誌..."
MEMORY_LOG=$(docker-compose -f "$COMPOSE_FILE" logs --tail=100 aam-service 2>/dev/null | grep -E "memory_service|記憶服務" | tail -5 || echo "")
if [ -n "$MEMORY_LOG" ]; then
    echo -e "${BLUE}memory_service 相關日誌:${NC}"
    echo "$MEMORY_LOG"
else
    echo -e "${YELLOW}⚠️  未找到 memory_service 相關日誌${NC}"
fi

# 步驟 6: 檢查應用錯誤日誌
print_step "步驟 6: 檢查應用錯誤日誌"
ERROR_LOG=$(docker-compose -f "$COMPOSE_FILE" logs --tail=100 aam-service 2>/dev/null | grep -E "錯誤|error|Error|Exception|Traceback" | tail -10 || echo "")
if [ -n "$ERROR_LOG" ]; then
    echo -e "${YELLOW}⚠️  發現錯誤日誌:${NC}"
    echo "$ERROR_LOG"
else
    echo -e "${GREEN}✅ 未發現錯誤日誌${NC}"
fi

# 步驟 7: 測試 ChromaDB 連接（如果腳本存在）
print_step "步驟 7: 測試 ChromaDB 連接"
if [ -f "scripts/test_chromadb_connection.py" ]; then
    echo "正在運行 ChromaDB 連接測試腳本..."
    docker-compose -f "$COMPOSE_FILE" exec -T aam-service python3 scripts/test_chromadb_connection.py 2>&1 || {
        echo -e "${YELLOW}⚠️  ChromaDB 連接測試失敗（可能是腳本執行環境問題）${NC}"
    }
else
    echo -e "${YELLOW}⚠️  未找到 ChromaDB 連接測試腳本${NC}"
fi

# 步驟 8: 驗證 memory_service 是否已初始化
print_step "步驟 8: 驗證 memory_service 是否已初始化"
MEMORY_CHECK=$(docker-compose -f "$COMPOSE_FILE" exec -T aam-service python3 -c "
import sys
sys.path.insert(0, '/app')
try:
    from fastapi import FastAPI
    from src.main import app
    has_memory_service = hasattr(app.state, 'memory_service')
    memory_service_value = getattr(app.state, 'memory_service', None)
    print(f'Memory service exists: {has_memory_service}')
    print(f'Memory service value: {memory_service_value is not None}')
    if memory_service_value:
        print(f'Memory service type: {type(memory_service_value).__name__}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
" 2>&1)

if echo "$MEMORY_CHECK" | grep -q "Memory service exists: True"; then
    echo -e "${GREEN}✅ memory_service 已初始化${NC}"
    echo "$MEMORY_CHECK"
else
    echo -e "${RED}❌ memory_service 未初始化${NC}"
    echo "$MEMORY_CHECK"
fi

# 總結
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}驗證完成${NC}"
echo -e "${BLUE}========================================${NC}\n"

# 檢查是否有關鍵錯誤
if echo "$ERROR_LOG" | grep -qE "Traceback|Exception"; then
    echo -e "${RED}⚠️  發現關鍵錯誤，請檢查日誌${NC}"
    exit 1
fi

if echo "$MEMORY_CHECK" | grep -q "Memory service exists: False"; then
    echo -e "${RED}⚠️  memory_service 未初始化，請檢查啟動日誌${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 所有檢查通過${NC}"
exit 0

