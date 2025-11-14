# AAM 管理系統 - 頁面佈局設計 (UI/UX Layout Design)

**版本**: v1.0  
**創建日期**: 2025-11-13  
**最後更新**: 2025-11-13  
**作者**:Daniel Chung

---

## 📋 目錄

1. [整體佈局架構](#1-整體佈局架構)
2. [導航結構](#2-導航結構)
3. [功能模塊頁面佈局](#3-功能模塊頁面佈局)
4. [響應式設計](#4-響應式設計)
5. [組件設計規範](#5-組件設計規範)
6. [顏色與主題](#6-顏色與主題)

---

## 1. 整體佈局架構

### 1.1 主佈局結構

```mermaid
flowchart TB
    subgraph "頂部導航欄 (Top Navigation)"
        A1[Logo + 系統名稱]
        A2[用戶信息]
        A3[通知中心]
        A4[設置]
        A5[登出]
    end
    
    subgraph "側邊欄 (Sidebar)"
        B1[儀表盤]
        B2[LLM Provider]
        B3[服務管理]
        B4[版本部署]
        B5[日誌管理]
        B6[安全管理]
        B7[系統設置]
    end
    
    subgraph "主內容區 (Main Content)"
        C1[麵包屑導航]
        C2[頁面標題]
        C3[操作工具欄]
        C4[內容區域]
        C5[分頁/底部信息]
    end
    
    A1 --> B1
    A1 --> C1
    B1 --> C4
    B2 --> C4
    B3 --> C4
    B4 --> C4
    B5 --> C4
    B6 --> C4
    B7 --> C4
    
    classDef topClass fill:#1976d2,stroke:#0d47a1,stroke-width:2px,color:#fff
    classDef sideClass fill:#f5f5f5,stroke:#bdbdbd,stroke-width:2px
    classDef contentClass fill:#ffffff,stroke:#e0e0e0,stroke-width:2px
    
    class A1,A2,A3,A4,A5 topClass
    class B1,B2,B3,B4,B5,B6,B7 sideClass
    class C1,C2,C3,C4,C5 contentClass
```

### 1.2 佈局尺寸規範

| 區域 | 寬度/高度 | 說明 |
|------|----------|------|
| 頂部導航欄 | 100% × 64px | 固定高度，全寬 |
| 側邊欄 | 240px × 100% | 固定寬度，可收起 |
| 主內容區 | 剩餘空間 | 自適應寬度 |
| 最小視窗寬度 | 1280px | 響應式斷點 |

---

## 2. 導航結構

### 2.1 導航層級結構

```mermaid
graph TD
    A[儀表盤<br/>Dashboard] 
    B[LLM Provider 管理]
    C[系統服務監管]
    D[版本與部署]
    E[日誌管理]
    F[安全管理]
    G[系統設置]
    
    B --> B1[Provider 列表]
    B --> B2[模型配置]
    B --> B3[Provider 測試]
    
    C --> C1[服務列表]
    C --> C2[服務控制]
    C --> C3[資源監控]
    
    D --> D1[版本列表]
    D --> D2[部署歷史]
    D --> D3[版本比較]
    
    E --> E1[實時日誌]
    E --> E2[日誌搜索]
    E --> E3[日誌導出]
    
    F --> F1[Token 管理]
    F --> F2[企業認證]
    F --> F3[訪問控制]
    F --> F4[操作審計]
    
    G --> G1[環境配置]
    G --> G2[通知設置]
    G --> G3[備份設置]
    
    classDef mainNav fill:#2196f3,stroke:#1976d2,stroke-width:2px,color:#fff
    classDef subNav fill:#e3f2fd,stroke:#90caf9,stroke-width:2px
    
    class A,B,C,D,E,F,G mainNav
    class B1,B2,B3,C1,C2,C3,D1,D2,D3,E1,E2,E3,F1,F2,F3,F4,G1,G2,G3 subNav
```

### 2.2 導航菜單設計

**一級菜單**（側邊欄）:
- 📊 儀表盤
- 🤖 LLM Provider
- 🖥️ 服務管理
- 🚀 版本部署
- 📝 日誌管理
- 🔒 安全管理
- ⚙️ 系統設置

**二級菜單**（展開顯示）:
- 在對應一級菜單下顯示子菜單項
- 支持摺疊/展開
- 當前頁面高亮顯示

---

## 3. 功能模塊頁面佈局

### 3.1 儀表盤 (Dashboard)

```mermaid
flowchart TB
    subgraph "儀表盤佈局"
        A[頂部統計卡片區]
        B[服務狀態監控]
        C[資源使用圖表]
        D[最近操作記錄]
        E[系統健康狀態]
    end
    
    subgraph "統計卡片 (4 列)"
        A1[運行服務數<br/>8/10]
        A2[LLM Provider<br/>3 Active]
        A3[當前版本<br/>v1.2.0]
        A4[系統負載<br/>65%]
    end
    
    subgraph "監控區域 (2 列)"
        B[服務狀態列表<br/>左側 50%]
        C[資源使用圖表<br/>右側 50%]
    end
    
    subgraph "底部區域 (2 列)"
        D[最近操作記錄<br/>左側 50%]
        E[系統健康狀態<br/>右側 50%]
    end
    
    A --> A1
    A --> A2
    A --> A3
    A --> A4
    
    A --> B
    A --> C
    
    B --> D
    C --> E
    
    classDef cardClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef monitorClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef infoClass fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    
    class A1,A2,A3,A4 cardClass
    class B,C monitorClass
    class D,E infoClass
```

**佈局說明**:
- **頂部**: 4 個統計卡片（響應式：桌面 4 列，平板 2 列，手機 1 列）
- **中部**: 服務狀態監控 + 資源使用圖表（並排顯示）
- **底部**: 最近操作記錄 + 系統健康狀態（並排顯示）

### 3.2 LLM Provider 管理頁面

```mermaid
flowchart LR
    subgraph "Provider 管理佈局"
        A[左側: Provider 列表<br/>30%]
        B[右側: 配置詳情<br/>70%]
    end
    
    subgraph "Provider 列表"
        A1[Qwen<br/>Active]
        A2[Gemini<br/>Active]
        A3[Ollama<br/>Inactive]
        A4[+ 添加 Provider]
    end
    
    subgraph "配置詳情區"
        B1[Provider 基本信息]
        B2[模型列表表格]
        B3[模型配置表單]
        B4[操作按鈕組]
    end
    
    A --> A1
    A --> A2
    A --> A3
    A --> A4
    
    A1 --> B
    A2 --> B
    A3 --> B
    
    B --> B1
    B --> B2
    B --> B3
    B --> B4
    
    classDef listClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef detailClass fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    
    class A,A1,A2,A3,A4 listClass
    class B,B1,B2,B3,B4 detailClass
```

**佈局說明**:
- **左側面板**: Provider 列表（可摺疊）
  - 顯示所有 Provider
  - 顯示狀態指示器（Active/Inactive）
  - 支持添加新 Provider
- **右側面板**: 選中 Provider 的詳細配置
  - Provider 基本信息
  - 模型列表（表格）
  - 模型配置表單（可編輯）
  - 操作按鈕（保存、測試、啟用/禁用）

### 3.3 服務管理頁面

```mermaid
flowchart TB
    subgraph "服務管理佈局"
        A[服務列表表格]
        B[服務詳情面板]
        C[操作工具欄]
    end
    
    subgraph "服務列表 (表格)"
        A1[服務名稱 | 狀態 | 版本 | CPU | 內存 | 操作]
        A2[AAM Service | 🟢 Running | v1.2.0 | 45% | 512MB | 啟動/停止]
        A3[ChromaDB | 🟢 Running | latest | 12% | 256MB | 重啟]
        A4[PostgreSQL | 🟢 Running | 15 | 8% | 128MB | 查看日誌]
    end
    
    subgraph "詳情面板 (抽屜/側邊欄)"
        B1[服務基本信息]
        B2[資源使用圖表]
        B3[實時日誌預覽]
        B4[操作歷史]
    end
    
    A --> A1
    A --> A2
    A --> A3
    A --> A4
    
    A2 --> B
    A3 --> B
    A4 --> B
    
    B --> B1
    B --> B2
    B --> B3
    B --> B4
    
    classDef tableClass fill:#ffffff,stroke:#e0e0e0,stroke-width:2px
    classDef detailClass fill:#f5f5f5,stroke:#bdbdbd,stroke-width:2px
    
    class A,A1,A2,A3,A4 tableClass
    class B,B1,B2,B3,B4 detailClass
```

**佈局說明**:
- **主區域**: 服務列表表格
  - 顯示所有服務的狀態、版本、資源使用
  - 每行有操作按鈕（啟動/停止/重啟/查看日誌）
- **詳情面板**: 點擊服務後從右側滑出
  - 服務基本信息
  - 資源使用實時圖表
  - 實時日誌預覽
  - 操作歷史記錄

### 3.4 版本部署頁面

```mermaid
flowchart TB
    subgraph "版本部署佈局"
        A[版本列表區域]
        B[部署配置區域]
        C[部署歷史區域]
    end
    
    subgraph "版本列表 (左側 40%)"
        A1[版本卡片 v1.2.0<br/>Active]
        A2[版本卡片 v1.1.0<br/>Available]
        A3[版本卡片 v1.0.0<br/>Deprecated]
        A4[+ 創建新版本]
    end
    
    subgraph "部署配置 (右側 60%)"
        B1[版本詳情]
        B2[部署策略選擇]
        B3[配置預覽]
        B4[部署按鈕]
    end
    
    subgraph "部署歷史 (底部 100%)"
        C1[歷史記錄表格]
    end
    
    A --> A1
    A --> A2
    A --> A3
    A --> A4
    
    A1 --> B
    A2 --> B
    A3 --> B
    
    B --> B1
    B --> B2
    B --> B3
    B --> B4
    
    B --> C
    C --> C1
    
    classDef versionClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef deployClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef historyClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class A,A1,A2,A3,A4 versionClass
    class B,B1,B2,B3,B4 deployClass
    class C,C1 historyClass
```

**佈局說明**:
- **左側**: 版本列表（卡片式）
  - 顯示版本號、狀態、創建時間
  - 當前活動版本高亮
  - 支持創建新版本
- **右側**: 部署配置區域
  - 選中版本的詳細信息
  - 部署策略選擇（藍綠/滾動/金絲雀）
  - 配置預覽
  - 部署操作按鈕
- **底部**: 部署歷史表格
  - 顯示所有部署記錄
  - 支持篩選和搜索

### 3.5 日誌管理頁面

```mermaid
flowchart TB
    subgraph "日誌管理佈局"
        A[日誌查看器]
        B[過濾器面板]
        C[日誌操作欄]
    end
    
    subgraph "過濾器 (頂部)"
        B1[服務選擇]
        B2[日誌級別]
        B3[時間範圍]
        B4[關鍵詞搜索]
        B5[搜索按鈕]
    end
    
    subgraph "日誌查看器 (主區域)"
        A1[實時日誌流<br/>可滾動]
        A2[日誌行<br/>時間戳 | 級別 | 服務 | 消息]
    end
    
    subgraph "操作欄 (底部)"
        C1[暫停/繼續]
        C2[清空日誌]
        C3[導出日誌]
        C4[下載日誌]
    end
    
    B --> B1
    B --> B2
    B --> B3
    B --> B4
    B --> B5
    
    B --> A
    A --> A1
    A1 --> A2
    
    A --> C
    C --> C1
    C --> C2
    C --> C3
    C --> C4
    
    classDef filterClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef logClass fill:#263238,stroke:#37474f,stroke-width:2px,color:#fff
    classDef actionClass fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    
    class B,B1,B2,B3,B4,B5 filterClass
    class A,A1,A2 logClass
    class C,C1,C2,C3,C4 actionClass
```

**佈局說明**:
- **頂部**: 過濾器工具欄
  - 服務選擇下拉框
  - 日誌級別選擇（DEBUG/INFO/WARNING/ERROR）
  - 時間範圍選擇器
  - 關鍵詞搜索框
- **主區域**: 日誌查看器（深色背景）
  - 實時日誌流（WebSocket）
  - 支持自動滾動
  - 不同級別使用不同顏色
  - 支持複製日誌行
- **底部**: 操作按鈕欄
  - 暫停/繼續實時日誌
  - 清空顯示
  - 導出/下載日誌

### 3.6 安全管理頁面

```mermaid
flowchart TB
    subgraph "安全管理佈局"
        A[Tab 標籤頁]
    end
    
    subgraph "Tab 1: Token 管理"
        A1[Token 列表表格]
        A2[發行 Token 表單]
        A3[Token 詳情面板]
    end
    
    subgraph "Tab 2: 企業認證"
        B1[企業認證配置表單]
        B2[認證狀態顯示]
        B3[測試連接按鈕]
    end
    
    subgraph "Tab 3: 訪問控制"
        C1[IP 白名單列表]
        C2[用戶權限管理]
        C3[角色配置]
    end
    
    subgraph "Tab 4: 操作審計"
        D1[審計日誌表格]
        D2[審計詳情面板]
        D3[導出審計報告]
    end
    
    A --> A1
    A --> A2
    A --> A3
    
    A --> B1
    A --> B2
    A --> B3
    
    A --> C1
    A --> C2
    A --> C3
    
    A --> D1
    A --> D2
    A --> D3
    
    classDef tabClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef contentClass fill:#ffffff,stroke:#e0e0e0,stroke-width:2px
    
    class A tabClass
    class A1,A2,A3,B1,B2,B3,C1,C2,C3,D1,D2,D3 contentClass
```

**佈局說明**:
- **Tab 標籤頁結構**:
  1. **Token 管理**: Token 列表 + 發行表單
  2. **企業認證**: 配置表單 + 狀態顯示
  3. **訪問控制**: IP 白名單 + 權限管理
  4. **操作審計**: 審計日誌表格 + 詳情面板

---

## 4. 響應式設計

### 4.1 響應式斷點

```mermaid
flowchart LR
    A[手機<br/>< 768px] --> B[平板<br/>768px - 1024px]
    B --> C[桌面<br/>1024px - 1440px]
    C --> D[大屏<br/>> 1440px]
    
    A --> A1[單列佈局<br/>側邊欄收起]
    B --> B1[2 列佈局<br/>側邊欄可收起]
    C --> C1[3-4 列佈局<br/>側邊欄展開]
    D --> D1[4+ 列佈局<br/>側邊欄展開]
    
    classDef mobileClass fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef tabletClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef desktopClass fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef largeClass fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    
    class A,A1 mobileClass
    class B,B1 tabletClass
    class C,C1 desktopClass
    class D,D1 largeClass
```

### 4.2 響應式佈局規則

| 設備類型 | 寬度範圍 | 側邊欄 | 主內容區 | 列數 |
|---------|---------|--------|---------|------|
| 手機 | < 768px | 隱藏（抽屜式） | 100% | 1 列 |
| 平板 | 768px - 1024px | 可收起 | 剩餘空間 | 2 列 |
| 桌面 | 1024px - 1440px | 展開 | 剩餘空間 | 3-4 列 |
| 大屏 | > 1440px | 展開 | 剩餘空間 | 4+ 列 |

### 4.3 移動端適配

```mermaid
flowchart TD
    A[移動端佈局] --> B[頂部導航欄<br/>固定]
    A --> C[主內容區<br/>可滾動]
    A --> D[底部導航欄<br/>固定]
    
    B --> B1[Logo]
    B --> B2[標題]
    B --> B3[菜單按鈕]
    
    C --> C1[內容區域]
    
    D --> D1[儀表盤]
    D --> D2[服務]
    D --> D3[日誌]
    D --> D4[設置]
    
    classDef topClass fill:#1976d2,stroke:#0d47a1,stroke-width:2px,color:#fff
    classDef contentClass fill:#ffffff,stroke:#e0e0e0,stroke-width:2px
    classDef bottomClass fill:#f5f5f5,stroke:#bdbdbd,stroke-width:2px
    
    class B,B1,B2,B3 topClass
    class C,C1 contentClass
    class D,D1,D2,D3,D4 bottomClass
```

---

## 5. 組件設計規範

### 5.1 通用組件

#### 5.1.1 卡片組件 (Card)

```mermaid
flowchart TB
    A[卡片容器] --> B[卡片標題區]
    A --> C[卡片內容區]
    A --> D[卡片操作區]
    
    B --> B1[標題文字]
    B --> B2[狀態指示器]
    
    C --> C1[主要內容]
    C --> C2[次要信息]
    
    D --> D1[操作按鈕]
    D --> D2[更多操作]
    
    classDef headerClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef contentClass fill:#ffffff,stroke:#e0e0e0,stroke-width:2px
    classDef actionClass fill:#f5f5f5,stroke:#bdbdbd,stroke-width:2px
    
    class B,B1,B2 headerClass
    class C,C1,C2 contentClass
    class D,D1,D2 actionClass
```

#### 5.1.2 表格組件 (Table)

```mermaid
flowchart LR
    A[表格容器] --> B[表格頭部]
    A --> C[表格主體]
    A --> D[表格底部]
    
    B --> B1[列標題]
    B --> B2[排序按鈕]
    B --> B3[篩選按鈕]
    
    C --> C1[數據行]
    C --> C2[操作列]
    
    D --> D1[分頁器]
    D --> D2[總數顯示]
    
    classDef headerClass fill:#f5f5f5,stroke:#bdbdbd,stroke-width:2px
    classDef bodyClass fill:#ffffff,stroke:#e0e0e0,stroke-width:1px
    classDef footerClass fill:#fafafa,stroke:#e0e0e0,stroke-width:2px
    
    class B,B1,B2,B3 headerClass
    class C,C1,C2 bodyClass
    class D,D1,D2 footerClass
```

#### 5.1.3 表單組件 (Form)

```mermaid
flowchart TB
    A[表單容器] --> B[表單標題]
    A --> C[表單字段區]
    A --> D[表單操作區]
    
    C --> C1[輸入框]
    C --> C2[選擇器]
    C --> C3[開關]
    C --> C4[文本域]
    
    D --> D1[保存按鈕]
    D --> D2[取消按鈕]
    D --> D3[重置按鈕]
    
    classDef titleClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef fieldClass fill:#ffffff,stroke:#e0e0e0,stroke-width:2px
    classDef actionClass fill:#f5f5f5,stroke:#bdbdbd,stroke-width:2px
    
    class B titleClass
    class C,C1,C2,C3,C4 fieldClass
    class D,D1,D2,D3 actionClass
```

### 5.2 狀態指示器

```mermaid
flowchart LR
    A[狀態指示器] --> B[運行中<br/>🟢 Green]
    A --> C[已停止<br/>🔴 Red]
    A --> D[錯誤<br/>🟠 Orange]
    A --> E[未知<br/>⚪ Gray]
    
    classDef runningClass fill:#4caf50,stroke:#2e7d32,stroke-width:2px,color:#fff
    classDef stoppedClass fill:#f44336,stroke:#c62828,stroke-width:2px,color:#fff
    classDef errorClass fill:#ff9800,stroke:#f57c00,stroke-width:2px,color:#fff
    classDef unknownClass fill:#9e9e9e,stroke:#616161,stroke-width:2px,color:#fff
    
    class B runningClass
    class C stoppedClass
    class D errorClass
    class E unknownClass
```

---

## 6. 顏色與主題

### 6.1 主色調方案

```mermaid
flowchart TB
    A[顏色主題] --> B[主色調<br/>#1976d2<br/>Blue]
    A --> C[輔助色調<br/>#388e3c<br/>Green]
    A --> D[警告色調<br/>#f57c00<br/>Orange]
    A --> E[錯誤色調<br/>#c62828<br/>Red]
    A --> F[中性色調<br/>#616161<br/>Gray]
    
    classDef primaryClass fill:#1976d2,stroke:#0d47a1,stroke-width:3px,color:#fff
    classDef successClass fill:#4caf50,stroke:#2e7d32,stroke-width:3px,color:#fff
    classDef warningClass fill:#ff9800,stroke:#f57c00,stroke-width:3px,color:#fff
    classDef errorClass fill:#f44336,stroke:#c62828,stroke-width:3px,color:#fff
    classDef neutralClass fill:#9e9e9e,stroke:#616161,stroke-width:3px,color:#fff
    
    class B primaryClass
    class C successClass
    class D warningClass
    class E errorClass
    class F neutralClass
```

### 6.2 顏色使用規範

| 顏色 | 用途 | 示例 |
|------|------|------|
| **主色調 (Blue #1976d2)** | 主要操作按鈕、鏈接、選中狀態 | 保存、提交、主要 CTA |
| **成功色 (Green #4caf50)** | 成功狀態、完成操作 | 服務運行中、操作成功 |
| **警告色 (Orange #ff9800)** | 警告信息、需要注意的狀態 | 資源使用率高、即將過期 |
| **錯誤色 (Red #f44336)** | 錯誤狀態、危險操作 | 服務停止、操作失敗 |
| **中性色 (Gray #616161)** | 次要信息、禁用狀態 | 輔助文字、禁用按鈕 |

### 6.3 深色模式支持

```mermaid
flowchart LR
    A[主題切換] --> B[淺色模式<br/>Light Mode]
    A --> C[深色模式<br/>Dark Mode]
    
    B --> B1[背景: #ffffff]
    B --> B2[文字: #212121]
    B --> B3[邊框: #e0e0e0]
    
    C --> C1[背景: #121212]
    C --> C2[文字: #ffffff]
    C --> C3[邊框: #424242]
    
    classDef lightClass fill:#ffffff,stroke:#e0e0e0,stroke-width:2px,color:#212121
    classDef darkClass fill:#121212,stroke:#424242,stroke-width:2px,color:#ffffff
    
    class B,B1,B2,B3 lightClass
    class C,C1,C2,C3 darkClass
```

---

## 7. 頁面佈局詳細設計

### 7.1 儀表盤詳細佈局

```
┌─────────────────────────────────────────────────────────────┐
│  Top Navigation Bar (64px)                                  │
├──────────┬──────────────────────────────────────────────────┤
│          │  Breadcrumb: 首頁 > 儀表盤                        │
│          │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐            │
│ Sidebar  │  │ 運行 │ │ LLM  │ │ 當前 │ │ 系統 │            │
│ (240px)  │  │ 服務 │ │ Prov │ │ 版本 │ │ 負載 │            │
│          │  │  8/10│ │  3   │ │v1.2.0│ │ 65%  │            │
│ 📊 儀表盤│  └──────┘ └──────┘ └──────┘ └──────┘            │
│ 🤖 LLM   │                                                    │
│ 🖥️ 服務  │  ┌──────────────────┐ ┌──────────────────┐    │
│ 🚀 版本  │  │  服務狀態監控    │ │  資源使用圖表    │    │
│ 📝 日誌  │  │                  │ │                  │    │
│ 🔒 安全  │  │  [服務列表]      │ │  [CPU/內存圖表]  │    │
│ ⚙️ 設置  │  └──────────────────┘ └──────────────────┘    │
│          │                                                    │
│          │  ┌──────────────────┐ ┌──────────────────┐    │
│          │  │  最近操作記錄    │ │  系統健康狀態    │    │
│          │  │                  │ │                  │    │
│          │  │  [操作日誌列表]  │ │  [健康指標]      │    │
│          │  └──────────────────┘ └──────────────────┘    │
└──────────┴──────────────────────────────────────────────────┘
```

### 7.2 LLM Provider 管理詳細佈局

```
┌─────────────────────────────────────────────────────────────┐
│  Top Navigation Bar                                          │
├──────────┬──────────────────────────────────────────────────┤
│          │  Breadcrumb: LLM Provider > Qwen                 │
│          │                                                    │
│ Sidebar  │  ┌──────────┐ ┌──────────────────────────────┐ │
│          │  │ Provider │ │  配置詳情                      │ │
│          │  │ 列表     │ │                                │ │
│          │  │          │ │  Provider: Qwen                │ │
│          │  │ [Qwen]   │ │  Status: Active               │ │
│          │  │  Active  │ │                                │ │
│          │  │          │ │  ┌──────────────────────────┐ │ │
│          │  │ [Gemini] │ │  │ 模型列表                  │ │ │
│          │  │  Active  │ │  │                          │ │ │
│          │  │          │ │  │  [表格: 模型配置]         │ │ │
│          │  │ [Ollama] │ │  └──────────────────────────┘ │ │
│          │  │ Inactive │ │                                │ │
│          │  │          │ │  ┌──────────────────────────┐ │ │
│          │  │ [+ 添加] │ │  │ 模型配置表單             │ │ │
│          │  └──────────┘ │  │                          │ │ │
│          │                │  │  [表單字段]              │ │ │
│          │                │  └──────────────────────────┘ │ │
│          │                │                                │ │
│          │                │  [保存] [測試] [啟用/禁用]    │ │
└──────────┴──────────────────────────────────────────────────┘
```

### 7.3 服務管理詳細佈局

```
┌─────────────────────────────────────────────────────────────┐
│  Top Navigation Bar                                          │
├──────────┬──────────────────────────────────────────────────┤
│          │  Breadcrumb: 服務管理                             │
│          │  [刷新] [批量操作]                                │
│ Sidebar  │                                                    │
│          │  ┌──────────────────────────────────────────────┐ │
│          │  │ 服務名稱 │ 狀態 │ 版本 │ CPU │ 內存 │ 操作 │ │
│          │  ├──────────┼──────┼──────┼─────┼──────┼──────┤ │
│          │  │ AAM      │ 🟢   │ v1.2 │ 45% │ 512M │ [操作]│ │
│          │  │ Service  │      │      │     │      │      │ │
│          │  ├──────────┼──────┼──────┼─────┼──────┼──────┤ │
│          │  │ ChromaDB │ 🟢   │ latest│ 12% │ 256M │ [操作]│ │
│          │  ├──────────┼──────┼──────┼─────┼──────┼──────┤ │
│          │  │ PostgreSQL│ 🟢 │ 15   │ 8%  │ 128M │ [操作]│ │
│          │  └──────────────────────────────────────────────┘ │
│          │                                                    │
│          │  [分頁器]                                          │
│          │                                                    │
│          │  ┌──────────────────────────────────────────────┐ │
│          │  │ 服務詳情面板 (抽屜，從右側滑出)              │ │
│          │  │                                                │ │
│          │  │  基本信息 | 資源監控 | 實時日誌 | 操作歷史    │ │
│          │  └──────────────────────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────────┘
```

### 7.4 版本部署詳細佈局

```
┌─────────────────────────────────────────────────────────────┐
│  Top Navigation Bar                                          │
├──────────┬──────────────────────────────────────────────────┤
│          │  Breadcrumb: 版本部署                             │
│          │                                                    │
│ Sidebar  │  ┌──────────┐ ┌──────────────────────────────┐ │
│          │  │ 版本列表 │ │  部署配置                      │ │
│          │  │          │ │                              │ │
│          │  │ ┌──────┐ │ │  版本: v1.2.0                │ │
│          │  │ │v1.2.0│ │ │  狀態: Active                │ │
│          │  │ │Active│ │ │  創建時間: 2025-11-13        │ │
│          │  │ └──────┘ │ │                              │ │
│          │  │          │ │  部署策略:                    │ │
│          │  │ ┌──────┐ │ │  ○ 藍綠部署                   │ │
│          │  │ │v1.1.0│ │ │  ○ 滾動更新                   │ │
│          │  │ │Avail │ │ │  ○ 金絲雀部署                 │ │
│          │  │ └──────┘ │ │                              │ │
│          │  │          │ │  [配置預覽]                    │ │
│          │  │ ┌──────┐ │ │                              │ │
│          │  │ │v1.0.0│ │ │  [部署] [取消]               │ │
│          │  │ │Deprec│ │ │                              │ │
│          │  │ └──────┘ │ └──────────────────────────────┘ │
│          │  │          │                                    │
│          │  │ [+ 創建] │  ┌──────────────────────────────┐ │
│          │  └──────────┘  │  部署歷史                      │ │
│          │                │                              │ │
│          │                │  [歷史記錄表格]              │ │
│          │                └──────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────────┘
```

### 7.5 日誌管理詳細佈局

```
┌─────────────────────────────────────────────────────────────┐
│  Top Navigation Bar                                          │
├──────────┬──────────────────────────────────────────────────┤
│          │  Breadcrumb: 日誌管理                             │
│          │                                                    │
│ Sidebar  │  ┌──────────────────────────────────────────────┐ │
│          │  │ 過濾器工具欄                                  │ │
│          │  │ [服務▼] [級別▼] [時間範圍] [搜索] [搜索按鈕]│ │
│          │  └──────────────────────────────────────────────┘ │
│          │                                                    │
│          │  ┌──────────────────────────────────────────────┐ │
│          │  │ 日誌查看器 (深色背景)                         │ │
│          │  │                                                │ │
│          │  │  2025-11-13 10:00:00 [INFO] AAM Service: ...  │ │
│          │  │  2025-11-13 10:00:01 [DEBUG] Memory: ...     │ │
│          │  │  2025-11-13 10:00:02 [WARN] Connection: ...  │ │
│          │  │  2025-11-13 10:00:03 [ERROR] Database: ...   │ │
│          │  │  ... (實時滾動)                               │ │
│          │  └──────────────────────────────────────────────┘ │
│          │                                                    │
│          │  ┌──────────────────────────────────────────────┐ │
│          │  │ 操作欄                                         │ │
│          │  │ [暫停] [清空] [導出] [下載]                   │ │
│          │  └──────────────────────────────────────────────┘ │
└──────────┴──────────────────────────────────────────────────┘
```

---

## 8. UI 組件庫建議

### 8.1 推薦的 UI 框架

#### 選項 1: Ant Design (推薦)
- **優點**: 
  - 組件豐富，文檔完善
  - 企業級設計規範
  - 支持深色模式
  - TypeScript 支持良好
- **適用場景**: 企業管理後台、數據密集型應用

#### 選項 2: Material-UI (MUI)
- **優點**:
  - Material Design 設計語言
  - 組件豐富，主題定制靈活
  - 響應式設計優秀
- **適用場景**: 現代化 Web 應用

#### 選項 3: Element Plus (Vue)
- **優點**:
  - 如果使用 Vue 3
  - 組件豐富，中文文檔
  - 企業級應用支持
- **適用場景**: Vue 技術棧項目

### 8.2 圖表庫建議

- **ECharts**: 功能強大，適合複雜圖表
- **Recharts**: React 友好，組件化設計
- **Chart.js**: 輕量級，易於使用

---

## 9. 交互設計規範

### 9.1 操作反饋

```mermaid
flowchart LR
    A[用戶操作] --> B{操作類型}
    B -->|成功| C[成功提示<br/>綠色 Toast]
    B -->|失敗| D[錯誤提示<br/>紅色 Toast]
    B -->|警告| E[警告提示<br/>橙色 Toast]
    B -->|加載| F[加載動畫<br/>Spinner]
    
    classDef successClass fill:#4caf50,stroke:#2e7d32,stroke-width:2px,color:#fff
    classDef errorClass fill:#f44336,stroke:#c62828,stroke-width:2px,color:#fff
    classDef warningClass fill:#ff9800,stroke:#f57c00,stroke-width:2px,color:#fff
    classDef loadingClass fill:#2196f3,stroke:#1976d2,stroke-width:2px,color:#fff
    
    class C successClass
    class D errorClass
    class E warningClass
    class F loadingClass
```

### 9.2 確認對話框

對於危險操作（如停止服務、刪除版本），必須顯示確認對話框：

```mermaid
flowchart TD
    A[觸發危險操作] --> B[顯示確認對話框]
    B --> C{用戶選擇}
    C -->|確認| D[執行操作]
    C -->|取消| E[取消操作]
    
    D --> F[顯示操作結果]
    E --> G[關閉對話框]
    
    classDef confirmClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef actionClass fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef cancelClass fill:#ffebee,stroke:#c62828,stroke-width:2px
    
    class B confirmClass
    class D,F actionClass
    class E,G cancelClass
```

---

## 10. 實施建議

### 10.1 技術棧推薦

**前端框架**:
- React 18+ + TypeScript
- Ant Design 5.x
- React Router 6.x
- Zustand (狀態管理)
- Axios (HTTP 客戶端)
- ECharts (圖表)

**構建工具**:
- Vite (推薦) 或 Create React App
- ESLint + Prettier (代碼規範)

### 10.2 開發階段

**階段一**: 基礎佈局
- [ ] 主佈局框架（頂部導航 + 側邊欄 + 主內容區）
- [ ] 路由配置
- [ ] 響應式適配

**階段二**: 核心頁面
- [ ] 儀表盤頁面
- [ ] 服務管理頁面
- [ ] 日誌查看頁面

**階段三**: 完整功能
- [ ] LLM Provider 管理頁面
- [ ] 版本部署頁面
- [ ] 安全管理頁面

**階段四**: 優化與增強
- [ ] 深色模式
- [ ] 動畫效果
- [ ] 性能優化

---

## 11. 頁面佈局示例代碼結構

### 11.1 主佈局組件結構

```typescript
// src/layouts/MainLayout.tsx
interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <TopNavigation />
      <Layout>
        <Sidebar />
        <Layout.Content>
          <Breadcrumb />
          <PageHeader />
          <Toolbar />
          <ContentArea>{children}</ContentArea>
        </Layout.Content>
      </Layout>
    </Layout>
  );
};
```

### 11.2 路由配置示例

```typescript
// src/routes/index.tsx
const routes = [
  {
    path: '/',
    element: <MainLayout />,
    children: [
      { path: 'dashboard', element: <DashboardPage /> },
      { path: 'llm-providers', element: <LLMProviderPage /> },
      { path: 'services', element: <ServiceManagementPage /> },
      { path: 'deployments', element: <DeploymentPage /> },
      { path: 'logs', element: <LogViewerPage /> },
      { path: 'security', element: <SecurityPage /> },
    ],
  },
];
```

---

**最後更新**: 2025-11-13  
**維護者**:Daniel Chung

