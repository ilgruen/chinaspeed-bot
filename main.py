import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "8296404221")  # Твой Telegram ID для получения лидов

# Этапы разговора
NAME, COMPANY, POSITION, INTEREST = range(4)

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало разговора"""
    await update.message.reply_text(
        "👋 Привет! Я бот China Speed Logistics.\n\n"
        "Вы хотите получить программу внедренческой миссии в Китай?\n\n"
        "Ответьте на несколько вопросов, и я отправлю вам подробную программу.\n\n"
        "📝 Как вас зовут?",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняем имя, спрашиваем компанию"""
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        f"Приятно познакомиться, {update.message.text}! 🤝\n\n"
        "🏢 В какой компании вы работаете?"
    )
    return COMPANY

async def get_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняем компанию, спрашиваем должность"""
    context.user_data['company'] = update.message.text
    await update.message.reply_text(
        "Отлично! 👔 Какая у вас должность?"
    )
    return POSITION

async def get_position(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняем должность, спрашиваем интерес"""
    context.user_data['position'] = update.message.text
    await update.message.reply_text(
        "🎯 Почему вас заинтересовала поездка в Китай?\n\n"
        "Расскажите кратко о вашем бизнесе и что хотите увидеть/внедрить."
    )
    return INTEREST

async def get_interest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняем интерес, отправляем PDF и уведомление админу"""
    context.user_data['interest'] = update.message.text
    user = update.effective_user
    
    # Собираем данные лида
    lead_info = (
        f"🔥 НОВЫЙ ЛИД!\n\n"
        f"👤 Имя: {context.user_data['name']}\n"
        f"🏢 Компания: {context.user_data['company']}\n"
        f"👔 Должность: {context.user_data['position']}\n"
        f"🎯 Интерес: {context.user_data['interest']}\n\n"
        f"📱 Telegram: @{user.username if user.username else 'нет username'}\n"
        f"🆔 User ID: {user.id}"
    )
    
    # Отправляем уведомление админу
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=lead_info)
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление админу: {e}")
    
    # Отправляем благодарность и PDF пользователю
    await update.message.reply_text(
        f"Спасибо, {context.user_data['name']}! ✅\n\n"
        "Вот программа внедренческой миссии China Speed Logistics 4.0 👇"
    )
    
    # Отправляем PDF файл
    try:
        with open('china-speed-program.pdf', 'rb') as pdf_file:
            await update.message.reply_document(
                document=pdf_file,
                filename='China_Speed_Logistics_Program.pdf',
                caption="📄 Программа миссии 25 мая – 1 июня 2025\n\n"
                        "Остались вопросы? Пишите в @chinaspeedlogistics"
            )
    except FileNotFoundError:
        await update.message.reply_text(
            "📄 Программа будет отправлена вам в ближайшее время.\n\n"
            "Остались вопросы? Пишите в @chinaspeedlogistics"
        )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена разговора"""
    await update.message.reply_text(
        "Диалог отменён. Если захотите получить программу — напишите /start",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчик разговора
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_company)],
            POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_position)],
            INTEREST: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_interest)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Запуск
    print("🤖 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
