import requests
from telegram.ext import CommandHandler,CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from ravager.bot.helpers.validators import *
from ravager.database.users import UserData
from ravager.database.helpers.structs import UserStruct
import logging

logger = logging.getLogger(__file__)


class Revoke:
    def __init__(self):
        pass

    @check_authorized()
    @check_group_admin()
    def revoke(self, update, context):
        revoke_options = [
            [InlineKeyboardButton(text="Yes", callback_data="revoke|yes"),
             InlineKeyboardButton(text="No", callback_data="revoke|no")]]

        reply_markup = InlineKeyboardMarkup(revoke_options)
        update.message.reply_text(text="Are you sure about revoking access for all accounts using your email address?",
                                  reply_markup=reply_markup)

    def callback_handler(self, update, context):
        callback_data = update.callback_query.data
        callback_data = callback_data.split("|")
        option = callback_data[1]
        if option == "yes":
            user_id = str(update.effective_chat.id)
            user = UserStruct()
            user.user_id = user_id
            user = UserData(user=user).get_user()
            refresh_token = user.refresh_token
            try:
                resp = requests.post('https://oauth2.googleapis.com/revoke',
                                     params={'token': refresh_token},
                                     headers={'content-type': 'application/x-www-form-urlencoded'})
                logger.info(resp)
                UserData().delete_user("refresh_token", refresh_token)
                update.callback_query.edit_message_text(
                    text="Successfully revoked access for all accounts using the email address: {}".format(user.email))

            except Exception as e:
                logger.error(e)
                update.message.reply_text(quote=True,
                                          text="User revocation failed  for {}".format(
                                              update.message.from_user.username))
        elif option == "no":
            update.callback_query.edit_message_text(text="Revocation command ignored")
        else:
            update.callback_query.edit_message_text(text="This shouldn't be seen")

    def revoke_handler(self):
        handler = CommandHandler("revoke", self.revoke)
        return handler

    def revoke_callback_handler(self):
        abort_callback = CallbackQueryHandler(self.callback_handler, pattern="revoke")
        return abort_callback
