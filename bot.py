import os
import telebot
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ['API_KEY']
bot = telebot.TeleBot(API_KEY)

bot.polling(none_stop=False, interval=0, timeout=20)

bot.set_webhook(url='https://interesting-hedwig-bot.herokuapp.com/')

@bot.message_handler(commands=['start'])
def greet(message):
  bot.reply_to(message, 'This is the very start of our Adventure. If you are ready, just send me a letter with Hedwig. The letter should include the Task word with the number of the task. To start with the first one send \'Task 1\'.')

@bot.message_handler(regexp=r'(?i)task\s*1')
def task_1(message):
  bot.send_message(message.chat.id, 'This is task 1 blablabla')

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, 'Sorry I dont know that')