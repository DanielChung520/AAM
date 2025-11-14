"""
@purpose: 系统设置相关的 Schema 类型定义
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class SystemSettingsResponse(BaseModel):
    """系统配置响应"""

    app_name: str = Field(..., description="应用名称")
    app_version: str = Field(..., description="应用版本")
    debug: bool = Field(..., description="调试模式")
    log_level: str = Field(..., description="日志级别")
    api_host: str = Field(..., description="API 主机")
    api_port: int = Field(..., description="API 端口")
    api_prefix: str = Field(..., description="API 前缀")
    cors_origins: List[str] = Field(..., description="CORS 允许的来源")
    database_url: str = Field(..., description="数据库 URL（只读）")
    docker_host: Optional[str] = Field(None, description="Docker 主机（只读）")
    docker_base_url: Optional[str] = Field(None, description="Docker Base URL（只读）")

    class Config:
        from_attributes = True


class SystemSettingsUpdateRequest(BaseModel):
    """系统配置更新请求"""

    app_name: Optional[str] = Field(None, description="应用名称")
    app_version: Optional[str] = Field(None, description="应用版本")
    debug: Optional[bool] = Field(None, description="调试模式")
    log_level: Optional[str] = Field(None, description="日志级别（DEBUG/INFO/WARNING/ERROR）")
    api_host: Optional[str] = Field(None, description="API 主机")
    api_port: Optional[int] = Field(None, description="API 端口")
    api_prefix: Optional[str] = Field(None, description="API 前缀")
    cors_origins: Optional[List[str]] = Field(None, description="CORS 允许的来源")


class EnvironmentVariableResponse(BaseModel):
    """环境变量响应"""

    key: str = Field(..., description="环境变量键")
    value: str = Field(..., description="环境变量值（可能部分隐藏）")
    is_sensitive: bool = Field(False, description="是否为敏感信息")
    description: Optional[str] = Field(None, description="描述")


class EnvironmentVariableListResponse(BaseModel):
    """环境变量列表响应"""

    items: List[EnvironmentVariableResponse] = Field(..., description="环境变量列表")
    total: int = Field(..., description="总数")


class EnvironmentVariableUpdateRequest(BaseModel):
    """环境变量更新请求"""

    value: str = Field(..., description="环境变量值")
    description: Optional[str] = Field(None, description="描述")


class SystemHealthStatusResponse(BaseModel):
    """系统健康状态响应"""

    overall_status: str = Field(..., description="总体状态（healthy/warning/unhealthy）")
    checks: Dict[str, Dict[str, Any]] = Field(..., description="各项检查结果")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="检查时间")


class BackupRecordResponse(BaseModel):
    """备份记录响应"""

    id: str = Field(..., description="备份 ID")
    name: str = Field(..., description="备份名称")
    created_at: datetime = Field(..., description="创建时间")
    size: int = Field(..., description="备份大小（字节）")
    status: str = Field(..., description="备份状态（completed/failed/in_progress）")
    includes: Dict[str, bool] = Field(..., description="包含的内容（database/config/versions）")
    description: Optional[str] = Field(None, description="描述")


class BackupListResponse(BaseModel):
    """备份列表响应"""

    items: List[BackupRecordResponse] = Field(..., description="备份列表")
    total: int = Field(..., description="总数")


class BackupRequest(BaseModel):
    """备份请求"""

    name: Optional[str] = Field(None, description="备份名称（可选，默认使用时间戳）")
    include_database: bool = Field(True, description="包含数据库")
    include_config: bool = Field(True, description="包含配置文件")
    include_versions: bool = Field(True, description="包含版本配置")
    description: Optional[str] = Field(None, description="描述")


class BackupRestoreRequest(BaseModel):
    """备份恢复请求"""

    backup_id: str = Field(..., description="备份 ID")
    restore_database: bool = Field(True, description="恢复数据库")
    restore_config: bool = Field(True, description="恢复配置文件")
    restore_versions: bool = Field(True, description="恢复版本配置")

