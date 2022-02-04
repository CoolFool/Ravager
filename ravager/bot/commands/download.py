from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from functools import partial
from celery import uuid
import secrets
from hashlib import blake2b
from datetime import datetime
import pytz
from ravager.bot.helpers.constants import *
from ravager.bot.helpers.timeout import ConversationTimeout
from ravager.bot.helpers.validators import *
from ravager.services.aria.download import Download as aria
from ravager.helpers.to_magnet import Torrent
from ravager.database.helpers.structs import UserStruct, OpsDataStruct
from ravager.database.tasks import Tasks
from ravager.config import TIMEZONE, DOWNLOAD_DIR
from ravager.services.aria.updater import Updater


class Download:
    def __init__(self):
        self.end_selection = ConversationTimeout.end_selection
        self.selection_timeout = ConversationTimeout.selection_timeout

    @check_authorized(is_convo=True)
    @check_filters(is_convo=True)
    @check_drive_selection()
    @check_celery_queue(is_convo=True)
    @give_uptime()
    def add_file(self, update, context):
        self.user_id = str(update.effective_chat.id)

        drive_options = [
            [InlineKeyboardButton(text="Direct Download", callback_data="download|ddl|{}".format(self.user_id)),
             InlineKeyboardButton(text="Torrent", callback_data="download|torrent|{}".format(self.user_id)),
             InlineKeyboardButton(text="Magnet", callback_data="download|magnet|{}".format(self.user_id))]]

        reply_markup = InlineKeyboardMarkup(drive_options)
        update.message.reply_text(quote=True, text="Select source format:",
                                  reply_markup=reply_markup)
        return DOWNLOAD_HANDLER

    def download_handler(self, update, context):
        # force reply in a group
        callback_data = update.callback_query.data
        callback_data = callback_data.split("|")
        action = callback_data[1]
        if action == "ddl":
            update.callback_query.edit_message_text(text="Send direct download link by replying to this message")
            return DDL_HANDLER
        elif action == "torrent":
            update.callback_query.edit_message_text(text="Send torrent file by replying to this message")
            return TORRENT_HANDLER
        elif action == "magnet":
            update.callback_query.edit_message_text(text="Send magnet uri by replying to this message")
            return MAGNET_HANDLER
        else:
            update.message.reply_text(text="Application crashed,contact admin", quote=True)
            logger.error("#1:Shouldn't reach here")
            return END

    def source_handler(self, update, context, data):
        user_id = str(update.effective_chat.id)
        if data == "ddl":
            user_data = update.message.text
        elif data == "magnet_uri":
            user_data = update.message.text
        elif data == "torrent":
            file_name = str(update.message.document.file_name)
            torrent = context.bot.getFile(update.message.document.file_id)
            path = torrent.download("{}/{}".format(DOWNLOAD_DIR, file_name))
            user_data = Torrent().to_magnet(str(path))
        else:
            update.message.reply_text(text="Application crashed,contact admin", quote=True)
            return END

        uri_data = bytes(user_data, "utf-8")
        folder_id = blake2b(digest_size=10)
        folder_id.update(uri_data)
        folder_id = folder_id.hexdigest()

        msg_data = update.message.reply_text(text="Processing Download", quote=True)
        msg_id = msg_data.message_id
        source_msg_id = msg_data.reply_to_message.message_id

        user = UserStruct()
        user.user_id = user_id

        task = OpsDataStruct()
        task.file_id = folder_id
        tasks = Tasks(task=task, key="file_id").get_tasks()
        task.gid = secrets.token_hex(8)
        task_id = uuid()
        task.msg_id = msg_id
        task.user_id = user_id
        task.source_msg_id = source_msg_id
        task.task_id = task_id
        task.start_time_stamp = datetime.now(pytz.timezone(TIMEZONE))
        task.file_path = "{}/{}".format(DOWNLOAD_DIR, folder_id)
        if tasks is None:
            task.status = "processing"
            Tasks(task=task).set_task()
            task = task.to_json()
            aria().start.apply_async(kwargs={"uri": str(user_data), "task": task}, task_id=task_id)
            return END
        else:
            for t in tasks:
                if t.status == "processing":
                    task.status = "processing"
                    Tasks(task=task).set_task()
                    return END

                elif t.status == "downloading":
                    task.status = "downloading"
                    task.gid = tasks[0].gid
                    context.bot.delete_message(chat_id=task.user_id, message_id=task.msg_id)
                    message = context.bot.send_message(chat_id=task.user_id, reply_to_message_id=task.source_msg_id,
                                                       text="Download Started")
                    msg_id = message.message_id
                    Tasks(task=task).set_task()
                    Updater().download_updater.apply_async(kwargs={"gid": task.gid, "msg_id": msg_id,"source_msg_id":source_msg_id},
                                                           task_id=task.task_id)
                    return END
                else:
                    task.status = "processing"
                    Tasks(task=task).set_task()
                    task = task.to_json()
                    aria().start.apply_async(kwargs={"uri": str(user_data), "task": task}, task_id=task_id)
                    return END

    @staticmethod
    def invalid_data_handler(update, context):
        update.message.reply_text(text="Send valid data according to your selection", quote=True)
        return END

    def download_convo_handler(self):
        download_convo_handler = ConversationHandler(
            entry_points=[CommandHandler("download", self.add_file)],
            states={
                DOWNLOAD_HANDLER: [CallbackQueryHandler(self.download_handler, pattern="^download\|")],

                DDL_HANDLER: [MessageHandler(Filters.regex(
                    r"(ftp|https?):\/\/[^\s]([\w+?\.\w+])+([a-zA-Z0-9\~\!\@\#\$\%\^\&\*\(\)_\-\=\+\\\/\?\.\:\;\'\,]*)?"),
                    partial(self.source_handler, data="ddl")),
                    MessageHandler(Filters.text, self.invalid_data_handler)],

                TORRENT_HANDLER: [MessageHandler(Filters.document.mime_type("application/x-bittorrent"),
                                                 partial(self.source_handler, data="torrent")),
                                  MessageHandler(Filters.text, self.invalid_data_handler),
                                  MessageHandler(Filters.document, self.invalid_data_handler)],

                MAGNET_HANDLER: [MessageHandler(Filters.regex(r"^magnet:\?xt=urn:[a-z0-9]+:[a-z0-9].+&dn=.+"),
                                                partial(self.source_handler, data="magnet_uri")),
                                 MessageHandler(Filters.text, self.invalid_data_handler)],

                ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, self.selection_timeout)]

            },
            fallbacks=[CommandHandler('cancel', self.end_selection),
                       MessageHandler(Filters.regex('^\/'), self.end_selection)],
            conversation_timeout=300
        )
        return download_convo_handler
