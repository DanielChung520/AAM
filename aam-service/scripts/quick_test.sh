#!/bin/bash
# @purpose: 快速測試 AAM 服務的 API 端點，包括健康檢查和 MCP Enrich 端點
# @author: Daniel Chung + AI
# @createdAt: 2025-11-12
# @lastModified: 2025-11-12
# @usage: ./scripts/quick_test.sh

set -e

# 顏色定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
API_BASE_URL="http://localhost:8000"
ENV_FILE=".env"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AAM Service API 快速測試${NC}"
echo -e "${BLUE}========================================${NC}\n"

# ============================================
# 1. 檢查 Docker 環境
# ============================================
echo -e "${YELLOW}🔍 步驟 1: 檢查 Docker 環境...${NC}"

# 1.1 檢查 Docker 是否安裝
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安裝${NC}"
    echo -e "${YELLOW}   請安裝 Docker Desktop: https://www.docker.com/products/docker-desktop${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker 已安裝: $(docker --version)${NC}"

# 1.2 檢查 Docker daemon 是否運行
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker daemon 未運行${NC}"
    echo -e "${YELLOW}   正在嘗試啟動 Docker Desktop...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open -a Docker 2>/dev/null || true
    fi
    echo -e "${YELLOW}   請等待 Docker Desktop 完全啟動（通常需要 30-60 秒）...${NC}"
    echo -e "${YELLOW}   然後再次運行此腳本${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker daemon 正在運行${NC}"

# 1.3 檢查 Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose 未安裝${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose 可用${NC}\n"

# 1.4 檢查是否在 Docker 環境中（檢查 aam-service 容器）
echo -e "${YELLOW}🔍 步驟 2: 檢查 AAM 服務容器狀態...${NC}"
cd "$PROJECT_DIR"

# 定義 Docker Compose 文件（開發環境）
COMPOSE_FILE="docker-compose.dev.yml"

# 檢查容器是否存在並獲取狀態（支持開發環境容器名稱 aam-service-dev）
CONTAINER_EXISTS=$(docker-compose -f "$COMPOSE_FILE" ps 2>/dev/null | grep -E "aam-service|aam-service-dev" | wc -l | tr -d ' ')
CONTAINER_STATUS=$(docker-compose -f "$COMPOSE_FILE" ps 2>/dev/null | grep -E "aam-service|aam-service-dev" | awk '{for(i=6;i<=NF;i++) printf "%s ", $i; print ""}' | xargs || echo "")

if [ "$CONTAINER_EXISTS" -gt 0 ]; then
    # 檢查容器是否正在運行（包含 Up 或 healthy）
    if echo "$CONTAINER_STATUS" | grep -qE "Up|healthy|running"; then
        echo -e "${GREEN}✅ AAM 服務容器正在運行${NC}"
        IN_DOCKER=true
    else
        echo -e "${YELLOW}⚠️  AAM 服務容器存在但未運行${NC}"
        echo -e "${BLUE}   正在啟動容器...${NC}"
        docker-compose -f "$COMPOSE_FILE" up -d aam-service
        sleep 5
        IN_DOCKER=true
    fi
else
    echo -e "${YELLOW}⚠️  未發現 AAM 服務容器${NC}"
    echo -e "${BLUE}   正在啟動 Docker 開發環境...${NC}"
    docker-compose -f "$COMPOSE_FILE" up -d
    sleep 10
    IN_DOCKER=true
fi

# 顯示容器狀態
echo ""
echo -e "${BLUE}容器狀態:${NC}"
docker-compose -f "$COMPOSE_FILE" ps | grep -E "(NAME|aam-service|chromadb|postgres|rabbitmq|redis)" || docker-compose -f "$COMPOSE_FILE" ps
echo ""

# ============================================
# 2. 檢查服務是否可訪問
# ============================================
echo -e "${YELLOW}🔍 步驟 3: 檢查服務可訪問性...${NC}"
MAX_RETRIES=5
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s "${API_BASE_URL}/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 服務可訪問: ${API_BASE_URL}${NC}\n"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo -e "${YELLOW}⏳ 等待服務啟動... (${RETRY_COUNT}/${MAX_RETRIES})${NC}"
            sleep 3
        else
            echo -e "${RED}❌ 錯誤: 服務未運行或無法訪問 ${API_BASE_URL}${NC}"
            if [ "$IN_DOCKER" = true ]; then
                echo -e "${YELLOW}💡 提示:${NC}"
                echo -e "   1. 檢查容器日誌: ${BLUE}docker-compose -f docker-compose.dev.yml logs aam-service${NC}"
                echo -e "   2. 檢查容器狀態: ${BLUE}docker-compose -f docker-compose.dev.yml ps${NC}"
                echo -e "   3. 重啟服務: ${BLUE}docker-compose -f docker-compose.dev.yml restart aam-service${NC}"
            else
                echo -e "${YELLOW}💡 提示: 請先啟動服務${NC}"
                echo -e "   Docker 開發環境: ${BLUE}docker-compose -f docker-compose.dev.yml up -d${NC}"
                echo -e "   本地環境: ${BLUE}python3 -m uvicorn src.main:app --reload --port 8000${NC}"
            fi
            exit 1
        fi
    fi
done

# 讀取 API_KEY
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ 錯誤: 找不到 .env 文件${NC}"
    exit 1
fi

API_KEY=$(grep "^API_KEY=" "$ENV_FILE" | cut -d '=' -f2 | tr -d '"' | tr -d "'")
if [ -z "$API_KEY" ]; then
    echo -e "${RED}❌ 錯誤: 在 .env 文件中找不到 API_KEY${NC}"
    exit 1
fi

echo -e "${BLUE}使用 API_KEY: ${API_KEY:0:10}...${NC}\n"

# 測試函數
test_endpoint() {
    local test_name=$1
    local method=$2
    local endpoint=$3
    local headers=$4
    local data=$5
    local expected_status=$6
    
    echo -e "${YELLOW}=== 測試: ${test_name} ===${NC}"
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "${API_BASE_URL}${endpoint}" $headers)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "${API_BASE_URL}${endpoint}" $headers -d "$data" -H "Content-Type: application/json")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ 狀態碼: ${http_code} (預期: ${expected_status})${NC}"
        if command -v python3 &> /dev/null && command -v json.tool &> /dev/null; then
            echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
        else
            echo "$body"
        fi
    else
        echo -e "${RED}❌ 狀態碼: ${http_code} (預期: ${expected_status})${NC}"
        echo "$body"
    fi
    echo ""
}

# 測試 1: 健康檢查
test_endpoint \
    "健康檢查端點" \
    "GET" \
    "/health" \
    "" \
    "" \
    "200"

# 測試 2: 就緒檢查
test_endpoint \
    "就緒檢查端點" \
    "GET" \
    "/ready" \
    "" \
    "" \
    "200"

# 測試 3: 根端點
test_endpoint \
    "根端點" \
    "GET" \
    "/" \
    "" \
    "" \
    "200"

# 測試 4: MCP Enrich - 成功場景
test_endpoint \
    "MCP Enrich - 成功場景" \
    "POST" \
    "/v1/mcp/enrich" \
    "-H \"X-API-KEY: ${API_KEY}\"" \
    '{
        "user_profile": {
            "user_id": "test-user-123"
        },
        "session_context": {
            "session_id": "test-session-123",
            "current_query": "What is Python?",
            "short_term_memory": []
        }
    }' \
    "200"

# 測試 5: MCP Enrich - 包含短期記憶
test_endpoint \
    "MCP Enrich - 包含短期記憶" \
    "POST" \
    "/v1/mcp/enrich" \
    "-H \"X-API-KEY: ${API_KEY}\"" \
    '{
        "user_profile": {
            "user_id": "test-user-123"
        },
        "session_context": {
            "session_id": "test-session-123",
            "current_query": "Tell me more",
            "short_term_memory": [
                {
                    "role": "user",
                    "content": "What is Python?"
                },
                {
                    "role": "assistant",
                    "content": "Python is a programming language."
                }
            ]
        }
    }' \
    "200"

# 測試 6: API Key 認證失敗
test_endpoint \
    "API Key 認證失敗" \
    "POST" \
    "/v1/mcp/enrich" \
    "-H \"X-API-KEY: wrong-api-key\"" \
    '{
        "user_profile": {
            "user_id": "test-user-123"
        },
        "session_context": {
            "session_id": "test-session-123",
            "current_query": "test",
            "short_term_memory": []
        }
    }' \
    "401"

# 測試 7: 缺少 API Key
test_endpoint \
    "缺少 API Key" \
    "POST" \
    "/v1/mcp/enrich" \
    "" \
    '{
        "user_profile": {
            "user_id": "test-user-123"
        },
        "session_context": {
            "session_id": "test-session-123",
            "current_query": "test",
            "short_term_memory": []
        }
    }' \
    "422"

# 測試 8: 無效請求體
test_endpoint \
    "無效請求體" \
    "POST" \
    "/v1/mcp/enrich" \
    "-H \"X-API-KEY: ${API_KEY}\"" \
    '{
        "invalid": "data"
    }' \
    "422"

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ 所有測試完成${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${YELLOW}💡 提示:${NC}"
echo -e "  - 訪問 Swagger UI: ${BLUE}http://localhost:8000/docs${NC}"
echo -e "  - 訪問 ReDoc: ${BLUE}http://localhost:8000/redoc${NC}"
echo ""

