"""
@purpose: 操作审计服务，负责记录、查询、过滤、导出和统计审计日志
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import csv
import json
import logging
from datetime import datetime, timedelta
from io import StringIO
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
from sqlalchemy.sql import text

from src.models.database import AuditLog, AuditAction, User

logger = logging.getLogger(__name__)


class AuditService:
    """操作审计服务类"""

    # 敏感字段列表（这些字段的值会被过滤）
    SENSITIVE_FIELDS = {
        "password",
        "api_key",
        "secret_key",
        "token",
        "access_token",
        "refresh_token",
        "authorization",
    }

    def __init__(self, db: Session):
        """
        初始化审计服务

        Args:
            db: 数据库会话
        """
        self.db = db

    def log_operation(
        self,
        user_id: Optional[int],
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        记录操作审计日志

        Args:
            user_id: 用户 ID
            action: 操作类型
            resource_type: 资源类型
            resource_id: 资源 ID
            description: 操作描述
            ip_address: IP 地址
            user_agent: 用户代理
            request_data: 请求数据（会被过滤敏感信息）
            response_data: 响应数据（会被过滤敏感信息）
            status: 操作状态（success/failed）
            error_message: 错误信息
            before_state: 操作前状态（用于配置变更对比）
            after_state: 操作后状态（用于配置变更对比）

        Returns:
            AuditLog: 创建的审计日志记录
        """
        # 过滤敏感信息
        filtered_request_data = self._filter_sensitive_data(request_data) if request_data else None
        filtered_response_data = (
            self._filter_sensitive_data(response_data) if response_data else None
        )
        filtered_before_state = (
            self._filter_sensitive_data(before_state) if before_state else None
        )
        filtered_after_state = (
            self._filter_sensitive_data(after_state) if after_state else None
        )

        # 创建审计日志记录
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            request_data=filtered_request_data,
            response_data=filtered_response_data,
            status=status,
            error_message=error_message,
            created_at=datetime.utcnow(),
        )

        # 如果有操作前后状态，存储到 extra_data 字段（需要扩展模型）
        if before_state or after_state:
            extra_data = {}
            if filtered_before_state:
                extra_data["before_state"] = filtered_before_state
            if filtered_after_state:
                extra_data["after_state"] = filtered_after_state
            audit_log.request_data = (
                filtered_request_data if filtered_request_data else {}
            ) | extra_data

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        logger.debug(
            f"Audit log created: id={audit_log.id}, user_id={user_id}, "
            f"action={action.value}, resource_type={resource_type}"
        )

        return audit_log

    def query_logs(
        self,
        user_id: Optional[int] = None,
        action: Optional[AuditAction] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[AuditLog], int]:
        """
        查询审计日志

        Args:
            user_id: 用户 ID（可选）
            action: 操作类型（可选）
            resource_type: 资源类型（可选）
            resource_id: 资源 ID（可选）
            status: 操作状态（可选）
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            keyword: 关键词搜索（可选，搜索 description 和 resource_id）
            page: 页码（从 1 开始）
            page_size: 每页数量
            sort_by: 排序字段（默认 created_at）
            sort_order: 排序顺序（asc/desc，默认 desc）

        Returns:
            Tuple[List[AuditLog], int]: (审计日志列表, 总数)
        """
        query = self.db.query(AuditLog)

        # 应用过滤条件
        if user_id is not None:
            query = query.filter(AuditLog.user_id == user_id)

        if action:
            query = query.filter(AuditLog.action == action)

        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)

        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)

        if status:
            query = query.filter(AuditLog.status == status)

        if start_time:
            query = query.filter(AuditLog.created_at >= start_time)

        if end_time:
            query = query.filter(AuditLog.created_at <= end_time)

        if keyword:
            # 关键词搜索：搜索 description 和 resource_id
            keyword_filter = or_(
                AuditLog.description.ilike(f"%{keyword}%"),
                AuditLog.resource_id.ilike(f"%{keyword}%"),
            )
            query = query.filter(keyword_filter)

        # 获取总数
        total = query.count()

        # 应用排序
        sort_column = getattr(AuditLog, sort_by, AuditLog.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column)
        else:
            query = query.order_by(desc(sort_column))

        # 应用分页
        offset = (page - 1) * page_size
        logs = query.offset(offset).limit(page_size).all()

        return logs, total

    def get_log(self, log_id: int) -> Optional[AuditLog]:
        """
        获取审计日志详情

        Args:
            log_id: 审计日志 ID

        Returns:
            Optional[AuditLog]: 审计日志记录，如果不存在返回 None
        """
        return self.db.query(AuditLog).filter(AuditLog.id == log_id).first()

    def get_stats(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        获取审计统计信息

        Args:
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）

        Returns:
            Dict[str, Any]: 统计信息字典
        """
        query = self.db.query(AuditLog)

        # 应用时间过滤
        if start_time:
            query = query.filter(AuditLog.created_at >= start_time)
        if end_time:
            query = query.filter(AuditLog.created_at <= end_time)

        # 总操作数
        total_operations = query.count()

        # 成功操作数
        success_count = query.filter(AuditLog.status == "success").count()

        # 失败操作数
        failed_count = query.filter(AuditLog.status == "failed").count()

        # 按操作类型统计
        action_stats = (
            query.with_entities(AuditLog.action, func.count(AuditLog.id).label("count"))
            .group_by(AuditLog.action)
            .all()
        )
        action_stats_dict = {action.value: count for action, count in action_stats}

        # 按操作者统计（前 10 名）
        user_stats = (
            query.with_entities(
                AuditLog.user_id, func.count(AuditLog.id).label("count")
            )
            .filter(AuditLog.user_id.isnot(None))
            .group_by(AuditLog.user_id)
            .order_by(desc("count"))
            .limit(10)
            .all()
        )

        # 获取用户名
        user_stats_list = []
        for user_id, count in user_stats:
            user = self.db.query(User).filter(User.id == user_id).first()
            username = user.username if user else f"User {user_id}"
            user_stats_list.append({"user_id": user_id, "username": username, "count": count})

        return {
            "total_operations": total_operations,
            "success_count": success_count,
            "failed_count": failed_count,
            "action_stats": action_stats_dict,
            "user_stats": user_stats_list,
        }

    def get_trends(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        group_by: str = "day",
        action: Optional[AuditAction] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取操作趋势数据

        Args:
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            group_by: 分组方式（hour/day/week/month，默认 day）
            action: 操作类型（可选，用于过滤）

        Returns:
            List[Dict[str, Any]]: 趋势数据列表，每个元素包含时间点和操作数量
        """
        query = self.db.query(AuditLog)

        # 应用时间过滤
        if start_time:
            query = query.filter(AuditLog.created_at >= start_time)
        if end_time:
            query = query.filter(AuditLog.created_at <= end_time)

        # 应用操作类型过滤
        if action:
            query = query.filter(AuditLog.action == action)

        # 根据分组方式构建 SQL 日期格式化
        if group_by == "hour":
            date_format = "%Y-%m-%d %H:00:00"
            sql_format = "TO_CHAR(created_at, 'YYYY-MM-DD HH24:00:00')"
        elif group_by == "day":
            date_format = "%Y-%m-%d"
            sql_format = "TO_CHAR(created_at, 'YYYY-MM-DD')"
        elif group_by == "week":
            date_format = "%Y-W%V"
            sql_format = "TO_CHAR(created_at, 'IYYY-IW')"
        elif group_by == "month":
            date_format = "%Y-%m"
            sql_format = "TO_CHAR(created_at, 'YYYY-MM')"
        else:
            date_format = "%Y-%m-%d"
            sql_format = "TO_CHAR(created_at, 'YYYY-MM-DD')"

        # 使用原生 SQL 进行分组统计（PostgreSQL）
        sql = text(
            f"""
            SELECT {sql_format} as time_point, COUNT(*) as count
            FROM audit_logs
            WHERE 1=1
            {"AND created_at >= :start_time" if start_time else ""}
            {"AND created_at <= :end_time" if end_time else ""}
            {"AND action = :action" if action else ""}
            GROUP BY time_point
            ORDER BY time_point
            """
        )

        params = {}
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if action:
            params["action"] = action.value

        result = self.db.execute(sql, params)
        trends = [
            {"time_point": row[0], "count": row[1]} for row in result.fetchall()
        ]

        return trends

    def export_logs(
        self,
        format: str = "csv",
        user_id: Optional[int] = None,
        action: Optional[AuditAction] = None,
        resource_type: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> str:
        """
        导出审计日志

        Args:
            format: 导出格式（csv/json）
            user_id: 用户 ID（可选）
            action: 操作类型（可选）
            resource_type: 资源类型（可选）
            status: 操作状态（可选）
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）

        Returns:
            str: 导出的数据（CSV 或 JSON 字符串）
        """
        # 查询日志（不分页，获取所有匹配的记录）
        logs, _ = self.query_logs(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            status=status,
            start_time=start_time,
            end_time=end_time,
            page=1,
            page_size=10000,  # 最大导出 10000 条
        )

        if format.lower() == "csv":
            return self._export_csv(logs)
        elif format.lower() == "json":
            return self._export_json(logs)
        else:
            raise ValueError(f"不支持的导出格式: {format}")

    def _filter_sensitive_data(self, data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        过滤敏感数据

        Args:
            data: 原始数据字典

        Returns:
            Optional[Dict[str, Any]]: 过滤后的数据字典
        """
        if not data:
            return data

        filtered = {}
        for key, value in data.items():
            # 检查键名是否包含敏感字段
            key_lower = key.lower()
            is_sensitive = any(
                sensitive_field in key_lower for sensitive_field in self.SENSITIVE_FIELDS
            )

            if is_sensitive:
                # 如果是敏感字段，只记录字段名，不记录值
                filtered[key] = "***FILTERED***"
            elif isinstance(value, dict):
                # 递归处理嵌套字典
                filtered[key] = self._filter_sensitive_data(value)
            elif isinstance(value, list):
                # 处理列表
                filtered[key] = [
                    self._filter_sensitive_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                filtered[key] = value

        return filtered

    def _export_csv(self, logs: List[AuditLog]) -> str:
        """
        导出为 CSV 格式

        Args:
            logs: 审计日志列表

        Returns:
            str: CSV 字符串
        """
        output = StringIO()
        writer = csv.writer(output)

        # 写入表头
        writer.writerow(
            [
                "ID",
                "用户 ID",
                "操作类型",
                "资源类型",
                "资源 ID",
                "描述",
                "IP 地址",
                "状态",
                "错误信息",
                "创建时间",
            ]
        )

        # 写入数据
        for log in logs:
            writer.writerow(
                [
                    log.id,
                    log.user_id or "",
                    log.action.value,
                    log.resource_type,
                    log.resource_id or "",
                    log.description or "",
                    log.ip_address or "",
                    log.status or "",
                    log.error_message or "",
                    log.created_at.isoformat() if log.created_at else "",
                ]
            )

        return output.getvalue()

    def _export_json(self, logs: List[AuditLog]) -> str:
        """
        导出为 JSON 格式

        Args:
            logs: 审计日志列表

        Returns:
            str: JSON 字符串
        """
        log_list = []
        for log in logs:
            log_dict = {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action.value,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "description": log.description,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "status": log.status,
                "error_message": log.error_message,
                "request_data": log.request_data,
                "response_data": log.response_data,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            log_list.append(log_dict)

        return json.dumps(log_list, ensure_ascii=False, indent=2)

