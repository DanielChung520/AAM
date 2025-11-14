"""
@purpose: 日志配置模块，配置文件日志轮转
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.core.config import get_settings

settings = get_settings()


def setup_file_logging() -> None:
    """
    配置文件日志记录
    日志文件最大 2MB，最多保留 3 个备份
    """
    # 创建 logs 目录（如果不存在）
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # 日志文件路径
    log_file = log_dir / "backend.log"

    # 配置 RotatingFileHandler
    # maxBytes: 2MB = 2 * 1024 * 1024 bytes
    # backupCount: 3 个备份文件
    file_handler = RotatingFileHandler(
        filename=str(log_file),
        maxBytes=2 * 1024 * 1024,  # 2MB
        backupCount=3,  # 最多保留 3 个备份
        encoding="utf-8",
    )

    # 设置日志格式
    log_format = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(log_format)

    # 设置日志级别
    log_level = getattr(logging, settings.app.log_level.upper(), logging.INFO)
    file_handler.setLevel(log_level)

    # 获取根日志记录器并添加文件处理器
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

    # 确保日志级别正确设置
    root_logger.setLevel(log_level)

    # 同时配置 structlog 的标准库日志记录器
    stdlib_logger = logging.getLogger("structlog")
    stdlib_logger.addHandler(file_handler)
    stdlib_logger.setLevel(log_level)

