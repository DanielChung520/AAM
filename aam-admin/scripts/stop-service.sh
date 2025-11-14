#!/bin/bash

# @purpose: AAM Admin 服务停止脚本
# @author: Daniel Chung
# @createdAt: 2025-01-14
# @lastModified: 2025-01-14
# @usage: ./scripts/stop-service.sh [all|backend|frontend]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 端口定义
BACKEND_PORT=8003
FRONTEND_PORT=3000
DB_PORT=5433

# 函数：打印信息
info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

# 函数：停止端口服务
stop_port_service() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        local pid=$(lsof -ti:$port)
        info "停止 $service_name 服务 (PID: $pid, Port: $port)..."
        kill -9 $pid 2>/dev/null || true
        sleep 1
        if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            success "$service_name 服务已停止"
        fi
    else
        info "$service_name 服务未运行"
    fi
}

# 函数：停止 Docker 容器
stop_docker_service() {
    local service_name=$1
    local container_name=$2
    
    if docker ps -a --format '{{.Names}}' | grep -q "^${container_name}$"; then
        if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
            info "停止 Docker 容器: $container_name"
            docker stop "$container_name" >/dev/null 2>&1 || true
            success "Docker 容器 $container_name 已停止"
        else
            info "Docker 容器 $container_name 未运行"
        fi
    else
        info "Docker 容器 $container_name 不存在"
    fi
}

# 函数：停止后端服务
stop_backend() {
    info "停止后端服务..."
    stop_port_service $BACKEND_PORT "Admin Backend"
    stop_docker_service "admin-backend" "admin-backend-dev"
    
    # 清理 PID 文件
    if [ -f /tmp/admin-backend.pid ]; then
        rm -f /tmp/admin-backend.pid
    fi
}

# 函数：停止前端服务
stop_frontend() {
    info "停止前端服务..."
    stop_port_service $FRONTEND_PORT "Admin Frontend"
    
    # 清理 PID 文件
    if [ -f /tmp/admin-frontend.pid ]; then
        rm -f /tmp/admin-frontend.pid
    fi
}

# 函数：停止数据库服务
stop_database() {
    info "停止数据库服务..."
    stop_docker_service "admin-db" "admin-db-dev"
}

# 函数：停止所有服务
stop_all() {
    info "停止所有服务..."
    stop_backend
    stop_frontend
    stop_database
    success "所有服务已停止"
}

# 主函数
main() {
    local command=${1:-all}
    
    case $command in
        all)
            stop_all
            ;;
        backend)
            stop_backend
            ;;
        frontend)
            stop_frontend
            ;;
        database|db)
            stop_database
            ;;
        *)
            echo "用法: $0 [all|backend|frontend|database]"
            echo ""
            echo "选项:"
            echo "  all        - 停止所有服务"
            echo "  backend    - 仅停止后端服务"
            echo "  frontend   - 仅停止前端服务"
            echo "  database   - 仅停止数据库服务"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"

