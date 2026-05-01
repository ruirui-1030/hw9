# Git 提交與推送技能 (Git Commit & Push Skill)

這個技能負責指導 AI 助理，在協助使用者進行程式碼版本控制（Git Commit 與 Push）時，所需遵循的標準流程、前置條件與規範。

## 1. 提交與推送的前置需求 (Prerequisites for Commit & Push)

在執行任何 Git 操作之前，必須確認以下條件已經滿足：

### 1.1 Git 設定 (Git Configuration)
為了識別提交者，必須確保 Git 的 `user.name` 與 `user.email` 已經設定。
- **User Name**: `Antigravity`
- **User Email**: `Antigravity` (或指定的機器人信箱)

### 1.2 變更確認 (Changes Verification)
- 確保所有欲提交的檔案變更皆已儲存。
- 使用 `git status` 確認有哪些檔案被修改、新增或刪除。

### 1.3 遠端儲存庫設定 (Remote Repository Configuration)
- 確認本地端已經初始化 Git 儲存庫 (`git init`) 或已從遠端克隆 (`git clone`)。
- 確認已經設定遠端節點 (Remote origin)，並且具備推送權限（例如：已設定 SSH Key 或 Personal Access Token）。

## 2. 提交與推送標準流程 (Standard Commit & Push Flow)

### 2.1 階段化變更 (Stage Changes)
將需要提交的變更加入暫存區：
```bash
git add <檔案名稱> 
# 或使用 git add . 將所有變更加入
```

### 2.2 撰寫提交訊息 (Commit Changes)
執行提交並撰寫清晰的提交訊息 (Commit Message)。
```bash
git commit -m "提交訊息"
```
**提交訊息規範 (Commit Message Format)**：
- 必須清晰描述此次變更的目的（例如：`feat: 實作 LINE Bot 自動回覆功能`、`fix: 修正資料庫連線錯誤`）。
- 建議使用 Conventional Commits 格式（如 `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`）。

### 2.3 推送至遠端 (Push to Remote)
將本地端的 commit 推送至遠端儲存庫：
```bash
git push origin <分支名稱>
# 例如：git push origin main
```

## 3. 異常處理與檢查 (Error Handling & Checks)
- **衝突處理 (Merge Conflict)**：如果 Push 被拒絕 (rejected) 因為遠端包含本地沒有的變更，需要先執行 `git pull`，解決衝突後再重新提交。
- **身分驗證失敗 (Authentication Failed)**：檢查 GitHub CLI 或 Git Credential 設定是否正確。

---
**給 AI 的指示 (Instruction for AI)**：
當使用者要求「進行 Git 提交與推送」或「幫我 commit 和 push」時，請確保遵守本文件的規範。若 Git 尚未設定識別資訊，請先協助使用者設定為 `Antigravity`，然後引導或代為執行 `add`, `commit`, 和 `push` 指令。
