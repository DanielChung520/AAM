"""
@purpose: FastAPI 依賴注入配置，提供服務實例的獲取函數
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
from fastapi import Request

from src.core.interfaces.i_memory_service import IMemoryService


def get_memory_service(request: Request) -> IMemoryService:
    """
    獲取記憶服務實例
    
    從 FastAPI 應用的 state 中獲取已初始化的記憶服務實例。
    該服務實例在應用啟動時（lifespan）被創建並存儲到 app.state 中。
    
    Args:
        request: FastAPI 請求對象，用於訪問應用狀態
        
    Returns:
        IMemoryService: 記憶服務實例
        
    Raises:
        RuntimeError: 如果服務實例未初始化
    """
    memory_service = getattr(request.app.state, "memory_service", None)
    if memory_service is None:
        raise RuntimeError(
            "記憶服務未初始化。請確保應用已正確啟動，並且 lifespan 函數已執行。"
        )
    return memory_service

