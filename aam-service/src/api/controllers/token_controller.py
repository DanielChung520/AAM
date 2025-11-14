"""
@purpose: Token 管理 API 控制器，提供 token 發行和驗證端點
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from src.config.settings import get_settings
from src.core.services.token_service import TokenService

# 配置結構化日誌
logger = structlog.get_logger(__name__)

# 創建路由器
router = APIRouter()


class IssueTokenRequest(BaseModel):
    """發行 Token 請求模型"""
    user_id: str = Field(..., description="用戶 ID")


class IssueTokenResponse(BaseModel):
    """發行 Token 響應模型"""
    token: str = Field(..., description="JWT token")
    user_id: str = Field(..., description="用戶 ID")
    expires_in_hours: int = Field(..., description="Token 有效期（小時）")


class VerifyTokenRequest(BaseModel):
    """驗證 Token 請求模型"""
    token: str = Field(..., description="JWT token")
    user_id: str = Field(..., description="用戶 ID")


class VerifyTokenResponse(BaseModel):
    """驗證 Token 響應模型"""
    valid: bool = Field(..., description="Token 是否有效")
    user_id: str = Field(..., description="用戶 ID")


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


def get_token_service() -> TokenService:
    """
    獲取 Token 服務實例（依賴注入）
    
    Returns:
        TokenService: Token 服務實例
    """
    return TokenService()


@router.post(
    "/issue",
    response_model=IssueTokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def issue_token(
    request: IssueTokenRequest,
    token_service: TokenService = Depends(get_token_service),
    api_key: str = Depends(verify_api_key),
) -> IssueTokenResponse:
    """
    發行 JWT token 端點
    
    此端點需要 API Key 認證，用於發行 token。
    通常由外部系統調用（外部系統負責用戶權限管理）。
    
    Args:
        request: 發行 Token 請求
        token_service: Token 服務實例（通過依賴注入獲取）
        api_key: API Key（通過依賴注入驗證）
        
    Returns:
        IssueTokenResponse: 發行的 Token 信息
        
    Raises:
        HTTPException: 當請求參數無效時，返回 400 狀態碼
    """
    user_id = request.user_id

    logger.info(
        "收到 Token 發行請求",
        user_id=user_id,
        api_key_prefix=api_key[:8] + "..." if len(api_key) > 8 else "***",
    )

    try:
        # 發行 token
        token = token_service.issue_token(user_id)

        # 獲取配置
        settings = token_service.settings

        # 記錄成功日誌（不記錄完整 token）
        logger.info(
            "Token 發行成功",
            user_id=user_id,
            token_prefix=token[:8] + "...",
            expires_in_hours=settings.token_expire_hours,
        )

        return IssueTokenResponse(
            token=token,
            user_id=user_id,
            expires_in_hours=settings.token_expire_hours,
        )

    except ValueError as e:
        logger.warning(
            "Token 發行失敗：參數無效",
            user_id=user_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        logger.error(
            "Token 發行失敗：內部錯誤",
            user_id=user_id,
            error=str(e),
            exc_info=e,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="發行 Token 時發生內部錯誤",
        )


@router.post(
    "/verify",
    response_model=VerifyTokenResponse,
    status_code=status.HTTP_200_OK,
)
async def verify_token(
    request: VerifyTokenRequest,
    token_service: TokenService = Depends(get_token_service),
    api_key: str = Depends(verify_api_key),
) -> VerifyTokenResponse:
    """
    驗證 JWT token 端點（用於測試）
    
    此端點需要 API Key 認證，用於驗證 token 的有效性。
    
    Args:
        request: 驗證 Token 請求
        token_service: Token 服務實例（通過依賴注入獲取）
        api_key: API Key（通過依賴注入驗證）
        
    Returns:
        VerifyTokenResponse: Token 驗證結果
    """
    token = request.token
    user_id = request.user_id

    logger.info(
        "收到 Token 驗證請求",
        user_id=user_id,
        token_prefix=token[:8] + "..." if len(token) > 8 else "***",
    )

    try:
        # 驗證 token
        is_valid = token_service.verify_token(token, user_id)

        # 記錄驗證結果
        if is_valid:
            logger.info(
                "Token 驗證成功",
                user_id=user_id,
                token_prefix=token[:8] + "...",
            )
        else:
            logger.warning(
                "Token 驗證失敗",
                user_id=user_id,
                token_prefix=token[:8] + "...",
            )

        return VerifyTokenResponse(
            valid=is_valid,
            user_id=user_id,
        )

    except ValueError as e:
        logger.warning(
            "Token 驗證失敗：參數無效",
            user_id=user_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        logger.error(
            "Token 驗證失敗：內部錯誤",
            user_id=user_id,
            error=str(e),
            exc_info=e,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="驗證 Token 時發生內部錯誤",
        )

