"""
@purpose: MCP 豐富化控制器，提供 POST /v1/mcp/enrich 端點，負責 HTTP 請求/響應處理
@author: Daniel Chung + AI
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, status

from src.api.dependencies import get_memory_service
from src.config.settings import get_settings
from src.core.interfaces.i_memory_service import IMemoryService
from src.models.api.mcp import EnrichedMCP, PartialMCP

# 配置結構化日誌
logger = structlog.get_logger(__name__)

# 創建路由器
router = APIRouter()


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-KEY")) -> str:
    """
    API Key 認證依賴函數
    
    驗證請求頭中的 X-API-KEY 是否與配置中的 API_KEY 匹配。
    如果驗證失敗，拋出 401 Unauthorized 異常。
    
    Args:
        x_api_key: 從請求頭 X-API-KEY 中提取的 API Key
        
    Returns:
        str: 驗證通過的 API Key
        
    Raises:
        HTTPException: 當 API Key 無效或缺失時，返回 401 狀態碼
    """
    settings = get_settings()
    if x_api_key != settings.api.api_key:
        logger.warning(
            "API Key 驗證失敗",
            provided_key=x_api_key[:8] + "..." if len(x_api_key) > 8 else "***",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return x_api_key


@router.post("/enrich", response_model=EnrichedMCP, status_code=status.HTTP_200_OK)
async def enrich_mcp(
    mcp: PartialMCP,
    memory_service: IMemoryService = Depends(get_memory_service),
    api_key: str = Depends(verify_api_key),
) -> EnrichedMCP:
    """
    豐富化 MCP 端點
    
    接收部分 MCP（PartialMCP）請求，調用記憶服務進行豐富化處理，
    返回包含檢索知識和用戶畫像的豐富化 MCP（EnrichedMCP）。
    
    此端點遵循「輕薄控制器」原則，僅負責 HTTP 請求/響應處理，
    所有業務邏輯都在 MemoryServiceImpl 中實現。
    
    Args:
        mcp: 部分 MCP 請求體（由 FastAPI 自動驗證）
        memory_service: 記憶服務實例（通過依賴注入獲取）
        api_key: API Key（通過依賴注入驗證）
        
    Returns:
        EnrichedMCP: 豐富化後的 MCP 響應體
        
    Raises:
        HTTPException: 當業務邏輯處理失敗時，返回適當的 HTTP 狀態碼
    """
    user_id = mcp.user_profile.user_id
    session_id = mcp.session_context.session_id
    query = mcp.session_context.current_query
    
    logger.info(
        "收到 MCP 豐富化請求",
        user_id=user_id,
        session_id=session_id,
        query_preview=query[:50] + "..." if len(query) > 50 else query,
    )
    
    try:
        # 調用業務邏輯層進行豐富化處理
        enriched_mcp = await memory_service.enrich(mcp)
        
        # 記錄成功日誌
        logger.info(
            "MCP 豐富化成功",
            user_id=user_id,
            session_id=session_id,
            request_id=str(enriched_mcp.metadata.request_id),
            docs_count=len(enriched_mcp.retrieved_knowledge.docs),
            kg_triples_count=len(enriched_mcp.retrieved_knowledge.kg_triples),
        )
        
        return enriched_mcp
        
    except Exception as e:
        # 記錄錯誤日誌
        logger.error(
            "MCP 豐富化處理失敗",
            user_id=user_id,
            session_id=session_id,
            error=str(e),
            exc_info=e,
        )
        
        # 根據異常類型返回適當的 HTTP 狀態碼
        # 如果是業務邏輯層已經處理的異常，直接重新拋出
        if isinstance(e, HTTPException):
            raise e
        
        # 其他未預期的異常，返回 500 錯誤
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="處理 MCP 豐富化請求時發生內部錯誤",
        )

