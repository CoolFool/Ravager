from ravager.bot.helpers.constants import *


class ConversationTimeout:
    def __init__(self):
        pass

    @staticmethod
    def end_selection(update,context):
        update.message.reply_text(quote=True, text="Conversation ended")
        return END

    @staticmethod
    def selection_timeout(update,context):
        update.message.reply_text(quote=True, text="Conversation has timed out")
        return END
