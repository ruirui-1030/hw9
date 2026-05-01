# 系統架構 (Architecture) 撰寫技能 (Architecture Generation Skill)

這個技能負責指導 AI 系統架構師，如何為「AI 股票分析 LINE Bot」撰寫系統架構設計文件 (Architecture Document)。此文件將作為開發團隊理解系統運作原理、各服務間互動關係以及技術選型的核心技術參考指南。

## 1. 架構設計核心目標 (Core Architectural Goals)
- **輕量化與高效**：使用 FastAPI 建立非同步 Web Server，快速響應 LINE Webhook 請求。
- **高內聚低耦合**：明確劃分 LINE 平台對接、業務邏輯（AI 分析）、與資料持久化（SQLite）的職責。
- **可本地運行**：確保專案結構與配置能讓開發者輕易在本地端透過 ngrok 進行開發與測試。

## 2. 架構文件產出格式要求 (Required Architecture Structure)
請 AI 在產出 `docs/ARCHITECTURE.md` 時，必須嚴格遵守以下章節結構：

### 2.1 系統概述 (System Overview)
簡述系統整體的技術架構與運作邏輯。說明系統如何從 LINE 平台接收訊息、交由後端處理，再呼叫外部 API (Gemini)，最後回傳結果。

### 2.2 系統架構圖 (Architecture Diagram)
必須提供一個 Mermaid 語法的流程圖 (Flowchart) 或循序圖 (Sequence Diagram)，清楚標示出以下元件的互動關係：
- User / LINE App
- LINE Platform (Webhook)
- FastAPI Server (Backend)
- SQLite Database (Local Storage)
- Google Gemini API (AI Service)

### 2.3 核心技術棧 (Technology Stack)
明確列出專案使用的核心技術與工具，包含但不限於：
- **後端框架**：FastAPI
- **套件/SDK**：`line-bot-sdk-python` v3, `google-generativeai`
- **資料庫**：SQLite
- **伺服器/代理**：Uvicorn, ngrok

### 2.4 核心元件說明 (Component Description)
詳細說明系統內部的模組劃分，建議包含：
1. **LINE Webhook 接收器 (`/callback`)**：說明簽章驗證 (`X-Line-Signature`) 的機制。
2. **事件處理器 (Event Handler)**：說明如何過濾、解析 `TextMessageContent`。
3. **業務邏輯與服務層 (Service Layer)**：
   - AI 分析服務：如何組合 Prompt 與呼叫 Gemini API。
   - 資料庫服務：如何將使用者的查詢行為寫入 SQLite。

### 2.5 資料庫設計 (Database Schema)
定義用於紀錄查詢日誌的資料表結構（為符合課程要求，需包含 SQLite 整合）。
- 表格名稱：例如 `chat_logs`
- 欄位定義：包含欄位名稱、資料型別與功能說明（如 `id`, `user_id`, `message_text`, `timestamp`）。

### 2.6 目錄結構 (Directory Structure)
提供專案的標準資料夾結構樹狀圖 (Tree)，並加上簡短的註解，例如：
- `.agents/skills/` (放置 AI Skill)
- `docs/` (放置 PRD 與 架構文件)
- `app.py` (主程式入口)
- `.env` / `requirements.txt` (環境設定)

### 2.7 部署與執行流程 (Deployment & Execution Flow)
條列式說明如何在本地端啟動這個系統，包含：
1. 安裝依賴套件。
2. 設定環境變數 (`.env`)。
3. 啟動 uvicorn 伺服器。
4. 使用 ngrok 產生外部連結並綁定到 LINE Developer Console。

---
**給 AI 的指示 (Instruction for AI)**：
當使用者要求「請根據 Architecture Skill 撰寫架構設計文件」或「產出 docs/ARCHITECTURE.md」時，請讀取此文件的規範，並輸出為一份完整的 Markdown 檔案。內容必須具備技術深度，描述精確且無邏輯衝突，成為工程師開發時的標準參考。
