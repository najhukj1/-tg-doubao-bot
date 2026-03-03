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

# 火山方舟正确的 API 地址
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
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
    # 先回复“思考中”
    msg = await context.bot.send_message(
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
            answer = f"AI 调用失败：{resp.status_code}\n{resp.text}"
    except Exception as e:
        answer = f"出错：{str(e)}"
    # 编辑刚才的“思考中”消息，替换成最终回答
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=msg.message_id,
        text=answer
    )

if __name__ == "__main__":
    # 显式设置参数，避免内部属性冲突
    application = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .concurrent_updates(False)  # 禁用并发更新
        .build()
    )
    start_handler = CommandHandler("start", start)
    echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, reply_ai)
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.run_polling()
