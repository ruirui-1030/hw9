import os
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Header
from google import genai

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# 載入環境變數
load_dotenv()

LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# 初始化 FastAPI
app = FastAPI()

# 初始化 LINE Bot API 與 Webhook Handler
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化 Gemini API
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# 初始化 SQLite 資料庫
DB_FILE = "chat_logs.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            message_text TEXT,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def log_message(user_id: str, message_text: str):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_logs (user_id, message_text, timestamp) VALUES (?, ?, ?)",
            (user_id, message_text, datetime.now())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

@app.post("/callback")
async def callback(request: Request, x_line_signature: str = Header(None)):
    if not x_line_signature:
        raise HTTPException(status_code=400, detail="Missing X-Line-Signature header")

    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text
    
    # 紀錄使用者的查詢
    log_message(user_id, user_message)

    try:
        if not gemini_client:
            reply_text = "系統錯誤：未設定 Gemini API 金鑰。"
        else:
            # 呼叫 Gemini API
            prompt = f"你是一位專業的金融分析師。請針對使用者詢問的股票『{user_message}』進行 300 字以內的精要分析。請包含：1. 近期概況與趨勢 2. 產業亮點 3. 潛稍微提示潛在風險。請直接給出分析，不要有開場白。"
            
            response = gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            reply_text = response.text if response.text else "抱歉，目前 AI 分析師無法產生回覆，請稍後再試。"
            
    except Exception as e:
        import traceback
        print(f"Gemini API Error: {traceback.format_exc()}")
        reply_text = f"抱歉，目前 AI 分析師正在休息中，請稍後再試。\n詳細錯誤：{e}"

    # 回傳訊息給使用者
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
