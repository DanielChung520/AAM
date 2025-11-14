#!/usr/bin/env python3
"""
@purpose: 测试日志轮转功能
@author: Daniel Chung
@createdAt: 2025-01-14
"""

import logging
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.logging_config import setup_file_logging

# 配置日志
setup_file_logging()

# 获取日志记录器
logger = logging.getLogger(__name__)

# 测试不同级别的日志
logger.debug("这是一条 DEBUG 级别的日志")
logger.info("这是一条 INFO 级别的日志")
logger.warning("这是一条 WARNING 级别的日志")
logger.error("这是一条 ERROR 级别的日志")

# 测试日志文件位置
log_file = Path(__file__).parent.parent / "logs" / "backend.log"
print(f"\n日志文件位置: {log_file}")
print(f"日志文件大小: {log_file.stat().st_size if log_file.exists() else 0} bytes")
print(f"日志文件存在: {log_file.exists()}")

# 显示日志文件内容（最后几行）
if log_file.exists():
    print("\n日志文件内容（最后 5 行）:")
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines[-5:]:
            print(line.rstrip())

