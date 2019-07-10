from flask import Flask, request, make_response, jsonify
import json
from telegram.ext import Updater
import threading

from TaskHandler import TaskHandler
from TelegramBot import TelegramBot
app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello!'


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    return make_response(handleRequest())


def handleRequest():
    req = request.get_json(force=True)
    print('Received new request:')
    print(req)
    task_handler = TaskHandler(req)

    return task_handler.handle()


if __name__ == '__main__':
    bot = TelegramBot()
    bot.start()
    app.run()
    bot.updater.idle()
