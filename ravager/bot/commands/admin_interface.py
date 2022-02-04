import logging
from functools import wraps

import psutil
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply, ParseMode
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from ravager.bot.helpers.constants import *
from ravager.bot.helpers.timeout import ConversationTimeout
from ravager.config import MAX_TASKS_PER_USER, STORAGE_TIME, STORAGE_SIZE, GROUP_PASSWORD, USER_PASSWORD, ALLOWLIST, \
    DOWNLOAD_DIR, LOGS_DIR,HEROKU_APP,HEROKU_API_TOKEN
from ravager.database.helpers.structs import UserStruct
from ravager.database.users import UserData
from ravager.helpers.humanize import humanize

logger = logging.getLogger(__file__)

HANDLE_ADMIN_PANEL, LIMITS_PANEL, FILTERS_PANEL, SYS_INFO_PANEL, LOGS_HANDLER = range(5)

limits_panel_text = "*Limits Configuration:*\
        \nDownload storage size: *{}* GB\
        \nDownload storage time: *{}* Hrs\n"

filter_panel_text = "*Filters and User Configuration:*\
                    \nFilters Enabled: *{}*\nGroup chat password: *{}*\
                    \nPrivate chat password: *{}*"

sys_info_text = "*System Information*\
                \n*Cpu Usage Percent:* {}%\
                \n*Used Ram:* {} {}\
                \n*Available Ram:* {} {}\
                \n*Network Ingress:* {} {}\
                \n*Network Egress:* {} {}\
                \n*Total Disk Space:* {} {}\
                \n*Total Disk Space Available: *{} {}"


class AdminInterface:
    def __init__(self):
        self.end_selection = ConversationTimeout.end_selection
        self.selection_timeout = ConversationTimeout.selection_timeout
        self.user = UserStruct()

    def _restricted(handlers):
        wraps(handlers)

        def wrapper(self, update, context, *args, **kwargs):
            user_id = update.effective_user.id
            user = UserStruct()
            user.user_id = user_id
            user = UserData(user=user).get_user()
            if user is not None and bool(user.is_admin):
                return handlers(self, update, context, *args, **kwargs)

            update.message.reply_text(text="Unauthorized user", quote=True)
            logger.error("Unauthorized access denied for {}.".format(user_id))
            return -1

        return wrapper

    @staticmethod
    def admin_panel():
        admin_panel = [[InlineKeyboardButton(text="Limits", callback_data="admin|admin_limits"),
                        InlineKeyboardButton(text="Filters", callback_data="admin|admin_filters")],
                       [InlineKeyboardButton(text="Sys Info", callback_data="admin|admin_sys_info"),
                        InlineKeyboardButton(text="Close", callback_data="admin|close")]]
        return InlineKeyboardMarkup(admin_panel)

    @staticmethod
    def admin_interface_filters():
        filters_panel = [[InlineKeyboardButton(text="Revoke Access", callback_data="filters|revoke_user"),
                          InlineKeyboardButton(text="Add Admin", callback_data="filters|add_admin")],
                         [InlineKeyboardButton(text="Back", callback_data="admin|admin_main"),
                          InlineKeyboardButton(text="Close", callback_data="admin|close")]]

        return InlineKeyboardMarkup(filters_panel)

    @staticmethod
    def admin_interface_limts():
        limits_panel = [[InlineKeyboardButton(text="Back", callback_data="admin|admin_main"),
                         InlineKeyboardButton(text="Close", callback_data="admin|close")]]
        return InlineKeyboardMarkup(limits_panel)

    @staticmethod
    def admin_interface_sys_info():
        sys_info_panel = [[InlineKeyboardButton(text="System Info", callback_data="sys_info|sys_info"),
                           InlineKeyboardButton(text="Logs", callback_data="sys_info|logs")],
                          [InlineKeyboardButton(text="Back", callback_data="admin|admin_main"),
                           InlineKeyboardButton(text="Close", callback_data="admin|close")]]

        return InlineKeyboardMarkup(sys_info_panel)

    @staticmethod
    def toggle_panel(back_menu):
        toggle_panel = [[InlineKeyboardButton(text="Enable", callback_data=""),
                         InlineKeyboardButton(text="Disable", callback_data=""),
                         InlineKeyboardButton(text="Back", callback_data="{}|".format(back_menu))]]

        return InlineKeyboardMarkup(toggle_panel)

    @staticmethod
    def last_step_btns(prev_menu):
        last_step_panel = [[InlineKeyboardButton(text="Back", callback_data="{}".format(prev_menu)),
                            InlineKeyboardButton(text="Back to main menu", callback_data="admin|admin_main")]]

        return InlineKeyboardMarkup(last_step_panel)

    def handle_admin_panel(self, update, context):
        callback_data = update.callback_query.data
        callback_data = callback_data.split("|")
        selection_option = callback_data[1]

        if selection_option == "admin_main":
            update.callback_query.edit_message_text(text="Admin Panel", reply_markup=self.admin_panel())
            return HANDLE_ADMIN_PANEL

        if selection_option == "admin_limits":
            download_storage_time_threshold = STORAGE_TIME
            download_storage_size_threshold = STORAGE_SIZE
            stats = limits_panel_text.format(download_storage_size_threshold,download_storage_time_threshold)

            update.callback_query.edit_message_text(text=stats, reply_markup=self.admin_interface_limts(),
                                                    parse_mode=ParseMode.MARKDOWN)
            return LIMITS_PANEL

        if selection_option == "admin_filters":
            group_passwd = GROUP_PASSWORD
            private_passwd = USER_PASSWORD
            allowlist_enabled = str(ALLOWLIST)
            text = filter_panel_text.format(allowlist_enabled, group_passwd, private_passwd)
            update.callback_query.edit_message_text(text=text, reply_markup=self.admin_interface_filters(),
                                                    parse_mode=ParseMode.MARKDOWN)
            return FILTERS_PANEL

        if selection_option == "admin_sys_info":
            update.callback_query.edit_message_text(text="Sys Health", reply_markup=self.admin_interface_sys_info())
            return SYS_INFO_PANEL

        if selection_option == "close":
            update.callback_query.edit_message_text(text="Admin Interface closed")
            return -1

    def filters_options(self, update, context):
        chat_id = update.effective_chat.id
        callback_data = update.callback_query.data
        callback_data = callback_data.split("|")
        selection_option = callback_data[1]

        if selection_option == "revoke_user":
            text = "*Revoke user's access from bot*\nSend user's username or user id"
            update.callback_query.edit_message_text(text=text, parse_mode=ParseMode.MARKDOWN,
                                                    reply_markup=self.last_step_btns(prev_menu="admin|admin_filters"))
            context.bot.send_message(chat_id=chat_id, text="Username or User ID", parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=ForceReply())

        if selection_option == "add_admin":
            text = "*Revoke user's access from bot*\nSend user's username or user id"
            update.callback_query.edit_message_text(text=text, parse_mode=ParseMode.MARKDOWN,
                                                    reply_markup=self.last_step_btns(prev_menu="admin|admin_filters"))
            context.bot.send_message(chat_id=chat_id, text="Username or User ID", parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=ForceReply())

        return

    @staticmethod
    def get_logs(update, context):
        # dump logs properly
        user_id = update.effective_user.id
        try:
            context.bot.sendDocument(chat_id=user_id, document=open("{}/ravager.log".format(LOGS_DIR), "rb"))
            context.bot.sendDocument(chat_id=user_id, document=open("{}/celery.log".format(LOGS_DIR), "rb"))
            context.bot.sendDocument(chat_id=user_id, document=open("{}/aria2.log".format(LOGS_DIR), "rb"))
        except Exception as e:
            update.message.reply_text(chat_id=user_id, text=str(e))
            logger.error(e)

    @staticmethod
    def logs_panel():
        logs_panel = [[InlineKeyboardButton(text="Aria logs", callback_data="sys_info_logs|aria_logs"),
                       InlineKeyboardButton(text="Celery logs", callback_data="sys_info_logs|celery_logs"),
                       InlineKeyboardButton(text="Ravager logs", callback_data="sys_info_logs|ravager_logs")],
                      [InlineKeyboardButton(text="Back", callback_data="admin|admin_sys_info"),
                       InlineKeyboardButton(text="Back to main menu", callback_data="admin|admin_main")]]
        reply_markup = InlineKeyboardMarkup(logs_panel)
        return reply_markup

    def system_options(self, update, context):
        callback_data = update.callback_query.data
        callback_data = callback_data.split("|")
        selection_option = callback_data[1]

        if selection_option == "sys_info":
            psutil.cpu_percent(interval=0.1)
            cpu_percent = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            disk_usage = psutil.disk_usage(str(DOWNLOAD_DIR))
            net = psutil.net_io_counters(pernic=False, nowrap=True)
            used_mem = humanize(mem.used)
            available_mem = humanize(mem.available)
            bytes_sent = humanize(net.bytes_sent)
            bytes_recvd = humanize(net.bytes_recv)
            total_disk_space = humanize(disk_usage.total)
            total_free_space = humanize(disk_usage.free)
            text = sys_info_text.format(cpu_percent, used_mem.size, used_mem.suffix, available_mem.size, available_mem.suffix,
                                        bytes_recvd.size, bytes_recvd.suffix, bytes_sent.size, bytes_sent.suffix,
                                        total_disk_space.size, total_disk_space.suffix, total_free_space.size,
                                        total_free_space.suffix)
            update.callback_query.edit_message_text(text=text, parse_mode=ParseMode.MARKDOWN,
                                                    reply_markup=self.last_step_btns(prev_menu="admin|admin_sys_info"))
            return SYS_INFO_PANEL

        if selection_option == "logs":
            update.callback_query.edit_message_text(text="*Get yo logs*", parse_mode=ParseMode.MARKDOWN,
                                                    reply_markup=self.logs_panel())
            return LOGS_HANDLER

    def logs_handler(self, update, context):
        callback_data = update.callback_query.data
        callback_data = callback_data.split("|")
        selection_option = callback_data[1]
        try:
            if selection_option == "aria_logs":
                context.bot.sendDocument(chat_id=update.callback_query.from_user.id,
                                         document=open("{}/aria2.log".format(LOGS_DIR), "rb"))
            if selection_option == "celery_logs":
                context.bot.sendDocument(chat_id=update.callback_query.from_user.id, document=open("{}/celery.log".format(LOGS_DIR), "rb"))
            if selection_option == "ravager_logs":
                context.bot.sendDocument(chat_id=update.callback_query.from_user.id, document=open("{}/ravager.log".format(LOGS_DIR), "rb"))
            return LOGS_HANDLER
        except Exception as e:
            logger.error(e)

    @_restricted
    def serve_admin_panel(self, update, context):
        if str(update.effective_chat.type) == "group" or str(update.effective_chat.type) == "supergroup":
            update.message.reply_text(text="This command can only be ran inside private chat")
            return -1
        self.user.user_id = update.effective_chat.id
        self.user = UserData(user=self.user).get_user()
        update.message.reply_text(text="Admin Panel", reply_markup=self.admin_panel())
        return HANDLE_ADMIN_PANEL

    def limits_options(self, update, context):
        callback_data = update.callback_query.data
        callback_data = callback_data.split("|")
        selection_option = callback_data[1]
        max_tasks_per_chat = MAX_TASKS_PER_USER
        download_storage_size_treshold = STORAGE_SIZE
        download_storage_time_treshold = STORAGE_TIME

        if selection_option == "max_tasks_per_chat":
            text = "*Max tasks per chat*\nCurrent value is: *{}*\nSend new value:".format(max_tasks_per_chat)

        if selection_option == "storage_size_treshold":
            text = "*Download storage size*\nCurrent value is: *{}* GB\nSend new value:".format(
                download_storage_size_treshold)

        if selection_option == "storage_duration":
            text = "*Download storage duration*\nCurrent value is: *{}* Hrs\nSend new value:".format(
                download_storage_time_treshold)

        update.callback_query.edit_message_text(text=text, parse_mode=ParseMode.MARKDOWN,
                                                reply_markup=self.last_step_btns(prev_menu="admin|admin_limits"))
        return LIMITS_PANEL

    def admin_interface_handler(self):
        admin_interface_handler = ConversationHandler(
            entry_points=[CommandHandler("admin_interface", self.serve_admin_panel)],
            states={
                HANDLE_ADMIN_PANEL: [CallbackQueryHandler(self.handle_admin_panel, pattern="admin")],

                LIMITS_PANEL: [CallbackQueryHandler(self.limits_options, pattern="limits")],

                FILTERS_PANEL: [CallbackQueryHandler(self.filters_options, pattern="filters")],

                SYS_INFO_PANEL: [CallbackQueryHandler(self.system_options, pattern="sys_info")],

                LOGS_HANDLER: [CallbackQueryHandler(self.logs_handler, pattern="sys_info_logs")]

            },
            fallbacks=[CallbackQueryHandler(self.handle_admin_panel, pattern="admin"),
                       CallbackQueryHandler(self.handle_admin_panel, pattern="limits"),
                       CallbackQueryHandler(self.handle_admin_panel, pattern="filters"),
                       CallbackQueryHandler(self.handle_admin_panel, pattern="close"),
                       CommandHandler('cancel', self.end_selection),
                       MessageHandler(Filters.regex('^\/'), self.end_selection)],
            conversation_timeout=300

        )
        return admin_interface_handler
