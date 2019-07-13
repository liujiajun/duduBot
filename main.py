from flask import Flask, request, make_response
import telegram
import logging

from TaskHandler import TaskHandler
from TelegramBot import TelegramBot

HOST = 'dudubot.appspot.com:8443'  # e7f8c83a.ngrok.io'
PORT = 8443

app = Flask(__name__)
bot = TelegramBot()
context = ('telegram1.pem', 'telegram1.key')

@app.route('/')
def index():
    return '1'


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    return make_response(handleRequest())


def handleRequest():
    req = request.get_json(force=True)
    print('Received new request:')
    print(req)
    task_handler = TaskHandler(req)

    return task_handler.handle()


# @app.route('/telegramwebhook', methods=['POST'])
# def telegramWebhook():
#     bot.enqueueOnWebhook(request.get_json(force=True))


# @app.route('/set_telegram_webhook', methods=['GET', 'POST'])
# def setTelegramWebhook():
#     s = bot.bot.set_webhook(url='https://{}/telegramwebhook'.format(HOST),
#                             certificate=open('telegram.pem', 'rb'))
#     if s:
#         return "webhook setup ok"
#     else:
#         return "webhook setup failed"

if __name__ == '__main__':
    #bot.start()
    app.run()
    #bot.idle()
