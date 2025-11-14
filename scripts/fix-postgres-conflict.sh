#!/bin/bash

# @purpose: 修复 PostgreSQL 端口冲突
# @author: Daniel Chung
# @createdAt: 2025-01-14
# @lastModified: 2025-01-14
# @usage: ./scripts/fix-postgres-conflict.sh

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

echo "🔧 PostgreSQL 端口冲突修复工具"
echo "=============================="
echo ""

# 检查端口 5432 占用
info "检查端口 5432 占用情况..."
if lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
    PID=$(lsof -ti:5432)
    PROCESS=$(ps -p $PID -o comm=,args= 2>/dev/null | head -1 || echo "unknown")
    warning "端口 5432 被占用"
    echo "   PID: $PID"
    echo "   进程: $PROCESS"
    echo ""
    
    # 检查是否是本地 PostgreSQL
    if echo "$PROCESS" | grep -q "postgres"; then
        warning "检测到本地 PostgreSQL 占用端口 5432"
        echo "   这会导致 aam-service 的 postgres 容器无法启动"
        echo ""
        
        echo "请选择操作："
        echo "  1) 停止本地 PostgreSQL（推荐，统一使用 Docker）"
        echo "  2) 修改 aam-service 的 PostgreSQL 端口为 5434"
        echo "  3) 取消"
        echo ""
        read -p "请输入选项 (1-3，默认: 1): " choice
        choice=${choice:-1}
        
        case $choice in
            1)
                info "停止本地 PostgreSQL..."
                
                # 尝试使用 Homebrew 停止
                if command -v brew >/dev/null 2>&1; then
                    if brew services list 2>/dev/null | grep -q "postgresql"; then
                        brew services stop postgresql@15 2>/dev/null || brew services stop postgresql 2>/dev/null
                        success "已通过 Homebrew 停止 PostgreSQL"
                    else
                        # 直接停止进程
                        kill $PID 2>/dev/null || true
                        sleep 2
                        if ! lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
                            success "已停止本地 PostgreSQL"
                        else
                            error "无法停止 PostgreSQL，请手动停止"
                        fi
                    fi
                else
                    # 直接停止进程
                    kill $PID 2>/dev/null || true
                    sleep 2
                    if ! lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
                        success "已停止本地 PostgreSQL"
                    else
                        error "无法停止 PostgreSQL，请手动停止"
                    fi
                fi
                ;;
            2)
                warning "修改 aam-service 的 PostgreSQL 端口..."
                info "需要修改 aam-service/docker-compose.dev.yml"
                info "将 postgres 的端口映射从 '5432:5432' 改为 '5434:5432'"
                info "并更新相关环境变量"
                echo ""
                echo "⚠️  注意: 此操作需要手动修改配置文件"
                ;;
            3)
                info "操作已取消"
                exit 0
                ;;
            *)
                error "无效选项"
                exit 1
                ;;
        esac
    else
        warning "端口 5432 被其他进程占用"
        echo "   请检查是否需要停止该进程"
    fi
else
    success "端口 5432 空闲"
fi
echo ""

# 验证修复
info "验证端口状态..."
if ! lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
    success "端口 5432 已释放，aam-service 的 postgres 容器可以正常启动"
else
    warning "端口 5432 仍被占用"
fi
echo ""

