"""
@purpose: 仪表盘相关的 Pydantic Schema 定义
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    """服务状态响应模型"""

    name: str = Field(..., description="服务名称")
    status: str = Field(..., description="服务状态 (running/stopped/error)")
    version: Optional[str] = Field(None, description="服务版本")
    cpu_usage: float = Field(0.0, description="CPU 使用率 (%)")
    memory_usage: float = Field(0.0, description="内存使用率 (%)")
    uptime: Optional[int] = Field(None, description="运行时间 (秒)")


class SystemMetrics(BaseModel):
    """系统资源指标响应模型"""

    cpu_usage: float = Field(..., description="CPU 使用率 (%)")
    memory_usage: float = Field(..., description="内存使用率 (%)")
    memory_total: float = Field(..., description="总内存 (MB)")
    memory_used: float = Field(..., description="已用内存 (MB)")
    disk_usage: float = Field(..., description="磁盘使用率 (%)")
    disk_total: float = Field(..., description="总磁盘空间 (GB)")
    disk_used: float = Field(..., description="已用磁盘空间 (GB)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


class RecentOperation(BaseModel):
    """最近操作记录响应模型"""

    id: int = Field(..., description="操作 ID")
    action: str = Field(..., description="操作类型")
    resource_type: str = Field(..., description="资源类型")
    resource_id: Optional[str] = Field(None, description="资源 ID")
    description: Optional[str] = Field(None, description="操作描述")
    operator: str = Field(..., description="操作者")
    status: str = Field(..., description="操作状态")
    created_at: datetime = Field(..., description="操作时间")


class DashboardStats(BaseModel):
    """仪表盘统计概览响应模型"""

    total_services: int = Field(..., description="总服务数")
    running_services: int = Field(..., description="运行中的服务数")
    total_providers: int = Field(..., description="总 LLM Provider 数")
    active_providers: int = Field(..., description="活跃的 Provider 数")
    current_version: Optional[str] = Field(None, description="当前版本")
    system_load: float = Field(..., description="系统负载 (%)")


class DashboardResponse(BaseModel):
    """仪表盘完整响应模型"""

    stats: DashboardStats = Field(..., description="统计概览")
    services: List[ServiceStatus] = Field(default_factory=list, description="服务状态列表")
    metrics: SystemMetrics = Field(..., description="系统资源指标")
    recent_operations: List[RecentOperation] = Field(
        default_factory=list, description="最近操作记录"
    )

