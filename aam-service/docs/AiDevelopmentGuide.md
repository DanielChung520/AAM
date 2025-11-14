# AI 開發指導手冊 (AI Development Guide) v2.0

## 🚨 強制執行聲明

**AI 開發助手，你必須嚴格遵守以下所有規則。違反任何規則都將導致代碼審查失敗。**

---

## 1. 核心原則 (Core Principles)

### 1.1 強制性規則概述

AI 開發助手，為了確保 EKAg 專案的代碼庫保持一致性 (Consistency)、文檔化 (Documentation) 和可追溯性 (Traceability)，你必須在執行任何開發或修改任務時，**嚴格遵守**以下指導原則。

**⚠️ 重要提醒：**
- 所有規則都是**強制性**的，不可忽略或跳過
- 每個任務完成後，你必須進行**自我檢查**並報告合規情況
- 違反規則的代碼將被拒絕，必須重新開發

### 1.2 規則零：深色模式對比度強制規範 ⚠️ 最高優先級

**這是最重要的規則，違反此規則的代碼將被立即拒絕。**

在編寫任何 UI 組件時，你必須：
1. **強制考慮**淺色和深色模式的文字對比度
2. **強制測試**兩種模式下的可讀性
3. **強制使用**主題變量而非硬編碼顏色
4. **強制實現**雙模式 hover 效果

**檢查清單（必須完成）：**
- [ ] 所有文字在深色模式下清晰可讀
- [ ] 所有 hover 效果在兩種模式下都有足夠對比度
- [ ] 所有狀態指示器在深色模式下可見
- [ ] 所有圖標在深色模式下清晰可見
- [ ] 使用主題變量而非硬編碼顏色值
### 1.3 規則一：文件位置強制規範 ⚠️ 強制執行

**在創建任何新文件前，你必須：**
1. **強制查閱**專案目錄結構
2. **強制確認**文件放置位置
3. **強制禁止**隨意創建新目錄
4. **強制禁止**將文件放在錯誤位置

**文件位置強制指引：**
- **前端文件**：**必須**放在 `frontend/src/` 對應的子目錄中
- **後端文件**：**必須**放在 `backend/` 對應的子目錄中
- **文檔文件**：**必須**放在 `docs/` 或 `frontend/doc/` 或 `backend/docs/` 中
- **腳本文件**：**必須**放在 `script/` 或 `backend/scripts/` 中
- **測試文件**：**必須**放在對應的 `test/` 目錄中

**違規後果：**
- 文件位置錯誤的代碼將被拒絕
- 必須重新創建文件在正確位置
- 不得移動現有文件到錯誤位置


## 2. 專案目錄結構 (Project Directory Structure) ⚠️ 強制遵守

### 2.1 強制性原則

**🚨 絕對禁止：**
- 隨意新增檔案
- 創建未經授權的目錄
- 將文件放在錯誤位置

**✅ 強制要求：**
- 在創建任何新文件之前，**必須**首先查閱以下已定義的目錄結構
- 將新文件放置在最符合其職責的目錄中
- 如果現有結構無法滿足需求，**必須**向人類開發者請求確認

### 2.2 目錄結構強制規範

KEN/                          # 專案根目錄
├── backend/                  # 後端服務目錄
│   ├── api/                  # API 路由模組
│   ├── core/                 # 核心功能模組 (dependencies, document_processor, graph_rag_chain)
│   ├── docs/                 # 後台文檔目錄
│   │   ├── DEPLOYMENT_GUIDE.md
│   │   ├── env_config.md
│   │   ├── CHROMADB_SETUP.md
│   │   └── ...
│   ├── models/               # 數據模型定義
│   ├── schemas/              # Pydantic 模式定義
│   ├── services/             # 業務邏輯服務層
│   ├── tasks/                # 異步任務處理 (Celery)
│   ├── test/                 # 後端測試目錄
│   │   ├── unit/             # 單元測試
│   │   ├── integration/      # 整合測試
│   │   ├── api/              # API 測試
│   │   └── fixtures/         # 測試數據
│   ├── scripts/              # 後台專用腳本
│   │   ├── install-dependencies.sh
│   │   ├── service-manager.sh
│   │   └── health-check.sh
│   ├── utils/                # 後台工具函數
│   ├── main.py               # FastAPI 應用入口
│   ├── config.py             # 配置文件
│   ├── database.py           # 數據庫配置
│   ├── auth.py               # 認證模組
│   └── requirements.txt      # Python 依賴
├── frontend/                 # 前端服務目錄
│   ├── public/               # 靜態資源與 PWA 圖示
│   ├── doc/                  # 前端文檔目錄
│   │   └── spec/             # 前端組件規格說明文件
│   ├── src/
│   │   ├── api/              # 封裝與後端 API 的所有通信邏輯
│   │   ├── assets/           # 圖片, SVG, 字體等
│   │   ├── components/       # 可複用的、純粹的 UI 組件
│   │   ├── config/           # 應用配置
│   │   ├── hooks/            # 自定義的 React Hooks
│   │   ├── pages/            # 頁面級組件
│   │   ├── services/         # 處理複雜的客戶端業務邏輯
│   │   ├── state/            # 全局狀態管理
│   │   ├── styles/           # 全局 CSS, 主題定義
│   │   ├── types/            # 全局 TypeScript 類型定義
│   │   └── utils/            # 通用輔助函數
│   ├── test/                 # 前端測試目錄
│   │   ├── unit/             # 單元測試
│   │   ├── integration/      # 整合測試
│   │   ├── e2e/              # 端到端測試
│   │   └── fixtures/         # 測試數據
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docs/                     # 專案級文檔目錄
│   ├── AiDevelopmentGuide.md # AI 開發指導手冊
│   ├── EKAg_backend.md       # 後台專案文檔
│   ├── EKAg_frontend.md      # 前端專案文檔
│   └── spec/                 # 專案級規格說明文件
├── script/                   # 專案級腳本目錄
│   ├── admin/                # 管理員腳本
│   ├── dev/                  # 開發環境腳本
│   ├── test/                 # 測試相關腳本
│   ├── deploy/               # 部署腳本
│   └── utils/                # 工具腳本
├── docker-compose.yml        # Docker 編排配置
└── README.md                 # 專案說明文檔
## 3. 代碼文件強制規範 (Code File Specification) ⚠️ 強制執行

### 3.1 強制性原則

**🚨 絕對要求：**
- 所有新建的代碼文件都**必須**包含標準頭部註釋
- 沒有頭部註釋的文件將被拒絕
- 頭部註釋格式錯誤的文件將被拒絕

### 3.1.1 規則二-A：目錄架構強制查閱規範 ⚠️ 最高優先級

**🚨 這是一條極其重要的規則，違反此規則的代碼將被立即拒絕。**

**強制要求：**
- 在創建任何新文件（包括代碼文件、測試文件、腳本文件）之前，**必須**先完整查閱第 2 節的專案目錄結構
- **必須**確認文件應該放置在正確的目錄中
- **必須**遵循現有的目錄結構，不得隨意創建新目錄
- **禁止**將文件放置在錯誤的目錄中

**強制查閱流程：**
1. **必須先**閱讀第 2 節 "專案目錄結構" 的全部內容
2. **必須確認**你理解每個目錄的用途和職責
3. **必須確認**你的新文件應該放在哪個目錄
4. **必須確認**該目錄是否已經存在
5. **如果目錄不存在，必須**向人類開發者請求確認，不得自行創建

**文件類型和對應目錄：**
- **前端代碼文件**：必須放在 `frontend/src/` 對應子目錄
  - 組件 → `frontend/src/components/`
  - 頁面 → `frontend/src/pages/`
  - Hooks → `frontend/src/hooks/`
  - 服務 → `frontend/src/services/`
  - API → `frontend/src/api/`
  - 工具函數 → `frontend/src/utils/`

- **前端測試文件**：必須放在 `frontend/test/` 對應子目錄
  - 單元測試 → `frontend/test/unit/`
  - 整合測試 → `frontend/test/integration/`
  - E2E 測試 → `frontend/test/e2e/`

- **後端代碼文件**：必須放在 `backend/` 對應子目錄
  - API 路由 → `backend/api/`
  - 核心邏輯 → `backend/core/`
  - 數據模型 → `backend/models/`
  - 業務服務 → `backend/services/`
  - 工具腳本 → `backend/utils/`

- **後端測試文件**：必須放在 `backend/test/` 對應子目錄
  - Pipeline 測試 → `backend/test/pipeline/`
  - ChromaDB 測試 → `backend/test/chromadb/`
  - 重複分析 → `backend/test/duplicates/`
  - Debug 工具 → `backend/test/debug/`
  - 其他測試 → `backend/test/other/`

- **專案級腳本**：必須放在 `script/` 對應子目錄
  - 開發腳本 → `script/dev/`
  - 測試腳本 → `script/test/`
  - 部署腳本 → `script/deploy/`
  - 管理員腳本 → `script/admin/`

- **文檔文件**：必須放在對應的 `docs/` 目錄
  - 專案文檔 → `docs/`
  - 前端規格 → `frontend/doc/spec/`
  - 後端文檔 → `backend/docs/`

**違規後果：**
- 文件位置錯誤的代碼將被立即拒絕
- 必須重新創建文件在正確位置
- 不得移動現有文件到錯誤位置
- 必須遵守現有目錄結構

**檢查清單（創建新文件前必須確認）：**
- [ ] 已完整閱讀第 2 節的目錄結構
- [ ] 已確認目標目錄存在
- [ ] 已確認文件類型與目錄用途匹配
- [ ] 已確認沒有創建未經授權的新目錄

### 3.2 規則二：代碼文件頭部註釋強制規範

**對於任何你新建的 `.ts`、`.tsx`、`.py`、`.sh` 文件，你必須：**
1. **強制在**文件最頂部插入標準格式的註釋塊
2. **強制填寫**所有必需字段
3. **強制使用**正確的日期格式
4. **強制描述**組件/模塊的用途和核心職責
```typescript
/**
 * @purpose: [簡潔說明這個組件/模塊的用途和核心職責]
 * @author: DanielChung and AI
 * @createdAt: [YYYY-MM-DD]
 * @lastModified: [YYYY-MM-DD]
 */

範例 (src/components/KnowledgeAssetCard.tsx):

/**
 * @purpose: 負責渲染單個知識資產（KnowledgeAsset）的卡片視圖，用於主儀表板。
 * @author: DanielChung and AI
 * @createdAt: 2024-05-23
 * @lastModified: 2024-05-23
 */

// ... component code starts here ...
### 3.3 規則三：規格文檔同步強制規範 ⚠️ 最高優先級

**這是一條極其重要的規則，違反此規則的代碼將被立即拒絕。**

**🚨 強制要求：**
- 當你新增或重大修改任何一個代碼模塊時，你**必須**同時在 `doc/spec/` 目錄下創建或更新對應的規格說明文件（.md 格式）
- 沒有對應規格文檔的代碼將被拒絕
- 規格文檔格式錯誤的代碼將被拒絕

**強制流程：**
1. **必須先**生成或更新 `doc/spec/` 中的規格文件
2. **必須再**根據該規格文件生成應用代碼
3. **禁止**先寫代碼後補規格文檔

**強制命名規則：**
- 規格文件名**必須**與其對應的代碼文件名保持一致
- `src/pages/AssetDashboard.tsx` -> `doc/spec/AssetDashboard.md`
- `src/hooks/useAuth.ts` -> `doc/spec/useAuth.md`
- `backend/services/user_service.py` -> `backend/docs/user_service.md`

**強制文件格式：**
- **必須**使用以下 Markdown 模板
- **必須**包含所有必需章節
- **必須**填寫修訂歷史

### 3.4 規格文件強制模板

內容: 規格文件必須包含核心職責、接口定義 (Props)、核心行為邏輯和修訂歷史。
# 規格說明: [組件/模塊名稱]

- **文件路徑:** `[指向對應的源代碼文件路徑]`
- **創建日期:** `[YYYY-MM-DD]`

---

### **1. 核心職責 (Purpose)**

[用 1-2 句話，清晰地描述這個模塊的核心功能和設計目的。]

---

### **2. 接口定義 (API / Props)**

[對於 React 組件，使用表格定義其 `Props`。對於普通 TS 模塊，定義其導出的主要函數的參數和返回值。]

**Props (以 KnowledgeAssetCard 為例):**
| Prop 名稱   | 類型                 | 是否必需 | 描述                                       |
| ----------- | -------------------- | -------- | ------------------------------------------ |
| `asset`     | `KnowledgeAssetData` | 是       | 要顯示的知識資產數據對象                   |
| `onNavigate`| `(id: string) => void` | 是       | 雙擊卡片時觸發的回調，用於頁面導航         |
| `onArchive` | `(asset: KnowledgeAssetData) => void` | 是       | 點擊存檔按鈕時觸發的回調                   |

---

### **3. 核心行為邏輯 (Behavior & Logic)**

[用列表形式，描述該模塊的關鍵行為邏輯和用戶交互流程。]

- **渲染邏輯:**
  - 卡片標題、描述、版本號和標籤必須從 `asset` prop 中正確渲染。
- **交互邏輯:**
  - 整個卡片區域監聽 `onDoubleClick` 事件，並觸發 `onNavigate` 回調。
  - 右上角的菜單按鈕包含「存檔」選項，點擊後會觸發 `onArchive` 回調。

---

### **4. 修訂歷史 (Revision History)**

| 版本 | 修改日期   | 修改者    | 修改內容摘要                 |
| ---- | ---------- | --------- | ---------------------------- |
| v1.0 | 2024-05-23 | DanielChung and AI | 初始創建規格文件。           |
|      |            |           |                              |

## 4. 強制開發工作流程 (Mandatory Development Workflow) ⚠️ 嚴格執行

### 4.1 強制性工作流程

**AI 助手，當接收到一個新的開發任務時，你必須嚴格遵循以下步驟，不得跳過任何步驟：**

### 4.2 步驟一：接收與理解任務 (Receive & Understand) - 強制執行

**你必須：**
1. **強制確認**理解人類開發者提出的需求
2. **強制分析**任務的具體要求
3. **強制識別**涉及的技術領域（前端/後端/文檔/腳本）
4. **強制確認**任務的優先級和緊急程度

**示例：**「實現資產的存檔功能」→ 分析：前端組件 + 後端 API + 數據庫操作

### 4.3 步驟二：定位與檢查 (Locate & Check) - 強制執行

**你必須：**
1. **強制閱讀**第 2 節的完整目錄結構
2. **強制分析**任務涉及哪些代碼模塊
3. **強制確認**文件應該放置的正確目錄
4. **強制檢查**目標目錄是否已存在
5. **強制確定**應該修改或創建哪些文件
6. **強制檢查**現有代碼的相關性

**強制查閱目錄結構：**
- **必須先**完整閱讀第 2 節的 "專案目錄結構"
- **必須理解**每個目錄的用途和職責
- **必須確認**新文件應該放在哪個目錄
- **如果目錄不存在，必須**向人類開發者請求確認，不得自行創建

**檢查清單：**
- [ ] 已完整閱讀第 2 節的目錄結構
- [ ] 已確認目標目錄存在
- [ ] 已確認文件類型與目錄用途匹配
- [ ] 已分析所有相關代碼模塊
- [ ] 已確認文件放置位置符合目錄結構
- [ ] 已檢查現有代碼的依賴關係
- [ ] 已識別需要修改的現有文件
- [ ] 已確認沒有創建未經授權的新目錄

### 4.4 步驟三：編寫/更新規格 (Write/Update Spec) - 強制執行

**你必須：**
1. **強制先**在 `doc/spec/` 目錄下找到對應的規格文件
2. **強制創建**新的 .md 規格文件（如果是新功能）
3. **強制更新**現有規格文件（如果是修改功能）
4. **強制填寫**修訂歷史記錄

**強制要求：**
- 在編寫任何應用代碼之前，**必須**先完成規格文檔
- **禁止**先寫代碼後補規格文檔
- **必須**使用標準模板格式

### 4.5 步驟四：生成/修改代碼 (Generate/Modify Code) - 強制執行

**你必須：**
1. **強制根據**規格文件編寫或修改代碼
2. **強制添加**標準頭部註釋（新文件）
3. **強制遵循**深色模式對比度規範
4. **強制使用**正確的文件位置

**強制檢查：**
- [ ] 代碼符合規格文檔要求
- [ ] 新文件包含標準頭部註釋
- [ ] UI 組件符合深色模式規範
- [ ] 文件位置正確

### 4.6 步驟五：完成報告 (Report Completion) - 強制執行

**任務完成後，你必須向人類開發者報告：**

1. **已完成的核心功能**
2. **已創建/更新的規格文件路徑**
3. **已創建/修改的源代碼文件路徑**
4. **合規性檢查結果**
5. **深色模式測試結果**
6. **任何已知問題或限制**

**強制格式：**
```
## 任務完成報告

### ✅ 已完成功能
- [功能描述]

### 📁 創建/修改的文件
- 規格文檔：`[路徑]`
- 源代碼：`[路徑]`

### ✅ 合規性檢查
- [ ] 深色模式對比度測試通過
- [ ] 文件位置正確
- [ ] 頭部註釋完整
- [ ] 規格文檔同步

### ⚠️ 注意事項
- [任何問題或限制]
```

---

## 5. 服務管理強制規範 (Service Management Guidelines) ⚠️ 強制執行

### 5.1 規則四：使用 screen 管理服務 - 強制執行

a. 

**🚨 強制要求：**
- 為了確保開發環境的穩定性和服務的可追蹤性，所有後台服務都**必須**使用 `screen` 會話進行管理
- **禁止**直接在終端中運行服務
- **禁止**使用其他進程管理工具（如 nohup、& 等）
- **必須**使用標準的 screen 會話名稱

### 5.2 服務命名強制規範

**🚨 強制要求：**
- 所有服務名稱**必須**嚴格按照以下規範命名
- **禁止**使用其他名稱
- **禁止**修改現有服務名稱

**當前服務：**
- `web` - 前端服務 (React + Vite) - **強制使用**
- `api` - 後端服務 (FastAPI + LangChain) - **強制使用**

**未來服務：**
- `rd` - Redis 服務 - **強制使用**
- `neo` - Neo4j 圖數據庫服務 - **強制使用**
- `vct` - ChromaDB 向量數據庫服務 - **強制使用**
- `task` - Celery 異步任務處理服務 - **強制使用**

### 5.3 screen 會話管理強制命令

**🚨 強制要求：**
- 所有服務啟動命令**必須**使用以下格式
- **禁止**修改命令格式
- **禁止**使用其他啟動方式

**強制啟動服務命令：**
```bash
# 前端服務 - 強制使用
screen -S web -d -m bash -c "cd frontend && npm run dev"

# 後端服務 - 強制使用
screen -S api -d -m bash -c "cd backend && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000"

# 未來服務示例 - 強制使用
screen -S rd -d -m bash -c "redis-server"
screen -S neo -d -m bash -c "neo4j start"
screen -S vct -d -m bash -c "cd backend && chroma run --host 0.0.0.0 --port 8001"
screen -S task -d -m bash -c "cd backend && source venv/bin/activate && celery -A main worker --loglevel=info"
```

**查看服務狀態：**
```bash
# 列出所有 screen 會話
screen -ls

# 查看特定服務
screen -r web    # 查看前端服務
screen -r api    # 查看後端服務
screen -r rd     # 查看 Redis 服務
screen -r neo    # 查看 Neo4j 服務
screen -r vct    # 查看 ChromaDB 服務
screen -r task   # 查看 Celery 服務
```

**停止服務：**
```bash
# 停止特定服務
screen -S web -X quit    # 停止前端服務
screen -S api -X quit    # 停止後端服務
screen -S rd -X quit     # 停止 Redis 服務
screen -S neo -X quit    # 停止 Neo4j 服務
screen -S vct -X quit    # 停止 ChromaDB 服務
screen -S task -X quit   # 停止 Celery 服務

# 停止所有服務
screen -ls | grep -E "(web|api|rd|neo|vct|task)" | cut -d. -f1 | xargs -I {} screen -S {} -X quit
```

### 6.3 服務啟動腳本

**快速啟動所有服務：**
盡量使用/script/dev/ 下的.sh指令進行啟動
a. 所有服務：restart-all-services
b. FastAPI：restart-api
c. Chroma：restart-chromadb
e. Celery：restart-celery
f. Redis：restart-redis
g. Neo4j：restart-neo4j
h. vite：restart-web
以上若沒有必要，按單一服務重啟，只有特定要求下才全部重啟

```bash
#!/bin/bash
# start-all-services.sh

echo "🚀 啟動 EKAg 所有服務..."

# 啟動前端服務
screen -S web -d -m bash -c "cd frontend && npm run dev"
echo "✅ 前端服務已啟動 (screen: web)"

# 啟動後端服務
screen -S api -d -m bash -c "cd backend && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000"
echo "✅ 後端服務已啟動 (screen: api)"

# 未來服務
# screen -S rd -d -m bash -c "redis-server"
# screen -S neo -d -m bash -c "neo4j start"
# screen -S vct -d -m bash -c "cd backend && chroma run --host 0.0.0.0 --port 8001"
# screen -S task -d -m bash -c "cd backend && source venv/bin/activate && celery -A main worker --loglevel=info"

echo "🎉 所有服務啟動完成！"
echo "📊 查看服務狀態: screen -ls"
echo "🔍 查看特定服務: screen -r <服務名>"
```

### 6.4 服務監控

**檢查服務健康狀態：**
```bash
# 檢查前端服務
curl -s http://localhost:5173 > /dev/null && echo "✅ 前端服務正常" || echo "❌ 前端服務異常"

# 檢查後端服務
curl -s http://localhost:8000/health > /dev/null && echo "✅ 後端服務正常" || echo "❌ 後端服務異常"

# 檢查 Redis 服務
redis-cli ping > /dev/null && echo "✅ Redis 服務正常" || echo "❌ Redis 服務異常"

# 檢查 Neo4j 服務
curl -s http://localhost:7474 > /dev/null && echo "✅ Neo4j 服務正常" || echo "❌ Neo4j 服務異常"

# 檢查 ChromaDB 服務
curl -s http://localhost:8001 > /dev/null && echo "✅ ChromaDB 服務正常" || echo "❌ ChromaDB 服務異常"
```

**注意事項：**
- 所有服務都必須在 screen 會話中運行，不得直接在終端中運行
- 服務名稱必須嚴格按照規範命名
- 在開發過程中，可以隨時使用 `screen -r <服務名>` 查看服務日誌
- 服務重啟時，必須先停止舊的 screen 會話，再啟動新的會話

---

## 6. 強制檢查機制與違規處理 (Mandatory Check Mechanism & Violation Handling) ⚠️ 嚴格執行

### 6.1 強制自我檢查機制

**AI 助手，在完成任何任務後，你必須進行以下強制檢查：**

#### 6.1.1 代碼合規性強制檢查

**你必須檢查：**
- [ ] **深色模式對比度**：所有 UI 組件在深色模式下清晰可讀
- [ ] **文件位置**：所有文件都在正確的目錄中
- [ ] **頭部註釋**：所有新文件都包含標準頭部註釋
- [ ] **規格文檔**：所有代碼都有對應的規格文檔
- [ ] **服務管理**：所有服務都使用 screen 會話管理
- [ ] **命名規範**：所有文件、組件、服務都使用標準命名

#### 6.1.2 強制測試檢查

**你必須測試：**
- [ ] **深色模式切換**：在瀏覽器中測試深色模式
- [ ] **Hover 效果**：所有可交互元素的 hover 效果
- [ ] **狀態指示器**：Chip、Badge 等在深色模式下的可見性
- [ ] **圖標可見性**：所有圖標在深色模式下清晰可見
- [ ] **文字對比度**：所有文字都有足夠的對比度

### 6.2 違規處理機制

#### 6.2.1 違規等級分類

**🚨 嚴重違規（立即拒絕）：**
- 深色模式對比度不足
- 文件位置錯誤
- 缺少規格文檔
- 缺少頭部註釋

**⚠️ 一般違規（需要修正）：**
- 命名不規範
- 服務管理不當
- 代碼格式問題

#### 6.2.2 強制修正流程

**當發現違規時，你必須：**
1. **立即停止**當前任務
2. **強制修正**所有違規問題
3. **重新檢查**修正後的代碼
4. **重新報告**合規性檢查結果

### 6.3 強制報告格式

**每次任務完成後，你必須使用以下格式報告：**

```markdown
## 🚨 強制合規性檢查報告

### ✅ 深色模式檢查
- [ ] 所有文字在深色模式下清晰可讀
- [ ] 所有 hover 效果在兩種模式下都有足夠對比度
- [ ] 所有狀態指示器在深色模式下可見
- [ ] 所有圖標在深色模式下清晰可見
- [ ] 使用主題變量而非硬編碼顏色值

### ✅ 文件位置檢查
- [ ] 所有文件都在正確的目錄中
- [ ] 沒有創建未經授權的目錄
- [ ] 文件命名符合規範

### ✅ 代碼規範檢查
- [ ] 所有新文件都包含標準頭部註釋
- [ ] 所有代碼都有對應的規格文檔
- [ ] 代碼格式符合規範

### ✅ 服務管理檢查
- [ ] 所有服務都使用 screen 會話管理
- [ ] 服務命名符合標準
- [ ] 服務啟動命令正確

### ⚠️ 違規問題
- [列出任何發現的違規問題]

### 🔧 修正措施
- [列出已採取的修正措施]
```

---

## 7. 深色模式開發強制規範 (Dark Mode Development Mandatory Guidelines) ⚠️ 最高優先級

### 7.1 規則六：深色模式對比度強制檢查清單 ⚠️ 最高優先級

**🚨 這是最重要的規則，違反此規則的代碼將被立即拒絕。**

**強制要求：**
- 在編寫或修改任何 UI 組件時，**必須**遵循以下檢查清單
- **必須**確保深色模式下的可讀性和用戶體驗
- **禁止**忽略深色模式測試

### 7.2 文字顏色強制規範

**🚨 強制使用主題變量：**
- ✅ **主要文字**：`color: 'text.primary'` - **強制使用**，確保最高對比度
- ✅ **次要文字**：`color: 'text.secondary'` - **強制使用**，適中對比度
- ✅ **輔助文字**：`color: 'text.tertiary'` - **強制使用**，較低對比度但仍可讀
- ❌ **絕對禁止**：硬編碼顏色值如 `#333333`、`#666666` 等

**錯誤示例：**
```typescript
// ❌ 錯誤：硬編碼顏色，深色模式下不可見
<Typography sx={{ color: '#333333' }}>文字內容</Typography>

// ❌ 錯誤：使用 Joy UI 的 color="neutral"，可能對比度不足
<Typography color="neutral">文字內容</Typography>
```

**正確示例：**
```typescript
// ✅ 正確：使用主題變量
<Typography sx={{ color: 'text.primary', fontWeight: 500 }}>主要文字</Typography>
<Typography sx={{ color: 'text.secondary', fontWeight: 400 }}>次要文字</Typography>
```

### 7.2 Hover 效果規範

**強制實現雙模式 Hover：**
所有可交互元素的 hover 效果必須同時定義淺色和深色模式的樣式。

**標準 Hover 模板：**
```typescript
sx={{
  '&:hover': {
    backgroundColor: (theme) => 
      theme.palette.mode === 'dark' 
        ? 'rgba(255, 255, 255, 0.08)'  // 深色模式：淡白色背景
        : 'rgba(0, 0, 0, 0.04)',       // 淺色模式：淡黑色背景
    color: 'text.primary !important',
    // 確保子元素也有正確顏色
    '& .MuiTypography-root': {
      color: 'text.primary !important',
    },
    '& .MuiSvgIcon-root': {
      color: 'text.primary !important',
    },
  },
}}
```

### 7.3 狀態指示器規範

**Chip 組件對比度規範：**
狀態膠囊必須在深色模式下有足夠的背景色對比度。

```typescript
// ✅ 正確的狀態膠囊實現
<Chip
  sx={{
    color: (theme) => {
      if (theme.palette.mode === 'dark') {
        switch (status) {
          case 'success': return '#ffffff';
          case 'warning': return '#000000';  // 黃色背景用黑字
          case 'error': return '#ffffff';
          default: return '#ffffff';
        }
      }
      return 'inherit';
    },
    backgroundColor: (theme) => {
      if (theme.palette.mode === 'dark') {
        switch (status) {
          case 'success': return 'rgba(76, 175, 80, 0.8)';   // 綠色
          case 'warning': return 'rgba(255, 193, 7, 0.8)';   // 黃色
          case 'error': return 'rgba(244, 67, 54, 0.8)';     // 紅色
          default: return 'rgba(158, 158, 158, 0.8)';        // 灰色
        }
      }
      return 'inherit';
    },
    fontWeight: 500,
  }}
>
```

### 7.4 圖標和裝飾元素規範

**圖標顏色強制規範：**
```typescript
// ✅ 正確：確保圖標在深色模式下可見
<DocumentIcon 
  sx={{
    color: 'text.primary',
  }}
/>

// ✅ 正確：進度指示器
<CircularProgress 
  sx={{
    color: 'text.primary',
  }}
/>
```

### 7.5 全局 CSS 覆蓋規範

**當 Joy UI 默認樣式無法覆蓋時，使用全局 CSS：**

在 `frontend/src/styles/theme-variables.css` 中添加強制樣式：

```css
/* 深色模式強制修復模板 */
[data-joy-color-scheme="dark"] .your-component-class:hover {
  background-color: rgba(255, 255, 255, 0.12) !important;
  color: #ffffff !important;
}

[data-joy-color-scheme="dark"] .your-component-class:hover .MuiTypography-root {
  color: #ffffff !important;
}

[data-joy-color-scheme="dark"] .your-component-class:hover .MuiSvgIcon-root {
  color: #ffffff !important;
}
```

### 7.6 開發檢查清單

**每個組件完成後必須檢查：**

- [ ] **文字對比度**：所有文字在深色背景下清晰可讀
- [ ] **Hover 效果**：hover 狀態下文字和背景有足夠對比度
- [ ] **狀態指示器**：Chip、Badge 等在深色模式下可見
- [ ] **圖標可見性**：所有圖標在深色模式下清晰可見
- [ ] **交互反饋**：按鈕、鏈接等交互元素有明確的視覺反饋
- [ ] **邊框和分割線**：使用 `divider` 主題變量而非硬編碼顏色

### 7.7 常見問題和解決方案

**問題 1：Joy UI 組件默認樣式覆蓋不了**
```typescript
// 解決方案：使用 !important 和更具體的選擇器
sx={{
  color: 'text.primary !important',
  '&.MuiComponent-root': {
    color: 'text.primary !important',
  },
}}
```

**問題 2：子元素顏色不繼承**
```typescript
// 解決方案：明確設置子元素顏色
sx={{
  '&:hover': {
    '& *': {
      color: 'text.primary !important',
    },
  },
}}
```

**問題 3：全局樣式衝突**
```typescript
// 解決方案：使用自定義 className 提高特異性
<Component 
  className="custom-component-name"
  sx={{...}}
/>
```

### 7.8 測試深色模式

**開發時必須測試：**
1. 在瀏覽器中切換到深色模式
2. 檢查所有文字是否清晰可讀
3. 測試所有 hover 效果
4. 驗證所有狀態指示器
5. 確認所有圖標可見

**測試工具：**
- Chrome DevTools 的深色模式切換
- 系統級深色模式切換
- 對比度檢查工具（如 WebAIM Contrast Checker）

---

## 8. 測試與腳本管理規範 (Testing & Script Management Guidelines)

**規則七：測試目錄結構規範**
為了確保測試的組織性和可維護性，所有測試文件都必須按照以下目錄結構進行組織。

### 8.1 測試目錄結構

```
KEN/
├── frontend/
│   └── test/                    # 前端測試目錄
│       ├── unit/               # 單元測試
│       ├── integration/        # 整合測試
│       ├── e2e/                # 端到端測試
│       └── fixtures/           # 測試數據和模擬文件
├── backend/
│   ├── test/                   # 後端測試目錄
│   │   ├── unit/               # 單元測試
│   │   ├── integration/        # 整合測試
│   │   ├── api/                # API 測試
│   │   └── fixtures/           # 測試數據和模擬文件
│   └── scripts/                # 後台專用腳本目錄
│       ├── install-dependencies.sh
│       ├── service-manager.sh
│       └── health-check.sh
├── docs/                       # 專案級文檔目錄
│   ├── AiDevelopmentGuide.md
│   ├── EKAg_backend.md
│   ├── EKAg_frontend.md
│   └── spec/                   # 專案級規格說明文件
└── script/                     # 專案級腳本目錄
    ├── admin/                  # 管理員腳本
    ├── dev/                    # 開發環境腳本
    ├── test/                   # 測試相關腳本
    ├── deploy/                 # 部署腳本
    └── utils/                  # 工具腳本
```

### 8.2 測試文件命名規範

**前端測試：**
- 組件測試：`ComponentName.test.tsx`
- Hook 測試：`useHookName.test.ts`
- 工具函數測試：`utilityName.test.ts`
- 整合測試：`featureName.integration.test.ts`
- E2E 測試：`scenarioName.e2e.test.ts`

**後端測試：**
- 單元測試：`test_module_name.py`
- 整合測試：`test_integration_feature.py`
- API 測試：`test_api_endpoint.py`
- 服務測試：`test_service_name.py`

### 8.3 腳本文件管理

**專案級腳本目錄 (`script/`)：**
- 所有專案級 `.sh` 腳本文件必須放在 `script/` 目錄下
- 按功能分類到子目錄中
- 腳本文件必須包含標準頭部註釋

**後台專用腳本目錄 (`backend/scripts/`)：**
- 後台服務專用的腳本文件放在 `backend/scripts/` 目錄下
- 包含安裝、服務管理、健康檢查等腳本

**腳本文件頭部註釋模板：**
```bash
#!/bin/bash
# @purpose: [簡潔說明腳本的用途和功能]
# @author: DanielChung and AI
# @createdAt: [YYYY-MM-DD]
# @lastModified: [YYYY-MM-DD]
# @usage: [使用方法和參數說明]
```

**腳本目錄說明：**
- `script/admin/` - 管理員相關腳本 (密碼重置、系統重置等)
- `script/dev/` - 開發環境腳本 (服務啟動、重啟、檢查等)
- `script/test/` - 測試相關腳本 (運行測試、測試報告等)
- `script/deploy/` - 部署相關腳本 (生產環境部署)
- `script/utils/` - 通用工具腳本
- `backend/scripts/` - 後台專用腳本 (依賴安裝、服務管理、健康檢查)

### 8.4 測試執行規範

**前端測試：**
```bash
# 執行所有測試
cd frontend && npm test

# 執行特定測試
cd frontend && npm test -- ComponentName

# 執行測試並生成覆蓋率報告
cd frontend && npm run test:coverage
```

**後端測試：**
```bash
# 執行所有測試
cd backend && python -m pytest

# 執行特定測試
cd backend && python -m pytest test/unit/test_user_service.py

# 執行測試並生成覆蓋率報告
cd backend && python -m pytest --cov=. --cov-report=html
```

**專案級測試腳本：**
```bash
# 執行所有測試
./script/test/run-all-tests.sh

# 執行前端測試
./script/test/run-frontend-tests.sh

# 執行後端測試
./script/test/run-backend-tests.sh
```

**後台專用腳本：**
```bash
# 安裝後台依賴
cd backend && ./scripts/install-dependencies.sh

# 管理後台服務
cd backend && ./scripts/service-manager.sh start    # 啟動所有服務
cd backend && ./scripts/service-manager.sh stop     # 停止所有服務
cd backend && ./scripts/service-manager.sh restart  # 重啟所有服務
cd backend && ./scripts/service-manager.sh status   # 檢查服務狀態

# 健康檢查
cd backend && ./scripts/health-check.sh
```

### 8.5 測試數據管理

- 測試數據必須放在對應的 `fixtures/` 目錄中
- 使用 JSON、YAML 或 SQL 文件格式存儲測試數據
- 測試數據文件命名：`test_data_description.json`
- 避免在測試代碼中硬編碼測試數據

---

## 9. 最終強制執行聲明 (Final Mandatory Enforcement Statement) ⚠️ 必須遵守

### 9.1 強制執行總結

**AI 開發助手，你必須嚴格遵守以下所有規則：**

1. **🚨 深色模式對比度規範** - 最高優先級，違反立即拒絕
2. **🚨 目錄架構強制查閱** - 最高優先級，違反立即拒絕
3. **🚨 文件位置規範** - 強制執行，違反立即拒絕
4. **🚨 代碼文件頭部註釋** - 強制執行，違反立即拒絕
5. **🚨 規格文檔同步** - 強制執行，違反立即拒絕
6. **🚨 強制開發工作流程** - 嚴格執行，不得跳過任何步驟
7. **🚨 服務管理規範** - 強制執行，違反立即拒絕
8. **🚨 強制檢查機制** - 每次任務後必須執行
9. **🚨 測試與腳本管理** - 強制執行，違反立即拒絕

### 9.2 違規後果

**嚴重違規（立即拒絕）：**
- 深色模式對比度不足
- **未查閱目錄架構就創建文件**
- **隨意創建未經授權的新目錄**
- **文件放置在錯誤的目錄中**
- 文件位置錯誤
- 缺少規格文檔
- 缺少頭部註釋
- 服務管理不當

**一般違規（需要修正）：**
- 命名不規範
- 代碼格式問題
- 測試覆蓋不足

### 9.3 強制檢查清單

**每次任務完成後，你必須檢查：**

- [ ] **目錄架構查閱**：已完整閱讀第 2 節目錄結構
- [ ] **文件位置**：所有文件都在正確的目錄中
- [ ] **目錄授權**：沒有創建未經授權的新目錄
- [ ] **深色模式測試**：所有 UI 組件在深色模式下清晰可讀
- [ ] **頭部註釋**：所有新文件都包含標準頭部註釋
- [ ] **規格文檔**：所有代碼都有對應的規格文檔
- [ ] **服務管理**：所有服務都使用 screen 會話管理
- [ ] **命名規範**：所有文件、組件、服務都使用標準命名
- [ ] **工作流程**：嚴格遵循 5 步強制開發工作流程
- [ ] **測試覆蓋**：所有新功能都有對應的測試

### 9.4 最終聲明

**AI 開發助手，這份指南是你的強制性開發規範。違反任何規則都將導致代碼審查失敗。你必須在每次任務中嚴格遵守這些規則，並在完成後進行強制自我檢查。**

**記住：**
- 所有規則都是**強制性**的
- 沒有例外情況
- 違規的代碼將被拒絕
- 必須重新開發符合規範的代碼

**現在開始嚴格執行這些規範！**