#!/bin/bash

# @purpose: 检查所有服务配置和状态
# @author: Daniel Chung
# @createdAt: 2025-01-14
# @lastModified: 2025-01-14
# @usage: ./scripts/check-all-services.sh

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

echo "🔍 AAM 系统服务配置检查"
echo "========================"
echo ""

# 1. 检查 Docker 状态
echo "1. Docker 状态检查"
echo "------------------"
if docker info >/dev/null 2>&1; then
    success "Docker daemon 可以连接"
    docker version --format '{{.Server.Version}}' 2>/dev/null | sed 's/^/   Server: /'
else
    error "Docker daemon 无法连接"
fi
echo ""

# 2. 检查端口占用
echo "2. 端口占用检查"
echo "----------------"
PORTS=(8000 8001 8003 3000 5432 5433 15672 6379)
PORT_NAMES=("AAM Service" "ChromaDB" "Admin Backend" "Admin Frontend" "PostgreSQL (AAM)" "PostgreSQL (Admin)" "RabbitMQ" "Redis")

for i in "${!PORTS[@]}"; do
    PORT=${PORTS[$i]}
    NAME=${PORT_NAMES[$i]}
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        PID=$(lsof -ti:$PORT)
        PROCESS=$(ps -p $PID -o comm= 2>/dev/null || echo "unknown")
        warning "$NAME (Port $PORT): 被占用 (PID: $PID, Process: $PROCESS)"
    else
        info "$NAME (Port $PORT): 空闲"
    fi
done
echo ""

# 3. 检查 Docker 容器
echo "3. Docker 容器状态"
echo "------------------"
if docker ps >/dev/null 2>&1; then
    CONTAINER_COUNT=$(docker ps -q | wc -l | tr -d ' ')
    if [ "$CONTAINER_COUNT" -gt 0 ]; then
        success "运行中的容器: $CONTAINER_COUNT 个"
        docker ps --format "   - {{.Names}} ({{.Image}}): {{.Status}}" 2>/dev/null
    else
        info "没有运行中的容器"
    fi
    
    STOPPED_COUNT=$(docker ps -a -f "status=exited" -q | wc -l | tr -d ' ')
    if [ "$STOPPED_COUNT" -gt 0 ]; then
        warning "已停止的容器: $STOPPED_COUNT 个"
        docker ps -a -f "status=exited" --format "   - {{.Names}} ({{.Image}})" 2>/dev/null | head -5
    fi
else
    error "无法列出容器（Docker daemon 未连接）"
fi
echo ""

# 4. 检查 Docker 网络
echo "4. Docker 网络检查"
echo "------------------"
if docker network ls >/dev/null 2>&1; then
    NETWORKS=$(docker network ls --format "{{.Name}}" | grep -E "aam|admin" || echo "")
    if [ -n "$NETWORKS" ]; then
        success "发现相关网络:"
        echo "$NETWORKS" | sed 's/^/   - /'
    else
        info "没有发现 aam 或 admin 相关网络"
    fi
else
    error "无法列出网络（Docker daemon 未连接）"
fi
echo ""

# 5. 检查 Docker Compose 配置
echo "5. Docker Compose 配置检查"
echo "---------------------------"

# 检查 aam-service
if [ -f "aam-service/docker-compose.dev.yml" ]; then
    success "aam-service/docker-compose.dev.yml 存在"
    
    # 检查端口
    AAM_PORTS=$(grep -E "^\s+- \"[0-9]+:" aam-service/docker-compose.dev.yml | sed 's/.*"\([0-9]*\):.*/\1/' | sort -u)
    echo "   使用的端口: $AAM_PORTS"
    
    # 检查网络
    AAM_NETWORK=$(grep -A 1 "networks:" aam-service/docker-compose.dev.yml | grep -E "^\s+- " | head -1 | sed 's/.*- //' || echo "default")
    echo "   使用的网络: $AAM_NETWORK"
else
    error "aam-service/docker-compose.dev.yml 不存在"
fi

# 检查 aam-admin
if [ -f "aam-admin/docker-compose.dev.yml" ]; then
    success "aam-admin/docker-compose.dev.yml 存在"
    
    # 检查端口
    ADMIN_PORTS=$(grep -E "^\s+- \"[0-9]+:" aam-admin/docker-compose.dev.yml | sed 's/.*"\([0-9]*\):.*/\1/' | sort -u)
    echo "   使用的端口: $ADMIN_PORTS"
    
    # 检查网络
    ADMIN_NETWORK=$(grep -A 1 "networks:" aam-admin/docker-compose.dev.yml | grep -E "^\s+- " | head -1 | sed 's/.*- //' || echo "default")
    echo "   使用的网络: $ADMIN_NETWORK"
else
    error "aam-admin/docker-compose.dev.yml 不存在"
fi
echo ""

# 6. 检查端口冲突
echo "6. 端口冲突检查"
echo "----------------"
AAM_SERVICE_PORTS="8000 8001 5432 15672 6379"
ADMIN_PORTS="8003 5433 3000"

CONFLICTS=0
for port in $AAM_SERVICE_PORTS; do
    for admin_port in $ADMIN_PORTS; do
        if [ "$port" = "$admin_port" ]; then
            error "端口冲突: $port 被两个服务使用"
            CONFLICTS=$((CONFLICTS + 1))
        fi
    done
done

if [ $CONFLICTS -eq 0 ]; then
    success "没有发现端口冲突"
else
    error "发现 $CONFLICTS 个端口冲突"
fi
echo ""

# 7. 检查 Docker 资源使用
echo "7. Docker 资源使用"
echo "-------------------"
if docker stats --no-stream >/dev/null 2>&1; then
    info "Docker 资源使用情况:"
    docker stats --no-stream --format "   {{.Name}}: CPU {{.CPUPerc}}, Memory {{.MemUsage}}" 2>/dev/null | head -5
else
    warning "无法获取资源使用情况（Docker daemon 未连接）"
fi
echo ""

# 8. 总结和建议
echo "📊 检查总结"
echo "============"
if docker info >/dev/null 2>&1; then
    success "Docker daemon 状态: 正常"
else
    error "Docker daemon 状态: 异常"
    echo ""
    echo "建议:"
    echo "  1. 打开 Docker Desktop 应用，查看错误信息"
    echo "  2. 检查 Docker Desktop 日志"
    echo "  3. 尝试重启 Docker Desktop"
fi
echo ""

