# ============================== ИМПОРТЫ ==============================
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import g4f
from g4f.client import Client

# ============================== НАСТРОЙКИ ==============================
# Включаем подробное логирование, чтобы видеть все процессы
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ⚠️ ВАШ ТОКЕН ОТ BOTFATHER (вставьте сюда)
BOT_TOKEN = "8475855320:AAERPPB2INBiymqDt0JJjhhnKP6A3Fg-mLI"

# ============================== КЛИЕНТ G4F ==============================
# Создаём клиента G4F. Никаких ключей не нужно!
# Если какой-то провайдер временно не работает, клиент автоматически попробует другие [citation:9].
client = Client()

# Модель, которую будем использовать. Можно выбрать любую из поддерживаемых.
# "gpt-4o-mini" — хороший баланс скорости и качества.
MODEL_NAME = "gpt-4o-mini"

# ============================== ФУНКЦИЯ ЗАПРОСА К AI ==============================
async def query_ai(user_message: str) -> str:
    """
    Отправляет запрос к AI через g4f и возвращает ответ.
    Используется асинхронный метод для неблокирующей работы [citation:2].
    """
    try:
        # Асинхронный вызов для генерации ответа
        response = await client.chat.completions.async_create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": user_message}],
            temperature=0.7,      # Немного креативности
            timeout=30             # Ждём ответ не больше 30 секунд
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Ошибка G4F: {e}")
        return "❌ Ошибка при обращении к AI. Попробуйте позже."

# ============================== ОБРАБОТЧИК КОМАНДЫ /start ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение с информацией о боте."""
    await update.message.reply_text(
        f"👋 Привет! Я бот на базе **g4f (GPT4Free)**.\n"
        f"Я использую модель `{MODEL_NAME}` и работаю полностью бесплатно, без ключей.\n"
        "Библиотека автоматически выбирает работающего провайдера, но стабильность не гарантируется [citation:5].\n"
        "Просто задавай вопросы!"
    )

# ============================== ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ ==============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получает текст от пользователя, отправляет запрос в AI и возвращает ответ."""
    await update.message.chat.send_action(action="typing")
    reply = await query_ai(update.message.text)

    MAX_LENGTH = 4096  # Лимит Telegram на одно сообщение

    # Кнопки для удобства
    keyboard = [
        [InlineKeyboardButton("🔄 Новый диалог", callback_data="new_chat")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Разбиваем длинный ответ на части, если он превышает лимит Telegram
    if len(reply) > MAX_LENGTH:
        for i in range(0, len(reply), MAX_LENGTH):
            part = reply[i:i+MAX_LENGTH]
            await update.message.reply_text(part)
        # После всех частей отправляем сообщение с кнопками
        await update.message.reply_text("✅ Ответ полностью отправлен. Что дальше?", reply_markup=reply_markup)
    else:
        await update.message.reply_text(reply, reply_markup=reply_markup)

# ============================== ОБРАБОТЧИК НАЖАТИЙ НА КНОПКИ ==============================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на инлайн-кнопки."""
    query = update.callback_query
    await query.answer()
    if query.data == "new_chat":
        await context.bot.send_message(chat_id=query.message.chat_id, text="🔄 Новый диалог начат!")
    elif query.data == "help":
        help_text = (
            "📚 **Как пользоваться ботом:**\n"
            "• Просто отправьте сообщение — я отвечу.\n"
            f"• Используется модель **{MODEL_NAME}** через g4f.\n"
            "• Если ответ длинный, он будет разбит на части.\n"
            "• Библиотека автоматически переключает провайдеров при сбоях [citation:9], но 100% стабильность не гарантируется [citation:5]."
        )
        await context.bot.send_message(chat_id=query.message.chat_id, text=help_text)

# ============================== ТОЧКА ВХОДА ==============================
def main():
    """Запускает бота."""
    if not BOT_TOKEN:
        logger.error("Ошибка: не задан BOT_TOKEN")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))

    logger.info("Бот с g4f запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
