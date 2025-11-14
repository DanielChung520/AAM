# 批次六：API 控制器實施計劃

**創建日期**: 2025-11-12  
**版本**: v1.0  
**狀態**: 已批准，已實施  
**前置依賴**: 批次四（業務邏輯層實現）已完成

---

## 計劃概述

根據 `AAM Agent SD v1.md` 的規範和 `AAM 服務第一階段 MVP 實施計劃.md`，完成批次六的 API 控制器層實現。本批次實現 `MCPEnrichmentController`、依賴注入配置和路由註冊，完成 `POST /v1/mcp/enrich` 端點，並實現 API Key 認證機制。

---

## 任務清單

### 任務 6.1：MCP 控制器實現

**文件**: `src/api/controllers/mcp_controller.py`

**任務內容**:

- [x] 創建 `MCPEnrichmentController` 類
  - 遵循「輕薄」原則，僅負責 HTTP 請求/響應處理
  - 通過構造函數接收 `IMemoryService` 依賴注入
- [x] 實現 `POST /v1/mcp/enrich` 端點
  - 使用 FastAPI 路由裝飾器
  - 請求體類型：`PartialMCP`（FastAPI 自動驗證）
  - 調用 `memory_service.enrich(mcp)` 方法
  - 返回 `EnrichedMCP` 響應
  - 添加結構化日誌記錄（request_id, user_id, session_id）
  - 實現異常處理（返回適當的 HTTP 狀態碼）
- [x] 添加 API Key 認證依賴
  - 使用 FastAPI `Depends` 機制
  - 驗證 `X-API-KEY` header
  - 與配置中的 `API_KEY` 進行比對
  - 認證失敗返回 401 Unauthorized

**參考規範**：
- SD 文件 3.1.2 節（同步 API 規格）
- SD 文件 8.1 節（API 控制器規範）
- SD 文件 8.3.1 節（組件實現指南）

---

### 任務 6.2：依賴注入配置

**文件**: `src/api/dependencies/__init__.py`

**任務內容**:

- [x] 實現服務實例創建函數
  - `get_memory_service()`: 返回 `IMemoryService` 實例
  - 從應用生命週期（lifespan）中獲取已初始化的服務實例
  - 或創建新的服務實例（使用全局配置）
- [x] 實現 FastAPI `Depends` 配置
  - 使用 FastAPI 的依賴注入機制
  - 確保服務實例的單例模式或適當的生命週期管理
- [x] 處理服務初始化邏輯
  - 從 `main.py` 的 `lifespan` 函數中獲取已創建的服務
  - 或獨立創建服務實例（需要初始化數據庫連接等）

**參考規範**：
- SD 文件 8.1 節（依賴倒置原則）
- SD 文件 8.3.2 節（業務邏輯層規範）

**實現方案**:
- **方案 A（已採用）**: 使用 FastAPI 的 `app.state` 存儲服務實例
  - 在 `lifespan` 中將服務存儲到 `app.state.memory_service`
  - 在 `dependencies.py` 中從 `app.state` 獲取

---

### 任務 6.3：路由註冊

**文件**: `src/main.py`

**任務內容**:

- [x] 導入 MCP 控制器路由
  - `from src.api.controllers.mcp_controller import router as mcp_router`
- [x] 註冊 MCP 路由到 FastAPI 應用
  - 使用 `app.include_router()` 方法
  - 配置 API 前綴：`/v1/mcp`
  - 配置標籤：`tags=["MCP"]`
- [x] 移除註釋掉的舊代碼（如果存在）
  - 清理第 242-243 行的註釋代碼

**參考規範**：
- SD 文件 3.1.2 節（端點路徑：`POST /v1/mcp/enrich`）

---

## 驗收標準

### 功能驗收

- [x] `POST /v1/mcp/enrich` 端點正常工作
  - 接收 `PartialMCP` 請求體
  - 返回 `EnrichedMCP` 響應體
  - 正確調用 `MemoryServiceImpl.enrich()` 方法
- [x] API Key 認證正常工作
  - 缺少 `X-API-KEY` header 時返回 401
  - API Key 錯誤時返回 401
  - API Key 正確時允許訪問
- [x] 路由註冊正確
  - 端點可通過 `/v1/mcp/enrich` 訪問
  - Swagger UI 中顯示正確的路由文檔

### 代碼質量驗收

- [x] 控制器保持「輕薄」
  - 不包含業務邏輯
  - 僅負責 HTTP 請求/響應處理
- [x] 符合 SD 文件規範
  - 遵循協議優先原則（使用 Pydantic 模型）
  - 遵循抽象驅動原則（依賴接口而非實現）
  - 遵循配置化原則（API Key 從配置讀取）
- [x] 代碼包含標準頭部註釋
  - 符合 `AiDevelopmentGuide.md` 規範
- [x] 通過類型檢查（mypy）
- [x] 通過代碼格式檢查（black, isort）

### 性能驗收

- [x] 符合性能目標（P95 < 500ms）
  - 端點響應時間符合要求
  - 不引入額外的性能瓶頸

### 測試驗收

- [x] 單元測試
  - 測試控制器邏輯（使用 Mock）
  - 測試 API Key 認證
  - 測試異常處理
- [x] 整合測試
  - 測試完整的 API 端點（使用測試客戶端）
  - 測試與 `MemoryServiceImpl` 的集成
- [x] 測試覆蓋率 > 80%

---

## 實施步驟

### 步驟 1：創建依賴注入配置 ✅

1. 創建 `src/api/dependencies/__init__.py` 文件
2. 實現 `get_memory_service()` 函數
3. 實現服務實例獲取邏輯（從 `app.state` 或創建新實例）

### 步驟 2：實現 MCP 控制器 ✅

1. 創建 `src/api/controllers/mcp_controller.py` 文件
2. 實現 `verify_api_key()` 認證依賴函數
3. 實現 `enrich_mcp()` 端點函數
4. 添加結構化日誌記錄
5. 添加異常處理

### 步驟 3：註冊路由 ✅

1. 修改 `src/main.py` 文件
2. 導入 MCP 控制器路由
3. 註冊路由到 FastAPI 應用
4. 清理註釋代碼

### 步驟 4：更新應用生命週期 ✅

1. 修改 `src/main.py` 的 `lifespan` 函數
2. 將 `memory_service` 存儲到 `app.state`
3. 添加日誌記錄

### 步驟 5：編寫測試 ✅

1. 創建 `tests/unit/test_mcp_controller.py`
2. 創建 `tests/integration/test_mcp_api.py`
3. 運行測試並確保通過

### 步驟 6：驗收測試 ✅

1. 啟動服務並測試 API 端點
2. 驗證 API Key 認證
3. 驗證響應格式和內容
4. 性能測試（可選）

---

## 技術細節

### API Key 認證實現

**方案**: 使用 FastAPI `Depends` 機制

```python
from fastapi import Header, HTTPException
from src.config.settings import get_settings

async def verify_api_key(x_api_key: str = Header(..., alias="X-API-KEY")) -> str:
    """驗證 API Key"""
    settings = get_settings()
    if x_api_key != settings.api.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key"
        )
    return x_api_key
```

### 服務實例獲取

**方案 A（已採用）**: 使用 `app.state`

在 `main.py` 的 `lifespan` 中：
```python
app.state.memory_service = memory_service
```

在 `dependencies/__init__.py` 中：
```python
from fastapi import Request

def get_memory_service(request: Request) -> IMemoryService:
    return request.app.state.memory_service
```

### 錯誤處理

- 使用 FastAPI 的 `HTTPException`
- 記錄結構化日誌（包含 request_id）
- 返回適當的 HTTP 狀態碼

---

## 風險與注意事項

### 風險

1. **服務實例生命週期管理**
   - 確保服務實例在應用啟動時正確初始化
   - 確保依賴注入正確獲取服務實例

2. **API Key 安全性**
   - API Key 必須從環境變量讀取，不得硬編碼
   - 生產環境必須使用強隨機 API Key

3. **性能影響**
   - API Key 驗證不應引入明顯延遲
   - 控制器層應保持輕量級

### 注意事項

1. 遵循「輕薄控制器」原則，業務邏輯應在 `MemoryServiceImpl` 中
2. 確保所有異常都被正確處理和記錄
3. 確保 API 文檔（Swagger UI）正確生成

---

## 參考文檔

- `docs/AAM Agent SD v1.md` - 系統設計規格
- `docs/AiDevelopmentGuide.md` - 開發規範
- `docs/plan/AAM 服務第一階段 MVP 實施計劃.md` - 總體實施計劃
- `src/core/services/memory_service.py` - 業務邏輯層實現
- `src/models/api/mcp.py` - MCP 數據模型定義

---

## 後續任務

完成本批次後，可以進行：
- API 端點測試和驗證
- 性能優化（如需要）
- 文檔更新（API 文檔）

---

**最後更新**: 2025-11-12

