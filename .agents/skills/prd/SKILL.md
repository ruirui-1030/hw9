# 產品需求文件 (PRD) 撰寫技能 (PRD Generation Skill)

這個技能負責指導 AI 系統工程師/產品經理，如何撰寫「AI 股票分析 LINE Bot」的產品需求文件 (PRD)。此 PRD 將成為後續開發 (`linebot-implement`) 的藍圖。

## 1. 產品核心價值 (Product Vision)
打造一個輕量化、即時的 LINE 聊天機器人，讓使用者只需在聊天室輸入「股票名稱」或「股票代號」，就能獲得由 Gemini AI 生成的專業個股分析報告，降低一般投資人獲取股票洞察的門檻。

## 2. 核心功能情境 (Core Scenarios)
- **股票分析觸發**：使用者輸入特定股票名稱（例如：「台積電」、「2330」）。
- **AI 智能解析**：後端攔截文字訊息，將其組合成特定的 Prompt，發送給 Gemini 模型進行運算。
- **結構化回覆**：將 Gemini 產生的分析報告（包含近期概況、產業亮點、風險提示等），透過 LINE Bot 回傳給使用者。

## 3. PRD 產出格式要求 (Required PRD Structure)
請 AI 在產出 `docs/PRD.md` 時，必須嚴格遵守以下章節結構：

### 3.1 專案簡介 (Overview)
簡述專案目標、目標受眾及預期效益。

### 3.2 使用者故事 (User Stories)
請列出 1~3 個核心使用者故事。例如：
> 「身為一名投資新手，我希望能在 LINE 輸入股票名稱後，立刻獲得 AI 對該股票的分析，幫助我快速了解這間公司。」

### 3.3 系統流程 (User Flow)
請使用文字或 Mermaid 語法描述從「使用者傳送訊息」到「收到 AI 回覆」的完整資料流。
(User -> LINE Platform -> FastAPI Webhook -> Gemini API -> FastAPI -> LINE Platform)

### 3.4 功能需求 (Functional Requirements)
詳細條列需要實作的功能：
1. **LINE Webhook 接收**：如何接收與解析使用者的 `TextMessageContent`。
2. **Gemini API 整合**：
   - 必須定義一段標準的 **System Prompt / 指令範本**。
   - 例如：「你是一位專業金融分析師，請針對『{stock_name}』進行 300 字以內的精要分析，列出重點與潛在風險。」
3. **錯誤處理機制 (Error Handling)**：
   - 處理使用者輸入無效文字的狀況。
   - 處理 Gemini API 呼叫失敗或無回應的狀況，並回傳友善的錯誤訊息給使用者。

### 3.5 非功能需求 (Non-Functional Requirements)
1. **效能與時間限制 (Timeout Constraints)**：
   - **⚠️ 關鍵限制**：LINE Bot 的 `reply_token` 時效僅有 1 分鐘，超過就會逾時報錯。
   - **解法要求**：PRD 必須規範 Gemini 的回應生成時間應控制在 10~20 秒內（可透過在 Prompt 中限制回答字數達成），確保系統能順利使用 `reply_token` 回覆。
2. **環境變數與安全性**：
   - 系統需使用 `.env` 管理 API Keys (包含 `LINE_CHANNEL_SECRET`, `LINE_CHANNEL_ACCESS_TOKEN`, `GEMINI_API_KEY`)。

### 3.6 資料需求 (Data Requirements) 
*(註：為符合作業 app.py 包含 SQLite 後端之要求)*
- PRD 中應規劃一個簡單的 SQLite 資料表（例如 `chat_logs`），用於紀錄使用者的查詢歷史。
- 欄位可包含：`id`, `user_id`, `message_text`, `timestamp` 等，以展示資料庫整合能力。

---
**給 AI 的指示 (Instruction for AI)**：
當使用者要求「請根據 PRD Skill 撰寫 PRD」時，請讀取此文件的規範，並輸出為一份完整的 Markdown 檔案 (建議路徑為 `docs/PRD.md`)。文件內容必須專業、具體，且能直接作為工程師撰寫程式碼的規格依據。
