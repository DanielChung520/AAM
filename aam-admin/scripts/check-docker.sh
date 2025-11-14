#!/bin/bash

# @purpose: Docker 状态诊断脚本
# @author: Daniel Chung
# @createdAt: 2025-01-14
# @lastModified: 2025-01-14
# @usage: ./scripts/check-docker.sh

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

echo "🔍 Docker 状态诊断"
echo "=================="
echo ""

# 1. 检查 Docker Desktop 应用
echo "1. 检查 Docker Desktop 应用..."
if pgrep -f "Docker Desktop" >/dev/null 2>&1; then
    success "Docker Desktop 应用正在运行"
    ps aux | grep -i "Docker Desktop" | grep -v grep | head -1 | awk '{print "   PID: " $2 " (" $11 ")"}'
else
    error "Docker Desktop 应用未运行"
    echo "   启动命令: open -a Docker"
fi
echo ""

# 2. 检查 Docker socket
echo "2. 检查 Docker socket..."
if [ -S ~/.docker/run/docker.sock ]; then
    success "Docker socket 存在"
    ls -lh ~/.docker/run/docker.sock | awk '{print "   权限: " $1 " 所有者: " $3 ":" $4}'
else
    error "Docker socket 不存在"
fi
echo ""

# 3. 检查 Docker context
echo "3. 检查 Docker context..."
if docker context ls >/dev/null 2>&1; then
    CURRENT_CONTEXT=$(docker context show 2>/dev/null || echo "unknown")
    success "当前 context: $CURRENT_CONTEXT"
    echo "   所有可用的 context:"
    docker context ls 2>/dev/null | tail -n +2 | while read line; do
        if echo "$line" | grep -q "*"; then
            echo "   * $line"
        else
            echo "     $line"
        fi
    done
else
    error "无法列出 Docker context"
fi
echo ""

# 4. 测试 Docker daemon 连接
echo "4. 测试 Docker daemon 连接..."
if docker info >/dev/null 2>&1; then
    success "Docker daemon 可以连接"
    echo "   Docker 版本信息:"
    docker version --format '{{.Server.Version}}' 2>/dev/null | sed 's/^/   Server: /'
    docker version --format '{{.Client.Version}}' 2>/dev/null | sed 's/^/   Client: /'
else
    error "Docker daemon 无法连接"
    echo "   错误详情:"
    docker info 2>&1 | sed 's/^/   /' | head -3
fi
echo ""

# 5. 检查 Docker 容器
echo "5. 检查 Docker 容器..."
if docker ps >/dev/null 2>&1; then
    CONTAINER_COUNT=$(docker ps -q | wc -l | tr -d ' ')
    if [ "$CONTAINER_COUNT" -gt 0 ]; then
        success "运行中的容器: $CONTAINER_COUNT 个"
        docker ps --format "   {{.Names}} ({{.Status}})" 2>/dev/null
    else
        info "没有运行中的容器"
    fi
else
    error "无法列出容器"
fi
echo ""

# 总结
echo "📊 诊断总结"
echo "============"
if docker info >/dev/null 2>&1; then
    success "Docker 状态正常，可以使用"
else
    error "Docker 无法使用"
    echo ""
    echo "建议的修复步骤:"
    echo "  1. 打开 Docker Desktop 应用"
    echo "  2. 查看是否有错误提示"
    echo "  3. 尝试 'Troubleshoot' → 'Restart'"
    echo "  4. 如果仍然失败，完全退出并重新启动 Docker Desktop"
    echo "  5. 检查系统资源（内存、CPU）"
fi
echo ""

