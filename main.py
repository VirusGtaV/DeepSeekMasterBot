import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# --- Настройки логирования ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- ТВОИ КЛЮЧИ (ВСТАВЛЕНЫ) ---
BOT_TOKEN = "8475855320:AAERPPB2INBiymqDt0JJjhhnKP6A3Fg-mLI"
OPENROUTER_API_KEY = "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"

# --- Клиент OpenRouter ---
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "https://bothost.ru/DeepSeekMasterBot",  # Можно оставить как есть
        "X-Title": "DeepSeekMasterBot",
    }
)

# --- Системный промпт (на русском) ---
SYSTEM_PROMPT = "Ты — полезный, умный и дружелюбный ассистент. Отвечай на русском языке."

# --- Бесплатная модель через OpenRouter (Qwen 2.5 72B) ---
MODEL_NAME = "qwen/qwen-2.5-72b-instruct:free"

async def query_model(user_message: str) -> str:
    """Отправляет запрос к модели и возвращает ответ"""
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            )
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Ошибка OpenRouter: {e}")
        return "❌ Ошибка при обращении к модели. Попробуйте позже."

# --- Обработчики Telegram ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я **DeepSeekMasterBot**, но теперь работаю через OpenRouter на модели Qwen 2.5.\n"
        "Я понимаю русский язык и отвечаю бесплатно.\n"
        "Просто напиши свой вопрос!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.chat.send_action(action="typing")
    response = await query_model(user_text)
    await update.message.reply_text(response)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Бот (OpenRouter) запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()