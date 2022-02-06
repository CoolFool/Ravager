from telegram.ext import CommandHandler
from telegram import ParseMode

help_text = "**Ravager Bot Commands**" \
            "/start : `Start the authorization flow for google drive access` " \
            "/add_drive : `Set default drive either personal or shared drive through the menu` " \
            "/download : `Add download task`" \
            "/upload : `If a download fails you can reply to the source message or just upload manually`" \
            "/abort : `Abort an ongoing task`" \
            "/admin_interface : `Admin interface access only available in private chat and for admins`" \
            "/revoke : `Revoke and delete your google account on the bot`" \
            "/help : `See all the commands`"


class Help:
    def __init__(self):
        pass

    @staticmethod
    def help(update, context):
        update.message.reply_text(quote=True, text=help_text, parse_mode=ParseMode.MARKDOWN_V2)

    def help_handler(self):
        help_handler = CommandHandler("upload", self.help)
        return help_handler
