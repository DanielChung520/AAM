"""
@purpose: 版本管理相关的 Pydantic Schema 定义
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class VersionStatus(str, Enum):
    """版本状态枚举"""

    ACTIVE = "active"
    AVAILABLE = "available"
    DEPRECATED = "deprecated"


class Version(BaseModel):
    """版本响应模型"""

    version: str = Field(..., description="版本号")
    status: VersionStatus = Field(..., description="版本状态")
    git_commit: Optional[str] = Field(None, description="Git Commit Hash")
    git_branch: Optional[str] = Field(None, description="Git Branch")
    git_tag: Optional[str] = Field(None, description="Git Tag")
    image_tag: Optional[str] = Field(None, description="Docker 镜像标签")
    created_at: datetime = Field(..., description="创建时间")
    created_by: Optional[str] = Field(None, description="创建者")
    description: Optional[str] = Field(None, description="版本描述")

    class Config:
        use_enum_values = True


class VersionCreateRequest(BaseModel):
    """版本创建请求模型"""

    version: str = Field(..., description="版本号（语义化版本格式，如 v1.0.0）")
    git_tag: Optional[str] = Field(None, description="Git Tag（可选，如果提供则从 Git 获取信息）")
    description: Optional[str] = Field(None, description="版本描述")
    image_tag: Optional[str] = Field(None, description="Docker 镜像标签（可选）")

    @validator("version")
    def validate_version_format(cls, v: str) -> str:
        """验证版本号格式"""
        if not v.startswith("v"):
            raise ValueError("版本号必须以 'v' 开头")
        parts = v[1:].split(".")
        if len(parts) != 3:
            raise ValueError("版本号格式应为 vMAJOR.MINOR.PATCH（如 v1.0.0）")
        try:
            int(parts[0])
            int(parts[1])
            int(parts[2])
        except ValueError:
            raise ValueError("版本号各部分必须为数字")
        return v


class VersionDetail(BaseModel):
    """版本详情响应模型"""

    version: str = Field(..., description="版本号")
    status: VersionStatus = Field(..., description="版本状态")
    git_commit: Optional[str] = Field(None, description="Git Commit Hash")
    git_branch: Optional[str] = Field(None, description="Git Branch")
    git_tag: Optional[str] = Field(None, description="Git Tag")
    image_tag: Optional[str] = Field(None, description="Docker 镜像标签")
    created_at: datetime = Field(..., description="创建时间")
    created_by: Optional[str] = Field(None, description="创建者")
    description: Optional[str] = Field(None, description="版本描述")
    config_snapshot: Optional[Dict] = Field(None, description="配置快照")
    docker_compose_config: Optional[Dict] = Field(None, description="Docker Compose 配置")
    environment_variables: Optional[Dict[str, str]] = Field(None, description="环境变量")
    service_config: Optional[Dict] = Field(None, description="服务配置")

    class Config:
        use_enum_values = True


class VersionCompareResponse(BaseModel):
    """版本比较响应模型"""

    version1: str = Field(..., description="版本1")
    version2: str = Field(..., description="版本2")
    differences: Dict[str, Dict] = Field(..., description="配置差异")
    summary: Dict[str, int] = Field(..., description="差异摘要（新增、删除、修改的数量）")

    class Config:
        schema_extra = {
            "example": {
                "version1": "v1.0.0",
                "version2": "v1.1.0",
                "differences": {
                    "docker_compose_config": {
                        "added": [],
                        "removed": [],
                        "modified": ["services.aam-service.image"],
                    },
                    "environment_variables": {
                        "added": ["NEW_FEATURE_ENABLED"],
                        "removed": [],
                        "modified": ["APP_VERSION"],
                    },
                },
                "summary": {"added": 1, "removed": 0, "modified": 2},
            }
        }


class VersionListResponse(BaseModel):
    """版本列表响应模型"""

    items: List[Version] = Field(..., description="版本列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class VersionFilter(BaseModel):
    """版本过滤参数"""

    status: Optional[VersionStatus] = Field(None, description="版本状态过滤")
    search: Optional[str] = Field(None, description="搜索关键词（版本号、描述）")
    created_after: Optional[datetime] = Field(None, description="创建时间起始")
    created_before: Optional[datetime] = Field(None, description="创建时间结束")

    class Config:
        use_enum_values = True

