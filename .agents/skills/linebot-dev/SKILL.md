# LINE Bot 開發技能 (LINE Bot Development Skill)

這個技能提供使用 Python 開發 LINE Bot 的指南與最佳實踐，並強制要求使用 `line-bot-sdk-python` v3 版本。

## 1. 開發前確認清單 (Checklist)
在開始開發 LINE Bot 之前，請確保已完成以下準備工作：
- [ ] **LINE Developers 帳號**：已註冊並登入。
- [ ] **Provider 與 Channel**：已建立一個 Provider 以及 Messaging API Channel。
- [ ] **Channel Secret & Access Token**：已從 Channel 設定中取得 (Basic settings -> Channel secret, Messaging API -> Channel access token (long-lived))。
- [ ] **Webhook URL 設定**：已在 LINE Developers Console 填寫指向伺服器端點的 HTTPS URL (例如：`https://yourdomain.com/callback`)。
- [ ] **Webhook 驗證 (Verify)**：在 Console 中點擊「Verify」按鈕，確認 LINE 伺服器能成功連線至你的伺服器。
- [ ] **關閉預設自動回覆**：如果打算全權透過程式處理訊息，請在官方帳號設定中關閉 LINE 預設的自動回覆訊息功能。
- [ ] **環境變數設定**：確保 `LINE_CHANNEL_SECRET` 與 `LINE_CHANNEL_ACCESS_TOKEN` 將會設定於 `.env` 檔案中（**絕對不要將金鑰寫死在程式碼中**）。

## 2. line-bot-sdk-python: v2 vs v3 差異對照
`line-bot-sdk-python` 在 v3 版本中引入了重大改變，從 v2 傳統的單一同步結構，轉變為更模組化、依據 API 分類的架構。

| 功能 / 元件 | v2 (舊版寫法) | v3 (現行標準寫法) |
| :--- | :--- | :--- |
| **匯入模組 (Import)** | `from linebot import LineBotApi, WebhookHandler` | `from linebot.v3 import WebhookHandler`<br>`from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage` |
| **API Client 初始化** | `LineBotApi(channel_access_token)` | `configuration = Configuration(access_token='...')`<br>`api_client = ApiClient(configuration)`<br>`line_bot_api = MessagingApi(api_client)` |
| **訊息物件 (Message Objects)**| `from linebot.models import TextSendMessage` | `from linebot.v3.messaging import TextMessage`<br>*(注意：v3 通常移除了 `SendMessage` 字尾，例如使用 `TextMessage` 而非 `TextSendMessage`)* |
| **回覆訊息 (Replying)** | `line_bot_api.reply_message(reply_token, TextSendMessage(text='...'))` | `line_bot_api.reply_message_with_http_info(ReplyMessageRequest(reply_token=..., messages=[TextMessage(text='...')]))` |
| **例外處理 (Exceptions)** | `from linebot.exceptions import InvalidSignatureError` | `from linebot.v3.exceptions import InvalidSignatureError` |

## 3. Webhook + Handler 標準寫法範例 (FastAPI)
以下是使用 FastAPI 與 SDK v3 建立 LINE Webhook 的標準樣板程式碼：

```python
import os
import sys
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from dotenv import load_dotenv

load_dotenv()

channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

if channel_secret is None or channel_access_token is None:
    print('請在環境變數中設定 LINE_CHANNEL_SECRET 與 LINE_CHANNEL_ACCESS_TOKEN。')
    sys.exit(1)

configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)

app = FastAPI()

@app.post("/callback")
async def callback(request: Request, background_tasks: BackgroundTasks):
    # 取得 X-Line-Signature 標頭值
    signature = request.headers.get('X-Line-Signature', '')
    
    # 取得請求內容字串
    body = await request.body()
    body_str = body.decode('utf-8')

    try:
        # 注意：handler.handle 是同步的。
        # 對於耗時操作，應考慮在此處手動解析 event 並將任務丟給 background_tasks 處理，以避免阻塞。
        handler.handle(body_str, signature)
    except InvalidSignatureError:
        print("簽章驗證失敗，請確認你的 channel access token/channel secret。")
        raise HTTPException(status_code=400, detail="Invalid signature.")

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        reply_req = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=f"你剛剛說了：{user_message}")]
        )
        line_bot_api.reply_message_with_http_info(reply_req)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 4. 常見地雷與避坑指南

1. **Reply Token 限制**:
   - 一個 `reply_token` **只能使用一次**。一旦使用它回覆過訊息，該 token 就會立刻失效。
   - `reply_token` 的有效期限為 **1 分鐘**。如果你的機器人處理請求的時間超過 1 分鐘，回覆將會失敗。
   - *解決方案*：如果處理時間較長，應立即回覆「處理中...」之類的訊息，或者稍後改用 `PushMessage` API 傳送結果（注意：PushMessage 需要使用者 ID，且可能會消耗官方帳號的免費訊息額度）。

2. **環境變數絕對不能寫死 (Hardcoding)**:
   - 絕對不要將 `LINE_CHANNEL_SECRET` 或 `LINE_CHANNEL_ACCESS_TOKEN` 直接寫在程式碼中，或者提交到版本控制系統（例如 GitHub）。
   - *解決方案*：務必使用 `.env` 檔案，透過 `os.getenv()` 讀取，並確保 `.env` 已加入 `.gitignore` 檔案中。

3. **耗時操作導致 Webhook 阻塞 (Timeout)**:
   - LINE 伺服器預期 Webhook 必須在幾秒內回傳 `200 OK`。如果你的 Webhook 被耗時的程式（例如：呼叫 LLM API、資料庫長時間查詢）卡住，LINE 會認為該請求失敗，並可能重試或甚至停用你的 Webhook。
   - *解決方案*：收到請求後應盡速回傳 `200 OK` 狀態碼。把耗時的工作交給背景任務（Background tasks）或是任務佇列（Worker queue）來處理，例如使用 FastAPI 的 `BackgroundTasks`、Celery 或是 `asyncio.create_task()`。

## 5. 事件類型 (Event) 與訊息類型 (Message) 列表

### 5.1 Webhook 事件類型 (Event Types)
當 LINE 伺服器發送請求到 Webhook 時，可能會包含以下事件（請從 `linebot.v3.webhooks` 匯入）：
- `MessageEvent`：使用者發送訊息。
- `FollowEvent`：使用者將機器人加為好友或解除封鎖。
- `UnfollowEvent`：使用者封鎖機器人。
- `JoinEvent`：機器人被加入群組或聊天室。
- `LeaveEvent`：機器人被踢出或離開群組/聊天室。
- `PostbackEvent`：使用者觸發了 Postback 動作（例如：點擊了樣板訊息上的按鈕）。
- `BeaconEvent`：使用者進入或離開 LINE Beacon 的訊號範圍。
- `MemberJoinedEvent`：有新成員加入機器人所在的群組或聊天室。
- `MemberLeftEvent`：有成員離開機器人所在的群組或聊天室。
- `ThingsEvent`：與 LINE Things（物聯網設備）相關的事件。
- `UnsendEvent`：使用者收回了訊息。
- `VideoPlayCompleteEvent`：使用者看完了帶有追蹤功能的影片。

### 5.2 收到的訊息內容類型 (Message Content Types)
在 `MessageEvent` 中，訊息的具體內容可能是以下類型：
- `TextMessageContent` (文字)
- `ImageMessageContent` (圖片)
- `VideoMessageContent` (影片)
- `AudioMessageContent` (語音)
- `LocationMessageContent` (位置資訊)
- `StickerMessageContent` (貼圖)
- `FileMessageContent` (檔案)

### 5.3 發送的訊息類型 (Outgoing Message Types)
當你要回覆 (Reply) 或主動推送 (Push) 訊息給使用者時，可使用的訊息類型（請從 `linebot.v3.messaging` 匯入）：
- `TextMessage` (文字訊息)
- `ImageMessage` (圖片訊息)
- `VideoMessage` (影片訊息)
- `AudioMessage` (語音訊息)
- `LocationMessage` (位置訊息)
- `StickerMessage` (貼圖訊息)
- `TemplateMessage` (樣板訊息，包含按鈕、確認、輪播、圖片輪播等形式)
- `FlexMessage` (高度客製化的 JSON UI 介面)

---
**給 AI 的開發指示**：當被要求建立或修改 LINE Bot 相關程式碼時，請務必嚴格遵循 SDK v3 的語法、確保機密金鑰從環境變數讀取，並妥善處理 reply token 的時效以及 Webhook 必須非同步回傳的問題！
