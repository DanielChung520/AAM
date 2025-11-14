#!/bin/bash
# @purpose: 停止本地后端服务
# @author: Daniel Chung
# @createdAt: 2025-01-14

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 PID 文件
if [ -f /tmp/admin-backend.pid ]; then
    PID=$(cat /tmp/admin-backend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        info "停止后端服务 (PID: $PID)..."
        kill $PID
        rm -f /tmp/admin-backend.pid
        info "后端服务已停止"
    else
        warning "PID 文件存在但进程不存在，清理 PID 文件"
        rm -f /tmp/admin-backend.pid
    fi
else
    warning "未找到 PID 文件，尝试查找进程..."
    # 尝试通过端口查找进程
    PID=$(lsof -ti:8003 2>/dev/null || echo "")
    if [ -n "$PID" ]; then
        info "找到运行在端口 8003 的进程 (PID: $PID)，正在停止..."
        kill $PID
        info "后端服务已停止"
    else
        info "未找到运行中的后端服务"
    fi
fi

