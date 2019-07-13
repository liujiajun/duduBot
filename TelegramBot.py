import json
from queue import Queue
from threading import Thread
from telegram.update import Update
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, Dispatcher
from DialogflowClient import DialogflowClient
import logging

from SecretCrush import SecretCrush


class TelegramBot:
    def __init__(self):
        with open('bot_config_private.json') as f:  # Use bot_config_private.json for development
            self.config = json.load(f)

        self.updater = Updater(token=self.config['telegram_token'])

        self.dispatcher = self.updater.dispatcher

        # self.bot = Bot(self.config['telegram_token'])
        # self.updateQueue = Queue()

        # self.dispatcher = Dispatcher(self.bot, self.updateQueue)

        crush_handler = SecretCrush().conversationHandler
        self.dispatcher.add_handler(crush_handler)
        text_handler = MessageHandler(Filters.text, self._receiveText)
        self.dispatcher.add_handler(text_handler)

        # self.thread = Thread(target=self.dispatcher.start, name='dispatcher')
        # self.thread.start()

        self.dfClient = DialogflowClient()

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

    def start(self):
        self.updater.start_polling()

    def idle(self):
        self.updater.idle()

    # def enqueueOnWebhook(self, updateJson):
    #    update = Update.de_json(updateJson)
    #    self.updateQueue.put(update)

    def _receiveText(self, bot, update):
        print('Received text')
        bot.send_chat_action(chat_id=update.message.chat_id, action='TYPING')
        reply = self.dfClient.detectIntent(update.message.chat_id, update.message.text)
        bot.send_message(chat_id=update.message.chat_id, text=reply)
