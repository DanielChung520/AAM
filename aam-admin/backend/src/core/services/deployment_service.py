"""
@purpose: 部署服务，负责部署的业务逻辑
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from src.core.services.deployment_history_service import DeploymentHistoryService
from src.core.services.version_service import VersionService
from src.models.database import DeploymentStatus
from src.models.schemas.deployment import (
    DeploymentStrategy,
    DeploymentPreviewResponse,
    DeploymentStatusResponse,
)
from src.models.schemas.version import VersionStatus
from src.models.version import Version

logger = logging.getLogger(__name__)


class DeploymentService:
    """部署服务类"""

    def __init__(self, db: Session):
        """
        初始化部署服务

        Args:
            db: 数据库会话
        """
        self.db = db
        self.history_service = DeploymentHistoryService(db)
        self.version_service = VersionService(db)

    def preview_deployment(
        self,
        version: str,
        strategy: DeploymentStrategy,
        config: Optional[Dict] = None,
    ) -> DeploymentPreviewResponse:
        """
        预览部署（验证配置、检查依赖）

        Args:
            version: 版本号
            strategy: 部署策略
            config: 部署配置

        Returns:
            DeploymentPreviewResponse: 部署预览结果

        Raises:
            ValueError: 当版本不存在时
        """
        # 检查版本是否存在
        version_obj = self.version_service.get_version(version)
        if not version_obj:
            raise ValueError(f"版本 {version} 不存在")

        warnings = []
        errors = []
        config_valid = True
        dependencies_ok = True

        # 验证配置
        if config:
            # 根据策略验证配置
            if strategy == DeploymentStrategy.BLUE_GREEN:
                # 蓝绿部署配置验证
                if "health_check_timeout" in config:
                    timeout = config.get("health_check_timeout", 300)
                    if timeout < 10 or timeout > 3600:
                        warnings.append("健康检查超时时间应在 10-3600 秒之间")
            elif strategy == DeploymentStrategy.ROLLING:
                # 滚动更新配置验证
                max_unavailable = config.get("max_unavailable", 1)
                max_surge = config.get("max_surge", 1)
                if max_unavailable < 0:
                    errors.append("最大不可用实例数不能为负数")
                    config_valid = False
                if max_surge < 1:
                    errors.append("最大新增实例数必须至少为 1")
                    config_valid = False
            elif strategy == DeploymentStrategy.CANARY:
                # 金丝雀部署配置验证
                initial_traffic = config.get("initial_traffic_percent", 10)
                if initial_traffic < 1 or initial_traffic > 50:
                    warnings.append("初始流量百分比建议在 1-50% 之间")
                max_error_rate = config.get("max_error_rate", 5)
                if max_error_rate < 0 or max_error_rate > 100:
                    errors.append("最大错误率必须在 0-100% 之间")
                    config_valid = False

        # 检查依赖（这里可以添加更多检查逻辑）
        # 例如：检查服务是否运行、检查配置兼容性等

        # 获取配置差异（与当前活动版本比较）
        config_diff = None
        try:
            active_version = self.version_service.get_active_version()
            if active_version:
                compare_result = self.version_service.compare_versions(
                    active_version.version, version
                )
                config_diff = compare_result.get("differences", {})
        except Exception as e:
            logger.warning(f"获取配置差异失败: {e}")
            warnings.append("无法获取配置差异")

        # 影响分析
        impact_analysis = {
            "affected_services": ["aam-service"],  # 这里可以根据实际情况分析
            "estimated_downtime": 0 if strategy == DeploymentStrategy.BLUE_GREEN else None,
            "rollback_available": True,
        }

        return DeploymentPreviewResponse(
            version=version,
            strategy=strategy,
            config_valid=config_valid and len(errors) == 0,
            dependencies_ok=dependencies_ok,
            config_diff=config_diff,
            impact_analysis=impact_analysis,
            warnings=warnings,
            errors=errors,
        )

    def deploy_version(
        self,
        version: str,
        strategy: DeploymentStrategy,
        operator_id: int,
        config: Optional[Dict] = None,
    ) -> int:
        """
        部署指定版本

        Args:
            version: 版本号
            strategy: 部署策略
            operator_id: 操作者 ID
            config: 部署配置

        Returns:
            int: 部署记录 ID

        Raises:
            ValueError: 当版本不存在或配置无效时
        """
        # 验证版本存在
        version_obj = self.version_service.get_version(version)
        if not version_obj:
            raise ValueError(f"版本 {version} 不存在")

        # 预览部署（验证配置）
        preview = self.preview_deployment(version, strategy, config)
        if not preview.config_valid:
            raise ValueError(f"配置验证失败: {', '.join(preview.errors)}")

        # 创建部署记录
        deployment = self.history_service.create_deployment_record(
            version=version,
            operator_id=operator_id,
            strategy=strategy,
            config_snapshot=config,
            extra_data={
                "preview": preview.dict(),
                "impact_analysis": preview.impact_analysis,
            },
        )

        # 更新状态为进行中
        self.history_service.update_deployment_status(
            deployment.id, DeploymentStatus.IN_PROGRESS
        )

        # 记录日志
        self.history_service.append_deployment_log(
            deployment.id, f"开始部署版本 {version}，策略: {strategy.value}"
        )

        # 使用部署策略服务执行部署
        try:
            from src.core.services.deployment_strategies import DeploymentStrategyFactory

            # 创建策略实例
            strategy_instance = DeploymentStrategyFactory.create_strategy(strategy, config)

            # 定义日志回调函数
            def log_callback(message: str):
                self.history_service.append_deployment_log(deployment.id, message)
                logger.info(f"[部署 {deployment.id}] {message}")

            # 执行部署（异步执行，这里简化处理）
            import asyncio

            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # 在后台执行部署
            async def execute_deployment():
                try:
                    success = await strategy_instance.deploy(
                        version, deployment.id, log_callback
                    )
                    if success:
                        self.history_service.update_deployment_status(
                            deployment.id, DeploymentStatus.SUCCESS
                        )
                        self.history_service.append_deployment_log(
                            deployment.id, f"部署成功完成，版本 {version} 已激活"
                        )
                        # 更新活动版本
                        self.version_service.set_active_version(version)
                    else:
                        self.history_service.update_deployment_status(
                            deployment.id, DeploymentStatus.FAILED
                        )
                        self.history_service.append_deployment_log(
                            deployment.id, "部署失败"
                        )
                except Exception as e:
                    logger.error(f"部署执行失败: {e}", exc_info=True)
                    self.history_service.update_deployment_status(
                        deployment.id, DeploymentStatus.FAILED
                    )
                    self.history_service.append_deployment_log(
                        deployment.id, f"部署失败: {str(e)}"
                    )

            # 在后台任务中执行（这里简化处理，实际应该使用 Celery 或类似的任务队列）
            loop.create_task(execute_deployment())

            logger.info(f"部署版本 {version}，策略 {strategy.value}，部署记录 ID: {deployment.id}")

        except Exception as e:
            logger.error(f"创建部署策略失败: {e}", exc_info=True)
            self.history_service.update_deployment_status(
                deployment.id, DeploymentStatus.FAILED
            )
            self.history_service.append_deployment_log(
                deployment.id, f"创建部署策略失败: {str(e)}"
            )
            raise

        return deployment.id

    def rollback_version(
        self,
        version: str,
        operator_id: int,
        reason: Optional[str] = None,
    ) -> int:
        """
        回滚到指定版本

        Args:
            version: 要回滚到的版本号
            operator_id: 操作者 ID
            reason: 回滚原因

        Returns:
            int: 部署记录 ID

        Raises:
            ValueError: 当版本不存在时
        """
        # 验证版本存在
        version_obj = self.version_service.get_version(version)
        if not version_obj:
            raise ValueError(f"版本 {version} 不存在")

        # 获取当前活动版本
        active_version = self.version_service.get_active_version()
        if not active_version:
            raise ValueError("当前没有活动版本")

        # 创建回滚部署记录
        deployment = self.history_service.create_deployment_record(
            version=version,
            operator_id=operator_id,
            strategy=DeploymentStrategy.BLUE_GREEN,  # 回滚默认使用蓝绿部署
            extra_data={
                "rollback": True,
                "rollback_from": active_version.version,
                "reason": reason,
            },
        )

        # 设置回滚版本
        self.history_service.set_rollback_version(deployment.id, active_version.version)

        # 更新状态为进行中
        self.history_service.update_deployment_status(
            deployment.id, DeploymentStatus.IN_PROGRESS
        )

        # 记录日志
        log_message = f"开始回滚到版本 {version}"
        if reason:
            log_message += f"，原因: {reason}"
        self.history_service.append_deployment_log(deployment.id, log_message)

        logger.info(f"回滚到版本 {version}，部署记录 ID: {deployment.id}")

        # TODO: 这里应该调用实际的部署策略服务来执行回滚
        # 实际回滚逻辑将在后续实现

        return deployment.id

    def switch_active_version(self, version: str, operator_id: int) -> bool:
        """
        切换活动版本（零中断）

        Args:
            version: 要切换到的版本号
            operator_id: 操作者 ID

        Returns:
            bool: 是否成功切换

        Raises:
            ValueError: 当版本不存在时
        """
        # 验证版本存在
        version_obj = self.version_service.get_version(version)
        if not version_obj:
            raise ValueError(f"版本 {version} 不存在")

        # 获取当前活动版本
        current_active = self.version_service.get_active_version()

        # 更新版本状态（使用版本服务的方法）
        if current_active:
            # 将当前活动版本设置为可用
            current_active.status = VersionStatus.AVAILABLE
            self.db.add(current_active)
            self.db.commit()

        # 将新版本设置为活动
        version_obj.status = VersionStatus.ACTIVE
        self.db.add(version_obj)
        self.db.commit()
        self.db.refresh(version_obj)

        logger.info(f"切换活动版本: {current_active.version if current_active else 'None'} -> {version}")

        return True

    def get_deployment_status(self, deployment_id: int) -> Optional[DeploymentStatusResponse]:
        """
        获取部署状态

        Args:
            deployment_id: 部署记录 ID

        Returns:
            Optional[DeploymentStatusResponse]: 部署状态，如果不存在则返回 None
        """
        deployment = self.history_service.get_deployment(deployment_id)
        if not deployment:
            return None

        # 计算进度（简化版本，实际应该根据部署步骤计算）
        progress = None
        if deployment.status == DeploymentStatus.SUCCESS:
            progress = 100.0
        elif deployment.status == DeploymentStatus.FAILED:
            progress = 0.0
        elif deployment.status == DeploymentStatus.IN_PROGRESS:
            progress = 50.0  # 默认进度，实际应该根据步骤计算
        elif deployment.status == DeploymentStatus.PENDING:
            progress = 0.0

        # 部署步骤（简化版本）
        steps = []
        if deployment.status != DeploymentStatus.PENDING:
            steps.append({"name": "准备部署", "status": "completed"})
        if deployment.status in [
            DeploymentStatus.IN_PROGRESS,
            DeploymentStatus.SUCCESS,
            DeploymentStatus.FAILED,
        ]:
            steps.append({"name": "执行部署", "status": "in_progress" if deployment.status == DeploymentStatus.IN_PROGRESS else "completed"})
        if deployment.status in [DeploymentStatus.SUCCESS, DeploymentStatus.FAILED]:
            steps.append({"name": "完成部署", "status": "completed"})

        return DeploymentStatusResponse(
            id=deployment.id,
            status=deployment.status,
            progress=progress,
            current_step=steps[-1]["name"] if steps else None,
            steps=steps,
            error_message=deployment.error_message,
        )

    def get_deployment_logs(self, deployment_id: int, tail: int = 1000) -> Optional[str]:
        """
        获取部署日志

        Args:
            deployment_id: 部署记录 ID
            tail: 返回最后 N 行

        Returns:
            Optional[str]: 部署日志，如果不存在则返回 None
        """
        deployment = self.history_service.get_deployment(deployment_id)
        if not deployment or not deployment.logs:
            return None

        # 返回最后 N 行日志
        lines = deployment.logs.split("\n")
        if len(lines) > tail:
            return "\n".join(lines[-tail:])
        return deployment.logs

