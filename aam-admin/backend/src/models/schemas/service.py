"""
@purpose: 服务管理相关的 Pydantic Schema 定义
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    """服务状态响应模型"""

    name: str = Field(..., description="服务名称")
    status: str = Field(..., description="服务状态 (running/stopped/error)")
    version: Optional[str] = Field(None, description="服务版本")
    cpu_usage: float = Field(0.0, description="CPU 使用率 (%)")
    memory_usage: float = Field(0.0, description="内存使用率 (%)")
    uptime: Optional[int] = Field(None, description="运行时间 (秒)")


class ServiceDetail(BaseModel):
    """服务详情响应模型"""

    name: str = Field(..., description="服务名称")
    status: str = Field(..., description="服务状态")
    version: Optional[str] = Field(None, description="服务版本")
    container_id: Optional[str] = Field(None, description="容器 ID")
    image: Optional[str] = Field(None, description="镜像名称")
    ports: List[str] = Field(default_factory=list, description="端口映射")
    cpu_usage: float = Field(0.0, description="CPU 使用率 (%)")
    memory_usage: Dict[str, float] = Field(
        default_factory=lambda: {"used": 0, "limit": 0, "percent": 0},
        description="内存使用情况",
    )
    uptime: Optional[int] = Field(None, description="运行时间 (秒)")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class ServiceStats(BaseModel):
    """服务资源统计响应模型"""

    service_name: str = Field(..., description="服务名称")
    cpu_usage: float = Field(..., description="CPU 使用率 (%)")
    memory_usage: Dict[str, float] = Field(..., description="内存使用情况")
    network_io: Optional[Dict[str, int]] = Field(None, description="网络 IO")
    disk_io: Optional[Dict[str, int]] = Field(None, description="磁盘 IO")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


class ServiceHealth(BaseModel):
    """服务健康状态响应模型"""

    service_name: str = Field(..., description="服务名称")
    status: str = Field(..., description="健康状态 (healthy/unhealthy/unknown)")
    last_check: datetime = Field(default_factory=datetime.utcnow, description="最后检查时间")
    details: Optional[Dict] = Field(None, description="健康检查详情")


class ServiceOperationRequest(BaseModel):
    """服务操作请求模型"""

    confirm: bool = Field(False, description="是否确认操作")
    reason: Optional[str] = Field(None, description="操作原因")


class ServiceOperationResponse(BaseModel):
    """服务操作响应模型"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="操作结果消息")
    service_name: str = Field(..., description="服务名称")
    operation: str = Field(..., description="操作类型")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="操作时间")

