import logging, os, re, json
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.environ['API_KEY']
PORT = int(os.environ.get('PORT', 80))
NUM_OF_TASKS = int(os.environ.get('NUM_OF_TASKS', 0))
TASK_QUESTION, TASK, FINISH = range(3)
STATE = 1
f = open('tasks.json')
tasks = json.load(f)
f.close()

def start(update: Update, context: CallbackContext) -> int:
  global STATE
  STATE = 1
  user = update.message.from_user
  logger.info("%s started the game", user.first_name)
    
  reply_keyboard = [['Begin']]

  update.message.reply_text(
    tasks['WELCOME']['text'],
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
  )
  return TASK_QUESTION


def task_question(update: Update, context: CallbackContext) -> int:
  user = update.message.from_user
  logger.info("%s read task_%s question", user.first_name, STATE)
    
  update.message.reply_text(
    tasks['TASK_{}'.format(STATE)]['question'],
    reply_markup=ReplyKeyboardRemove(),
  )
  return TASK


def task_hint(update: Update, context: CallbackContext) -> int:
  user = update.message.from_user
  logger.info("%s asked for hint at task_%s", user.first_name, STATE)

  update.message.reply_text(
    tasks['TASK_{}'.format(STATE)]['hint'],
    reply_markup=ReplyKeyboardRemove(),
  )
  return TASK


def task_solve(update: Update, context: CallbackContext) -> int:
  user = update.message.from_user
  global STATE

  if(re.search(tasks['TASK_{}'.format(STATE)]['solution'], update.message.text)):
    logger.info("%s solved task_%s", user.first_name, STATE)
    
    if(STATE == NUM_OF_TASKS):
      logger.info("%s solved all the tasks", user.first_name)

      reply_keyboard = [['Finish']]
      update.message.reply_text(
        'You solved all the tasks!',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
      )
      return FINISH
        
    reply_keyboard = [['Next']]
    update.message.reply_text(
      'You solved the task, press Next if you are ready for the next one!',
      reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    STATE += 1
    return TASK_QUESTION

  logger.info("%s typed a wrong answer for task_%s", user.first_name, STATE)
  update.message.reply_text(
    'Wrong answer!\n'
    'If you need any help reply with \'Hint\'.\n'
    'If you would like to read the question again, reply with \'Task\'.',
    reply_markup=ReplyKeyboardRemove(),
  )
  return TASK


def finish(update: Update, context: CallbackContext) -> int:
  update.message.reply_text('Congratulations!')
  return ConversationHandler.END


def main() -> None:
  updater = Updater(TOKEN)

  dispatcher = updater.dispatcher

  conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
      TASK_QUESTION: [MessageHandler(Filters.text, task_question)],
      TASK: [
        MessageHandler(Filters.regex(r'(?i)(TASK)$'), task_question),
        MessageHandler(Filters.regex(r'(?i)(HINT)$'), task_hint),
        MessageHandler(Filters.text, task_solve)
      ],
      FINISH: [MessageHandler(Filters.text, finish)]
    },
    fallbacks=[],
  )

  dispatcher.add_handler(conv_handler)

  if(os.environ.get('IS_LOCAL', False)):
    updater.start_polling()
  else:
    updater.start_webhook(
      listen="0.0.0.0",
      port=int(PORT),
      url_path=TOKEN,
      webhook_url='https://interesting-hedwig-bot.herokuapp.com/' + TOKEN
    )

    updater.idle()


if __name__ == '__main__':
  main()