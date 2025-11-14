"""
@purpose: 部署历史服务，负责部署记录的创建、查询和更新
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc

from src.models.database import DeploymentRecord, DeploymentStatus, User
from src.models.schemas.deployment import DeploymentStrategy

logger = logging.getLogger(__name__)


class DeploymentHistoryService:
    """部署历史服务类"""

    def __init__(self, db: Session):
        """
        初始化部署历史服务

        Args:
            db: 数据库会话
        """
        self.db = db

    def create_deployment_record(
        self,
        version: str,
        operator_id: int,
        strategy: Optional[DeploymentStrategy] = None,
        config_snapshot: Optional[Dict] = None,
        extra_data: Optional[Dict] = None,
    ) -> DeploymentRecord:
        """
        创建部署记录

        Args:
            version: 版本号
            operator_id: 操作者 ID
            strategy: 部署策略
            config_snapshot: 配置快照
            extra_data: 额外信息

        Returns:
            DeploymentRecord: 创建的部署记录
        """
        deployment = DeploymentRecord(
            version=version,
            status=DeploymentStatus.PENDING,
            operator_id=operator_id,
            deployment_strategy=strategy.value if strategy else None,
            config_snapshot=config_snapshot,
            extra_data=extra_data,
        )

        self.db.add(deployment)
        self.db.commit()
        self.db.refresh(deployment)

        logger.info(f"创建部署记录: ID={deployment.id}, Version={version}, Operator={operator_id}")
        return deployment

    def get_deployment(self, deployment_id: int) -> Optional[DeploymentRecord]:
        """
        获取部署记录详情

        Args:
            deployment_id: 部署记录 ID

        Returns:
            Optional[DeploymentRecord]: 部署记录，如果不存在则返回 None
        """
        return self.db.query(DeploymentRecord).filter(DeploymentRecord.id == deployment_id).first()

    def list_deployments(
        self,
        page: int = 1,
        page_size: int = 20,
        version: Optional[str] = None,
        status: Optional[DeploymentStatus] = None,
        operator_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        sort_by: str = "deployment_time",
        sort_order: str = "desc",
    ) -> Tuple[List[DeploymentRecord], int]:
        """
        查询部署历史列表

        Args:
            page: 页码
            page_size: 每页数量
            version: 版本号过滤
            status: 状态过滤
            operator_id: 操作者 ID 过滤
            start_time: 开始时间过滤
            end_time: 结束时间过滤
            sort_by: 排序字段
            sort_order: 排序顺序（asc/desc）

        Returns:
            Tuple[List[DeploymentRecord], int]: (部署记录列表, 总数量)
        """
        query = self.db.query(DeploymentRecord)

        # 应用过滤条件
        if version:
            query = query.filter(DeploymentRecord.version == version)
        if status:
            query = query.filter(DeploymentRecord.status == status)
        if operator_id:
            query = query.filter(DeploymentRecord.operator_id == operator_id)
        if start_time:
            query = query.filter(DeploymentRecord.deployment_time >= start_time)
        if end_time:
            query = query.filter(DeploymentRecord.deployment_time <= end_time)

        # 获取总数
        total = query.count()

        # 排序
        if sort_by == "deployment_time":
            order_column = DeploymentRecord.deployment_time
        elif sort_by == "status":
            order_column = DeploymentRecord.status
        elif sort_by == "version":
            order_column = DeploymentRecord.version
        else:
            order_column = DeploymentRecord.deployment_time

        if sort_order.lower() == "asc":
            query = query.order_by(asc(order_column))
        else:
            query = query.order_by(desc(order_column))

        # 分页
        offset = (page - 1) * page_size
        deployments = query.offset(offset).limit(page_size).all()

        return deployments, total

    def update_deployment_status(
        self,
        deployment_id: int,
        status: DeploymentStatus,
        error_message: Optional[str] = None,
        logs: Optional[str] = None,
        extra_data: Optional[Dict] = None,
    ) -> Optional[DeploymentRecord]:
        """
        更新部署状态

        Args:
            deployment_id: 部署记录 ID
            status: 新状态
            error_message: 错误信息（如果失败）
            logs: 部署日志
            extra_data: 额外信息

        Returns:
            Optional[DeploymentRecord]: 更新后的部署记录，如果不存在则返回 None
        """
        deployment = self.get_deployment(deployment_id)
        if not deployment:
            return None

        deployment.status = status

        # 如果状态为成功或失败，设置完成时间
        if status in [DeploymentStatus.SUCCESS, DeploymentStatus.FAILED, DeploymentStatus.ROLLED_BACK]:
            deployment.completed_time = datetime.utcnow()

        if error_message:
            deployment.error_message = error_message
        if logs:
            # 追加日志
            if deployment.logs:
                deployment.logs = deployment.logs + "\n" + logs
            else:
                deployment.logs = logs
        if extra_data:
            if deployment.extra_data:
                deployment.extra_data.update(extra_data)
            else:
                deployment.extra_data = extra_data

        self.db.commit()
        self.db.refresh(deployment)

        logger.info(f"更新部署状态: ID={deployment_id}, Status={status.value}")
        return deployment

    def append_deployment_log(self, deployment_id: int, log_message: str) -> Optional[DeploymentRecord]:
        """
        追加部署日志

        Args:
            deployment_id: 部署记录 ID
            log_message: 日志消息

        Returns:
            Optional[DeploymentRecord]: 更新后的部署记录，如果不存在则返回 None
        """
        deployment = self.get_deployment(deployment_id)
        if not deployment:
            return None

        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] {log_message}\n"

        if deployment.logs:
            deployment.logs = deployment.logs + log_entry
        else:
            deployment.logs = log_entry

        self.db.commit()
        self.db.refresh(deployment)

        return deployment

    def set_rollback_version(self, deployment_id: int, rollback_version: str) -> Optional[DeploymentRecord]:
        """
        设置回滚版本

        Args:
            deployment_id: 部署记录 ID
            rollback_version: 回滚版本号

        Returns:
            Optional[DeploymentRecord]: 更新后的部署记录，如果不存在则返回 None
        """
        deployment = self.get_deployment(deployment_id)
        if not deployment:
            return None

        deployment.rollback_version = rollback_version
        self.db.commit()
        self.db.refresh(deployment)

        logger.info(f"设置回滚版本: ID={deployment_id}, RollbackVersion={rollback_version}")
        return deployment

