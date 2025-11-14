# MCP Server 安全實現文檔

## 概述

本文檔描述了 AAM 服務中 MCP Server 的安全實現，包括 JWT token 發行、驗證機制和安全中間件。

## 安全設計原則

### 1. 雙層安全認證架構

AAM 服務採用**雙層安全認證架構**，確保服務器間和用戶級別的安全：

1. **企業級認證（服務器間相互認證）**
   - 用於 SmartQ 等企業 GAI 系統與 AAM 服務之間的認證
   - 使用企業 Secret Key 進行 HMAC-SHA256 簽名驗證
   - 在系統部署時由雙方協議配置
   - 防止未授權的服務器訪問

2. **用戶級認證（用戶身份驗證）**
   - 用於驗證具體用戶的身份和權限
   - 使用 JWT token 進行驗證
   - 確保 user_id 和 token 的綁定關係

### 2. 簡化原則
- 用戶權限管理在外部系統，AAM 只負責 token 驗證
- AAM 發行 JWT token，包含 user_id 信息
- 驗證邏輯：驗證 user_id 存在且 token 是 AAM 發行的有效 token

### 3. 嚴格管制
- 確保 user_id 和 token 的綁定關係
- 防止越權訪問（用戶 A 的 token 不能訪問用戶 B 的數據）
- 確保只有授權的企業系統（如 SmartQ）可以訪問 AAM 服務

## 核心組件

### 1. TokenService (`src/core/services/token_service.py`)

負責 JWT token 的發行、驗證和 user_id 提取。

#### 主要方法：

- **`issue_token(user_id: str) -> str`**
  - 發行 JWT token
  - 包含 user_id、iss（發行者）、iat（發行時間）、exp（過期時間）
  - 使用 HS256 算法和 SECRET_KEY 簽名

- **`verify_token(token: str, user_id: str) -> bool`**
  - 驗證 JWT token
  - 檢查 token 格式、簽名、過期時間
  - 驗證 token 中的 user_id 與請求的 user_id 匹配

- **`extract_user_id(token: str) -> Optional[str]`**
  - 從 token 中提取 user_id（不驗證簽名，僅用於提取）

### 2. AuthMiddleware (`src/mcp_server/auth_middleware.py`)

MCP Server 安全中間件，負責企業級認證、token 驗證和 user_id 匹配驗證。

#### 主要方法：

- **`verify_request(token: Optional[str], user_id: str, enterprise_signature: Optional[str] = None) -> tuple[bool, Optional[str]]`**
  - 驗證 MCP 請求（雙層認證）
  - 步驟 1：企業級認證（如果啟用）
    - 驗證企業 Secret Key 簽名（HMAC-SHA256）
  - 步驟 2：用戶級認證
    - 檢查 token 是否存在
    - 驗證 token 有效性
    - 驗證 user_id 和 token 的綁定關係

- **`generate_enterprise_signature(user_id: str, token: Optional[str] = None) -> str`**
  - 生成企業級簽名（HMAC-SHA256）
  - 用於測試或客戶端實現參考

- **`_verify_enterprise_signature(signature: str, user_id: str, token: Optional[str]) -> bool`**
  - 驗證企業級簽名
  - 使用安全比較防止時間攻擊

### 3. MCPServer (`src/mcp_server/server.py`)

MCP Server 實現，提供以下工具：

- **`enrich_context`**: 檢索 ChromaDB 知識庫並豐富化上下文（需要 token 驗證）
- **`archive_dialogue`**: 歸檔對話消息到知識庫（需要 token 驗證）
- **`issue_token`**: 發行 token（用於測試或管理）

### 4. TokenController (`src/api/controllers/token_controller.py`)

Token 管理 API，提供以下端點：

- **`POST /v1/tokens/issue`**: 發行 token（需要 API Key 認證）
- **`POST /v1/tokens/verify`**: 驗證 token（用於測試）

## Token 結構

```json
{
  "user_id": "user_123",
  "iss": "aam-agent",
  "iat": 1234567890,
  "exp": 1234654290
}
```

## 驗證流程（雙層認證）

```
步驟 1: 企業級認證（如果啟用）
  1. 檢查是否啟用企業級認證
  2. 如果啟用，檢查是否有企業簽名
  3. 驗證企業簽名（HMAC-SHA256）
     - 計算期望簽名：HMAC-SHA256(ENTERPRISE_SECRET_KEY, user_id + token)
     - 與提供的簽名進行安全比較

步驟 2: 用戶級認證
  1. 提取 token 和 user_id
  2. 驗證 token 格式
  3. 驗證 token 簽名（使用 SECRET_KEY）
  4. 驗證 token 未過期
  5. 驗證 token 中的 user_id 與請求的 user_id 匹配

步驟 3: 執行業務邏輯
  6. 雙層認證都通過後，執行業務邏輯
```

## 配置項

在 `SecuritySettings` 中新增以下配置：

**用戶級認證配置**：
- `TOKEN_EXPIRE_HOURS=24`: Token 有效期（小時）
- `TOKEN_ISSUER=aam-agent`: Token 發行者標識
- `ENABLE_USER_ID_VALIDATION=true`: 是否啟用 user_id 驗證

**企業級認證配置**：
- `ENTERPRISE_SECRET_KEY=<企業 Secret Key>`: 企業 Secret Key（用於服務器間相互認證，如 SmartQ）
- `ENABLE_ENTERPRISE_AUTH=true`: 是否啟用企業級認證（服務器間相互認證）

## 安全最佳實踐

1. **Token 存儲**：不在日誌中記錄完整 token，只記錄前 8 位
2. **Token 傳輸**：使用 HTTPS（生產環境）
3. **企業級認證**：
   - 在部署前由雙方協議 ENTERPRISE_SECRET_KEY
   - 使用強隨機密鑰生成器生成企業 Secret Key
   - 不同企業使用不同的 Secret Key
   - 定期輪換企業 Secret Key
   - 不在日誌中記錄企業簽名
   - 使用 HMAC-SHA256 進行簽名（防止時間攻擊）
4. **審計日誌**：記錄所有安全相關事件（區分企業級和用戶級認證失敗）
5. **錯誤處理**：不洩露敏感信息（如 token 簽名密鑰、企業 Secret Key）

## 使用示例

### 發行 Token

```python
from src.core.services.token_service import TokenService

token_service = TokenService()
token = token_service.issue_token("user_123")
```

### 驗證 Token

```python
is_valid = token_service.verify_token(token, "user_123")
```

### MCP Server 使用

```python
from src.mcp_server.server import MCPServer
from src.core.services.token_service import TokenService
from src.core.services.memory_service import MemoryServiceImpl

token_service = TokenService()
memory_service = MemoryServiceImpl(...)
mcp_server = MCPServer(memory_service, token_service)
await mcp_server.run()
```

## 測試

### 單元測試

- `tests/unit/test_token_service.py`: Token 服務單元測試
  - Token 發行測試
  - Token 驗證測試（有效 token）
  - Token 驗證測試（過期 token）
  - Token 驗證測試（無效簽名）
  - User ID 匹配測試（正確）
  - User ID 匹配測試（不匹配 - 越權訪問）

### 集成測試

- `tests/integration/test_mcp_server_security.py`: MCP Server 安全集成測試
  - MCP Server 啟動測試
  - Token 驗證中間件測試
  - 越權訪問防護測試
  - Token 過期處理測試

## 注意事項

1. **MCP 協議限制**：MCP 協議可能不支持直接在請求中傳遞 token，需要查看 MCP SDK 文檔確定最佳方式
2. **向後兼容**：保持現有 HTTP API 的兼容性
3. **企業級認證部署**：
   - 在部署前，AAM 服務和 SmartQ 服務的管理員必須協議 ENTERPRISE_SECRET_KEY
   - 雙方必須配置相同的 ENTERPRISE_SECRET_KEY
   - 生產環境建議啟用企業級認證（ENABLE_ENTERPRISE_AUTH=true）
   - 開發環境可以關閉企業級認證以便測試
4. **性能考慮**：Token 驗證和企業簽名驗證不應顯著影響性能
5. **測試覆蓋**：確保安全測試覆蓋所有邊界情況（包括企業級認證失敗場景）

## 修訂歷史

| 版本 | 修改日期 | 修改者 | 修改內容摘要 |
|------|---------|--------|------------|
| v1.0 | 2025-11-13 | Daniel Chung + AI | 初始創建文檔 |

