"""
@purpose: 部署管理相关的 Pydantic Schema 定义
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DeploymentStatus(str, Enum):
    """部署状态枚举"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DeploymentStrategy(str, Enum):
    """部署策略枚举"""

    BLUE_GREEN = "blue_green"
    ROLLING = "rolling"
    CANARY = "canary"


class DeploymentRecord(BaseModel):
    """部署记录响应模型"""

    id: int = Field(..., description="部署记录 ID")
    version: str = Field(..., description="版本号")
    status: DeploymentStatus = Field(..., description="部署状态")
    operator_id: int = Field(..., description="操作者 ID")
    operator_name: Optional[str] = Field(None, description="操作者名称")
    deployment_time: datetime = Field(..., description="部署时间")
    completed_time: Optional[datetime] = Field(None, description="完成时间")
    rollback_version: Optional[str] = Field(None, description="回滚版本")
    deployment_strategy: Optional[DeploymentStrategy] = Field(None, description="部署策略")
    config_snapshot: Optional[Dict] = Field(None, description="配置快照")
    error_message: Optional[str] = Field(None, description="错误信息")
    extra_data: Optional[Dict] = Field(None, description="额外信息")

    class Config:
        use_enum_values = True


class DeploymentRequest(BaseModel):
    """部署请求模型"""

    version: str = Field(..., description="要部署的版本号")
    strategy: DeploymentStrategy = Field(..., description="部署策略")
    config: Optional[Dict] = Field(None, description="部署配置（策略相关）")
    preview: bool = Field(False, description="是否仅预览（不实际部署）")

    class Config:
        use_enum_values = True


class DeploymentPreviewResponse(BaseModel):
    """部署预览响应模型"""

    version: str = Field(..., description="版本号")
    strategy: DeploymentStrategy = Field(..., description="部署策略")
    config_valid: bool = Field(..., description="配置是否有效")
    dependencies_ok: bool = Field(..., description="依赖检查是否通过")
    config_diff: Optional[Dict] = Field(None, description="配置差异")
    impact_analysis: Optional[Dict] = Field(None, description="影响分析")
    warnings: List[str] = Field(default_factory=list, description="警告信息")
    errors: List[str] = Field(default_factory=list, description="错误信息")

    class Config:
        use_enum_values = True


class DeploymentListResponse(BaseModel):
    """部署列表响应模型"""

    items: List[DeploymentRecord] = Field(..., description="部署记录列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class DeploymentStatusResponse(BaseModel):
    """部署状态响应模型"""

    id: int = Field(..., description="部署记录 ID")
    status: DeploymentStatus = Field(..., description="部署状态")
    progress: Optional[float] = Field(None, description="部署进度（0-100）")
    current_step: Optional[str] = Field(None, description="当前步骤")
    steps: List[Dict] = Field(default_factory=list, description="部署步骤列表")
    error_message: Optional[str] = Field(None, description="错误信息")

    class Config:
        use_enum_values = True


class RollbackRequest(BaseModel):
    """回滚请求模型"""

    version: str = Field(..., description="要回滚到的版本号")
    reason: Optional[str] = Field(None, description="回滚原因")

