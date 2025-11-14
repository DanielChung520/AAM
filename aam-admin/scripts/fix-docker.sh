#!/bin/bash

# @purpose: Docker Desktop 修复脚本
# @author: Daniel Chung
# @createdAt: 2025-01-14
# @lastModified: 2025-01-14
# @usage: ./scripts/fix-docker.sh

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

echo "🔧 Docker Desktop 修复工具（温和模式）"
echo "====================================="
echo ""

# 步骤 1: 检查正在运行的容器
info "步骤 1: 检查正在运行的 Docker 容器..."
RUNNING_CONTAINERS=$(docker ps -q 2>/dev/null | wc -l | tr -d ' ' || echo "0")
if [ "$RUNNING_CONTAINERS" -gt 0 ] && [ "$RUNNING_CONTAINERS" != "0" ]; then
    warning "发现 $RUNNING_CONTAINERS 个正在运行的容器"
    echo "   正在运行的容器列表:"
    docker ps --format "   - {{.Names}} ({{.Image}})" 2>/dev/null | head -5
    echo ""
    echo "⚠️  注意: 此修复不会停止这些容器，只会修复 Docker 连接问题"
    echo ""
    read -p "是否继续？(Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        info "操作已取消"
        exit 0
    fi
else
    info "没有正在运行的容器"
fi
echo ""

# 步骤 2: 检查 Docker daemon 状态
info "步骤 2: 检查 Docker daemon 状态..."
if docker info >/dev/null 2>&1; then
    success "Docker daemon 可以连接，无需修复"
    echo ""
    echo "Docker 状态:"
    docker version --format '{{.Server.Version}}' 2>/dev/null | sed 's/^/   Server: /'
    docker version --format '{{.Client.Version}}' 2>/dev/null | sed 's/^/   Client: /'
    exit 0
else
    warning "Docker daemon 无法连接，需要修复"
fi
echo ""

# 步骤 3: 清理损坏的 socket 文件（不重启 Docker）
info "步骤 3: 清理损坏的 socket 文件..."
if [ -S ~/Library/Containers/com.docker.docker/Data/backend.sock ]; then
    # 检查 socket 是否真的无法连接
    if ! docker info >/dev/null 2>&1; then
        rm -f ~/Library/Containers/com.docker.docker/Data/backend.sock
        success "已删除损坏的 backend.sock"
    else
        info "backend.sock 正常，无需删除"
    fi
else
    info "backend.sock 不存在"
fi

# 只清理明显损坏的文件，不清理整个 run 目录
if [ -d ~/.docker/run ]; then
    # 只清理明显有问题的文件
    if [ -S ~/.docker/run/docker.sock ] && ! docker info >/dev/null 2>&1; then
        rm -f ~/.docker/run/docker.sock
        success "已清理损坏的 docker.sock"
    else
        info "Docker socket 正常"
    fi
fi
echo ""

# 步骤 4: 尝试重新连接（不重启 Docker Desktop）
info "步骤 4: 尝试重新连接 Docker daemon..."
echo "   等待 Docker daemon 自动恢复连接（不会影响正在运行的容器）..."
echo ""

max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker info >/dev/null 2>&1; then
        success "Docker daemon 已恢复连接！"
        echo ""
        echo "Docker 信息:"
        docker version --format '{{.Server.Version}}' 2>/dev/null | sed 's/^/   Server: /'
        docker version --format '{{.Client.Version}}' 2>/dev/null | sed 's/^/   Client: /'
        echo ""
        echo "正在运行的容器（未受影响）:"
        docker ps --format "   - {{.Names}} ({{.Status}})" 2>/dev/null | head -5
        exit 0
    fi
    if [ $((attempt % 5)) -eq 0 ] && [ $attempt -gt 0 ]; then
        info "仍在等待连接恢复... (${attempt}/${max_attempts} 秒)"
    fi
    attempt=$((attempt + 1))
    sleep 1
done

error "Docker daemon 连接恢复超时（等待了 ${max_attempts} 秒）"
warning "温和修复失败，可能需要重启 Docker Desktop"
echo ""
echo "如果仍然失败，请尝试："
echo "  1. 打开 Docker Desktop，查看错误信息"
echo "  2. 在 Docker Desktop 中：Settings → Troubleshoot → Restart"
echo "  3. 使用强制修复脚本: ./scripts/fix-docker-force.sh（会停止所有容器）"
echo "  4. 检查系统资源（内存、CPU）"
echo ""
echo "⚠️  注意: 如果使用强制修复，会停止所有容器，包括 aam-service"
echo ""

