#!/bin/bash

# @purpose: 统一启动所有服务（aam-service 和 aam-admin）
# @author: Daniel Chung
# @createdAt: 2025-01-14
# @lastModified: 2025-01-14
# @usage: ./scripts/start-all-services.sh [aam-service|aam-admin|all]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 函数：检查 Docker
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        error "Docker daemon 无法连接"
        warning "请确保 Docker Desktop 正在运行"
        return 1
    fi
    return 0
}

# 函数：停止所有服务（清理）
cleanup_all() {
    info "清理所有服务..."
    
    # 停止 aam-service
    if [ -f "aam-service/docker-compose.dev.yml" ]; then
        cd aam-service
        docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
        cd ..
    fi
    
    # 停止 aam-admin
    if [ -f "aam-admin/docker-compose.dev.yml" ]; then
        cd aam-admin
        docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
        cd ..
    fi
    
    success "清理完成"
}

# 函数：启动 aam-service
start_aam_service() {
    info "启动 aam-service..."
    
    if [ ! -f "aam-service/docker-compose.dev.yml" ]; then
        error "aam-service/docker-compose.dev.yml 不存在"
        return 1
    fi
    
    cd aam-service
    
    # 检查是否已在运行
    if docker-compose -f docker-compose.dev.yml ps 2>/dev/null | grep -q "Up"; then
        warning "aam-service 已在运行中"
        cd ..
        return 0
    fi
    
    # 启动服务
    info "启动 aam-service 容器..."
    if docker-compose -f docker-compose.dev.yml up -d; then
        success "aam-service 启动成功"
        
        # 等待服务就绪
        info "等待 aam-service 就绪..."
        sleep 10
        
        # 检查服务状态
        if docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
            success "aam-service 运行正常"
        else
            warning "aam-service 可能未完全启动，请检查日志"
        fi
    else
        error "aam-service 启动失败"
        cd ..
        return 1
    fi
    
    cd ..
    return 0
}

# 函数：启动 aam-admin
start_aam_admin() {
    info "启动 aam-admin..."
    
    if [ ! -f "aam-admin/docker-compose.dev.yml" ]; then
        error "aam-admin/docker-compose.dev.yml 不存在"
        return 1
    fi
    
    cd aam-admin
    
    # 检查是否已在运行
    if docker-compose -f docker-compose.dev.yml ps 2>/dev/null | grep -q "Up"; then
        warning "aam-admin 已在运行中"
        cd ..
        return 0
    fi
    
    # 启动服务
    info "启动 aam-admin 容器..."
    if docker-compose -f docker-compose.dev.yml up -d; then
        success "aam-admin 启动成功"
        
        # 等待服务就绪
        info "等待 aam-admin 就绪..."
        sleep 10
        
        # 检查服务状态
        if docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
            success "aam-admin 运行正常"
        else
            warning "aam-admin 可能未完全启动，请检查日志"
        fi
    else
        error "aam-admin 启动失败"
        cd ..
        return 1
    fi
    
    cd ..
    return 0
}

# 函数：显示服务状态
show_status() {
    echo ""
    echo "📊 服务状态"
    echo "=========="
    
    # aam-service 状态
    if [ -f "aam-service/docker-compose.dev.yml" ]; then
        echo ""
        echo "aam-service:"
        cd aam-service
        docker-compose -f docker-compose.dev.yml ps 2>/dev/null || echo "  未运行"
        cd ..
    fi
    
    # aam-admin 状态
    if [ -f "aam-admin/docker-compose.dev.yml" ]; then
        echo ""
        echo "aam-admin:"
        cd aam-admin
        docker-compose -f docker-compose.dev.yml ps 2>/dev/null || echo "  未运行"
        cd ..
    fi
    
    echo ""
    echo "🌐 访问地址"
    echo "=========="
    echo "  - AAM Service:      http://localhost:8000"
    echo "  - AAM Service API:   http://localhost:8000/docs"
    echo "  - Admin Backend:     http://localhost:8003"
    echo "  - Admin Backend API: http://localhost:8003/docs"
    echo "  - ChromaDB:          http://localhost:8001"
    echo "  - RabbitMQ:          http://localhost:15672 (admin/admin)"
    echo ""
}

# 主函数
main() {
    local command=${1:-all}
    
    echo "🚀 AAM 系统服务启动脚本"
    echo "========================"
    echo ""
    
    # 检查 Docker
    if ! check_docker; then
        exit 1
    fi
    
    # 根据命令执行
    case $command in
        aam-service)
            start_aam_service
            ;;
        aam-admin)
            # 先确保 aam-service 运行
            if ! docker ps --format "{{.Names}}" | grep -q "aam-service-dev"; then
                warning "aam-service 未运行，先启动 aam-service..."
                if ! start_aam_service; then
                    error "无法启动 aam-service，aam-admin 需要 aam-service"
                    exit 1
                fi
                # 等待 aam-service 完全就绪
                info "等待 aam-service 完全就绪..."
                sleep 15
            fi
            start_aam_admin
            ;;
        all)
            # 先清理（可选）
            read -p "是否先清理所有服务？(y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                cleanup_all
                sleep 5
            fi
            
            # 启动 aam-service
            if ! start_aam_service; then
                error "aam-service 启动失败，无法继续"
                exit 1
            fi
            
            # 等待 aam-service 完全就绪
            info "等待 aam-service 完全就绪..."
            sleep 15
            
            # 启动 aam-admin
            if ! start_aam_admin; then
                error "aam-admin 启动失败"
                exit 1
            fi
            
            success "所有服务启动完成！"
            ;;
        cleanup)
            cleanup_all
            exit 0
            ;;
        *)
            echo "用法: $0 [aam-service|aam-admin|all|cleanup]"
            echo ""
            echo "选项:"
            echo "  aam-service  - 仅启动 aam-service"
            echo "  aam-admin    - 仅启动 aam-admin（需要 aam-service 运行）"
            echo "  all          - 启动所有服务（推荐）"
            echo "  cleanup      - 清理所有服务"
            exit 1
            ;;
    esac
    
    # 显示状态
    show_status
}

# 执行主函数
main "$@"

