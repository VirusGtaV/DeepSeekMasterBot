# ============================== ИМПОРТЫ ==============================
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from openai import OpenAI

# ============================== НАСТРОЙКИ ==============================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ⚠️ ТВОИ ДАННЫЕ (ВСТАВЬ СВОИ ЗНАЧЕНИЯ)
BOT_TOKEN = "8475855320:AAERPPB2INBiymqDt0JJjhhnKP6A3Fg-mLI"          # Токен от BotFather
GITHUB_TOKEN = "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 "  # Твой токен GitHub

# ============================== КЛИЕНТ GITHUB MODELS ==============================
client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=GITHUB_TOKEN,
)

# ============================== ВЫБОР МОДЕЛИ ==============================
# Доступные модели: openai/gpt-4.1, meta/llama-4-maverick, xai/grok-4, deepseek/deepseek-v3 и др.
MODEL_NAME = "openai/gpt-4.1"  # Можно заменить на другую модель

async def query_ai(user_message: str) -> str:
    """Отправляет запрос к GitHub Models и возвращает ответ."""
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": user_message}],
                temperature=0.7,
                max_tokens=4000  # Учитываем лимит вывода
            )
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Ошибка GitHub Models: {e}")
        # Понятные сообщения об ошибках
        if "401" in str(e):
            return "❌ Ошибка авторизации: неверный токен GitHub. Проверьте токен и его права."
        elif "429" in str(e):
            return "❌ Превышен лимит запросов. Попробуйте позже."
        elif "model_not_found" in str(e).lower() or "404" in str(e):
            return f"❌ Модель {MODEL_NAME} временно недоступна. Попробуйте другую модель (например, openai/gpt-4.1)."
        else:
            return "❌ Ошибка при обращении к модели. Попробуйте позже."

# ============================== ОБРАБОТЧИК КОМАНДЫ /start ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Привет! Я бот на базе **GitHub Models** (модель `{MODEL_NAME}`).\n"
        "Я использую твой GitHub Personal Access Token для доступа к современным AI-моделям.\n"
        "Бесплатный лимит: ~150 запросов в день.\n"
        "Просто задавай вопросы!"
    )

# ============================== ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ ==============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(action="typing")
    reply = await query_ai(update.message.text)

    MAX_LENGTH = 4096  # Лимит Telegram на одно сообщение
    keyboard = [
        [InlineKeyboardButton("🔄 Новый диалог", callback_data="new_chat")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if len(reply) > MAX_LENGTH:
        # Разбиваем длинный ответ на части
        for i in range(0, len(reply), MAX_LENGTH):
            await update.message.reply_text(reply[i:i+MAX_LENGTH])
        await update.message.reply_text("✅ Ответ полностью отправлен. Что дальше?", reply_markup=reply_markup)
    else:
        await update.message.reply_text(reply, reply_markup=reply_markup)

# ============================== ОБРАБОТЧИК НАЖАТИЙ НА КНОПКИ ==============================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "new_chat":
        await context.bot.send_message(chat_id=query.message.chat_id, text="🔄 Новый диалог начат!")
    elif query.data == "help":
        help_text = (
            "📚 **Как пользоваться ботом:**\n"
            "• Просто отправьте сообщение — я отвечу.\n"
            f"• Используется модель **{MODEL_NAME}**.\n"
            "• Если ответ длинный, он будет разбит на части.\n"
            "• Лимиты: ~150 запросов в день, ~15 в минуту.\n"
            "• Если возникла ошибка, проверьте токен GitHub в коде."
        )
        await context.bot.send_message(chat_id=query.message.chat_id, text=help_text)

# ============================== ТОЧКА ВХОДА ==============================
def main():
    # Проверяем, что ключи заданы
    if not BOT_TOKEN:
        logger.error("Ошибка: не задан BOT_TOKEN")
        return
    if not GITHUB_TOKEN or GITHUB_TOKEN == "github_pat_...":
        logger.error("Ошибка: не задан или не изменён GITHUB_TOKEN")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))

    logger.info(f"Бот с GitHub Models ({MODEL_NAME}) запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()

