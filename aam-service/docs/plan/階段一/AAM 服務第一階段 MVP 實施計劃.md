# AAM 服務第一階段 MVP 實施計劃

**創建日期**: 2025-11-12  
**版本**: v1.0  
**狀態**: 已批准，準備實施

---

## 計劃概述

根據 `AAM Agent SD v1.md` 的規範，分批次完成第一階段 MVP（記憶寫入管道）的缺失組件。每個批次都是可獨立驗證的模塊，確保代碼質量和架構一致性。

---

## 批次一：數據協議定義（Protocol Definition）

### 目標
定義所有核心數據結構，為後續開發提供基礎。

### 任務清單

#### 1.1 MCP 協議模型（`src/models/api/mcp.py`）
- [ ] 定義 `UserProfile` 模型
  - `user_id: str`
- [ ] 定義 `SessionContext` 模型
  - `session_id: str`
  - `current_query: str`
  - `short_term_memory: List[Message]`
- [ ] 定義 `Message` 模型（role, content）
- [ ] 定義 `PartialMCP` 模型
  - `user_profile: UserProfile`
  - `session_context: SessionContext`
- [ ] 定義 `Metadata` 模型
  - `request_id: UUID`
  - `aam_version: str`
- [ ] 定義 `RetrievedDoc` 模型
  - `source: str`
  - `content: str`
  - `score: float`
- [ ] 定義 `KnowledgeTriple` 模型
  - `subject: str`
  - `predicate: str`
  - `object: str`
- [ ] 定義 `RetrievedKnowledge` 模型
  - `docs: List[RetrievedDoc]`
  - `kg_triples: List[KnowledgeTriple]`
- [ ] 定義 `EnrichedMCP` 模型
  - `metadata: Metadata`
  - `user_profile: UserProfile`（擴展版）
  - `session_context: SessionContext`
  - `retrieved_knowledge: RetrievedKnowledge`

**參考規範**：SD 文件 4.1 節

#### 1.2 對話歸檔消息模型（`src/models/domain/dialogue.py`）
- [ ] 定義 `DialogueArchiveMessage` 模型
  - `dialog_id: str`
  - `user_id: str`
  - `timestamp: datetime`
  - `turn: int`
  - `user_query: str`
  - `ai_response: str`

**參考規範**：SD 文件 4.2 節

#### 1.3 數據庫 Schema 模型（`src/models/domain/database.py`）
- [ ] 定義 `KnowledgeAsset` 模型（ChromaDB）
  - `user_id: str`
  - `session_id: str`
  - `timestamp: int`
  - `source_type: Literal["dialogue", "document"]`
  - `entities: List[str]`
  - `triples_json: str`
- [ ] 定義 `UserProfile` 模型（PostgreSQL）
  - `user_id: str`
  - `style_tags: Dict[str, int]`
  - `sentiment_history: Dict[str, int]`
  - `last_updated: datetime`

**參考規範**：SD 文件 4.3 節

### 驗收標準
- 所有模型使用 Pydantic BaseModel
- 包含完整的類型註解
- 符合 SD 文件規範
- 通過類型檢查（mypy）

---

## 批次二：抽象接口定義（Interface Layer）✅ 已完成

### 目標
定義所有抽象接口，實現依賴倒置原則。

### 任務清單

#### 2.1 PersonalityInsights 模型（`src/models/domain/personality.py`）
- [x] 定義 `PersonalityInsights` Pydantic 模型
  - `style_tags: Dict[str, int]` - 風格標籤字典
  - `sentiment: str` - 情感狀態
  - `language_patterns: List[str]` - 語言模式列表
  - `confidence_score: float` - 分析置信度分數（0.0-1.0）

**參考規範**：SD 文件 6.2 節類圖

#### 2.2 記憶服務接口（`src/core/interfaces/i_memory_service.py`）
- [x] 定義 `IMemoryService` 抽象類
  - `enrich(mcp: PartialMCP) -> EnrichedMCP`（異步）
  - `archive(message: DialogueArchiveMessage)`（異步）

**參考規範**：SD 文件 6.2 節類圖

#### 2.3 知識庫接口（`src/core/interfaces/i_knowledge_store.py`）
- [x] 定義 `IKnowledgeStore` 抽象類
  - `save(knowledge: KnowledgeAsset)`（異步）
  - `search(query: str, user_id: str, limit: int = 10) -> List[RetrievedDoc]`（異步）

**參考規範**：SD 文件 6.2 節類圖

#### 2.4 用戶畫像接口（`src/core/interfaces/i_persona_store.py`）
- [x] 定義 `IPersonaStore` 抽象類
  - `save_or_update(profile: UserProfileDB)`（異步）
  - `get(user_id: str) -> Optional[UserProfileDB]`（異步）

**參考規範**：SD 文件 6.2 節類圖

#### 2.5 分析模型接口（`src/core/interfaces/i_analysis_model.py`）
- [x] 定義 `IAnalysisModel` 抽象類
  - `extract_knowledge(text: str, user_id: str, session_id: str) -> KnowledgeAsset`（異步）
  - `analyze_personality(text: str) -> PersonalityInsights`（異步）

**參考規範**：SD 文件 6.2 節類圖

#### 2.6 模塊導出更新
- [x] 更新 `src/models/domain/__init__.py`
- [x] 更新 `src/models/__init__.py`
- [x] 更新 `src/core/interfaces/__init__.py`

#### 2.7 單元測試
- [x] 創建 `tests/unit/test_personality_model.py`
- [x] 創建 `tests/unit/test_interfaces.py`

### 驗收標準
- [x] 使用 `abc.ABC` 和 `@abstractmethod`
- [x] 所有方法包含完整的類型註解
- [x] 符合依賴倒置原則
- [x] 通過類型檢查
- [x] 通過單元測試（25/25 通過）

---

## 批次三：數據存取層實現（Data Access Layer）

### 目標
實現 ChromaDB 和 PostgreSQL 的數據存取層。

### 任務清單

#### 3.1 ChromaDB 知識庫實現（`src/infrastructure/database/chroma_knowledge_store.py`）
- [ ] 實現 `ChromaKnowledgeStore` 類
  - 繼承 `IKnowledgeStore`
  - 初始化 ChromaDB 客戶端
  - 實現 `save()` 方法
    - 向量化文本
    - 存儲到 ChromaDB collection
  - 實現 `search()` 方法
    - 混合搜索（向量 + 元數據）
    - 返回相關文檔列表

**參考規範**：SD 文件 3.2 節、5.1 節

#### 3.2 PostgreSQL 用戶畫像實現（`src/infrastructure/database/pg_persona_store.py`）
- [ ] 實現 `PgPersonaStore` 類
  - 繼承 `IPersonaStore`
  - 初始化 SQLAlchemy 連接
  - 實現數據庫表創建（Alembic migration）
  - 實現 `save_or_update()` 方法
  - 實現 `get()` 方法

**參考規範**：SD 文件 3.3 節、5.1 節

#### 3.3 數據庫連接管理（`src/infrastructure/database/__init__.py`）
- [ ] 創建數據庫連接工廠函數
- [ ] 實現連接池管理

### 驗收標準
- 實現 Repository Pattern
- 封裝所有數據庫特定邏輯
- 通過單元測試（使用 Mock）
- 符合 SD 文件規範

---

## 批次四：業務邏輯層實現（Business Logic Layer）

### 目標
實現核心業務邏輯，協調數據存取和 AI 模型。

### 任務清單

#### 4.1 記憶服務實現（`src/core/services/memory_service.py`）
- [ ] 實現 `MemoryServiceImpl` 類
  - 繼承 `IMemoryService`
  - 依賴注入：`IKnowledgeStore`, `IPersonaStore`, `IAnalysisModel`
  - 實現 `enrich()` 方法
    - 並行查詢知識庫和用戶畫像
    - 組裝 EnrichedMCP
  - 實現 `archive()` 方法
    - 調用 AI 模型進行分析
    - 保存知識和用戶畫像

**參考規範**：SD 文件 3.1.2 節、5.1 節、6.2 節

### 驗收標準
- 框架無關（不依賴 FastAPI 或 RabbitMQ）
- 通過依賴注入接收接口實現
- 通過單元測試（使用 Mock）
- 符合業務邏輯規範

---

## 批次五：消息隊列處理（Message Queue Processing）

### 目標
實現 RabbitMQ 消費者，處理對話歸檔消息。

### 任務清單

#### 5.1 RabbitMQ 配置（`src/infrastructure/messaging/rabbitmq_config.py`）
- [ ] 實現連接管理
- [ ] 實現隊列聲明
- [ ] 實現交換機配置

#### 5.2 對話歸檔消費者（`src/infrastructure/messaging/dialogue_consumer.py`）
- [ ] 實現 `DialogueArchiveConsumer` 類
  - 監聽 `aam.dialogue.archive` 隊列
  - 消息驗證（使用 Pydantic）
  - 調用 `MemoryServiceImpl.archive()`
  - 錯誤處理和重試機制

**參考規範**：SD 文件 3.1.1 節、5.1 節

#### 5.3 集成到主應用（`src/main.py`）
- [ ] 在 `lifespan` 中啟動消費者
- [ ] 優雅關閉處理

### 驗收標準
- 正確處理消息驗證
- 實現錯誤處理和日誌記錄
- 通過整合測試
- 符合異步處理規範

---

## 批次六：API 控制器（API Layer）

### 目標
實現 FastAPI 端點，提供 MCP 豐富化 API。

### 任務清單

#### 6.1 MCP 控制器（`src/api/controllers/mcp_controller.py`）
- [ ] 實現 `MCPEnrichmentController`
- [ ] 實現 `POST /v1/mcp/enrich` 端點
  - 請求驗證（FastAPI 自動）
  - 調用 `MemoryServiceImpl.enrich()`
  - 返回 `EnrichedMCP`
  - API Key 認證（`X-API-KEY` header）

**參考規範**：SD 文件 3.1.2 節、5.2 節

#### 6.2 依賴注入配置（`src/api/dependencies.py`）
- [ ] 實現服務實例創建
- [ ] 實現 FastAPI Depends 配置

#### 6.3 路由註冊（`src/main.py`）
- [ ] 註冊 MCP 路由
- [ ] 配置 API 前綴

### 驗收標準
- 控制器保持「輕薄」
- 通過 API 測試
- 符合性能目標（P95 < 500ms）
- 符合 SD 文件規範

---

## 實施原則

1. **協議優先**：所有數據結構使用 Pydantic 模型
2. **抽象驅動**：業務邏輯依賴抽象接口
3. **配置化**：所有配置通過環境變量
4. **測試驅動**：每個批次都包含測試

## 文件組織

- 模型文件：`src/models/api/` 和 `src/models/domain/`
- 接口文件：`src/core/interfaces/`
- 服務文件：`src/core/services/`
- 數據存取：`src/infrastructure/database/`
- 消息隊列：`src/infrastructure/messaging/`
- API 控制器：`src/api/controllers/`

## 驗收標準總覽

- 所有代碼符合 SD 文件規範
- 通過類型檢查（mypy）
- 通過單元測試（pytest）
- 通過整合測試
- 代碼包含標準頭部註釋
- 符合項目開發規範

---

## 實施順序

1. **批次一**：數據協議定義（基礎，無依賴）
2. **批次二**：抽象接口定義（依賴批次一）
3. **批次三**：數據存取層（依賴批次二）
4. **批次四**：業務邏輯層（依賴批次三）
5. **批次五**：消息隊列處理（依賴批次四）
6. **批次六**：API 控制器（依賴批次四）

---

## 進度追蹤

- [x] 批次一：數據協議定義 ✅ 已完成
- [x] 批次二：抽象接口定義 ✅ 已完成
- [ ] 批次三：數據存取層實現
- [ ] 批次四：業務邏輯層實現
- [ ] 批次五：消息隊列處理
- [ ] 批次六：API 控制器

---

**最後更新**: 2025-11-12

