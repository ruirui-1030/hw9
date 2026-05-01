# LINE Bot 實作技能 (LINE Bot Implementation Skill)

這個技能負責指導 AI 系統工程師，在實作「LINE Bot (特別是搭配 FastAPI 與 LINE Bot SDK v3)」時，所需遵循的標準架構、程式碼規範與開發避坑指南。

## 1. SDK 版本規範 (SDK Version Guidelines)
**必須使用 `line-bot-sdk-python` v3 版本**。v3 版本與 v2 版本不相容，實作時請嚴格遵守 v3 的導入與寫法：
- **API 客戶端初始化**：必須使用 `Configuration`, `ApiClient`, 與 `MessagingApi`。
- **Webhook 處理**：必須使用 `WebhookHandler` (來自 `linebot.v3.webhook`)。
- **訊息結構**：使用 `linebot.v3.messaging` 底下的類別，例如 `ReplyMessageRequest`, `TextMessage`。

## 2. 核心架構與 Webhook 實作 (Core Architecture & Webhook)
在 FastAPI 中實作 LINE Webhook 時，必須包含以下標準流程：

### 2.1 環境變數載入
確保使用 `python-dotenv` 讀取環境變數，包含：
- `LINE_CHANNEL_SECRET`
- `LINE_CHANNEL_ACCESS_TOKEN`

### 2.2 API 與 Handler 初始化範例
```python
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi

configuration = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
```

### 2.3 Webhook 路由實作
`/callback` 路由必須驗證 `X-Line-Signature` 標頭：
```python
from fastapi import Request, HTTPException, Header

@app.post("/callback")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return "OK"
```

## 3. 事件處理與訊息回覆 (Event Handling)
處理使用者傳送的文字訊息時，必須正確攔截 `MessageEvent` 與 `TextMessageContent`：

```python
from linebot.v3.webhook import MessageEvent, TextMessageContent
from linebot.v3.messaging import ReplyMessageRequest, TextMessage

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    # 這裡可以加入呼叫 Gemini API 的邏輯
    
    # 建立回覆訊息
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f"這是回覆：{user_message}")]
            )
        )
```

## 4. 常見開發陷阱與注意事項 (Common Pitfalls & Cautions)

1. **Webhook Timeout 機制**：
   - LINE 平台要求 Webhook 必須盡快收到 `200 OK` 回應（通常建議在數秒內）。
   - **注意**：`reply_token` 的有效期限為 **1 分鐘**。如果整合 Gemini API 等耗時操作，必須確保 API 呼叫能在這 1 分鐘內完成並回覆，否則會發生逾時錯誤。

2. **安全性 (Security)**：
   - 絕對不可以將 Channel Secret 或 Access Token 硬編碼 (Hardcode) 在程式碼中，必須統一透過 `.env` 管理。
   - `X-Line-Signature` 驗證是必須的，不可省略。

3. **錯誤捕捉 (Error Handling)**：
   - 呼叫外部 API (如 Gemini) 時，務必包裝 `try-except` 區塊。若發生錯誤，應回傳友善的錯誤訊息給 LINE 使用者（例如：「目前系統繁忙中，請稍後再試。」），避免 Bot 變成已讀不回。

---
**給 AI 的指示 (Instruction for AI)**：
當使用者要求「實作 LINE Bot」、「新增 LINE Bot 功能」或「處理 LINE Webhook」時，請先閱讀本文件的規範，確保你產出的程式碼符合 **LINE Bot SDK v3** 的標準寫法，並有妥善處理例外與簽章驗證。
