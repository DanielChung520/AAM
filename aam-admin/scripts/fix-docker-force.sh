#!/bin/bash

# @purpose: Docker Desktop 强制修复脚本（会重启 Docker，影响所有容器）
# @author: Daniel Chung
# @createdAt: 2025-01-14
# @lastModified: 2025-01-14
# @usage: ./scripts/fix-docker-force.sh
# @warning: 此脚本会重启 Docker Desktop，停止所有容器

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

echo "🔧 Docker Desktop 强制修复工具"
echo "=============================="
echo ""
warning "⚠️  警告: 此脚本会重启 Docker Desktop，停止所有容器！"
echo ""

# 检查正在运行的容器
info "检查正在运行的容器..."
RUNNING_CONTAINERS=$(docker ps -q 2>/dev/null | wc -l | tr -d ' ' || echo "0")
if [ "$RUNNING_CONTAINERS" -gt 0 ] && [ "$RUNNING_CONTAINERS" != "0" ]; then
    error "发现 $RUNNING_CONTAINERS 个正在运行的容器"
    echo "   这些容器将被停止:"
    docker ps --format "   - {{.Names}} ({{.Image}})" 2>/dev/null
    echo ""
    read -p "确认要继续吗？这将停止所有容器！(yes/N): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        info "操作已取消"
        exit 0
    fi
else
    info "没有正在运行的容器"
fi
echo ""

# 步骤 1: 停止 Docker Desktop
info "步骤 1: 停止 Docker Desktop..."
if pgrep -f "Docker Desktop" >/dev/null 2>&1; then
    killall "Docker Desktop" 2>/dev/null || true
    sleep 3
    success "Docker Desktop 已停止"
else
    info "Docker Desktop 未运行"
fi
echo ""

# 步骤 2: 清理 socket 文件
info "步骤 2: 清理 Docker socket 文件..."
if [ -S ~/Library/Containers/com.docker.docker/Data/backend.sock ]; then
    rm -f ~/Library/Containers/com.docker.docker/Data/backend.sock
    success "已删除 backend.sock"
fi

if [ -d ~/.docker/run ]; then
    rm -rf ~/.docker/run/*
    success "已清理 Docker run 目录"
fi
echo ""

# 步骤 3: 重新启动 Docker Desktop
info "步骤 3: 重新启动 Docker Desktop..."
open -a Docker
success "Docker Desktop 启动命令已执行"
echo ""

# 步骤 4: 等待并验证
info "步骤 4: 等待 Docker 启动（这可能需要 60-90 秒）..."
echo "   请观察菜单栏的 Docker 图标，等待它不再动画"
echo ""

max_attempts=90
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker info >/dev/null 2>&1; then
        success "Docker daemon 已就绪！"
        echo ""
        echo "Docker 信息:"
        docker version --format '{{.Server.Version}}' 2>/dev/null | sed 's/^/   Server: /'
        docker version --format '{{.Client.Version}}' 2>/dev/null | sed 's/^/   Client: /'
        exit 0
    fi
    if [ $((attempt % 10)) -eq 0 ] && [ $attempt -gt 0 ]; then
        info "仍在等待... (${attempt}/${max_attempts} 秒)"
    fi
    attempt=$((attempt + 1))
    sleep 1
done

error "Docker daemon 启动超时"
warning "请手动检查 Docker Desktop 状态"
echo ""

