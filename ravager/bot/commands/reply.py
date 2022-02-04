from telegram.ext import MessageHandler, Filters
import pytz
from datetime import datetime, timedelta
from ravager.bot.commands.start import Start
from ravager.config import TIMEZONE


class Reply(Start):
    def __init__(self):

        super().__init__()

    def reply_handler(self, update, context):
        user_id = str(update.effective_user.id)
        current_time = datetime.now(pytz.timezone(TIMEZONE))
        valid_time = timedelta(minutes=5)
        if (context.user_data["allowlisting"] and (context.user_data["time"] - current_time <= valid_time)
                and (update.message.reply_to_message.message_id == context.user_data["user_msg_id"])):
            self.get_allowlist_passwd(update, context)
        else:
            context.user_data["allowlisting"] = False
            if context.user_data["allowlisting"]:
                update.message.reply_text(text="Timed out or Replied to Invalid message,Try Whitelisting again",
                                          quote=True)

    def reply_msg_handler(self):
        reply_handler = MessageHandler(filters=(Filters.text & Filters.reply & (~Filters.group) & (~Filters.forwarded)),
                                       callback=self.reply_handler)
        return reply_handler
