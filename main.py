# ============================== ИМПОРТЫ ==============================
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from g4f.client import Client

# ============================== НАСТРОЙКИ ==============================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ⚠️ ТОКЕН ОТ BOTFATHER
BOT_TOKEN = "8475855320:AAERPPB2INBiymqDt0JJjhhnKP6A3Fg-mLI"

# ============================== КЛИЕНТ G4F ==============================
client = Client()
MODEL_NAME = "gpt-4o-mini"

async def query_ai(user_message: str) -> str:
    """Запрос к AI через g4f (асинхронный метод create)"""
    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": user_message}],
            temperature=0.7,
            timeout=30
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Ошибка G4F: {e}")
        return "❌ Ошибка при обращении к AI. Попробуйте позже."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Привет! Я бот на g4f (модель {MODEL_NAME}).\n"
        "Задавай вопросы!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(action="typing")
    reply = await query_ai(update.message.text)

    MAX_LENGTH = 4096
    keyboard = [
        [InlineKeyboardButton("🔄 Новый диалог", callback_data="new_chat")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if len(reply) > MAX_LENGTH:
        for i in range(0, len(reply), MAX_LENGTH):
            await update.message.reply_text(reply[i:i+MAX_LENGTH])
        await update.message.reply_text("✅ Ответ полностью отправлен.", reply_markup=reply_markup)
    else:
        await update.message.reply_text(reply, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "new_chat":
        await context.bot.send_message(chat_id=query.message.chat_id, text="🔄 Новый диалог начат!")
    elif query.data == "help":
        help_text = "📚 Просто отправляй сообщения, я отвечу."
        await context.bot.send_message(chat_id=query.message.chat_id, text=help_text)

def main():
    if not BOT_TOKEN:
        logger.error("Нет BOT_TOKEN")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    logger.info("Бот с g4f запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
