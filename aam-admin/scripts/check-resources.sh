#!/bin/bash

# @purpose: AAM Admin 资源占用检查脚本
# @author: Daniel Chung
# @createdAt: 2025-01-14
# @lastModified: 2025-01-14
# @usage: ./scripts/check-resources.sh

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

# 函数：检查 Docker 容器资源占用
check_docker_resources() {
    local container_name=$1
    local service_name=$2
    
    if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        local stats=$(docker stats --no-stream --format "{{.MemUsage}}" "$container_name" 2>/dev/null)
        local mem_usage=$(echo "$stats" | awk '{print $1}')
        local mem_percent=$(echo "$stats" | awk '{print $3}' | tr -d '()')
        
        echo -e "${GREEN}✓${NC} $service_name (Docker):"
        echo "  内存占用: $mem_usage ($mem_percent)"
        return 0
    else
        echo -e "${RED}✗${NC} $service_name (Docker): 未运行"
        return 1
    fi
}

# 函数：检查本地进程资源占用
check_local_process() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        local pid=$(lsof -ti:$port)
        if [ -n "$pid" ]; then
            local mem_usage=$(ps -o rss= -p $pid 2>/dev/null | awk '{printf "%.1f MB", $1/1024}')
            local cpu_usage=$(ps -o %cpu= -p $pid 2>/dev/null | awk '{print $1"%"}')
            
            echo -e "${GREEN}✓${NC} $service_name (本地):"
            echo "  PID: $pid"
            echo "  内存占用: $mem_usage"
            echo "  CPU 占用: $cpu_usage"
            return 0
        fi
    else
        echo -e "${RED}✗${NC} $service_name (本地): 未运行"
        return 1
    fi
}

# 主函数
main() {
    echo "📊 AAM Admin 资源占用检查"
    echo "========================"
    echo ""
    
    # 检查 Docker 容器
    echo "🐳 Docker 容器资源占用:"
    check_docker_resources "admin-db-dev" "Admin Database"
    check_docker_resources "admin-backend-dev" "Admin Backend"
    echo ""
    
    # 检查本地进程
    echo "💻 本地进程资源占用:"
    check_local_process 8003 "Admin Backend"
    check_local_process 3000 "Admin Frontend"
    echo ""
    
    # 总结
    echo "📈 资源占用总结:"
    local docker_containers=$(docker ps --format '{{.Names}}' | grep -E "admin-db-dev|admin-backend-dev" | wc -l | tr -d ' ')
    local local_processes=$(lsof -i :8003 -i :3000 -sTCP:LISTEN -t 2>/dev/null | wc -l | tr -d ' ')
    
    echo "  Docker 容器: $docker_containers 个"
    echo "  本地进程: $local_processes 个"
    echo ""
    
    # 建议
    if [ "$docker_containers" -gt 0 ] && [ "$local_processes" -gt 0 ]; then
        warning "检测到混合模式运行（Docker + 本地）"
        echo ""
        echo "💡 建议:"
        echo "  - 如需环境一致性，使用 Docker 模式: ./scripts/start-service.sh all --docker"
        echo "  - 如需快速开发，使用本地模式: ./scripts/start-service.sh all"
        echo "  - 查看详细说明: cat docs/开发模式选择指南.md"
    elif [ "$docker_containers" -gt 0 ] && [ "$local_processes" -eq 0 ]; then
        success "当前使用 Docker 模式（环境一致）"
    elif [ "$docker_containers" -eq 0 ] && [ "$local_processes" -gt 0 ]; then
        warning "当前使用本地模式（数据库未运行）"
    else
        info "当前无服务运行"
    fi
}

# 执行主函数
main "$@"

