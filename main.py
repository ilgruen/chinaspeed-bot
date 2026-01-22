import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "8296404221")

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие"""
    await update.message.reply_text(
        "👋 Привет! Я бот China Speed Logistics.\n\n"
        "🚀 Хотите получить программу внедренческой миссии в Китай?\n\n"
        "Напишите мне одним сообщением:\n"
        "• Ваше имя\n"
        "• Компания\n"
        "• Должность\n"
        "• Почему интересует поездка\n\n"
        "И я сразу пришлю вам программу! 📄"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка любого сообщения"""
    user = update.effective_user
    text = update.message.text
    
    # Отправляем лид админу
    lead_info = (
        f"🔥 НОВЫЙ ЛИД!\n\n"
        f"📝 Сообщение:\n{text}\n\n"
        f"📱 Telegram: @{user.username if user.username else 'нет'}\n"
        f"🆔 ID: {user.id}\n"
        f"👤 Имя в TG: {user.first_name} {user.last_name or ''}"
    )
    
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=lead_info)
    except Exception as e:
        logging.error(f"Ошибка отправки админу: {e}")
    
    # Отправляем PDF пользователю
    await update.message.reply_text("Спасибо! ✅ Вот программа миссии:")
    
    try:
        with open('china-speed-program.pdf', 'rb') as pdf:
            await update.message.reply_document(
                document=pdf,
                filename='China_Speed_Program.pdf',
                caption="📄 Миссия 25 мая – 1 июня 2025\n\nВопросы? → @chinaspeedlogistics"
            )
    except:
        await update.message.reply_text(
            "📄 Программу пришлём вам лично.\n"
            "Напишите в @chinaspeedlogistics"
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
