#!/bin/bash
# @purpose: 运行后端测试脚本
# @author: Daniel Chung
# @createdAt: 2025-01-14
# @lastModified: 2025-01-14

set -e

echo "=========================================="
echo "运行后端单元测试"
echo "=========================================="

cd "$(dirname "$0")/.."

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "警告: 未检测到虚拟环境，建议先激活虚拟环境"
fi

# 运行测试
echo ""
echo "运行所有测试..."
pytest tests/ -v --tb=short

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="

