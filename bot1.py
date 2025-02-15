import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# API ключи
WEATHER_API_KEY = 'b42c6a56beeb9d375d969a79ce6286be'
TELEGRAM_TOKEN = '7908654479:AAHx3cBkh6DgZaJMAlooCf_b7jKrMFJ-fko'
NEWS_API_KEY = 'cacd0ef483324cca980117946259fd95'
CURRENCY_API_KEY = 'ba3b9403583fdf701dc523e7'

# Функции для получения информации
def get_weather(lat, lon):
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric'
    response = requests.get(url)
    data = response.json()
    if data.get('main'):
        temp = data['main']['temp']
        description = data['weather'][0]['description']
        return f"Температура: {temp}°C, {description.capitalize()}"
    else:
        return "Не удалось получить погоду."

def get_news():
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    data = response.json()
    if data.get('articles'):
        news = "\n\n".join([f"{article['title']} - {article['description']}" for article in data['articles'][:5]])
        return news
    else:
        return "Не удалось получить новости."

def get_exchange_rate():
    url = f'https://api.exchangerate-api.com/v4/latest/USD' 
    response = requests.get(url)
    data = response.json()
    if data.get('rates'):
        rate = data['rates']['EUR'] 
        return f"Курс доллара к евро: {rate}"
    else:
        return "Не удалось получить курс валют."

# Функция для старта
async def start(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("Отправить геопозицию", request_location=True)],
        [KeyboardButton("Новости"), KeyboardButton("Курс валют")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text("Привет, я Илья, и я могу помочь тебе с погодой, новостями и курсом валют. Выбери опцию:", reply_markup=reply_markup)

# Обработка геопозиции
async def handle_location(update: Update, context: CallbackContext):
    user_location = update.message.location
    latitude = user_location.latitude
    longitude = user_location.longitude
    weather = get_weather(latitude, longitude)
    await update.message.reply_text(f"Ты находишься в точке {latitude}, {longitude}. {weather}")

# Обработка новостей
async def handle_news(update: Update, context: CallbackContext):
    news = get_news()
    await update.message.reply_text(news)

# Обработка курса валют
async def handle_exchange(update: Update, context: CallbackContext):
    exchange = get_exchange_rate()
    await update.message.reply_text(exchange)

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Обрабатываем команду /start
    application.add_handler(CommandHandler("start", start))

    # Обработчики для различных запросов
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Новости$'), handle_news))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Курс валют$'), handle_exchange))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
