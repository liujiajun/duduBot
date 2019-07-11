import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from DialogflowClient import DialogflowClient
import logging


class TelegramBot:
    def __init__(self):
        with open('bot_config_private.json') as f:  # Use bot_config_private.json for development
            config = json.load(f)

        self.updater = Updater(token=config['telegram_token'])
        self.dispatcher = self.updater.dispatcher
        self.dfClient = DialogflowClient()

        text_handler = MessageHandler(Filters.text, self._receiveText)
        self.dispatcher.add_handler(text_handler)

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

    def start(self):
        self.updater.start_polling()

    def _receiveText(self, bot, update):
        print(update.message.chat_id)
        bot.send_chat_action(chat_id=update.message.chat_id, action='TYPING')
        reply = self.dfClient.detectIntect(update.message.chat_id, update.message.text)
        bot.send_message(chat_id=update.message.chat_id, text=reply)

    def _receiveImage(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text='I received an image')
