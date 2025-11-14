# GitHub 倉庫設置指南

## 📋 概述

本文檔說明如何將 AAM 服務項目連接到 GitHub 遠端倉庫。

## ✅ 已完成的工作

- ✅ 本地 Git 倉庫已初始化
- ✅ 初始提交已創建（29 個文件，1207 行代碼）
- ✅ `.gitignore` 已配置（忽略 `.env`、`__pycache__` 等）

## 🚀 設置步驟

### 步驟 1：在 GitHub 創建倉庫

#### 方式 A：使用網頁界面

1. **訪問 GitHub**
   - 打開瀏覽器，訪問：https://github.com/new
   - 或點擊 GitHub 右上角「+」→「New repository」

2. **填寫倉庫信息**
   - **Repository name**: `aam-service`（或自定義名稱）
   - **Description**: `AI-Augmented Memory (AAM) Service - 提供長期記憶和上下文豐富化能力`
   - **Visibility**: 
     - ✅ **Private**（推薦）- 代碼不公開
     - ⚠️ Public - 代碼公開
   - ⚠️ **重要**：不要勾選以下選項：
     - ❌ Add a README file（我們已有 README.md）
     - ❌ Add .gitignore（我們已有 .gitignore）
     - ❌ Choose a license（可選，後續添加）

3. **創建倉庫**
   - 點擊「Create repository」按鈕

#### 方式 B：使用 GitHub CLI（如果已安裝）

```bash
# 創建私有倉庫
gh repo create aam-service --private --description "AI-Augmented Memory Service"

# 或創建公開倉庫
gh repo create aam-service --public --description "AI-Augmented Memory Service"
```

### 步驟 2：連接本地與遠端倉庫

#### 方式 A：使用設置腳本（推薦）

```bash
cd /Users/Daniel/Documents/GitHub/AAM/aam-service

# 運行設置腳本
./scripts/setup-github.sh YOUR_GITHUB_USERNAME aam-service

# 然後按照提示操作
```

#### 方式 B：手動設置

```bash
cd /Users/Daniel/Documents/GitHub/AAM/aam-service

# 添加遠端倉庫（HTTPS）
git remote add origin https://github.com/YOUR_USERNAME/aam-service.git

# 或使用 SSH（如果已配置 SSH key）
git remote add origin git@github.com:YOUR_USERNAME/aam-service.git

# 驗證遠端倉庫
git remote -v
```

**替換 `YOUR_USERNAME` 為您的 GitHub 用戶名**

### 步驟 3：推送代碼到 GitHub

```bash
# 推送代碼到遠端 main 分支
git push -u origin main
```

**注意**：如果是第一次推送，可能需要：
- **HTTPS**：輸入 GitHub 用戶名和 Personal Access Token（不是密碼）
- **SSH**：確保 SSH key 已添加到 GitHub

### 步驟 4：驗證推送成功

1. **訪問 GitHub 倉庫**
   - 打開：`https://github.com/YOUR_USERNAME/aam-service`

2. **檢查文件**
   - 確認所有文件都已上傳
   - 確認 `.env` 文件**沒有**被上傳（這是正確的）

3. **查看提交歷史**
   - 應該能看到初始提交：「feat: 初始化 AAM 服務項目結構」

## 🔐 認證設置

### HTTPS 認證

如果使用 HTTPS，需要設置 Personal Access Token：

1. **創建 Token**
   - 訪問：https://github.com/settings/tokens
   - 點擊「Generate new token」→「Generate new token (classic)」
   - 設置名稱和過期時間
   - 選擇權限：至少勾選 `repo`
   - 生成並複製 Token

2. **使用 Token**
   - 推送時，用戶名輸入 GitHub 用戶名
   - 密碼輸入 Personal Access Token

3. **保存憑證（可選）**
   ```bash
   git config --global credential.helper osxkeychain  # macOS
   # 或
   git config --global credential.helper store         # Linux/Windows
   ```

### SSH 認證（推薦）

1. **檢查 SSH key**
   ```bash
   ls -la ~/.ssh/id_rsa.pub
   # 或
   ls -la ~/.ssh/id_ed25519.pub
   ```

2. **如果沒有 SSH key，創建一個**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

3. **添加 SSH key 到 GitHub**
   ```bash
   # 複製公鑰
   cat ~/.ssh/id_ed25519.pub
   # 或
   cat ~/.ssh/id_rsa.pub
   
   # 然後訪問：https://github.com/settings/keys
   # 點擊「New SSH key」，貼上公鑰內容
   ```

4. **測試連接**
   ```bash
   ssh -T git@github.com
   ```

## 📝 常用 Git 命令

```bash
# 查看狀態
git status

# 查看提交歷史
git log --oneline --graph

# 添加文件
git add .
git add <file>

# 提交
git commit -m "提交信息"

# 推送到遠端
git push origin main

# 拉取遠端更新
git pull origin main

# 查看遠端倉庫
git remote -v

# 更新遠端 URL
git remote set-url origin <new-url>
```

## ⚠️ 注意事項

1. **不要提交敏感信息**
   - ✅ `.env` 已添加到 `.gitignore`
   - ✅ `.env.example` 會被提交（這是正確的）
   - ⚠️ 確保沒有 API keys、密碼等敏感信息

2. **提交前檢查**
   ```bash
   git status
   git diff
   ```

3. **使用有意義的提交信息**
   ```bash
   git commit -m "feat: 添加新功能"
   git commit -m "fix: 修復 Bug"
   git commit -m "docs: 更新文檔"
   ```

## 🆘 常見問題

### Q: 推送時提示「Permission denied」
**A**: 檢查認證設置，確保使用正確的 Personal Access Token 或 SSH key

### Q: 推送時提示「Repository not found」
**A**: 確認倉庫名稱和用戶名正確，確認倉庫已創建

### Q: 如何更改遠端倉庫 URL？
```bash
git remote set-url origin <new-url>
```

### Q: 如何移除遠端倉庫？
```bash
git remote remove origin
```

## ✅ 完成檢查清單

- [ ] GitHub 倉庫已創建
- [ ] 遠端倉庫已連接（`git remote -v`）
- [ ] 代碼已成功推送（`git push -u origin main`）
- [ ] GitHub 上可以看到所有文件
- [ ] `.env` 文件**沒有**出現在 GitHub 上
- [ ] 提交歷史正確顯示

## 📚 相關資源

- [GitHub 文檔](https://docs.github.com/)
- [Git 官方文檔](https://git-scm.com/doc)
- [GitHub CLI 文檔](https://cli.github.com/)

