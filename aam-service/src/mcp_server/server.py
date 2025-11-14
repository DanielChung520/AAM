"""
@purpose: MCP Server 實現，提供 enrich_context 和 archive_dialogue 工具
@author: Daniel Chung + AI
@createdAt: 2025-11-13
@lastModified: 2025-11-13
"""
import logging
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from src.core.interfaces.i_memory_service import IMemoryService
from src.core.services.token_service import TokenService
from src.mcp_server.auth_middleware import AuthMiddleware
from src.models.api.mcp import PartialMCP, SessionContext, UserProfile
from src.models.domain.dialogue import DialogueArchiveMessage

# 配置日誌
logger = logging.getLogger(__name__)


class MCPServer:
    """MCP Server 實現類"""

    def __init__(
        self,
        memory_service: IMemoryService,
        token_service: TokenService,
    ):
        """
        初始化 MCP Server
        
        Args:
            memory_service: 記憶服務實例
            token_service: Token 服務實例
        """
        self.memory_service = memory_service
        self.token_service = token_service
        self.auth_middleware = AuthMiddleware(token_service)
        self.server = Server("aam-mcp-server")

        # 註冊工具 handlers
        self._register_tools()

    def _register_tools(self) -> None:
        """註冊 MCP 工具 handlers"""
        # 註冊 list_tools handler
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """列出所有可用的工具"""
            return self._get_tools_list()

        # 註冊 call_tool handler
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[dict[str, Any]]:
            """調用工具"""
            return await self._handle_tool_call(name, arguments)

    def _get_tools_list(self) -> list[Tool]:
        """
        獲取所有可用的工具列表
        
        Returns:
            list[Tool]: 工具列表
        """
        return [
            Tool(
                name="enrich_context",
                description="檢索 ChromaDB 知識庫並豐富化上下文",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "用戶 ID",
                        },
                        "session_id": {
                            "type": "string",
                            "description": "會話 ID",
                        },
                        "current_query": {
                            "type": "string",
                            "description": "當前查詢",
                        },
                        "token": {
                            "type": "string",
                            "description": "JWT token（用於驗證）",
                        },
                        "enterprise_signature": {
                            "type": "string",
                            "description": "企業級簽名（HMAC-SHA256，用於服務器間相互認證，可選）",
                        },
                    },
                    "required": ["user_id", "session_id", "current_query", "token"],
                },
            ),
            Tool(
                name="archive_dialogue",
                description="歸檔對話消息到知識庫",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "用戶 ID",
                        },
                        "dialog_id": {
                            "type": "string",
                            "description": "對話 ID",
                        },
                        "user_query": {
                            "type": "string",
                            "description": "用戶查詢",
                        },
                        "ai_response": {
                            "type": "string",
                            "description": "AI 響應",
                        },
                        "turn": {
                            "type": "integer",
                            "description": "對話輪次",
                        },
                        "token": {
                            "type": "string",
                            "description": "JWT token（用於驗證）",
                        },
                        "enterprise_signature": {
                            "type": "string",
                            "description": "企業級簽名（HMAC-SHA256，用於服務器間相互認證，可選）",
                        },
                    },
                    "required": [
                        "user_id",
                        "dialog_id",
                        "user_query",
                        "ai_response",
                        "turn",
                        "token",
                    ],
                },
            ),
            Tool(
                name="issue_token",
                description="發行 JWT token（用於測試或管理）",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "用戶 ID",
                        },
                    },
                    "required": ["user_id"],
                },
            ),
        ]

    async def _handle_tool_call(
        self, name: str, arguments: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        處理工具調用
        
        Args:
            name: 工具名稱
            arguments: 工具參數
            
        Returns:
            list[dict[str, Any]]: 工具執行結果（MCP 格式）
        """
        try:
            if name == "enrich_context":
                result = await self._handle_enrich_context(arguments)
            elif name == "archive_dialogue":
                result = await self._handle_archive_dialogue(arguments)
            elif name == "issue_token":
                result = await self._handle_issue_token(arguments)
            else:
                return [
                    {
                        "type": "text",
                        "text": f"Unknown tool: {name}",
                    }
                ]
            
            # 轉換為 MCP 格式
            if result.get("isError"):
                return [
                    {
                        "type": "text",
                        "text": result.get("error", "Unknown error"),
                    }
                ]
            else:
                return result.get("content", [])
        except Exception as e:
            logger.error(
                f"Error calling tool {name}: {e}",
                exc_info=e,
                extra={"tool_name": name, "arguments": arguments},
            )
            return [
                {
                    "type": "text",
                    "text": f"Error: {str(e)}",
                }
            ]

    async def _handle_enrich_context(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """
        處理 enrich_context 工具調用
        
        Args:
            arguments: 工具參數
            
        Returns:
            dict[str, Any]: 執行結果
        """
        user_id = arguments.get("user_id")
        session_id = arguments.get("session_id")
        current_query = arguments.get("current_query")
        token = arguments.get("token")
        enterprise_signature = arguments.get("enterprise_signature")

        # 驗證請求（包含企業級認證）
        is_valid, error_message = self.auth_middleware.verify_request(
            token, user_id, enterprise_signature
        )
        if not is_valid:
            return {
                "error": error_message,
                "isError": True,
            }

        # 構建 PartialMCP
        mcp = PartialMCP(
            user_profile=UserProfile(user_id=user_id),
            session_context=SessionContext(
                session_id=session_id,
                current_query=current_query,
                short_term_memory=[],
            ),
        )

        # 調用記憶服務
        enriched_mcp = await self.memory_service.enrich(mcp)

        # 返回結果（MCP 格式）
        return {
            "content": [
                {
                    "type": "text",
                    "text": enriched_mcp.model_dump_json(),
                }
            ],
            "isError": False,
        }

    async def _handle_archive_dialogue(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """
        處理 archive_dialogue 工具調用
        
        Args:
            arguments: 工具參數
            
        Returns:
            dict[str, Any]: 執行結果
        """
        user_id = arguments.get("user_id")
        dialog_id = arguments.get("dialog_id")
        user_query = arguments.get("user_query")
        ai_response = arguments.get("ai_response")
        turn = arguments.get("turn")
        token = arguments.get("token")
        enterprise_signature = arguments.get("enterprise_signature")

        # 驗證請求（包含企業級認證）
        is_valid, error_message = self.auth_middleware.verify_request(
            token, user_id, enterprise_signature
        )
        if not is_valid:
            return {
                "error": error_message,
                "isError": True,
            }

        # 構建 DialogueArchiveMessage
        from datetime import datetime

        message = DialogueArchiveMessage(
            dialog_id=dialog_id,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            turn=turn,
            user_query=user_query,
            ai_response=ai_response,
        )

        # 調用記憶服務
        await self.memory_service.archive(message)

        # 返回結果（MCP 格式）
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"對話已成功歸檔: dialog_id={dialog_id}, turn={turn}",
                }
            ],
            "isError": False,
        }

    async def _handle_issue_token(
        self, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """
        處理 issue_token 工具調用
        
        Args:
            arguments: 工具參數
            
        Returns:
            dict[str, Any]: 執行結果
        """
        user_id = arguments.get("user_id")

        if not user_id:
            return {
                "error": "user_id 不能為空",
                "isError": True,
            }

        # 發行 token
        token = self.token_service.issue_token(user_id)

        # 返回結果（MCP 格式，包含 token）
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Token issued successfully for user_id={user_id}, "
                    f"token_prefix={token[:8]}...\nToken: {token}",
                }
            ],
            "isError": False,
        }

    async def run(self) -> None:
        """
        運行 MCP Server（使用 stdio）
        
        注意：此方法會阻塞，直到服務停止
        """
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )

