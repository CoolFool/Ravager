from telegram.ext import CommandHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from ravager.bot.helpers.validators import *
from ravager.database.tasks import Tasks
from ravager.database.helpers.structs import OpsDataStruct
import logging

logger = logging.getLogger(__file__)


class Abort:
    def __init__(self):
        pass

    @check_authorized()
    @check_drive_selection()
    def stop_tasks(self, update, context):
        chat_id = update.effective_chat.id

        if update.message.reply_to_message is not None:
            reply_msg_id = update.message.reply_to_message.message_id
            task = OpsDataStruct()
            task.source_msg_id = reply_msg_id
            task = Tasks(task=task).get_task()
            status = task.status
            try:
                if status is None:
                    context.bot.send_message(chat_id=chat_id, reply_to_message_id=reply_msg_id,
                                             text="Error occurred while handling request")
                elif status == "processing":
                    context.bot.send_message(chat_id=chat_id, reply_to_message_id=reply_msg_id,
                                             text="Download not started")

                else:
                    valid_statuses = ["downloading", "uploading"]

                    if status == "aborted":
                        context.bot.send_message(chat_id=chat_id, reply_to_message_id=reply_msg_id,
                                                 text="Task has been already aborted")
                    elif status == "uploaded":
                        context.bot.send_message(chat_id=chat_id, reply_to_message_id=reply_msg_id,
                                                 text="The transfer is already complete,can't abort")
                    elif status == "upload failed":
                        context.bot.send_message(chat_id=chat_id, reply_to_message_id=reply_msg_id,
                                                 text="Uploading failed no need to abort")
                    elif status in valid_statuses:
                        drive_options = [
                            [InlineKeyboardButton(text="Yes", callback_data="abort|yes|{}".format(reply_msg_id)),
                             InlineKeyboardButton(text="No", callback_data="abort|no|{}".format(reply_msg_id))]]

                        reply_markup = InlineKeyboardMarkup(drive_options)
                        context.bot.send_message(chat_id=chat_id, reply_to_message_id=reply_msg_id,
                                                 text="Are you sure about aborting ongoing tranfer?",
                                                 reply_markup=reply_markup)
                    else:
                        context.bot.send_message(chat_id=chat_id, reply_to_message_id=reply_msg_id,
                                                 text="Error occurred while aborting")
            except Exception as e:
                logger.error(e)
                context.bot.send_message(chat_id=chat_id, reply_to_message_id=reply_msg_id,
                                         text="Download not yet started or Invalid data")

    def abort_handler(self):
        stop_handler = CommandHandler("abort", self.stop_tasks)
        return stop_handler
