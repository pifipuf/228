import logging
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests
import os

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Ключи API
WEATHER_API_KEY = 'b42c6a56beeb9d375d969a79ce6286be'
TELEGRAM_TOKEN = '7908654479:AAHx3cBkh6DgZaJMAlooCf_b7jKrMFJ-fko'
NEWS_API_KEY = 'cacd0ef483324cca980117946259fd95'
CURRENCY_API_KEY = 'ba3b9403583fdf701dc523e7'

# Функция для получения погоды
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

# Функция для получения новостей
def get_news():
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    data = response.json()
    if data.get('articles'):
        news = "\n\n".join([f"{article['title']} - {article['description']}" for article in data['articles'][:5]])
        return news
    else:
        return "Не удалось получить новости."

# Функция для получения курса валют
def get_exchange_rate():
    url = f'https://api.exchangerate-api.com/v4/latest/USD'
    response = requests.get(url)
    data = response.json()
    if data.get('rates'):
        rate = data['rates']['EUR']
        return f"Курс доллара к евро: {rate}"
    else:
        return "Не удалось получить курс валют."

# Функция для команды /start
async def start(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("Отправить геопозицию", request_location=True)],
        [KeyboardButton("Новости"), KeyboardButton("Курс валют")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    
    # Отправляем приветственное сообщение с клавиатурой
    await update.message.reply_text("Привет, я Илья, и я могу помочь тебе с погодой, новостями и курсом валют. Выбери опцию:", reply_markup=reply_markup)

# Основная функция для запуска Telegram-бота
async def run_bot():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Обработчики сообщений
    application.run_polling()

# Роут для корневого URL
@app.route('/')
def index():
    return 'Bot is running!'

# Роут для запуска бота
@app.route('/start_bot', methods=["GET", "POST"])
def start_bot():
    run_bot()
    return "Bot started!"

# Стартовый командный скрипт для запуска Flask-сервера и бота
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
