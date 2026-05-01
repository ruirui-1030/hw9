# W11 作業：股票 LINE Bot

> **繳交方式**：將你的 GitHub repo 網址貼到作業繳交區
> **作業性質**：個人作業

---

## 作業目標

利用上週設計的 Skill，開發一個股票相關的 LINE Bot。
重點不是功能多寡，而是你設計的 **Skill 品質**——Skill 寫得越具體，AI 產出的程式碼就越接近可以直接執行。

---

## 功能要求（擇一實作）

| 功能 | 說明 |
| --- | --- |
| AI 分析股票 | 使用者說股票名稱，Gemini 給出分析 |
| 追蹤清單 | 儲存使用者的自選股清單到 SQLite |
| 查詢即時價格 | 整合 yfinance 或 twstock 取得股價 |

> 以「可以執行、能回覆訊息」為目標，不需要複雜

---

## 繳交項目

你的 GitHub repo 需要包含：

| 項目 | 說明 |
| --- | --- |
| `app.py` | LINE Webhook + Gemini + SQLite 後端 |
| `requirements.txt` | 所有套件 |
| `.env.example` | 環境變數範本（不含真實 token） |
| `.agents/skills/` | 至少包含 `/linebot-implement` Skill |
| `README.md` | 本檔案（含心得報告） |
| `screenshots/chat.png` | LINE Bot 對話截圖（至少一輪完整對話） |

### Skill 要求

`.agents/skills/` 至少需要包含：

- `/linebot-implement`：產出 LINE Bot 主程式（必要）
- `/prd` 或 `/architecture`：延用上週的
- `/commit`：延用上週的

---

## 專案結構

```
your-repo/
├── .agents/
│   └── skills/
│       ├── prd/SKILL.md
│       ├── linebot-implement/SKILL.md
│       └── commit/SKILL.md
├── docs/
│   └── PRD.md
├── screenshots/
│   └── chat.png
├── app.py
├── requirements.txt
├── .env.example
└── README.md
```

> `.env` 和 `users.db` 不要 commit（加入 `.gitignore`）

---

## 啟動方式

```bash
# 1. 建立虛擬環境
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. 安裝套件
pip install -r requirements.txt

# 3. 設定環境變數
cp .env.example .env
# 編輯 .env，填入三個 token

# 4. 啟動 FastAPI
uvicorn app:app --reload

# 5. 另開終端機啟動 ngrok
ngrok http 8000
# 複製 https 網址，填入 LINE Developers Console 的 Webhook URL（加上 /callback）
# 點「Verify」確認連線正常後，掃 QR Code 加好友開始測試
```

---

## 心得報告

**姓名**：
**學號**：

**Q1. 你在 `/linebot-implement` Skill 的「注意事項」寫了哪些規則？為什麼這樣寫？**

> 1. **Webhook Timeout 機制**：因為 LINE 規定 reply_token 時效為一分鐘，且要求盡快回傳 200 OK，若超時會出錯，因此要求限制 Gemini 的生成時間。
> 2. **安全性 (Security)**：強調絕不可將 Channel Secret 或 Access Token 寫死在程式中，必須使用 `.env` 統一管理，避免機密外洩；且必須驗證 `X-Line-Signature`。
> 3. **錯誤捕捉 (Error Handling)**：要求呼叫外部 API 時必須包裝 `try-except` 區塊，若發生錯誤需回傳友善錯誤訊息，避免 Bot 變成已讀不回。

---

**Q2. 你的 Skill 第一次執行後，AI 產出的程式直接能跑嗎？需要修改哪些地方？修改後有沒有更新 Skill？**

> 基本上幾乎一次就能跑。因為在 `linebot-implement` 的 Skill 中已經明確定義了 v3 SDK 的所有初始化與 Webhook 流程，並清楚要求使用 Gemini 與 SQLite，所以 AI 生成的程式碼很精確，可以直接執行而無需大幅度修改。我也將 SQLite 的建表邏輯直接整合進腳本中，讓系統更完整。

---

**Q3. 你遇到什麼問題是 AI 沒辦法自己解決、需要你介入處理的？**

> 取得 LINE Channel Access Token 與 Secret 以及 Gemini API Key 的動作，必須手動進入 LINE Developers Console 與 Google AI Studio 申請並設定到 `.env` 檔案中。此外，將本地端服務公開到網際網路（如設定 ngrok 並貼到 Webhook URL 上）也是需要手動操作的步驟。

---

**Q4. 如果你要把這個 LINE Bot 讓朋友使用，你還需要做什麼？**

> 1. 將此程式部署到雲端伺服器 (如 Render, Heroku) 或 VPS，確保 24 小時運作。
> 2. 使用真正的 HTTPS 網域設定為 Webhook URL，而不是會變動的 ngrok。
> 3. 確保 LINE Channel 狀態從 Developer 轉為 Public，朋友才能搜尋並加入這個 Bot。