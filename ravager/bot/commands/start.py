from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from hashlib import blake2b
from ravager.bot.helpers.constants import *
from datetime import datetime, timedelta
import pytz
from ravager.bot.helpers.timeout import ConversationTimeout
from ravager.bot.helpers.validators import *
from ravager.database.helpers.structs import UserStruct
from ravager.database.users import UserData
from ravager.services.google.helpers.controller import GoogleController
from ravager.config import GROUP_PASSWORD, USER_PASSWORD, TIMEZONE


class Start:
    def __init__(self):
        self.end_selection = ConversationTimeout().end_selection
        self.selection_timeout = ConversationTimeout().selection_timeout

    @check_filters(is_start=True)
    @check_group_admin(is_start=True)
    def start(self, update, context):
        user = UserStruct()
        user_id = str(update.effective_user.id)
        user.user_id = str(update.effective_chat.id)
        chat_id = str(update.effective_chat.id)
        user = UserData(user).get_user()
        allowlist_status = os.environ.get("ALLOWLIST")
        if not UserData().get_num_of_users() and (str(update.effective_chat.type) == "group" or str(
                update.effective_chat.type) == "supergroup"):
            update.message.reply_text(quote=True,
                                      text="This bot can't be initialised for the first time in a group or supergroup")
            return END
        if user is None or not user.authorized:
            if allowlist_status:
                if str(update.effective_chat.type) == "group" or str(update.effective_chat.type) == "supergroup":
                    update.message.reply_text(quote=True,
                                              text="Provide your allowlisting password in private chat and proceed "
                                                   "accordingly")
                    private_msg = context.bot.send_message(chat_id=user_id,
                                                           text="Send your allowlisting password by replying to this",
                                                           reply_markup=ForceReply(selective=True))
                    context.user_data["user_id"] = user_id
                    context.user_data["user_msg_id"] = private_msg.message_id
                    context.user_data["from_chat"] = chat_id
                    context.user_data["time"] = datetime.now(pytz.timezone(TIMEZONE))
                    context.user_data["group_name"] = update.effective_chat.title
                    context.user_data["allowlisting"] = True
                    context.user_data["group"] = True
                    admins = update.message.bot.get_chat_administrators(chat_id=chat_id)
                    admin_list = []
                    for i in admins:
                        admin_list.append(i.user.id)
                    context.user_data["admins"] = ",".join([str(i) for i in admin_list])
                    return END
                update.message.reply_text(quote=True, text="Provide your allowlisting password",
                                          reply_markup=ForceReply(selective=True))
                return GET_ALLOWLIST_PASSWD
            else:
                return SEND_AUTH_URL
        else:
            if str(update.effective_chat.type) == "group" or str(update.effective_chat.type) == "supergroup":
                update.message.reply_text(quote=True, text="Welcome back {}!".format(update.effective_chat.title))
            else:
                update.message.reply_text(quote=True, text="Welcome back {}!".format(update.message.from_user.username))
            return END

    def get_allowlist_passwd(self, update, context):
        if "group" in context.user_data and bool(context.user_data["group"]):
            allowlist_passwd = GROUP_PASSWORD
            context.user_data["group"] = False
        else:
            allowlist_passwd = USER_PASSWORD
        user_data = str(update.message.text)
        if user_data == allowlist_passwd:
            self.send_auth_url(update, context)
            return END
        else:
            update.message.reply_text(text="Invalid allowlisting password,Try Again", quote=True)
            return END

    def send_auth_url(self, update, context):
        user = UserStruct()
        if "group" in context.user_data and update.effective_user.id != context.user_data["from_chat"]:
            chat_id = context.user_data["from_chat"]
            user.tg_group_title = context.user_data["group_name"]
            admins = context.user_data["admins"].split(",")
            user.tg_group_admins = admins
        else:
            chat_id = update.effective_user.id
        context.user_data.clear()
        user_id = update.effective_user.id
        user.user_id = chat_id
        google = GoogleController()
        state = blake2b(key=SECRET_SALT, digest_size=16)
        state.update(str(chat_id).encode("utf-8"))
        state = state.hexdigest()
        auth_url = google.get_oauth_url(state=state)
        # callback_data="authorize|authorization process started for {}".format(chat_id)
        auth_button = [InlineKeyboardButton(text="Authorize", url=auth_url)]
        reply_markup = InlineKeyboardMarkup([auth_button])
        context.bot.send_message(chat_id=chat_id,
                                 text="Authorize the bot by clicking on the button and proceed accordingly",
                                 reply_markup=reply_markup)
        user.state = state
        if chat_id == user_id:
            user.tg_username = update.effective_chat.username
            if not UserData().get_num_of_users():
                user.is_admin = True
            user.tg_firstname = update.effective_chat.first_name
            UserData(user).set_user()
        else:
            UserData(user).set_user()

        return END

    def reply_handler(self, update, context):
        current_time = datetime.now(pytz.timezone(TIMEZONE))
        valid_time = timedelta(minutes=5)
        if "allowlisting" in context.user_data:
            if (context.user_data["allowlisting"] and (context.user_data["time"] - current_time <= valid_time)
                    and (update.message.reply_to_message.message_id == context.user_data["user_msg_id"])):
                self.get_allowlist_passwd(update, context)
            else:
                context.user_data["allowlisting"] = False
                if context.user_data["allowlisting"]:
                    update.message.reply_text(text="Timed out or Replied to Invalid message,Try allowlisting again",
                                              quote=True)
        else:
            update.message.reply_text(text="Try starting the conversation again using /start",
                                      quote=True)

    def reply_msg_handler(self):
        reply_handler = MessageHandler(
            filters=(Filters.text & Filters.reply & (~Filters.chat_type.groups) & (~Filters.forwarded)),
            callback=self.reply_handler)
        return reply_handler

    def authorization_convo_handler(self):
        authorization_convo_handler = ConversationHandler(
            name="authorize",
            persistent=True,
            per_user=True,
            per_chat=True,
            entry_points=[CommandHandler("start", self.start)],
            states={
                GET_ALLOWLIST_PASSWD: [MessageHandler(Filters.text, self.get_allowlist_passwd)],

                SEND_AUTH_URL: [CallbackQueryHandler(self.send_auth_url)],

                ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, self.selection_timeout)]

            },
            fallbacks=[CommandHandler('cancel', self.end_selection),
                       MessageHandler(Filters.regex('^\/'), self.end_selection)],
            conversation_timeout=60

        )
        return authorization_convo_handler
