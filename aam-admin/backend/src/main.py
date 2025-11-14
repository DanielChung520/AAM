"""
@purpose: FastAPI 应用入口文件，包含基础路由、健康检查和异常处理
@author: Daniel Chung
@createdAt: 2025-01-01
@lastModified: 2025-01-14
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import get_settings

# 配置结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    应用程序生命周期管理
    处理启动和关闭事件
    """
    # 启动事件
    logger.info(
        "应用程序启动",
        app_name=settings.app.app_name,
        version=settings.app.app_version,
        debug=settings.app.debug,
    )

    # TODO: 初始化数据库连接
    # TODO: 初始化 Docker 客户端
    # TODO: 初始化其他服务

    yield

    # 关闭事件
    logger.info("应用程序关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.app.app_name,
    version=settings.app.app_version,
    description="AAM 管理系统后端 API",
    debug=settings.app.debug,
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins if not settings.app.debug else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 审计中间件（需要在 CORS 之后，认证之前）
from src.api.middleware.audit_middleware import AuditMiddleware

app.add_middleware(AuditMiddleware)


# 异常处理中间件
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    logger.error(
        "未处理的异常",
        exc_info=exc,
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "内部服务器错误",
            "detail": str(exc) if settings.app.debug else "请联系系统管理员",
        },
    )


# 健康检查端点
@app.get("/health", tags=["健康检查"])
async def health_check() -> dict[str, str]:
    """
    健康检查端点
    用于 Kubernetes/Docker 健康检查
    """
    return {
        "status": "healthy",
        "service": settings.app.app_name,
        "version": settings.app.app_version,
    }


# 根端点
@app.get("/", tags=["根"])
async def root() -> dict[str, str]:
    """根端点"""
    return {
        "service": settings.app.app_name,
        "version": settings.app.app_version,
        "docs": "/docs",
        "health": "/health",
    }


# 注册路由
from src.api.routers import auth, dashboard, llm_provider, logs, service, security, version, deployment, audit, settings
from src.api.websocket import logs as ws_logs

app.include_router(auth.router, prefix=settings.api.api_prefix)
app.include_router(dashboard.router, prefix=settings.api.api_prefix)
app.include_router(llm_provider.router, prefix=settings.api.api_prefix)
app.include_router(service.router, prefix=settings.api.api_prefix)
app.include_router(logs.router, prefix=settings.api.api_prefix)
app.include_router(security.router, prefix=settings.api.api_prefix)
app.include_router(version.router, prefix=settings.api.api_prefix + "/admin")
app.include_router(deployment.router, prefix=settings.api.api_prefix + "/admin")
app.include_router(audit.router, prefix=settings.api.api_prefix + "/admin")
app.include_router(settings.router, prefix=settings.api.api_prefix + "/admin")
app.include_router(ws_logs.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api.api_host,
        port=settings.api.api_port,
        reload=settings.app.debug,
        log_level=settings.app.log_level.lower(),
    )
