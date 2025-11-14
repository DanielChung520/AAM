#!/bin/bash

# @purpose: AAM Admin 服务状态检查脚本
# @author: Daniel Chung
# @createdAt: 2025-01-14
# @lastModified: 2025-01-14
# @usage: ./scripts/status-service.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 端口定义
BACKEND_PORT=8003
FRONTEND_PORT=3000
DB_PORT=5433

# 函数：检查端口状态
check_port_status() {
    local port=$1
    local service_name=$2
    local url=$3
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        local pid=$(lsof -ti:$port)
        echo -e "${GREEN}✓${NC} $service_name: 运行中 (PID: $pid, Port: $port)"
        if [ -n "$url" ]; then
            if curl -s "$url" >/dev/null 2>&1; then
                echo -e "   ${GREEN}  → 健康检查: 通过${NC}"
            else
                echo -e "   ${YELLOW}  → 健康检查: 失败${NC}"
            fi
        fi
        return 0
    else
        echo -e "${RED}✗${NC} $service_name: 未运行 (Port: $port)"
        return 1
    fi
}

# 函数：检查 Docker 容器状态
check_docker_status() {
    local container_name=$1
    local service_name=$2
    
    if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        local status=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null)
        echo -e "${GREEN}✓${NC} $service_name: 运行中 (Container: $container_name, Status: $status)"
        return 0
    elif docker ps -a --format '{{.Names}}' | grep -q "^${container_name}$"; then
        echo -e "${YELLOW}⚠${NC} $service_name: 已停止 (Container: $container_name)"
        return 1
    else
        echo -e "${RED}✗${NC} $service_name: 不存在 (Container: $container_name)"
        return 1
    fi
}

# 主函数
main() {
    echo "📊 AAM Admin 服务状态"
    echo "===================="
    echo ""
    
    # 检查数据库
    echo "🗄️  数据库服务:"
    check_docker_status "admin-db-dev" "Admin Database"
    echo ""
    
    # 检查后端
    echo "🔧 后端服务:"
    check_port_status $BACKEND_PORT "Admin Backend" "http://localhost:$BACKEND_PORT/health"
    echo ""
    
    # 检查前端
    echo "🎨 前端服务:"
    check_port_status $FRONTEND_PORT "Admin Frontend" "http://localhost:$FRONTEND_PORT"
    echo ""
    
    # 访问地址
    echo "🌐 访问地址:"
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "   - 后端 API: http://localhost:$BACKEND_PORT"
        echo "   - API 文档: http://localhost:$BACKEND_PORT/docs"
    fi
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "   - 前端界面: http://localhost:$FRONTEND_PORT"
    fi
    echo ""
}

# 执行主函数
main "$@"

