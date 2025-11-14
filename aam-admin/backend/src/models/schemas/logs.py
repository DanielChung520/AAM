"""
@purpose: 日志管理相关的 Pydantic Schema 定义
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    """日志条目响应模型"""

    timestamp: datetime = Field(..., description="时间戳")
    level: str = Field(..., description="日志级别 (DEBUG/INFO/WARNING/ERROR)")
    service: str = Field(..., description="服务名称")
    message: str = Field(..., description="日志消息")
    raw: Optional[str] = Field(None, description="原始日志行")


class LogSearchRequest(BaseModel):
    """日志搜索请求模型"""

    service: Optional[str] = Field(None, description="服务名称过滤")
    level: Optional[str] = Field(None, description="日志级别过滤 (DEBUG/INFO/WARNING/ERROR)")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    keyword: Optional[str] = Field(None, description="关键词搜索")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(100, ge=1, le=1000, description="每页数量")


class LogSearchResponse(BaseModel):
    """日志搜索响应模型"""

    items: List[LogEntry] = Field(default_factory=list, description="日志条目列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class LogExportRequest(BaseModel):
    """日志导出请求模型"""

    service: Optional[str] = Field(None, description="服务名称过滤")
    level: Optional[str] = Field(None, description="日志级别过滤")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    keyword: Optional[str] = Field(None, description="关键词搜索")
    format: str = Field("json", description="导出格式 (json/csv)")


