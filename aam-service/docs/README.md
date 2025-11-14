# AAM 服務文檔索引

本文檔目錄包含 AAM 服務的所有規範和指南文檔。

## 📚 文檔列表

### 開發規範

1. **[AI 開發指導手冊](./AiDevelopmentGuide.md)**
   - 強制性開發規則
   - 目錄結構規範
   - 代碼文件規範
   - 深色模式規範
   - 服務管理規範

2. **[Git 版本管理與團隊協作規範](./GIT_WORKFLOW.md)** ⭐ **新增**
   - Checkout/Checkin 規範
   - 分支策略
   - 提交信息規範
   - Pull Request 流程
   - 代碼審查規範
   - 衝突解決指南

3. **[GitHub 設置指南](./GITHUB_SETUP.md)**
   - GitHub 倉庫設置步驟
   - 認證配置
   - 常見問題解答

4. **[LLM Provider 配置指南](./LLM_Provider配置指南.md)** ⭐ **新增**
   - LLM Provider 統一配置管理
   - API Key 設置方式
   - 環境變量配置
   - 未來 MoE 擴展支持

5. **[AAM 企業安全認證管理手冊](./AAM企業安全認證管理手冊.md)** ⭐ **新增**
   - MCP Server 調用指南
   - Token 發行與驗證
   - 企業級認證（服務器間相互認證）
   - 前端集成示例
   - 管理員操作指南
   - 安全管理最佳實踐

> **📌 注意**: AAM 管理系統相關文檔已移至 `../aam-admin/docs/`：
> - [AAM 管理系統 - 系統設計規格](../aam-admin/docs/AAM管理系統-SD.md)
> - [AAM 管理系統 - 頁面佈局設計](../aam-admin/docs/AAM管理系統-頁面佈局設計.md)

### 系統設計文檔

4. **[AAM 系統架構文檔](./AAM%20(AI-Augmented%20Memory)%20SA%20v1.md)**
   - 系統架構設計
   - 核心組件說明
   - 開發規劃

5. **[AAM Agent 系統設計規格](./AAM%20Agent%20SD%20v1.md)**
   - 組件規格
   - MCP 協議定義
   - 數據庫 Schema
   - 實施階段

## 🚀 快速開始

### 新團隊成員入門

1. **閱讀開發規範**
   - 先閱讀 [AI 開發指導手冊](./AiDevelopmentGuide.md)
   - 然後閱讀 [Git 版本管理規範](./GIT_WORKFLOW.md)

2. **設置開發環境**
   - 參考 [GitHub 設置指南](./GITHUB_SETUP.md)
   - 配置 Git 和 GitHub

3. **了解系統架構**
   - 閱讀 [AAM 系統架構文檔](./AAM%20(AI-Augmented%20Memory)%20SA%20v1.md)
   - 閱讀 [AAM Agent 系統設計規格](./AAM%20Agent%20SD%20v1.md)

## 📋 文檔更新記錄

| 日期 | 文檔 | 版本 | 更新內容 |
|------|------|------|---------|
| 2025-11-13 | AAM 企業安全認證管理手冊 | v1.0 | 初始創建 |
| 2025-11-13 | AAM 管理系統文檔 | - | 已移至 `../aam-admin/docs/` |
| 2025-11-13 | LLM Provider 配置指南 | v1.0 | 初始創建 |
| 2025-11-12 | Git 版本管理規範 | v1.0 | 初始創建 |
| 2025-11-12 | GitHub 設置指南 | v1.0 | 初始創建 |
| 2025-11-12 | AI 開發指導手冊 | v2.0 | 已存在 |

## 🔍 文檔查找指南

### 按主題查找

- **開發規範** → [AI 開發指導手冊](./AiDevelopmentGuide.md)
- **版本管理** → [Git 版本管理規範](./GIT_WORKFLOW.md)
- **GitHub 設置** → [GitHub 設置指南](./GITHUB_SETUP.md)
- **LLM配置** → [LLM Provider 配置指南](./LLM_Provider配置指南.md)
- **MCP/Token/企業認證** → [AAM 企業安全認證管理手冊](./AAM企業安全認證管理手冊.md)
- **管理系統設計** → [AAM 管理系統 - 系統設計規格](../aam-admin/docs/AAM管理系統-SD.md) 📌 已移至 `aam-admin/docs/`
- **管理系統 UI** → [AAM 管理系統 - 頁面佈局設計](../aam-admin/docs/AAM管理系統-頁面佈局設計.md) 📌 已移至 `aam-admin/docs/`
- **系統架構** → [AAM 系統架構文檔](./AAM%20(AI-Augmented%20Memory)%20SA%20v1.md)
- **系統設計** → [AAM Agent 系統設計規格](./AAM%20Agent%20SD%20v1.md)

### 按角色查找

- **開發者** → 開發規範 + Git 規範
- **前端開發者** → AAM 企業安全認證管理手冊 + [AAM 管理系統頁面佈局設計](../aam-admin/docs/AAM管理系統-頁面佈局設計.md) + 開發規範
- **系統管理員** → AAM 企業安全認證管理手冊 + [AAM 管理系統設計](../aam-admin/docs/AAM管理系統-SD.md) + 環境設置指南
- **新成員** → 所有文檔（按順序閱讀）
- **架構師** → 系統架構文檔 + 系統設計規格
- **項目經理** → 系統架構文檔 + 開發規劃

## ⚠️ 重要提醒

**所有團隊成員必須：**

1. ✅ 閱讀並遵守 [AI 開發指導手冊](./AiDevelopmentGuide.md)
2. ✅ 閱讀並遵守 [Git 版本管理規範](./GIT_WORKFLOW.md)
3. ✅ 在開發前查閱相關文檔
4. ✅ 及時更新文檔（如有變更）

## 📝 文檔貢獻

如需更新或添加文檔：

1. 創建功能分支：`git checkout -b docs/update-documentation`
2. 更新文檔內容
3. 提交更改：`git commit -m "docs: 更新文檔內容"`
4. 創建 Pull Request
5. 等待代碼審查和合併

## 📞 聯繫方式

如有文檔相關問題，請：
- 創建 GitHub Issue
- 聯繫項目維護者
- 在團隊頻道討論

---

**最後更新：2025-11-13**

