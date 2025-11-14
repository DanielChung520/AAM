# AAM (AI-Augmented Memory) Service

**版本**: 1.0.0  
**狀態**: Phase I 已完成 (70%)，Phase II 規劃中  
**最後更新**: 2025-11-12

---

## 📋 項目簡介

AAM Service 是一個獨立的微服務，旨在為任何上層應用（如 SmartQ）提供強大的長期記憶和上下文豐富化能力。系統遵循異步解耦的微服務架構，將實時交互與後台學習分離，以確保高性能、高可用性和可擴展性。

### 核心能力

- **長期記憶存儲**: 使用向量數據庫 (ChromaDB) 存儲對話和知識
- **用戶畫像管理**: 使用 PostgreSQL 存儲用戶個性化偏好
- **語義分析**: 多層級降級策略的語義分析（Eb-MM → LangChain Embedding → LLM）
- **異步處理**: 通過 RabbitMQ 異步處理對話歸檔
- **上下文豐富化**: 通過 MCP (Model Context Protocol) 提供豐富的上下文信息

---

## 🏗️ 系統架構

### 核心組件

- **即時互動子系統**: 處理同步、低延遲的對話交互
- **AAM 異步代理子系統**: 作為系統的「認知後台」，負責異步地、深度地處理對話信息

### 三大支柱

1. **短期工作記憶**: 由 LLM 的上下文視窗提供
2. **長期情景記憶**: 由 AAM 模組提供，通過向量資料庫儲存
3. **個性化模型**: 由 Eb-MM 提供，分析用戶的語言習慣和情感

### 開發階段

- **Phase I (MVP)**: ✅ 已完成 70%
  - 基礎架構、數據協議、接口層、API層、數據存取層、消息隊列處理、測試實現
- **Phase II (語義分析)**: 📋 規劃中
  - 降級策略框架、LangChain Embedding、LLM 降級層、Eb-MM 模型集成

---

## 🚀 快速開始

### 前置要求

- Docker & Docker Compose
- Python 3.11+ (本地開發，可選)

### 使用 Docker Compose 啟動（推薦）

```bash
# 1. 複製環境變量文件
cp .env.example .env

# 2. 編輯 .env 文件，設置必要的配置（特別是 API_KEY 和 SECRET_KEY）

# 3. 使用開發環境配置啟動（推薦）
docker-compose -f docker-compose.dev.yml up -d

# 或使用啟動腳本（自動檢查 Docker 環境）
./scripts/start-dev.sh

# 4. 查看服務狀態
docker-compose -f docker-compose.dev.yml ps

# 5. 查看日誌
docker-compose -f docker-compose.dev.yml logs -f aam-service
```

### 驗證服務

```bash
# 健康檢查
curl http://localhost:8000/health

# 就緒檢查
curl http://localhost:8000/ready

# 快速測試（自動檢查環境並執行所有 API 測試）
./scripts/quick_test.sh

# API 文檔
# 瀏覽器打開: http://localhost:8000/docs
```

### 本地開發（可選）

```bash
# 1. 創建虛擬環境（可選，推薦使用 Docker）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安裝依賴
pip install -r requirements-dev.txt

# 3. 啟動服務（需要先啟動依賴服務：ChromaDB, PostgreSQL, RabbitMQ）
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📁 項目結構詳解

```
aam-service/
├── src/                              # 源代碼目錄
│   ├── api/                          # API 層
│   │   ├── controllers/             # API 控制器
│   │   │   └── mcp_controller.py     # MCP 豐富化端點控制器
│   │   ├── dependencies/             # 依賴注入
│   │   │   └── dependencies.py     # FastAPI 依賴注入配置
│   │   └── middleware/              # 中間件
│   │       └── auth_middleware.py   # API Key 認證中間件
│   │
│   ├── core/                         # 核心業務邏輯層
│   │   ├── interfaces/               # 抽象接口定義（依賴倒置原則）
│   │   │   ├── i_memory_service.py  # 記憶服務接口
│   │   │   ├── i_knowledge_store.py # 知識庫接口
│   │   │   ├── i_persona_store.py   # 用戶畫像存儲接口
│   │   │   └── i_analysis_model.py  # AI 分析模型接口
│   │   └── services/                # 業務服務實現
│   │       └── memory_service.py    # 記憶服務核心業務邏輯
│   │
│   ├── infrastructure/               # 基礎設施層（具體實現）
│   │   ├── database/                # 數據訪問層
│   │   │   ├── chroma_knowledge_store.py  # ChromaDB 知識庫實現
│   │   │   ├── pg_persona_store.py        # PostgreSQL 用戶畫像實現
│   │   │   ├── models.py                  # 數據庫模型定義
│   │   │   └── __init__.py                # 數據庫連接工廠
│   │   ├── messaging/                # 消息隊列處理
│   │   │   ├── dialogue_consumer.py  # 對話歸檔消息消費者
│   │   │   └── rabbitmq_config.py   # RabbitMQ 連接配置
│   │   └── ai/                      # AI 模型相關
│   │       ├── embedding_service.py      # 向量化服務（Sentence Transformer）
│   │       └── mock_analysis_model.py     # Mock 分析模型（臨時實現）
│   │
│   ├── models/                       # 數據模型（Pydantic）
│   │   ├── api/                      # API 數據模型
│   │   │   └── mcp.py                # MCP 協議模型（PartialMCP, EnrichedMCP）
│   │   └── domain/                   # 領域模型
│   │       ├── dialogue.py          # 對話歸檔消息模型
│   │       ├── database.py           # 數據庫 Schema 模型
│   │       └── personality.py        # 個性分析模型
│   │
│   ├── config/                       # 配置管理
│   │   ├── settings.py               # Pydantic BaseSettings 配置
│   │   └── __init__.py
│   │
│   └── main.py                       # FastAPI 應用程序入口
│
├── tests/                            # 測試目錄
│   ├── unit/                         # 單元測試
│   │   ├── test_memory_service.py    # 記憶服務測試
│   │   ├── test_mcp_controller.py    # API 控制器測試
│   │   ├── test_chroma_knowledge_store.py  # 知識庫測試
│   │   ├── test_pg_persona_store.py  # 用戶畫像存儲測試
│   │   ├── test_interfaces.py        # 接口測試
│   │   └── ...                       # 其他單元測試
│   ├── integration/                 # 整合測試
│   │   ├── test_mcp_api.py           # E2E API 測試
│   │   └── test_message_queue_integration.py  # 消息隊列整合測試
│   ├── reports/                      # 測試報告
│   │   ├── 批次二-抽象接口定義-測試報告.md
│   │   ├── 批次三-数据存取层实现-測試報告.md
│   │   ├── 批次四-业务逻辑层实现-測試報告.md
│   │   ├── 批次五：消息隊列處理（Message Queue Processing）-測試報告.md
│   │   └── 批次六：API控制器-測試報告.md
│   └── conftest.py                   # pytest 配置和 fixtures
│
├── scripts/                          # 腳本目錄
│   ├── start-dev.sh                  # 啟動開發環境（自動檢查 Docker）
│   ├── quick_test.sh                 # 快速 API 測試腳本
│   ├── check-docker.sh               # Docker 環境檢查腳本
│   ├── verify_setup.sh               # 環境驗證腳本
│   └── ...                           # 其他腳本
│
├── docs/                             # 文檔目錄
│   ├── plan/                         # 實施計劃
│   │   ├── AAM Phase II.md          # Phase II 實施計劃
│   │   ├── AAM 服務第一階段 MVP 實施計劃.md
│   │   └── 批次*.md                  # 各批次實施計劃
│   ├── AAM Agent SD v2.md           # 系統設計規格文檔
│   ├── AAM (AI-Augmented Memory) SA v1.md  # 系統架構文檔
│   ├── AAM_SD_实施进度报告.md       # 實施進度報告
│   ├── AiDevelopmentGuide.md        # AI 開發指導手冊
│   ├── GIT_WORKFLOW.md              # Git 版本管理規範
│   ├── GITHUB_SETUP.md              # GitHub 設置指南
│   ├── Docker环境问题排查.md        # Docker 問題排查
│   ├── Docker目录结构调整说明.md    # Docker 目錄結構說明
│   └── README.md                    # 文檔索引
│
├── docker/                           # Docker 配置文件目錄
│   ├── Dockerfile.dev                # 開發環境 Dockerfile
│   ├── Dockerfile.staging            # 沙盒環境 Dockerfile（待創建）
│   ├── Dockerfile.prod              # 生產環境 Dockerfile（待創建）
│   └── README.md                    # Docker 配置說明
│
├── alembic/                          # 數據庫遷移工具
│   ├── versions/                    # 遷移版本文件
│   │   └── 73e92db0ee84_create_user_profiles_table.py
│   ├── env.py                       # Alembic 環境配置
│   └── script.py.mako               # 遷移腳本模板
│
├── model_cache/                     # AI 模型緩存目錄（Docker 卷掛載）
│
├── docker-compose.yml               # Docker Compose 配置（默認，指向開發環境）
├── docker-compose.dev.yml           # 開發環境 Docker Compose 配置
├── docker-compose.staging.yml       # 沙盒環境配置（待創建）
├── docker-compose.prod.yml          # 生產環境配置（待創建）
├── alembic.ini                      # Alembic 配置文件
├── pytest.ini                       # pytest 配置文件
├── requirements.txt                 # 生產依賴
├── requirements-dev.txt             # 開發依賴
└── README.md                        # 本文件
```

---

## 📂 目錄詳細說明

### `src/` - 源代碼目錄

#### `src/api/` - API 層
**職責**: 處理 HTTP 請求和響應，作為系統的對外接口

- **`controllers/`**: API 端點控制器
  - `mcp_controller.py`: 實現 `POST /v1/mcp/enrich` 端點，處理 MCP 豐富化請求
- **`dependencies/`**: FastAPI 依賴注入
  - `dependencies.py`: 定義依賴注入函數，提供服務實例
- **`middleware/`**: 中間件
  - `auth_middleware.py`: API Key 認證中間件

#### `src/core/` - 核心業務邏輯層
**職責**: 實現核心業務邏輯，遵循依賴倒置原則（DIP）

- **`interfaces/`**: 抽象接口定義
  - `i_memory_service.py`: 記憶服務接口（enrich, archive）
  - `i_knowledge_store.py`: 知識庫接口（save, search）
  - `i_persona_store.py`: 用戶畫像存儲接口（get, save_or_update）
  - `i_analysis_model.py`: AI 分析模型接口（extract_knowledge, analyze_personality）
- **`services/`**: 業務服務實現
  - `memory_service.py`: `MemoryServiceImpl` - 核心業務邏輯，協調數據存取和 AI 模型

#### `src/infrastructure/` - 基礎設施層
**職責**: 實現具體的技術細節，封裝外部依賴

- **`database/`**: 數據訪問層
  - `chroma_knowledge_store.py`: ChromaDB 知識庫實現（向量存儲和檢索）
  - `pg_persona_store.py`: PostgreSQL 用戶畫像存儲實現
  - `models.py`: 數據庫模型定義（KnowledgeAsset, UserProfileDB）
  - `__init__.py`: 數據庫連接工廠函數
- **`messaging/`**: 消息隊列處理
  - `dialogue_consumer.py`: RabbitMQ 消費者，處理對話歸檔消息
  - `rabbitmq_config.py`: RabbitMQ 連接和配置管理
- **`ai/`**: AI 模型相關
  - `embedding_service.py`: Sentence Transformer 向量化服務
  - `mock_analysis_model.py`: Mock 分析模型（臨時實現，Phase II 將替換）

#### `src/models/` - 數據模型
**職責**: 定義所有數據結構，使用 Pydantic 進行驗證

- **`api/`**: API 數據模型
  - `mcp.py`: MCP 協議模型（PartialMCP, EnrichedMCP, UserProfile, SessionContext 等）
- **`domain/`**: 領域模型
  - `dialogue.py`: 對話歸檔消息模型（DialogueArchiveMessage）
  - `database.py`: 數據庫 Schema 模型（KnowledgeAsset, UserProfileDB）
  - `personality.py`: 個性分析模型（PersonalityInsights）

#### `src/config/` - 配置管理
**職責**: 管理所有配置項，使用 Pydantic BaseSettings

- `settings.py`: 配置類定義，從環境變量加載配置

#### `src/main.py` - 應用程序入口
**職責**: FastAPI 應用程序主體，路由註冊，生命週期管理

---

### `tests/` - 測試目錄

#### `tests/unit/` - 單元測試
**職責**: 測試單個組件的功能，使用 Mock 隔離依賴

- 測試所有業務邏輯、接口、數據存取層
- 使用 `unittest.mock` 進行依賴隔離

#### `tests/integration/` - 整合測試
**職責**: 測試組件之間的集成，使用真實的數據庫和消息隊列

- E2E API 測試
- 消息隊列整合測試

#### `tests/reports/` - 測試報告
**職責**: 存儲各批次的測試報告

---

### `scripts/` - 腳本目錄

**職責**: 提供開發、測試、部署相關的腳本

- **`start-dev.sh`**: 啟動開發環境，自動檢查 Docker 環境，支持重啟/停止/重建
- **`quick_test.sh`**: 快速 API 測試腳本，自動檢查 Docker 環境並執行所有測試
- **`check-docker.sh`**: Docker 環境檢查腳本
- **`verify_setup.sh`**: 環境驗證腳本

---

### `docs/` - 文檔目錄

**職責**: 存儲所有項目文檔

#### `docs/plan/` - 實施計劃
- **`AAM Phase II.md`**: Phase II 詳細實施計劃（4 個批次）
- **`AAM 服務第一階段 MVP 實施計劃.md`**: Phase I 實施計劃
- **`批次*.md`**: 各批次的詳細實施計劃

#### 系統設計文檔
- **`AAM Agent SD v2.md`**: 系統設計規格文檔（包含降級策略設計）
- **`AAM (AI-Augmented Memory) SA v1.md`**: 系統架構文檔

#### 開發規範
- **`AiDevelopmentGuide.md`**: AI 開發指導手冊（強制性開發規則）
- **`GIT_WORKFLOW.md`**: Git 版本管理與團隊協作規範
- **`GITHUB_SETUP.md`**: GitHub 設置指南

#### 其他文檔
- **`AAM_SD_实施进度报告.md`**: 實施進度報告
- **`Docker环境问题排查.md`**: Docker 問題排查指南
- **`Docker目录结构调整说明.md`**: Docker 目錄結構說明

---

### `docker/` - Docker 配置文件目錄

**職責**: 存儲不同環境的 Docker 配置文件

- **`Dockerfile.dev`**: 開發環境 Dockerfile（支持熱重載、代碼掛載）
- **`Dockerfile.staging`**: 沙盒環境 Dockerfile（待創建）
- **`Dockerfile.prod`**: 生產環境 Dockerfile（待創建）
- **`README.md`**: Docker 配置說明文檔

---

### `alembic/` - 數據庫遷移

**職責**: 管理數據庫 Schema 變更

- **`versions/`**: 遷移版本文件
- **`env.py`**: Alembic 環境配置
- **`script.py.mako`**: 遷移腳本模板

---

### 根目錄文件

- **`docker-compose.yml`**: 默認 Docker Compose 配置（指向開發環境，向後兼容）
- **`docker-compose.dev.yml`**: 開發環境 Docker Compose 配置
- **`docker-compose.staging.yml`**: 沙盒環境配置（待創建）
- **`docker-compose.prod.yml`**: 生產環境配置（待創建）
- **`requirements.txt`**: 生產依賴
- **`requirements-dev.txt`**: 開發依賴（包含測試工具）
- **`pytest.ini`**: pytest 配置文件
- **`alembic.ini`**: Alembic 配置文件

---

## 🔧 配置

所有配置通過環境變量管理，參考 `.env.example` 文件。

### 主要配置項

- **應用配置**: `APP_NAME`, `APP_VERSION`, `DEBUG`, `LOG_LEVEL`
- **API 配置**: `API_HOST`, `API_PORT`, `API_KEY`
- **數據庫配置**: 
  - ChromaDB: `CHROMADB_HOST`, `CHROMADB_PORT`, `CHROMADB_COLLECTION_NAME`
  - PostgreSQL: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- **消息隊列配置**: `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USER`, `RABBITMQ_PASSWORD`
- **AI 模型配置**: `EMBEDDING_MODEL`, `MODEL_CACHE_DIR`
- **Redis 配置**: `REDIS_HOST`, `REDIS_PORT` (可選)

---

## 🧪 測試

### 運行測試

```bash
# 運行所有測試
pytest

# 運行單元測試
pytest tests/unit/

# 運行整合測試
pytest tests/integration/

# 生成覆蓋率報告
pytest --cov=src --cov-report=html

# 查看覆蓋率報告
open htmlcov/index.html
```

### 快速 API 測試

```bash
# 自動檢查 Docker 環境並執行所有 API 測試
./scripts/quick_test.sh
```

---

## 📚 API 文檔

啟動服務後，訪問以下端點查看 API 文檔：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要 API 端點

- **`GET /health`**: 健康檢查
- **`GET /ready`**: 就緒檢查
- **`POST /v1/mcp/enrich`**: MCP 豐富化端點（需要 `X-API-KEY` Header）

---

## 🐳 Docker 服務

### 開發環境服務

使用 `docker-compose.dev.yml` 啟動的服務：

- **AAM Service**: http://localhost:8000
- **ChromaDB**: http://localhost:8001
- **PostgreSQL**: localhost:5432
- **RabbitMQ Management**: http://localhost:15672 (admin/admin)
- **Redis**: localhost:6379

### 管理命令

```bash
# 啟動開發環境
docker-compose -f docker-compose.dev.yml up -d

# 查看服務狀態
docker-compose -f docker-compose.dev.yml ps

# 查看日誌
docker-compose -f docker-compose.dev.yml logs -f aam-service

# 停止服務
docker-compose -f docker-compose.dev.yml down

# 重啟服務
docker-compose -f docker-compose.dev.yml restart
```

---

## 📊 開發進度

### Phase I (MVP) - ✅ 已完成 70%

| 階段 | 狀態 | 完成度 |
|------|------|--------|
| 基礎架構搭建 | ✅ | 100% |
| 數據協議定義 | ✅ | 100% |
| 接口層實現 | ✅ | 100% |
| API層實現 | ✅ | 100% |
| 數據存取層 | ✅ | 100% |
| AI模型集成 | ⚠️ | 60% (Mock 實現) |
| 消息隊列處理 | ✅ | 100% |
| 測試實現 | ✅ | 90% |
| LoRA訓練管道 | ❌ | 0% |
| 部署與監控 | ⚠️ | 50% |

**詳細進度報告**: [docs/AAM_SD_实施进度报告.md](docs/AAM_SD_实施进度报告.md)

### Phase II (語義分析) - 📋 規劃中

**實施計劃**: [docs/plan/AAM Phase II.md](docs/plan/AAM Phase II.md)

**批次劃分**:
1. **批次一**: 降級策略框架與質量評估機制（優先級：最高）
2. **批次二**: LangChain Embedding 模型實現（優先級：最高）
3. **批次三**: LLM 降級層實現（優先級：中）
4. **批次四**: Eb-MM 模型集成（優先級：中）

---

## 🔐 安全

- **API Key 認證**: 通過 `X-API-KEY` Header 進行認證
- **環境變量管理**: 敏感信息通過環境變量管理，不硬編碼
- **生產環境要求**: 必須修改默認的 `API_KEY` 和 `SECRET_KEY`

---

## 📝 開發規範

**所有開發者必須閱讀並遵守以下規範：**

1. **[AI 開發指導手冊](docs/AiDevelopmentGuide.md)** ⚠️ **強制性**
   - 目錄結構規範
   - 代碼文件規範
   - 開發原則

2. **[Git 版本管理與團隊協作規範](docs/GIT_WORKFLOW.md)** ⚠️ **強制性**
   - Checkout/Checkin 規範
   - 分支策略
   - Pull Request 流程

3. **[GitHub 設置指南](docs/GITHUB_SETUP.md)**
   - GitHub 倉庫設置
   - 認證配置

**完整文檔索引**: [docs/README.md](docs/README.md)

---

## 🏗️ 架構設計原則

### 1. 依賴倒置原則 (DIP)

業務邏輯層 (`MemoryServiceImpl`) 依賴於抽象接口，而不是具體實現。這使得：
- ✅ 高可測試性（可使用 Mock 對象）
- ✅ 低耦合度（可輕鬆替換實現）
- ✅ 高可維護性

### 2. 協議優先 (Protocol-First)

所有核心數據對象都使用 Pydantic 模型進行嚴格定義和驗證：
- ✅ MCP 協議模型
- ✅ 對話歸檔消息模型
- ✅ 數據庫 Schema 模型

### 3. 配置化 (Configuration-Driven)

所有配置項通過環境變量管理，使用 Pydantic BaseSettings：
- ✅ 不同環境使用不同配置
- ✅ 提高安全性
- ✅ 提高可移植性

### 4. 降級策略 (Fallback Strategy) - Phase II

實現多層級降級策略，確保系統高可用性：
- 優先級 1: Eb-MM (小模型，成本最低)
- 優先級 2: LangChain Embedding (中等模型)
- 優先級 3: LLM (大模型，最後保障)

---

## 🔄 工作流程

### 開發流程

1. **創建功能分支**: `git checkout -b feature/your-feature`
2. **開發和測試**: 遵循開發規範，編寫測試
3. **提交代碼**: `git commit -m "feat: your feature description"`
4. **創建 Pull Request**: 等待代碼審查
5. **合併到主分支**: 審查通過後合併

### 測試流程

1. **單元測試**: 開發時運行 `pytest tests/unit/`
2. **整合測試**: 提交前運行 `pytest tests/integration/`
3. **快速測試**: 使用 `./scripts/quick_test.sh` 驗證 API

---

## 📞 相關資源

### 文檔

- **系統設計**: [docs/AAM Agent SD v2.md](docs/AAM Agent SD v2.md)
- **系統架構**: [docs/AAM (AI-Augmented Memory) SA v1.md](docs/AAM%20(AI-Augmented%20Memory)%20SA%20v1.md)
- **實施計劃**: [docs/plan/](docs/plan/)
- **進度報告**: [docs/AAM_SD_实施进度报告.md](docs/AAM_SD_实施进度报告.md)

### 腳本

- **啟動開發環境**: `./scripts/start-dev.sh`
- **快速 API 測試**: `./scripts/quick_test.sh`
- **Docker 環境檢查**: `./scripts/check-docker.sh`

---

## 📄 許可證

[待定]

---

## 👥 貢獻者

[待定]

---

## 📞 聯繫方式

[待定]

---

**最後更新**: 2025-11-12
