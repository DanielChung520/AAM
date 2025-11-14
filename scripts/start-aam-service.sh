#!/bin/bash

# @purpose: 启动 AAM Service 服务
# @author: Daniel Chung
# @createdAt: 2025-01-14
# @lastModified: 2025-01-14
# @usage: ./scripts/start-aam-service.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

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

# 函数：检查 Docker 是否运行
check_docker() {
    # 检查 Docker Desktop 应用是否在运行
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
    
    # 检查 Docker daemon 是否就绪（最多等待 90 秒）
    info "等待 Docker daemon 启动（这可能需要 30-90 秒）..."
    local max_attempts=90
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker info >/dev/null 2>&1; then
            success "Docker daemon 已就绪"
            return 0
        fi
        # 每 10 秒显示一次进度
        if [ $((attempt % 10)) -eq 0 ] && [ $attempt -gt 0 ]; then
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
    echo "  3. 使用修复脚本: cd aam-admin && ./scripts/fix-docker.sh"
    echo "  4. 检查系统资源（内存、CPU）是否充足"
    echo ""
    return 1
}

# 主函数
main() {
    echo "🚀 启动 AAM Service"
    echo "=================="
    echo ""
    
    # 检查 Docker
    if ! check_docker; then
        error "无法启动 AAM Service：Docker daemon 未就绪"
        exit 1
    fi
    
    # 检查 aam-service 目录
    if [ ! -d "aam-service" ]; then
        error "aam-service 目录不存在"
        exit 1
    fi
    
    # 启动 aam-service
    info "启动 AAM Service..."
    cd aam-service
    
    if [ -f "scripts/start-dev.sh" ]; then
        ./scripts/start-dev.sh
    else
        error "启动脚本不存在: aam-service/scripts/start-dev.sh"
        exit 1
    fi
}

# 执行主函数
main "$@"

