"""
@purpose: 部署策略服务，提供部署策略的抽象基类和工厂模式
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional

from src.models.schemas.deployment import DeploymentStrategy

logger = logging.getLogger(__name__)


class DeploymentStrategyBase(ABC):
    """部署策略抽象基类"""

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化部署策略

        Args:
            config: 策略配置
        """
        self.config = config or {}

    @abstractmethod
    async def deploy(
        self,
        version: str,
        deployment_id: int,
        log_callback: Optional[callable] = None,
    ) -> bool:
        """
        执行部署

        Args:
            version: 版本号
            deployment_id: 部署记录 ID
            log_callback: 日志回调函数，用于记录部署日志

        Returns:
            bool: 是否部署成功
        """
        pass

    @abstractmethod
    async def rollback(
        self,
        version: str,
        deployment_id: int,
        log_callback: Optional[callable] = None,
    ) -> bool:
        """
        执行回滚

        Args:
            version: 要回滚到的版本号
            deployment_id: 部署记录 ID
            log_callback: 日志回调函数，用于记录回滚日志

        Returns:
            bool: 是否回滚成功
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        获取策略名称

        Returns:
            str: 策略名称
        """
        pass


class DeploymentStrategyFactory:
    """部署策略工厂类"""

    _strategies: Dict[DeploymentStrategy, type] = {}

    @classmethod
    def register_strategy(cls, strategy_type: DeploymentStrategy, strategy_class: type):
        """
        注册部署策略类

        Args:
            strategy_type: 策略类型
            strategy_class: 策略类
        """
        if not issubclass(strategy_class, DeploymentStrategyBase):
            raise ValueError(f"策略类必须继承自 DeploymentStrategyBase")
        cls._strategies[strategy_type] = strategy_class
        logger.info(f"注册部署策略: {strategy_type.value} -> {strategy_class.__name__}")

    @classmethod
    def create_strategy(
        cls, strategy_type: DeploymentStrategy, config: Optional[Dict] = None
    ) -> DeploymentStrategyBase:
        """
        创建部署策略实例

        Args:
            strategy_type: 策略类型
            config: 策略配置

        Returns:
            DeploymentStrategyBase: 部署策略实例

        Raises:
            ValueError: 当策略类型未注册时
        """
        if strategy_type not in cls._strategies:
            raise ValueError(f"未注册的部署策略类型: {strategy_type.value}")

        strategy_class = cls._strategies[strategy_type]
        return strategy_class(config)

    @classmethod
    def is_strategy_registered(cls, strategy_type: DeploymentStrategy) -> bool:
        """
        检查策略是否已注册

        Args:
            strategy_type: 策略类型

        Returns:
            bool: 是否已注册
        """
        return strategy_type in cls._strategies


# 延迟导入，避免循环依赖
def _register_strategies():
    """注册所有部署策略"""
    try:
        from src.core.services.strategies.blue_green_strategy import BlueGreenDeploymentStrategy
        from src.core.services.strategies.rolling_update_strategy import RollingUpdateStrategy
        from src.core.services.strategies.canary_strategy import CanaryDeploymentStrategy

        DeploymentStrategyFactory.register_strategy(
            DeploymentStrategy.BLUE_GREEN, BlueGreenDeploymentStrategy
        )
        DeploymentStrategyFactory.register_strategy(
            DeploymentStrategy.ROLLING, RollingUpdateStrategy
        )
        DeploymentStrategyFactory.register_strategy(
            DeploymentStrategy.CANARY, CanaryDeploymentStrategy
        )
    except ImportError as e:
        logger.warning(f"无法导入部署策略类: {e}")


# 在模块加载时注册策略
try:
    _register_strategies()
except Exception as e:
    logger.warning(f"注册部署策略失败: {e}")

