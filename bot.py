import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

# 从环境变量读取密钥
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY")

DOUBAO_API_URL = "https://api.doubao.com/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {DOUBAO_API_KEY}",
    "Content-Type": "application/json"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👋 我是接入豆包的 Telegram 机器人，直接发消息我就会回答～"
    )

async def reply_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="思考中..."
    )
    try:
        data = {
            "model": "doubao-lite-4k",
            "messages": [{"role": "user", "content": update.message.text}]
        }
        resp = requests.post(DOUBAO_API_URL, json=data, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            answer = resp.json()["choices"][0]["message"]["content"]
        else:
            answer = f"AI 调用失败：{resp.status_code}"
    except Exception as e:
        answer = f"出错：{str(e)}"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=answer
    )

if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    start_handler = CommandHandler("start", start)
    echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, reply_ai)
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.run_polling()
