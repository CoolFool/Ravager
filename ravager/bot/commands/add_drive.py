from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
from ravager.bot.helpers.constants import *
from ravager.bot.helpers.timeout import ConversationTimeout
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from ravager.bot.helpers.validators import *
from ravager.database.helpers.structs import UserStruct
from ravager.database.users import UserData
from ravager.services.google.helpers.controller import GoogleController


class AddDrive:
    def __init__(self):
        self.pagination_num = 0
        self.end_selection = ConversationTimeout().end_selection
        self.selection_timeout = ConversationTimeout().selection_timeout
        self.user = UserStruct()
        self.drive_list = []
        self.page_dict = {}

    @check_authorized(is_convo=True)
    @check_filters(is_convo=True)
    def set_default_drive(self, update, context):
        self.user.user_id = str(update.effective_chat.id)
        drive_options = [
            [InlineKeyboardButton(text="Personal", callback_data="set_default|personal|{}".format(self.user.user_id)),
             InlineKeyboardButton(text="Shared Drive", callback_data="set_default|shared|{}".format(self.user.user_id))]]

        reply_markup = InlineKeyboardMarkup(drive_options)
        update.message.reply_text(quote=True, text="Set default drive for storing downloaded files",
                                  reply_markup=reply_markup)

        return DRIVE_HANDLER

    def drive_selection_handler(self, update, context):
        callback_data = update.callback_query.data
        callback_data = callback_data.split("|")
        method = callback_data[0]
        action = callback_data[1]
        if method == "set_default":
            user_id = str(update.effective_chat.id)
            self.user.user_id = user_id
            if action == "personal":
                self.user.storage_type = "personal"
                self.user.drive_id = ""
                UserData(user=self.user).set_user()
                update.callback_query.edit_message_text(text="Default Storage set to Personal")
                return END

            elif action == "shared":
                drive_list, page, pagination_num = self.shared_drive_list(user_id=user_id, page_dict={})
                self.drive_list = drive_list
                self.page_dict.update(page)
                self.pagination_num = pagination_num
                if not self.drive_list:
                    update.callback_query.edit_message_text(text="No Shared drives found,try again")
                    return END
                shared_drive_keyboard_btns = []
                for i in self.drive_list:
                    shared_drive_keyboard_btns.append([InlineKeyboardButton(text=str(i["name"]),
                                                                            callback_data="shared_drive|shared_drive|{}|{}".format(
                                                                                self.user.user_id, str(i["id"])))])
                if self.page_dict[pagination_num] is not None:
                    shared_drive_keyboard_btns.append([InlineKeyboardButton(text="Next",
                                                                            callback_data="shared_drive|next|{}|{}".format(
                                                                                self.user.user_id, pagination_num))])
                reply_markup = InlineKeyboardMarkup(shared_drive_keyboard_btns)
                update.callback_query.edit_message_text(text="Select Shared drives from the list below:",
                                                        reply_markup=reply_markup)
                return SHARED_DRIVE_SELECTION

    def shared_drive_selection(self, update, context):
        callback_data = update.callback_query.data
        callback_data = callback_data.split("|")
        method = callback_data[0]
        action = callback_data[1]
        if method == "shared_drive":
            if action == "shared_drive":
                shared_drive_id = str(callback_data[3])
                self.user.drive_id = shared_drive_id
                self.user.storage_type = "shared"
                UserData(user=self.user).set_user()
                logger.error(self.drive_list)
                for i in self.drive_list:
                    if i["id"] == shared_drive_id:
                        update.callback_query.edit_message_text(text="Default storage set as {}".format(i["name"]))
                        return END

            elif action == "next":
                page_num_tracker = int(callback_data[3])

                user_id = str(update.effective_chat.id)
                drive_list, page, pagination_num = self.shared_drive_list(user_id=user_id, page_dict=self.page_dict,
                                                                          next_page_token=self.page_dict[
                                                                              len(self.page_dict)])
                shared_drive_keyboard_btns = []
                for i in drive_list:
                    self.drive_list.append(i) if i not in self.drive_list else self.drive_list
                    shared_drive_keyboard_btns.append([InlineKeyboardButton(text=str(i["name"]),
                                                                            callback_data="shared_drive|shared_drive|{}|{}".format(
                                                                                self.user.user_id, str(i["id"])))])
                if page[pagination_num] is not None:
                    if page_num_tracker == 0:
                        drive_list, page, pagination_num = self.shared_drive_list(user_id=user_id, page_dict={})
                        self.drive_list.append(drive_list)
                        self.page_dict.update(page)
                        self.pagination_num = pagination_num
                        shared_drive_keyboard_btns = []
                        for i in drive_list:
                            shared_drive_keyboard_btns.append([InlineKeyboardButton(text=str(i["name"]),
                                                                                    callback_data="shared_drive|shared_drive|{}|{}".format(
                                                                                        self.user.user_id, str(i["id"])))])
                        if page[pagination_num] is not None:
                            self.page_dict.update(page)
                            shared_drive_keyboard_btns.append([InlineKeyboardButton(text="Next",
                                                                                    callback_data="shared_drive|next|{}|{}".format(
                                                                                        self.user.user_id, pagination_num))])
                        reply_markup = InlineKeyboardMarkup(shared_drive_keyboard_btns)
                        update.callback_query.edit_message_text(text="Select Shared drives from the list below:",
                                                                reply_markup=reply_markup)
                        return SHARED_DRIVE_SELECTION
                    else:
                        page_num_tracker -= 1
                        shared_drive_keyboard_btns.append([InlineKeyboardButton(text="Next",
                                                                                callback_data="shared_drive|next|{}|{}".format(
                                                                                    self.user.user_id, page_num_tracker))])

                reply_markup = InlineKeyboardMarkup(shared_drive_keyboard_btns)
                self.drive_list.append(drive_list)
                update.callback_query.edit_message_text(text="Select Shared drives from the list below:",
                                                        reply_markup=reply_markup)
                return SHARED_DRIVE_SELECTION

    def shared_drive_list(self, user_id, page_dict, next_page_token=None):
        pagination_num = 1
        gc = GoogleController()
        user_refresh_token = UserData(user=self.user).get_user().refresh_token
        google_creds = gc.credentials_handler(refresh_token=str(user_refresh_token))
        pagination = {}
        if next_page_token is None:
            drive_list, next_page_token = gc.get_shared_drive_list(google_auth_creds=google_creds)
        else:
            drive_list, next_page_token = gc.get_shared_drive_list(google_auth_creds=google_creds,
                                                                   next_page_token=next_page_token)
            pagination_num += 1

        pagination[pagination_num] = next_page_token
        page_dict = {**pagination}
        return drive_list, page_dict, pagination_num

    def default_convo_handler(self):
        set_default_convo_handler = ConversationHandler(
            entry_points=[CommandHandler("add_drive", self.set_default_drive)],
            states={
                DRIVE_HANDLER: [CallbackQueryHandler(self.drive_selection_handler, pattern="^set_default\|")],

                SHARED_DRIVE_SELECTION: [CallbackQueryHandler(self.shared_drive_selection, pattern="^shared_drive\|")],

                ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, self.selection_timeout)]
            },
            fallbacks=[CommandHandler('cancel', self.end_selection),
                       MessageHandler(Filters.regex('^\/'), self.end_selection)],
            conversation_timeout=300
        )
        return set_default_convo_handler
