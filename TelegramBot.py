import json
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from DialogflowClient import DialogflowClient
import logging

FINISH_ADDING = 0
ADD_CRUSH = 1
REMOVE_CRUSH = 2
class TelegramBot:
    def __init__(self):
        with open('bot_config_private.json') as f:  # Use bot_config_private.json for development
            config = json.load(f)

        self.updater = Updater(token=config['telegram_token'])
        self.dispatcher = self.updater.dispatcher
        self.dfClient = DialogflowClient()

        text_handler = MessageHandler(Filters.text, self._receiveText)
        self.dispatcher.add_handler(text_handler)

        crush_handler = SecretCrush().convHandler
        self.dispatcher.add_handler(crush_handler)

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

    def start(self):
        self.updater.start_polling()

    def _receiveText(self, bot, update):
        bot.send_chat_action(chat_id=update.message.chat_id, action='TYPING')
        reply = self.dfClient.detectIntent(update.message.chat_id, update.message.text)
        bot.send_message(chat_id=update.message.chat_id, text=reply)

    def _receiveCrush(self, bot, update):
        bot.send_chat_action(chat_id=update.message.chat_id, action='TYPING')
        bot.send_message(chat_id=update.message.chat_id, text='Dududu')

class SecretCrush:
    def __init__(self):
        self.convHandler = ConversationHandler(
            entry_points=[CommandHandler('ilike', self.startCrush)],

            states = {
                REMOVE_CRUSH: [MessageHandler(Filters.text, self.deleteCrush)],
                FINISH_ADDING: [MessageHandler(Filters.text, self.finishAdding)]
            },

            fallbacks=[CommandHandler('cancel', self.cancel)]

        )
    def startCrush(self, bot, update):
        reply_keyboard = [['I want to remove a crush']]
        update.message.reply_text("Hi! I'm Dudu, your wingman in relationship. "
                                  "\nNow, tell me the name of your SECRET CRUSH. Don't worry. I won't gossip.",
                                  reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
                                  )
        return FINISH_ADDING

    def finishAdding(self, bot, update):
        print('finishAdding', update.message.text)
        update.message.reply_text("Got it! I will notify you and your crush immediately once there's a match. "
                                  "Meanwhile, you can edit your crush list anytime. All the best!",
                                  reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def deleteCrush(self, bot, update):
        update.message.reply_text('Finished')
        return ConversationHandler.END

    def cancel(self, bot, update):
        update.message.reply_text('Bye! I hope we can talk again some day.',
                                  reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
