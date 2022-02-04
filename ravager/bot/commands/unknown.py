from telegram.ext import Filters, MessageHandler


class Unknown:
    def __init__(self):
        pass

    def unknown_callback(self, update, context):
        update.message.reply_text(quote=True, text="I am sorry,I didn't understand you")

    def unknown_handler(self):
        unknown = MessageHandler(filters=Filters.all, callback=self.unknown_callback)
        return unknown
