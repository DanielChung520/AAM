#!/bin/bash

# @purpose: 检查 Docker 配置冲突
# @author: Daniel Chung
# @createdAt: 2025-01-14
# @lastModified: 2025-01-14
# @usage: ./scripts/check-docker-conflicts.sh

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

echo "🔍 Docker 配置冲突检查"
echo "======================"
echo ""

# 检查 Docker daemon
if ! docker info >/dev/null 2>&1; then
    error "Docker daemon 无法连接"
    exit 1
fi

CONFLICTS=0

# 1. 检查容器名称冲突
echo "1. 容器名称检查"
echo "----------------"
AAM_CONTAINERS=$(grep "container_name:" aam-service/docker-compose.dev.yml 2>/dev/null | sed 's/.*container_name: *//' | tr -d ' ' || echo "")
ADMIN_CONTAINERS=$(grep "container_name:" aam-admin/docker-compose.dev.yml 2>/dev/null | sed 's/.*container_name: *//' | tr -d ' ' || echo "")

echo "aam-service 容器:"
echo "$AAM_CONTAINERS" | sed 's/^/   - /'
echo ""
echo "aam-admin 容器:"
echo "$ADMIN_CONTAINERS" | sed 's/^/   - /'
echo ""

# 检查是否有重复
ALL_CONTAINERS=$(echo -e "$AAM_CONTAINERS\n$ADMIN_CONTAINERS")
DUPLICATES=$(echo "$ALL_CONTAINERS" | sort | uniq -d)
if [ -n "$DUPLICATES" ]; then
    error "发现重复的容器名称:"
    echo "$DUPLICATES" | sed 's/^/   - /'
    CONFLICTS=$((CONFLICTS + 1))
else
    success "没有容器名称冲突"
fi
echo ""

# 2. 检查网络名称冲突
echo "2. 网络名称检查"
echo "----------------"
AAM_NETWORKS=$(grep -A 1 "^networks:" aam-service/docker-compose.dev.yml 2>/dev/null | grep -E "^\s+[a-zA-Z]" | sed 's/.*: *//' | tr -d ' ' || echo "")
ADMIN_NETWORKS=$(grep -A 1 "^networks:" aam-admin/docker-compose.dev.yml 2>/dev/null | grep -E "^\s+[a-zA-Z]" | sed 's/.*: *//' | tr -d ' ' || echo "")

echo "aam-service 网络:"
echo "$AAM_NETWORKS" | sed 's/^/   - /'
echo ""
echo "aam-admin 网络:"
echo "$ADMIN_NETWORKS" | sed 's/^/   - /'
echo ""

ALL_NETWORKS=$(echo -e "$AAM_NETWORKS\n$ADMIN_NETWORKS")
DUPLICATES=$(echo "$ALL_NETWORKS" | sort | uniq -d)
if [ -n "$DUPLICATES" ]; then
    error "发现重复的网络名称:"
    echo "$DUPLICATES" | sed 's/^/   - /'
    CONFLICTS=$((CONFLICTS + 1))
else
    success "没有网络名称冲突"
fi
echo ""

# 3. 检查卷名称冲突
echo "3. 卷名称检查"
echo "--------------"
AAM_VOLUMES=$(grep -A 10 "^volumes:" aam-service/docker-compose.dev.yml 2>/dev/null | grep -E "^\s+[a-zA-Z]" | sed 's/.*: *//' | tr -d ' ' || echo "")
ADMIN_VOLUMES=$(grep -A 10 "^volumes:" aam-admin/docker-compose.dev.yml 2>/dev/null | grep -E "^\s+[a-zA-Z]" | sed 's/.*: *//' | tr -d ' ' || echo "")

echo "aam-service 卷:"
echo "$AAM_VOLUMES" | sed 's/^/   - /'
echo ""
echo "aam-admin 卷:"
echo "$ADMIN_VOLUMES" | sed 's/^/   - /'
echo ""

ALL_VOLUMES=$(echo -e "$AAM_VOLUMES\n$ADMIN_VOLUMES")
DUPLICATES=$(echo "$ALL_VOLUMES" | sort | uniq -d)
if [ -n "$DUPLICATES" ]; then
    error "发现重复的卷名称:"
    echo "$DUPLICATES" | sed 's/^/   - /'
    CONFLICTS=$((CONFLICTS + 1))
else
    success "没有卷名称冲突"
fi
echo ""

# 4. 检查端口冲突
echo "4. 端口冲突检查"
echo "----------------"
AAM_PORTS=$(grep -E "^\s+- \"[0-9]+:" aam-service/docker-compose.dev.yml 2>/dev/null | sed 's/.*"\([0-9]*\):.*/\1/' | sort -u || echo "")
ADMIN_PORTS=$(grep -E "^\s+- \"[0-9]+:" aam-admin/docker-compose.dev.yml 2>/dev/null | sed 's/.*"\([0-9]*\):.*/\1/' | sort -u || echo "")

echo "aam-service 端口: $AAM_PORTS"
echo "aam-admin 端口: $ADMIN_PORTS"
echo ""

for port in $AAM_PORTS; do
    for admin_port in $ADMIN_PORTS; do
        if [ "$port" = "$admin_port" ]; then
            error "端口冲突: $port"
            CONFLICTS=$((CONFLICTS + 1))
        fi
    done
done

if [ $CONFLICTS -eq 0 ]; then
    success "没有端口冲突"
fi
echo ""

# 5. 检查运行中的容器
echo "5. 运行中的容器检查"
echo "-------------------"
RUNNING_CONTAINERS=$(docker ps --format "{{.Names}}" 2>/dev/null || echo "")
if [ -n "$RUNNING_CONTAINERS" ]; then
    info "运行中的容器:"
    echo "$RUNNING_CONTAINERS" | sed 's/^/   - /'
    
    # 检查是否有冲突的容器名称
    for container in $RUNNING_CONTAINERS; do
        if echo "$AAM_CONTAINERS" | grep -q "^${container}$" && echo "$ADMIN_CONTAINERS" | grep -q "^${container}$"; then
            error "容器 $container 在两个配置中都存在"
            CONFLICTS=$((CONFLICTS + 1))
        fi
    done
else
    info "没有运行中的容器"
fi
echo ""

# 总结
echo "📊 检查总结"
echo "============"
if [ $CONFLICTS -eq 0 ]; then
    success "没有发现配置冲突"
    exit 0
else
    error "发现 $CONFLICTS 个冲突"
    exit 1
fi

