import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from deep_translator import GoogleTranslator, single_detection, exceptions
import gtts
from io import BytesIO

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Глобальная переменная для хранения введенного текста и исходного языка
user_text = ""
detected_lang = ""

# Словарь для отображения полных названий языков
lang_name_map = {
    "to_en": "английский",
    "to_ru": "русский",
    "to_uk": "украинский",
    "to_es": "испанский",
    "to_de": "немецкий",
    "to_fr": "французский",
    "to_zh": "китайский"
}

# Функция для перевода текста
def translate_text(text, target_lang):
    translator = GoogleTranslator(target=target_lang)
    return translator.translate(text)

# Функция для автоматического определения языка
def detect_language(text):
    try:
        lang = single_detection(text)
        return lang
    except exceptions.NotValidPayload:
        return "неизвестный язык"
    except Exception as e:
        logging.error(f"Ошибка определения языка: {e}")
        return "ошибка определения языка"

# Функция для генерации аудио с произношением
def generate_audio(text, lang):
    tts = gtts.gTTS(text, lang=lang)
    audio = BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)
    return audio

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне текст для перевода.")


# Обработка текста, который отправляет пользователь
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_text, detected_lang
    user_text = update.message.text

    # Определяем язык введенного текста
    detected_lang = detect_language(user_text)

    # Предлагаем варианты перевода с улучшенной компоновкой
    keyboard = [
        [
            InlineKeyboardButton("Английский", callback_data='to_en'),
            InlineKeyboardButton("Русский", callback_data='to_ru')
        ],
        [
            InlineKeyboardButton("Украинский", callback_data='to_uk'),
            InlineKeyboardButton("Испанский", callback_data='to_es')
        ],
        [
            InlineKeyboardButton("Немецкий", callback_data='to_de'),
            InlineKeyboardButton("Французский", callback_data='to_fr')
        ],
        [
            InlineKeyboardButton("Китайский", callback_data='to_zh')
        ],
        [
            InlineKeyboardButton("Начать новый перевод", callback_data='new_translation')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f"Выберите, на какой язык перевести:", reply_markup=reply_markup)


# Обработка нажатий на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_text, detected_lang
    query = update.callback_query
    await query.answer()

    if query.data == 'new_translation':
        # Сбрасываем текст и язык
        user_text = ""
        detected_lang = ""

        # Информируем пользователя о начале нового перевода
        await query.edit_message_text("Отправь мне текст для перевода.")
        return

    lang_map = {
        "to_en": "en",
        "to_ru": "ru",
        "to_uk": "uk",
        "to_es": "es",
        "to_de": "de",
        "to_fr": "fr",
        "to_zh": "zh-TW"
    }

    if query.data in lang_map:
        target_lang = lang_map[query.data]
        translated_text = translate_text(user_text, target_lang)
        language_name = lang_name_map[query.data]  # Получаем полное название языка
        response = f"Исходный текст : {user_text}\nПеревод ({language_name}): {translated_text}"

        # Генерация аудио
        audio = generate_audio(translated_text, target_lang)

        await query.edit_message_text(text=response)
        await query.message.reply_audio(audio=audio)


# Основная функция
if __name__ == '__main__':
    # Вставьте сюда ваш токен от Telegram Bot
    TOKEN = '8032649222:AAHxmrJS4WP9xTPPRU_J6MJE-wkXQBdRYg4'

    # Создаем приложение
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(button))

    # Запускаем бота
    application.run_polling()
