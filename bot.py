import os
import requests
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

# --- 配置部分 ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DOUBAO_API_KEY = os.environ.get("DOUBAO_API_KEY")

# 火山方舟 API 地址
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {DOUBAO_API_KEY}",
    "Content-Type": "application/json"
}

# --- 机器人功能 ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👋 我是接入豆包的 AI 机器人，直接发送消息即可开始对话！"
    )

async def reply_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理普通文本消息"""
    if not update.message or not update.message.text:
        return

    # 发送提示消息
    status_msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🤔 思考中..."
    )

    try:
        # 调用豆包 API
        payload = {
            "model": "doubao-lite-4k",
            "messages": [{"role": "user", "content": update.message.text}]
        }
        
        # 注意：在异步函数中使用 requests 是同步阻塞的，
        # 但对于简单的机器人，这通常不是报错的主要原因。
        resp = requests.post(DOUBAO_API_URL, json=payload, headers=HEADERS, timeout=30)
        
        if resp.status_code == 200:
            answer = resp.json()["choices"][0]["message"]["content"]
        else:
            answer = f"❌ AI 调用失败 (状态码: {resp.status_code})\n详情: {resp.text[:100]}"
            
    except Exception as e:
        answer = f"⚠️ 发生错误: {str(e)}"

    # 更新刚才的“思考中”消息
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=status_msg.message_id,
        text=answer
    )

# --- 主程序 ---
if __name__ == "__main__":
    # 1. 检查环境变量
    if not TELEGRAM_BOT_TOKEN:
        print("CRITICAL ERROR: TELEGRAM_BOT_TOKEN is missing!")
        exit(1)

    # 2. 构建 Application
    # 简化了 Builder，移除了可能导致版本冲突的额外参数
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # 3. 注册处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_ai))

    # 4. 启动机器人
    print("Bot is starting... Press Ctrl+C to stop.")
    # drop_pending_updates 会清理掉机器人离线期间堆积的消息，避免堆栈溢出
    application.run_polling(drop_pending_updates=True)
