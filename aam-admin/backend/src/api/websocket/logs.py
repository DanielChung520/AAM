"""
@purpose: WebSocket 日志端点，提供实时日志流
@author: Daniel Chung
@createdAt: 2025-01-14
@lastModified: 2025-01-14
"""

import asyncio
import json
import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from src.core.services.log_service import LogService
from src.core.services.docker_service import DockerService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/logs/{container_name}")
async def websocket_logs(
    websocket: WebSocket,
    container_name: str,
    since: Optional[str] = Query(None, description="开始时间（ISO 格式）"),
    until: Optional[str] = Query(None, description="结束时间（ISO 格式）"),
    filter_level: Optional[str] = Query(None, description="日志级别过滤"),
    filter_text: Optional[str] = Query(None, description="文本过滤"),
):
    """
    WebSocket 日志流端点，支持暂停/恢复功能

    Args:
        websocket: WebSocket 连接
        container_name: 容器名称
        since: 开始时间
        until: 结束时间
        filter_level: 日志级别过滤
        filter_text: 文本过滤
    """
    await websocket.accept()
    logger.info(f"WebSocket connection established for container: {container_name}")

    try:
        # 创建 Docker 和日志服务
        docker_service = DockerService()
        log_service = LogService(docker_service)

        # 控制变量
        paused = False
        log_queue = asyncio.Queue()

        # 日志流任务
        async def log_stream_task():
            """日志流任务"""
            try:
                async for log_line in log_service.stream_logs(
                    container_name=container_name,
                    since=since,
                    until=until,
                    filter_level=filter_level,
                    filter_text=filter_text,
                ):
                    if not paused:
                        await log_queue.put(log_line)
                    await asyncio.sleep(0.01)  # 避免 CPU 占用过高
            except Exception as e:
                logger.error(f"Error in log stream task: {e}")
                await log_queue.put(None)  # 发送结束信号

        # 发送任务
        async def send_task():
            """发送任务"""
            while True:
                try:
                    log_line = await asyncio.wait_for(log_queue.get(), timeout=1.0)
                    if log_line is None:
                        break  # 结束信号
                    if not paused:
                        await websocket.send_text(
                            json.dumps({"type": "log", "data": log_line})
                        )
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error sending log: {e}")
                    break

        # 启动任务
        stream_task = asyncio.create_task(log_stream_task())
        send_task_obj = asyncio.create_task(send_task())

        # 处理客户端消息（暂停/恢复控制）
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                data = json.loads(message)
                if data.get("type") == "pause":
                    paused = True
                    await websocket.send_text(json.dumps({"type": "paused"}))
                elif data.get("type") == "resume":
                    paused = False
                    await websocket.send_text(json.dumps({"type": "resumed"}))
            except asyncio.TimeoutError:
                continue
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error handling client message: {e}")
                break

        # 清理任务
        stream_task.cancel()
        send_task_obj.cancel()
        try:
            await stream_task
        except asyncio.CancelledError:
            pass
        try:
            await send_task_obj
        except asyncio.CancelledError:
            pass

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for container: {container_name}")
    except Exception as e:
        logger.error(f"WebSocket error for container {container_name}: {e}")
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
