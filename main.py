from flask import Flask, request, make_response
import json
import logging

from TaskHandler import TaskHandler
from TelegramBot import TelegramBot

config = json.load(open('bot_config_private.json'))
HOST = config['app_engine_host']
TELEGRAM_TOKEN = config['telegram_token']

app = Flask(__name__)
bot = TelegramBot()

logging.basicConfig(format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
                    level=logging.INFO)

@app.route('/')
def index():
    return '1'


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    req = request.get_json(force=True)
    logging.info('Received fulfillment request.')
    try:
        task_handler = TaskHandler(req)
        return make_response(task_handler.handle())
    except Exception:
        logging.error('Failed to handle request.')
        return 'failed'


@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def telegramWebhook():
    logging.info('Received update from telegram.')
    if request.method == "POST":
        try:
            bot.enqueueOnWebhook(request.get_json(force=True))
        except Exception:
            logging.error('Failed to handle telegram update.')
            return 'failed'

    return 'ok'


@app.route('/set_telegram_webhook', methods=['GET', 'POST'])
def setTelegramWebhook():
    s = bot.bot.set_webhook(url='https://{}/{}'.format(HOST, TELEGRAM_TOKEN))
    if s:
        logging.info('Telegram webhook setup ok.')
        return "webhook setup ok."
    else:
        logging.error('Telegram webhook setup failed.')
        return "webhook setup failed."

if __name__ == '__main__':
    app.run()
