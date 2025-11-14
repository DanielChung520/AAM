#!/bin/bash
# @purpose: 检查 Docker 环境状态
# @author: DanielChung and AI
# @createdAt: 2025-11-12
# @lastModified: 2025-11-12
# @usage: ./scripts/check-docker.sh

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Docker 环境状态检查${NC}"
echo -e "${BLUE}========================================${NC}\n"

# 1. 检查 Docker 是否安装
echo -e "${YELLOW}1. 检查 Docker 安装...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    echo -e "${YELLOW}   请安装 Docker Desktop: https://www.docker.com/products/docker-desktop${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker 已安装: $(docker --version)${NC}\n"

# 2. 检查 Docker daemon 是否运行
echo -e "${YELLOW}2. 检查 Docker daemon...${NC}"
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker daemon 未运行${NC}"
    echo -e "${YELLOW}   正在尝试启动 Docker Desktop...${NC}"
    open -a Docker
    
    echo -e "${YELLOW}   等待 Docker Desktop 启动（通常需要 30-60 秒）...${NC}"
    echo -e "${YELLOW}   请等待 Docker Desktop 图标停止动画后，再次运行此脚本${NC}"
    echo -e "${BLUE}   或者手动检查: docker info${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker daemon 正在运行${NC}\n"

# 3. 检查 Docker Compose
echo -e "${YELLOW}3. 检查 Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null && ! docker compose version >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose 未安装${NC}"
    exit 1
fi
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✅ Docker Compose 已安装: $(docker-compose --version)${NC}"
else
    echo -e "${GREEN}✅ Docker Compose 已安装: $(docker compose version)${NC}"
fi
echo ""

# 4. 检查容器状态
echo -e "${YELLOW}4. 检查 AAM 服务容器...${NC}"
cd "$(dirname "$0")/.."

if docker-compose ps 2>/dev/null | grep -q "aam-service"; then
    echo -e "${GREEN}✅ 发现 AAM 服务容器${NC}"
    echo ""
    echo -e "${BLUE}容器状态:${NC}"
    docker-compose ps
    echo ""
    
    # 检查容器是否运行
    if docker-compose ps | grep -q "Up"; then
        echo -e "${GREEN}✅ 服务正在运行${NC}"
        
        # 检查容器内的依赖版本
        echo ""
        echo -e "${YELLOW}5. 检查容器内的依赖版本...${NC}"
        echo -e "${BLUE}transformers & sentence-transformers:${NC}"
        docker-compose exec -T aam-service pip list 2>/dev/null | grep -E "(transformers|sentence-transformers|numpy)" || echo "无法获取依赖信息"
    else
        echo -e "${YELLOW}⚠️  容器存在但未运行${NC}"
        echo -e "${BLUE}   启动命令: docker-compose up -d${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  未发现 AAM 服务容器${NC}"
    echo -e "${BLUE}   启动命令: docker-compose up --build -d${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}检查完成！${NC}"
echo -e "${BLUE}========================================${NC}\n"

