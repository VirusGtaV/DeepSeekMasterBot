import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from puter import PuterAI, PuterAuthError, PuterAPIError

# ============================== НАСТРОЙКИ ==============================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ⚠️ ТВОИ ДАННЫЕ
BOT_TOKEN = "8475855320:AAERPPB2INBiymqDt0JJjhhnKP6A3Fg-mLI"
PUTER_USERNAME = "vituavirus"      # <-- ЗАМЕНИ
PUTER_PASSWORD = "Dima!!"      # <-- ЗАМЕНИ

# Глобальный клиент Puter (будет инициализирован при старте)
puter_client = None

async def init_puter():
    """Инициализация клиента Puter при запуске бота"""
    global puter_client
    try:
        puter_client = PuterAI(username=PUTER_USERNAME, password=PUTER_PASSWORD)
        if puter_client.login():
            logger.info("✅ Puter login successful")
            # Устанавливаем желаемую модель (можно поменять)
            # Список моделей: https://developer.puter.com/ai/models/
            puter_client.set_model("gpt-5-nano")  # Лёгкая и быстрая модель
            return True
        else:
            logger.error("❌ Puter login failed")
            return False
    except Exception as e:
        logger.error(f"Puter init error: {e}")
        return False

async def query_ai(user_message: str) -> str:
    """Отправляет запрос к Puter и возвращает ответ."""
    global puter_client
    try:
        # Если клиент ещё не инициализирован — делаем это сейчас
        if not puter_client:
            if not await init_puter():
                return "❌ Ошибка подключения к Puter. Попробуйте позже."

        # Отправляем запрос
        response = puter_client.chat(user_message)
        return response

    except PuterAuthError as e:
        logger.error(f"Puter auth error: {e}")
        return "❌ Ошибка авторизации Puter. Проверьте логин/пароль."
    except PuterAPIError as e:
        logger.error(f"Puter API error: {e}")
        if "usage-limited" in str(e).lower():
            return "❌ Исчерпан дневной лимит Puter. Попробуйте завтра или создайте новый аккаунт."
        return "❌ Ошибка Puter API. Попробуйте позже."
    except Exception as e:
        logger.error(f"Puter error: {e}")
        return "❌ Неизвестная ошибка. Попробуйте позже."

# ============================== ОБРАБОТЧИКИ ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Привет! Я бот на базе **Puter.js**.\n"
        f"Модель: `gpt-5-nano` (можно сменить в коде).\n"
        "Задавай вопросы — я отвечу!"
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
        if puter_client:
            puter_client.clear_chat_history()  # Сбрасываем историю диалога в Puter
        await context.bot.send_message(chat_id=query.message.chat_id, text="🔄 Новый диалог начат!")
    elif query.data == "help":
        help_text = "📚 Просто отправляй сообщения, я отвечу."
        await context.bot.send_message(chat_id=query.message.chat_id, text=help_text)

def main():
    if not BOT_TOKEN:
        logger.error("Ошибка: не задан BOT_TOKEN")
        return
    if not PUTER_USERNAME or not PUTER_PASSWORD or PUTER_USERNAME == "твой_логин_на_puter":
        logger.error("Ошибка: не заданы или не изменены PUTER_USERNAME/PUTER_PASSWORD")
        return

    # Создаём приложение Telegram
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))

    # Запускаем инициализацию Puter в фоне
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_puter())

    logger.info("Бот с Puter запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
