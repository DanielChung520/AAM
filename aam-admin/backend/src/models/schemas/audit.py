"""
@purpose: 审计系统相关的 Schema 类型定义
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field


class OperationType(str, Enum):
    """操作类型枚举（扩展 AuditAction）"""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    DEPLOY = "deploy"
    ROLLBACK = "rollback"
    START_SERVICE = "start_service"
    STOP_SERVICE = "stop_service"
    RESTART_SERVICE = "restart_service"


class ResourceType(str, Enum):
    """资源类型枚举"""

    SERVICE = "service"
    CONFIG = "config"
    DEPLOYMENT = "deployment"
    TOKEN = "token"
    LLM_PROVIDER = "llm_provider"
    USER = "user"
    SETTINGS = "settings"


class AuditLogResponse(BaseModel):
    """审计日志响应"""

    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str = Field(..., description="操作类型")
    resource_type: str = Field(..., description="资源类型")
    resource_id: Optional[str] = None
    description: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    before_state: Optional[Dict[str, Any]] = Field(None, description="操作前状态")
    after_state: Optional[Dict[str, Any]] = Field(None, description="操作后状态")
    status: Optional[str] = Field(None, description="操作状态（success/failed）")
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """审计日志列表响应"""

    items: List[AuditLogResponse]
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


class AuditLogQueryRequest(BaseModel):
    """审计日志查询请求"""

    user_id: Optional[int] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    keyword: Optional[str] = Field(None, description="关键词搜索")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    sort_by: str = Field("created_at", description="排序字段")
    sort_order: str = Field("desc", description="排序顺序（asc/desc）")


class AuditLogStatsResponse(BaseModel):
    """审计统计响应"""

    total_operations: int = Field(..., description="总操作数")
    success_count: int = Field(..., description="成功操作数")
    failed_count: int = Field(..., description="失败操作数")
    action_stats: Dict[str, int] = Field(..., description="按操作类型统计")
    user_stats: List[Dict[str, Any]] = Field(..., description="按操作者统计（前10名）")


class AuditLogTrendResponse(BaseModel):
    """审计趋势响应"""

    trends: List[Dict[str, Any]] = Field(..., description="趋势数据列表")
    group_by: str = Field(..., description="分组方式（hour/day/week/month）")


class AuditLogExportRequest(BaseModel):
    """审计日志导出请求"""

    format: str = Field("csv", description="导出格式（csv/json）")
    user_id: Optional[int] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

