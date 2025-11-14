#!/bin/bash
# @purpose: 本地启动后端服务（使用 venv）
# @author: Daniel Chung
# @createdAt: 2025-01-14

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"

# 函数：打印信息
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# 函数：打印警告
warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 函数：打印错误
error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查虚拟环境
if [ ! -d "$BACKEND_DIR/venv" ]; then
    error "虚拟环境不存在，请先创建:"
    echo "  cd $BACKEND_DIR"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# 检查是否已有进程在运行
if [ -f /tmp/admin-backend.pid ]; then
    OLD_PID=$(cat /tmp/admin-backend.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        warning "检测到已有后端服务在运行 (PID: $OLD_PID)"
        read -p "是否要停止旧服务并启动新服务? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill $OLD_PID 2>/dev/null || true
            rm -f /tmp/admin-backend.pid
        else
            info "保持现有服务运行"
            exit 0
        fi
    else
        rm -f /tmp/admin-backend.pid
    fi
fi

# 检查数据库连接
info "检查数据库连接..."
if ! docker ps | grep -q admin-db-dev; then
    warning "数据库容器未运行，请先启动数据库:"
    echo "  cd $PROJECT_DIR"
    echo "  docker-compose -f docker-compose.dev.yml up admin-db -d"
    exit 1
fi

# 启动后端服务
info "启动后端服务 (端口: 8003)..."
cd "$BACKEND_DIR"

# 在后台启动服务
(
    source venv/bin/activate
    uvicorn src.main:app --host 0.0.0.0 --port 8003 --reload > /tmp/admin-backend.log 2>&1 &
    echo $! > /tmp/admin-backend.pid
)

# 等待服务启动
sleep 3

# 检查服务是否启动成功
max_attempts=10
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8003/health >/dev/null 2>&1; then
        info "后端服务已启动 (本地, http://localhost:8003)"
        info "API 文档: http://localhost:8003/docs"
        info "日志文件: /tmp/admin-backend.log"
        info "PID 文件: /tmp/admin-backend.pid"
        echo ""
        info "查看日志: tail -f /tmp/admin-backend.log"
        info "停止服务: kill \$(cat /tmp/admin-backend.pid)"
        exit 0
    fi
    attempt=$((attempt + 1))
    sleep 1
done

error "后端服务启动失败，请查看日志: /tmp/admin-backend.log"
tail -20 /tmp/admin-backend.log
exit 1

