import json
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from google.cloud import datastore
from google.oauth2 import service_account
import datetime

FINISH_ADDING = 0
FINISH_DELETING = 1


class SecretCrush:
    def __init__(self):
        self.conversationHandler = ConversationHandler(
            entry_points=[CommandHandler('ilike', self.welcome)],

            states={
                FINISH_ADDING: [MessageHandler(Filters.text | Filters.contact, self.finishAdding)],
                FINISH_DELETING: [MessageHandler(Filters.text | Filters.contact, self.finishDeleting)]
            },

            fallbacks=[CommandHandler('cancel', self.cancel)]

        )

        with open('bot_config_private.json') as f:
            config = json.load(f)
        self.credential = service_account.Credentials.from_service_account_file(config['app_engine_credential_path'])

        # create Google database client
        self.dataClient = datastore.Client(project=config['app_engine_project_id'], credentials=self.credential)

    def welcome(self, bot, update):
        reply_keyboard = [['Add a Crush'], ['Remove Crushes'], ['Show Crush List']]
        self.kb_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
        update.message.reply_text("Hi! I'm Dudu, your WINGMAN in relationship. "
                                  "\nNow, share the contact of your SECRET CRUSH "
                                  "(click the clip-shaped button left to textbox, then select Contact). "
                                  "Don't worry. I won't gossip.",
                                  reply_markup=self.kb_markup
                                  )
        return FINISH_ADDING

    def finishAdding(self, bot, update):
        if update.message.text == 'Add a Crush':
            update.message.reply_text("Great! Who's your crush?",
                                      reply_markup=ReplyKeyboardRemove())
            return FINISH_ADDING

        elif update.message.text == 'Remove Crushes':
            update.message.reply_text('Who do you want to remove from your crush list?',
                                      reply_markup=ReplyKeyboardRemove())
            return FINISH_DELETING

        elif update.message.text == 'Show Crush List':
            reply = self.show(update.message.from_user.id)
            if not reply:
                update.message.reply_text("You don't have any crush yet.",
                                          reply_markup=self.kb_markup)
            else:
                update.message.reply_text(reply, reply_markup=self.kb_markup)

            return FINISH_ADDING

        else:
            if update.message.contact != None:
                try:
                    self.insert(update.message.from_user.id,
                                update.message.contact.user_id,
                                update.message.contact.first_name)
                except Exception:
                    update.message.reply_text("I've run into a problem. Please try again later.")

                update.message.reply_text("Got it! I will notify you and your crush immediately once there's a match. "
                                          "Meanwhile, you can edit your crush list anytime. Love wins!",
                                          reply_markup=self.kb_markup)
                return FINISH_ADDING

            else:
                update.message.reply_text("Could you share your crush as a contact? "
                                          "Just click the clip-shaped button left to textbox, then select Contact",
                                          reply_markup=self.ReplyKeyboardRemove())
                return FINISH_ADDING

    def finishDeleting(self, bot, update):
        if update.message.contact != None:
            try:
                res = self.removeById(update.message.from_user.id, update.message.contact.user_id)
            except Exception:
                update.message.reply_text("I've run into a problem. Please try again later.")
        if res == 0:
            update.message.reply_text('OK.', reply_markup=self.kb_markup)
        else:
            update.message.reply_text(
                "Sorry. {} is not found in your crush list.".format(update.message.contact.first_name))
        return FINISH_ADDING

    def cancel(self, bot, update):
        update.message.reply_text('Bye! I hope we can talk again some day.',
                                  reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def insert(self, admirer_id, crush_id, crush_name):
        key = self.dataClient.key('Crush', admirer_id)  # admirer's key
        admirer = self.dataClient.get(key)
        if not admirer:
            # First time user. Create key.
            admirer = datastore.Entity(key)
            admirer.update({
                'last_modified': datetime.datetime.utcnow(),
                'ids': [
                    crush_id
                ],
                'names': [
                    crush_name
                ]
            })
        elif not crush_id in admirer['ids']:
            admirer['ids'].append(crush_id)
            admirer['names'].append(crush_name)
        self.dataClient.put(admirer)

    def removeById(self, admirer_id, crush_id):
        key = self.dataClient.key('Crush', admirer_id)
        admirer = self.dataClient.get(key)
        if not admirer:
            return -1
        elif crush_id not in admirer['ids']:
            return -1
        print(admirer['ids'])
        print(admirer['names'])
        admirer['names'].pop(admirer['ids'].index(crush_id))
        admirer['ids'].pop(admirer['ids'].index(crush_id))
        self.dataClient.put(admirer)
        return 0

    def show(self, my_id):
        key = self.dataClient.key('Crush', my_id)
        admirer = self.dataClient.get(key)
        if not admirer:
            return None
        else:
            reply = 'Your crushes:\n'
            for name in admirer['names']:
                reply = reply + name + '\n'
            return reply


if __name__ == '__main__':
    sc = SecretCrush()
