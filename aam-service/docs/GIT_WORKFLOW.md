# Git 版本管理與團隊協作規範 (Git Workflow & Team Collaboration Guide) v1.0

## 🚨 強制執行聲明

**所有團隊成員必須嚴格遵守以下 Git 工作流程規範。違反任何規範都將導致代碼審查失敗或合併請求被拒絕。**

---

## 📋 目錄

1. [核心原則](#1-核心原則)
2. [分支策略](#2-分支策略)
3. [Checkout 規範](#3-checkout-規範)
4. [Checkin 規範](#4-checkin-規範)
5. [提交信息規範](#5-提交信息規範)
6. [Pull Request 流程](#6-pull-request-流程)
7. [代碼審查規範](#7-代碼審查規範)
8. [衝突解決](#8-衝突解決)
9. [團隊協作最佳實踐](#9-團隊協作最佳實踐)
10. [常見問題與解決方案](#10-常見問題與解決方案)

---

## 1. 核心原則

### 1.1 強制性原則

**🚨 所有團隊成員必須遵守：**

- ✅ **永遠不要直接推送到 `main` 分支**
- ✅ **所有更改必須通過 Pull Request 進行**
- ✅ **提交前必須先拉取最新代碼**
- ✅ **使用有意義的提交信息**
- ✅ **保持提交歷史清晰和可追溯**
- ✅ **定期同步遠端分支**

### 1.2 工作流程圖

```
main (生產分支)
  ↑
  | (Pull Request + Code Review)
  |
develop (開發主線)
  ↑
  | (合併)
  |
feature/xxx (功能分支)
  ↑
  | (開發)
  |
本地開發
```

---

## 2. 分支策略

### 2.1 分支類型與命名規範

#### 主分支（Main Branches）

| 分支名稱 | 用途 | 保護規則 |
|---------|------|---------|
| `main` | 生產就緒的代碼 | ✅ 受保護，禁止直接推送 |
| `develop` | 開發主線，整合所有功能 | ✅ 受保護，通過 PR 合併 |

#### 功能分支（Feature Branches）

| 分支類型 | 命名規範 | 用途 | 示例 |
|---------|---------|------|------|
| `feature/` | `feature/功能名稱` | 新功能開發 | `feature/mcp-enrich-api` |
| `fix/` | `fix/問題描述` | Bug 修復 | `fix/config-validation-error` |
| `hotfix/` | `hotfix/緊急修復` | 緊急生產修復 | `hotfix/critical-security-patch` |
| `refactor/` | `refactor/重構內容` | 代碼重構 | `refactor/settings-module` |
| `docs/` | `docs/文檔內容` | 文檔更新 | `docs/api-documentation` |
| `test/` | `test/測試內容` | 測試相關 | `test/integration-tests` |

**命名規則：**
- 使用小寫字母和連字符（`-`）
- 描述性且簡潔
- 避免使用特殊字符
- 長度不超過 50 個字符

### 2.2 分支生命週期

```
創建分支 → 開發 → 提交 → 推送 → Pull Request → 代碼審查 → 合併 → 刪除分支
```

---

## 3. Checkout 規範 ⚠️ 強制執行

### 3.1 開始新功能開發（Checkout）

#### 步驟 1：確保本地代碼是最新的

```bash
# 切換到 main 分支
git checkout main

# 拉取最新代碼
git pull origin main

# 如果存在 develop 分支，也同步更新
git checkout develop
git pull origin develop
```

#### 步驟 2：創建功能分支

```bash
# 從 develop 分支創建新功能分支（推薦）
git checkout develop
git checkout -b feature/your-feature-name

# 或從 main 分支創建（如果 develop 不存在）
git checkout main
git checkout -b feature/your-feature-name
```

#### 步驟 3：驗證分支創建

```bash
# 查看當前分支
git branch

# 查看分支狀態
git status

# 確認遠端分支（推送後）
git branch -r
```

### 3.2 Checkout 檢查清單

**在創建新分支前，必須確認：**

- [ ] 當前工作區是乾淨的（`git status` 無未提交更改）
- [ ] 已切換到正確的基礎分支（`main` 或 `develop`）
- [ ] 已拉取最新代碼（`git pull`）
- [ ] 分支命名符合規範
- [ ] 分支名稱描述性且清晰

### 3.3 切換到現有分支

```bash
# 切換到本地分支
git checkout branch-name

# 切換到遠端分支（首次）
git checkout -b local-branch-name origin/remote-branch-name

# 拉取遠端分支的最新更改
git checkout branch-name
git pull origin branch-name
```

### 3.4 常見 Checkout 錯誤與解決

**錯誤 1：工作區有未提交的更改**
```bash
# 解決方案 A：提交更改
git add .
git commit -m "feat: 工作進度保存"

# 解決方案 B：暫存更改（推薦用於臨時切換）
git stash
git checkout other-branch
# 完成後恢復
git checkout original-branch
git stash pop
```

**錯誤 2：分支不存在**
```bash
# 檢查遠端分支
git fetch origin
git branch -r

# 創建並追蹤遠端分支
git checkout -b local-branch origin/remote-branch
```

---

## 4. Checkin 規範 ⚠️ 強制執行

### 4.1 提交前檢查清單

**在每次提交前，必須完成以下檢查：**

- [ ] 代碼已通過本地測試
- [ ] 代碼已通過 lint 檢查
- [ ] 已拉取最新代碼（`git pull`）
- [ ] 沒有合併衝突
- [ ] 提交信息符合規範
- [ ] 沒有提交敏感信息（`.env`、密碼等）
- [ ] 沒有提交臨時文件或調試代碼

### 4.2 標準 Checkin 流程

#### 步驟 1：檢查狀態

```bash
# 查看當前狀態
git status

# 查看更改內容
git diff

# 查看暫存區內容
git diff --cached
```

#### 步驟 2：添加文件到暫存區

```bash
# 添加特定文件
git add path/to/file.py

# 添加所有更改（謹慎使用）
git add .

# 交互式添加（推薦）
git add -p
```

**⚠️ 注意：**
- 不要使用 `git add .` 添加所有文件，除非確認所有更改都是相關的
- 使用 `git add -p` 可以選擇性地添加更改

#### 步驟 3：提交更改

```bash
# 標準提交
git commit -m "feat: 添加 MCP 豐富化 API"

# 詳細提交（推薦）
git commit -m "feat: 添加 MCP 豐富化 API

- 實現 /v1/mcp/enrich 端點
- 添加請求驗證邏輯
- 添加單元測試
- 更新 API 文檔"
```

#### 步驟 4：推送到遠端

```bash
# 首次推送（設置上游分支）
git push -u origin feature/your-feature-name

# 後續推送
git push
```

### 4.3 提交頻率規範

**提交原則：**

- ✅ **頻繁提交**：每完成一個小功能或修復就提交
- ✅ **原子性提交**：每次提交只包含一個邏輯更改
- ✅ **可回滾**：每次提交都應該是可獨立回滾的
- ❌ **避免大提交**：不要累積大量更改後一次性提交
- ❌ **避免無意義提交**：不要提交未完成的代碼

**提交頻率建議：**
- 功能開發：每 2-4 小時提交一次
- Bug 修復：修復完成後立即提交
- 文檔更新：完成一個章節後提交

### 4.4 提交前自動檢查

**使用 Git Hooks（可選但推薦）：**

創建 `.git/hooks/pre-commit`：

```bash
#!/bin/bash
# 運行測試
pytest tests/unit/ || exit 1

# 運行 lint
flake8 src/ || exit 1

# 檢查提交信息格式
commit_msg=$(cat $1)
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?:"; then
    echo "❌ 提交信息格式錯誤，請使用 Conventional Commits 格式"
    exit 1
fi
```

---

## 5. 提交信息規範 ⚠️ 強制執行

### 5.1 Conventional Commits 格式

**標準格式：**

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 5.2 提交類型（Type）

| 類型 | 說明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加用戶認證功能` |
| `fix` | Bug 修復 | `fix: 修復配置驗證錯誤` |
| `docs` | 文檔更新 | `docs: 更新 API 文檔` |
| `style` | 代碼格式（不影響功能） | `style: 格式化代碼` |
| `refactor` | 代碼重構 | `refactor: 重構配置管理模組` |
| `test` | 測試相關 | `test: 添加單元測試` |
| `chore` | 構建/工具變更 | `chore: 更新依賴版本` |
| `perf` | 性能優化 | `perf: 優化數據庫查詢` |
| `ci` | CI/CD 變更 | `ci: 添加 GitHub Actions` |

### 5.3 提交信息示例

#### 簡單提交

```bash
git commit -m "feat: 添加 MCP 豐富化 API"
git commit -m "fix: 修復 ChromaDB 連接問題"
git commit -m "docs: 更新 README 安裝說明"
```

#### 詳細提交（推薦）

```bash
git commit -m "feat(api): 添加 MCP 豐富化端點

實現 /v1/mcp/enrich API 端點，支持：
- Partial MCP 請求驗證
- 向量檢索和上下文豐富化
- 錯誤處理和日誌記錄

相關 Issue: #123"
```

### 5.4 提交信息檢查清單

- [ ] 使用正確的類型前綴（feat, fix, docs 等）
- [ ] 主題行不超過 50 個字符
- [ ] 主題行使用祈使語氣（"添加" 而非 "添加了"）
- [ ] 主題行首字母小寫（除非是專有名詞）
- [ ] 詳細說明在 body 中（可選但推薦）
- [ ] 關聯 Issue 或 PR（如果適用）

---

## 6. Pull Request 流程 ⚠️ 強制執行

### 6.1 創建 Pull Request 前檢查

**必須完成以下步驟：**

- [ ] 代碼已通過所有測試
- [ ] 代碼已通過 lint 檢查
- [ ] 已同步最新代碼（`git pull origin develop`）
- [ ] 已解決所有合併衝突
- [ ] 提交歷史清晰（必要時使用 `git rebase`）
- [ ] PR 描述完整且清晰

### 6.2 標準 PR 流程

#### 步驟 1：同步最新代碼

```bash
# 確保功能分支是最新的
git checkout feature/your-feature-name
git pull origin develop
git rebase develop  # 或 git merge develop
```

#### 步驟 2：推送分支到遠端

```bash
git push origin feature/your-feature-name

# 如果已推送過，使用 force push（謹慎使用）
git push --force-with-lease origin feature/your-feature-name
```

#### 步驟 3：在 GitHub 創建 Pull Request

1. **訪問 GitHub 倉庫**
   - 打開：https://github.com/DanielChung520/aam-service

2. **創建 PR**
   - 點擊「Compare & pull request」
   - 或點擊「Pull requests」→「New pull request」

3. **填寫 PR 信息**
   - **標題**：簡潔描述更改內容
   - **描述**：使用 PR 模板（見下方）
   - **審查者**：指定至少一名審查者
   - **標籤**：添加適當的標籤（feature, bugfix 等）

### 6.3 Pull Request 模板

**PR 描述模板：**

```markdown
## 📋 變更描述
簡要描述此 PR 的變更內容

## 🔗 相關 Issue
關聯的 Issue 編號：#123

## ✅ 檢查清單
- [ ] 代碼已通過所有測試
- [ ] 已添加/更新相關測試
- [ ] 代碼已通過 lint 檢查
- [ ] 文檔已更新（如適用）
- [ ] 提交信息符合規範
- [ ] 無合併衝突

## 🧪 測試說明
描述如何測試此變更

## 📸 截圖（如適用）
如果是 UI 變更，請提供截圖

## 📝 備註
其他需要說明的內容
```

### 6.4 PR 審查流程

1. **創建 PR** → 自動觸發 CI/CD
2. **代碼審查** → 至少一名審查者批准
3. **解決反饋** → 更新代碼並推送
4. **最終審查** → 審查者批准
5. **合併** → Squash and merge（推薦）或 Merge commit

### 6.5 PR 合併規範

**合併選項：**

| 選項 | 說明 | 使用場景 |
|------|------|---------|
| **Squash and merge** | 將所有提交壓縮為一個 | ✅ **推薦** - 保持歷史清晰 |
| **Merge commit** | 創建合併提交 | 保留完整提交歷史 |
| **Rebase and merge** | 線性歷史 | 簡單的功能分支 |

**⚠️ 禁止使用：**
- ❌ 直接推送到 `main` 或 `develop`
- ❌ 未經審查的合併
- ❌ 強制推送（除非特殊情況）

---

## 7. 代碼審查規範 ⚠️ 強制執行

### 7.1 審查者職責

**審查者必須檢查：**

- [ ] 代碼符合項目規範
- [ ] 代碼邏輯正確且清晰
- [ ] 已添加適當的測試
- [ ] 文檔已更新（如適用）
- [ ] 沒有安全問題
- [ ] 性能影響（如適用）
- [ ] 提交信息符合規範

### 7.2 審查反饋規範

**反饋類型：**

- ✅ **批准（Approve）**：代碼可以合併
- 💬 **評論（Comment）**：需要討論但不阻塞
- 🔄 **需要更改（Request Changes）**：必須修改後才能合併

**反饋原則：**

- ✅ 建設性和尊重
- ✅ 具體且可操作
- ✅ 解釋原因
- ❌ 避免個人攻擊
- ❌ 避免過於嚴苛的審查

### 7.3 審查時間規範

- **小型 PR**（< 200 行）：24 小時內審查
- **中型 PR**（200-500 行）：48 小時內審查
- **大型 PR**（> 500 行）：72 小時內審查

---

## 8. 衝突解決 ⚠️ 強制執行

### 8.1 預防衝突

**最佳實踐：**

- ✅ 頻繁拉取最新代碼（每天至少一次）
- ✅ 在開始新功能前先同步代碼
- ✅ 與團隊成員溝通，避免同時修改相同文件
- ✅ 保持功能分支小而專注

### 8.2 解決合併衝突

#### 步驟 1：識別衝突

```bash
# 拉取最新代碼
git pull origin develop

# 如果有衝突，Git 會提示
# CONFLICT (content): Merge conflict in file.py
```

#### 步驟 2：查看衝突文件

```bash
# 查看衝突文件列表
git status

# 查看衝突內容
git diff
```

#### 步驟 3：解決衝突

**衝突標記：**

```
<<<<<<< HEAD
你的更改
=======
遠端的更改
>>>>>>> branch-name
```

**解決方法：**

1. 手動編輯文件，保留需要的代碼
2. 刪除衝突標記（`<<<<<<<`, `=======`, `>>>>>>>`）
3. 保存文件

#### 步驟 4：標記衝突已解決

```bash
# 添加解決後的文件
git add conflicted-file.py

# 完成合併
git commit -m "fix: 解決合併衝突"
```

### 8.3 使用 Rebase 避免衝突

```bash
# 在功能分支上
git checkout feature/your-feature-name

# 同步最新代碼並 rebase
git fetch origin
git rebase origin/develop

# 如果有衝突，解決後繼續
git add .
git rebase --continue

# 強制推送（因為歷史已改寫）
git push --force-with-lease origin feature/your-feature-name
```

---

## 9. 團隊協作最佳實踐

### 9.1 日常工作流程

**每日開始工作：**

```bash
# 1. 拉取最新代碼
git checkout develop
git pull origin develop

# 2. 切換到功能分支
git checkout feature/your-feature-name

# 3. 同步最新代碼
git pull origin develop
git rebase develop  # 或 merge
```

**每日結束工作：**

```bash
# 1. 提交當天的工作
git add .
git commit -m "feat: 今日工作進度"

# 2. 推送到遠端
git push origin feature/your-feature-name
```

### 9.2 溝通規範

- ✅ **重大更改前**：在團隊頻道或 Issue 中討論
- ✅ **阻塞問題**：及時尋求幫助，不要卡住
- ✅ **PR 創建後**：@ 相關審查者
- ✅ **衝突解決**：與相關開發者溝通

### 9.3 分支管理

**定期清理：**

```bash
# 刪除已合併的本地分支
git branch --merged | grep -v "\*\|main\|develop" | xargs -n 1 git branch -d

# 刪除遠端已合併的分支
git fetch --prune
```

---

## 10. 常見問題與解決方案

### Q1: 如何撤銷最後一次提交？

```bash
# 保留更改，撤銷提交
git reset --soft HEAD~1

# 完全撤銷提交和更改（謹慎使用）
git reset --hard HEAD~1
```

### Q2: 如何修改最後一次提交信息？

```bash
git commit --amend -m "新的提交信息"
```

### Q3: 如何將多個提交合併為一個？

```bash
# 交互式 rebase
git rebase -i HEAD~3  # 合併最近 3 個提交

# 在編輯器中將 "pick" 改為 "squash" 或 "s"
```

### Q4: 如何恢復已刪除的文件？

```bash
# 查看刪除歷史
git log --diff-filter=D --summary

# 恢復文件
git checkout <commit-hash> -- path/to/file
```

### Q5: 如何查看特定文件的更改歷史？

```bash
git log --follow -- path/to/file
git blame path/to/file
```

### Q6: 如何暫時保存工作進度？

```bash
# 暫存當前更改
git stash

# 查看暫存列表
git stash list

# 恢復暫存
git stash pop
```

---

## 📚 參考資源

- [Git 官方文檔](https://git-scm.com/doc)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub 協作指南](https://docs.github.com/en/get-started/quickstart/github-flow)

---

## ✅ 快速參考

### 常用命令速查

```bash
# 查看狀態
git status

# 查看更改
git diff

# 添加文件
git add <file>

# 提交
git commit -m "type: 描述"

# 推送
git push origin branch-name

# 拉取
git pull origin branch-name

# 創建分支
git checkout -b feature/name

# 切換分支
git checkout branch-name

# 查看分支
git branch

# 合併分支
git merge branch-name

# Rebase
git rebase branch-name
```

---

**最後更新：2025-11-12**  
**版本：v1.0**

