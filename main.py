import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# --- Настройки логирования ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Твои ключи (вставлены напрямую) ---
BOT_TOKEN = "8475855320:AAERPPB2INBiymqDt0JJjhhnKP6A3Fg-mLI"
DEEPSEEK_API_KEY = "sk-a395259d4fb64376b9e9c606b39c49cc"

# --- Клиент DeepSeek ---
client = OpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=DEEPSEEK_API_KEY,
)

# --- Системный промпт ---
SYSTEM_PROMPT = "Ты — полезный, умный и дружелюбный ассистент. Отвечай на русском языке."

async def query_deepseek(user_message: str) -> str:
    """Отправляет запрос к DeepSeek и возвращает ответ"""
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            )
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Ошибка DeepSeek: {e}")
        return "❌ Произошла ошибка при обращении к DeepSeek. Попробуйте позже."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я **DeepSeekMasterBot**.\n"
        "Я понимаю русский язык, помогаю с программированием, логикой и любыми вопросами.\n"
        "Просто напиши свой вопрос!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.chat.send_action(action="typing")
    response = await query_deepseek(user_text)
    await update.message.reply_text(response)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Бот DeepSeekMasterBot запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()