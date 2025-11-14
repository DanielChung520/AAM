#!/bin/bash

# @purpose: AAM Admin 服务启动脚本
# @author: Daniel Chung
# @createdAt: 2025-01-14
# @lastModified: 2025-01-14
# @usage: ./scripts/start-service.sh [all|backend|frontend]

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

error() {
    echo -e "${RED}✗ ${1}${NC}"
}

# 函数：检查端口是否被占用
check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        local pid=$(lsof -ti:$port)
        warning "$service_name 服务正在运行 (PID: $pid, Port: $port)"
        return 0
    else
        info "$service_name 服务未运行 (Port: $port)"
        return 1
    fi
}

# 函数：停止服务
stop_service() {
    local port=$1
    local service_name=$2
    
    if check_port $port "$service_name"; then
        info "正在停止 $service_name 服务..."
        local pid=$(lsof -ti:$port)
        if [ -n "$pid" ]; then
            kill -9 $pid 2>/dev/null || true
            sleep 1
            if ! check_port $port "$service_name"; then
                success "$service_name 服务已停止"
            else
                error "无法停止 $service_name 服务"
                return 1
            fi
        fi
    fi
}

# 函数：停止 Docker 容器
stop_docker_service() {
    local service_name=$1
    local container_name=$2
    
    if docker ps -a --format '{{.Names}}' | grep -q "^${container_name}$"; then
        if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
            info "正在停止 Docker 容器: $container_name"
            docker stop "$container_name" >/dev/null 2>&1 || true
            success "Docker 容器 $container_name 已停止"
        fi
    fi
}

# 函数：检查 Docker 是否运行
check_docker() {
    # 首先检查 Docker Desktop 应用是否在运行
    if ! pgrep -f "Docker Desktop" >/dev/null 2>&1; then
        error "Docker Desktop 应用未运行"
        warning "请启动 Docker Desktop，然后再次运行此脚本"
        warning "启动命令: open -a Docker"
        return 1
    fi
    
    # 确保使用正确的 Docker context
    if docker context show 2>/dev/null | grep -q "desktop-linux"; then
        docker context use desktop-linux >/dev/null 2>&1
    fi
    
    # 检查 Docker daemon 是否就绪（最多等待 60 秒，因为有时需要更长时间）
    info "等待 Docker daemon 启动（这可能需要 30-60 秒）..."
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker info >/dev/null 2>&1; then
            success "Docker daemon 已就绪"
            return 0
        fi
        # 每 5 秒显示一次进度
        if [ $((attempt % 5)) -eq 0 ] && [ $attempt -gt 0 ]; then
            info "仍在等待 Docker daemon... (${attempt}/${max_attempts} 秒)"
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    error "Docker daemon 启动超时（等待了 ${max_attempts} 秒）"
    warning "Docker Desktop 应用正在运行，但 daemon 未就绪"
    echo ""
    echo "请尝试以下步骤："
    echo "  1. 打开 Docker Desktop 应用，查看是否有错误提示"
    echo "  2. 在 Docker Desktop 中点击 'Troubleshoot' → 'Restart'"
    echo "  3. 完全退出 Docker Desktop 并重新启动"
    echo "  4. 检查系统资源（内存、CPU）是否充足"
    echo ""
    return 1
}

# 函数：启动数据库
start_database() {
    info "检查数据库服务..."
    
    # 检查 Docker 是否运行
    if ! check_docker; then
        return 1
    fi
    
    if check_port $DB_PORT "Admin Database"; then
        # 检查是否是 Docker 容器
        if docker ps --format '{{.Names}}' | grep -q "^admin-db-dev$"; then
            success "数据库服务已在运行 (Docker)"
        else
            warning "端口 $DB_PORT 被占用，但不是 Docker 容器"
            warning "请检查是否有其他 PostgreSQL 服务在运行"
            return 1
        fi
    else
        info "启动数据库服务..."
        docker-compose -f docker-compose.dev.yml up admin-db -d
        
        # 等待数据库就绪
        info "等待数据库就绪..."
        local max_attempts=30
        local attempt=0
        while [ $attempt -lt $max_attempts ]; do
            if docker exec admin-db-dev pg_isready -U admin -d aam_admin >/dev/null 2>&1; then
                success "数据库服务已就绪"
                return 0
            fi
            attempt=$((attempt + 1))
            sleep 1
        done
        error "数据库服务启动超时"
        return 1
    fi
}

# 函数：启动后端服务
start_backend() {
    local use_docker=${1:-false}
    
    info "启动后端服务..."
    
    if [ "$use_docker" = "true" ]; then
        # Docker 模式 - 检查 Docker 是否运行
        if ! check_docker; then
            return 1
        fi
    fi
    
    # 停止旧服务
    stop_service $BACKEND_PORT "Admin Backend"
    if [ "$use_docker" = "true" ]; then
        stop_docker_service "admin-backend" "admin-backend-dev"
    fi
    
    # 检查数据库
    if ! start_database; then
        error "数据库服务未就绪，无法启动后端"
        return 1
    fi
    
    if [ "$use_docker" = "true" ]; then
        # Docker 模式
        info "使用 Docker 模式启动后端服务..."
        docker-compose -f docker-compose.dev.yml up admin-backend -d
        
        # 等待服务启动
        sleep 5
        
        # 检查服务是否启动成功
        local max_attempts=15
        local attempt=0
        while [ $attempt -lt $max_attempts ]; do
            if curl -s http://localhost:$BACKEND_PORT/health >/dev/null 2>&1; then
                success "后端服务已启动 (Docker, http://localhost:$BACKEND_PORT)"
                success "API 文档: http://localhost:$BACKEND_PORT/docs"
                return 0
            fi
            attempt=$((attempt + 1))
            sleep 1
        done
        
        error "后端服务启动失败，查看日志: docker-compose -f docker-compose.dev.yml logs admin-backend"
        return 1
    else
        # 本地模式
        # 检查虚拟环境
        if [ ! -d "backend/venv" ]; then
            warning "虚拟环境不存在，请先创建: python -m venv backend/venv"
            return 1
        fi
        
        info "使用本地模式启动后端服务 (端口: $BACKEND_PORT)..."
        
        # 在后台启动后端服务
        (
            cd backend
            source venv/bin/activate
            uvicorn src.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > /tmp/admin-backend.log 2>&1 &
            echo $! > /tmp/admin-backend.pid
        )
        
        # 等待服务启动
        sleep 3
        
        # 检查服务是否启动成功
        local max_attempts=10
        local attempt=0
        while [ $attempt -lt $max_attempts ]; do
            if curl -s http://localhost:$BACKEND_PORT/health >/dev/null 2>&1; then
                success "后端服务已启动 (本地, http://localhost:$BACKEND_PORT)"
                success "API 文档: http://localhost:$BACKEND_PORT/docs"
                return 0
            fi
            attempt=$((attempt + 1))
            sleep 1
        done
        
        error "后端服务启动失败，请查看日志: /tmp/admin-backend.log"
        return 1
    fi
}

# 函数：启动前端服务
start_frontend() {
    info "启动前端服务..."
    
    # 停止旧服务
    stop_service $FRONTEND_PORT "Admin Frontend"
    
    # 检查 node_modules 和 vite
    if [ ! -d "frontend/node_modules" ] || [ ! -f "frontend/node_modules/.bin/vite" ]; then
        warning "依赖未安装或 vite 未找到，正在安装..."
        cd frontend
        npm install
        cd ..
    fi
    
    info "启动前端服务 (端口: $FRONTEND_PORT)..."
    
    # 在后台启动前端服务
    (
        cd frontend
        npx vite > /tmp/admin-frontend.log 2>&1 &
        echo $! > /tmp/admin-frontend.pid
    )
    
    # 等待服务启动（Vite 需要更长时间）
    sleep 8
    
    # 检查服务是否启动成功
    local max_attempts=20
    local attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:$FRONTEND_PORT >/dev/null 2>&1; then
            success "前端服务已启动 (http://localhost:$FRONTEND_PORT)"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    # 检查进程是否在运行
    if [ -f /tmp/admin-frontend.pid ] && ps -p $(cat /tmp/admin-frontend.pid 2>/dev/null) > /dev/null 2>&1; then
        warning "前端服务可能正在启动中，请稍后访问: http://localhost:$FRONTEND_PORT"
        warning "查看日志: tail -f /tmp/admin-frontend.log"
        return 0
    else
        error "前端服务启动失败，请查看日志: /tmp/admin-frontend.log"
        return 1
    fi
}

# 函数：启动所有服务
start_all() {
    local use_docker=${1:-true}  # 默认使用 Docker 模式
    info "启动所有服务..."
    
    # 启动数据库
    if ! start_database; then
        error "数据库启动失败"
        return 1
    fi
    
    # 启动后端
    if ! start_backend "$use_docker"; then
        error "后端启动失败"
        return 1
    fi
    
    # 启动前端（Docker 模式下，前端也使用本地模式以保持热重载速度）
    if [ "$use_docker" = "true" ]; then
        info "前端服务建议使用本地模式以保持热重载速度"
        info "如需启动前端，请运行: ./scripts/start-service.sh frontend"
    else
        if ! start_frontend; then
            error "前端启动失败"
            return 1
        fi
    fi
    
    success "所有服务已启动！"
    echo ""
    echo "访问地址:"
    if [ "$use_docker" = "true" ]; then
        echo "  - 后端 API: http://localhost:$BACKEND_PORT (Docker)"
        echo "  - API 文档: http://localhost:$BACKEND_PORT/docs"
        echo "  - 前端: http://localhost:$FRONTEND_PORT (如需启动，运行: ./scripts/start-service.sh frontend)"
        echo ""
        echo "查看日志:"
        echo "  - 后端: docker-compose -f docker-compose.dev.yml logs -f admin-backend"
        echo "  - 数据库: docker-compose -f docker-compose.dev.yml logs -f admin-db"
    else
        echo "  - 前端: http://localhost:$FRONTEND_PORT"
        echo "  - 后端 API: http://localhost:$BACKEND_PORT"
        echo "  - API 文档: http://localhost:$BACKEND_PORT/docs"
        echo ""
        echo "日志文件:"
        echo "  - 后端: /tmp/admin-backend.log"
        echo "  - 前端: /tmp/admin-frontend.log"
    fi
}

# 主函数
main() {
    local command=${1:-all}
    local use_docker=true  # 默认使用 Docker 模式
    
    # 检查是否使用本地模式
    if [ "$command" = "local" ] || [ "$command" = "--local" ]; then
        use_docker=false
        command="all"
    elif [ "$2" = "--local" ] || [ "$2" = "local" ]; then
        use_docker=false
    fi
    
    case $command in
        all)
            start_all "$use_docker"
            ;;
        backend)
            start_backend "$use_docker"
            ;;
        frontend)
            start_frontend
            ;;
        docker|--docker)
            # Docker 模式启动所有服务
            start_all "true"
            ;;
        *)
            echo "用法: $0 [all|backend|frontend] [--local]"
            echo ""
            echo "选项:"
            echo "  all           - 启动所有服务（默认 Docker 模式）"
            echo "  backend       - 仅启动后端服务（默认 Docker 模式）"
            echo "  frontend      - 仅启动前端服务（本地模式）"
            echo ""
            echo "模式选项:"
            echo "  --local       - 使用本地模式（后端使用本地 Python 环境）"
            echo ""
            echo "示例:"
            echo "  $0 all              # Docker 模式启动所有服务（默认）"
            echo "  $0 all --local      # 本地模式启动所有服务"
            echo "  $0 backend          # Docker 模式启动后端（默认）"
            echo "  $0 backend --local  # 本地模式启动后端"
            echo "  $0 frontend         # 启动前端（本地模式）"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"

