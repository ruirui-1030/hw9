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

**姓名**：林瑞城
**學號**：D1123896

**Q1. 你在 `/linebot-implement` Skill 的「注意事項」寫了哪些規則？為什麼這樣寫？**

> 1. **Webhook Timeout 機制**：因為 LINE 規定 reply_token 時效為一分鐘，且要求盡快回傳 200 OK，若超時會出錯，因此要求限制 Gemini 的生成時間。
> 2. **安全性 (Security)**：強調絕不可將 Channel Secret 或 Access Token 寫死在程式中，必須使用 `.env` 統一管理，避免機密外洩；且必須驗證 `X-Line-Signature`。
> 3. **錯誤捕捉 (Error Handling)**：要求呼叫外部 API 時必須包裝 `try-except` 區塊，若發生錯誤需回傳友善錯誤訊息，避免 Bot 變成已讀不回。

---

**Q2. 你的 Skill 第一次執行後，AI 產出的程式直接能跑嗎？需要修改哪些地方？修改後有沒有更新 Skill？**

> 第一次產出的程式碼架構非常完整，但有一個小 bug 需要修改：
> AI 產生的 `from linebot.v3.webhook import ...` 少寫了 `s`，正確應該是 `linebot.v3.webhooks`，這導致了 `ImportError` 無法啟動。後來透過 AI 檢查並修正了這行程式碼才順利跑起來。此外，原本程式就已經完美整合了 SQLite 的建表邏輯，這點非常方便。

---

**Q3. 你遇到什麼問題是 AI 沒辦法自己解決、需要你介入處理的？**

> 除了金鑰申請與 ngrok/localtunnel 的設定必須手動處理外，我在實際測試時還遇到了兩個 AI 無法自動排除的「環境陷阱」，需要我和 AI 一起來回 Debug：
> 1. **環境變數快取問題**：我換了新的 Gemini API Key 到 `.env`，但因為 Uvicorn 伺服器沒有徹底重啟，導致它一直吃到舊的無效金鑰，不斷回覆我自訂的錯誤訊息。
> 2. **localtunnel 斷線**：免費的通道軟體因為閒置而自動關閉，導致 LINE 傳送的訊息根本進不到我的電腦，造成「完全沒有回覆」的死寂狀態。這些都需要手動介入重新啟動伺服器與通道才能解決。

---

**Q4. 如果你要把這個 LINE Bot 讓朋友使用，你還需要做什麼？**

> 1. 將此程式部署到雲端伺服器 (如 Render, Heroku) 或 VPS，確保 24 小時運作。
> 2. 使用真正的 HTTPS 網域設定為 Webhook URL，而不是會變動的 ngrok。
> 3. 確保 LINE Channel 狀態從 Developer 轉為 Public，朋友才能搜尋並加入這個 Bot。