import os
import requests
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

# 启用日志，方便在 Render 终端看报错
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 配置
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY")
# 替换为你的 32k 模型对应的 Endpoint ID
DOUBAO_API_URL = "https://ep-20260304075356-66mff.ark.cn-beijing.volces.com/api/v3/chat/completions"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="👋 已连接豆包 32k AI！")

async def reply_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    msg = await context.bot.send_message(chat_id=update.effective_chat.id, text="思考中...")

    try:
        data = {
            # 这里也替换为你的 32k 模型对应的 Endpoint ID
            "model": "ep-20260304075356-66mff",
            "messages": [{"role": "user", "content": update.message.text}]
        }
        resp = requests.post(
            DOUBAO_API_URL,
            json=data,
            headers={"Authorization": f"Bearer {DOUBAO_API_KEY}", "Content-Type": "application/json"},
            timeout=30
        )
        if resp.status_code == 200:
            answer = resp.json()["choices"][0]["message"]["content"]
        else:
            answer = f"Error: {resp.status_code}\n{resp.text}"
    except Exception as e:
        answer = f"出错：{str(e)}"

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=msg.message_id,
        text=answer
    )

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("未发现 TOKEN")
        return

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_ai))

    print("正在启动机器人...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
